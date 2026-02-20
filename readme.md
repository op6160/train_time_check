> **이 프로젝트는 학습 목적으로 제작된 비공식 프로젝트이며, 상업적 사용을 금지합니다. 제공되는 정보의 정확성을 보장하지 않으므로 어떠한 법적 책임도 지지 않습니다.**

# 열차 운행 정보 알리미

이 프로젝트는 JR 센트럴의 열차 운행 정보를 웹 스크래핑하여, 지연 또는 운행 중단 중일 경우 디스코드로 알림을 보내는 자동화 시스템을 위한 프로젝트입니다.

## 주요 기능

-   **실시간 운행 정보 확인**: JR 중앙선 웹사이트의 정보를 스크래핑하여 현재 운행 상태를 확인합니다.
-   **지연 정보 파싱**: 열차 지연 발생 시, 상세 지연 정보(영향 구간, 시간 등)와 각 열차의 위치 정보를 추출합니다.
-   **다국어 지원**: 확인된 정보를 한국어, 일본어, 영어로 가공하여 제공합니다.
-   **디스코드 알림**: 서식이 적용된 운행 정보를 지정된 디스코드 채널에 웹훅을 통해 전송합니다.
-   **자동화 실행**: GitHub Actions 또는 서버 Cron job을 통해 특정 시간(예: 출퇴근 시간)에 자동으로 실행되도록 설정할 수 있습니다.
-   **타겟팅 기능**: 특정 역과 이동 방향(상행/하행)을 기준으로 관련 있는 열차 정보만 필터링하여 알림을 보낼 수 있습니다.

## 동작 원리

1.  **데이터 수집 (Web Scraping)**:
    -   `requests` 와 `BeautifulSoup4` (또는 `selenium`)를 사용하여 JR 중앙선의 운행 정보 페이지 HTML을 가져옵니다.
    -   (**`src/parse/rate_train_info.py`**)

2.  **정보 파싱 및 분석**:
    -   가져온 HTML을 파싱하여 전체 운행 상태가 '정상 운행'인지 확인합니다.
    -   지연이 발생한 경우, 공지 전문과 함께 지연된 각 열차의 종류, 목적지, 현재 위치, 지연 시간 등의 상세 정보를 추출합니다.
    -   (**`src/parse/train_info.py`**, **`src/parse/rate_train_info.py`**)

3.  **데이터 처리 및 가공**:
    -   추출된 원시 데이터를 필터링(특정 역, 방향 기준)하고, 다국어(ko, en, ja) 메시지로 변환합니다.
    -   (**`src/api.py`**, **`src/get_contents.py`**)

4.  **알림 전송**:
    -   가공된 메시지를 Discord 웹훅 URL로 POST 요청하여 알림을 보냅니다.
    -   (**`src/DiscordManager.py`**)

5.  **자동화**:
    -   **GitHub Actions**: `.github/workflows/` 내의 `schedule_morning.yml`, `schedule_evening.yml` 파일이 정해진 시간에 워크플로우를 트리거합니다.
    -   **Server (Cron)**: `ubuntu/` 디렉토리의 쉘 스크립트(`schedule_morning.sh` 등)를 사용하여 서버의 Cron job으로 등록하고 주기적으로 실행합니다.

## 프로젝트 구조

-   `.github/workflows/`: GitHub Actions를 위한 워크플로우 파일들이 위치합니다. `schedule_morning.yml` 같이 특정 시간에 스크립트를 실행시키는 역할을 합니다.
-   `src/`: 애플리케이션의 핵심 소스 코드가 들어있는 메인 디렉토리입니다.
    -   `api.py`: 전체 프로세스를 조율하는 메인 진입점 역할을 합니다. 외부에서 호출할 API 함수들을 정의합니다.
    -   `parse/`: 웹사이트의 HTML을 파싱하는 모듈들이 있습니다.
        -   `rate_train_info.py`: 운행 정보 페이지 전체를 파싱하여 지연 상태 및 공지, 각 열차 정보를 추출합니다.
        -   `train_info.py`: 지연된 개별 열차의 상세 정보를 파싱합니다.
    -   `get_contents.py`: 파싱된 데이터를 사용자가 읽기 쉬운 다국어(ko, en, ja) 메시지로 가공하고 포맷팅합니다.
    -   `DiscordManager.py`: 포맷팅된 메시지를 Discord 웹훅으로 전송하는 역할을 담당합니다.
-   `ubuntu/`: Ubuntu 서버 환경에서 Cron job으로 스크립트를 실행시키기 위한 쉘 스크립트들이 있습니다.
-   `config.py`: 스크래핑할 목표 URL, 파싱에 필요한 키워드 등 주요 설정 값들을 관리합니다.
-   `requirements.txt`: 프로젝트 실행에 필요한 Python 패키지들의 목록입니다.
-   `LICENSE`: 프로젝트의 오픈소스 라이선스(MIT)를 명시한 파일입니다.

## 주요 로직 흐름

1.  **실행 (Trigger)**: GitHub Actions의 스케줄러나 서버의 Cron job이 지정된 시간에 실행 스크립트(`reusable_check.yml` 또는 `reusable_check.py`)를 호출합니다.
2.  **API 호출**: 스크립트는 `src/api.py`에 정의된 `get_train_status_range_api`와 같은 함수를 호출하여 프로세스를 시작합니다. 이때, 확인하고자 하는 역, 방향, 언어 등의 파라미터를 전달합니다.
3.  **HTML 수집**: `src/parse/rate_train_info.py`가 JR 중앙 웹사이트에 접속하여 최신 운행 정보가 담긴 HTML 페이지를 가져옵니다.
4.  **운행 상태 확인**: 가져온 HTML을 분석하여 '정상 운행'인지, '지연'인지 먼저 판별합니다. 정상 운행일 경우, 알림 없이 프로세스를 종료합니다.
5.  **상세 정보 파싱**: 지연이 발생했을 경우, `BeautifulSoup4`를 이용해 지연 공지 내용과 각 열차의 정보를 추출합니다.
6.  **개별 열차 정보 추출**: `src/parse/train_info.py`가 각 열차의 HTML 조각으로부터 열차 종류, 목적지, 현재 위치, 지연 시간 등 구체적인 정보를 뽑아냅니다.
7.  **데이터 필터링**: `src/api.py`는 추출된 모든 열차 정보 중에서 사용자가 설정한 역과 방향(상행/하행)에 해당하는 것들만 걸러냅니다.
8.  **메시지 생성**: `src/get_contents.py`가 필터링된 데이터를 바탕으로 지정된 언어(ko, en, ja)에 맞춰 Discord로 보낼 최종 메시지를 생성합니다.
9.  **알림 발송**: `src/DiscordManager.py`가 생성된 메시지를 Discord 웹훅 URL로 전송하여 사용자에게 알림을 보냅니다.

## 설치 및 사용 방법

### 사전 요구사항

-   Python 3.x
-   `pip`
-   `git`

### 1. 로컬 환경에서 실행

1.  **프로젝트 클론 및 서브모듈 초기화**:
    ```bash
    git clone https://github.com/your-username/train_time_check.git
    cd train_time_check
    git submodule update --init --recursive
    ```

2.  **의존성 설치**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **환경 변수 설정**:
    -   `.env` 파일을 프로젝트 루트에 생성하고 Discord 웹훅 URL을 추가합니다.
      ```
      WEBHOOK_URL="https://discord.com/api/webhooks/your/webhook_url"
      ```

4.  **테스트 실행**:
    -   `src/api.py` 파일을 직접 실행하여 특정 조건의 결과를 콘솔에서 확인할 수 있습니다.
      ```python
      # src/api.py의 맨 아래 테스트 코드 수정
      result = get_train_status_range_api("刈谷", range_n=6, language="ko", direction="up")
      ...
      ```

### 2. GitHub Actions로 자동화

1.  **리포지토리 Fork**: 이 리포지토리를 자신의 GitHub 계정으로 Fork합니다.
2.  **Secrets 설정**:
    -   Fork한 리포지토리의 `Settings` > `Secrets and variables` > `Actions`로 이동합니다.
    -   `New repository secret`을 클릭하여 `WEBHOOK_URL`이라는 이름으로 자신의 Discord 웹훅 URL을 등록합니다.
3.  **워크플로우 활성화 및 수정**:
    -   `.github/workflows/`의 `schedule_*.yml` 파일에서 cron 스케줄의 주석을 해제하고 원하는 시간으로 설정합니다.
    -   `with` 섹션에서 `target_station`, `direction` 등의 파라미터를 자신의 환경에 맞게 수정합니다.
    -   변경 사항을 `main` 또는 `dev` 브랜치에 푸시하면 워크플로우가 활성화됩니다.

### 3. 서버(Ubuntu)에서 Cron으로 자동화

1.  **서버에 프로젝트 배포**: 로컬 환경과 동일하게 프로젝트를 클론하고 설정합니다.
2.  **실행 스크립트 수정**: `ubuntu/` 디렉토리의 `schedule_morning.sh`, `schedule_evening.sh` 파일에서 `TARGET_STATION`, `DIRECTION` 등 변수를 설정합니다.
3.  **Cron job 등록**:
    ```bash
    crontab -e
    ```
    -   에디터에서 아래와 같이 스케줄을 추가합니다 (매일 오전 7시 30분에 실행 예시)
      ```cron
      30 7 * * 1-5 /path/to/your/project/train_time_check/ubuntu/schedule_morning.sh
      ```

## 면책 조항 및 저작권 고지

-   **데이터 출처 및 저작권**: 이 프로젝트에서 제공하는 모든 정보의 원본 데이터 및 콘텐츠 저작권은 **JR 중앙(東海旅客鉄道株式会社)**에 있습니다. 본 프로젝트는 데이터의 소유권을 주장하지 않습니다.
-   **비공식 프로젝트**: 본 프로젝트는 JR 중앙과 제휴, 보증, 또는 어떠한 공식적인 관계도 없는 **순수 학습 목적의 비공식(Unofficial) 개인 프로젝트**입니다.
-   **비상업적 이용**: 본 프로젝트는 비상업적인 용도로만 사용되어야 하며, 어떠한 형태의 영리적 목적으로도 사용될 수 없습니다.
-   **데이터 비저장**: 이 애플리케이션은 스크래핑한 데이터를 외부 서버나 파일에 저장하지 않습니다. 정보는 알림 전송 목적으로만 일시적으로 메모리에서 처리되며, 프로세스 종료 시 즉시 휘발됩니다.
-   **정보의 한계와 책임**: 본 프로젝트는 공식 API가 아닌 웹 스크래핑 기술에 의존하므로, 원본 웹사이트의 구조 변경 시 예고 없이 기능이 중단될 수 있습니다. 제공되는 정보의 정확성이나 실시간성을 보장하지 않으며, 이로 인해 발생하는 모든 직접적, 간접적 손해에 대해 개발자는 어떠한 법적 책임도 지지 않습니다.
-   **스크래핑에 대한 책임**: 사용자는 본 프로젝트를 사용함으로써 JR 중앙 웹사이트에 과도한 부하를 주지 않고, 웹사이트의 서비스 약관(Terms of Service)을 존중할 책임이 있습니다. 본 프로젝트의 사용으로 인해 발생하는 모든 법적 문제(데이터 제공원에 대한 권리 침해 포함)의 책임은 전적으로 사용자에게 있습니다.
