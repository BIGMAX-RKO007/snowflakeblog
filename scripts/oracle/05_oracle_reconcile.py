"""
05_oracle_reconcile.py - Run Oracle benchmark queries for Chapter 05 Reconciliation
"""
import subprocess
import os
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_oracle_sql(sql_text, use_wslc=True):
    wrapped = """SET PAGESIZE 50000 LINESIZE 250 FEEDBACK OFF HEADING ON TAB OFF TRIMSPOOL ON DEFINE OFF;
COLUMN TABLE_NAME FORMAT A20
COLUMN TARGET_TABLE FORMAT A20
COLUMN CUST_ID FORMAT A12
COLUMN CUST_NAME_KANJI FORMAT A20
COLUMN CURRENCY FORMAT A10
COLUMN TRADE_TYPE_CD FORMAT A12
COLUMN STATUS_CD FORMAT A10
COLUMN CHECK_TYPE FORMAT A30
COLUMN CHAR_LENGTH FORMAT 9999
COLUMN BYTE_LENGTH FORMAT 9999
COLUMN REMARKS FORMAT A60
""" + sql_text + "\nEXIT;\n"
    cmd = ['wslc' if use_wslc else 'docker', 'exec', '-i', 'mitsui_oracle_11g', 'sqlplus', '-S', 'mitsui_src/Mitsui_Sec_2026@//localhost:1521/xe']
    proc = subprocess.run(cmd, input=wrapped.encode('utf-8'), capture_output=True)
    out = proc.stdout.decode('utf-8', errors='replace')
    return out

def main():
    use_wslc = True
    try:
        subprocess.run(['wslc', '--version'], capture_output=True, check=True)
    except Exception:
        use_wslc = False

    print("=================================================================")
    print(" [Oracle 11g] 実行中：第05章 新旧データ突合検証ベンチマーク ")
    print("=================================================================\n")

    sql_1 = """
PROMPT === [Tier 1: 件数突合 (Row Count)] ===
SELECT 'CUST_MASTER' AS TABLE_NAME, COUNT(*) AS TOTAL_COUNT FROM CUST_MASTER
UNION ALL
SELECT 'CUST_TRADE_DETAIL' AS TABLE_NAME, COUNT(*) AS TOTAL_COUNT FROM CUST_TRADE_DETAIL;
"""
    out_1 = run_oracle_sql(sql_1, use_wslc)
    print(out_1)

    sql_2 = """
PROMPT === [Tier 2: 重要金融メトリクス集計 (Financial Aggregations)] ===
SELECT 
    COUNT(*)                                       AS TOTAL_TRADES,
    SUM(TRADE_QTY)                                 AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
    TO_CHAR(MIN(TRADE_DATE), 'YYYYMMDD')           AS EARLIEST_TRADE_DATE,
    TO_CHAR(MAX(TRADE_DATE), 'YYYYMMDD')           AS LATEST_TRADE_DATE
FROM CUST_TRADE_DETAIL;
"""
    out_2 = run_oracle_sql(sql_2, use_wslc)
    print(out_2)

    sql_3 = """
PROMPT === [Tier 3.1: INNER JOIN 外部キー突合 (期待値: 11件)] ===
SELECT 
    t.CUST_ID,
    m.CUST_NAME_KANJI,
    m.BRANCH_CD,
    TO_CHAR(t.TRADE_DATE, 'YYYYMMDD') AS TRADE_DATE,
    t.TRADE_TYPE_CD,
    t.TRADE_QTY,
    t.AMOUNT_JPY,
    t.CCY_CODE
FROM CUST_TRADE_DETAIL t
INNER JOIN CUST_MASTER m ON t.CUST_ID = m.CUST_ID
ORDER BY t.CUST_ID, t.TRADE_DATE, t.TRADE_TYPE_CD;

PROMPT === [Tier 3.2: LEFT JOIN 未取引顧客検知 (期待値: 2件)] ===
SELECT 
    m.CUST_ID,
    m.CUST_NAME_KANJI,
    m.STATUS_CD,
    m.BRANCH_CD,
    COUNT(t.CUST_ID) AS TRADE_COUNT
FROM CUST_MASTER m
LEFT JOIN CUST_TRADE_DETAIL t ON m.CUST_ID = t.CUST_ID
GROUP BY m.CUST_ID, m.CUST_NAME_KANJI, m.STATUS_CD, m.BRANCH_CD
HAVING COUNT(t.CUST_ID) = 0
ORDER BY m.CUST_ID;

PROMPT === [Tier 3.3: 通貨別・取引区分別クロス集計] ===
SELECT 
    NVL(CCY_CODE, 'JPY')        AS CURRENCY,
    TRADE_TYPE_CD,
    COUNT(*)                    AS TRADE_COUNT,
    SUM(TRADE_QTY)              AS TOTAL_QTY,
    ROUND(SUM(AMOUNT_JPY), 3)   AS TOTAL_JPY,
    ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3) AS TOTAL_FCY
FROM CUST_TRADE_DETAIL
GROUP BY NVL(CCY_CODE, 'JPY'), TRADE_TYPE_CD
ORDER BY CURRENCY, TRADE_TYPE_CD;

PROMPT === [Tier 3.4: 日本語全角文字 (CHAR/BYTE) & NULL検知] ===
SELECT 
    'TRADE_DETAIL_REMARKS_EXTREME' AS CHECK_TYPE,
    CUST_ID,
    LENGTH(REMARKS)                AS CHAR_LENGTH,
    LENGTHB(REMARKS)               AS BYTE_LENGTH,
    REMARKS
FROM CUST_TRADE_DETAIL
WHERE CUST_ID = 'CU00004445'
UNION ALL
SELECT 
    'CUST_MASTER_STATUS_NULL'      AS CHECK_TYPE,
    CUST_ID,
    LENGTH(NVL(STATUS_CD, ''))     AS CHAR_LENGTH,
    LENGTHB(NVL(STATUS_CD, ''))    AS BYTE_LENGTH,
    NVL(STATUS_CD, '<<NULL_DETECTED>>') AS REMARKS
FROM CUST_MASTER
WHERE STATUS_CD IS NULL;
"""
    out_3 = run_oracle_sql(sql_3, use_wslc)
    print(out_3)

if __name__ == '__main__':
    main()
