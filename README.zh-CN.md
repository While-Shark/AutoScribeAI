# AutoScribeAI

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja-JP.md) · [한국어](README.ko-KR.md)

> 把一个软件项目交给 AI，自动得到一套带真实截图的操作手册。

**在线 Demo：** https://auto-scribe-ai-tau.vercel.app/?lang=zh-CN

AutoScribeAI 是一套便携 Skills。它让 AI 自动理解项目、操作已授权界面、采集截图、记录真实结果，并输出 **HTML、Word / DOCX、Markdown** 操作手册。

**不需要部署 AutoScribeAI 后端服务。**

## 先看效果

在线 Demo 里有 3 个真实测试项目：

| 项目 | 语言 | 实际验证情况 |
| --- | --- | --- |
| Uptime Kuma | 简体中文 | **3/3** 流程已验证 |
| changedetection.io | 日本語 | **0/3**，受阻原因保留，不编造步骤 |
| IT Tools | 한국어 | **1/3**，真实操作与源码候选流程明确分开 |

**[打开在线 Demo →](https://auto-scribe-ai-tau.vercel.app/?lang=zh-CN)**

进去后可以直接：

- 查看生成的 HTML 操作手册；
- 预览实际生成的 Word 文档；
- 查看真实截图和验证状态。

## 最后能得到什么

- **离线 HTML**：可搜索、可浏览，还能另导出单文件分享。
- **Word / DOCX**：方便客户交付、培训和二次编辑。
- **Markdown**：适合 Git 仓库、Wiki、知识库。
- **PDF（可选）**：安装 LibreOffice 后导出固定版式文件。
- **覆盖率 / 质量报告**：明确哪些流程已验证、受阻或未验证。
- **复核工具**：按角色阅读、中断流程恢复、版本差异复查和交付包断链检查。

AutoScribeAI 只有在存在真实操作结果和截图证据时，才会把流程标记为“已验证”。只通过源码发现的功能仍然保持未验证状态。

## 怎么使用

先保留完整仓库：

```bash
git clone https://github.com/While-Shark/AutoScribeAI.git
cd AutoScribeAI
python -m pip install -r requirements.txt
```

然后在这个目录里启动你的 AI Agent，并告诉它：

```text
读取 skills/autoscribe/SKILL.md，
使用 AutoScribeAI 为目标项目生成完整的带图操作手册。
```

Agent 至少需要文件和终端能力；如果要真正操作界面、验证流程和截图，还需要浏览器或 Computer Use 能力。

<details>
<summary><strong>Codex</strong></summary>

在 AutoScribeAI 根目录启动：

```bash
codex
```

然后告诉 Codex：

```text
读取 skills/autoscribe/SKILL.md，
按照 AutoScribeAI 工作流生成操作手册。
```

不需要把单个 Skill 拷贝出去，直接让 Codex 在完整仓库里工作最稳妥。

</details>

<details>
<summary><strong>Claude Code</strong></summary>

在 AutoScribeAI 根目录启动：

```bash
claude
```

然后输入：

```text
读取 skills/autoscribe/SKILL.md，
并按照 AutoScribeAI 流程执行。
```

Claude Code 原生支持文件系统 Skills，但 AutoScribeAI 的多个 Skill 会共同使用仓库里的 `scripts/`、`schemas/`、`references/`，因此推荐保留完整目录直接运行。

</details>

<details>
<summary><strong>Pi</strong></summary>

在 AutoScribeAI 根目录启动 Pi，然后让它读取：

```text
skills/autoscribe/SKILL.md
```

Pi 原生支持 Agent Skills / `SKILL.md`。对于 AutoScribeAI，直接以整个仓库作为工作区最简单。

</details>

<details>
<summary><strong>Agy / Google Antigravity</strong></summary>

在 AutoScribeAI 根目录运行 `agy`，然后告诉它读取：

```text
skills/autoscribe/SKILL.md
```

Antigravity 原生支持 Agent Skills。保留完整工作区可以避免 Skill 与共享脚本、Schema、参考文件之间的相对路径失效。

</details>

<details>
<summary><strong>OpenCode</strong></summary>

在 AutoScribeAI 根目录启动 OpenCode，然后告诉它读取：

```text
skills/autoscribe/SKILL.md
```

OpenCode 原生支持 `SKILL.md`，也兼容 `.opencode/skills`、`.claude/skills` 和 `.agents/skills`。AutoScribeAI 默认推荐直接使用完整仓库。

</details>

<details>
<summary><strong>其他 Agent：Cursor、Cline、Roo Code、Gemini CLI 等</strong></summary>

只要 Agent 能读文件、执行命令，就可以使用。

把 AutoScribeAI 仓库作为工作区打开，然后输入：

```text
读取 skills/autoscribe/SKILL.md。
保留完整 AutoScribeAI 目录，
使用其中的 scripts、schemas、references 和 skills 生成操作手册。
```

如果 Agent 还具备浏览器或 Computer Use 能力，就可以继续做真实 UI 验证和截图采集。

</details>

## 多语言

内置手册界面支持：

- **English — `en-US`（默认）**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

## 更多

- [在线 Demo](https://auto-scribe-ai-tau.vercel.app/?lang=zh-CN)
- [真实样例](tests/manual_samples/README.md)
- [安装说明](docs/INSTALLATION.md)
- [技术方案](docs/TECHNICAL_DESIGN.md)
- [证据规则](references/EVIDENCE.md)
