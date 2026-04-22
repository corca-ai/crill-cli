# 내부 iOS 트라이얼 운영 메모

이 문서는 **참여자에게 직접 보여주는 문서가 아니라**, 대면 내부 개밥먹기
세션에서 진행자가 참고하는 운영 메모입니다. 실제로 참여자에게는 아래
Slack 문안만 보내고, 같은 회의실에서 설치와 첫 실행을 같이 봅니다.

핵심 설치 문서는 공개 raw URL 하나로 고정합니다.

`https://raw.githubusercontent.com/corca-ai/crill-cli/main/docs/install.md`

막히면 Slack `#crill-internal` 에 `crill doctor --json` 출력과 런 디렉터리
경로를 붙여 받습니다.

## 이 세션에서 확인할 것

먼저 아주 짧게 이렇게 설명합니다.

- `crill` 은 모바일 앱 UX 탐색과 경쟁사 변화 감지를 위한 CLI 입니다.
- 한 번의 스캔이 `scenario.yaml` 과 런 디렉터리라는 재사용 가능한 아티팩트를
  만들고, 그 결과를 이후 `report`, `replay`, `diff` 같은 흐름에 다시 씁니다.
- 이번 트라이얼의 목적은 "모든 기능 검증" 이 아니라, 에이전트가 설치부터 첫
  iOS 실기기 스캔과 리포트까지 무리 없이 끌고 가는지 보는 것입니다.

## 당일 진행 순서

### 1. 짧은 소개

`crill` 이 무엇을 하고 왜 만들었는지 1분 정도로만 설명합니다.

- 모바일 앱을 사람처럼 훑어보는 탐색형 에이전트다.
- 한 번 실행하고 끝나는 데모가 아니라, 결과를 런 아티팩트로 남긴다.
- 설치, 온보딩, 첫 스캔까지의 에이전트 UX 자체를 이번에 검증한다.

### 2. 설치 단계 시작

준비물을 확인한 뒤 이렇게 안내합니다.

- 테스트하고자 하는 저장소에서 터미널을 연다.
- Codex 또는 Claude Code 에이전트 세션을 새로 연다.
- 아래 문장을 그대로 붙여 넣는다.

```text
이 내용을 읽고 그대로 실행해줘: https://raw.githubusercontent.com/corca-ai/crill-cli/main/docs/install.md
```

이 단계에서는 진행자가 옆에서 설치 과정을 관찰하고, 필요하면 세션을 그대로
export 받습니다.

### 3. 설치 단계에서 기대하는 에이전트 행동

이 단계에서 기대하는 흐름은 아래와 같습니다.

- `brew install corca-ai/tap/crill` 로 바이너리를 설치한다.
- Gatekeeper 가 막으면 사람이 해야 하는 동작을 정확히 요구한다.
- `crill auth login <email>` 으로 로그인까지 자연스럽게 유도한다.
- `@corca.ai` 주소라면 activation code / invitation key 없이 로그인돼야 한다.
- 사람 개입이 필요한 단계는 에이전트가 스스로 우회하지 말고 정확히 요청한다.
- `crill skills install` 까지 끝낸다.
- 마지막에 `crill doctor` 또는 `crill doctor --json` 으로 상태를 확인한다.
- 끝나면 "이제 새 세션에서 `crill` skill 을 실행해 보세요" 라고 안내한다.

호스트마다 skill 호출 표기가 다를 수 있으므로, 기본 원칙은 **현재 에이전트가
안내하는 표기대로 `crill` skill 을 실행**하는 것입니다. 예시로는 Claude Code
에서 `/crill`, Codex 에서 `$crill` 을 기대할 수 있습니다.

### 4. 다음 세션에서 기대하는 흐름

새 세션에서 참여자가 `crill` skill 을 아무 파라미터 없이 실행하면, 기대하는
흐름은 아래와 같습니다.

- skill 이 먼저 `crill doctor --json` 으로 현재 상태를 읽는다.
- skill 이 자기 `references/onboarding.md` 계약을 읽고 첫 미완료 단계부터 이어간다.
- 첫 skill 실행 상태라면 온보딩 경로로 들어간다.
- 아직 iOS 기기 선택이 안 되어 있으면 `crill setup --ios` 를 진행한다.
- 앱을 무엇을 테스트할지 물어본다.
- `crill ios apps --json` 으로 설치된 앱을 보고 앱 이름 또는 bundle id 를
  해석한다.
- 첫 스캔을 실행한다.
- 스캔이 끝나면 `crill report <run-dir>` 로 리포트를 띄운다.

## 첫 스캔 기대값

첫 스캔은 좁고 단순해야 합니다.

- iOS 실기기 1대
- 앱 1개
- 작은 한계값 (`--max-actions 10 --max-states 10`)
- 첫 판은 예산 비교나 `diff` 를 붙이지 않는다

첫 실행에서 "로그인 전까지만 탐색" 같은 우회 흐름을 만들기보다, 로그인 후
좁은 첫 실기기 스캔 1회를 성공시키는 쪽을 우선합니다.

## 진행자가 볼 포인트

- 설치 문서 하나만으로 설치, 로그인, skill 설치까지 가는가
- `@corca.ai` 로그인에서 activation code 없이 자연스럽게 들어가는가
- 에이전트가 사람 개입이 필요한 순간을 정확히 구분하는가
- provider 를 어떻게 감지했고 무엇을 쓰겠다고 말하는지가 충분히 자연스러운가
- 새 세션 handoff 가 자연스러운가
- `crill` skill 첫 실행이 `doctor` 기반으로 온보딩에 들어가는가
- 앱 선택 뒤 첫 `scan -> report` 경로가 실제로 닫히는가

## 참여자에게 보낼 Slack 문안

```md
내일 `crill` 내부 iOS 트라이얼 세션이 있어요.

`crill` 은 모바일 앱 UX 탐색과 경쟁사 변화 감지를 위한 CLI 입니다. 이번
세션에서는 "한 번의 스캔이 재사용 가능한 런 아티팩트를 만들고, 그걸 report
등으로 이어서 볼 수 있는가" 와 "에이전트가 설치부터 첫 실행까지 자연스럽게
끌고 가는가" 를 같이 봅니다.

준비물:
- 맥북
- 아이폰 + 케이블
- 시스템 설정에 로그인된 Apple ID
- 아이폰에 이미 설치된 대상 앱
- Homebrew

세션이 시작되면 테스트하고 싶은 저장소에서 터미널을 열고, Codex 또는
Claude Code 에 아래 문장을 그대로 넣어 주세요.

이 내용을 읽고 그대로 실행해줘: https://raw.githubusercontent.com/corca-ai/crill-cli/main/docs/install.md

설치가 끝나면 에이전트가 새 세션에서 `crill` skill 을 실행하라고 안내할
예정입니다. 같은 회의실에서 같이 진행할 테니, 중간에 사람 개입이 필요한
단계가 나오면 그때 같이 처리하면 됩니다.

막히면 Slack `#crill-internal` 에 아래 두 가지를 보내 주세요.
- `crill doctor --json` 출력
- 런 디렉터리 경로
```
