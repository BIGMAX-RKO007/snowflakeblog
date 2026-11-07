import os
import time
from playwright.sync_api import sync_playwright

os.makedirs("docs/images", exist_ok=True)

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

    print("Navigating to Snowflake login...")
    page.goto(ACCOUNT_URL, timeout=60000)
    page.wait_for_timeout(4000)

    # Fill username and password if login page appears
    user_input = page.locator("input[name='username'], input[type='text']").first
    pwd_input = page.locator("input[name='password'], input[type='password']").first
    if user_input.is_visible() and pwd_input.is_visible():
        print("Filling credentials...")
        user_input.fill(USER)
        pwd_input.fill(PASSWORD)
        page.locator("button:has-text('Sign In'), button[type='submit']").first.click()
        page.wait_for_timeout(10000)

    print("Logged in, current URL:", page.url)

    # Screenshot 1: Data -> Databases -> AIRBNB -> DEV -> Views
    print("Navigating to AIRBNB.DEV views...")
    page.goto(f"{ACCOUNT_URL}/#/data/databases/AIRBNB/schemas/DEV/views", timeout=60000)
    page.wait_for_timeout(8000)
    page.screenshot(path="docs/images/dbt_03_step_02_snowflake_dev_views.png")
    print("Captured docs/images/dbt_03_step_02_snowflake_dev_views.png")

    # Screenshot 2: Workspaces SQL Worksheet querying AIRBNB.DEV.SRC_LISTINGS
    print("Navigating to Workspaces SQL Worksheet...")
    page.goto(f"{ACCOUNT_URL}/#/workspaces", timeout=60000)
    page.wait_for_timeout(8000)

    # Click on the first worksheet if available or create a new one
    first_ws = page.locator("div[role='row'], tr, div:has-text('Worksheet')").first
    if first_ws.is_visible():
        first_ws.click()
        page.wait_for_timeout(4000)

    page.screenshot(path="docs/images/dbt_03_step_03_snowflake_worksheet_query.png")
    print("Captured docs/images/dbt_03_step_03_snowflake_worksheet_query.png")

    browser.close()
    print("All Chapter 03 browser screenshots captured!")

