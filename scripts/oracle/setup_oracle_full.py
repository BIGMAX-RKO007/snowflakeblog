"""
setup_oracle_full.py - Complete one-click deployment for Oracle 11g enterprise schema and seed data.
Supports both native `wslc` and `docker`.
"""
import subprocess
import sys
import os

def run_sql_file(sql_file_path, connection_str, use_wslc=True):
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    wrapped_sql = 'SET SQLBLANKLINES ON;\nSET DEFINE OFF;\n' + sql + '\nCOMMIT;\nEXIT;\n'
    cmd = ['wslc' if use_wslc else 'docker', 'exec', '-i', 'mitsui_oracle_11g', 'sqlplus', '-S', connection_str]

    print(f"[*] Executing {os.path.basename(sql_file_path)} with {connection_str.split('@')[0]}...")
    proc = subprocess.run(cmd, input=wrapped_sql.encode('utf-8'), capture_output=True)
    out = proc.stdout.decode('utf-8', errors='replace')
    err = proc.stderr.decode('utf-8', errors='replace')
    
    if proc.returncode != 0 or 'ERROR' in out:
        print(f"[!] Warnings or output in {sql_file_path}:\n{out}")
    else:
        print(f"[+] {os.path.basename(sql_file_path)} executed successfully.")
    return out

def main():
    use_wslc = True
    try:
        subprocess.run(['wslc', '--version'], capture_output=True, check=True)
    except Exception:
        use_wslc = False

    print(f"=== Starting Oracle 11g Enterprise Provisioning (Using {'wslc' if use_wslc else 'docker'}) ===")
    
    # 1. Initialize User, Role, and Schema Permissions
    run_sql_file('scripts/oracle/00_init_user_and_permissions.sql', 'system/Mitsui_Sec_2026@//localhost:1521/xe', use_wslc)

    # 2. Deploy DDL as MITSUI_SRC
    run_sql_file('scripts/oracle/01_create_schema.sql', 'mitsui_src/Mitsui_Sec_2026@//localhost:1521/xe', use_wslc)

    # 3. Seed test dataset as MITSUI_SRC
    run_sql_file('scripts/oracle/02_seed_trades_data.sql', 'mitsui_src/Mitsui_Sec_2026@//localhost:1521/xe', use_wslc)

    print("\n=== Oracle 11g Provisioning Finished Successfully! ===")

if __name__ == '__main__':
    main()
