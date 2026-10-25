-- ==============================================================================
-- 脚本名称: 04_data_migration_master.sql
-- 业务场景: 银行证券 Oracle 11g ➔ Snowflake 生产级数据迁移与跨系统数据突合实战
-- 运行环境: Snowflake Snowsight / SnowSQL
-- 包含阶段: 
--   1. 前置准备与权限确认 (确保 MITSUI_WH、目标表与 MITSUI_ANALYST 数据库权限就绪)
--   2. 数据工程师 (MITSUI_ENGINEER):
--      - 暂存区文件元数据核查 (LIST @MITSUI_STAGE)
--      - 无表预检：直接在 Stage 上执行 SELECT 查询与字段转换试跑
--      - 批量加载 CUST_MASTER (客户维度主表)
--      - 批量加载 CUST_TRADE_DETAIL (交易事实明细表，处理日期/时间戳转换)
--      - 任务运行审计追踪 (COPY_HISTORY)
--   3. 业务分析师 (MITSUI_ANALYST):
--      - 四重金融级数据突合审计 (行数对账、资金总计对账、币种分布核对、全局哈希指纹校验)
-- ==============================================================================

-- ==============================================================================
-- 阶段零：基盘基础设施与 RBAC 权限完善 (由 SYSADMIN / MITSUI_ADMIN 确认)
-- ==============================================================================

USE ROLE SYSADMIN;

-- 确认虚拟计算仓库存在并向业务角色下发 USAGE 权限
CREATE WAREHOUSE IF NOT EXISTS MITSUI_WH
    WITH 
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = '三井证券生产与迁移专用虚拟计算仓库';

GRANT USAGE, OPERATE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ADMIN;
GRANT USAGE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ENGINEER;
GRANT USAGE ON WAREHOUSE MITSUI_WH TO ROLE MITSUI_ANALYST;

-- 关键避坑：确保 MITSUI_ANALYST 拥有底层数据库的 USAGE 权限
GRANT USAGE ON DATABASE MITSUI_SEC_DB TO ROLE MITSUI_ANALYST;
GRANT USAGE ON SCHEMA MITSUI_SEC_DB.RAW_ORACLE TO ROLE MITSUI_ANALYST;


-- ==============================================================================
-- 阶段一：数据工程师身份接入与上下文设置 (MITSUI_ENGINEER)
-- ==============================================================================

-- 【Step 01: 切换工程师角色与工作环境】
-- 目的・理由: 遵循最小特权原则，使用数据工程师专属角色 MITSUI_ENGINEER，并指定虚拟计算仓库与目标 Schema。
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 确保 CUST_MASTER 目标表存在（如已在第 03 章创建则跳过）
CREATE TABLE IF NOT EXISTS CUST_MASTER (
    CUST_ID            VARCHAR(10)       NOT NULL COMMENT '顧客ID (CHAR(10)规范化)',
    CUST_NAME_KANJI    VARCHAR(50)       NOT NULL COMMENT '顧客氏名 (漢字全角)',
    CUST_NAME_KANA     VARCHAR(50)       COMMENT '顧客氏名 (カナ)',
    CUST_RANK_CD       VARCHAR(2)        DEFAULT 'C ' NOT NULL COMMENT '顧客ランク (A /B /C 等)',
    BRANCH_CD          VARCHAR(4)        NOT NULL COMMENT '支店コード',
    STATUS_CD          VARCHAR(2)        COMMENT '口座状態 (01:有効, 02:休眠, NULL:未設定)',
    OPEN_DATE          DATE              NOT NULL COMMENT '口座開設日',
    REG_DATETIME       TIMESTAMP_NTZ     NOT NULL COMMENT '登録日時',
    MIGRATED_AT        TIMESTAMP_LTZ     DEFAULT CURRENT_TIMESTAMP() COMMENT 'Snowflake 迁移入云时间戳',
    CONSTRAINT PK_CUST_MASTER PRIMARY KEY (CUST_ID)
) COMMENT = '顧客基本台帳（Oracle 11g 迁移目标表）';

GRANT SELECT ON TABLE CUST_MASTER TO ROLE MITSUI_ANALYST;
GRANT SELECT ON TABLE CUST_TRADE_DETAIL TO ROLE MITSUI_ANALYST;


-- ==============================================================================
-- 阶段二：Stage 暂存区文件核验与轻量预检 (Dry-Run Preview)
-- ==============================================================================

-- 【Step 02: 查看暂存区文件元数据】
-- 目的・理由: 确认 Oracle 端导出的压缩数据文件已完整上传至受控内部暂存区 @MITSUI_STAGE。
LIST @MITSUI_STAGE;

-- 【Step 03: Stage 暂存区数据直接投影预览 (无表预检)】
-- 目的・理由: 
--   1. Snowflake 支持在未执行 COPY 前直接用 SELECT $1, $2 语法查询 Stage 中的压缩 CSV。
--   2. 由于带有 (SELECT ...) 转换的 COPY INTO 不支持 VALIDATION_MODE，提前在 Stage 上做轻量试跑可 100% 验证字段映射与类型转换表达式。
SELECT 
    t.$1::NUMBER(15, 0)                       AS TRADE_QTY,
    t.$2::NUMBER(18, 3)                       AS AMOUNT_JPY,
    t.$3::NUMBER(18, 3)                       AS AMOUNT_FCY,
    t.$4::VARCHAR(3)                          AS CCY_CODE,
    t.$5::NUMBER(9, 6)                        AS EXCHANGE_RATE,
    t.$6::VARCHAR(100)                        AS REMARKS,
    t.$7::VARCHAR(10)                         AS CUST_ID,
    t.$8::VARCHAR(2)                          AS TRADE_TYPE_CD,
    t.$9::VARCHAR(4)                          AS BRANCH_CD,
    TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD')    AS TRADE_DATE,
    TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM')      AS SETTLE_MONTH,
    TO_TIMESTAMP_NTZ(t.$12)                   AS REG_DATETIME,
    TO_TIMESTAMP_NTZ(t.$13)                   AS UPD_DATETIME
FROM @MITSUI_STAGE/cust_trade_detail.csv.gz (FILE_FORMAT => 'CSV_ORACLE_IMPORT_FF') t
LIMIT 5;


-- ==============================================================================
-- 阶段三：执行生产级 COPY INTO 批量数据导入
-- ==============================================================================

-- 【Step 04: 批量加载 CUST_MASTER (客户维度主表)】
-- 目的・理由: 
--   1. 精确指定 @MITSUI_STAGE/cust_master.csv.gz，严格定向加载，杜绝多文件混杂污染。
--   2. ON_ERROR = 'ABORT_STATEMENT' 确保金融数据一致性，遇任何脏数据立即全单回退。
--   3. 未显式指定的 MIGRATED_AT 列将自动采用 DEFAULT CURRENT_TIMESTAMP() 填入入云时间戳。
COPY INTO CUST_MASTER (
    CUST_ID,
    CUST_NAME_KANJI,
    CUST_NAME_KANA,
    CUST_RANK_CD,
    BRANCH_CD,
    STATUS_CD,
    OPEN_DATE,
    REG_DATETIME
)
FROM (
    SELECT 
        t.$1,
        t.$2,
        t.$3,
        t.$4,
        t.$5,
        t.$6,
        TO_DATE(t.$7),
        TO_TIMESTAMP_NTZ(t.$8)
    FROM @MITSUI_STAGE/cust_master.csv.gz t
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;

-- 验证主表装载行数（应为 13 行）
SELECT COUNT(*) AS MASTER_LOADED_ROWS FROM CUST_MASTER;

-- 【Step 05: 批量加载 CUST_TRADE_DETAIL (核心交易事实明细表)】
-- 目的・理由:
--   1. 执行金融字段类型显式强转：日期转 YYYYMMDD、结算月转 YYYYMM、金额与汇率精确匹配。
--   2. 精确指定 @MITSUI_STAGE/cust_trade_detail.csv.gz，实现安全隔离装载。
COPY INTO CUST_TRADE_DETAIL (
    TRADE_QTY,
    AMOUNT_JPY,
    AMOUNT_FCY,
    CCY_CODE,
    EXCHANGE_RATE,
    REMARKS,
    CUST_ID,
    TRADE_TYPE_CD,
    BRANCH_CD,
    TRADE_DATE,
    SETTLE_MONTH,
    REG_DATETIME,
    UPD_DATETIME
)
FROM (
    SELECT 
        t.$1::NUMBER(15, 0),                       -- TRADE_QTY: 数量
        t.$2::NUMBER(18, 3),                       -- AMOUNT_JPY: 日元金额
        t.$3::NUMBER(18, 3),                       -- AMOUNT_FCY: 外币金额
        t.$4::VARCHAR(3),                          -- CCY_CODE: 币种代码
        t.$5::NUMBER(9, 6),                        -- EXCHANGE_RATE: 汇率
        t.$6::VARCHAR(100),                        -- REMARKS: 摘要（支持百字日文全角）
        t.$7::VARCHAR(10),                         -- CUST_ID: 客户编号
        t.$8::VARCHAR(2),                          -- TRADE_TYPE_CD: 交易类型
        t.$9::VARCHAR(4),                          -- BRANCH_CD: 营业网点
        TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD'),    -- TRADE_DATE: 转换为 YYYYMMDD
        TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM'),      -- SETTLE_MONTH: 转换为 YYYYMM
        TO_TIMESTAMP_NTZ(t.$12),                   -- REG_DATETIME: 注册时间戳
        TO_TIMESTAMP_NTZ(t.$13)                    -- UPD_DATETIME: 更新时间戳
    FROM @MITSUI_STAGE/cust_trade_detail.csv.gz t
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;

-- 验证明细表装载行数（应为 11 行）
SELECT COUNT(*) AS TRADE_LOADED_ROWS FROM CUST_TRADE_DETAIL;


-- ==============================================================================
-- 阶段四：数据入云审计与加载历史追踪 (Audit & Governance)
-- ==============================================================================

-- 【Step 06: 查询最近 24 小时内的加载历史与吞吐指标】
-- 目的・理由: 检查文件装载状态（STATUS = LOADED）、解析行数（ROW_PARSED）、装载行数（ROW_COUNT）以及零报错（ERROR_COUNT = 0）。
SELECT 
    TABLE_NAME,
    FILE_NAME,
    STATUS,
    ROW_COUNT,
    ROW_PARSED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'CUST_TRADE_DETAIL',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
))
UNION ALL
SELECT 
    TABLE_NAME,
    FILE_NAME,
    STATUS,
    ROW_COUNT,
    ROW_PARSED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'CUST_MASTER',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
));


-- ==============================================================================
-- 阶段五：切换业务分析师角色，执行跨系统金融突合与数据审计 (MITSUI_ANALYST)
-- ==============================================================================

-- 【Step 07: 切换分析师角色】
-- 目的・理由: 切换至 MITSUI_ANALYST，验证数据分析师账号对 RAW_ORACLE 双表仅拥有只读（SELECT）权限，符合职责分离原则。
USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 【Step 08: 双表总行数对账 (Row Count Reconciliation)】
-- 预期结果: CUST_MASTER = 13, CUST_TRADE_DETAIL = 11
SELECT 
    'CUST_MASTER' AS TABLE_NAME,
    COUNT(*)      AS RECORD_COUNT
FROM CUST_MASTER
UNION ALL
SELECT 
    'CUST_TRADE_DETAIL' AS TABLE_NAME,
    COUNT(*)            AS RECORD_COUNT
FROM CUST_TRADE_DETAIL;

-- 【Step 09: 核心金融金额与交易总量突合 (Financial Metrics Reconciliation)】
-- 目的・理由:
--   - 确保从 Oracle 到 Snowflake 的传输过程中，没有发生任何浮点数精度截断或舍入误差。
--   - 必须精确比对总数量、总日元金额（含全 9 极限值）、总外币金额、最早与最晚约定日。
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_TRADE_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;

-- 【Step 10: 多币种分布交叉审计与全局哈希指纹校验】
-- 目的・理由:
--   1. 按币种分组核算笔数与金额，确保外币资产分类无漂移。
--   2. 通过 HASH_AGG 与 HASH 计算全局数据指纹，与 Oracle 端提取的哈希摘要严密对账。
-- 10.1 币种分布与交易类型交叉突合
SELECT 
    NVL(CCY_CODE, 'JPY')      AS CURRENCY,
    TRADE_TYPE_CD,
    COUNT(*)                  AS TRADE_COUNT,
    SUM(TRADE_QTY)            AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3) AS TOTAL_JPY
FROM CUST_TRADE_DETAIL
GROUP BY NVL(CCY_CODE, 'JPY'), TRADE_TYPE_CD
ORDER BY CURRENCY, TRADE_TYPE_CD;

-- 10.2 全局数据指纹（哈希对账）
SELECT 
    HASH_AGG(
        HASH(
            CUST_ID,
            TRADE_DATE,
            TRADE_TYPE_CD,
            BRANCH_CD,
            TRADE_QTY,
            AMOUNT_JPY,
            AMOUNT_FCY,
            CCY_CODE,
            EXCHANGE_RATE,
            REMARKS
        )
    ) AS GLOBAL_TABLE_HASH
FROM CUST_TRADE_DETAIL;
