-- ==============================================================================
-- 脚本名称: 02_sysadmin_objects.sql
-- 业务场景: 三井证券 仓库/数据库/Schema/Stage/Table 渐进式授权与创建 (Step 4.5 ~ 4.15)
-- 映射对象: CUST_TRADE_DETAIL (顧客取引明細)
-- 执行角色: SYSADMIN 及 业务角色 MITSUI_ADMIN / MITSUI_ENGINEER
-- ==============================================================================

-- ==============================================================================
-- 阶段一：SYSADMIN 分配计算资源与建库特权
-- ==============================================================================
USE ROLE SYSADMIN;

-- 4.5：WAREHOUSE 作成
CREATE WAREHOUSE IF NOT EXISTS MITSUI_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = '三井证券核心数据批处理与迁移专用WH';

-- 授予计算仓库使用权给 MITSUI_ADMIN (及其下属继承的 ENGINEER 与 ANALYST)
GRANT USAGE, OPERATE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ADMIN;

-- 4.6：DB 作成権限付与
GRANT CREATE DATABASE ON ACCOUNT TO ROLE MITSUI_ADMIN;


-- ==============================================================================
-- 阶段二：切换 MITSUI_ADMIN，验证权限并建立数据库
-- ==============================================================================

-- 4.7：アカウント切り替え登録
USE ROLE MITSUI_ADMIN;
USE WAREHOUSE MITSUI_WH;

-- 4.8：DATABASE の作成
CREATE DATABASE IF NOT EXISTS MITSUI_SEC_DB
    COMMENT = '三井证券核心生产数据云端迁移仓';

USE DATABASE MITSUI_SEC_DB;

-- 4.9：スキーマ 作成権限付与 (授权给工程师角色 MITSUI_ENGINEER)
GRANT USAGE ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ENGINEER;
GRANT CREATE SCHEMA ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ENGINEER;


-- ==============================================================================
-- 阶段三：切换 MITSUI_ENGINEER，创建 Schema 与对象特权下发
-- ==============================================================================

-- 4.10：アカウント切り替え登録
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;

-- 4.11：SCHEMA 作成
CREATE SCHEMA IF NOT EXISTS RAW_ORACLE
    DATA_RETENTION_TIME_IN_DAYS = 7
    COMMENT = 'Oracle 迁移落地原始表 Schema';

USE SCHEMA RAW_ORACLE;

-- 4.12：ステージ／テーブル 作成権限付与
-- 当前角色 MITSUI_ENGINEER 即为 SCHEMA 的 OWNER，拥有创建 Stage 和 Table 的全部特权
-- 为分析师角色授予只读权（最小权限原则）
GRANT USAGE ON SCHEMA MITSUI_SEC_DB.RAW_ORACLE TO ROLE MITSUI_ANALYST;

-- 4.13：アカウント切り替え登録 (确认当前上下文)
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 4.14：ステージ作成 (定义文件格式与 Stage)
CREATE OR REPLACE FILE FORMAT CSV_ORACLE_IMPORT_FF
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    RECORD_DELIMITER = '\n'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'
    ENCODING = 'UTF8';

CREATE OR REPLACE STAGE MITSUI_STAGE
    FILE_FORMAT = CSV_ORACLE_IMPORT_FF
    COMMENT = '接收来自 Oracle 导出的中间受控暂存区';

-- 4.15：テーブル作成 (严格对应 Excel CUST_TRADE_DETAIL 转换规范)
CREATE OR REPLACE TABLE CUST_TRADE_DETAIL (
    -- ① 取引数量：Number(15) -> NUMBER(15, 0)
    TRADE_QTY          NUMBER(15, 0)     DEFAULT 0 NOT NULL COMMENT '取引数量',

    -- ② 約定金額・円貨：Number(18,3) -> NUMBER(18, 3)
    AMOUNT_JPY         NUMBER(18, 3)     DEFAULT 0 NOT NULL COMMENT '約定金額・円貨',

    -- ③ 約定金額・外貨 ＋ 通貨区分：Number(18,3) + VARCHAR(3)
    AMOUNT_FCY         NUMBER(18, 3)     DEFAULT 0 COMMENT '約定金額・外貨',
    CCY_CODE           VARCHAR(3)        COMMENT '通貨区分 (USD/EUR等)',

    -- ④ 為替レート：Number(9,6) -> NUMBER(9, 6)
    EXCHANGE_RATE      NUMBER(9, 6)      COMMENT '為替レート',

    -- ⑤ 摘要・備考：VARCHAR2(100 CHAR) -> VARCHAR(100)
    REMARKS            VARCHAR(100)      DEFAULT ' ' COMMENT '摘要・備考',

    -- ⑥ 顧客ID：VARCHAR2(10 CHAR) -> VARCHAR(10)
    CUST_ID            VARCHAR(10)       NOT NULL COMMENT '顧客ID',

    -- ⑦ 取引区分・支店コード
    TRADE_TYPE_CD      VARCHAR(2)        NOT NULL COMMENT '取引区分 (01:買付, 02:売付)',
    BRANCH_CD          VARCHAR(4)        NOT NULL COMMENT '支店コード',

    -- ⑧ 日付情報変換 (DATE -> VARCHAR(8) YYYYMMDD / VARCHAR(6) YYYYMM)
    TRADE_DATE         VARCHAR(8)        NOT NULL COMMENT '約定日 (YYYYMMDD形式)',
    SETTLE_MONTH       VARCHAR(6)        COMMENT '決済対象月 (YYYYMM形式)',

    -- ⑨ 時刻情報変換 (DATE -> TIMESTAMP_NTZ(6))
    REG_DATETIME       TIMESTAMP_NTZ(6)  DEFAULT CURRENT_TIMESTAMP() NOT NULL COMMENT '登録日時 (秒/マイクロ秒)',
    UPD_DATETIME       TIMESTAMP_NTZ(6)  COMMENT '更新日時',

    -- 迁移审计字段
    MIGRATED_AT        TIMESTAMP_LTZ(6)  DEFAULT CURRENT_TIMESTAMP() COMMENT 'Snowflake 移行取込日時',

    CONSTRAINT PK_CUST_TRADE_DETAIL PRIMARY KEY (CUST_ID, TRADE_DATE, TRADE_TYPE_CD)
)
COMMENT = '顧客取引明細（Oracle移行先 Snowflake設計）';

-- 授权分析师可以 SELECT 该表
GRANT SELECT ON TABLE CUST_TRADE_DETAIL TO ROLE MITSUI_ANALYST;

-- 验证创建结果
SHOW STAGES LIKE 'MITSUI_STAGE';
SHOW TABLES LIKE 'CUST_TRADE_DETAIL';
