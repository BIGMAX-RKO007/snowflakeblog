# 第 07 章：非構造化ファイルデータ同期の実践 —— Snowflake Openflow と Box クラウドストレージの統合

> 本章は **『尚硅谷（Shangguigu）技術テキスト作成規範』** に準拠して全面再構成されています：本質を突く極小比較、業務ノイズを排除した純粋技術フォーカス、実機レスポンスを伴う 3 ステップ実証、落とし穴と回避策の明示、前提条件の完全前置。

---

## 導入：本質を突く極小メンタルモデル

これまでの章では、リレーショナルデータベース（Oracle 等）内の**構造化テーブルデータ**を、CSV/gzip を経由して Snowflake へ同期する方法を学習してきました。

しかし、現代のデータウェアハウス基盤には、もう一つの巨大なデータ資産が存在します。それが、クラウドストレージ（Box、AWS S3、Google Drive 等）に保存されている **PDF 規程書・Word 設計書・TXT 運用チェックリストなどの「非構造化ファイルデータ（Unstructured Files）」** です。

### 直感的な対比：構造化データ vs 非構造化ファイル

```
【構造化データ (Oracle 等)】
┌────┬────────┬─────────┐
│ Id │ Name   │ Balance │  ───────> 従来の ETL / COPY INTO ───> Snowflake テーブル (行と列)
├────┼────────┼─────────┤                                       SQL による集計・検索が直接可能
│ 1  │ 田中   │ 100.00  │
└────┴────────┴─────────┘

【非構造化ファイル (Box クラウドストレージ)】
┌─────────────────────────┐
│ 01_セキュリティ規程.pdf │
│ 02_アーキ設計仕様.docx  │  ───────> Openflow ファイル同期 ─────> Snowflake Stage (原本物理バイナリ)
│ 03_保守点検リスト.txt   │                                       ＋ メタデータ台帳表 (サイズ/ハッシュ)
└─────────────────────────┘                                       ＋ 本文チャンク表 (段落・条文)
```

- **初学者の根本的な疑問**：クラウド上のファイルはどのように自動・増分同期されるのか？同期された原本は Snowflake のどこに格納されるのか？メタデータ表は何を記録しているのか？そして最も重要な点として：**「ファイルの中身の実データは SQL で直接参照できるのか？」**
- **本章の目的**：特定の業務ドメイン（銀行や証券の難解な業務ルール）を完全に排除し、純粋な**データ同期・階層ストレージ・SQL クエリ検証のエンジニアリング視点**で、全行程を確実に完結させます！

---

## 一、前提条件と検証環境 (Prerequisites)

実機操作中に環境起因で停止することを防ぐため、事前に以下の環境と権限を確認してください：

| 構成要素 | 必須バージョン / 権限 | 役割 |
| :--- | :--- | :--- |
| **Snowflake アカウント** | `ACCOUNTADMIN` または `SECURITYADMIN` + `SYSADMIN` | 同期用ロール、ウェアハウス、ステージ、テーブルの作成 |
| **Box 開発者アカウント** | Enterprise または個人開発者 Trial（2FA 有効化済み） | Custom App サービスアカウント作成および JWT 秘密鍵の生成 |
| **対象共有フォルダ** | Box 上で `Editor` または `Owner` 権限を持つフォルダ | サービスアカウントへ共有招待し、同期対象ファイルを格納 |
| **Python 環境** | Python 3.10+（任意：テストデータ準備・突合確認用） | 複数形式のテストファイル生成および自動突合の実行 |

---

## 二、技術アーキテクチャとデータフロー

実装に着手する前に、下図にてシステム全体の 4 層構造を整理します：

```mermaid
flowchart TD
    subgraph Source["データソース (Data Source)"]
        B1["Box 共有フォルダ<br/>(PDF / Word / TXT 原本ファイルを配置)"]
        B2["Box カスタムアプリ (Custom App)<br/>(JWT 鍵ペアによるサーバー間自動認証)"]
        B3["Box 監査イベントストリーム<br/>(過去14日間の CDC 差分変更を追跡)"]
    end

    subgraph Pipeline["データ転送パイプライン (Pipeline)"]
        O1["Snowflake Openflow Connector for Box"]
        O2["コネクタ主要パラメータ構成<br/>(Box Source / SF Target / Ingestion)"]
        O3["軽量ランタイムエンジン<br/>(ファイルストリーム転送・再試行・ハッシュ計算)"]
    end

    subgraph Target["データターゲット (Snowflake Target)"]
        subgraph S_Stage["1. 物理ストレージ層"]
            T1["内部受管ステージ<br/>(@BOX_RAW_STAGE/<br/>ファイルの物理原本バイナリ/テキストを保存)"]
        end

        subgraph S_Meta["2. メタデータ台帳層"]
            T2["メタデータ台帳表<br/>(BOX_DOCUMENT_METADATA<br/>ファイル ID、サイズ、SHA-256、同期時刻を記録)"]
        end

        subgraph S_Chunk["3. 本文チャンク層"]
            T3["テキストチャンク表<br/>(BOX_DOC_CHUNKS<br/>長文ドキュメントを段落分割し、権限を紐付け)"]
        end
    end

    subgraph QueryLayer["データ検索・活用層"]
        Q1["SQL ステージ直読<br/>(TXT 本文の直接クエリ)"]
        Q2["SQL メタデータクエリ<br/>(ハッシュ値とサイズの突合)"]
        Q3["SQL チャンク検索<br/>(分割された条文・段落の抽出)"]
    end

    B1 -->|フォルダ共有招待| B2
    B2 -->|JWT 秘密鍵による免密接続| O1
    B3 -.->|変更イベント検知| O1
    O1 --> O3
    O3 -->|1. 原本物理配置| T1
    O3 -->|2. サイズ・ハッシュ登録| T2
    O3 -->|3. テキスト分割チャンク化| T3
    T1 --> Q1
    T2 --> Q2
    T3 --> Q3

    style Source fill:#f0f5ff,stroke:#adc6ff
    style Pipeline fill:#f6ffed,stroke:#b7eb8f
    style Target fill:#fff7e6,stroke:#ffd591
    style QueryLayer fill:#f9f0ff,stroke:#d3adf7
```

### 技術選定の比較：Openflow コネクタ vs 自作 Python スクリプト

| 評価軸 | 方式 A：Snowflake Openflow コネクタ（推奨） | 方式 B：自作 Python スクリプト ＋ Box REST API |
| :--- | :--- | :--- |
| **開発工数** | **極小（GUI 設定のみ、半日程度で全線開通）** | 大（認証トークン管理、ページング、再試行処理の実装が必要） |
| **クレデンシャル管理** | **Openflow 内で JWT 秘密鍵設定を暗号化管理、運用フリー** | 独自サーバーで Token 保存・2時間毎のリフレッシュ処理が必要 |
| **増分同期 (CDC)** | **標準装備：Box の過去14日間監査ログから自動追跡** | ウォーターマーク日時の自前管理、または Webhook 受信基盤が必要 |
| **一貫性突合** | **ファイルサイズおよび SHA-256 ハッシュを自動算出して登録** | ローカルスクリプトでハッシュを計算し、SQL を発行して登録 |
| **権限継承 (ACL)** | **ファイルに紐づく閲覧者メールアドレスリストを自動抽出** | Box コラボレーション API を再帰的に呼び出す必要があり複雑 |

---

## 三、Box データソース側の準備と認証情報の取得

### Step 3.1: バックエンドサービスアプリ（Custom App）の作成
1. [Box Developer Console (開発者コンソール)](https://app.box.com/developers/console) へログインします。

![Box Developer Console コントロールパネルTOP](../images/07_step_01_box_console_home.png)

2. 画面右上の **「Create Platform App」** をクリックします。
3. アプリケーションタイプとして **「Custom App」** を選択します。

![Custom App アプリタイプの選択](../images/07_step_02_box_app_type_custom.png)

4. 基本情報を入力します：
   - **App Name**：`Snowflake_Openflow_Box`
   - **Purpose**：`Integration`（データ統合）を選択
5. 認証方式（Authentication Method）として **「Server Authentication (with JWT)」**（公開鍵/秘密鍵による自動認証）を選択します。

![Server Authentication JWT 認証方式の選択](../images/07_step_02_box_jwt_auth_selection.png)

### Step 3.2: 最小権限スコープ（Application Scopes）の設定
アプリの **「Configuration」** タブを開き、設定を行います：

1. **App Access Level**：**「App + Enterprise Access」** を選択。
2. **Content Scopes**：
   - `Read all files and folders stored in Box`：**チェック**（ファイル一覧およびバイナリ取得に必須）。
   - `Write all files and folders stored in Box`：**チェック**  
     *(注：Box 側でダウンロード用トークンを払い出すために必須の仕様です。ファイル本体の改変は行いません)*。

![Box ファイル読み取り権限スコープの設定](../images/07_step_03_box_content_scopes.png)

3. **Administrative Actions**：
   - `Manage users` および `Manage groups`：チェック（ファイルごとのアクセス権限リスト `user_emails` の抽出用）。
   - `Manage enterprise properties`：チェック（監査イベントストリームを取得し、増分 CDC 同期を実現するため）。

![Box ユーザーおよび管理権限スコープの設定](../images/07_step_04_box_admin_scopes.png)

### Step 3.3: 鍵ペアの生成と構成ファイル（`config.json`）のダウンロード
1. 設定画面の下部にある **「Add and Manage Public Keys」** セクションへ移動します。

![公開鍵・秘密鍵管理セクション](../images/07_step_05_box_keypair_section.png)

2. **「Generate a Public/Private Keypair」** をクリックします：
   > [!WARNING] **【避坑ポイント：Box 2要素認証（2FA）の必須要件】**  
   > Box アカウントで 2 要素認証が無効の場合、秘密鍵生成時に警告画面でブロックされます。アカウント設定から認証アプリまたは SMS を設定した後に再実行してください：
   > 
   > ![Box 2要素認証セキュリティ確認](../images/07_step_06_box_2fa_prompt.png)

3. 生成が完了すると、JSON 認証ファイル（例：`2717878_xxxx_config.json`）がダウンロードされます。この中には `clientID`、`enterpriseID`、および RSA 秘密鍵が含まれており、Openflow 接続時の主要な認証設定となります。

### Step 3.4: フォルダ共有招待と Folder ID の取得
1. アプリの **「Authorization」** タブで **「Review and Submit」** をクリックします。
2. Box 組織管理者が [Box 管理コンソール](https://app.box.com/master) の「カスタムアプリマネージャー」から **「承認 (Authorize)」** を行います。
3. アプリの **「General Settings」** 画面から、サービスアカウントのメールアドレスをコピーします：
   - 例：`AutomationUser_2717878_XevDdBO55B@boxdevedition.com`
4. Box Web 画面で同期対象フォルダ（例：`社内規程マニュアル`）を新規作成します。
5. **「共有」** $\rightarrow$ **「コラボレータを招待」** を開き、上記メールアドレスを貼り付けて権限を **「ビューアー (Viewer)」** に設定します：

![Box フォルダへのサービスアカウント招待](../images/07_step_07_box_folder_collaborator.png)

6. **Folder ID の記録**：ブラウザのアドレスバーの末尾にある数値 ID（例：`https://app.box.com/folder/431546000913` の **`431546000913`**）を記録します。`0` を指定するとルート配下全体が対象になります。

### Step 3.5: テストファイルのアップロード
様々なフォーマットの同期を網羅的に検証するため、3 種類の代表的なテストファイルを準備し、アップロードします：
1. `01_情報セキュリティ基本規程_2026.pdf`（PDF 文書、サイズ 781 バイト）
2. `02_クラウド移行プロジェクト_機密設計書.docx`（Word 文書、サイズ 1,825 バイト）
3. `03_コンプライアンス遵守チェックリスト_2026.txt`（プレーンテキスト、サイズ 1,429 バイト）

対象フォルダ内でファイルが正常に認識されていることを確認します：

![Box フォルダへのテストファイルアップロード完了](../images/07_step_08_box_files_uploaded.png)

---

## 四、Snowflake ターゲット環境の構築（RBAC と階層ストレージ）

Snowflake 側では、最小特権の原則に基づき、専用のロール・サービスユーザー・仮想ウェアハウス・内部ステージ・テーブルを作成します。

同梱の初期化スクリプト [`07_openflow_box_setup.sql`](file:///c:/Users/FX/Projects/SnowflakeBlog/scripts/snowflake/07_openflow_box_setup.sql) を実行します：

```sql
-- 1. セキュリティおよびロール構成 (SECURITYADMIN)
USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Snowflake Openflow Box コネクタ専用実行ロール';

CREATE ROLE IF NOT EXISTS CORTEX_SEARCH_READ_ROLE
    COMMENT = '下流検索アプリケーション用の読み取り専用ロール';

CREATE USER IF NOT EXISTS OPENFLOW_BOX_SVC_USER
    TYPE = SERVICE
    DEFAULT_ROLE = OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Openflow データパイプライン専用サービスユーザー';

GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO USER OPENFLOW_BOX_SVC_USER;
GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO ROLE SYSADMIN;
GRANT ROLE CORTEX_SEARCH_READ_ROLE TO ROLE SYSADMIN;

-- 2. コンピュートおよびストレージの作成 (SYSADMIN)
USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS OPENFLOW_INGEST_WH
    WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Box ファイル同期とテキストチャンク処理専用のコンピュートリソース';

CREATE DATABASE IF NOT EXISTS BOX_INTEGRATION_DB;
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.BOX_LANDING_DATA;
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.CORTEX;

GRANT USAGE, OPERATE ON WAREHOUSE OPENFLOW_INGEST_WH TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE ON DATABASE BOX_INTEGRATION_DB TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE, CREATE TABLE, CREATE STAGE ON SCHEMA BOX_INTEGRATION_DB.BOX_LANDING_DATA TO ROLE OPENFLOW_CONNECTOR_ROLE;
GRANT USAGE, CREATE TABLE ON SCHEMA BOX_INTEGRATION_DB.CORTEX TO ROLE OPENFLOW_CONNECTOR_ROLE;

-- 3. ストレージおよびテーブル構造の初期化 (OPENFLOW_CONNECTOR_ROLE)
USE ROLE OPENFLOW_CONNECTOR_ROLE;
USE WAREHOUSE OPENFLOW_INGEST_WH;
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- ① 内部受管ステージの作成 (原本ファイルの物理格納場所)
CREATE OR REPLACE STAGE BOX_RAW_STAGE
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    COMMENT = 'Box から同期された非構造化ファイルの原本を保存する内部ステージ';

-- ② メタデータ・突合管理テーブルの作成 (台帳管理用)
CREATE OR REPLACE TABLE BOX_DOCUMENT_METADATA (
    FILE_ID             VARCHAR(64) PRIMARY KEY,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    FOLDER_PATH         VARCHAR(1024),
    SHA256_HASH         VARCHAR(128) NOT NULL,
    SIZE_BYTES          NUMBER(38, 0),
    BOX_CREATED_AT      TIMESTAMP_NTZ,
    BOX_MODIFIED_AT     TIMESTAMP_NTZ,
    INGESTED_AT         TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    USER_EMAILS         ARRAY COMMENT 'Box 側で閲覧権限を持つユーザーメールアドレスリスト (ACL 制御用)'
)
COMMENT = 'Box ファイルのメタデータ台帳および CDC バージョン管理テーブル';

-- ③ テキストチャンクテーブルの作成 (検索・抽出用)
USE SCHEMA BOX_INTEGRATION_DB.CORTEX;

CREATE OR REPLACE TABLE BOX_DOC_CHUNKS (
    CHUNK_ID            VARCHAR(128) PRIMARY KEY,
    FILE_ID             VARCHAR(64) NOT NULL,
    FILE_NAME           VARCHAR(512) NOT NULL,
    FOLDER_ID           VARCHAR(64) NOT NULL,
    CHUNK_INDEX         NUMBER(10, 0),
    CHUNK_TEXT          VARCHAR(16777216) NOT NULL,
    USER_EMAILS         ARRAY NOT NULL,
    UPDATED_AT          TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = '長文ドキュメントを分割した段落単位のテキストデータ';
```

---

## 五、Openflow コネクタ設定の全パラメータ対応表

**Openflow Connector for Box** を設定する際に求められる 3 大カテゴリのパラメータ対応表です：

### 1. Boxソースパラメーター (Box Source Parameters)

| パラメータ名（日 / 英） | 概要・役割 | 推奨設定値 | 技術的補足 |
| :--- | :--- | :--- | :--- |
| **Box App 構成 JSON**<br/>*(Box App Configuration JSON)* | Box 認証 JSON 文字列 | `{ "boxAppSettings": { ... } }` | フェーズ 3 で取得した `config.json` のテキスト内容全体をそのまま貼り付けます。 |
| **Box App構成ファイル**<br/>*(Box App Configuration File)* | Box 構成ファイルのパス | `/path/to/box_config.json` | CLI やボリュームマウントを利用する場合に物理パスを指定（上記 JSON と二者択一）。 |

### 2. Box宛先パラメーター (Box Destination Parameters)

| パラメータ名（日 / 英） | 概要・役割 | 推奨設定値 | 技術的補足 |
| :--- | :--- | :--- | :--- |
| **宛先データベース**<br/>*(Destination Database)* | 格納先データベース | `BOX_INTEGRATION_DB` | ステージおよびメタデータテーブルが所属するデータベース。 |
| **宛先スキーマ**<br/>*(Destination Schema)* | 格納先スキーマ | `BOX_LANDING_DATA` | ファイルがランディングするスキーマ名。 |
| **Snowflake認証ストラテジー**<br/>*(Snowflake Authentication Strategy)* | 認証方式 | `Keypair`（推奨）または `Snowflake Credentials` | 運用上のパスワード期限切れを回避するため、非対称鍵ペア（Keypair）を推奨。 |
| **Snowflakeアカウント識別子**<br/>*(Snowflake Account Identifier)* | アカウント識別子 | `aakjsrd-oq04293` | `<組織名>-<アカウント名>` の形式で指定。 |
| **Snowflake秘密キー**<br/>*(Snowflake Private Key)* | サービスユーザー秘密鍵 | `-----BEGIN ENCRYPTED PRIVATE KEY-----...` | サービスアカウント（`OPENFLOW_BOX_SVC_USER`）に登録した秘密鍵の内容。 |
| **Snowflake秘密キーファイル**<br/>*(Snowflake Private Key File)* | 秘密鍵ファイルのパス | `/secrets/rsa_key.p8` | 秘密鍵ファイルの物理マウントパス（秘密鍵文字列と二者択一）。 |
| **Snowflake秘密キーパスワード**<br/>*(Snowflake Private Key Password)* | 秘密鍵のパスフレーズ | `********` | 秘密鍵生成時に指定したパスフレーズ（暗号化されていない場合は空欄）。 |
| **Snowflakeロール**<br/>*(Snowflake Role)* | コネクタ実行ロール | `OPENFLOW_CONNECTOR_ROLE` | 格納先スキーマへの書き込み権限を有する専用ロール。 |
| **Snowflakeのユーザー名**<br/>*(Snowflake Username)* | コネクタ実行ユーザー | `OPENFLOW_BOX_SVC_USER` | パイプライン専用のサービスアカウント。 |
| **オーバーサイズ値戦略**<br/>*(Oversized Value Strategy)* | 長大データの処理方針 | `Truncate` または `Fail` | 単一カラムの上限値を超過した際の切り捨てまたはエラー中断。 |
| **Snowflakeウェアハウス**<br/>*(Snowflake Warehouse)* | 使用ウェアハウス | `OPENFLOW_INGEST_WH` | ステージ更新およびテーブル書き込みに使用するコンピュートリソース。 |

### 3. Box取り込みパラメーター (Box Ingestion Parameters)

| パラメータ名（日 / 英） | 概要・役割 | 推奨設定値 | 技術的補足 |
| :--- | :--- | :--- | :--- |
| **Boxフォルダー ID**<br/>*(Box Folder ID)* | 同期対象フォルダ ID | `431546000913`（または `0`） | 対象とするフォルダの数値 ID。`0` を指定するとアクセス可能な配下全体を再帰探索。 |
| **取り込むファイルの拡張子**<br/>*(Extensions of Files to Ingest)* | 許可拡張子の指定 | `pdf,docx,txt,md` | 同期対象とするファイル拡張子のカンマ区切り（ドット不要）。 |
| **Snowflakeファイルのハッシュテーブル名**<br/>*(Snowflake File Hash Table Name)* | ハッシュ突合テーブル名 | `BOX_DOCUMENT_METADATA` | 重複排除・整合性確認および差分追跡（CDC）を行う台帳テーブル名。 |

---

## 六、データ同期の閉ループ実機検証（3 ステップ方式）

同期実行後、ファイルは Box から Snowflake へ転送されます。尚硅谷スタイルの**「課題提起 $\rightarrow$ 標準 SQL 構文 $\rightarrow$ 実機実行結果と回顕画面」**の 3 ステップで検証を進めます：

### 実機検証 ①：メタデータ台帳による整合性突合（Metadata Reconciliation）

- **【課題提起】**：転送されたファイルが破損していないか、サイズやハッシュが元ファイルと一致しているかをどう確認するか？
- **【標準構文】**：メタデータテーブルを照会し、サイズと SHA-256 ハッシュ値を検証：

```sql
SELECT 
    FILE_ID,
    FILE_NAME,
    SIZE_BYTES,
    LEFT(SHA256_HASH, 16) || '...' AS HASH_PREFIX,
    FOLDER_ID,
    FOLDER_PATH,
    TO_VARCHAR(INGESTED_AT, 'YYYY-MM-DD HH24:MI:SS') AS SYNC_TIME
FROM BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_DOCUMENT_METADATA
ORDER BY FILE_ID;
```

- **【実機実行結果と画面】**：
実行時間は **540ms** で、3 件の台帳レコードが即座に返却されました。`SIZE_BYTES` および SHA-256 ハッシュ値がローカルの元ファイルと 100% 一致しており、**データ破損や欠損がゼロであること**が完全に証明されました：

![Snowflake ワークシート画面でのリアルメタデータ突合検証結果](../images/07_step_09_snowflake_stage_files.png)

---

### 実機検証 ②：SQL によるステージ内テキストファイル実データの直接読み出し（Stage Query）

- **【課題提起】**：メタデータ表には属性情報しかありません。**ファイルの中身の実テキスト**は SQL で直接確認できるのか？
- **【標準構文】**：単一列プレーンテキストフォーマットを定義し、クォーテーション付きステージパスまたは `PATTERN` で照会：

```sql
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. 単一列テキスト読み込み用フォーマットの作成 (行単位で取得)
CREATE OR REPLACE FILE FORMAT BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT 
    TYPE = 'CSV' 
    FIELD_DELIMITER = NONE 
    RECORD_DELIMITER = '\n';

-- 2. ステージ上の 03_コンプライアンス遵守チェックリスト_2026.txt の実本文データを直接クエリ
SELECT $1 AS FILE_CONTENT 
FROM '@BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_RAW_STAGE/compliance/' 
(FILE_FORMAT => 'BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT', PATTERN => '.*03.*txt');
```

- **【実機実行結果と画面】**：
実行時間はわずか **145ms** で、ステージ内のファイルから全 **20 行の実本文データ**（章立てや運用点検項目など）がクエリ結果グリッドに直接表示されました：

![Snowflake Stage ファイル本文データの直接クエリ実行結果](../images/07_step_10_stage_file_content_query.png)

---

### 実機検証 ③：解析・チャンク化済み PDF / Word の実本文データ検索

- **【課題提起】**：バイナリ形式である PDF や Word から、条文や段落単位でテキストをピンポイント抽出するにはどうすればよいか？
- **【標準構文】**：テキスト分割パイプライン完了後、`BOX_DOC_CHUNKS` テーブルを直接照会：

```sql
SELECT 
    FILE_NAME,
    CHUNK_INDEX,
    CHUNK_TEXT
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
ORDER BY FILE_ID, CHUNK_INDEX;
```

- **【実機実行結果と画面】**：
実行時間 **143ms** で、『01_情報セキュリティ基本規程_2026.pdf』のパスワード運用規程や『02_クラウド移行プロジェクト_機密設計書.docx』の閉域網設計といった実際の内容が確認できます：

![Snowflake Cortex 文書チャンク実データ検索結果](../images/07_step_11_doc_chunks_content_query.png)

---

### 実機検証 ④：原本プレビュー・ダウンロード用 URL の発行（Scoped URL）

- **【課題提起】**：業務ユーザーがブラウザ上で原本の PDF や Word を直接閲覧・ダウンロードするにはどうすればよいか？
- **【標準構文】**：Snowflake 組み込みの `BUILD_SCOPED_FILE_URL` 関数を使用して時限付き認証 URL を生成：

```sql
SELECT 
    RELATIVE_PATH,
    SIZE,
    BUILD_SCOPED_FILE_URL(@BOX_RAW_STAGE, RELATIVE_PATH) AS DIRECT_DOWNLOAD_URL
FROM DIRECTORY(@BOX_RAW_STAGE);
```

返却された URL をクリックすることで、ブラウザから元ファイルをそのままダウンロードまたは閲覧できます。

---

## 七、実戦での落とし穴とトラブルシューティング（重点）

初学者が現場で最も遭遇しやすい 3 つの課題と、その確実な回避策を明示します：

### 避坑ポイント 1：ステージパスに多バイト（日本語）が含まれる構文エラー

> [!WARNING] **【エラー現象】**  
> Snowflake ワークシート上でクォーテーションを付けずにパスを直接記述した場合：
> ```sql
> SELECT $1 FROM @BOX_RAW_STAGE/compliance/03_コンプライアンス遵守チェックリスト_2026.txt;
> ```
> コンパイルエラーが発生：`SQL compilation error: syntax error line 22 at position 34 unexpected 'コン'.`

- **原因分析**：Snowflake の SQL レキサーは、クォーテーションなしのステージパスでは ASCII 文字のみを許容するため、非 ASCII 文字（日本語・中国語等）に遭遇した時点で構文エラーと判定されます。
- **標準回避策**：
  1. ステージパス全体をシングルクォーテーションで囲む：`FROM '@BOX_RAW_STAGE/compliance/03_...'`；
  2. または親ディレクトリを指定し、`PATTERN` 正規表現で指定する：`FROM '@BOX_RAW_STAGE/compliance/' (PATTERN => '.*03.*txt')`。

---

### 避坑ポイント 2：Trial アカウントにおける `AI_PARSE_DOCUMENT` の制限

> [!WARNING] **【エラー現象】**  
> ドキュメント解析関数を実行した際のエラー：
> ```sql
> SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@BOX_RAW_STAGE', '01_規程.pdf', {'mode': 'LAYOUT'});
> ```
> `SNOWFLAKE.CORTEX.PARSE_DOCUMENT is not available on this account`、または：  
> `AI function _AI_PARSE_DOCUMENT is not available for trial accounts.`

- **原因分析**：
  1. **関数プレフィックスの変更**：新仕様では `SNOWFLAKE.CORTEX.` が廃止され、トップレベル関数 `AI_PARSE_DOCUMENT` / `AI_SUMMARIZE` に統合されました。
  2. **Trial アカウントの GPU 制限**：ドキュメント OCR 解析は大量の GPU 算力を消費するため、Snowflake 公式の **30 日間 Free Trial アカウントでは一律制限されています**。
- **標準回避策**：
  - **商用本番環境**：有償アカウントへ移行することで即座に `AI_PARSE_DOCUMENT` が利用可能。
  - **学習・検証環境**：本章で実証した **ステージ直接読み出し（`TXT_FORMAT`）**、**Snowpark Python によるバイナリ取得（`SnowflakeFile.open`）**、および **チャンクテーブル（`BOX_DOC_CHUNKS`）** を利用することで、完全な検証が可能です。

---

### 避坑ポイント 3：秘密鍵生成時の 2 要素認証（2FA）によるブロック

> [!WARNING] **【エラー現象】**  
> Box Developer Console で「Generate a Public/Private Keypair」を押した際、`2-Step Verification Required` の警告が表示されて生成できない。

- **原因分析**：エンタープライズ権限を有する秘密鍵の漏洩を防ぐため、Box プラットフォーム側で開発者アカウントの 2 要素認証が強制されています。
- **標準回避策**：Box アカウント設定の「セキュリティ」から SMS または Authenticator アプリによる認証を有効化した後、再度生成を行ってください。

---

## 本章のまとめ

本章では**尚硅谷スタイル**を徹底し、非構造化ファイルデータ同期の全技術フローを完結させました：
1. **脱・業務ノイズ**：難解な金融業務を排除し、「クラウドファイルを安全にデータウェアハウスへ搬送する」という純粋な技術課題に集中；
2. **明快なストレージ階層**：
   - **Stage** で物理原本の整合性を担保；
   - **メタデータ台帳表** で SHA-256 による厳密なデータ突合を実現；
   - **チャンク表とステージ直接クエリ** により、ファイル実データに対する柔軟な SQL 検索を確立。
3. **実機レスポンスとトラブルシューティングの透明化**：実際の処理時間（145ms、540ms）、実データ画面、およびエラー回避策を 100% 開示。
