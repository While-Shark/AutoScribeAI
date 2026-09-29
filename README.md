# AutoScribeAI

让 AI 理解并操作软件，自动整理各模块的使用流程，生成有真实截图、可核验、可导出的操作手册。

> 当前阶段：M0 运行基础、M1 清单/覆盖与截图处理、M2 离线 HTML 与 M3 DOCX/Markdown 导出已实现。浏览器自动操作和真实截图采集仍待完成。

安装与宿主要求见[安装指南](docs/INSTALLATION.md)。可用 `python scripts/package_skills.py` 生成保留完整运行目录的 Skills ZIP。

## 已确定的方向

- 面向企业级项目及开源项目，围绕软件各模块的实际使用编写操作手册。
- 以一套 Skills 交付，利用 AI 运行环境中的浏览器、终端及其他工具工作，无需额外部署常驻后端或数据库服务。
- 使用真实操作截图解释步骤，兼顾功能入口、前置条件、操作过程和预期结果。
- 以 HTML 作为主要阅读和交付界面，支持导出 Word（DOCX）和 Markdown。
- 当前按 M0–M4 逐步开发；完整图文手册闭环仍在开发中。

## 预期使用方式

向支持该技能包的 AI 提供项目地址或源码，以及可用的演示环境、账号角色和手册范围。AI 检查工具能力后，分析模块、规划操作流程、探索界面、采集证据、生成手册并检查遗漏。

源码模式可以整理模块和候选流程，但没有可访问的运行界面时，不能声称已完成操作验证，也不能编造截图。浏览器模式只能覆盖当前账号可见、可操作的范围。源码与运行环境同时可用时，可以交叉检查遗漏。

“无需部署服务”指 AutoScribeAI 自身不需要独立常驻服务；AI 宿主仍需提供相应工具，目标项目也需要可访问。安装依赖、启动目标项目、登录及测试数据准备应按实际环境处理。

## 开始使用（开发版）

需要 Python 3.10+，无需常驻服务或数据库。在仓库根目录执行：

```bash
python -m pip install -r requirements.txt
python scripts/autoscribe_cli.py validate project examples/project.json
python scripts/autoscribe_cli.py init examples/project.json --run-dir runs/demo --host examples/host.json
python scripts/autoscribe_cli.py status runs/demo
python -m unittest discover -s tests -v
# 生成未验证手册骨架和覆盖计划（示例清单仅作结构演示）
python scripts/autoscribe_cli.py analyze --config examples/project.json --inventory examples/inventory.json --manual-out runs/demo/manual.json --plan-out runs/demo/coverage-plan.json
python scripts/autoscribe_cli.py coverage --plan runs/demo/coverage-plan.json --inventory examples/inventory.json --config examples/project.json --manual runs/demo/manual.json --out runs/demo/coverage.json
# 截图安全派生：脱敏后另存；按需要添加 --redact/--callout/--crop 参数
python scripts/autoscribe_cli.py prepare-image /tmp/capture.png runs/demo/evidence/step-01.png --root runs/demo --redact 0.12,0.08,0.24,0.07 --callout 0.72,0.43
# 输出离线 HTML 目录包
python scripts/autoscribe_cli.py render-html --manual runs/demo/manual.json --coverage runs/demo/coverage.json --out-dir runs/demo/html
# 也可单独导出 Word 或 Markdown ZIP
python scripts/autoscribe_cli.py export-docx --manual runs/demo/manual.json --out runs/demo/manual.docx
python scripts/autoscribe_cli.py export-markdown --manual runs/demo/manual.json --out-zip runs/demo/manual-markdown.zip
```

示例只分析此仓库，不连接任何网站。实际使用时复制配置并填写项目来源、版本、角色、范围和允许动作；源码路径相对配置文件解析。已有任务使用 `resume`，不要重新初始化同一目录。

让 AI 从 [入口技能](skills/autoscribe-orchestrator/SKILL.md) 开始；五个技能共同引用根目录脚本、schemas 和 references，因此安装时须保留完整目录。可用打包脚本生成便携 ZIP；它不会自动安装到特定 AI 产品的全局技能目录。

| 能力 | 状态 |
| --- | --- |
| 配置、模型、ID/引用/截图摘要与路径校验 | 已实现 |
| 能力预检、源码模式降级、原子状态、阶段级恢复 | 已实现 |
| 候选清单导入、范围映射、模块/流程覆盖报告 | 已实现（M1 基础） |
| 截图裁剪、打码、编号标注与 SHA-256 证据准备 | 已实现（需 AI/人工指定坐标） |
| HTML 离线手册、目录搜索、图片放大、覆盖与质量报告 | 已实现 |
| 有副作用动作的登记、恢复阻断与明确核查后重试 | 已实现（仍需遵守技能流程） |
| 五个技能的职责和交接规范 | 已编写，完成源码模式试用 |
| DOCX 导出（含内嵌截图、图注与页码） | 已实现；需视觉复核输出 |
| Markdown ZIP 导出（相对图片资源） | 已实现 |
| HTML 下载 DOCX 与 Markdown 包 | 已实现 |
| 浏览器自动探索、真实截图采集、目标应用端到端验证 | 待实现 |
| 跨格式版式与章节一致性验收 | 进行中 |

HTML 离线阅读包包含 index.html、evidence/、manual.json、coverage.json、quality-report.json、manual.docx 和 manual-markdown.zip。Markdown ZIP 中的图片使用相对路径；DOCX 图片内嵌。结构校验不证明截图真实或内容正确；交付前仍需检查截图、DOCX 页面和内容一致性。文本敏感信息检测属于启发式规则，仍需人工审阅。详见 [运行约定](references/RUN_PROTOCOL.md)、[证据约定](references/EVIDENCE.md) 和 [清单格式](references/INVENTORY.md)。

## 文档入口

| 文档 | 内容 |
| --- | --- |
| [技术方案](docs/TECHNICAL_DESIGN.md) | 技能分工、执行流程、证据结构、HTML 与导出方案、边界和质量检查 |
| [开发任务](docs/ROADMAP.md) | 优先级、依赖、阶段交付、验收标准和当前状态 |

## 设计原则

1. 手册内容能够追溯到实际界面与操作证据；未知信息明确标注。
2. 高内聚、低耦合；按清晰职责拆分，避免庞大的单文件和无意义的层级。
3. 同一份结构化内容生成不同格式，避免 HTML、Word、Markdown 各自维护。
4. 探索过程可暂停、可恢复；覆盖范围和阻塞原因可见。
5. 不将测试账号密码、Cookie、令牌或未经脱敏的业务数据写入仓库或交付物。

## 方案记录

整理日期：2026-09-29。

依据：用户当前指令及可恢复的前次讨论。用户提供的分享链接本次未能直接读取，因此这里不是原对话的逐字归档。五个 Skill 的拆分、结构化中间模型、阶段安排等属于待验证的实现方案；上文“已确定的方向”是需求约束。
