---
name: autoscribe-manual-writer
description: 将软件操作证据整理为统一 manual.json，写成面向用户的模块说明与操作步骤。用于 AutoScribeAI 手册编写及后续 HTML、Word、Markdown 导出前的内容准备。
---

# 编写手册内容

读取 [证据约定](../../references/EVIDENCE.md) 和 `schemas/manual.schema.json`。

输入：项目地图、流程、步骤、真实截图证据与已知限制。

1. 按模块组织章节，交代用途、角色、入口和前置条件。使用自然语言描述“在哪里操作、做什么、应看到什么”，保留原有业务术语。
2. 通过 workflowIds 和 stepIds 引用统一对象，不复制出多个不一致的步骤。只为 observed 步骤填写实际观察结果；推断与人工补充保留来源。
3. 输出 manual.json，保留所有范围内的未验证与阻塞项及原因。缺少截图时注明缺口，禁止用生成图片补充界面证据。
4. 执行 `python <repo>/scripts/autoscribe_cli.py validate manual <run>/manual.json`。修复悬空引用、路径和摘要问题，再交给 verifier。
5. 当前 M0 尚未实现 HTML、DOCX、Markdown 渲染。需要完整交付时把 export 阶段标为 blocked 并说明缺少导出器；不要把 JSON 改扩展名冒充 Word 或声称已有下载文件。
