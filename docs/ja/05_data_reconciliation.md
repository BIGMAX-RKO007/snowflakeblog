# 第05章：移行後データ突合検証・整合性監査 (Data Reconciliation)

銀行証券のデータアナリストロール（`MITSUI_ANALYST`）により、Oracle 側と Snowflake 側の `CUST_TRADE_DETAIL` データ突合検証を実施します。

---

## 1. 件数・集計値突合クエリ

Oracle と Snowflake の双方で同一クエリを実行し、差異が **0** であることを確認します。

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

---

## 2. 全量ハッシュ値（フィンガープリント）突合

```sql
SELECT 
    HASH_AGG(
        HASH(
            CUST_ID, TRADE_DATE, TRADE_TYPE_CD, BRANCH_CD,
            TRADE_QTY, AMOUNT_JPY, AMOUNT_FCY, CCY_CODE,
            EXCHANGE_RATE, REMARKS
        )
    ) AS GLOBAL_TABLE_HASH
FROM MITSUI_SEC_DB.RAW_ORACLE.CUST_TRADE_DETAIL;
```

---

## 3. 突合完了報告書（監査サインオフ用テンプレート）

| 監査項目 | 移行元 (Oracle 11g) | 移行先 (Snowflake) | 差分 (Diff) | 判定 |
| :--- | :--- | :--- | :--- | :--- |
| **総注文件数** | 11 件 | 11 件 | 0 件 | ✅ 合格 (PASS) |
| **総約定数量** | 1,000,000,000,002,160 株 | 1,000,000,000,002,160 株 | 0 株 | ✅ 合格 (PASS) |
| **総約定金額 (円貨)** | ¥1,000,000,042,396,878.900 | ¥1,000,000,042,396,878.900 | ¥0.000 | ✅ 合格 (PASS) |
| **総約定金額 (外貨)** | 1,000,000,000,071,000.499 | 1,000,000,000,071,000.499 | 0.000 | ✅ 合格 (PASS) |
| **全角100桁文字境界** | 格納成功・文字化けなし | 格納成功・文字化けなし | 0 桁溢れ | ✅ 合格 (PASS) |
