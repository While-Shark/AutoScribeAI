# AutoScribeAI

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja-JP.md) · [한국어](README.ko-KR.md)

> Give an AI a software project and get a screenshot-backed user manual.

**Live Demo:** https://auto-scribe-ai-tau.vercel.app

AutoScribeAI is a portable Skill Pack for documenting real software workflows. It helps an AI inspect a project, operate authorized UI flows, capture screenshots, record observed results, and export a manual as **HTML, Word / DOCX, and Markdown**.

No AutoScribeAI backend is required.

## See it first

The live gallery contains three real examples:

| Project | Language | Verified scope |
| --- | --- | --- |
| Uptime Kuma | 简体中文 | **3/3** workflows verified |
| changedetection.io | 日本語 | **0/3** verified; blocker preserved instead of inventing steps |
| IT Tools | 한국어 | **1/3** verified; observed and source-discovered flows are separated |

**[Open Live Demo →](https://auto-scribe-ai-tau.vercel.app)**

From the gallery you can:

- open the generated interactive HTML manual;
- preview the generated Word document;
- inspect real screenshots and verification status.

## What you get

- **Offline HTML** — searchable and visual, with an optional single-file export for sharing.
- **Word / DOCX** — editable and suitable for delivery or training.
- **Markdown** — convenient for Git repositories and knowledge bases.
- **Coverage / quality report** — shows what was verified, blocked, or still unverified.
- **Review tools** — role focused reading, interrupted workflow recovery, version change review, and package link checks.

AutoScribeAI only marks a workflow as verified when real observed steps and evidence exist. Source-code discovery alone stays unverified.

## Use it

Clone the repository and keep the full directory structure:

```bash
git clone https://github.com/While-Shark/AutoScribeAI.git
cd AutoScribeAI
python -m pip install -r requirements.txt
```

Then start your AI agent in this directory and ask:

```text
Read skills/autoscribe/SKILL.md and use AutoScribeAI
to generate a complete illustrated user manual for this project.
```

The agent should have file access and a terminal. Real UI verification additionally requires an authorized browser or computer-use capability.

<details>
<summary><strong>Codex</strong></summary>

From the AutoScribeAI root:

```bash
codex
```

Then ask Codex to read `skills/autoscribe/SKILL.md` and generate the manual.

AutoScribeAI uses the open `SKILL.md` pattern, so Codex can work directly from the repository without copying the skill files elsewhere.

</details>

<details>
<summary><strong>Claude Code</strong></summary>

From the AutoScribeAI root:

```bash
claude
```

Prompt:

```text
Read skills/autoscribe/SKILL.md and follow the AutoScribeAI workflow.
```

Claude Code supports native filesystem Skills, but AutoScribeAI recommends keeping the full repository together because the Skills reference shared scripts, schemas, and reference files.

</details>

<details>
<summary><strong>Pi</strong></summary>

Open Pi in the AutoScribeAI root and tell it to read:

```text
skills/autoscribe/SKILL.md
```

Pi supports Agent Skills and `SKILL.md`, but workspace mode is the simplest way to preserve all AutoScribeAI supporting files.

</details>

<details>
<summary><strong>Agy / Google Antigravity</strong></summary>

Start `agy` in the AutoScribeAI root, then ask it to read:

```text
skills/autoscribe/SKILL.md
```

Antigravity supports Agent Skills natively. Keeping the complete AutoScribeAI workspace avoids breaking relative references between Skills and shared resources.

</details>

<details>
<summary><strong>OpenCode</strong></summary>

Start OpenCode in the AutoScribeAI root and ask it to load:

```text
skills/autoscribe/SKILL.md
```

OpenCode supports `SKILL.md` and Agent Skills locations such as `.opencode/skills`, `.claude/skills`, and `.agents/skills`. For AutoScribeAI, using the repository directly is the simplest option.

</details>

<details>
<summary><strong>Other agents: Cursor, Cline, Roo Code, Gemini CLI, etc.</strong></summary>

If the agent can read files and run commands, no special integration is required.

Open the AutoScribeAI repository as the workspace and give it this instruction:

```text
Read skills/autoscribe/SKILL.md.
Keep the full AutoScribeAI directory available.
Use its scripts, schemas, references, and skills to generate the manual.
```

If the agent also has browser or computer-use tools, it can perform real UI verification and capture screenshot evidence.

</details>

## Languages

Built-in manual UI labels support:

- **English — `en-US` (default)**
- Simplified Chinese — `zh-CN`
- Japanese — `ja-JP`
- Korean — `ko-KR`

## More

- [Live Demo](https://auto-scribe-ai-tau.vercel.app)
- [Real sample outputs](tests/manual_samples/README.md)
- [Installation](docs/INSTALLATION.md)
- [Technical design](docs/TECHNICAL_DESIGN.md)
- [Evidence rules](references/EVIDENCE.md)
