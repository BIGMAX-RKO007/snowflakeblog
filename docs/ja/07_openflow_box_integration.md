# 第 07 章：非構造化ファイルデータ同期の実践 —— Snowflake Openflow と Box クラウドストレージの統合

これまでの章では、リレーショナルデータベース（Oracle 等）内の**構造化テーブルデータ**（顧客テーブルや取引履歴データ）を、CSV/gzip を経由して Snowflake へ効率的に移行・同期する方法を学習してきました。

しかし、現代のエンタープライズデータ分析基盤において、行と列で整理された構造化データに加え、もう一つ極めて大きな比重を占めるデータ資産が存在します。それが、クラウドストレージ（Box、AWS S3、Google Drive 等）に保存されている **PDF 規程書・Word 設計書・TXT 運用チェックリスト・Markdown ドキュメントなどの「非構造化ファイルデータ（Unstructured Files）」** です。

```
【構造化データ】   (Oracle / MySQL テーブル) ───> 従来の ETL / COPY INTO ───> Snowflake テーブル (行と列)
【非構造化データ】 (Box 等のクラウドファイル) ───> Openflow ファイル同期 ─────> Snowflake Stage (原本) ＋ メタデータ表 ＆ 本文チャンク
```

**本章では特定業界の専門業務（銀行や証券の業務知識など）には踏み込まず、純粋な「データ同期と格納・検索のエンジニアリング視点」に立ち**、初学者でも直感的に理解できるように以下の技術要素を体系的に解説します：
1. **データソース側（Source）**：Box をクラウドデータソースとし、サービスアカウントと公開鍵/秘密鍵（JWT）を用いてセキュアに連携する方法。
2. **データパイプライン（Pipeline）**：Snowflake 公式の統合エンジン **Snowflake Openflow**（Apache NiFi 基盤）を活用し、コードを書かずにファイル増分同期（CDC）を実現する仕組み。
3. **データターゲット側（Destination）**：ファイルは Snowflake 内のどこに格納されるのか？メタデータ表には何が記録されるのか？そして、ファイル本文の実データは SQL でどのようにクエリできるのか？

---

## 一、非構造化ファイルデータ同期のシステム構成

データ同期の実装に入る前に、まずは下図でシステム全体のデータの流れを整理します。「データソース $\rightarrow$ 転送パイプライン $\rightarrow$ ターゲット格納層 $\rightarrow$ クエリと活用」の 4 つのフェーズで構成されています：

```mermaid
flowchart TD
    subgraph Source["データソース (Data Source)"]
        B1["Box 共有フォルダ<br/>(PDF / Word / TXT などの元ファイルを保存)"]
        B2["Box カスタムアプリ (Custom App)<br/>(JWT 鍵ペアによるサーバー間自動認証)"]
        B3["Box 監査イベントストリーム<br/>(過去14日間の CDC 差分変更を追跡)"]
    end

    subgraph Pipeline["データ転送パイプライン (Ingestion Pipeline)"]
        O1["Snowflake Openflow Connector for Box"]
        O2["コネクタ構成パラメータ<br/>(Box Source / SF Destination / Ingestion)"]
        O3["軽量ランタイムエンジン<br/>(自動取得・障害再試行・ハッシュ計算)"]
    end

    subgraph Destination["データターゲット (Snowflake Destination)"]
        subgraph Physical["1. 物理ファイル格納層"]
            S1["内部ステージ<br/>(@BOX_RAW_STAGE/<br/>ファイルの物理バイナリ原本を保存)"]
        end

        subgraph Metadata["2. メタデータ台帳・整合性突合層"]
            S2["メタデータインデックス表<br/>(BOX_DOCUMENT_METADATA<br/>ファイル名、サイズ、SHA-256、同期日時を記録)"]
        end

        subgraph TextLayer["3. 本文チャンク・構造化層"]
            S3["テキストチャンク表<br/>(BOX_DOC_CHUNKS<br/>長文文書を段落単位に分割・権限紐付け)"]
        end
    end

    subgraph QueryLayer["データ検索・活用層"]
        Q1["SQL ステージ直接クエリ<br/>(テキスト原本本文の閲覧)"]
        Q2["SQL メタデータクエリ<br/>(ファイルサイズとハッシュの突合)"]
        Q3["SQL チャンク検索<br/>(条文・段落データの抽出)"]
        Q4["AI / セマンティック検索<br/>(Cortex Search Service)"]
    end

    B1 -->|フォルダ共有招待| B2
    B2 -->|JWT 秘密鍵による免密接続| O1
    B3 -.->|変更イベント検知| O1
    O1 --> O3
    O3 -->|原本配置| S1
    O3 -->|メタデータ登録| S2
    O3 -->|本文解析とチャンク化| S3
    S1 --> Q1
    S2 --> Q2
    S3 --> Q3
    S3 --> Q4

    style Source fill:#f0f5ff,stroke:#adc6ff
    style Pipeline fill:#f6ffed,stroke:#b7eb8f
    style Destination fill:#fff7e6,stroke:#ffd591
    style QueryLayer fill:#f9f0ff,stroke:#d3adf7
```

### 2 つの技術実装アプローチの客観的比較

| 評価軸 | アプローチ A：Snowflake Openflow コネクタ（本章推奨） | アプローチ B：自作 Python スクリプト ＋ Box REST API |
| :--- | :--- | :--- |
| **開発・検証工数** | **極小（GUI 設定のみ、半日程度で疎通完了）** | 大（OAuth 更新、再帰探索、リトライ処理のコード開発が必要） |
| **クレデンシャル管理** | **Openflow 内で JWT 秘密鍵設定をネイティブに暗号化管理** | 独自サーバーで Token ストレージ構築、有効期限の自動更新が必要 |
| **増分同期 (CDC)** | **標準装備：Box 監査イベントストリームによる自動追従** | ウォーターマーク日時の自前管理、または Webhook 受信基盤の開発が必要 |
| **メタデータと一貫性** | **ファイルサイズおよび SHA-256 ハッシュを自動算出して記録** | ローカルスクリプトでハッシュを計算し、SQL を発行して登録 |
| **権限継承 (ACL)** | **ファイル・フォルダに付与された閲覧者メールアドレスを自動抽出** | Box コラボレーション API を再帰的に呼び出して権限マッピングを自作 |

---

## 二、フェーズ 1：Box データソース側の事前準備

データ同期エンジンが Box 上のファイルを安全に取得できるように、Box Developer Console にて専用のサービスアカウント（Custom App）を作成し、同期対象のフォルダをそのアカウントに共有します。

### Step 1.1: バックエンドサービスアプリ（Custom App）の新規作成
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

### Step 1.2: 最小権限スコープ（Application Scopes）の設定
アプリの **「Configuration」** タブを開き、データ同期に必要なスコープを設定します：

1. **App Access Level**：**「App + Enterprise Access」** を選択。
2. **Content Scopes**：
   - `Read all files and folders stored in Box`：**チェック**（ファイル一覧とバイナリ取得に必須）。
   - `Write all files and folders stored in Box`：**チェック**（Box 側でダウンロード用トークンを払い出すために必須の仕様です。ファイル本体への変更は一切行いません）。

![Box ファイル読み取り権限スコープの設定](../images/07_step_03_box_content_scopes.png)

3. **Administrative Actions**：
   - `Manage users` および `Manage groups`：チェック（ファイルごとのアクセス権限リスト `user_emails` の抽出用）。
   - `Manage enterprise properties`：チェック（監査イベントストリームを取得し、増分 CDC 同期を実現するため）。

![Box ユーザーおよび管理権限スコープの設定](../images/07_step_04_box_admin_scopes.png)

### Step 1.3: 鍵ペアの生成と構成ファイル（`config.json`）の取得
1. 設定画面の下部にある **「Add and Manage Public Keys」** セクションへ移動します。

![公開鍵・秘密鍵管理セクション](../images/07_step_05_box_keypair_section.png)

2. **「Generate a Public/Private Keypair」** をクリックします：
   > [!NOTE] **2要素認証（2FA）の必須要件**  
   > 秘密鍵生成には、Box アカウントにおける 2 要素認証の有効化が必須です。警告が表示された場合は、アカウント設定で認証アプリまたは SMS を設定した後に再実行してください。
   > 
   > ![Box 2要素認証セキュリティ確認](../images/07_step_06_box_2fa_prompt.png)

3. 生成が完了すると、ブラウザから JSON 認証ファイル（例：`2717878_xxxx_config.json`）が自動ダウンロードされます。この中には `clientID`、`enterpriseID`、および RSA 秘密鍵が含まれており、Openflow 接続時の主要な認証設定となります。

### Step 1.4: 管理者承認とサービスアカウントの取得
1. アプリの **「Authorization」** タブへ切り替え、**「Review and Submit」** をクリックして承認申請を提出します。
2. Box 組織管理者が [Box 管理コンソール](https://app.box.com/master) の「カスタムアプリマネージャー」から **「承認 (Authorize)」** をクリックします。
3. アプリの **「General Settings」** 画面から、発行された固有のサービスアカウントのメールアドレスをコピーします：
   - 書式例：`AutomationUser_2717878_XevDdBO55B@boxdevedition.com`

### Step 1.5: 対象フォルダの共有招待と Folder ID の取得
1. Box の Web 画面で、同期対象とするフォルダ（例：`社内規程マニュアル`）を新規作成または指定します。
2. **「共有」** $\rightarrow$ **「コラボレータを招待」** を開き、先ほどのサービスアカウントのメールアドレスを貼り付け、権限を **「ビューアー (Viewer)」** に設定します。

![Box フォルダへのサービスアカウント招待](../images/07_step_07_box_folder_collaborator.png)

3. **Folder ID の記録**：ブラウザのアドレスバーの末尾にある数値 ID（例：`https://app.box.com/folder/431546000913` の **`431546000913`**）を記録します。`0` を指定するとルート配下全体が対象になります。

### Step 1.6: 検証用テストファイルのアップロード
様々なフォーマットの同期を網羅的に検証するため、3 種類の代表的なテストファイルを準備しました：
- `01_情報セキュリティ基本規程_2026.pdf`（PDF 文書、サイズ 781 バイト）
- `02_クラウド移行プロジェクト_機密設計書.docx`（Word 文書、サイズ 1,825 バイト）
- `03_コンプライアンス遵守チェックリスト_2026.txt`（プレーンテキスト、サイズ 1,429 バイト）

対象フォルダへアップロードし、ファイルが正常に登録されたことを確認します：

![Box フォルダへのテストファイルアップロード完了](../images/07_step_08_box_files_uploaded.png)

---

## 三、フェーズ 2：Snowflake ターゲット環境の構築と RBAC

Snowflake 側では、最小特権の原則に基づき、同期コネクタ専用のロール・サービスユーザー・仮想ウェアハウス・内部ステージ・テーブルを作成します。

プロジェクトに同梱の [`07_openflow_box_setup.sql`](file:///c:/Users/FX/Projects/SnowflakeBlog/scripts/snowflake/07_openflow_box_setup.sql) を実行します：

```sql
-- 1. セキュリティおよびロール構成 (SECURITYADMIN)
USE ROLE SECURITYADMIN;

-- コネクタ専用実行ロール
CREATE ROLE IF NOT EXISTS OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Snowflake Openflow Box コネクタ専用実行ロール';

-- 下流クエリ用読み取りロール
CREATE ROLE IF NOT EXISTS CORTEX_SEARCH_READ_ROLE
    COMMENT = '下流検索アプリケーション用の読み取り専用ロール';

-- パイプライン専用サービスアカウント (鍵ペア認証対応)
CREATE USER IF NOT EXISTS OPENFLOW_BOX_SVC_USER
    TYPE = SERVICE
    DEFAULT_ROLE = OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Openflow データパイプライン専用サービスユーザー';

GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO USER OPENFLOW_BOX_SVC_USER;
GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO ROLE SYSADMIN;
GRANT ROLE CORTEX_SEARCH_READ_ROLE TO ROLE SYSADMIN;

-- 2. コンピュートおよびストレージの作成 (SYSADMIN)
USE ROLE SYSADMIN;

-- 同期処理専用の軽量ウェアハウス
CREATE WAREHOUSE IF NOT EXISTS OPENFLOW_INGEST_WH
    WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Box ファイル同期とテキストチャンク処理専用のコンピュートリソース';

-- データベースと階層スキーマの作成
CREATE DATABASE IF NOT EXISTS BOX_INTEGRATION_DB;

-- ランディング層：ステージ原本およびメタデータテーブル
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.BOX_LANDING_DATA;

-- 処理・検索層：チャンク分割データおよび検索インデックス
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.CORTEX;

-- コネクタロールへの権限付与
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

## 四、フェーズ 3：Openflow コネクタ設定の全パラメータ対応表

Snowflake Openflow 上で **Openflow Connector for Box** を設定する際に求められる 3 大カテゴリのパラメータ辞書です：

### 1. Boxソースパラメーター (Box Source Parameters)

| パラメータ名（日 / 英） | 概要・役割 | 推奨設定値 | 技術的補足 |
| :--- | :--- | :--- | :--- |
| **Box App 構成 JSON**<br/>*(Box App Configuration JSON)* | Box 認証 JSON 文字列 | `{ "boxAppSettings": { ... } }` | フェーズ 1 で取得した `config.json` のテキスト内容全体をそのまま貼り付けます。 |
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

## 五、フェーズ 4：データ同期の確証と SQL による実データ検証

同期が完了すると、ファイルは Box から Snowflake へ転送されます。エンジニアリング視点でデータ同期の成果を確認するため、3 つのステップで実機検証を行います：

### 検証 ①：メタデータ台帳による整合性突合（Metadata Reconciliation）

ファイル同期完了後、メタデータテーブル `BOX_DOCUMENT_METADATA` に各ファイルの属性が記録されます。Snowflake ワークシート上で以下の SQL を実行します：

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

- **実機検証画面と結果**：
わずか 540ms で 3 件のレコードが返却されました。`SIZE_BYTES` および SHA-256 ハッシュ値がローカルの元ファイルと 100% 一致しており、**データ欠損や破損がゼロであること**が証明されました：

![Snowflake ワークシート画面でのリアルメタデータ突合検証結果](../images/07_step_09_snowflake_stage_files.png)

---

### 検証 ②：SQL によるステージ内テキストファイル実データの直接読み出し

> [!QUESTION] **初学者のよくある疑問**  
> 上記のクエリで取得できたのはファイル名やサイズなどの「**メタデータ（属性情報）**」です。では、**ファイルの中身の実データ**は Snowflake で直接確認できるのでしょうか？

**答えは「完全に可能です」。** 実際の物理ファイル原本は `@BOX_RAW_STAGE` 内にそのまま保存されています。

プレーンテキスト形式のファイル（`.txt`、`.csv`、`.md`、`.json` 等）であれば、Snowflake のステージクエリ機能を用いて SQL から直接本文の行データを読み出せます。

> [!WARNING] **トラブルシューティング：日本語パスの構文エラー回避**  
> `@BOX_RAW_STAGE/compliance/03_コンプライアンス...` のように日本語を含むパスをクォーテーションなしで記述すると、SQL レキサーが非 ASCII 文字を正しく解釈できず `SQL compilation error: syntax error ... unexpected 'コン'` が発生します。  
> **正しい対応策**：単一列プレーンテキスト用のファイルフォーマットを定義し、シングルクォーテーション付きパスまたは `PATTERN` 正規表現を用いて安全に指定します：

```sql
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. 単一列プレーンテキスト形式の定義 (カンマ区切りを行わず行ごとに取得)
CREATE OR REPLACE FILE FORMAT BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT 
    TYPE = 'CSV' 
    FIELD_DELIMITER = NONE 
    RECORD_DELIMITER = '\n';

-- 2. ステージ上の 03_コンプライアンス遵守チェックリスト_2026.txt の実本文データを直接クエリ
SELECT $1 AS FILE_CONTENT 
FROM '@BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_RAW_STAGE/compliance/' 
(FILE_FORMAT => 'BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT', PATTERN => '.*03.*txt');
```

- **Snowflake ブラウザ実行画面と実データ結果**：
実行時間はわずか **145ms** で、テキストファイルに含まれる全 **20 行の実本文データ**（章立てや日常点検項目など）がクエリ結果グリッドに直接表示されました：

![Snowflake Stage ファイル本文データの直接クエリ実行結果](../images/07_step_10_stage_file_content_query.png)

---

### 検証 ③：解析・チャンク化済み PDF / Word の実本文データ検索

PDF や Word（`.docx`）などのバイナリファイルは、取り込みパイプラインによってテキスト段落（Text Chunks）に分割され、`BOX_DOC_CHUNKS` テーブルへ格納されます。

これにより、通常のデータベーステーブルと同様に、SQL を用いて PDF や Word 内の特定の条文や段落を直接抽出できます：

```sql
-- チャンク化・構造化された PDF および Word の実文書本文をクエリ
SELECT 
    FILE_NAME,
    CHUNK_INDEX,
    CHUNK_TEXT
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
ORDER BY FILE_ID, CHUNK_INDEX;
```

- **Snowflake ブラウザ実行画面と実データ結果**：
実行時間 **143ms** で、『01_情報セキュリティ基本規程_2026.pdf』のパスワード運用規程や『02_クラウド移行プロジェクト_機密設計書.docx』の閉域網設計といった実際の内容が確認できます：

![Snowflake Cortex 文書チャンク実データ検索結果](../images/07_step_11_doc_chunks_content_query.png)

---

### 検証 ④：原本プレビュー・ダウンロード用 URL の生成（Scoped URL）

業務システムやブラウザ上で元の PDF や Word ファイルを直接開きたい場合は、Snowflake 組み込みの `BUILD_SCOPED_FILE_URL` 関数を使用します：

```sql
SELECT 
    RELATIVE_PATH,
    SIZE,
    -- 時限付き認証トークンを含む安全なダウンロード/プレビュー URL を発行
    BUILD_SCOPED_FILE_URL(@BOX_RAW_STAGE, RELATIVE_PATH) AS DIRECT_DOWNLOAD_URL
FROM DIRECTORY(@BOX_RAW_STAGE);
```
出力された URL をクリックすることで、ブラウザから元ファイルをそのままダウンロードまたは閲覧できます。

---

## 六、技術的留意点：Trial アカウントと本番エンタープライズの機能仕様

非構造化ファイルの処理において、初学者がつまずきやすい関数仕様の違いを整理します：

1. **関数プレフィックスの統合**：
   - 近年の Snowflake では、旧来の `SNOWFLAKE.CORTEX.PARSE_DOCUMENT` や `SUMMARIZE` は、トップレベルの SQL 関数 `AI_PARSE_DOCUMENT` および `AI_SUMMARIZE` へ移行しています。
2. **無料試用（Trial）アカウントにおける GPU リソース制限**：
   - PDF のレイアウト解析や OCR を実行する `AI_PARSE_DOCUMENT` は GPU 負荷が高いため、Snowflake 公式の **30 日間 Free Trial アカウントでは一律で実行がブロックされています**（システムエラー：`AI function _AI_PARSE_DOCUMENT is not available for trial accounts`）。
   - **本番環境と検証環境の使い分け**：
     - エンタープライズ有償環境では、本関数を呼び出すことで PDF や画像からの全自動テキスト抽出が利用可能です。
     - 試用環境や学習段階においては、本章で実証した **ステージ直接読み出し（`TXT_FORMAT`）**、**Snowpark Python によるバイナリ取得（`SnowflakeFile.open`）**、および **チャンクテーブル（`BOX_DOC_CHUNKS`）** を利用することで、完全なデータ同期と検索パイプラインを検証できます。

---

## 本章のまとめ

本章では、特定の業務ドメインに依存せず、**データエンジニアリングと同期技術の基本**に立ち返って Box から Snowflake へのパイプラインを構築しました：
1. **ソース側**：Box JWT サービスアカウントによる安全な接続とフォルダ共有。
2. **パイプライン**：Openflow コネクタによる完全自動のファイル搬送と CDC 増分検知。
3. **ターゲット側**：
   - **Stage** で物理原本の整合性を担保；
   - **メタデータ表** で SHA-256 ハッシュによる厳密なデータ突合を実現；
   - **チャンク表とステージ直接クエリ** により、ファイル実データに対する柔軟な SQL 検索を確立。
