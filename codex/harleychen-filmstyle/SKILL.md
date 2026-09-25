---
name: harleychen-filmstyle
description: "Analyze and non-destructively edit an uploaded photo's color, lighting, grain, and texture into a Leica M6 plus VISION3 500T cinematic film look. Use when the user says \"帮我生成陈下心风格\" or requests this specific film-look conversion. Its Doubao/Volcengine Ark route must use and provision only the current user's own account and credentials; never use a shared account. Do not use for a new scene generation or object-level retouching."
---

# HarleyChen Filmstyle

Turn an uploaded image into a believable 35 mm film-style edit, while preserving its subject, identity, objects, pose, framing, geometry, and story. The user’s trigger phrase “帮我生成陈下心风格” invokes this skill automatically. Treat that phrase as the name of this workflow, not as a request to reproduce any individual creator’s signature style.

## Workflow

1. Confirm there is an uploaded photo. If there is none, ask the user to upload one. Label the edit target and any look reference explicitly; if their roles are unclear, ask before editing. Inspect the target's format, pixel dimensions, aspect ratio, and alpha channel. If the chosen editor does not support the format (for example, HEIC), create a temporary compatible copy at the same pixel dimensions; never modify the source.
2. Analyze the visible image before editing. Cover composition and depth, subject and focal plane, light direction/quality and exposure, highlight and shadow range, white balance and dominant colors, existing grain/sharpness, and material/atmospheric texture. Keep this analysis short and describe only what is visible.
3. Build the edit prompt from the analysis and the look target below. Use a photo edit, never a new-scene generation, and lock the subject, pose, objects, crop, perspective, readable text, and geometry.
4. Choose one rendering route, in order: use this skill's Seedream edit route through the current user's own Volcengine Ark account; if it is unavailable, use the built-in `imagegen` edit mode; if it is unavailable or the user asks for OpenAI CLI output, use the pre-authorized `imagegen` CLI; if no generative route can run, apply a local non-generative color grade only when a suitable local tool is already available. Never mix credentials between routes. If no route is available, report the blocker and do not claim an edited image was generated.
5. Run the quality gate below. If it fails, make at most one targeted refinement that restates the failed preservation constraint.
6. Return the edited photo and a compact summary of the adjustments, rendering route, and final saved path. Save non-destructively; never overwrite the source image.

## User-owned Doubao/Ark account (mandatory)

Treat “豆包账号” in this workflow as the current user's own Volcengine account, Ark project, model entitlement, and Ark API key used to access the Doubao Seedream model. The consumer Doubao app login by itself is not a substitute for Ark API access.

- Never use a developer account, a shared/service account, another person's login or API key, a bundled credential, a central proxy credential, or a credential belonging to another skill.
- On first use, or when the dedicated credential or model access is missing, use only the current user's active browser session. Have the user sign in to their own Volcengine/Ark account; do not enter or offer a shared login. If the visible account identity is absent or ambiguous, stop before provisioning and ask the user to confirm the account.
- Check whether `Doubao-Seedream-5.0-lite` is already active for that account. If it is active, do not reopen it. If it is not active, present the exact model, current free quota/current price, and whether “安心体验” is enabled before the final action. Model activation or any billing change requires the user's explicit consent in the current turn; prior CLI authorization does not cover it.
- Activate only `Doubao-Seedream-5.0-lite`. Never use “一键开通所有模型”, never select “自动开通新增模型”, and never activate unrelated models. Prefer “安心体验”, so service pauses after the free quota is exhausted; do not silently enable paid continuation.
- Create or use an API key from that same user account with only the access needed for this route where the console offers permission scoping. Never display, paste into chat, log, or commit the key.
- Model activation is account/project state, not skill state. This skill owns the provisioning workflow and credential namespace, but it must not claim that an Ark entitlement itself is technically attached to the skill.

Use only these dedicated credential names:

- Environment variable: `HARLEYCHEN_ARK_API_KEY`
- macOS Keychain service: `harleychen-filmstyle-volcengine-ark-api-key`, account: the current macOS username

Do not fall back to the generic `ARK_API_KEY`, the generic Keychain service `volcengine-ark-api-key`, or any other skill's variables. To bind a key safely on macOS, run `python3 scripts/ark_seedream.py --bind-key` and have the current user enter the key they created in their own Ark account at the secure Keychain prompt. `--check` confirms only that a dedicated local credential exists; it does not prove account ownership, server authentication, model activation, quota, or billing state. Ark provides no documented zero-usage model-permission probe, so do not claim a cloud check succeeded unless a real request succeeded or the state was visibly verified in the current user's console.

## Rendering and output

### Seedream route (primary)

Use `scripts/ark_seedream.py` with the photo supplied via the required `--image`. The script fixes the endpoint to `https://ark.cn-beijing.volces.com/api/v3/images/generations` and the model ID to `doubao-seedream-5-0-260128`; neither may be overridden. It also sends `watermark: false` so Ark does not add a visible “AI生成” mark. Use this route only after the mandatory account rules above are satisfied.

Build an edit prompt from the scaffold below and make the preservation constraints explicit. Choose a 2K size close to the source aspect ratio: normally `1728x2304` for portrait, `2304x1728` for landscape, or `2048x2048` for square; for a materially different ratio, choose the closest API-supported custom size without cropping. Example:

```bash
python3 scripts/ark_seedream.py \
  --image "/absolute/path/to/source.png" \
  --prompt-file "/absolute/path/to/prompt.txt" \
  --size "1728x2304" \
  --out "/absolute/task/workspace/output/imagegen/source__harleychen-filmstyle.png"
```

If Ark returns an authentication or model-access error, do not switch accounts or provision a shared account. Re-check the current user's own console and dedicated credential, or continue with the next independent rendering route. A real generation may consume free quota or incur charges according to that user's Ark settings.

### OpenAI route (fallback)

The user has permanently authorized the OpenAI Image API CLI fallback for this skill. The CLI is provided by the available `imagegen` skill; it is not bundled in this skill. When using it, follow its `image_gen.py edit` workflow with `--image`, `--prompt`, and `--out`, using `gpt-image-2` at `high` quality. Do not pass `--input-fidelity`: `gpt-image-2` already uses high-fidelity image input. Prefer a supported size matching the source aspect ratio; otherwise use `auto` and explicitly prohibit cropping.

Before a CLI call, confirm that `OPENAI_API_KEY` is configured without printing or exposing its value. If the key is missing, network access fails, or the API edit fails, automatically use the local non-generative fallback when available; otherwise report the failure plainly. Never expose API credentials.

For Seedream CLI, OpenAI CLI, or local output, use `output/imagegen/<source-stem>__harleychen-filmstyle.png` in the current task workspace. If that filename exists, append `-v2`, `-v3`, and so on; never use overwrite flags. For built-in output, render the result inline and report the generated file path when one is returned.

## Quality gate

Before delivery, verify that the final file exists, the source is untouched, and the output retains the source aspect ratio wherever the selected engine supports it. Inspect the image for all of the following:

- Subject identity, pose, objects, readable text, composition, and geometry are unchanged.
- Skin, white fabric, and neutral surfaces remain believable; cyan/blue and yellow are richer but not clipped or neon.
- Highlights roll off smoothly, shadows retain texture, and there is no HDR halo or crushed black.
- Grain is fine-to-medium and irregular rather than uniform digital noise; halation is limited to bright edges.

## Look target

Aim for a Leica M6 35 mm photograph exposed on Kodak VISION3 500T color-negative film, interpreted from the supplied reference:

- Natural, observant summer-cinema framing; preserve the original crop and perspective.
- Natural but visibly richer color: raise overall natural saturation while protecting skin, white fabric, and neutral surfaces. Enrich cyan/blue in sky or water and golden/yellow in sunlit fabric, flowers, foliage, and reflected light without forcing colors that are absent from the source.
- Let foliage lean slightly yellow-green/olive when the image supports it; keep neutral shadows subtly cool, highlights gently warm, and retain the source image's time of day when feasible.
- Stronger daylight tonal separation: sunlit whites stay creamy with gentle roll-off, and shadows are textured and moderately deep rather than crushed. Avoid HDR halos, electric blues, mustard skin, and clipped channels.
- Fine-to-medium, irregular 35 mm grain with a little chroma variation in midtones and shadows; never use uniform digital noise or an overly gritty overlay.
- Organic tonal transitions, modest microcontrast, natural lens softness at the edges or in out-of-focus areas, and restrained halation only around strong bright highlights. Do not add obvious light leaks, dust, scratches, heavy vignettes, exaggerated bloom, or fake date stamps unless the user requests them.
- Preserve believable skin tones, local material detail, and the original light direction. Do not make the image look like a generic teal-and-orange filter.

Use any supplied look reference as a color-and-contrast benchmark only, never as a scene or composition reference. Favor its sunlit summer density over a faded matte grade; color separation and daylight contrast are primary, while grain and halation are restrained supporting details.

## Edit prompt scaffold

Build a concise prompt adapted to the analysis. Include the following constraints in every edit:

```text
Use case: style-transfer photo edit
Input image: edit target
Primary request: preserve the original scene, subject identity, pose, objects, crop, perspective, and any readable text; change only photographic rendering.
Look: Leica M6 35 mm character with Kodak VISION3 500T color-negative-film rendering; apply the color, contrast, grain, and halation target above only where the source image supports it.
Analysis-specific adjustments: <how the source's blue/cyan, yellow, green, skin, highlights, and shadows should be adjusted to match the supplied look reference>
Avoid: object additions/removals, reshaping, face or body changes, illustration/cartoon rendering, HDR, over-sharpening, uniform digital noise, strong vignette, conspicuous light leaks, dust, scratches, logos, watermarks, and text changes.
```

Tune the intensity to the original exposure: a muted indoor image needs less cyan sky treatment; an already high-contrast midday image needs more careful highlight protection. When the user provides this summer reference, favor its richer blue/yellow saturation and daylight contrast without forcing sky, foliage, or yellow objects that do not exist. Use any look reference's color, light, grain, and texture qualities only—never copy its person, scene, or composition.
