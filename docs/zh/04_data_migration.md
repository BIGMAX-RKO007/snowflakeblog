# 第 04 章：数据迁移实战（Oracle 导出、Stage 暂存与 COPY INTO 加载）

完成 Snowflake 基础设施与权限层级搭建后，本章进入核心迁移阶段。
针对银行证券 `CUST_TRADE_DETAIL` 表的迁移，完整演练**从本地导出分块 -> SnowSQL PUT 加密上传到 `@MITSUI_STAGE` -> 执行字段转换与批量 `COPY INTO`**。

---

## 1. Oracle 端数据导出 (Export)

将 Oracle 中的 `CUST_TRADE_DETAIL` 数据导出为 UTF-8 编码、带双引号包裹的 CSV 文件：

- 文件名建议：`cust_trade_detail_*.csv.gz`
- 字段顺序：
  1. `TRADE_QTY`
  2. `AMOUNT_JPY`
  3. `AMOUNT_FCY`
  4. `CCY_CODE`
  5. `EXCHANGE_RATE`
  6. `REMARKS`
  7. `CUST_ID`
  8. `TRADE_TYPE_CD`
  9. `BRANCH_CD`
  10. `TRADE_DATE`
  11. `SETTLE_MONTH`
  12. `REG_DATETIME`
  13. `UPD_DATETIME`

---

## 2. 上传数据至 Snowflake 内部暂存区 (PUT)

使用数据工程师账号登录 SnowSQL：

```bash
snowsql -a <your_account_identifier> \
        -u MITSUI_ENGINEER_USER \
        -r MITSUI_ENGINEER \
        -w MITSUI_WH \
        -d MITSUI_SEC_DB \
        -s RAW_ORACLE

# 执行加密上传
PUT file:///tmp/oracle_exports/cust_trade_detail_*.csv @MITSUI_STAGE 
    AUTO_COMPRESS = TRUE 
    OVERWRITE = TRUE;
```

在 Snowflake 验证上传结果：
```sql
LIST @MITSUI_STAGE;
```

---

## 3. 执行 COPY INTO 批量加载与类型转换

在 Snowflake 中执行带有表达式转换的 `COPY INTO`，将日期转换为规范的 `YYYYMMDD` / `YYYYMM` 格式：

```sql
USE ROLE MITSUI_ENGINEER;
USE WAREHOUSE MITSUI_WH;
USE DATABASE MITSUI_SEC_DB;
USE SCHEMA RAW_ORACLE;

-- 1. 试运行模式 (Dry-Run / Validation)
COPY INTO CUST_TRADE_DETAIL
FROM @MITSUI_STAGE
FILE_FORMAT = (FORMAT_NAME = 'CSV_ORACLE_IMPORT_FF')
VALIDATION_MODE = 'RETURN_ERRORS';

-- 2. 正式执行批量加载
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

---

## 4. 加载审计追踪

```sql
SELECT 
    FILE_NAME,
    STATUS,
    ROW_COUNT,
    ROW_PARSED,
    ERROR_COUNT,
    LAST_LOAD_TIME
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
    TABLE_NAME => 'CUST_TRADE_DETAIL',
    START_TIME => DATEADD(HOURS, -24, CURRENT_TIMESTAMP())
));
```
