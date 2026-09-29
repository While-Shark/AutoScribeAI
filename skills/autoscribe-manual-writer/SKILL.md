---
name: autoscribe-manual-writer
description: 将软件操作证据整理为统一 manual.json，写成面向用户的模块说明与操作步骤。用于 AutoScribeAI 手册编写及后续 HTML、Word、Markdown 导出前的内容准备。
---

# 编写手册内容

读取 [证据约定](../../references/EVIDENCE.md) 和 `schemas/manual.schema.json`。

输入：项目地图、流程、步骤、真实截图证据与已知限制。所有面向读者的章节、步骤说明、FAQ 和限制说明均使用项目配置中的 `language`；保留软件界面上的菜单、按钮、字段和专有名词原文，必要时在首次出现时补充目标语言解释。

1. 按模块组织章节，交代用途、角色、入口和前置条件。仅在有可靠依据时加入常见问题；每条记录 source，并关联相关 workflow。source=observed 的 FAQ 必须引用已验证流程。使用自然语言描述“在哪里操作、做什么、应看到什么”，保留原有业务术语。
2. 通过 workflowIds 和 stepIds 引用统一对象，不复制出多个不一致的步骤。只为 observed 步骤填写实际观察结果；推断与人工补充保留来源。
3. 输出 manual.json，保留所有范围内的未验证与阻塞项及原因。缺少截图时注明缺口，禁止用生成图片补充界面证据。
4. 执行 `python <repo>/scripts/autoscribe_cli.py validate manual <run>/manual.json`。修复悬空引用、路径和摘要问题，再交给 verifier。
5. M2/M3 已实现 HTML、DOCX 和 Markdown ZIP 导出。先运行 analyzer 生成 coverage plan，保存并校验 manual.json 后执行 `python <repo>/scripts/autoscribe_cli.py coverage --plan <run>/coverage-plan.json --inventory <run>/inventory.json --config <config> --manual <run>/manual.json --out <run>/coverage.json`，再运行 `render-html --manual <run>/manual.json --coverage <run>/coverage.json --out-dir <new-output-directory>`。输出目录必须不存在，包含 index.html、evidence/、manual.json、coverage.json、quality-report.json、manual.docx 和 manual-markdown.zip。也可用 `export-docx --manual <run>/manual.json --out <new-file.docx>` 或 `export-markdown --manual <run>/manual.json --out-zip <new-file.zip>` 单独导出。交付前核对所有格式的章节与步骤，并检查 DOCX 渲染页面。
