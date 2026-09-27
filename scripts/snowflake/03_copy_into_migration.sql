-- ==============================================================================
-- 脚本名称: 03_copy_into_migration.sql
-- 业务场景: 三井证券 批量执行 CUST_TRADE_DETAIL 的 COPY INTO 加载
-- 执行角色: MITSUI_ENGINEER
-- ==============================================================================

USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 1. 查看暂存区文件
LIST @MITSUI_STAGE;

-- 2. 格式校验 (Dry-Run)
COPY INTO CUST_TRADE_DETAIL
FROM @MITSUI_STAGE
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
VALIDATION_MODE = 'RETURN_ERRORS';

-- 3. 正式批量加载并做字段映射与转换
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
        t.$1::NUMBER(15, 0),                       -- TRADE_QTY
        t.$2::NUMBER(18, 3),                       -- AMOUNT_JPY
        t.$3::NUMBER(18, 3),                       -- AMOUNT_FCY
        t.$4::VARCHAR(3),                          -- CCY_CODE
        t.$5::NUMBER(9, 6),                        -- EXCHANGE_RATE
        t.$6::VARCHAR(100),                        -- REMARKS
        t.$7::VARCHAR(10),                         -- CUST_ID
        t.$8::VARCHAR(2),                          -- TRADE_TYPE_CD
        t.$9::VARCHAR(4),                          -- BRANCH_CD
        TO_VARCHAR(TO_DATE(t.$10), 'YYYYMMDD'),    -- TRADE_DATE (YYYYMMDD)
        TO_VARCHAR(TO_DATE(t.$11), 'YYYYMM'),      -- SETTLE_MONTH (YYYYMM)
        TO_TIMESTAMP_NTZ(t.$12),                   -- REG_DATETIME
        TO_TIMESTAMP_NTZ(t.$13)                    -- UPD_DATETIME
    FROM @MITSUI_STAGE t
)
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
ON_ERROR = 'ABORT_STATEMENT'
PURGE = FALSE;

-- 4. 统计结果
SELECT COUNT(*) AS LOADED_ROWS FROM CUST_TRADE_DETAIL;
