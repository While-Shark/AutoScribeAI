# 内容与证据约定（schemaVersion 0.1）

`schemas/project.schema.json` 定义输入；`schemas/manual.schema.json` 定义 Project、Module、Feature、Workflow、Step、Evidence、Chapter 和 Manual。`manifest.schema.json` 定义运行状态。小写稳定 ID 在手册内全局唯一，不随着展示顺序变化。

- source=observed：本次实际观察；source=source：静态源码推断；source=human：人工补充。
- verified 流程必须有步骤，每一步都有 observed 来源、实际结果和截图引用。该结构规则只是必要条件，仍须检查截图与流程是否对应。
- 步骤顺序从 1 连续递增；workflow ↔ step、step ↔ evidence 双向引用必须一致；角色属于功能声明范围；章节只引用本模块的流程。
- evidence.path 使用任务目录内的相对路径，拒绝绝对路径、跨目录跳转与逃逸符号链接。首期只接受 PNG/JPEG 签名并核对 SHA-256；完整图像解码、尺寸与可读性在后续采集/质检任务处理。
- capturedAt 使用含时区的 ISO 时间；viewport 记录采集时视口，不等同于最终截图尺寸。page 使用脱敏 URL 或页面名称。
- redacted 表示图片是否经过脱敏处理；false 也可以是无需脱敏的公开页面，必须人工检查。M0 不做 OCR 或自动打码。
- 页面结构可帮助提出敏感区域，但截图脱敏使用显式坐标；逐张核对处理后的像素和原图留存策略。
- 暂不把缺少证据的流程排进已验证教程；保留原范围及阻塞原因。校验器不自动生成覆盖率或质量报告，这属于 M1/M2。
- 截图摘要用于检测文件被替换，不能证明截图来源真实。不得使用生成图或示意图冒充实际界面证据。


## 截图派生处理（T11）

将宿主采集的原图保存为临时输入；使用 `prepare-image` 另存经过检查的 PNG 证据，不覆盖源图。坐标为基于原图宽高的 0–1 比例，方便不同分辨率复用：

```bash
python scripts/autoscribe_cli.py prepare-image \
  /tmp/capture.png runs/demo/evidence/step-01.png --root runs/demo \
  --redact 0.12,0.08,0.24,0.07 --callout 0.72,0.43
```

命令返回相对证据根目录的路径、尺寸、脱敏框数、标记数和 SHA-256；据此填写 Evidence 对象。重复 `--redact` 或 `--callout` 可增加区域。打码使用实色覆盖，避免可逆模糊暴露敏感数据；标号按参数顺序生成，截图正文中应按同号解释步骤。标记点表示实际界面位置，不验证用户选择的坐标是否正确。

超 4000 万像素的图片会被拒绝，以控制本地内存占用。EXIF 方向会先校正，输出 PNG 不包含原图 EXIF。此工具供人工/AI 指定框和点后确定性处理；没有 OCR、人脸识别、自动脱敏或截图采集。处理后仍需逐张检查遮盖是否完整、标号是否准确及文字是否可读。原图只有在工作区受控且按项目策略完成人工复核/清理后保存；本脚本不自动清理原图。


## HTML 输出目录包（M2）

`render-html` 要求手册与覆盖报告匹配。覆盖报告按 manual.json 字节摘要绑定；手册变化后须重新生成覆盖报告。输出目录需为新路径，避免覆盖已有内容。交付包括 `index.html`、`evidence/`、`manual.json`、`coverage.json` 和 `quality-report.json`。

页面包含模块目录、浏览器本地关键词搜索、响应式版式、截图对话框放大及范围/模块覆盖表。不加载 CDN、外部脚本、字体或图片。图片保存在相对路径，移动整个 HTML 输出文件夹后保持离线可用。质量报告中的 ready 只表示所有计划流程都在结构上标为 verified、没有限制说明；仍需人工审阅真实性和 HTML 视觉效果。

模块章节可带可选 `faqs`。每条常见问题记录 question、answer、source，可列出相关 workflowIds。只有能从已验证流程得到支持的答案才标记 source=observed；源码推断或人工补充须显式标记。HTML、DOCX 和 Markdown 均从同一字段渲染。


## Word 与 Markdown 导出（M3）

`render-html` 同时生成 `manual.docx` 与 `manual-markdown.zip` 并在页面顶部提供下载链接。也可分别调用 `export-docx` 和 `export-markdown`。DOCX 把截图作为文档内图片嵌入，Markdown ZIP 包含 `README.md` 和 `assets/<evidence-id>.<ext>`，图片链接为相对路径。导出基于同一份已校验的 `manual.json`；输出文件已存在时拒绝覆盖。DOCX 需在交付前渲染并检查分页，不能只以文件可打开视为版式合格。

交付后运行 `audit --manual <manual.json> --coverage <coverage.json> --package <HTML目录> --out <任务目录/audit-report.json>` 检查图像解码、HTML 链接及锚点、DOCX/Markdown 包完整性。审计报告必须放在交付目录之外。机械检查通过后仍需视觉与隐私复核。HTML 可按角色筛选；Word/Markdown 单独导出可加 `--role <role-id>`。
