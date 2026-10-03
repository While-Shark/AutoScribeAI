# AutoScribeAI

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja-JP.md) | [한국어](README.ko-KR.md)

## 把真实软件操作变成有证据的图文操作手册

给 AI 一个项目、可访问的测试环境和需要覆盖的业务流程，AutoScribeAI 会指导 AI 分析项目、操作已授权界面、采集真实截图、保存证据，并生成用户真正能照着使用的操作手册。

**一次流程可同时输出离线 HTML、Word 和 Markdown。默认输出语言为英文，同时内置简体中文、日文和韩文模板。**

[查看真实样例](tests/manual_samples/README.md) · [安装指南](docs/INSTALLATION.md)

### 核心特点

- **HTML 是主阅读体验**：支持目录、搜索、截图查看和离线使用。
- **manual.json 是唯一事实源**：Word 和 Markdown 与 HTML 共享同一结构化数据，不做脆弱的格式互转。
- **证据优先**：源码分析只能形成候选流程；只有真实执行结果和截图证据才能标为“已验证”。
- **无需部署服务**：项目由五个 Skills + 本地确定性脚本组成，浏览器操作能力由 AI 宿主提供。
- **可恢复**：运行状态保存在文件中，中断后可从 checkpoint 继续，不自动重放有副作用的动作。

## 五个 Skills

- `autoscribe-orchestrator`：任务规划、启动、恢复与协调。
- `autoscribe-project-analyzer`：模块、功能、角色和候选流程分析。
- `autoscribe-software-explorer`：真实界面探索、操作与截图证据采集。
- `autoscribe-manual-writer`：将证据整理成统一 `manual.json`。
- `autoscribe-manual-verifier`：检查来源、引用、覆盖率与交付质量。

## 输出结构

```text
项目 / 界面探索
      ↓
    Evidence
      ↓
  manual.json
      ↓
 ┌────┼────────────┐
 ↓    ↓            ↓
HTML  DOCX    Markdown ZIP
```

## 多语言

内置固定模板支持：

- English — `en-US` **默认**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

项目配置省略 `language` 时自动使用 `en-US`。其他 BCP-47 语言也可用于 AI 编写正文，固定模板标签回退到英文。菜单、按钮、字段等产品原始名称在有助于准确性的情况下应保留原文。

## 快速开始

安装依赖：

```bash
python -m pip install -r requirements.txt
```

生成便携技能包：

```bash
python scripts/package_skills.py --output dist/autoscribeai-skills.zip
```

让 AI 从以下入口开始：

```text
skills/autoscribe-orchestrator/SKILL.md
```

示例任务：

> 使用 AutoScribeAI 为这个项目生成完整操作手册。源码是［路径或仓库］，测试环境是［URL］，使用角色是［角色］。允许在测试环境创建合成测试数据。请真实执行流程、采集截图，无法验证的内容明确保留未验证状态，并输出离线 HTML、Word 和 Markdown。

如果没有指定语言，默认生成英文手册；需要中文时显式指定 `zh-CN` 或直接说明“生成简体中文手册”。

## 真实样例

| 样例 | 语言 | 实测范围 |
| --- | --- | --- |
| [Uptime Kuma](tests/manual_samples/uptime-kuma/README.md) | 简体中文 | 监控、通知配置、状态页，3/3 |
| [changedetection.io](tests/manual_samples/changedetection/README.md) | 日本語 | 公开页面证据；功能流程 0/3 |
| [IT Tools](tests/manual_samples/it-tools/README.md) | 한국어 | JSON→YAML，1/3 |

详细内容见 [安装指南](docs/INSTALLATION.md)、[技术方案](docs/TECHNICAL_DESIGN.md)、[开发计划](docs/ROADMAP.md)、[运行约定](references/RUN_PROTOCOL.md) 和 [证据约定](references/EVIDENCE.md)。
