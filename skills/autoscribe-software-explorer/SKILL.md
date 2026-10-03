---
name: autoscribe-software-explorer
description: 在授权的测试环境观察软件操作流程并采集真实截图，用于 AutoScribeAI 的图文证据。处理登录接管、阻塞、结果检查和中断后的人工复核。
---

# 探索软件

读取 [运行约定](../../references/RUN_PROTOCOL.md) 与 [证据约定](../../references/EVIDENCE.md)。当前仅提供流程规范，浏览器操作由宿主工具执行，未提供自动采集适配器。

输入：已通过预检的 manifest、候选流程、角色与授权动作。

1. 使用当前宿主支持且已获授权的浏览器工具；不要绕过工具权限、验证码或登录接管。
2. 在动作前检查当前页面、角色和前置条件。默认只读；业务写入须在明确授权的动作和测试数据范围内。对写操作先运行 `action-begin` 写入日志，再执行一次；执行后立即使用 `action-resolve` 记录完成结果。恢复后先检查 `action-status` 及目标系统，只有确认未产生副作用并记录原因才允许重试。日志不能替代授权，也不能保护绕开本技能的手动点击。若授权不明确，先做无副作用观察再询问。
3. 每条计划流程开始前使用 `workflow-progress <run> --workflow <id> --status running --note <非敏感说明>`；每一步记录 action、location、expectedResult、actualResult。等待可观察的稳定结果；超时记录 blocked，不无限重试。流程结束后记录 completed 或 blocked，必须写核查说明。恢复时先检查流程进度与动作日志，不能直接再次点击提交。
4. 采集入口、关键表单和结果截图；使用真实工具输出。优先从宿主页面结构识别密码、密钥、邮箱和私人数据区域，人工核对所有需要遮盖的框。使用 `python <repo>/scripts/autoscribe_cli.py prepare-image <原图> <run>/evidence/<文件名>.png --root <run>` 派生 PNG。按需重复 `--redact x,y,w,h` 与 `--callout x,y`，或使用 `--crop x,y,w,h`；坐标按原图 0–1 比例。命令返回相对路径与 SHA-256；写入 Evidence 并建立双向引用。原图不会被改动。处理后逐张检查脱敏、标注位置和文字可读性。没有实际截图的步骤不得标成已验证。
5. 结果满足 successCriteria 且证据完整时才设置 workflow.status=verified。登录受阻、权限不足、缺数据或动作未获授权时设置 blocked 并记录原因。
6. 测试数据建立前按 `testDataPolicy` 设计非敏感演示场景；创建和删除都分别登记动作。完成后运行 `test-data-report <run>`，核对尚未清理的对象并按授权策略处理。恢复任务先核对已有业务结果，不仅依赖 checkpoint。交接步骤、证据及阻塞记录给 writer。
