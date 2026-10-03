# AutoScribeAI

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja-JP.md) | [한국어](README.ko-KR.md)

## 실제 소프트웨어 사용 과정을 증거 기반 이미지 매뉴얼로 변환

AI에 프로젝트, 접근 가능한 테스트 환경, 문서화할 워크플로를 제공하면 AutoScribeAI가 프로젝트 분석, 승인된 UI 조작, 실제 스크린샷 수집, 증거 저장, 사용자 매뉴얼 생성 절차를 안내합니다.

**한 번의 워크플로로 오프라인 HTML, Word, Markdown을 생성할 수 있습니다. 기본 출력 언어는 영어이며 중국어 간체, 일본어, 한국어 템플릿을 기본 제공합니다.**

## 핵심 설계

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
