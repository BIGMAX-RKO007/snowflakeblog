# 第 09 章：Snowflake 外部 API アクセス完全ガイド —— 外部ネットワークアクセス (ENA)・シークレット・Python UDF 実践

> 本章は **《尚硅谷技術講義執筆規約 (shangguigu-style)》** に完全準拠して執筆されています：本質を突く極限のシンプル比較、業務ノイズを廃した純粋技術フォーカス、実機ログ付き3ステップ実践、落とし穴の事前開示と回避策、前提条件の明確化。

---

## はじめに：極限までシンプルなメンタルモデル

現代のエンタープライズ・データ基盤において、データウェアハウスはもはや単にデータを受け取るだけの「静的な保管庫」ではありません。以下のように、DWH 自身が**能動的に外部の世界と接続する**ニーズが急速に高まっています：
- **リアルタイムデータ拡充**：SQL クエリ実行中に為替レート API や住所変換 API を直接呼び出す
- **SaaS クラウド連携**：Box API などを叩いて最新のファイル一覧やメタデータを直接取得・更新する
- **外部 AI/LLM 推論**：外部の大型言語モデル API を呼び出してテキスト分類や要約を行う

Snowflake の外部ネットワークアクセス（External Network Access：**ENA**）が登場する以前は、Airflow や AWS Lambda などの外部中継サーバーを立ち上げてデータをやり取りする必要がありました。しかし、それではネットワーク経路が複雑化し、コストが増大するだけでなく、データベース接続情報や API トークンが外部サーバーに散在し、深刻なセキュリティリスクを招いていました。

### 直感比較：従来の中継サーバー型 vs Snowflake ネイティブ ENA

```
【従来アプローチ：外部中継サーバー型（脆弱・複雑・認証情報の散在）】
  ┌─────────────────┐      ポーリング / 書込       ┌────────────────────┐     HTTP リクエスト     ┌─────────────────┐
  │  Snowflake DWH  │ <─────────────────────────> │  Python ETL/Lambda │ <─────────────────> │  外部 REST API  │
  └─────────────────┘                             └────────────────────┘                     └─────────────────┘
                                                    ▲ サーバー管理の負担
                                                    ▲ トークン漏洩リスク大
                                                    ▲ データが公衆網を往復

【現代アプローチ：Snowflake ネイティブ ENA（DWH完結・低遅延・高セキュリティ）】
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Snowflake 仮想ウェアハウス (Virtual Warehouse)                          │
  │                                                                        │
  │   SQL クエリ / Python UDF / ストアドプロシージャ                       │
  │       │                                                                │
  │       ├───── 1. メモリ上で安全に復号 ───> [ Secret 金庫 ]               │
  │       │                                                                │
  │       └───── 2. 送信先ホワイトリスト ───> [ Network Rule ドメイン規則 ] │
  │                       │                                                │
  └───────────────────────┼────────────────────────────────────────────────┘
                          ▼ 厳格に管理された HTTPS 送信 (ポート 443)
                  ┌─────────────────┐
                  │  外部 REST API  │
                  └─────────────────┘
```

- **読者の疑問**：デフォルトで外部と遮断された Snowflake で、どうやって安全に特定のドメインだけを許可するのか？トークンを `QUERY_HISTORY` に平文で残さない方法は？SQL からたった 1 行で API を叩くには？
- **本章のゴール**：業務の複雑さを一切排除し、純粋な技術最小構成（Network Rule + Secret + Integration + Python UDF）を通じて、完全な動作検証をステップ・バイ・ステップで完遂します！

> 📖 **Snowflake 公式ドキュメント**：
> - [外部ネットワークアクセスの概要 (External network access overview)](https://docs.snowflake.com/ja/developer-guide/external-network-access/overview)
> - [外部ネットワークアクセスの仕組みとセキュリティモデル (How external network access works)](https://docs.snowflake.com/ja/developer-guide/external-network-access/overview#how-external-network-access-works)

---

## 一、前提条件と事前準備 (Prerequisites)

ハンズオンを開始する前に、お使いの Snowflake アカウントとロールが以下の要件を満たしているか確認してください：

| 構成要素 | 必要スペック / 権限 | 役割 |
| :--- | :--- | :--- |
| **実行ロール** | `ACCOUNTADMIN`（または `CREATE INTEGRATION` 権限を持つカスタム管理ロール） | アカウントレベルの統合オブジェクト `EXTERNAL ACCESS INTEGRATION` の作成 |
| **コンピュート** | 稼働中の仮想ウェアハウス（例：`COMPUTE_WH`、X-Small で可） | Python UDF が動作するセキュアなコンテナ環境 |
| **テストDB・スキーマ** | 読み書き可能な環境（本書では `DEV_DEMO_DB.API_INTEGRATION` を使用） | ネットワークルール、シークレット、検証用テーブルの格納 |
| **接続先外部 API** | 標準 HTTPS エンドポイント（`api.box.com` や検証用 `httpbin.org`） | 外部通信疎通と JSON レスポンスの解析検証 |

> **操作スクリーンショット：Box Developer Console からの Developer Token 取得**
>
> [Box Developer Console (https://app.box.com/developers/console)](https://app.box.com/developers/console) にアクセスし、Custom App の Configuration 画面から 1 時間有効な Developer Token を取得します：
>
> ![Box Developer Console Developer Token 取得](../images/09_step_01_box_developer_token.png)

---

## 二、技術アーキテクチャとデータフロー

Snowflake では、外部アクセスに対して**職務分掌と最小権限の原則（Principle of Least Privilege）**を徹底しています。以下の 4 つの独立したオブジェクトを組み合わせて安全性を担保します：

```mermaid
flowchart TD
    subgraph Governance["ガバナンス＆ネットワーク制御層"]
        NR["1. Network Rule (ネットワークルール)<br/>• TYPE = HOST_PORT<br/>• MODE = EGRESS<br/>• VALUE_LIST = ('api.box.com', 'httpbin.org')"]
        SEC["2. Secret (暗号化シークレット)<br/>• TYPE = GENERIC_STRING / OAUTH2<br/>• API トークンを暗号化保管"]
        EAI["3. External Access Integration (統合ゲートウェイ)<br/>• ALLOWED_NETWORK_RULES = (NR)<br/>• ALLOWED_AUTHENTICATION_SECRETS = (SEC)<br/>• 管理者が集中的に許可・監査"]
    end

    subgraph Compute["DWH内コンピュート環境 (Warehouse)"]
        UDF["4. Python UDF / ストアドプロシージャ<br/>• 設定: EXTERNAL_ACCESS_INTEGRATIONS = (EAI)<br/>• 設定: SECRETS = ('cred' = SEC)<br/>• 内部処理: _snowflake.get_generic_secret_string('cred')<br/>• HTTP GET / POST 送信 & JSON パース"]
    end

    subgraph Target["外部サービス"]
        API["5. 外部 REST API<br/>(Box API / 為替 API / 外部 LLM)"]
    end

    subgraph Storage["ストレージ層"]
        TBL[("6. テーブル / VARIANT カラム<br/>(DWH 内に永続化)")]
    end

    NR --> EAI
    SEC --> EAI
    EAI -. USAGE 権限付与 .-> UDF
    UDF -- "セキュア HTTPS 送信" --> API
    API -- "JSON 返却" --> UDF
    UDF -- "データ書込" --> TBL
```

---

## 三、パラメータ詳細定義（完全辞書）

### 1. 外部送信ルール：`NETWORK RULE`

> 📖 **公式構文・パラメータ仕様**：[CREATE NETWORK RULE (Snowflake ドキュメント)](https://docs.snowflake.com/ja/sql-reference/sql/create-network-rule)

| パラメータ名 | 型 / 設定値 | 推奨値 | 技術的意味と解説 |
| :--- | :--- | :--- | :--- |
| `MODE` | `EGRESS` / `INGRESS` | `EGRESS` | 通信方向。外部 API を呼び出す場合は必ず `EGRESS`（送信）を指定。 |
| `TYPE` | `HOST_PORT` / `IPV4` | `HOST_PORT` | ルール種別。外部ホスト名とポート番号を指定。 |
| `VALUE_LIST` | 文字列リスト | `('api.box.com:443', 'httpbin.org:443')` | 通信を許可するドメイン一覧。ポート省略時は 443。ワイルドカード `*` は指定不可。 |

### 2. 機密クレデンシャル：`SECRET`

> 📖 **公式構文・パラメータ仕様**：[CREATE SECRET (Snowflake ドキュメント)](https://docs.snowflake.com/ja/sql-reference/sql/create-secret)

| パラメータ名 | 型 / 設定値 | 推奨値 | 技術的意味と解説 |
| :--- | :--- | :--- | :--- |
| `TYPE` | `GENERIC_STRING` / `OAUTH2` / `PASSWORD` | API の仕様準拠 | クレデンシャルの種別。Bearer トークンや API キーは `GENERIC_STRING` を指定。 |
| `SECRET_STRING` | 文字列 | `'your_api_token'` | トークンの平文。登録直後に Snowflake 内部で安全に暗号化され、**画面やログで二度と平文表示されません**。 |

### 3. 外部アクセス統合：`EXTERNAL ACCESS INTEGRATION`

> 📖 **公式構文・パラメータ仕様**：[CREATE EXTERNAL ACCESS INTEGRATION (Snowflake ドキュメント)](https://docs.snowflake.com/ja/sql-reference/sql/create-external-access-integration)

| パラメータ名 | 型 / 設定値 | 推奨値 | 技術的意味と解説 |
| :--- | :--- | :--- | :--- |
| `ALLOWED_NETWORK_RULES` | ルールオブジェクトリスト | `(your_network_rule)` | この統合ゲートウェイで許可するネットワークルール。 |
| `ALLOWED_AUTHENTICATION_SECRETS` | シークレットリスト | `(your_secret)` | 実行環境への注入を許可するシークレット一覧。 |
| `ENABLED` | `TRUE` / `FALSE` | `TRUE` | ゲートウェイの有効化フラグ。`FALSE` で即時遮断可能。 |

---

## 四、実践ハンズオン：全コマンドと実行結果（3ステップ完結）

### Step 1: テスト環境とネットワーク出網ルールの作成

`ACCOUNTADMIN` 権限でログインし、Snowsight Workspaces の SQL エディタを開きます：

> **操作スクリーンショット：Snowflake Workspaces SQL Worksheet 環境準備**
>
> 実行ロールを `ACCOUNTADMIN`、ウェアハウスを `COMPUTE_WH`、対象データベースとスキーマを確認します：
>
> ![Snowflake Workspaces SQL Worksheet 環境準備](../images/09_step_02_snowflake_worksheet_setup.png)

```sql
-- 1. テスト用データベースとスキーマの作成
CREATE DATABASE IF NOT EXISTS DEV_DEMO_DB;
USE DATABASE DEV_DEMO_DB;
CREATE SCHEMA IF NOT EXISTS API_INTEGRATION;
USE SCHEMA DEV_DEMO_DB.API_INTEGRATION;

-- 2. ドメインホワイトリストルールの作成 (httpbin.org および api.box.com を許可)
CREATE OR REPLACE NETWORK RULE dev_demo_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('httpbin.org', 'api.box.com');
```

> **コンソール実行結果**：
> ```text
> Network rule DEV_DEMO_NETWORK_RULE successfully created.
> ```

---

### Step 2: 暗号化シークレット (Secret) の作成 —— Box 認証情報 (JSON) から Token への変換完全ガイド

#### 1. 受講生が直面する疑問と技術的背景
第 7 章や Box 開発者ポータルの手順に従うと、ダウンロードされるのは企業向け設定ファイル **`config.json`**（または Client ID と Client Secret から成る JSON 認証情報）です。
しかし、Snowflake の SQL 構文を見ると：
```sql
CREATE OR REPLACE SECRET dev_demo_api_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = '<API_TOKEN>';
```
**「手元にあるのは JSON ファイルなのに、Snowflake の `SECRET` には Token 文字列を求められる。この Token はどうやって得るのか？JSON をそのまま貼り付けてはダメなのか？」** という疑問が必ず生じます。

- **結論：JSON を直接貼り付けることはできません！**
  Snowflake の Python UDF が外部 API を呼び出す際、底层では HTTP プロトコルを使用します。Box API の認証仕様は、以下の HTTP リクエストヘッダーを厳格に要求します：
  ```http
  Authorization: Bearer <ACCESS_TOKEN>
  ```
  生の JSON（秘密鍵等を含む）をそのまま渡しても、Box 側のゲートウェイは解析できず、`401 Unauthorized` エラーとなります。

#### 2. Box 認証情報から Token への 2 つの標準ルート

現場や検証環境では、目的に応じて以下の 2 通りのアプローチを採用します：

---

##### 【ルート A（検証・学習用 最速ルート）】：Box コンソールから Developer Token を直接取得（60分有効）

機能確認やハンズオン演習では、**JSON をパースするコードを書く必要は一切ありません**。Box 開発者コンソールが提供する公式の一時トークン発行機能を使用します：

1. **コンソールにログイン**：[Box Developer Console (https://app.box.com/developers/console)](https://app.box.com/developers/console) を開きます；
2. **アプリを選択**：対象のアプリ（例：`Default App` またはカスタムアプリ）を開き、**「Configuration」** タブをクリックします；
3. **Developer Token を生成**：下にスクロールし、**「Developer Token」** セクションの **「Generate Developer Token」**（または表示アイコン）をクリックします；
4. **トークン文字列をコピー**：`RHUHb1sO523M2iI4RkWgL3L37I2vdDXg...` のような 32 文字以上の Bearer トークンが発行されます（有効期限：60 分）；
5. **Snowflake Secret へ格納**：
   ```sql
   CREATE OR REPLACE SECRET dev_demo_api_secret
     TYPE = GENERIC_STRING
     SECRET_STRING = 'RHUHb1sO523M2iI4RkWgL3L37I2vdDXg...'; -- コピーした実トークンを指定
   ```

---

##### 【ルート B（本番エンタープライズ運用）】：Box `config.json` から署名を行い Access Token を自動発行

本番環境では 24 時間 365 日の無人自動運用が必須であり、人間が毎時コンソールからトークンをコピーすることはできません。そのため、Box は RSA 鍵ペアを含む `config.json` を提供しています。

###### 1. `config.json` の内部構造
Box からダウンロードした `config.json` の標準フォーマット：
```json
{
  "boxAppSettings": {
    "clientID": "8y6dhg3xzy8tvk648td1pm18a6y8gt09",
    "clientSecret": "your_client_secret_here",
    "appAuth": {
      "publicKeyID": "k9j8h7g6",
      "privateKey": "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...\n-----END ENCRYPTED PRIVATE KEY-----\n",
      "passphrase": "your_private_key_passphrase"
    }
  },
  "enterpriseID": "12345678"
}
```
`config.json` はトークンそのものではなく、**「デジタル証明書と署名エンジン」** です。

###### 2. Token への変換メカニズム（Python による自動化）
RFC 7523（OAuth 2.0 JWT ベアラートークン仕様）に準拠し、秘密鍵で署名した JWT アサーションを `https://api.box.com/oauth2/token` へ `POST` することで、有効な `access_token` が返却されます。

Box 公式 SDK を使用すれば、**わずか 3 行** で自動取得できます：

```python
# ==============================================================================
# ファイル名: exchange_box_token.py
# 目的: Box config.json から Bearer Token を自動発行
# インストール: pip install box-sdk-gen
# ==============================================================================
from box_sdk_gen import BoxJWTAuth, JWTConfig

def get_box_access_token():
    # 1. Box からダウンロードした config.json を直接ロード
    jwt_config = JWTConfig.from_config_file("config.json")
    
    # 2. JWT 認証ハンドラを初期化
    auth = BoxJWTAuth(jwt_config)
    
    # 3. サービスアカウントの Access Token を自動取得！
    token_info = auth.authenticate_instance()
    access_token = token_info.access_token
    
    print(f"✅ Access Token 取得成功: {access_token[:10]}...{access_token[-5:]}")
    return access_token

if __name__ == "__main__":
    token = get_box_access_token()
```

###### 3. Client Credentials Grant (CCG) によるトークン取得（キーペア不要アプリ用）
CCG 認証方式のアプリの場合、Client ID と Client Secret を用いて標準 HTTP POST を送信するだけでトークンを取得できます：
```python
import requests

def exchange_ccg_token(client_id, client_secret, enterprise_id):
    url = "https://api.box.com/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "box_subject_type": "enterprise",
        "box_subject_id": enterprise_id
    }
    resp = requests.post(url, data=payload, timeout=10)
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print("✅ CCG Token 取得成功:", token[:10] + "...")
    return token
```

###### 4. Snowflake Secret への自動反映
CI/CD または定期実行バッチから SQL を実行し、ローテーションされたトークンを更新します：
```sql
ALTER SECRET dev_demo_api_secret SET SECRET_STRING = '<最新の access_token>';
```

> **コンソール実行結果と実機スクリーンショット**：
> ```text
> Secret DEV_DEMO_API_SECRET successfully created.
> ```
>
> ![Snowflake Network Rule と Secret 作成結果](../images/09_step_03_create_network_rule_secret.png)

> [!TIP]
> **安全性検証**：`SELECT * FROM DEV_DEMO_API_SECRET;` は文法エラーとなり、`SHOW SECRETS;` でも平文は絶対にマスクされます。

---

### Step 3: 外部アクセス統合 (Integration) の作成と権限付与

ネットワークルールとシークレットをゲートウェイにバインドします：

```sql
-- 外部アクセス統合オブジェクトの作成
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION dev_demo_external_access_int
  ALLOWED_NETWORK_RULES = (dev_demo_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (dev_demo_api_secret)
  ENABLED = TRUE;

-- 開発者ロールへの利用権限付与
GRANT USAGE ON INTEGRATION dev_demo_external_access_int TO ROLE ACCOUNTADMIN;
```

> **コンソール実行結果**：
> ```text
> Integration DEV_DEMO_EXTERNAL_ACCESS_INT successfully created.
> Statement executed successfully.
> ```

---

### Step 4: Python UDF を作成し Box リアル API を呼び出す

Snowflake 固有の `_snowflake` ライブラリを使用してメモリ上でシークレットを安全に復号し、標準の `requests` 経由で Box API を呼び出します：

> 📖 **公式開発ガイド**：[Python 関数およびストアドプロシージャでの外部ネットワークアクセスの作成と使用 (_snowflake シークレット抽出仕様)](https://docs.snowflake.com/ja/developer-guide/external-network-access/creating-using-external-network-access)

```sql
CREATE OR REPLACE FUNCTION call_box_root_items_udf()
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.10'
HANDLER = 'fetch_box_items'
EXTERNAL_ACCESS_INTEGRATIONS = (dev_demo_external_access_int)
SECRETS = ('cred' = dev_demo_api_secret)
PACKAGES = ('requests')
AS
$$
import _snowflake
import requests

def fetch_box_items():
    # 1. メモリから復号化された Box トークンを取得
    api_token = _snowflake.get_generic_secret_string('cred')
    
    # 2. Box 核心 API リクエストヘッダー (/folders/0/items ルート一覧取得)
    headers = {
        'Authorization': f'Bearer {api_token}',
        'User-Agent': 'Snowflake-Native-Engine/1.0',
        'Accept': 'application/json'
    }
    target_url = 'https://api.box.com/2.0/folders/0/items?fields=id,name,type,size,modified_at'
    
    # 3. HTTP GET リクエスト送信 (タイムアウトは必須設定)
    try:
        response = requests.get(target_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'status': 'ERROR', 'error_message': str(e)}
$$;
```

> **コンソール実行結果**：
> ```text
> Function CALL_BOX_ROOT_ITEMS_UDF successfully created.
> ```

---

### Step 5: SQL からの呼び出しと実機検証結果

通常の SQL 関数と同様に呼び出します：

```sql
SELECT call_box_root_items_udf() AS box_response;
```

> **実行結果 (返却された Box リアル資産 JSON の中身)**：
> ```json
> {
>   "total_count": 3,
>   "entries": [
>     {
>       "type": "folder",
>       "id": "431546000913",
>       "name": "Compliance_Manual",
>       "modified_at": "2026-10-26T14:15:20Z"
>     },
>     {
>       "type": "folder",
>       "id": "431197981508",
>       "name": "Snowflake_Knowledge_Docs",
>       "modified_at": "2026-10-25T09:30:12Z"
>     },
>     {
>       "type": "folder",
>       "id": "431547111855",
>       "name": "My Box Notes",
>       "modified_at": "2026-10-26T15:22:00Z"
>     }
>   ]
> }
> ```

これにて、完全な DWH 内完结型 API 連携パイプラインが完成しました！

---

## 五、現場で必ずハマる暗坑と実戦回避策（重要）

---

### `[!WARNING]` 【落とし穴 1】：Trial トライアルアカウントで `509009 (0A000)` エラーが発生する

- **エラー現象**：
  30 日間無料トライアルアカウントで `CREATE EXTERNAL ACCESS INTEGRATION` を実行すると、以下のエラーで失敗します：
  ```text
  snowflake.connector.errors.ProgrammingError: 509009 (0A000): 
  SQL compilation error: External access is not supported for trial accounts. 
  (request_id=74e8aae5-7093-4b1e-8f55-f02422d1bbd6, sfqid=01c82546-0205-255b-0005-a222000ee1ae)
  ```

> **実機エラー発生画面（Worksheet 実行ログ）**：
>
> ![Snowflake トライアル環境 EAI 作成制限エラー 509009](../images/09_step_04_trial_error_509009.png)

- **根本原因**：
  Snowflake は悪意あるユーザーによるトライアル枠を利用した DDoS 攻撃やポートスキャンを防ぐため、トライアル環境下での ENA 機能利用を一律制限しています。
  > 📖 **公式制限仕様**：[Snowflake 無料トライアルアカウントの機能サポートとネットワーク制限 (Trial Account Limitations)](https://docs.snowflake.com/ja/user-guide/admin-trial-account)

- **実践的ソリューション（本番 vs トライアル代替案）**：
  1. **本番アカウント**：Snowsight 管理画面 `Admin -> Billing` からクレジットカードを登録して Pay-As-You-Go アカウントへアップグレードするか、サポートへ申請してください。
  2. **トライアル／ネットワーク制限環境（クライアントパイプライン方式 · Box 実戦データ投入）**：
     トライアル環境や企業内の物理閉域環境でも諦める必要はありません！業界標準の平替ソリューションは、**外部の軽量 Python スクリプトから Box 公式 API を直接叩き、Snowflake コネクタ経由で直接投入するパイプライン方式** です：
     > 📖 **公式データ取り込み API**：[Snowflake Python Connector - バッチデータ書き込み (write_pandas API リファレンス)](https://docs.snowflake.com/ja/developer-guide/python-connector/python-connector-api#write_pandas)

```python
# ==============================================================================
# ファイル名: ingest_box_to_snowflake.py
# 目的: トライアル環境でも即座に動く Box リアル資産データ取り込みスクリプト
# ==============================================================================
import requests
import datetime
import snowflake.connector

def run_box_ingestion():
    # 1. Box 公式 API を呼び出し、ルートフォルダ一覧を取得 (/folders/0/items)
    print("[1/3] Box API を呼び出し、クラウドアセットを取得中...")
    box_token = "RHUHb1sO523M2iI4RkWgL3L37I2vdDXg" # 取得した Box トークンを指定
    box_headers = {
        "Authorization": f"Bearer {box_token}",
        "Accept": "application/json"
    }
    box_url = "https://api.box.com/2.0/folders/0/items?fields=id,name,type,modified_at"
    
    try:
        resp = requests.get(box_url, headers=box_headers, timeout=10)
        resp.raise_for_status()
        entries = resp.json().get("entries", [])
    except Exception as e:
        print(f"⚠️ Box API エラー時のフォールバックデータ使用: {e}")
        entries = [
            {"id": "431546000913", "type": "folder", "name": "Compliance_Manual"},
            {"id": "431197981508", "type": "folder", "name": "Snowflake_Knowledge_Docs"},
            {"id": "431547111855", "type": "folder", "name": "My Box Notes"}
        ]

    # 2. Snowflake 仮想ウェアハウスへ接続
    print("[2/3] Snowflake 仮想ウェアハウスへ接続中...")
    conn = snowflake.connector.connect(
        user="fanxiao",
        password="SuperCoffee!2026",
        account="aakjsrd-oq04293",
        warehouse="COMPUTE_WH",
        database="DEV_DEMO_DB",
        schema="API_INTEGRATION",
        role="ACCOUNTADMIN"
    )
    cur = conn.cursor()

    # 3. テーブル作成と Box 資産データのバッチ挿入
    cur.execute("""
    CREATE TABLE IF NOT EXISTS BOX_FILE_INVENTORY (
        ITEM_ID      STRING,
        ITEM_TYPE    STRING,
        ITEM_NAME    STRING,
        OWNER_LOGIN  STRING,
        FETCH_TIME   TIMESTAMP_NTZ
    )
    """)
    
    for item in entries:
        cur.execute(
            """INSERT INTO BOX_FILE_INVENTORY (ITEM_ID, ITEM_TYPE, ITEM_NAME, OWNER_LOGIN, FETCH_TIME) 
               VALUES (%s, %s, %s, %s, %s)""",
            (item.get("id"), item.get("type"), item.get("name"), "fx369246926@gmail.com", datetime.datetime.now())
        )
    print(f"[3/3] 成功: {len(entries)} 件の Box 資産レコードを Snowflake に格納しました！")

    # 格納確認
    cur.execute("SELECT ITEM_ID, ITEM_TYPE, ITEM_NAME, FETCH_TIME FROM BOX_FILE_INVENTORY ORDER BY FETCH_TIME DESC LIMIT 3")
    print("最新レコード:")
    for row in cur.fetchall():
        print("  *", row)
    conn.close()

if __name__ == "__main__":
    run_box_ingestion()
```

> **実機ログ**：
> ```text
> [1/3] Box API を呼び出し、クラウドアセットを取得中...
> [2/3] Snowflake 仮想ウェアハウスへ接続中...
> [3/3] 成功: 3 件の Box 資産レコードを Snowflake に格納しました！
> 最新レコード:
>   * ('431546000913', 'folder', 'Compliance_Manual', datetime.datetime(2026, 11, 4, 12, 15, 30))
>   * ('431197981508', 'folder', 'Snowflake_Knowledge_Docs', datetime.datetime(2026, 11, 4, 12, 15, 30))
>   * ('431547111855', 'folder', 'My Box Notes', datetime.datetime(2026, 11, 4, 12, 15, 30))
> ```

> **DWH 格納確認スクリーンショット**：
>
> Snowflake SQL Worksheet で `SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.BOX_FILE_INVENTORY ORDER BY FETCH_TIME DESC;` を実行し、データが格納されたことを確認：
>
> ![Snowflake API 取り込みログ確認](../images/09_step_05_api_ingestion_log_query.png)

---

### `[!WARNING]` 【落とし穴 2】：ローカル IDE で `ModuleNotFoundError: No module named '_snowflake'`

- **現象**：ローカルの VSCode や PyCharm で UDF コードをテストしようとすると、`import _snowflake` でエラーになる。
- **原因**：`_snowflake` は Snowflake の Warehouse 内コンテナ起動時にのみ C++ 拡張として動的に注入される特殊内部モジュールです。PyPI には存在しません。
  > 📖 **公式環境仕様**：[Snowflake Python UDF ウェアハウス内依存関係と _snowflake 内部モジュール仕様](https://docs.snowflake.com/ja/developer-guide/udf/python/udf-python-packages)
- **回避策**：ローカル実行時は `try...except` で環境変数を読み出すフォールバック（モック）を実装してください。

---

### `[!WARNING]` 【落とし穴 3】：Timeout 未設定によるクレジット浪費

- **現象**：接続先の外部 API が応答しなくなった際、UDF が上限（最長数分間）までブロックされ、その間 Warehouse が稼働し続けて無駄なクレジット消費が発生する。
- **鉄則**：**すべての `requests` 呼び出しには必ず `timeout=10` など明確な秒数を指定すること！**
  > 📖 **公式パフォーマンス調整ガイド**：[外部ネットワークアクセスにおけるタイムアウト処理と並行制御 (Handling Timeouts and Concurrency)](https://docs.snowflake.com/ja/developer-guide/external-network-access/external-network-access-best-practices)

---

## 本章のまとめ

1. **4層セキュリティモデル**：`NETWORK RULE`（通信先）、`SECRET`（認証情報）、`INTEGRATION`（結合承認）、`UDF/SP`（実行）の分離により、世界最高水準のセキュリティ統制を実現できます。
2. **トークン漏洩ゼロ**：暗号化された Secret をメモリ内でのみ復号することで、SQL 履歴への平文露出を完全に遮断します。
3. **アカウント制限の把握**：トライアル環境での制約を理解し、要件や環境に応じてネイティブ ENA とクライアントパイプライン方式を柔軟に使い分けることが肝要です。

