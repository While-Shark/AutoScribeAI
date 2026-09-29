# 三份公开项目样例手册

这些样例通过 AutoScribeAI 的项目分析、手册编写、流程核验技能制作，并从 `manual.json` 导出 HTML、DOCX 和 Markdown ZIP。每个项目固定到下表的 Git commit。

| 项目 | 手册语言 | 固定源码版本 | 许可证 | 实测截图 | 流程覆盖 |
| --- | --- | --- | --- | --- | --- |
| [Uptime Kuma](uptime-kuma/README.md) | 简体中文 | [`e7420f8`](https://github.com/louislam/uptime-kuma/commit/e7420f8fa546a8baa7ac4bf9d10a32545d4346e0) | MIT | [首次启动页面](uptime-kuma/screenshots/uptime-kuma-initial-setup.jpg) | 0/3；尚未创建管理员账户 |
| [changedetection.io](changedetection/README.md) | 日本語 | [`0e05667`](https://github.com/dgtlmoon/changedetection.io/commit/0e0566721b1c483dcf7ae548210ee10532d9b181) | Apache-2.0 | [官方公开页面](changedetection/screenshots/changedetection-public-homepage.jpg) | 0/3；公开页面转入付费订阅 |
| [IT Tools](it-tools/README.md) | 한국어 | [`d505845`](https://github.com/CorentinTh/it-tools/commit/d505845f918e946ec300af7b36efc107e2f66e9e) | GPL-3.0 | [JSON→YAML 实测截图](it-tools/output/evidence/ev-it-tools-json-yaml.jpg) | 1/3；JSON→YAML 已验证 |

## 查看导出结果

每个项目目录都有离线 HTML、Word、Markdown 压缩包、结构化手册和质量报告。打开样例目录中的 `output/` 即可查看。HTML 和 DOCX 已嵌入关联的实测截图；Markdown ZIP 也包含图片资源。Uptime Kuma 的截图显示首次启动要求创建管理员账户；为避免创建账号，流程未继续。changedetection.io 的截图显示官方公开站点的付费订阅入口，没有提交 URL 或付款。两个项目的功能流程因此保持未验证。

IT Tools 的 JSON→YAML 操作已在公开部署页面输入合成样例并观察转换结果。源码索引固定版本与公开部署版本未对齐；手册明确记录该限制。文本哈希与 QR 码仍未实测。三份质量报告均为 `ready: false`，表示仍有未验证流程。

每个样例保留配置、源码清单、手册、覆盖计划和运行状态，便于查看技能输入如何映射到导出。项目源码未复制进本目录；截图为本次浏览器实测页面。
