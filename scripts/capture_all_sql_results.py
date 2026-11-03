from playwright.sync_api import sync_playwright
import time
import os

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

def run_all_queries():
    os.makedirs("docs/images", exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            viewport={"width": 1280, "height": 980},
            args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        
        print("[1] Opening Workspaces...")
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/workspaces/ws/USER%24/PUBLIC/DEFAULT%24", timeout=60000)
        page.wait_for_timeout(6000)
        
        ws_frame = next((f for f in page.frames if "workspaces-wave1" in f.url), None)
        if not ws_frame:
            print("Error: ws_frame not found")
            return

        run_btn = ws_frame.locator("button[aria-label*='Run']").first
        print("Run button found:", run_btn.is_visible())
        
        def run_and_capture(sql_text, save_path, wait_sec=6):
            print(f"\n--- Running: {save_path} ---")
            # Click into editor
            page.mouse.click(500, 250)
            page.wait_for_timeout(300)
            
            # Select all and delete
            page.keyboard.press("Control+A")
            page.wait_for_timeout(200)
            page.keyboard.press("Backspace")
            page.wait_for_timeout(200)
            
            # Type text
            page.keyboard.insert_text(sql_text)
            page.wait_for_timeout(800)
            
            # Select all
            page.keyboard.press("Control+A")
            page.wait_for_timeout(300)
            
            # Click Run button
            run_btn.click()
            print(f"Clicked Run button, waiting {wait_sec}s for result...")
            page.wait_for_timeout(wait_sec * 1000)
            
            page.screenshot(path=save_path)
            print(f"-> Successfully captured: {save_path}")

        # 1. Network Rule & Secret
        sql1 = """USE DATABASE DEV_DEMO_DB;
USE SCHEMA API_INTEGRATION;

CREATE OR REPLACE NETWORK RULE dev_demo_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('httpbin.org', 'api.box.com');

CREATE OR REPLACE SECRET dev_demo_api_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'demo_token_xyz_98765';
"""
        run_and_capture(sql1, "docs/images/09_step_03_create_network_rule_secret.png", wait_sec=7)

        # 2. External Access Integration (Error 509009)
        sql2 = """CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION dev_demo_external_access_int
  ALLOWED_NETWORK_RULES = (dev_demo_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (dev_demo_api_secret)
  ENABLED = TRUE;
"""
        run_and_capture(sql2, "docs/images/09_step_04_trial_error_509009.png", wait_sec=6)

        # 3. Query API Ingestion Log Table
        sql3 = """SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.API_INGESTION_LOG 
ORDER BY FETCH_TIME DESC;
"""
        run_and_capture(sql3, "docs/images/09_step_05_api_ingestion_log_query.png", wait_sec=6)

        # 4. Chapter 10 Step 1 - test_sales_metrics
        sql4 = """SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics 
ORDER BY date ASC;
"""
        run_and_capture(sql4, "docs/images/10_step_01_test_sales_metrics_table.png", wait_sec=6)

        # 5. Chapter 10 Step 2 - List Stage
        sql5 = """LIST @DEV_DEMO_DB.API_INTEGRATION.dev_streamlit_stage;
"""
        run_and_capture(sql5, "docs/images/10_step_02_stage_streamlit_file.png", wait_sec=6)

        context.close()
        print("ALL SQL QUERIES CAPTURED!")

if __name__ == "__main__":
    run_all_queries()

