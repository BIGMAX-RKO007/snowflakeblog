"""
export_to_csv.py - Export Oracle 11g tables to UTF-8 CSV and gzip files.
Supports both native `wslc` and `docker`.
Generates:
  - data/exports/cust_master.csv
  - data/exports/cust_master.csv.gz
  - data/exports/cust_trade_detail.csv
  - data/exports/cust_trade_detail.csv.gz
"""
import subprocess
import os
import csv
import gzip
import io

def run_sqlplus_query(sql_query, connection_str, use_wslc=True):
    wrapped_sql = (
        "SET PAGESIZE 0;\n"
        "SET FEEDBACK OFF;\n"
        "SET HEADING OFF;\n"
        "SET LINESIZE 32767;\n"
        "SET TRIMSPOOL ON;\n"
        + sql_query
        + "\nEXIT;\n"
    )
    cmd = [
        "wslc" if use_wslc else "docker",
        "exec",
        "-i",
        "mitsui_oracle_11g",
        "sqlplus",
        "-S",
        connection_str,
    ]
    proc = subprocess.run(cmd, input=wrapped_sql.encode("utf-8"), capture_output=True)
    raw = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"[!] Error executing query: {proc.stderr.decode('utf-8', errors='replace')}")
    return raw

def export_cust_master(output_dir, connection_str, use_wslc):
    print("[*] Exporting CUST_MASTER (顧客基本台帳)...")
    sql = """
    SELECT 
        CUST_ID || '|||' || 
        CUST_NAME_KANJI || '|||' || 
        NVL(CUST_NAME_KANA, '') || '|||' || 
        CUST_RANK_CD || '|||' || 
        BRANCH_CD || '|||' || 
        NVL(STATUS_CD, '') || '|||' || 
        TO_CHAR(OPEN_DATE, 'YYYY-MM-DD') || '|||' || 
        TO_CHAR(REG_DATETIME, 'YYYY-MM-DD HH24:MI:SS')
    FROM CUST_MASTER
    ORDER BY CUST_ID;
    """
    raw_output = run_sqlplus_query(sql, connection_str, use_wslc)
    rows = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) == 8:
            rows.append(parts)

    headers = [
        "CUST_ID",
        "CUST_NAME_KANJI",
        "CUST_NAME_KANA",
        "CUST_RANK_CD",
        "BRANCH_CD",
        "STATUS_CD",
        "OPEN_DATE",
        "REG_DATETIME",
    ]

    csv_path = os.path.join(output_dir, "cust_master.csv")
    gz_path = os.path.join(output_dir, "cust_master.csv.gz")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(rows)

    with open(csv_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        f_out.writelines(f_in)

    print(f"[+] CUST_MASTER exported: {len(rows)} rows -> {csv_path} and {gz_path}")
    return len(rows)

def export_cust_trade_detail(output_dir, connection_str, use_wslc):
    print("[*] Exporting CUST_TRADE_DETAIL (顧客取引明細)...")
    sql = """
    SELECT 
        NVL(TO_CHAR(TRADE_QTY), '0') || '|||' ||
        TO_CHAR(AMOUNT_JPY, 'FM999999999999990.000') || '|||' ||
        NVL(TO_CHAR(AMOUNT_FCY, 'FM999999999999990.000'), '') || '|||' ||
        NVL(CCY_CODE, '') || '|||' ||
        NVL(TO_CHAR(EXCHANGE_RATE, 'FM990.000000'), '') || '|||' ||
        NVL(REMARKS, '') || '|||' ||
        CUST_ID || '|||' ||
        TRADE_TYPE_CD || '|||' ||
        BRANCH_CD || '|||' ||
        TO_CHAR(TRADE_DATE, 'YYYY-MM-DD') || '|||' ||
        NVL(TO_CHAR(SETTLE_MONTH, 'YYYY-MM-DD'), '') || '|||' ||
        TO_CHAR(REG_DATETIME, 'YYYY-MM-DD HH24:MI:SS') || '|||' ||
        NVL(TO_CHAR(UPD_DATETIME, 'YYYY-MM-DD HH24:MI:SS'), '')
    FROM CUST_TRADE_DETAIL
    ORDER BY CUST_ID, TRADE_DATE, TRADE_TYPE_CD;
    """
    raw_output = run_sqlplus_query(sql, connection_str, use_wslc)
    rows = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) == 13:
            rows.append(parts)

    headers = [
        "TRADE_QTY",
        "AMOUNT_JPY",
        "AMOUNT_FCY",
        "CCY_CODE",
        "EXCHANGE_RATE",
        "REMARKS",
        "CUST_ID",
        "TRADE_TYPE_CD",
        "BRANCH_CD",
        "TRADE_DATE",
        "SETTLE_MONTH",
        "REG_DATETIME",
        "UPD_DATETIME",
    ]

    csv_path = os.path.join(output_dir, "cust_trade_detail.csv")
    gz_path = os.path.join(output_dir, "cust_trade_detail.csv.gz")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(rows)

    with open(csv_path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
        f_out.writelines(f_in)

    print(f"[+] CUST_TRADE_DETAIL exported: {len(rows)} rows -> {csv_path} and {gz_path}")
    return len(rows)

def main():
    use_wslc = True
    try:
        subprocess.run(["wslc", "--version"], capture_output=True, check=True)
    except Exception:
        use_wslc = False

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "exports"))
    os.makedirs(output_dir, exist_ok=True)

    conn_str = "mitsui_src/Mitsui_Sec_2026@//localhost:1521/xe"
    print(f"=== Oracle 11g Data Export Starting ({'wslc' if use_wslc else 'docker'}) ===")
    
    master_count = export_cust_master(output_dir, conn_str, use_wslc)
    detail_count = export_cust_trade_detail(output_dir, conn_str, use_wslc)

    print("\n=== Export Summary ===")
    print(f"CUST_MASTER:        {master_count} records exported")
    print(f"CUST_TRADE_DETAIL:  {detail_count} records exported")
    print(f"Destination Folder: {output_dir}")

if __name__ == "__main__":
    main()
