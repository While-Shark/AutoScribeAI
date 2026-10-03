# AutoScribeAI

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja-JP.md) · [한국어](README.ko-KR.md)

> 소프트웨어 프로젝트를 AI에 전달하면 실제 스크린샷이 포함된 사용자 매뉴얼을 생성합니다.

**Live Demo:** https://auto-scribe-ai-tau.vercel.app/?lang=ko

AutoScribeAI는 프로젝트 분석, 승인된 UI 조작, 스크린샷 수집, 실제 결과 기록을 거쳐 **HTML, Word / DOCX, Markdown**을 출력하는 휴대형 Skill Pack입니다.

AutoScribeAI 전용 백엔드는 필요하지 않습니다.

## 먼저 결과 보기

Live Demo에는 실제 프로젝트 3개가 포함되어 있습니다.

| Project | Language | Verified |
| --- | --- | --- |
| Uptime Kuma | 简体中文 | **3/3** |
| changedetection.io | 日本語 | **0/3**. 막힌 이유를 보존하고 실행하지 않은 절차를 만들지 않음 |
| IT Tools | 한국어 | **1/3**. 실제 관찰과 소스 기반 후보를 구분 |

**[Open Live Demo →](https://auto-scribe-ai-tau.vercel.app/?lang=ko)**

생성된 HTML 매뉴얼, 실제 Word 문서, 스크린샷, 검증 상태를 바로 볼 수 있습니다.

## 결과물

- **Offline HTML**
- **Word / DOCX**
- **Markdown**
- **Coverage / Quality report**
- **검토 도구**: 역할별 보기, 중단된 작업 재개, 버전 변경 검토, 결과물 링크 검사.

실제 조작 결과와 증거가 없는 워크플로는 verified로 표시되지 않습니다.

## 사용 방법

```bash
git clone https://github.com/While-Shark/AutoScribeAI.git
cd AutoScribeAI
python -m pip install -r requirements.txt
```

이 디렉터리에서 AI Agent를 실행하고 다음과 같이 요청합니다.

```text
Read skills/autoscribe/SKILL.md and use AutoScribeAI
to generate a complete illustrated user manual.
```

<details>
<summary><strong>Codex</strong></summary>

AutoScribeAI 루트에서 `codex`를 실행하고 `skills/autoscribe/SKILL.md`를 읽도록 요청합니다.

</details>

<details>
<summary><strong>Claude Code</strong></summary>

AutoScribeAI 루트에서 `claude`를 실행하고 autoscribe Skill을 읽도록 요청합니다.

Claude Code는 native Skills를 지원하지만 AutoScribeAI는 공용 scripts / schemas / references를 사용하므로 전체 저장소를 유지하는 방식이 가장 단순합니다.

</details>

<details>
<summary><strong>Pi</strong></summary>

AutoScribeAI 루트에서 Pi를 실행하고 `skills/autoscribe/SKILL.md`를 읽게 합니다. Pi는 Agent Skills / `SKILL.md`를 지원합니다.

</details>

<details>
<summary><strong>Agy / Google Antigravity</strong></summary>

AutoScribeAI 루트에서 `agy`를 실행하고 autoscribe Skill을 읽게 합니다. Antigravity는 Agent Skills를 네이티브 지원합니다.

</details>

<details>
<summary><strong>OpenCode</strong></summary>

AutoScribeAI 루트에서 OpenCode를 실행하고 autoscribe Skill을 읽게 합니다. OpenCode는 `SKILL.md` 및 Agent Skills를 지원합니다.

</details>

<details>
<summary><strong>Other agents</strong></summary>

Cursor, Cline, Roo Code, Gemini CLI 등도 파일 읽기와 명령 실행이 가능하면 사용할 수 있습니다.

전체 AutoScribeAI 디렉터리를 워크스페이스로 열고 autoscribe Skill을 읽도록 요청하면 됩니다.

</details>

## Languages

- **English — `en-US` (default)**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

## Links

- [Live Demo](https://auto-scribe-ai-tau.vercel.app/?lang=ko)
- [Samples](tests/manual_samples/README.md)
- [Installation](docs/INSTALLATION.md)
- [Technical design](docs/TECHNICAL_DESIGN.md)
