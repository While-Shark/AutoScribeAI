# 内容与证据约定（schemaVersion 0.1）

`schemas/project.schema.json` 定义输入；`schemas/manual.schema.json` 定义 Project、Module、Feature、Workflow、Step、Evidence、Chapter 和 Manual。`manifest.schema.json` 定义运行状态。小写稳定 ID 在手册内全局唯一，不随着展示顺序变化。

- source=observed：本次实际观察；source=source：静态源码推断；source=human：人工补充。
- verified 流程必须有步骤，每一步都有 observed 来源、实际结果和截图引用。该结构规则只是必要条件，仍须检查截图与流程是否对应。
- 步骤顺序从 1 连续递增；workflow ↔ step、step ↔ evidence 双向引用必须一致；角色属于功能声明范围；章节只引用本模块的流程。
- evidence.path 使用任务目录内的相对路径，拒绝绝对路径、跨目录跳转与逃逸符号链接。首期只接受 PNG/JPEG 签名并核对 SHA-256；完整图像解码、尺寸与可读性在后续采集/质检任务处理。
- capturedAt 使用含时区的 ISO 时间；viewport 记录采集时视口，不等同于最终截图尺寸。page 使用脱敏 URL 或页面名称。
- redacted 表示图片是否经过脱敏处理；false 也可以是无需脱敏的公开页面，必须人工检查。M0 不做 OCR 或自动打码。
- 暂不把缺少证据的流程排进已验证教程；保留原范围及阻塞原因。校验器不自动生成覆盖率或质量报告，这属于 M1/M2。
- 截图摘要用于检测文件被替换，不能证明截图来源真实。不得使用生成图或示意图冒充实际界面证据。
