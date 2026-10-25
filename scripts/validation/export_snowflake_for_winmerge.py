"""
export_snowflake_for_winmerge.py - Export Snowflake tables to CSV for WinMerge visual comparison
"""
import sys
import csv
import shutil
import snowflake.connector

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def main():
    print("[*] Preparing Oracle and Snowflake CSV files for WinMerge comparison...")

    # Copy Oracle baselines
    shutil.copyfile("data/exports/cust_master.csv", "data/exports/oracle_cust_master.csv")
    shutil.copyfile("data/exports/cust_trade_detail.csv", "data/exports/oracle_cust_trade_detail.csv")
    print("[+] Prepared Oracle baselines in data/exports/")

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

    # 1. Export Snowflake CUST_MASTER
    cs.execute("""
    SELECT 
        CUST_ID,
        CUST_NAME_KANJI,
        NVL(CUST_NAME_KANA, ''),
        CUST_RANK_CD,
        BRANCH_CD,
        NVL(STATUS_CD, ''),
        TO_VARCHAR(OPEN_DATE, 'YYYY-MM-DD'),
        TO_VARCHAR(REG_DATETIME, 'YYYY-MM-DD HH24:MI:SS')
    FROM CUST_MASTER
    ORDER BY CUST_ID;
    """)
    master_rows = cs.fetchall()
    master_header = [
        "CUST_ID", "CUST_NAME_KANJI", "CUST_NAME_KANA", "CUST_RANK_CD",
        "BRANCH_CD", "STATUS_CD", "OPEN_DATE", "REG_DATETIME"
    ]
    with open("data/exports/snowflake_cust_master.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(master_header)
        for r in master_rows:
            writer.writerow(list(r))
    print(f"[+] Exported Snowflake CUST_MASTER: {len(master_rows)} rows")

    # 2. Export Snowflake CUST_TRADE_DETAIL
    cs.execute("""
    SELECT 
        TRADE_QTY,
        AMOUNT_JPY::VARCHAR,
        NVL(AMOUNT_FCY::VARCHAR, ''),
        NVL(CCY_CODE, ''),
        NVL(EXCHANGE_RATE::VARCHAR, ''),
        NVL(REMARKS, ''),
        CUST_ID,
        TRADE_TYPE_CD,
        BRANCH_CD,
        TO_VARCHAR(TO_DATE(TRADE_DATE, 'YYYYMMDD'), 'YYYY-MM-DD'),
        CASE WHEN SETTLE_MONTH IS NOT NULL THEN TO_VARCHAR(TO_DATE(SETTLE_MONTH, 'YYYYMM'), 'YYYY-MM-01') ELSE '' END,
        TO_VARCHAR(REG_DATETIME, 'YYYY-MM-DD HH24:MI:SS'),
        CASE WHEN UPD_DATETIME IS NOT NULL THEN TO_VARCHAR(UPD_DATETIME, 'YYYY-MM-DD HH24:MI:SS') ELSE '' END
    FROM CUST_TRADE_DETAIL
    ORDER BY CUST_ID, TRADE_DATE, TRADE_TYPE_CD;
    """)
    trade_rows = cs.fetchall()
    trade_header = [
        "TRADE_QTY", "AMOUNT_JPY", "AMOUNT_FCY", "CCY_CODE", "EXCHANGE_RATE",
        "REMARKS", "CUST_ID", "TRADE_TYPE_CD", "BRANCH_CD", "TRADE_DATE",
        "SETTLE_MONTH", "REG_DATETIME", "UPD_DATETIME"
    ]
    with open("data/exports/snowflake_cust_trade_detail.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(trade_header)
        for r in trade_rows:
            writer.writerow(list(r))
    print(f"[+] Exported Snowflake CUST_TRADE_DETAIL: {len(trade_rows)} rows")

    cs.close()
    ctx.close()
    print("[+] All CSV files successfully generated for WinMerge!")

if __name__ == '__main__':
    main()
