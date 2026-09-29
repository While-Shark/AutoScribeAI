---
name: autoscribe-manual-verifier
description: 核对 AutoScribeAI 手册的结构、证据引用、截图、敏感信息与覆盖缺口。用于交付前检查，也用于恢复任务后复核已有内容。
---

# 核验手册

读取 [证据约定](../../references/EVIDENCE.md) 与 [运行约定](../../references/RUN_PROTOCOL.md)。

输入：manifest、manual.json、全部证据与已生成的格式文件。

1. 运行 manual 校验器。结构通过不代表截图真实、内容正确或已脱敏；逐张查看截图，核对页面、步骤、实际结果和文字可读性。
2. 运行 `python <repo>/scripts/autoscribe_cli.py coverage --plan <run>/coverage-plan.json --inventory <run>/inventory.json --config <config> --manual <run>/manual.json --out <run>/coverage.json`。核对每个模块和每项原始范围的计划数、已验证、未验证和阻塞数。分母来自分析时的清单；零分母显示不适用。报告拒绝被删掉或额外增加的流程。
3. 检查账号、令牌、个人信息和业务数据。文本启发式检测不能代替人工检查。未脱敏资源不得进入交付包。
4. 对实际存在的 HTML、DOCX、Markdown 检查章节、步骤、图片和链接一致性；HTML 离线与窄屏检查，DOCX 渲染检查。M0 无导出器，不把这些检查标成通过。
5. 输出 `quality-report.json`，逐项记录 passed/failed/blocked、发现与修复建议；报告格式目前为约定草案。存在缺口时明确交付限制，缺失格式不能算全部验收。
