"""
upload_to_stage.py - Secure automated upload of Oracle exported CSV/gzip datasets to Snowflake @MITSUI_STAGE.
Uses snowflake-connector-python and executes standard PUT commands with MITSUI_ENGINEER_USER.
Notice: The PUT command uploads directly to cloud storage and does NOT consume warehouse credits.
"""
import os
import snowflake.connector

def upload_files():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "exports"))
    files_to_upload = [
        os.path.join(data_dir, "cust_master.csv.gz"),
        os.path.join(data_dir, "cust_trade_detail.csv.gz"),
    ]

    for f in files_to_upload:
        if not os.path.exists(f):
            raise FileNotFoundError(f"Export file not found: {f}. Run export_to_csv.py first.")

    print(f"[*] Connecting to Snowflake as MITSUI_ENGINEER_USER...")
    conn = snowflake.connector.connect(
        user="MITSUI_ENGINEER_USER",
        password="MitsuiSecStrongPass2026!",
        account="prqilyp-he58274",
        database="MITSUI_SEC_DB",
        schema="RAW_ORACLE",
        role="MITSUI_ENGINEER",
    )
    cur = conn.cursor()

    try:
        for fpath in files_to_upload:
            normalized_path = fpath.replace("\\", "/")
            fname = os.path.basename(fpath)
            print(f"[*] Executing PUT for {fname}...")
            # Note: file URI format on Windows for Snowflake PUT: file://<path>
            put_sql = f"PUT file://{normalized_path} @MITSUI_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
            cur.execute(put_sql)
            results = cur.fetchall()
            for r in results:
                print(f"    Target: {r[0]}, Source Size: {r[2]}B, Uploaded Size: {r[3]}B, Status: {r[6]}")

        print("\n[*] Validating stage contents (LIST @MITSUI_STAGE)...")
        cur.execute("LIST @MITSUI_STAGE;")
        stage_files = cur.fetchall()
        for sf in stage_files:
            print(f"    -> {sf[0]} ({sf[1]} bytes, md5={sf[2]})")

        print("\n[+] Stage upload completed successfully!")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    upload_files()
