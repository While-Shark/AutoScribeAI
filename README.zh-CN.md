# AutoScribeAI

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja-JP.md) | [한국어](README.ko-KR.md)

## 把一个软件项目交给 AI，直接得到能交付的图文操作手册

给 AI 一个项目、可访问的测试环境和需要覆盖的流程，AutoScribeAI 会指导它梳理模块、真实操作已授权界面、采集截图、记录实际结果，再生成有证据的操作手册。

**不需要部署 AutoScribeAI 后端。一次执行即可同时得到可搜索的离线 HTML、可编辑 Word / DOCX、Markdown 和覆盖率报告。**

**特别适合：** 项目交付、新员工培训、企业内部系统、开源项目文档、客户培训、验收材料，以及版本更新后的手册维护。

### 先看 Demo，再决定要不要用

现在仓库里有一个 Vercel-ready 的统一 Demo Gallery，把 3 个真实测试项目放在同一页；可以直接打开生成的 HTML 手册，也可以预览实际生成的 Word 文档。

- Uptime Kuma：简体中文，目标流程 **3/3 已验证**
- changedetection.io：日语，受公开付费流程限制，**0/3 已验证**，不会编造未执行步骤
- IT Tools：韩语，**1/3 已验证**，已验证与源码候选流程明确分开

Demo 源码：[`demo/`](demo/) · Vercel 配置：[`vercel.json`](vercel.json) · 真实产物：[`tests/manual_samples`](tests/manual_samples/README.md)
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
