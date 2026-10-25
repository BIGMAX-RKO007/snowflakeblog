"""
05_snowflake_reconcile_verify.py - Execute 05_reconciliation_master.sql against Snowflake and verify results
"""
import sys
import snowflake.connector

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    ctx = snowflake.connector.connect(
        account='prqilyp-he58274',
        user='MITSUI_ANALYST_USER',
        password='MitsuiSecStrongPass2026!',
        warehouse='MITSUI_WH',
        database='MITSUI_SEC_DB',
        schema='RAW_ORACLE',
        role='MITSUI_ANALYST'
    )
    cs = ctx.cursor()

    print("=================================================================")
    print(" [Snowflake] 実行中：第05章 新旧データ突合検証 (MITSUI_ANALYST) ")
    print("=================================================================\n")

    # Tier 1
    print("=== [Tier 1: 件数突合 (Row Count)] ===")
    cs.execute("""
        SELECT 'CUST_MASTER' AS TARGET_TABLE, COUNT(*) AS TOTAL_ROWS FROM CUST_MASTER
        UNION ALL
        SELECT 'CUST_TRADE_DETAIL' AS TARGET_TABLE, COUNT(*) AS TOTAL_ROWS FROM CUST_TRADE_DETAIL;
    """)
    for row in cs.fetchall():
        print(f"TABLE: {row[0]:<20} ROWS: {row[1]}")

    # Tier 2
    print("\n=== [Tier 2: 重要金融メトリクス集計 (Financial Aggregations)] ===")
    cs.execute("""
        SELECT 
            COUNT(*)                                       AS TOTAL_TRADES,
            SUM(TRADE_QTY)                                 AS TOTAL_QTY,
            ROUND(SUM(AMOUNT_JPY), 3)                      AS TOTAL_AMOUNT_JPY,
            ROUND(SUM(NVL(AMOUNT_FCY, 0)), 3)              AS TOTAL_AMOUNT_FCY,
            MIN(TRADE_DATE)                                AS EARLIEST_TRADE_DATE,
            MAX(TRADE_DATE)                                AS LATEST_TRADE_DATE
        FROM CUST_TRADE_DETAIL;
    """)
    r = cs.fetchone()
    print(f"TOTAL_TRADES:     {r[0]}")
    print(f"TOTAL_QTY:        {r[1]:,}")
    print(f"TOTAL_AMOUNT_JPY: {r[2]:,}")
    print(f"TOTAL_AMOUNT_FCY: {r[3]:,}")
    print(f"EARLIEST_DATE:    {r[4]}")
    print(f"LATEST_DATE:      {r[5]}")

    # Tier 3.1
    print("\n=== [Tier 3.1: INNER JOIN 外部キー突合 (期待値: 11件)] ===")
    cs.execute("""
        SELECT 
            t.CUST_ID,
            m.CUST_NAME_KANJI,
            m.BRANCH_CD,
            t.TRADE_DATE,
            t.TRADE_TYPE_CD,
            t.TRADE_QTY,
            t.AMOUNT_JPY,
            t.CCY_CODE
        FROM CUST_TRADE_DETAIL t
        INNER JOIN CUST_MASTER m 
            ON t.CUST_ID = m.CUST_ID
        ORDER BY t.CUST_ID, t.TRADE_DATE, t.TRADE_TYPE_CD;
    """)
    rows = cs.fetchall()
    print(f"INNER JOIN MATCHED ROWS: {len(rows)}")
    for row in rows:
        ccy = row[7] if row[7] else 'JPY'
        print(f"{row[0]:<12} {row[1]:<12} {row[2]:<6} {row[3]:<10} {row[4]:<4} QTY:{row[5]:<18} JPY:{row[6]:<22} {ccy}")

    # Tier 3.2
    print("\n=== [Tier 3.2: LEFT JOIN 未取引顧客検知 (期待値: 2件)] ===")
    cs.execute("""
        SELECT 
            m.CUST_ID,
            m.CUST_NAME_KANJI,
            m.STATUS_CD,
            m.BRANCH_CD,
            COUNT(t.CUST_ID) AS TRADE_COUNT
        FROM CUST_MASTER m
        LEFT JOIN CUST_TRADE_DETAIL t 
            ON m.CUST_ID = t.CUST_ID
        GROUP BY m.CUST_ID, m.CUST_NAME_KANJI, m.STATUS_CD, m.BRANCH_CD
        HAVING COUNT(t.CUST_ID) = 0
        ORDER BY m.CUST_ID;
    """)
    for row in cs.fetchall():
        status = row[2] if row[2] else 'NULL'
        print(f"NO_TRADE_CUST: {row[0]} | NAME: {row[1]} | STATUS: {status} | BRANCH: {row[3]} | TRADES: {row[4]}")

    # Tier 3.3
    print("\n=== [Tier 3.3: 通貨別・取引区分別クロス集計] ===")
    cs.execute("""
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
    """)
    for row in cs.fetchall():
        print(f"CCY: {row[0]:<5} | TYPE: {row[1]} | COUNT: {row[2]} | QTY: {row[3]:<18} | JPY: {row[4]:<22} | FCY: {row[5]}")

    # Tier 3.4
    print("\n=== [Tier 3.4: 日本語全角文字 (CHAR/BYTE) & NULL検知] ===")
    cs.execute("""
        SELECT 
            'TRADE_DETAIL_REMARKS_EXTREME' AS CHECK_TYPE,
            CUST_ID,
            LENGTH(REMARKS)                AS CHAR_LENGTH,
            OCTET_LENGTH(REMARKS)          AS BYTE_LENGTH,
            REMARKS
        FROM CUST_TRADE_DETAIL
        WHERE CUST_ID = 'CU00004445'
        UNION ALL
        SELECT 
            'CUST_MASTER_STATUS_NULL'      AS CHECK_TYPE,
            CUST_ID,
            LENGTH(NVL(STATUS_CD, ''))     AS CHAR_LENGTH,
            OCTET_LENGTH(NVL(STATUS_CD, '')) AS BYTE_LENGTH,
            NVL(STATUS_CD, '<<NULL_DETECTED>>') AS REMARKS
        FROM CUST_MASTER
        WHERE STATUS_CD IS NULL;
    """)
    for row in cs.fetchall():
        print(f"CHECK: {row[0]:<30} | CUST: {row[1]} | CHAR_LEN: {row[2]} | BYTE_LEN: {row[3]} | VAL: {row[4]}")

    # Tier 4
    print("\n=== [Tier 4: 暗号ハッシュ指紋 (Global Table Hash)] ===")
    cs.execute("""
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
    """)
    print("GLOBAL_TABLE_HASH:", cs.fetchone()[0])

    cs.close()
    ctx.close()

if __name__ == '__main__':
    main()
