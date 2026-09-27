# 第04章：データ移行実務（抽出・ステージング・COPY INTO）

Oracle の `CUST_TRADE_DETAIL` テーブルからデータを抽出し、Snowflake のセキュア内部ステージ `@MITSUI_STAGE` を経由してデータ変換を伴う並列ロードを実行します。

---

## 1. データ抽出とアップロード (SnowSQL PUT)

```bash
# SnowSQL ログイン (データエンジニアロール)
snowsql -a <your_account_identifier> \
        -u MITSUI_ENGINEER_USER \
        -r MITSUI_ENGINEER \
        -w MITSUI_WH \
        -d MITSUI_SEC_DB \
        -s RAW_ORACLE

# 暗号化アップロード実行
PUT file:///tmp/oracle_exports/cust_trade_detail_*.csv @MITSUI_STAGE 
    AUTO_COMPRESS = TRUE 
    OVERWRITE = TRUE;
```

---

## 2. データ変換を伴う COPY INTO バッチ実行

Oracle の `DATE` 型を `YYYYMMDD` および `YYYYMM` 文字列へ変換しながら格納します：

```sql
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 事前検証（Dry-Run）
COPY INTO CUST_TRADE_DETAIL
FROM @MITSUI_STAGE
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
VALIDATION_MODE = 'RETURN_ERRORS';

-- 本番データロード実行
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
```
