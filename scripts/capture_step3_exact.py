from playwright.sync_api import sync_playwright
import time

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        viewport={"width": 1280, "height": 980},
        args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/workspaces/ws/USER%24/PUBLIC/DEFAULT%24", timeout=60000)
    page.wait_for_timeout(6000)
    
    ws_frame = next((f for f in page.frames if "workspaces-wave1" in f.url), None)
    if ws_frame:
        run_btn = ws_frame.locator("button[aria-label*='Run']").first
        
        # Click at x=500, y=120 (Line 1 of editor)
        page.mouse.click(500, 120)
        page.wait_for_timeout(400)
        
        # Select all and delete
        page.keyboard.press("Control+A")
        page.wait_for_timeout(200)
        page.keyboard.press("Backspace")
        page.wait_for_timeout(200)
        
        sql = """USE DATABASE DEV_DEMO_DB;
USE SCHEMA API_INTEGRATION;

CREATE OR REPLACE NETWORK RULE dev_demo_network_rule
  MODE = EGRESS TYPE = HOST_PORT VALUE_LIST = ('httpbin.org', 'api.box.com');

CREATE OR REPLACE SECRET dev_demo_api_secret
  TYPE = GENERIC_STRING SECRET_STRING = 'demo_token_xyz_98765';
"""
        page.keyboard.insert_text(sql)
        page.wait_for_timeout(800)
        
        page.keyboard.press("Control+A")
        page.wait_for_timeout(300)
        
        run_btn.click()
        print("Clicked Run button, waiting 7s...")
        page.wait_for_timeout(7000)
        
        page.screenshot(path="docs/images/09_step_03_create_network_rule_secret.png")
        print("Captured docs/images/09_step_03_create_network_rule_secret.png")

    context.close()

