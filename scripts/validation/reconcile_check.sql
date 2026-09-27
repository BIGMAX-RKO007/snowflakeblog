-- ==============================================================================
-- 脚本名称: reconcile_check.sql
-- 业务场景: 三井证券 跨系统(Oracle vs Snowflake) CUST_TRADE_DETAIL 数据突合与质量审计
-- 执行角色: MITSUI_ANALYST
-- ==============================================================================

USE ROLE MITSUI_ANALYST;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 1. 总行数对比
SELECT 'SNOWFLAKE' AS SOURCE, COUNT(*) AS TOTAL_COUNT 
FROM CUST_TRADE_DETAIL;

-- 2. 金融关键金额与数量指标对比 (日元金额、外币金额、交易股数)
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;

-- 3. 按货币与交易区分聚合突合
SELECT 
    NVL(CCY_CODE, 'JPY') AS CURRENCY,
    TRADE_TYPE_CD,
    COUNT(*) AS TRADE_COUNT,
    SUM(TRADE_QTY) AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3) AS TOTAL_JPY
FROM CUST_TRADE_DETAIL
GROUP BY NVL(CCY_CODE, 'JPY'), TRADE_TYPE_CD
ORDER BY CURRENCY, TRADE_TYPE_CD;

-- 4. 全局哈希数据指纹校验
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
