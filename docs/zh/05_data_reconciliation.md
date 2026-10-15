# 第 05 章：迁移后两方数据差异对比与质量对账 (Data Reconciliation)

在日企金融 IT 工程中，新旧系统数据对账阶段被称为 **「新旧データ突合検証 (Reconciliation & Validation)」**。

针对银行证券 `CUST_TRADE_DETAIL`，我们由 `MITSUI_ANALYST` 角色执行四层递进式对账。

---

## 1. 第一阶梯：总行数对账 (Row Count)

### Oracle 源库：
```sql
SELECT 'ORACLE' AS SOURCE, COUNT(*) AS TOTAL_COUNT FROM CUST_TRADE_DETAIL;
```

### Snowflake 目标库：
```sql
USE ROLE MITSUI_ANALYST;
SELECT 'SNOWFLAKE' AS SOURCE, COUNT(*) AS TOTAL_COUNT FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL;
```
> **判定规则**：行数差值 $\Delta = 0$。

---

## 2. 第二阶梯：关键金融指标汇总对账 (Business Aggregations)

针对金额、数量、日期跨度进行绝对精度汇总对比：

### Oracle 端汇总：
```sql
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    TO_CHAR(MIN(TRADE_DATE), 'YYYYMMDD')           AS EARLIEST_TRADE_DATE,
    TO_CHAR(MAX(TRADE_DATE), 'YYYYMMDD')           AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
```

### Snowflake 端汇总：
```sql
USE ROLE MITSUI_ANALYST;
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
    MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL;
```
> **判定规则**：`TOTAL_AMOUNT_JPY` 与 `TOTAL_AMOUNT_FCY` 必须绝对一致，差值为 0.000。

---

## 3. 第三阶梯：全量哈希数据指纹 (Hash Aggregate)

```sql
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
FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL;
```

---

## 4. 突合验收交付件模版 (Reconciliation Sign-off)

| 审计维度 | Oracle 迁移源端 | Snowflake 目标端 | 差异值 (Diff) | 审计结论 |
| :--- | :--- | :--- | :--- | :--- |
| **总记录数** | 11 条 | 11 条 | 0 条 | ✅ 一致 (PASS) |
| **取引数量合计** | 1,000,000,000,002,160 株 | 1,000,000,000,002,160 株 | 0 株 | ✅ 一致 (PASS) |
| **日元金额合计 (JPY)** | 1,000,000,042,396,878.900 円 | 1,000,000,042,396,878.900 円 | 0.000 円 | ✅ 一致 (PASS) |
| **外币金额合计 (FCY)** | 1,000,000,000,071,000.499 | 1,000,000,000,071,000.499 | 0.000 | ✅ 一致 (PASS) |
| **全角百字边界** | 成功存储并一致 | 成功存储并一致 | 0 溢出 | ✅ 一致 (PASS) |
