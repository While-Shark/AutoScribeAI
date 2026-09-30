# AutoScribeAI

## 把软件的使用过程，变成看得懂、跟得上的图文手册

给 AI 一个项目、一个可访问的演示环境和你想讲清楚的功能，让它按技能流程探索界面、记录操作、采集真实截图，再整理成可以阅读、编辑和分享的手册。

**一次整理，同时交付离线网页、Word 和 Markdown。支持简体中文、英语、日语、韩语。**

[查看真实样例](tests/manual_samples/README.md) · [开始使用](#开始使用) · [安装指南](docs/INSTALLATION.md)

### 先看一次真实操作的结果

我们用 Uptime Kuma 的官方临时演示实例，完成了创建 HTTP 监控、保存并关联通知配置、发布状态页三项流程。下面是状态页的真实截图：

![Uptime Kuma 状态页：测试监控运行正常](tests/manual_samples/uptime-kuma/screenshots/status-page-public.jpg)

[查看完整图文样例](tests/manual_samples/uptime-kuma/README.md) · [下载 Word](tests/manual_samples/uptime-kuma/output/manual.docx) · [下载 Markdown 包](tests/manual_samples/uptime-kuma/output/manual-markdown.zip)

通知使用占位 Webhook 地址，已验证保存和关联，尚未验证消息投递。演示实例的运行版本未与固定源码版本对齐；这些限制也保留在手册和质量报告中。

## 你会得到什么？

| 交付物 | 怎么用 |
| --- | --- |
| **离线 HTML 手册** | 在浏览器打开，按目录阅读、搜索内容、放大截图；也能下载 Word 和 Markdown 包 |
| **Word 文档** | 截图内嵌，方便继续编辑、补充说明、交给客户或培训同事 |
| **Markdown ZIP** | 包含正文和图片资源，便于放进项目文档、知识库或版本仓库 |
| **覆盖与质量报告** | 看清哪些流程已经实测、哪些仍待验证，以及当前交付的限制 |

手册围绕使用者的问题展开：**在哪里操作？需要先准备什么？每一步怎么做？完成后应该看到什么？**

## 适合这些时候

- **新同事入门**：把“我演示一遍”整理成能反复查看的操作说明。
- **交付项目**：给使用者一份有步骤、有截图、可编辑的手册。
- **维护开源项目**：从项目源码和可用界面整理功能说明，减少反复回答相同问题。
- **更新培训材料**：重新检查指定流程，再更新对应章节和截图。
- **面向不同语言的读者**：用中文、英文、日文或韩文交付同一套使用流程。

## 开始使用

### 1. 准备完整项目目录

下载或克隆本仓库，保留完整目录。在仓库根目录安装依赖（Python 3.10+）：

```bash
python -m pip install -r requirements.txt
```

需要可搬移的技能包时，执行：

```bash
python scripts/package_skills.py --output dist/autoscribeai-skills.zip
```

### 2. 让 AI 读取入口技能

在支持本地 Skills 的 AI 环境中，提供完整项目目录，并让它从 [`skills/autoscribe-orchestrator/SKILL.md`](skills/autoscribe-orchestrator/SKILL.md) 开始。不要只复制一个 `SKILL.md`，其他脚本和资源也需要保留。

AI 环境需要终端和文件读写能力；要生成实测截图，还需要可用且已授权的浏览器与截图能力。AutoScribeAI 自身无需部署常驻服务，目标软件仍需要可以访问。

### 3. 告诉 AI，你想为谁写什么

可以从这样的任务开始，替换其中的项目和地址：

> 请使用 AutoScribeAI，为我的项目生成一份面向普通使用者的简体中文操作手册。先读取入口技能。项目源码在［源码路径］，测试环境是［演示地址］，使用者角色是［角色］。范围包括创建监控、配置通知和发布状态页。允许在测试环境创建合成测试数据，请记录真实操作结果并采集截图。输出离线 HTML、Word 和 Markdown ZIP；无法验证的步骤请明确说明。

需要日语或韩语时，把输出语言改为“日语”或“韩语”即可。登录凭据通过宿主的安全登录方式提供，不写进配置或手册。

详细安装、宿主要求和命令行流程见[安装指南](docs/INSTALLATION.md)。

## 三个项目，三种语言，直接看效果

| 样例 | 语言 | 当前实测范围 | 查看 |
| --- | --- | --- | --- |
| **Uptime Kuma** | 简体中文 | 监控、通知配置、状态页，3/3 流程；通知投递未验证 | [手册与截图](tests/manual_samples/uptime-kuma/README.md) |
| **changedetection.io** | 日本語 | 公开页面截图；功能流程 0/3，订阅入口阻碍继续验证 | [手册与截图](tests/manual_samples/changedetection/README.md) |
| **IT Tools** | 한국어 | JSON→YAML 转换，1/3 流程；哈希和二维码未验证 | [手册与截图](tests/manual_samples/it-tools/README.md) |

每份样例都保留了输入配置、截图、导出文件和质量报告，可以对照检查。[打开样例索引](tests/manual_samples/README.md)。

## 关于当前版本

AutoScribeAI 目前为开发版。项目分析、截图处理、离线 HTML、DOCX、Markdown 导出及四种语言模板已实现；真实浏览器操作由 AI 宿主提供，尚无通用的浏览器自动采集适配器。

只有源码时，可以整理功能清单和候选流程；具备可访问的界面后，才能实际验证操作并采集截图。流程状态和截图证据会保留在输出中。质量报告中的 `ready: false` 表示仍有需要说明或处理的缺口，交付前请检查内容、截图及 Word 排版。

其他语言可以由 AI 撰写正文，固定模板标签暂时回退为英语。

## 想进一步了解或参与？

| 入口 | 内容 |
| --- | --- |
| [安装指南](docs/INSTALLATION.md) | 安装技能、准备环境、执行命令 |
| [技术方案](docs/TECHNICAL_DESIGN.md) | 技能分工、内容模型和导出方案 |
| [开发计划](docs/ROADMAP.md) | 当前进度与后续工作 |
| [运行约定](references/RUN_PROTOCOL.md) | 任务恢复与操作记录 |
| [证据约定](references/EVIDENCE.md) | 截图、脱敏与核验 |

发现说明不清楚、截图缺失或步骤有误，欢迎提交 [Issue](https://github.com/While-Shark/AutoScribeAI/issues)，附上对应章节、运行环境和实际结果。反馈中请移除密码、令牌及业务敏感数据。
