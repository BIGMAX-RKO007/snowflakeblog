# 第 07-2 章：Snowflake Openflow による Box クラウド連携と Cortex ナレッジ検索実践

> 💡 **シリーズナビゲーション**：本章は Openflow 実践編です。事前に [第 07-1 章：Snowflake Openflow コアアーキテクチャとマルチモーダルデータ統合](./07_01_openflow_architecture_and_concepts.md) を通じて Apache NiFi エンジン、SPCS デプロイモデル、統合ガバナンス基盤をご確認いただくことを推奨します。
>
> 本章は **『尚硅谷（Shangguigu）技術テキスト作成規範』** に準拠して全面再構成されています：本質を突く極小比較、業務ノイズを排除した純粋技術フォーカス、全 SQL 設定項目の 1 行単位での徹底解説、実機キャプチャとミリ秒単位の実行ログによる AI 幻覚（ハルシネーション）の完全排除、落とし穴と回避策の明示、前提条件の完全前置。

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

- **初学者の根本的な疑問**：クラウド上のファイルはどのように自動・増分同期されるのか？同期された原本は Snowflake のどこに格納されるのか？メタデータ表は何を記録しているのか？各 SQL 設定パラメータの技術的背景は何か？そして最も重要な点として：**「ファイルの中身の実データは SQL で直接参照できるのか？AI の幻覚ではなく実機画面で証明されているのか？」**
- **本章の目的**：特定の業務ドメイン（銀行や証券の難解な業務ルール）を完全に排除し、純粋な**データ同期・階層ストレージ・1行ごとのパラメータ解析・SQL クエリ実証のエンジニアリング視点**で、実機キャプチャとミリ秒単位の実行メトリクスを交えて全行程を完結させます！

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

### 比較評価：Openflow コネクタ vs 自作 Python スクリプト

| 評価軸 | パターン A：Snowflake Openflow コネクタ（推奨） | パターン B：自作 Python による Box REST API 呼出 |
| :--- | :--- | :--- |
| **開発工数** | **極小（設定パラメータの入力のみ、数時間で疎通完了）** | 大（認証トークン更新、ページネーション、リトライ実装が必要） |
| **認証情報管理** | **Openflow が暗号化保管（JWT `config.json` を安全に管理）** | 自前のシークレット管理が必要、2時間でのトークン失効対策が必要 |
| **増分同期 (CDC)** | **標準対応：Box の過去 14 日間監査イベントストリームを自動追跡** | 自前で更新日時ウォーターマークや Webhook サーバーの保守が必要 |
| **データ整合性担保** | **SHA-256 ハッシュ値とファイルサイズを自動計算・テーブル格納** | ダウンロードストリーム内でハッシュ計算と INSERT を手動実装 |
| **アクセス権限継承** | **Box 側の閲覧許可ユーザーリスト（`user_emails`）を自動抽出** | Box コラボレーション API を再帰的に呼び出す複雑なロジックが必要 |

---

## 三、コアメカニズム解剖：Stage 原本保管 vs テーブル構造化チャンク（二段式ストレージ）とマルチソース統治

非構造化ドキュメントをデータレイクハウスに統合する際、エンジニアが最も頻繁に直面する 2 つの疑問に答えます：

### 疑問 1：ファイル原本をそのまま保管するのか？それとも ETL でテーブル列に格納するのか？

結論：**本番のエンタープライズ設計では「二者択一」ではなく、「二段階ハイブリッドストレージ（Two-Stage Hybrid Architecture）」を採用します！**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│               非構造化ドキュメント二段階ストレージアーキテクチャ (Two-Stage Hybrid)        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│                                  【データソース：Box クラウド】                          │
│                           (PDF 規程書 / Word 設計書 / TXT チェックリスト)               │
│                                              │                                         │
│                                              ▼                                         │
│                 ┌────────────────────────────────────────────────────────┐             │
│                 │ 第 1 段階：物理原本ステージ層 (Raw Ingestion Layer)     │             │
│                 │ • 格納先：Snowflake 内部受管ステージ (@BOX_RAW_STAGE/)   │             │
│                 │ • 特徴：バイナリ完全保持、レイアウト・画像・書式を非破壊│             │
│                 │ • 価値：監査証跡、改ざん防止、時限署名 URL (Scoped URL)  │             │
│                 └────────────────────────────────────────────────────────┘             │
│                                              │                                         │
│                      ┌───────────────────────┴───────────────────────┐                 │
│                      ▼                                               ▼                 │
│ ┌──────────────────────────────────────────┐   ┌─────────────────────────────────────┐ │
│ │ 第 2 段階 A：メタデータ台帳表 (Catalog)  │   │ 第 2 段階 B：本文チャンク表 (Chunks)│ │
│ │ • テーブル名：BOX_DOCUMENT_METADATA      │   │ • テーブル名：BOX_DOC_CHUNKS        │ │
│ │ • カラム：ファイル ID、SHA-256、サイズ   │   │ • カラム：段落番号、本文、Embedding │ │
│ │ • 価値：データ整合性突合、重複取り込み防止│   │ • 価値：全文検索、SQL フィルタ、RAG │ │
│ └──────────────────────────────────────────┘   └─────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **第 1 段階：ステージ原本保管**：
   - ファイルのバイナリを損なうことなく内部ステージ（`@BOX_RAW_STAGE`）に格納します。
   - **価値**：監査法人の原本確認要件を満たすとともに、Snowflake の `BUILD_SCOPED_FILE_URL` 関数を使用して、ブラウザから原本 PDF を直接安全にプレビュー・ダウンロードさせることができます。
2. **第 2 段階：メタデータ台帳登録と本文チャンク分割**：
   - **メタデータ台帳 (`BOX_DOCUMENT_METADATA`)**：ファイルサイズや SHA-256 ハッシュ値を記録し、100% のデータ整合性を担保します；
   - **テキストチャンク表 (`BOX_DOC_CHUNKS`)**：数万字のドキュメントを段落ごとに分割（例：500 文字/チャンク）し、SQL 検索や Cortex ベクトル検索の入力として利用します。

---

### 疑問 2：複数の非構造化データソース（Box, S3, SharePoint, Google Drive）を統合管理する方法は？

データソースが Box だけでなく、AWS S3、SharePoint、Google Drive 等に分散している場合、**「マルチステージ物理分離 + 共通統一カタログテーブル + プラグイン型パーサー + 統一 RLS」** の中台アーキテクチャで一元管理します：

```sql
CREATE OR REPLACE TABLE UNSTRUCTURED_DOCUMENT_CATALOG (
    -- ドキュメントグローバル一意識別子 (SHA-256 または UUID)
    doc_global_id         VARCHAR(64) PRIMARY KEY,
    
    -- ソースシステム情報
    source_system         VARCHAR(32) NOT NULL,   -- 'BOX', 'AWS_S3', 'SHAREPOINT', 'LOCAL_SFTP'
    source_file_id        VARCHAR(256) NOT NULL,  -- ソース側の元ファイル ID
    
    -- 物理ストレージマッピング
    stage_name            VARCHAR(128) NOT NULL,  -- '@BOX_RAW_STAGE', '@S3_CORP_STAGE'
    stage_relative_path   VARCHAR(1024) NOT NULL, -- ステージ内の相対パス
    file_name             VARCHAR(256) NOT NULL,  -- 実ファイル名
    mime_type             VARCHAR(64) NOT NULL,   -- MIME タイプ
    file_size_bytes       NUMBER(38,0) NOT NULL,  -- バイト単位のファイルサイズ
    
    -- データ整合性・冪等性検証
    content_sha256        VARCHAR(64) NOT NULL,   -- SHA-256 ハッシュ値
    ingestion_timestamp   TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    
    -- パース状態管理
    parsing_status        VARCHAR(32) DEFAULT 'PENDING', -- 'PENDING', 'PARSED', 'FAILED'
    parsed_timestamp      TIMESTAMP_LTZ,
    
    -- 拡張メタデータ (JSON 形式でソース固有属性を保持)
    source_metadata       VARIANT,                -- Box フォルダパス、S3 タグ等
    
    -- アクセス制御リスト (ソース側の権限体系を継承)
    acl_permissions       ARRAY                   -- 閲覧許可ユーザー配列 ['tanaka@corp.jp', 'group_sec']
);
```

---

## 四、Box データソース側の準備と認証情報の取得（全行程実機キャプチャ）

### Step 3.1: バックエンドサービスアプリ（Custom App）の作成
1. [Box Developer Console (開発者コンソール)](https://app.box.com/developers/console) へログインします。

![Box Developer Console コントロールパネルTOP](../images/07_step_01_box_console_home.png)

2. 画面右上の **「Create Platform App」** をクリックします。
3. アプリケーションタイプとして **「Custom App」** を選択します。

![Custom App アプリタイプの選択](../images/07_step_02_box_app_type_custom.png)

4. 基本情報を入力します：
   - **App Name**：`Snowflake_Openflow_Box`
   - **Purpose**：`Integration`（データ統合）を選択
5. 認証方式として **「Server Authentication (with JWT)」**（公開鍵/秘密鍵による自動認証）を選択します。

![Server Authentication JWT 認証方式の選択](../images/07_step_02_box_jwt_auth_selection.png)

6. JWT バックエンドアプリの作成を確認します：

![JWT バックエンドアプリ作成の確定画面](../images/07_step_03_box_create_app_jwt.png)

---

### Step 3.2: 最小権限スコープ（Application Scopes）の設定
アプリの **「Configuration」** タブを開き、設定を行います：

![Box アプリ基本設定画面](../images/07_step_04_box_configuration_page.png)

1. **App Access Level**：**「App + Enterprise Access」** を選択。
2. **Content Scopes**：
   - `Read all files and folders stored in Box`：**チェック**（ファイル一覧およびバイナリ取得に必須）。
   - `Write all files and folders stored in Box`：**チェック**（ダウンロード用トークン発行のために必須）。

![Box ファイル読み取り権限スコープの設定](../images/07_step_03_box_content_scopes.png)

3. **Administrative Actions**：
   - `Manage users` および `Manage groups`：チェック（アクセス権限リスト `user_emails` の抽出用）。
   - `Manage enterprise properties`：チェック（14 日間監査イベントログによる CDC 同期用）。

![Box ユーザーおよび管理権限スコープの設定](../images/07_step_04_box_admin_scopes.png)

---

### Step 3.3: 鍵ペアの生成と構成ファイル（`config.json`）のダウンロード
1. 設定画面の下部にある **「Add and Manage Public Keys」** セクションへ移動します。

![公開鍵・秘密鍵管理セクション](../images/07_step_05_box_keypair_section.png)

2. **「Generate a Public/Private Keypair」** をクリックします：

![署名鍵管理パネル](../images/07_step_05_manage_signature_keys.png)

> [!WARNING] **【避坑ポイント：Box 2要素認証（2FA）の必須要件】**  
> Box アカウントで 2 要素認証が無効の場合、秘密鍵生成時に警告画面でブロックされます。セキュリティ設定から認証アプリまたは SMS を設定してください：
> 
> ![Box 2要素認証セキュリティ確認](../images/07_step_06_box_2fa_prompt.png)

3. 2 要素認証の完了後、鍵ペアが自動的に生成・構成されます：

![JWT 鍵ペア構成完了画面](../images/07_step_06_jwt_configured.png)

4. 右上の **「Save Changes」** をクリックしてアプリ設定を保存します：

![アプリ設定保存完了](../images/07_step_07_jwt_saved.png)

5. ブラウザから JSON 認証ファイル（例：`2717878_xxxx_config.json`）がダウンロードされます。Client ID や暗号化された RSA 秘密鍵が含まれています：

![認証構成ファイルダウンロード完了](../images/07_step_09_config_downloaded.png)

---

### Step 3.4: フォルダ共有招待と Folder ID の取得
1. アプリの **「General Settings」** 画面から、サービスアカウントのメールアドレスをコピーします（例：`AutomationUser_2717878_XevDdBO55B@boxdevedition.com`）；
2. Box Web 画面で同期対象フォルダ（例：`社内規程マニュアル`）を新規作成します；
3. **「共有」** $\rightarrow$ **「コラボレータを招待」** を開き、上記メールアドレスを貼り付けて権限を **「ビューアー (Viewer)」** に設定します：

![Box フォルダへのサービスアカウント招待](../images/07_step_07_box_folder_collaborator.png)

4. 共有招待が完了し、サービスアカウントが共同作業者として登録されます：

![コラボレーション招待完了画面](../images/07_step_10_folder_collaboration_invited.png)

5. **Folder ID の記録**：アドレスバーの末尾の数値 ID（例：`https://app.box.com/folder/431546000913` の **`431546000913`**）を記録します。`0` を指定するとルート配下全体が対象になります。

---

### Step 3.5: 3 種類のテストファイルのアップロード
3 種類のテストファイルを対象フォルダにアップロードします：
1. `01_情報セキュリティ基本規程_2026.pdf`（PDF 文書、サイズ **781 バイト**）
2. `02_クラウド移行プロジェクト_機密設計書.docx`（Word 文書、サイズ **1,825 バイト**）
3. `03_コンプライアンス遵守チェックリスト_2026.txt`（プレーンテキスト、サイズ **1,429 バイト**）

フォルダ内でファイルが正常に認識されていることを確認します：

![Box フォルダへのテストファイルアップロード完了](../images/07_step_08_box_files_uploaded.png)

---

## 五、Snowflake ターゲット環境の構築（全 DDL スクリプトと 1 行ごとのパラメータ徹底解説）

Snowflake 側では、最小特権の原則に基づき、専用のロール・サービスユーザー・仮想ウェアハウス・内部ステージ・テーブルを作成します。

同梱の初期化スクリプト [`07_openflow_box_setup.sql`](file:///c:/Users/FX/Projects/SnowflakeBlog/scripts/snowflake/07_openflow_box_setup.sql) を実行します：

```sql
-- 1. セキュリティおよびロール構成 (SECURITYADMIN)
USE ROLE SECURITYADMIN;

-- データ同期専用ロールの作成
CREATE ROLE IF NOT EXISTS OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Snowflake Openflow Box コネクタ専用実行ロール';

-- 下流検索アプリケーション用読み取りロールの作成
CREATE ROLE IF NOT EXISTS CORTEX_SEARCH_READ_ROLE
    COMMENT = '下流検索アプリケーション用の読み取り専用ロール';

-- パイプライン自動化専用サービスユーザーの作成 (公開鍵免密認証)
CREATE USER IF NOT EXISTS OPENFLOW_BOX_SVC_USER
    TYPE = SERVICE
    DEFAULT_ROLE = OPENFLOW_CONNECTOR_ROLE
    COMMENT = 'Openflow データパイプライン専用サービスユーザー';

GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO USER OPENFLOW_BOX_SVC_USER;
GRANT ROLE OPENFLOW_CONNECTOR_ROLE TO ROLE SYSADMIN;
GRANT ROLE CORTEX_SEARCH_READ_ROLE TO ROLE SYSADMIN;

-- 2. コンピュートおよびストレージの作成 (SYSADMIN)
USE ROLE SYSADMIN;

-- データ同期専用の軽量仮想ウェアハウスを作成
CREATE WAREHOUSE IF NOT EXISTS OPENFLOW_INGEST_WH
    WITH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Box ファイル同期とテキストチャンク処理専用のコンピュートリソース';

-- データベースと階層スキーマの作成
CREATE DATABASE IF NOT EXISTS BOX_INTEGRATION_DB;
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.BOX_LANDING_DATA;
CREATE SCHEMA IF NOT EXISTS BOX_INTEGRATION_DB.CORTEX;

-- コネクタ専用ロールへの権限付与
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

### 1行ごとの設定項目・パラメータ徹底解説（技術辞書）

すべての SQL 設定意図を完全に透明化するため、上記スクリプトの各パラメータを詳細に解説します：

#### 1. サービスアカウントと権限項目 (`CREATE USER ... TYPE = SERVICE`)

| 設定項目 | 設定値 | 技術的根拠とセキュリティベストプラクティス |
| :--- | :--- | :--- |
| `TYPE = SERVICE` | `SERVICE` | **専用サービスアカウント種別**。一般の対話型ユーザー（`PERSON`）と異なり、Web 画面ログインやパスワード認証を禁止し、RSA 鍵ペア（Keypair）による非対話型 API 自動実行に特化させます。企業の SSO パスワード失効ポリシーの影響を受けません。 |
| `DEFAULT_ROLE` | `OPENFLOW_CONNECTOR_ROLE` | **デフォルトアクティブロール**。Openflow が接続した際に明示的な Role 指定が省略された場合、自動的にこの専用ロールが適用され、不要な権限行使を防ぎます。 |
| `GRANT ROLE ... TO SYSADMIN` | ロール継承 | **Snowflake セキュリティ標準**。すべてのカスタムロールを最上位の `SYSADMIN` に階層集約することで、管理不能な「野良ロール」の発生を防止します。 |

#### 2. コンピュートウェアハウス設定項目 (`CREATE WAREHOUSE OPENFLOW_INGEST_WH`)

| 設定項目 | 設定値 | 技術的根拠とコスト防衛策 |
| :--- | :--- | :--- |
| `WAREHOUSE_SIZE` | `'XSMALL'` | **最小算力スペック（1 クレジット/時間）**。メタデータ書き込みやテキスト分割処理は I/O 主体の軽量タスクであり、XSMALL で十分なスループットを発揮します。無駄な課金を防止します。 |
| `AUTO_SUSPEND` | `120`（秒） | **2分間のアイドル後自動停止**。バッチ処理の終了後、2分間新規クエリがなければ即座にウェアハウスが休眠し、アイドリング課金を遮断します。 |
| `AUTO_RESUME` | `TRUE` | **自動再開フラグ**。下流からクエリや書き込み要求が到着すると、1秒以内に自動起動します。 |
| `INITIALLY_SUSPENDED` | `TRUE` | **作成時即座サスペンド**。オブジェクト作成直後から課金が発生することを防ぎ、初回の実クエリ発行時まで停止状態を維持します。 |

#### 3. 内部ステージ設定項目 (`CREATE STAGE BOX_RAW_STAGE`)

| 設定項目 | 設定値 | 技術的根拠と機能連携 |
| :--- | :--- | :--- |
| `DIRECTORY = (ENABLE = TRUE)` | `ENABLE = TRUE` | **ステージディレクトリテーブル（Directory Table）の有効化**。非構造化データ管理の最重要機能です。有効化によりステージ内のファイルをテーブルのように `SELECT * FROM DIRECTORY(@BOX_RAW_STAGE)` でクエリでき、Snowflake Stream をバインドして差分検知が可能になります。 |
| `ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')` | `'SNOWFLAKE_SSE'` | **サーバーサイド暗号化**。AES-256 アルゴリズムを用い、Snowflake 管理の鍵によって自動暗号化されます。原本ファイル保存時の静止データ機密性を担保します。 |

#### 4. メタデータ台帳テーブル設定項目 (`BOX_DOCUMENT_METADATA`)

| カラム名 | データ型制約 | 技術的役割と業務的意義 |
| :--- | :--- | :--- |
| `FILE_ID` | `VARCHAR(64) PRIMARY KEY` | **Box 側の一意オブジェクト ID**。主キー制約を付与し、増分同期時の Upsert 冪等性を保証します。 |
| `FILE_NAME` | `VARCHAR(512) NOT NULL` | **拡張子付きファイル名**。検索およびファイル形式識別のキーとなります。 |
| `FOLDER_ID` / `FOLDER_PATH` | `VARCHAR` | **フォルダ階層パンくず情報**。ソース側の配置コンテキストを保存します。 |
| `SHA256_HASH` | `VARCHAR(128) NOT NULL` | **ファイル本体の SHA-256 暗号化ハッシュ値**。コンテンツ変更検知（CDC）およびネットワーク伝送時のビット化け検知の絶対基準です。 |
| `SIZE_BYTES` | `NUMBER(38, 0)` | **正確なファイルバイト数**。ソース側ファイルサイズとの完全一致を突合します。 |
| `BOX_CREATED_AT` / `MODIFIED_AT` | `TIMESTAMP_NTZ` | **ソース側の作成・更新タイムスタンプ**。増分同期の水位線（ウォーターマーク）となります。 |
| `USER_EMAILS` | `ARRAY` | **アクセス権限リスト（ACL）**。半構造化配列として格納し、行レベルセキュリティ（RAP）のフィルタ対象とします。 |

#### 5. 本文チャンクテーブル設定項目 (`BOX_DOC_CHUNKS`)

| カラム名 | データ型制約 | 技術的役割と業務的意義 |
| :--- | :--- | :--- |
| `CHUNK_ID` | `VARCHAR(128) PRIMARY KEY` | **複合チャンク主キー**。`<file_id>_<chunk_index>` の命名規則により一意性を保証します。 |
| `CHUNK_INDEX` | `NUMBER(10, 0)` | **段落連番**。ドキュメント内での前後の文脈順序を保持します。 |
| `CHUNK_TEXT` | `VARCHAR(16777216) NOT NULL` | **段落のテキスト実データ**。Snowflake 最大幅の 16MB 列を使用し、分割された本文を格納します。 |
| `USER_EMAILS` | `ARRAY NOT NULL` | **継承権限リスト**。チャンク検索時にも権限フィルタを適用し、情報漏洩を防ぎます。 |

---

## 六、Openflow コネクタ設定の全パラメータ対応表

**Openflow Connector for Box** を設定する際、ウィザードで指定する全パラメータの詳細対比表です：

### 1. Box データソース側パラメータ（Boxソースパラメーター / Box Source Parameters）

| 設定項目（日 / 英） | 推奨値 | 詳細な技術仕様 |
| :--- | :--- | :--- |
| **Box App 構成 JSON**<br/>*(Box App Configuration JSON)* | `{ "boxAppSettings": { ... } }` | Step 3.3 でダウンロードした `config.json` のテキスト内容をそのまま貼り付けます。 |
| **Box App構成ファイル**<br/>*(Box App Configuration File)* | `/path/to/box_config.json` | CLI やボリュームマウント経由で指定する場合の物理ファイルパス（JSON テキストと排他）。 |

### 2. Snowflake ターゲット側パラメータ（Box宛先パラメーター / Box Destination Parameters）

| 設定項目（日 / 英） | 推奨値 | 詳細な技術仕様 |
| :--- | :--- | :--- |
| **宛先データベース**<br/>*(Destination Database)* | `BOX_INTEGRATION_DB` | ステージおよびメタデータテーブルが配置されているターゲット DB。 |
| **宛先スキーマ**<br/>*(Destination Schema)* | `BOX_LANDING_DATA` | ファイル原本を配置するランディング層のスキーマ。 |
| **Snowflake認証ストラテジー**<br/>*(Snowflake Authentication Strategy)* | `Keypair`（推奨） | RSA 公開鍵・秘密鍵ペアによる自動認証（パスワード失効リスクを完全排除）。 |
| **Snowflakeアカウント識別子**<br/>*(Snowflake Account Identifier)* | `aakjsrd-oq04293` | 組織名とアカウント名（`<org>-<account>` 形式）。 |
| **Snowflake秘密キー**<br/>*(Snowflake Private Key)* | `-----BEGIN ENCRYPTED PRIVATE KEY-----...` | サービスアカウント（`OPENFLOW_BOX_SVC_USER`）にバインドされた秘密鍵テキスト。 |
| **Snowflake秘密キーファイル**<br/>*(Snowflake Private Key File)* | `/secrets/rsa_key.p8` | 秘密鍵の物理マウントパス（秘密鍵テキストと排他）。 |
| **Snowflake秘密キーパスワード**<br/>*(Snowflake Private Key Password)* | `********` | 秘密鍵の暗号化パスフレーズ（暗号化されていない場合は空欄）。 |
| **Snowflakeロール**<br/>*(Snowflake Role)* | `OPENFLOW_CONNECTOR_ROLE` | ターゲットステージへの書き込み権限を持つ専用実行ロール。 |
| **Snowflakeのユーザー名**<br/>*(Snowflake Username)* | `OPENFLOW_BOX_SVC_USER` | パイプライン専用サービスアカウントの名称。 |
| **オーバーサイズ値戦略**<br/>*(Oversized Value Strategy)* | `Truncate`（切り捨て）または `Fail`（エラー） | Box メタデータが Snowflake の列制限を超過した際の処理ポリシー。 |
| **Snowflakeウェアハウス**<br/>*(Snowflake Warehouse)* | `OPENFLOW_INGEST_WH` | メタデータ登録およびステージ更新を実行する仮想ウェアハウス。 |

### 3. 取り込みパラメータ（Box取り込みパラメーター / Box Ingestion Parameters）

| 設定項目（日 / 英） | 推奨値 | 詳細な技術仕様 |
| :--- | :--- | :--- |
| **Boxフォルダー ID**<br/>*(Box Folder ID)* | `431546000913`（または `0`） | 対象となる Box フォルダの ID。`0` を指定するとアクセス可能な全フォルダを走査します。 |
| **取り込むファイルの拡張子**<br/>*(Extensions of Files to Ingest)* | `pdf,docx,txt,md` | 取り込み対象とする拡張子のホワイトリスト（カンマ区切り、ドットなし）。 |
| **Snowflakeファイルのハッシュテーブル名**<br/>*(Snowflake File Hash Table Name)* | `BOX_DOCUMENT_METADATA` | バージョン管理、ハッシュ値、CDC 状態を管理する台帳テーブル名。 |

---

## 七、データ同期の動作検証と実機キャプチャ（AI 幻覚の完全排除）

同期実行後、Box のファイルが Snowflake に正しく到達しているかを検証します。**「課題の提示 $\rightarrow$ 標準 SQL $\rightarrow$ 実機コンソール画面キャプチャとミリ秒単位のメトリクス」** の 3 ステップで進めます：

### 実機検証環境のメトリクス情報：
- **検証組織・アカウント**：`aakjsrd-oq04293` (AWS Tokyo リージョン)
- **仮想ウェアハウス**：`OPENFLOW_INGEST_WH` (X-Small)
- **対象データベース**：`BOX_INTEGRATION_DB`
- **検証メトリクス**：すべての画面キャプチャは実際の Snowflake Worksheets 実行結果を直接記録したものです。

---

### 実証 1：メタデータ台帳クエリとハッシュ突合（Metadata Reconciliation）

- **【課題】**：ファイルが同期された後、途中でバイト欠損がなく最新版であることをどう確認するか？
- **【標準構文】**：メタデータ台帳を照会し、ファイルサイズおよび SHA-256 ハッシュ値を検証します：

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

- **【実機コンソール実行結果と画面キャプチャ】**：
実行時間 **540ms**。3 件の台帳レコードが正常に取得されました。各ファイルの `SIZE_BYTES` と SHA-256 ハッシュ値は Box 上の原本と 100% 完全一致（PDF: 781 バイト、DOCX: 1,825 バイト、TXT: 1,429 バイト）しており、**転送時のバイト欠損ゼロ** が実証されています：

![Snowflake ワークスペース実機クエリ実行とメタデータ突合結果](../images/07_step_09_snowflake_stage_files.png)

---

### 実証 2：SQL によるステージ内テキストファイル原本の直接照会（Stage Query）

- **【課題】**：台帳（ファイル名やサイズ）だけでなく、ステージ内の**ファイル本文の実データ**を SQL で直接読み込めるか？
- **【標準構文】**：プレーンテキスト形式を定義し、ステージパスに対して直接クエリを発行します：

```sql
USE DATABASE BOX_INTEGRATION_DB;
USE SCHEMA BOX_LANDING_DATA;

-- 1. 単一列テキスト読み込みファイルフォーマットの作成
CREATE OR REPLACE FILE FORMAT BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT 
    TYPE = 'CSV' 
    FIELD_DELIMITER = NONE 
    RECORD_DELIMITER = '\n';

-- 2. ステージ上の 03_コンプライアンス遵守チェックリスト_2026.txt の本文を直接抽出
SELECT $1 AS FILE_CONTENT 
FROM '@BOX_INTEGRATION_DB.BOX_LANDING_DATA.BOX_RAW_STAGE/compliance/' 
(FILE_FORMAT => 'BOX_INTEGRATION_DB.BOX_LANDING_DATA.TXT_FORMAT', PATTERN => '.*03.*txt');
```

- **【実機コンソール実行結果と画面キャプチャ】**：
実行時間はわずか **145ms**。対象ファイルの全 **20 行の本文テキスト実データ**（規程タイトル、各条文チェック項目）が直接取得されました：

![Snowflake ステージファイル本文直接クエリ実行結果](../images/07_step_10_stage_file_content_query.png)

---

### 実証 3：PDF および Word から分割抽出されたテキストチャンクの照会

- **【課題】**：バイナリ形式である PDF や Word ドキュメントについて、段落ごとのテキスト実データをどう取得するか？
- **【標準構文】**：テキストチャンクテーブル `BOX_DOC_CHUNKS` をクエリします：

```sql
SELECT 
    FILE_NAME,
    CHUNK_INDEX,
    CHUNK_TEXT
FROM BOX_INTEGRATION_DB.CORTEX.BOX_DOC_CHUNKS
ORDER BY FILE_ID, CHUNK_INDEX;
```

- **【実機コンソール実行結果と画面キャプチャ】**：
実行時間 **143ms**。PDF のセキュリティパスワード規程や Word のクラウド移行専用線アーキテクチャ設計本文が正確に分割・取得されました：

![Snowflake Cortex ドキュメントチャンク本文クエリ実行結果](../images/07_step_11_doc_chunks_content_query.png)

---

### 実証 4：ブラウザ安全プレビュー・ダウンロード時限署名 URL の生成 (Scoped URL)

- **【課題】**：エンドユーザーが原本 PDF や Word をダウンロードまたはブラウザで閲覧するための安全な URL はどう払い出すか？
- **【標準構文】**：Snowflake の `BUILD_SCOPED_FILE_URL` 関数を使用します：

```sql
SELECT 
    RELATIVE_PATH,
    SIZE,
    -- 時限署名付き安全ダウンロード / プレビュー URL を生成
    BUILD_SCOPED_FILE_URL(@BOX_RAW_STAGE, RELATIVE_PATH) AS DIRECT_DOWNLOAD_URL
FROM DIRECTORY(@BOX_RAW_STAGE);
```

返却された URL をクリックすることで、外部ストレージのクレデンシャルを露出させることなく、ブラウザ内蔵 PDF ビューアーで原本を直接安全にプレビューできます。

---

## 八、実務での落とし穴とトラブルシューティング（重点注意点と課金防護）

実際の構築・運用で頻出する 4 つの落とし穴と、検証済みの解決策を提示します：

### 落とし穴 1：マルチバイト文字を含むステージパスの構文エラー（`unexpected 'コン'`）

> [!WARNING] **【事象とエラーメッセージ】**  
> ワークシートで以下のようにシングルクォートなしで実行した場合：
> ```sql
> SELECT $1 FROM @BOX_RAW_STAGE/compliance/03_コンプライアンス遵守チェックリスト_2026.txt;
> ```
> コンパイルエラーが発生します：`SQL compilation error: syntax error line 22 at position 34 unexpected 'コン'.`

- **根本原因**：Snowflake の SQL パーサーは、クォートされていないステージパスを ASCII 識別子として解釈するため、日本語文字を不正なトークンとして処理します。
- **解決策**：
  1. ステージパス全体をシングルクォートで囲む：`FROM '@BOX_RAW_STAGE/compliance/03_...'`；
  2. 親ディレクトリを指定し、`PATTERN` 正規表現で指定する：`FROM '@BOX_RAW_STAGE/compliance/' (PATTERN => '.*03.*txt')`。

---

### 落とし穴 2：トライアルアカウントにおける `AI_PARSE_DOCUMENT` の実行制限

> [!WARNING] **【事象とエラーメッセージ】**  
> ドキュメント解析関数を実行した際：
> ```sql
> SELECT SNOWFLAKE.CORTEX.PARSE_DOCUMENT('@BOX_RAW_STAGE', '01_安全規程.pdf', {'mode': 'LAYOUT'});
> ```
> エラーが発生します：`AI function _AI_PARSE_DOCUMENT is not available for trial accounts.`

- **根本原因**：GPU 算力を大量に消費する OCR/レイアウト解析は、**30 日間無料トライアル環境では不正利用防止のため一律で制限**されています。
- **解決策**：
  - **本番環境**：正式課金組織へ移行することで利用可能となります；
  - **検証・学習環境**：本章の実証で行った通り、**ステージのテキスト直接クエリ（`TXT_FORMAT`）** や **`BOX_DOC_CHUNKS` テーブル** を活用することで、課金を発生させずに完全に同期と検索の検証が可能です。

---

### 落とし穴 3：秘密鍵生成時の 2 要素認証（2FA）によるブロック

> [!WARNING] **【事象とエラーメッセージ】**  
> Box Developer Console で鍵ペア生成をクリックした際、`2-Step Verification Required` の警告ポップアップが表示されて中断する。

- **根本原因**：Enterprise 権限を持つ秘密鍵の生成には 2 要素認証が必須化されています。
- **解決策**：Box アカウントのセキュリティ設定から認証アプリまたは SMS を連携した後に再度生成を実行してください。

---

### 落とし穴 4：`CORTEX SEARCH SERVICE` の `TARGET_LAG` による 400 ドル枠の枯渇！

> [!CAUTION] **【重大事故事例：400ドルクレジットの全焼】**  
> トライアル開始後 1 週間ほどで突然以下の画面が表示され、すべてのウェアハウスが強制停止されるトラブルが発生します：  
> `Your free trial has ended and all of your virtual warehouses have been suspended.`

![Snowflake トライアルアカウントの算力制限・遮断の実機画面](../images/07_step_11_snowflake_trial_expired.png)

- **根本原因**：
  Cortex Search Service を作成する際、以下の設定を行っていたことが原因です：
  ```sql
  CREATE OR REPLACE CORTEX SEARCH SERVICE BOX_ENTERPRISE_SEARCH_SERVICE
      ON CHUNK_TEXT
      ATTRIBUTES USER_EMAILS, FILE_NAME, FOLDER_ID
      WAREHOUSE = OPENFLOW_INGEST_WH
      TARGET_LAG = '1 hour'   -- ⚠️ 元凶：1時間ごとのバックグラウンド自動同期！
  ```
  `TARGET_LAG = '1 hour'` を設定すると、前台で誰も操作していなくても **1 時間ごとにサーバーレスエンジンが自動起動し、ベクトル化とインデックス再構築を実行** します。7 日間（168 回）バックグラウンドで処理が回り続け、400 ドル分のクレジット（約 130〜150 Credits）が一気に枯渇します！

- **本番および検証における鉄則**：
  1. **検証完了後は即座にバックグラウンドサービスを削除する**：
     ```sql
     -- 検証終了後、即座に検索サービスを破棄（テーブルは保持、バックグラウンド課金のみ停止）
     DROP CORTEX SEARCH SERVICE IF EXISTS BOX_INTEGRATION_DB.CORTEX.BOX_ENTERPRISE_SEARCH_SERVICE;
     ```
  2. **すべてのウェアハウスに 60 秒の自動サスペンドを設定する**：
     ```sql
     ALTER WAREHOUSE OPENFLOW_INGEST_WH SET AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
     ```
  3. **トライアル枠が尽きた場合の対処**：
     クレジットカードを入力する必要はありません。学習用途であれば別のメールアドレスで新しい 30 日間トライアルを作成すれば、即座に新しい 400 ドル枠が利用可能になります。

---

## 本章のまとめ

本章では、**『尚硅谷技術テキスト規範』** に準拠して非構造化ドキュメント同期の実践を完結させました：
1. **純粋技術フォーカス**：特定の業務ロジックを排除し、「クラウドから DWH への安全なファイル同期・保管・検索」というコア技術を実証しました；
2. **全パラメータの透明性**：`CREATE USER (TYPE = SERVICE)`、`CREATE WAREHOUSE`、`CREATE STAGE (DIRECTORY = TRUE)` およびテーブル全カラムの技術的背景を 1 行ごとに完全解説しました；
3. **明確な階層分離**：
   - **Stage** による物理原本バイナリの保護；
   - **メタデータ台帳** による SHA-256 ハッシュ値を用いた 100% のデータ整合性突合；
   - **チャンク表とステージ直読** による高効率な SQL 本文クエリ。
4. **実機エビデンスによる AI 幻覚の排除**：実機環境（`aakjsrd-oq04293`）のキャプチャ、540ms/145ms/143ms の精密なレスポンスタイム、実機制限の回避策を提示し、実務で即座に役立つ知見を提供しました。
