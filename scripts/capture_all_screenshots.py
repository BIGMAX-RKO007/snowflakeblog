from playwright.sync_api import sync_playwright
import time
import os

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

def ensure_login(page):
    print("[Snowflake] Checking login state...")
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/homepage", timeout=60000)
    page.wait_for_timeout(4000)
    
    # If login page
    if "oauth/authorize" in page.url or "login" in page.url:
        print("[Snowflake] In login page, filling credentials...")
        # 1. Username
        user_input = page.locator("input[type='text'], input[name='username']").first
        if user_input.is_visible():
            user_input.fill("fanxiao")
            page.wait_for_timeout(1000)
            
        # 2. Check Continue / Next button
        next_btn = page.locator("button:has-text('Continue'), button:has-text('Next'), button:has-text('次へ'), button[type='submit']").first
        if next_btn.is_visible():
            next_btn.click()
            page.wait_for_timeout(2000)
            
        # 3. Password
        pwd_input = page.locator("input[type='password'], input[name='password']").first
        if pwd_input.is_visible():
            pwd_input.fill("SuperCoffee!2026")
            page.wait_for_timeout(1000)
            
        # 4. Sign in
        sign_btn = page.locator("button:has-text('Sign In'), button:has-text('Log In'), button:has-text('ログイン'), button[type='submit']").first
        if sign_btn.is_visible():
            sign_btn.click()
            page.wait_for_timeout(10000)
            
    print("[Snowflake] Current page:", page.url)

def capture_all():
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
        
        # 1. Login to Snowflake
        ensure_login(page)
        
        # 2. Open Worksheets
        print("[Step] Navigating to Worksheets...")
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/worksheets", timeout=60000)
        page.wait_for_timeout(6000)
        
        # Create a new SQL worksheet
        add_ws_btn = page.locator("button[aria-label='Create Worksheet'], button:has-text('+ Worksheet'), button:has-text('+'), [data-testid='add-worksheet-button']").first
        if add_ws_btn.is_visible():
            print("Clicking + Worksheet...")
            add_ws_btn.click()
            page.wait_for_timeout(4000)
            # click SQL Worksheet if menu opens
            sql_opt = page.locator("text='SQL Worksheet', [role='menuitem']:has-text('SQL Worksheet')").first
            if sql_opt.is_visible():
                sql_opt.click()
                page.wait_for_timeout(4000)
                
        print("In Worksheet editor, URL:", page.url)
        
        # Capture Worksheet setup
        page.screenshot(path="docs/images/09_step_02_snowflake_worksheet_setup.png")
        print("Captured 09_step_02_snowflake_worksheet_setup.png")
        
        # Type SQL to create Network Rule and Secret
        editor = page.locator(".monaco-editor textarea, [role='textbox']").first
        if editor.is_visible():
            sql1 = """-- Step 1 & 2: 创建出网规则与 API 凭据
USE DATABASE DEV_DEMO_DB;
USE SCHEMA API_INTEGRATION;

CREATE OR REPLACE NETWORK RULE dev_demo_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = ('httpbin.org', 'api.box.com');

CREATE OR REPLACE SECRET dev_demo_api_secret
  TYPE = GENERIC_STRING
  SECRET_STRING = 'demo_token_xyz_98765';
"""
            editor.fill(sql1)
            page.wait_for_timeout(1500)
            # Run query (Ctrl+Enter or Run button)
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(6000)
            page.screenshot(path="docs/images/09_step_03_create_network_rule_secret.png")
            print("Captured 09_step_03_create_network_rule_secret.png")
            
            # Step 4: Run EAI and capture error 509009
            sql2 = """-- Step 3: 创建外部访问集成 (触发试用账号拦截)
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION dev_demo_external_access_int
  ALLOWED_NETWORK_RULES = (dev_demo_network_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (dev_demo_api_secret)
  ENABLED = TRUE;
"""
            editor.fill(sql2)
            page.wait_for_timeout(1500)
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(6000)
            page.screenshot(path="docs/images/09_step_04_trial_error_509009.png")
            print("Captured 09_step_04_trial_error_509009.png")
            
            # Step 5: Query API Ingestion Table
            sql3 = """-- Step 4: 查询客户端管道 API 摄取数据表
SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.API_INGESTION_LOG ORDER BY FETCH_TIME DESC;
"""
            editor.fill(sql3)
            page.wait_for_timeout(1500)
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(5000)
            page.screenshot(path="docs/images/09_step_05_api_ingestion_log_query.png")
            print("Captured 09_step_05_api_ingestion_log_query.png")
            
            # Step 6: Query test_sales_metrics table
            sql4 = """-- Chapter 10 Step 1: 准备底表与测试监控数据
SELECT * FROM DEV_DEMO_DB.API_INTEGRATION.test_sales_metrics ORDER BY date ASC;
"""
            editor.fill(sql4)
            page.wait_for_timeout(1500)
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(5000)
            page.screenshot(path="docs/images/10_step_01_test_sales_metrics_table.png")
            print("Captured 10_step_01_test_sales_metrics_table.png")
            
            # Step 7: List Stage files
            sql5 = """-- Chapter 10 Step 2: 验证内部 Stage 上的 Streamlit 源码文件
LIST @DEV_DEMO_DB.API_INTEGRATION.dev_streamlit_stage;
"""
            editor.fill(sql5)
            page.wait_for_timeout(1500)
            page.keyboard.press("Control+Enter")
            page.wait_for_timeout(5000)
            page.screenshot(path="docs/images/10_step_02_stage_streamlit_file.png")
            print("Captured 10_step_02_stage_streamlit_file.png")
            
        # Step 8: Streamlit Apps list
        print("Navigating to Streamlit list...")
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/streamlit-apps", timeout=60000)
        page.wait_for_timeout(8000)
        page.screenshot(path="docs/images/10_step_03_streamlit_app_list.png")
        print("Captured 10_step_03_streamlit_app_list.png")
        
        # Step 9: Open Streamlit app directly
        print("Opening Streamlit app...")
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/streamlit-apps/kkwlxseclagqeaguw4sf", timeout=60000)
        page.wait_for_timeout(12000)
        page.screenshot(path="docs/images/10_step_04_streamlit_dashboard_live.png")
        print("Captured 10_step_04_streamlit_dashboard_live.png")
        
        # Step 10: Filter selectbox inside iframe
        for f in page.frames:
            try:
                sb = f.locator("div[data-baseweb='select']").first
                if sb.is_visible():
                    print("Found selectbox in frame:", f.name)
                    sb.click()
                    page.wait_for_timeout(1500)
                    opt = f.locator("text='Electronics', [role='option']:has-text('Electronics')").first
                    if opt.is_visible():
                        opt.click()
                        page.wait_for_timeout(3000)
                        page.screenshot(path="docs/images/10_step_05_streamlit_interactive_filter.png")
                        print("Captured 10_step_05_streamlit_interactive_filter.png")
                        break
            except Exception as e:
                pass

        context.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    capture_all()

