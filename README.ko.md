# dbskill

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | 한국어 | [繁體中文](README.zh-TW.md)

> 창업가와 콘텐츠 제작자를 위한 중국어 AI Skills 도구 상자입니다. 실제 비즈니스, 콘텐츠, 실행 문제를 Agent 에게 전달하면 명확한 판단과 바로 시작할 수 있는 다음 행동을 얻을 수 있습니다.

[![Version](https://img.shields.io/badge/version-2.17.13-111111.svg)](VERSION)
[![Skills](https://img.shields.io/badge/Skills-29-111111.svg)](docs/新手入门.md#skill-全目录)
[![License](https://img.shields.io/badge/license-CC%20BY--NC%204.0-111111.svg)](LICENSE)

**豆包, WorkBuddy, Claude Code, Codex 및 Skills 를 지원하는 다른 Agent 에서 사용할 수 있습니다.**

dbskill 은 [dontbesilent](https://x.com/dontbesilent)가 만들었습니다. 공개 게시물 16,152 개에서 4,176 개의 구조화 지식 원자와 직접 호출할 수 있는 29 개의 Skills 를 정리했습니다.

[빠른 시작](#빠른-시작) · [설치](#설치) · [기능](#기능-목록) · [전체 가이드](docs/新手入门.md) · [릴리스](https://github.com/dontbesilent2025/dbskill/releases)

![dbskill 라우팅 맵](docs/skill-link-map.svg)

## dbskill 이 해결하는 문제

복잡한 방법론을 먼저 배울 필요가 없고, 어떤 도구를 호출할지 외울 필요도 없습니다. 현재의 비즈니스 상황, 자료, 선택, 막힌 지점을 `/dbs` 에 전달하면 대화 문맥에 맞춰 적절한 Skill 을 선택합니다.

| 상황 | 얻는 결과 |
| --- | --- |
| 고객이 비싸다고 말함 | 비즈니스 진단, 위험, 검증 행동 |
| 주제는 있지만 사람들이 볼 콘텐츠로 만들기 어려움 | 방향, 도입부, 제목, 대본 개선 |
| 해야 할 일은 알지만 진전이 없음 | 막힘의 분석과 시작할 수 있는 행동 1 개 |
| 같은 결정을 반복하지만 경험이 쌓이지 않음 | 의사결정 기록, 패턴, 스냅샷 |
| 원고, 주제, 사례가 흩어져 있음 | 유지 가능한 콘텐츠 자산 프로젝트 |

## 빠른 시작

설치 후 Agent 에 다음을 입력하세요.

```text
/dbs 저는 어린이 코딩 수업을 운영합니다. 유료 학생은 40 명이지만 재등록률이 낮습니다.
문제가 상품, 가격, 고객층 중 어디에 있는지 판단하고 싶습니다.
```

`/dbs` 는 현재 대화의 정보를 읽고 적절한 경로를 선택합니다. 한 번 작업한 뒤 새로운 사실이나 피드백을 추가하고 `/dbs` 를 다시 입력하면 다음에 할 일을 판단합니다.

작업 목적을 이미 알고 있다면 Skill 을 직접 호출할 수 있습니다.

```text
/dbs-diagnosis 육아 중인 엄마를 위한 정리 컨설팅을 합니다. 고객이 비싸다고 합니다. 무엇을 바꿔야 하나요?
/dbs-content “보통 사람은 개인 브랜딩을 서두르지 말아야 한다”는 주제를 콘텐츠로 만들고 싶습니다.
/dbs-hook 영상 대본의 첫 20 초입니다. 도입부를 개선해 주세요: …
/dbs-benchmark 기업 서비스 콘텐츠 계정을 연구하고 싶습니다. 어떤 벤치마크를 조사해야 하나요?
```

## 기능 목록

| 목표 | 주요 Skill | 대표 결과 |
| --- | --- | --- |
| 비즈니스, 상품, 가격, 고객 판단 | `/dbs-diagnosis` | 진단, 위험, 검증 계획 |
| 벤치마크 탐색과 연구 | `/dbs-benchmark` | 대상 목록과 연구 프레임 |
| 주제, 콘텐츠, 제목, 영상 제작 | `/dbs-content`, `/dbs-hook`, `/dbs-xhs-title` | 방향과 게시용 원고 |
| 공감, 논리, 확산성 점검 | `/dbs-resonate`, `/dbs-script-flow`, `/dbs-spread` | 우선순위가 있는 수정안 |
| 개념, 목표, 질문 명확화 | `/dbs-deconstruct`, `/dbs-goal`, `/dbs-good-question` | 검증 가능한 정의와 목표 |
| 미루기와 실행 정체 해결 | `/dbs-action`, `/dbs-slowisfast` | 정체 분석과 다음 행동 |
| 장기 의사결정 기록과 회고 | `/dbs-decision`, `/dbs-save`, `/dbs-restore`, `/dbs-report` | 로컬 기록과 보고서 |
| 콘텐츠 자산과 다중 Agent 환경 구축 | `/dbs-content-system`, `/dbs-agent-migration`, `/dbs-bridge` | 로컬 프로젝트와 연결 계획 |
| 로컬 폴더를 지식 베이스로 전환 | `/dbs-knowledge` | 지식 탐색, 버전 규칙, 바로 쓸 수 있는 질문 예시 |
| 로컬 Skill 위험 감사 | `/dbs-skill-cleaner` | 위험 보고서와 확인 후 격리 |

29 개 Skills 의 전체 목록, 입력 예시, 사용 흐름은 [전체 가이드](docs/新手入门.md#skill-全目录)에서 확인하세요.

## 설치

### 권장: Claude Code, 豆包, WorkBuddy, Codex 및 Skills 지원 Agent

터미널에서 실행합니다.

```bash
npx -y skills add dontbesilent2025/dbskill -g --all
```

Agent 로 돌아가 `/dbs 新手入门` 을 입력해 시작하세요.

### Claude Code 마켓플레이스

Claude Code 마켓플레이스를 통해 전체 도구 모음을 설치할 수도 있습니다.

```bash
claude plugin marketplace add dontbesilent2025/dbskill
claude plugin install dbs@dontbesilent-skills
```

`dbs` 플러그인에는 정식 비즈니스 Skill 29개와 `dbs-update` 시스템 항목 1개가 포함됩니다. Claude Code는 플러그인 Skill에 네임스페이스를 추가합니다. 메인 라우터는 `/dbs:dbs`, 개별 기능은 `/dbs:dbs-diagnosis`와 같은 명령을 사용합니다.

기능 하나만 설치하려면 해당 마켓플레이스 플러그인을 선택하세요. 예: `claude plugin install dbs-diagnosis@dontbesilent-skills`

![Claude Code 설치 데모](demo.gif)

### 업데이트

현재 Agent 에 다음처럼 말하세요.

```text
更新 dbskill
```

공식 dbskill 을 동기화하며, `~/.dbs/` 아래의 기록, 보고서, 의사결정 데이터는 변경하지 않습니다. 변경 사항은 [GitHub Releases](https://github.com/dontbesilent2025/dbskill/releases)에서 확인하세요.

## 작동 방식

```text
실제 작업
   ↓
/dbs 가 문맥을 읽고 현재의 진입점을 선택
   ↓
하나의 Skill 이 진단, 결과물 또는 기록을 생성
   ↓
결과와 피드백을 추가하고 다음 단계를 결정
```

## 지식 베이스와 로컬 기록

저장소에는 4,176 개의 구조화 지식 원자, Skill 별 방법론 문서, 고빈도 개념 용어집이 들어 있습니다.

- 데이터 범위와 필드는 [원자 라이브러리 안내](知识库/原子库/README.md)를 확인하세요.
- 자체 RAG 구축에는 `知识库/原子库/atoms.jsonl` 을 사용할 수 있습니다.
- 방법론은 [Skill 지식 팩](知识库/Skill知识包)에서 볼 수 있습니다.
- 대화를 이어서 작업하려면 `/dbs-save`, `/dbs-restore`, `/dbs-report` 를 사용하세요. 데이터는 `~/.dbs/` 에 로컬로 저장됩니다.

![dbskill 지식 파이프라인](docs/knowledge-pipeline.svg)

## 프로젝트 구조

```text
dbskill/
├── skills/                  # 공개된 29 개 Skills + 1 개 업데이트 항목
├── 知识库/                   # 지식 원자, 방법론, 용어집
├── docs/                    # 가이드, 다이어그램, 데모 자료
├── .claude-plugin/          # Claude Code 마켓플레이스 정의
└── tools/                   # 빌드와 유지보수 스크립트
```

로컬 배포 패키지는 다음으로 빌드합니다.

```bash
bash tools/build-skills.sh
```

패키지는 `dist/skills/` 에 생성됩니다. 이름에 `beta` 가 포함된 로컬 실험 Skill 은 제외됩니다.

## 작성자와 지원

작성자: [@dontbesilent](https://x.com/dontbesilent) · [샤오홍슈](https://xhslink.com/m/637xuspR4iI) · [더우인](https://v.douyin.com/pRUDhpBqOrc/)

유료 Q&A 지원은 QR 코드를 스캔하거나 [그룹 안내](https://mp.weixin.qq.com/s/RpwNjMo4M_er4GOrfCYt1g)를 확인하세요.

![유료 Q&A 그룹 QR 코드](docs/paid-qa-group-qrcode.png)

## 라이선스

[CC BY-NC 4.0](LICENSE)를 적용합니다.

- 개인 사용, 학습, 연구, 비상업 프로젝트에 사용할 수 있습니다.
- 파생 작업을 공개할 때는 출처를 표기해 주세요.
- 상업적 사용은 별도 허가가 필요합니다. 작성자에게 문의하세요.
