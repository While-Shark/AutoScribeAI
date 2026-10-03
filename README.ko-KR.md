# AutoScribeAI

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja-JP.md) | [한국어](README.ko-KR.md)

## 프로젝트를 AI에 전달하고, 실제로 사용할 수 있는 이미지 매뉴얼을 생성\n\n프로젝트, 접근 가능한 테스트 환경, 문서화할 워크플로를 AI에 제공하면 AutoScribeAI가 모듈 분석, 승인된 UI의 실제 조작, 스크린샷 수집, 실제 결과 기록, 매뉴얼 출력을 안내합니다.\n\n**AutoScribeAI 전용 백엔드는 필요하지 않습니다. 한 번의 실행으로 Offline HTML, Word / DOCX, Markdown, 커버리지 보고서를 만들 수 있습니다.**\n\n프로젝트 납품, 신규 사용자 온보딩, 사내 시스템, 오픈소스 문서, 고객 교육, 인수 자료, 릴리스 후 매뉴얼 갱신에 실용적입니다.\n\n### Demo Gallery\n\n3개의 실제 프로젝트 샘플을 한 페이지에서 비교할 수 있는 Vercel-ready Gallery를 추가했습니다. 생성된 HTML 매뉴얼과 실제 Word 문서를 바로 확인할 수 있습니다.\n\n- Uptime Kuma — 简体中文 — **3/3 verified**\n- changedetection.io — 日本語 — **0/3 verified**, 유료 흐름으로 막힌 상태를 그대로 보존\n- IT Tools — 한국어 — **1/3 verified**, 실제 관찰과 소스 기반 후보를 구분\n\nGallery: [`demo/`](demo/) · Vercel: [`vercel.json`](vercel.json) · Samples: [`tests/manual_samples`](tests/manual_samples/README.md)\n## 핵심 설계

- HTML을 기본 읽기 경험으로 사용
- `manual.json`을 단일 기준 데이터로 사용
- 실제 실행 결과와 스크린샷 증거가 있을 때만 검증 완료로 표시
- 상시 실행 서버가 필요 없는 5개 Skills + 로컬 스크립트 구조
- 체크포인트 기반으로 중단된 작업을 안전하게 재개

## Skills

- `autoscribe-orchestrator` — 계획, 시작, 재개, 전체 조정
- `autoscribe-project-analyzer` — 모듈, 기능, 역할, 후보 워크플로 분석
- `autoscribe-software-explorer` — 실제 UI 조작 및 증거 수집
- `autoscribe-manual-writer` — 증거를 `manual.json`으로 정리
- `autoscribe-manual-verifier` — 출처, 참조, 커버리지, 품질 검증

## 언어

- English — `en-US` **기본값**
- 简体中文 — `zh-CN`
- 日本語 — `ja-JP`
- 한국어 — `ko-KR`

프로젝트 설정에서 `language`를 생략하면 `en-US`가 사용됩니다. 다른 BCP-47 언어도 AI 본문 작성에 사용할 수 있으며, 고정 템플릿 라벨은 영어로 폴백합니다.

## 빠른 시작

```bash
python -m pip install -r requirements.txt
python scripts/package_skills.py --output dist/autoscribeai-skills.zip
```

AI에는 `skills/autoscribe-orchestrator/SKILL.md`부터 읽도록 요청하세요. 실제 스크린샷을 생성하려면 AI 호스트에 승인된 브라우저 또는 Computer Use 기능이 필요합니다.

실제 예시는 [tests/manual_samples](tests/manual_samples/README.md), 자세한 사용법은 [Installation](docs/INSTALLATION.md)을 참고하세요.
