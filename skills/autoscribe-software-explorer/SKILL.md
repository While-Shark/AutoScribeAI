---
name: autoscribe-software-explorer
description: 在授权的测试环境观察软件操作流程并采集真实截图，用于 AutoScribeAI 的图文证据。处理登录接管、阻塞、结果检查和中断后的人工复核。
---

# 探索软件

读取 [运行约定](../../references/RUN_PROTOCOL.md) 与 [证据约定](../../references/EVIDENCE.md)。当前仅提供流程规范，浏览器操作由宿主工具执行，未提供自动采集适配器。

输入：已通过预检的 manifest、候选流程、角色与授权动作。

1. 使用当前宿主支持且已获授权的浏览器工具；不要绕过工具权限、验证码或登录接管。
2. 在动作前检查当前页面、角色和前置条件。默认只读；业务写入须在明确授权的动作和测试数据范围内。若不明确，先保存无副作用的观察结果再询问。
3. 每一步记录 action、location、expectedResult、actualResult。等待可观察的加载完成或稳定结果；超时记录 blocked，不无限重试。写入后的超时先核查结果，不能直接再次点击提交。
4. 采集入口、关键表单和结果截图；使用真实工具输出。完成脱敏与可读性检查后，把 PNG/JPEG 放在任务目录 evidence 下，计算 SHA-256 并建立双向引用。没有实际截图的步骤不得标成已验证。
5. 结果满足 successCriteria 且证据完整时才设置 workflow.status=verified。登录受阻、权限不足、缺数据或动作未获授权时设置 blocked 并记录原因。
6. 恢复任务先核对已有业务结果，不仅依赖 checkpoint。交接步骤、证据及阻塞记录给 writer；不要承担排版与格式导出。
