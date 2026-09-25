#!/usr/bin/env python3
"""Edit an image with Seedream through the current user's dedicated Ark credential."""

import argparse
import base64
import getpass
import json
import mimetypes
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL = "doubao-seedream-5-0-260128"
KEYCHAIN_SERVICE = "harleychen-filmstyle-volcengine-ark-api-key"
API_KEY_ENV = "HARLEYCHEN_ARK_API_KEY"
PENDING = {"queued", "pending", "in_progress", "running", "processing"}
FAILED = {"failed", "error", "cancelled", "canceled"}


def fail(message):
    raise SystemExit(f"error: {message}")


def api_key():
    key = os.environ.get(API_KEY_ENV)
    if key:
        return key, API_KEY_ENV
    if sys.platform == "darwin":
        result = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-a",
                getpass.getuser(),
                "-s",
                KEYCHAIN_SERVICE,
                "-w",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), f"macOS Keychain service {KEYCHAIN_SERVICE}"
    return None, None


def bind_key():
    if sys.platform != "darwin":
        fail(f"--bind-key requires macOS; set {API_KEY_ENV} in the current user's environment")
    print(
        "Enter the Ark API key created in your own Volcengine account at the secure "
        "macOS Keychain prompt. The value is not printed by this script.",
        file=sys.stderr,
    )
    result = subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-a",
            getpass.getuser(),
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ]
    )
    if result.returncode != 0:
        fail("the dedicated Ark credential was not stored")
    print(f"stored dedicated credential in macOS Keychain service {KEYCHAIN_SERVICE}")


def reference_value(value):
    if value.startswith(("https://", "data:")):
        return value
    if value.startswith("http://"):
        fail("reference image URLs must use HTTPS")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        fail(f"reference image not found: {path}")
    if path.stat().st_size > 30 * 1024 * 1024:
        fail("reference image exceeds 30 MB")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def public_payload(payload):
    safe = dict(payload)
    image = safe.get("image")
    if isinstance(image, list):
        safe["image"] = ["<reference image>" for _ in image]
    elif image:
        safe["image"] = "<reference image>"
    return safe


def request_json(url, method, key, payload=None, timeout=300):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        fail(f"Ark returned HTTP {error.code}")
    except URLError as error:
        fail(f"could not reach Ark: {error.reason}")


def wait_for_result(endpoint, key, response, timeout):
    deadline = time.monotonic() + timeout
    while response.get("status", "").lower() in PENDING:
        task_id = response.get("id") or response.get("task_id")
        if not task_id:
            fail("Ark returned a pending task without an id")
        if time.monotonic() >= deadline:
            fail("timed out while waiting for Ark image generation")
        time.sleep(2)
        response = request_json(
            f"{endpoint}/{quote(str(task_id), safe='')}", "GET", key, timeout=timeout
        )
    if response.get("status", "").lower() in FAILED:
        fail("Ark image generation failed")
    return response


def image_bytes(item):
    data = item.get("b64_json")
    if data:
        if data.startswith("data:"):
            data = data.split(",", 1)[1]
        return base64.b64decode(data)
    url = item.get("url")
    if not url:
        fail("Ark response did not contain an image")
    try:
        with urlopen(url, timeout=120) as response:
            return response.read()
    except URLError as error:
        fail(f"could not download Ark result: {error.reason}")


def output_paths(path, count, output_format):
    path = Path(path)
    if path.suffix == "":
        path = path.with_suffix(".jpg" if output_format == "jpeg" else ".png")
    if count == 1:
        return [path]
    return [
        path.with_name(f"{path.stem}-{index}{path.suffix}")
        for index in range(1, count + 1)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt")
    parser.add_argument("--prompt-file")
    parser.add_argument(
        "--image",
        action="append",
        default=[],
        help="required edit target: local path, HTTPS URL, or data URI",
    )
    parser.add_argument("--size", default="2K")
    parser.add_argument("--output-format", choices=("png", "jpeg"), default="png")
    parser.add_argument("--out", default="output/imagegen/harleychen-filmstyle.png")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check only for a dedicated local credential; does not contact Ark",
    )
    parser.add_argument(
        "--bind-key",
        action="store_true",
        help="securely prompt the current macOS user to store their own Ark API key",
    )
    args = parser.parse_args()

    if args.bind_key:
        bind_key()
        return

    if args.check:
        key, source = api_key()
        if key:
            print(f"HarleyChen Ark credential is configured locally via {source}")
            return
        fail(
            f"dedicated credential not found; set {API_KEY_ENV} or use macOS Keychain "
            f"service {KEYCHAIN_SERVICE}"
        )

    if bool(args.prompt) == bool(args.prompt_file):
        fail("provide exactly one of --prompt or --prompt-file")
    prompt = (
        Path(args.prompt_file).read_text(encoding="utf-8")
        if args.prompt_file
        else args.prompt
    )
    if not prompt.strip():
        fail("prompt is empty")
    if not args.image:
        fail("provide at least one --image; this skill edits photos and does not generate a new scene")

    references = [reference_value(value) for value in args.image]
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": args.size,
        "output_format": args.output_format,
        "response_format": "b64_json",
        "watermark": False,
    }
    if references:
        payload["image"] = references[0] if len(references) == 1 else references

    endpoint = BASE_URL + "/images/generations"
    planned_paths = output_paths(args.out, 1, args.output_format)
    if not args.dry_run and planned_paths[0].exists():
        fail(f"output already exists: {planned_paths[0]}")
    if args.dry_run:
        print(
            json.dumps(
                {"endpoint": endpoint, "payload": public_payload(payload)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    key, _ = api_key()
    if not key:
        fail(
            f"dedicated credential not found; set {API_KEY_ENV} or use macOS Keychain "
            f"service {KEYCHAIN_SERVICE}"
        )
    response = wait_for_result(
        endpoint,
        key,
        request_json(endpoint, "POST", key, payload, args.timeout),
        args.timeout,
    )
    images = response.get("data") or []
    if not images:
        fail("Ark response contained no completed images")

    paths = output_paths(args.out, len(images), args.output_format)
    for path in paths:
        if path.exists():
            fail(f"output already exists: {path}")
    for path, item in zip(paths, images):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image_bytes(item))
        print(path.resolve())


if __name__ == "__main__":
    main()
