# HarleyChen Filmstyle

将上传照片转换为 Leica M6 + Kodak VISION3 500T 的电影胶片观感，同时保留人物、服装、物件、构图、透视和建筑几何。

触发语：`帮我生成陈下心风格`。这只是本工作流的名称，不代表复刻任何特定创作者的个人风格。

## 包结构

```text
codex/harleychen-filmstyle/   # 完整 Codex Skill：本地脚本 + 专属 macOS 钥匙串支持
doubao/harleychen-filmstyle/ # 豆包适配说明：不含密钥，不依赖 macOS 钥匙串
```

不要将两个目录混装：它们针对不同运行环境。`codex/` 是可执行版；`doubao/` 是面向豆包工作区或自定义 Skill 的安全适配版。

## 安全与账号边界

- 不提交 API Key、`.env`、钥匙串导出、原图或生成结果。
- 每位使用者只使用自己的火山方舟/豆包账号和 API Key，禁止共享、打包或复用他人的凭据。
- 仅使用 `Doubao-Seedream-5.0-lite`（API ID：`doubao-seedream-5-0-260128`）。开通模型或改变计费前必须由当前使用者确认；不要使用“全量开通”或自动开通未来模型。
- Codex 版只读取 `HARLEYCHEN_ARK_API_KEY` 或 macOS Keychain 的 `harleychen-filmstyle-volcengine-ark-api-key`；不会读取通用 `ARK_API_KEY`。

仓库故意不含许可证。公开发布前，请自行选择并加入适合的许可证；在此之前默认保留全部权利。

## 发布到 GitHub

1. 在 GitHub 创建一个**空仓库**，建议先设为 Private，例如 `harleychen-filmstyle`。
2. 在此目录执行：

```bash
git init
git add README.md .gitignore codex doubao
git commit -m "Initial HarleyChen Filmstyle skill package"
git branch -M main
git remote add origin https://github.com/<你的用户名>/harleychen-filmstyle.git
git push -u origin main
```

提交前运行 `git status` 与 `git diff --cached`，确认其中没有密钥、照片、输出文件或本机路径。

## 安装给 Codex

在 Codex 对话中输入以下请求，交由内置 `skill-installer` 安装：

```text
请从 GitHub 仓库 <你的用户名>/harleychen-filmstyle 安装 Skill，路径是 codex/harleychen-filmstyle。
```

安装后可输入 `$harleychen-filmstyle`，或直接说“帮我生成陈下心风格”。首次使用方舟路线时，使用者应在自己的火山方舟账号中开通指定模型，并通过环境变量或 macOS 钥匙串配置自己的密钥。

## 在豆包中使用

请阅读 [豆包适配说明](doubao/harleychen-filmstyle/README.md)。普通豆包聊天、移动端和豆包工作区对“GitHub 导入”“脚本执行”“安全变量”的支持不同；GitHub 仓库本身不能让任何宿主自动获得或执行你的本机钥匙串密钥。
