import os
import time
from playwright.sync_api import sync_playwright

USER = "FANXIAO"
PASSWORD = "SuperCoffee!2026"
ACCOUNT_URL = "https://mvfryvt-nv04752.snowflakecomputing.com"

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()

    page.goto(ACCOUNT_URL, timeout=60000)
    page.wait_for_timeout(4000)

    user_input = page.locator("input[name='username'], input[type='text']").first
    pwd_input = page.locator("input[name='password'], input[type='password']").first
    if user_input.is_visible() and pwd_input.is_visible():
        user_input.fill(USER)
        pwd_input.fill(PASSWORD)
        page.locator("button:has-text('Sign In'), button[type='submit']").first.click()
        page.wait_for_timeout(8000)

    # Navigate to Workspaces directly
    page.goto("https://app.snowflake.com/mvfryvt/nv04752/#/workspaces", timeout=60000)
    page.wait_for_timeout(6000)

    # Click first item in worksheets table
    first_row = page.locator("tr[role='row'], div[role='row']").nth(1)
    if first_row.is_visible():
        first_row.click()
        page.wait_for_timeout(5000)
        
        # Click run button (Ctrl+Enter or button with run icon / text 'Run')
        run_btn = page.locator("button[aria-label*='Run'], button:has-text('Run')").first
        if run_btn.is_visible():
            run_btn.click()
            page.wait_for_timeout(6000)

    page.screenshot(path="docs/images/dbt_03_step_03_snowflake_worksheet_query.png")
    print("Updated docs/images/dbt_03_step_03_snowflake_worksheet_query.png")

    browser.close()

