-- ====================================================================
-- 三井証券 / Snowflake エンタープライズ RBAC 権限設計と環境構築マスタースクリプト
-- ファイル名: 03_rbac_and_env_master.sql
-- 概要: FISC安全基準および最小特権の原則に準拠した3層ロール・権限委譲・DB/Schema/Stage/Dual Table構築
-- ====================================================================

-- --------------------------------------------------------------------
-- 【Step 01: 切换 useradmin 账户】
-- 目的・理由: 職務分掌（Separation of Duties）に基づき、ユーザーおよびロールのライフサイクル管理は
--             グローバル最高権限 ACCOUNTADMIN を使用せず、専任の USERADMIN に切り替えて実行します。
-- --------------------------------------------------------------------
USE ROLE USERADMIN;


-- --------------------------------------------------------------------
-- 【Step 02: 创建 role】
-- 目的・理由: 銀行証券データ基盤における3層業務ロール（統括管理者・エンジニア・アナリスト）を新設します。
-- --------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS MITSUI_ADMIN    COMMENT = '銀行証券プロジェクト統括管理者ロール';
CREATE ROLE IF NOT EXISTS MITSUI_ENGINEER COMMENT = '銀行証券データエンジニアロール（移行・ETL担当）';
CREATE ROLE IF NOT EXISTS MITSUI_ANALYST  COMMENT = '銀行証券データアナリストロール（照会・分析担当）';


-- --------------------------------------------------------------------
-- 【Step 03: 赋予/继承权限】
-- 目的・理由: Snowflake の階層ツリーを構築します。MITSUI_ADMIN を SYSADMIN 配下に束ねて全体ガバナンスを
--             確保し、上位ロールが下位ロールの特権を自然継承する構造を確立します。
-- --------------------------------------------------------------------
-- 統括管理者を SYSADMIN に束ねる
GRANT ROLE MITSUI_ADMIN TO ROLE SYSADMIN;

-- エンジニアは統括管理者へ権限を集約
GRANT ROLE MITSUI_ENGINEER TO ROLE MITSUI_ADMIN;

-- アナリストはエンジニアへ権限を集約
GRANT ROLE MITSUI_ANALYST TO ROLE MITSUI_ENGINEER;


-- --------------------------------------------------------------------
-- 【Step 04: 创建 user】
-- 目的・理由: 実際の運用担当者向けアカウントを作成し、初期パスワード・デフォルトロール・デフォルトWHを
--             バインドして、権限の混同や想定外のコスト発生を防止します。
-- --------------------------------------------------------------------
-- エンジニア業務アカウント
CREATE USER IF NOT EXISTS MITSUI_ENGINEER_USER
    PASSWORD = 'MitsuiSecStrongPass2026!'
    DEFAULT_ROLE = MITSUI_ENGINEER
    DEFAULT_WAREHOUSE = MITSUI_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT = '銀行証券データエンジニア業務アカウント';

-- アナリスト業務アカウント
CREATE USER IF NOT EXISTS MITSUI_ANALYST_USER
    PASSWORD = 'MitsuiSecStrongPass2026!'
    DEFAULT_ROLE = MITSUI_ANALYST
    DEFAULT_WAREHOUSE = MITSUI_WH
    MUST_CHANGE_PASSWORD = FALSE
    COMMENT = '銀行証券アナリスト分析・監査業務アカウント';


-- --------------------------------------------------------------------
-- 【Step 05: 赋予角色】
-- 目的・理由: 作成したアカウントに対して各ロールを正式に付与し、SHOW コマンドで作成状態を検証します。
-- --------------------------------------------------------------------
GRANT ROLE MITSUI_ENGINEER TO USER MITSUI_ENGINEER_USER;
GRANT ROLE MITSUI_ANALYST TO USER MITSUI_ANALYST_USER;

-- 作成されたロールとユーザーの検証
SHOW ROLES LIKE 'MITSUI_%';
SHOW USERS LIKE 'MITSUI_%';


-- --------------------------------------------------------------------
-- 【Step 06: 切换 sysadmin 账户】
-- 目的・理由: コンピュート（Warehouse）やストレージ（DB）等の物理インフラ管理を司る SYSADMIN へ切り替えます。
-- --------------------------------------------------------------------
USE ROLE SYSADMIN;


-- --------------------------------------------------------------------
-- 【Step 07: WAREHOUSE作成】
-- 目的・理由: 移行およびバッチ処理専用の仮想ウェアハウス MITSUI_WH を作成します。
--             5分（300秒）無稼働時の自動休眠（AUTO_SUSPEND）を設定し、不要な課金を徹底遮断します。
-- --------------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS MITSUI_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300           -- 5分間クエリがない場合、自動休眠（課金停止）
    AUTO_RESUME = TRUE           -- SQLリクエスト到着時に自動起動
    INITIALLY_SUSPENDED = TRUE   -- 作成時は即時課金させず停止状態でスタンバイ
    COMMENT = '銀行証券データ移行・バッチ処理専用仮想ウェアハウス';

-- 各業務ロールに対して利用権限（USAGE / OPERATE）を配分
GRANT USAGE, OPERATE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ADMIN;
GRANT USAGE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ENGINEER;
GRANT USAGE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ANALYST;

SHOW WAREHOUSES LIKE 'MITSUI_WH';


-- --------------------------------------------------------------------
-- 【Step 08: DB 作成権限付与】
-- 目的・理由: 業務プロジェクト部門の自立運用のため、SYSADMIN から MITSUI_ADMIN に対して
--             アカウント階層での CREATE DATABASE 権限を正式委任します。
-- --------------------------------------------------------------------
GRANT CREATE DATABASE ON ACCOUNT TO ROLE MITSUI_ADMIN;


-- --------------------------------------------------------------------
-- 【Step 09: アカウント切り替え登録 (MITSUI_ADMIN)】
-- 目的・理由: プロジェクト統括管理者 MITSUI_ADMIN にロールを切り替え、コンテキストを確立します。
-- --------------------------------------------------------------------
USE ROLE MITSUI_ADMIN;
USE WAREHOUSE MITSUI_WH;


-- --------------------------------------------------------------------
-- 【Step 10: DATABASEの作成】
-- 目的・理由: MITSUI_ADMIN が委譲された特権を行使し、三井証券の基幹データベース MITSUI_SEC_DB を作成します。
-- --------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS MITSUI_SEC_DB
    COMMENT = '三井証券基幹データクラウド移行データベース';

USE DATABASE MITSUI_SEC_DB;


-- --------------------------------------------------------------------
-- 【Step 11: スキーマ 作成権限付与】
-- 目的・理由: 統括管理者から実務担当エンジニア（MITSUI_ENGINEER）へ、データベース利用権と
--             スキーマ作成権（CREATE SCHEMA）を委譲します。
-- --------------------------------------------------------------------
GRANT USAGE ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ENGINEER;
GRANT CREATE SCHEMA ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ENGINEER;


-- --------------------------------------------------------------------
-- 【Step 12: アカウント切り替え登録 (MITSUI_ENGINEER)】
-- 目的・理由: データエンジニア MITSUI_ENGINEER にコンテキストを切り替えます。
-- --------------------------------------------------------------------
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;


-- --------------------------------------------------------------------
-- 【Step 13: SCHEMA作成】
-- 目的・理由: Oracle 11g からの生データ受入用スキーマ RAW_ORACLE を作成します。
--             金融要件に基づき 7 日間の Time Travel 保持期間を設定します。
-- --------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS RAW_ORACLE
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Oracle移行生データ格納用スキーマ（Time Travel: 7日）';

USE SCHEMA RAW_ORACLE;


-- --------------------------------------------------------------------
-- 【Step 14: ステージ／テーブル 作成権限付与（スキーマ利用権付与）】
-- 目的・理由: 最小特権の原則に基づき、スキーマ所有者（エンジニア）からアナリストへ
--             スキーマの利用権（USAGE）のみを付与し、不正なオブジェクト作成を遮断します。
-- --------------------------------------------------------------------
GRANT USAGE ON SCHEMA MITSUI_SEC_DB.RAW_ORACLE TO ROLE MITSUI_ANALYST;


-- --------------------------------------------------------------------
-- 【Step 15: アカウント切り替え登録（コンテキスト確認）】
-- 目的・理由: 以降のストレージオブジェクト作成に向けて、エンジニアの実行コンテキストを再確認・固定します。
-- --------------------------------------------------------------------
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;


-- --------------------------------------------------------------------
-- 【Step 16: ステージ作成】
-- 目的・理由: Oracle からの CSV 抽出データを受領するため、カンマ区切り・NULL判定（空文字変換）・UTF-8
--             対応の高精度ファイルフォーマットと受取用内部ステージ MITSUI_STAGE を作成します。
-- --------------------------------------------------------------------
CREATE OR REPLACE FILE FORMAT CSV_ORACLE_IMPORT_FF
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE             -- Oracle特有の ''(空文字) を Snowflake NULL に正規化
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
    ENCODING = 'UTF8';

CREATE OR REPLACE STAGE MITSUI_STAGE
    FILE_FORMAT = CSV_ORACLE_IMPORT_FF
    COMMENT = 'Oracle 11g 抽出データ受取用内部ステージ';

SHOW STAGES LIKE 'MITSUI_STAGE';


-- --------------------------------------------------------------------
-- 【Step 17: テーブル作成】
-- 目的・理由: 第02章の型定義に基づき、顧客基本台帳（CUST_MASTER）と顧客取引明細（CUST_TRADE_DETAIL）
--             の1:N関係テーブルを作成し、アナリストロールへ SELECT 参照権限のみを付与します。
-- --------------------------------------------------------------------
-- ① 顧客基本台帳（ディメンションテーブル）
CREATE OR REPLACE TABLE CUST_MASTER (
    CUST_ID            VARCHAR(10)       NOT NULL COMMENT '顧客ID (CHAR(10)正規化)',
    CUST_NAME_KANJI    VARCHAR(50)       NOT NULL COMMENT '顧客氏名 (漢字全角)',
    CUST_NAME_KANA     VARCHAR(50)       COMMENT '顧客氏名 (カナ)',
    CUST_RANK_CD       VARCHAR(2)        DEFAULT 'C ' NOT NULL COMMENT '顧客ランク (A /B /C 等)',
    BRANCH_CD          VARCHAR(4)        NOT NULL COMMENT '支店コード',
    STATUS_CD          VARCHAR(2)        COMMENT '口座状態 (01:有効, 02:休眠, NULL:未設定)',
    OPEN_DATE          DATE              NOT NULL COMMENT '口座開設日',
    REG_DATETIME       TIMESTAMP_NTZ(6)  DEFAULT CURRENT_TIMESTAMP() NOT NULL COMMENT '登録日時',
    MIGRATED_AT        TIMESTAMP_LTZ(6)  DEFAULT CURRENT_TIMESTAMP() COMMENT 'Snowflake 移行取込日時',
    CONSTRAINT PK_CUST_MASTER PRIMARY KEY (CUST_ID)
) COMMENT = '顧客基本台帳（Oracle 11g 移行先テーブル）';

GRANT SELECT ON TABLE CUST_MASTER TO ROLE MITSUI_ANALYST;

-- ② 顧客取引明細（ファクトテーブル）
CREATE OR REPLACE TABLE CUST_TRADE_DETAIL (
    TRADE_QTY          NUMBER(15, 0)     DEFAULT 0 NOT NULL COMMENT '取引数量',
    AMOUNT_JPY         NUMBER(18, 3)     DEFAULT 0 NOT NULL COMMENT '約定金額・円貨',
    AMOUNT_FCY         NUMBER(18, 3)     DEFAULT 0 COMMENT '約定金額・外貨',
    CCY_CODE           VARCHAR(3)        COMMENT '通貨区分 (USD/EUR等)',
    EXCHANGE_RATE      NUMBER(9, 6)      COMMENT '為替レート',
    REMARKS            VARCHAR(100)      DEFAULT ' ' COMMENT '摘要・備考 (全角半角混在安全)',
    CUST_ID            VARCHAR(10)       NOT NULL COMMENT '顧客ID',
    TRADE_TYPE_CD      VARCHAR(2)        NOT NULL COMMENT '取引区分 (01:買付, 02:売付)',
    BRANCH_CD          VARCHAR(4)        NOT NULL COMMENT '支店コード',
    TRADE_DATE         VARCHAR(8)        NOT NULL COMMENT '約定日 (YYYYMMDD形式)',
    SETTLE_MONTH       VARCHAR(6)        COMMENT '決済対象月 (YYYYMM形式)',
    REG_DATETIME       TIMESTAMP_NTZ(6)  DEFAULT CURRENT_TIMESTAMP() NOT NULL COMMENT '登録日時',
    UPD_DATETIME       TIMESTAMP_NTZ(6)  COMMENT '更新日時',
    MIGRATED_AT        TIMESTAMP_LTZ(6)  DEFAULT CURRENT_TIMESTAMP() COMMENT 'Snowflake 移行取込日時',
    CONSTRAINT PK_CUST_TRADE_DETAIL PRIMARY KEY (CUST_ID, TRADE_DATE, TRADE_TYPE_CD)
) COMMENT = '顧客取引明細（Oracle 11g 移行先テーブル）';

GRANT SELECT ON TABLE CUST_TRADE_DETAIL TO ROLE MITSUI_ANALYST;

SHOW TABLES IN SCHEMA MITSUI_SEC_DB.RAW_ORACLE;


-- --------------------------------------------------------------------
-- 【Step 18: 疎通検証 (Sanity Check - MITSUI_ENGINEER)】
-- 目的・理由: エンジニアロールにおいて、RAW_ORACLE 内での一時テーブル作成・書き込み・読み出しが
--             正常に実行できることを検証します（サンドボックスレベル健全性検証）。
-- --------------------------------------------------------------------
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

CREATE OR REPLACE TEMPORARY TABLE _SANITY_CHECK (
    CHECK_ID    INT,
    OPERATOR    VARCHAR(50),
    CHECKED_AT  TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO _SANITY_CHECK (CHECK_ID, OPERATOR) VALUES (1, CURRENT_USER());

SELECT * FROM _SANITY_CHECK;

DROP TABLE IF EXISTS _SANITY_CHECK;


-- --------------------------------------------------------------------
-- 【Step 19: 最小特権防御検証 (Least Privilege Defense - MITSUI_ANALYST)】
-- 目的・理由: アナリストロールに切り替え、SELECT は正常実行でき、かつ INSERT（不正な書込）は
--             アクセス制御機構により厳格に拒否（Access Denied）されることを実証します。
-- --------------------------------------------------------------------
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 1. SELECT は許可されているため実行可能（0行返却）
SELECT * FROM CUST_MASTER;

-- 2. INSERT 権限はないため、システムにより即座に遮断される（エラー発生が正常）
INSERT INTO CUST_MASTER (CUST_ID, CUST_NAME_KANJI, OPEN_DATE) 
VALUES ('TEST0001', '不正書込テスト', CURRENT_DATE());
-- 期待エラー: SQL compilation error: Object 'CUST_MASTER' does not exist or not authorized.
