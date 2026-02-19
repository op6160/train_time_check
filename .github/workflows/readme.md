# How to set Workflow 

[한국어](#개요) [日本語](#概要)

## 개요
- 서버 자원 없이도 스크립트를 자동화하여 사용할 수 있도록 Github Actions Workflow를 이용할 수 있다.
  
reusable_check.yml 은 스크립트를 워크플로우로 실행하기 위한 템플릿이며, 
schedule_evening.yml, schedule_morning.yml 은 reusable_check.yml 을 자동화하여 사용하는 예시이다.

---
## 설정방법
[schedule_evening.yaml](https://github.com/op6160/train_time_check/blob/main/.github/workflows/schedule_evening.yml)에서 발췌

### 환경 설정
- Discord Webhook을 사용해 알림을 수신하기 위해서는, 리포지토리 Secret변수에 WEBHOOK_URL 변수 설정이 필요함 <br>
리포지토리를 Fork한 경우, https://github.com/사용자id/train_time_check/settings/secrets/actions 에서 등록 가능 <br>
New repository secret 을 하고, Name: WEBHOOK_URL, Value: 사용할 Discord 채널 webhook url <br>
등록이 필요함

### 트리거 설정
```yaml
on:
  schedule:
   - cron: '00 08 * * 1-5'
   - cron: '30 08 * * 1-5'
  workflow_dispatch:
  push:
    branches:
      - dev
```
Github Actions는 여러가지 트리거를 설정할 수 있다. 자세한 내용은 [참조](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#using-a-single-event)  <br>
[cron](https://www.ibm.com/docs/en/aix/7.3.0?topic=c-crontab-command)은 자동화 스케쥴링으로, Gihtub actions의 경우 UTC+0을 기준으로 실행된다.  <br>
```00 08 * * 1-5``` 로 설정한 경우, KST(UTC+9) 기준, 월요일~금요일 17:00에 실행된다.
> ※ Github Actions의 cron은 불안정한데, 실행이 되지 않거나 지연되는 경우가 잦다.

### 권한설정
```yaml
permissions:
  contents: read
  issues: write
```
자동화 작업으로 리포지토리에 상호작용을 하기 위해서는, 권한 제공이 필요하다. 자세한 내용은 [참조](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#permissions) <br>
스크립트 실행을 위한 ```contents: read``` ,
이슈 작성을 위한 ```issues: write``` 를 제공하였다. <br>

### 스크립트 실행
```yaml
jobs:
  evening-check:
    uses: ./.github/workflows/reusable_check.yml
    with:
      direction: "up"
      target_station: "刈谷"
      range_n: "6"
      # enable_error_notification: "true"

    secrets:
      WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
reusable_check.yml 을 [재사용](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsuses)하는 형식으로 사용할 수 있다. <br>
reusable_check.yml 실행 시 ```with```를 통한 매개변수 선언이 필요하다.
```direction: up(하행: 豊橋→米原) or down(상행: 米原→豊橋)``` 도카이 구간에서의 직관적인 사용을 위해, up down의 동작을 교환하여 지정하였다.<br>
```target_station: "역 이름" ``` 기준점이 될 역의 역명을 입력. 일본어 역명만 지원된다. <br>
```range_n: "기준역으로부터 확인할 역 수" ``` 기준역으로부터 range에 지정된 앞 역 까지 구간을 체크한다. <br>
up, 刈谷, 6 으로 설정된 경우, 岡崎～刈谷 구간의 열차를 탐색한다.

---
## 概要
- サーバーリソースがなくてもスクリプトを自動化し使用できるように、Github Actions Workflow を利用が可能。

reusable_check.yml はスクリプトをワークフローで実行するためのテンプレートであり、
schedule_evening.yml、schedule_morning.yml は reusable_check.yml を自動化し実行する例である。

---
## 設定方法
[schedule_evening.yaml](https://github.com/op6160/train_time_check/blob/main/.github/workflows/schedule_evening.yml)から抜粋

### 환경 설정
- Discord Webhookを使用、通知を受信するためには、リポジトリの Secret変数に WEBHOOK_URL を登録する必要がある <br>
本リポジトリをForkした場合、https://github.com/ユーザーid/train_time_check/settings/secrets/actions で可能 <br>
New repository secret から, Name: WEBHOOK_URL, Value: Discordのチャンネル固有 webhook url <br>

### トリガー設定
```yaml
on:
  schedule:
   - cron: '00 08 * * 1-5'
   - cron: '30 08 * * 1-5'
  workflow_dispatch:
  push:
    branches:
      - dev
```
Github Actionsは様々なトリガーを設定が可能である。詳細仕様は[こちら](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#using-a-single-event)  <br>
[cron](https://www.ibm.com/docs/en/aix/7.3.0?topic=c-crontab-command)は自動化スケジューリング機能であり、Gihtub Actionsの場合、UTC+0をもとに実行される。  <br>
```00 08 * * 1-5``` に設定した場合、JST(UTC+9) 毎月、毎週、月曜~金曜のみ、17:00に実行される。
> ※ Github Actionsの cronは不安定であり、実行されない場合や、遅延する場合がある。

### 権限設定
```yaml
permissions:
  contents: read
  issues: write
```
自動化作業でリポジトリにインスタレーションするためには、権限設定が必要。詳細仕様は[こちら](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#permissions) <br>
スクリプトの実行のために ```contents: read``` 、
イシュー作成ための ```issues: write``` を提供した。 <br>

### スクリプト実行
```yaml
jobs:
  evening-check:
    uses: ./.github/workflows/reusable_check.yml
    with:
      direction: "up"
      target_station: "刈谷"
      range_n: "6"
      # enable_error_notification: "true"

    secrets:
      WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
reusable_check.yml を [再使用](https://docs.github.com/ja/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idstepsuses)する形で使用可能。 <br>
reusable_check.yml 実行の際 ```with```ブロック内でパラメータの設定が必要。
```direction: up(下行: 豊橋→米原) or down(上行: 米原→豊橋)``` 東海エリアでの直感的な私用のため、 up down の動作を交換している状態。<br>
```target_station: "駅名" ``` 基準になる駅の駅名を入力、日本語駅名のみ <br>
```range_n: "基準駅からの区間設定" ``` 基準駅から range に指定された駅までの区間をチェックする。  <br>
それぞれ 「up, 刈谷, 6」 に設定した場合、岡崎～刈谷 間の列車を探索する。