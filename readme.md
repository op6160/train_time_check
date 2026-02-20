# 열차 운행 정보 알리미

이 프로젝트는 JR 센트럴(JR Central)의 홈페이지에서 열차 지연 및 운행 중단 정보를 확인하고, 지정된 디스코드 채널로 알림을 보내주는 시스템입니다. <br>
공식 푸시 알림 서비스의 부재로 인해 매번 웹사이트를 직접 확인해야 하거나, 역에 도착하고서야 열차의 지연 여부를 눈치채는, 출퇴근시 발생하는 번거로움을 해결하기 위해 개발되었습니다.<br>

이 프로젝트는 두 가지 자동화 방식을 지원합니다.<br>
1. Cron 자동화: 안정적인 정기/주기적 실행을 위한 권장 방식입니다. `ubuntu/` 디렉토리의 스크립트를 사용하여 설정할 수 있습니다.<br>
서버 또는 디바이스가 필요합니다.
> 동작이 확인된 OS: `mac 26.2` , `ubuntu 22.04`
2. GitHub Actions: 별도의 서버 환경이 없는 사용자를 위한 대안입니다. `.github/workflows/`의 `schedule_*.yml` 파일 내 `cron` 부분의 주석을 해제하여 활성화할 수 있으며, 리포지토리 코드 갱신 시 자동적인 디버깅 용도로도 사용됩니다.

## 주요 기능

-   **실시간 운행 정보 확인**: JR 중앙선 웹사이트의 정보를 스크래핑하여 현재 운행 상태를 확인합니다.
-   **지연 정보 파싱**: 열차 지연 발생 시, 상세 지연 정보(영향 구간, 시간 등)와 각 열차의 위치 정보를 추출합니다.
-   **다국어 지원**: 확인된 정보를 한국어, 일본어, 영어로 가공하여 제공합니다.
-   **디스코드 알림**: 서식이 적용된 운행 정보를 지정된 디스코드 채널에 웹훅을 통해 전송합니다.
-   **자동화 실행**: GitHub Actions 또는 서버 Cron job을 통해 특정 시간(예: 출퇴근 시간)에 자동으로 실행되도록 설정할 수 있습니다.
-   **타겟팅 기능**: 특정 역과 이동 방향(상행/하행)을 기준으로 관련 있는 열차 정보만 필터링하여 알림을 보낼 수 있습니다.
-   **오류 보고**: 새로운 오류 발생 시, Github에 issue를 자동으로 등록합니다.

## 동작 원리

1.  **데이터 수집 (Web Scraping)**:
    -   `requests` 또는 `selenium`을 사용하여 JR 중앙선의 운행 정보 페이지 HTML을 가져옵니다.
    -   (**`src/parse/rate_train_info.py`**)

2.  **정보 파싱 및 분석**:
    -   가져온 HTML을 `Beautifulsoup` 를 사용하여, 파싱해 전체 운행 상태가 '정상 운행'인지 확인합니다.
    -   지연이 발생한 경우, 공지 전문과 함께 지연된 각 열차의 종류, 목적지, 현재 위치, 지연 시간 등의 상세 정보를 추출합니다.
    -   (**`src/parse/train_info.py`**, **`src/parse/rate_train_info.py`**)

3.  **데이터 처리 및 가공**:
    -   추출된 원시 데이터를 필터링(특정 역, 방향 기준)하고, 다국어(ko, en, ja) 메시지로 변환합니다.
    -   (**`src/api.py`**, **`src/get_contents.py`**)

4.  **알림 전송**:
    -   가공된 메시지를 Discord 웹훅 URL로 POST 요청하여 사용자에게 알림을 보냅니다.
    -   (**`src/DiscordManager.py`**)

5.  **자동화**:
    -   **GitHub Actions**: `.github/workflows/` 내의 `schedule_morning.yml`, `schedule_evening.yml` 파일이 정해진 시간에 워크플로우를 트리거합니다.
    -   **Server (Cron)**: `ubuntu/` 디렉토리의 쉘 스크립트(`schedule_morning.sh` 등)를 사용하여 서버의 Cron job으로 등록하고 주기적으로 실행합니다.

## 프로젝트 구조

-   `.github/workflows/`: GitHub Actions를 위한 워크플로우 파일들이 위치함.
-   `src/`: 애플리케이션의 핵심 소스 코드가 들어있는 메인 디렉토리.
    -   `api.py`: 외부에서 호출할 API 함수들을 정의함.
    -   `parse/`: 웹사이트 데이터를 파싱하는 모듈.
        -   `rate_train_info.py`: 운행 정보 페이지 전체를 파싱하여 지연 상태 및 공지, 각 열차 정보를 추출함.
        -   `train_info.py`: 지연된 개별 열차의 상세 정보를 파싱함.
    -   `get_contents.py`: 파싱된 데이터를 사용자가 읽기 쉬운 다국어(ko, en, ja) 메시지로 가공하고 포맷팅함.
    -   `DiscordManager.py`: 메시지를 Discord 웹훅으로 전송하기 위한 매니저.
-   `ubuntu/`: Ubuntu 서버 환경에서 스크립트를 자동화하기 위한 쉘 스크립트들이 들어있는 디렉토리.
-   `config.py`: 스크래핑할 목표 URL, 파싱에 필요한 키워드 등 동작에 필요한 주요 설정 값들을 관리.
-   `requirements.txt`: 프로젝트 실행에 필요한 Python 패키지들의 목록.
-   `LICENSE`

## 주요 로직 흐름

1.  **실행 **: GitHub Actions의 스케줄러나 서버의 Cron job이 지정된 시간에 실행 스크립트(`reusable_check.yml` 또는 `reusable_check.py`)를 호출합니다.
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

## 주의 사항 및 면책 조항
* 본 프로젝트는 개인적인 학습 및 편의를 위해 제작된 비공식 오픈소스 프로젝트이며, 상업적 이용은 금지됩니다.

* 데이터 출처 및 권리: 제공되는 모든 열차 운행 정보의 원 저작권은 JR 센트럴(東海旅客鉄道株式会社)에 있습니다. 본 프로젝트는 원본 데이터의 소유권을 주장하지 않으며, 알림 전송 후 데이터를 별도로 저장하지 않습니다.

* 부하 방지: 타겟 웹사이트 서버에 무리를 주지 않도록 적절한 실행 주기(Cron 등)를 설정하여 사용해 주시기 바랍니다. 무분별한 짧은 주기 실행으로 인해 발생하는 IP 차단 등의 문제는 사용자 본인에게 있습니다.
  
* 공식 API가 아닌 웹 스크래핑을 활용하므로, 대상 웹사이트의 구조가 변경될 경우 예고 없이 정상 작동하지 않을 수 있습니다. 제공되는 정보의 100% 정확성이나 실시간성을 보장하지는 않습니다.