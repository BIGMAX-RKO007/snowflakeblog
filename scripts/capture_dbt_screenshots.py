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

    # Screenshot 1: Data -> Databases -> AIRBNB
    print("Navigating to Databases...")
    page.goto(f"{ACCOUNT_URL}/#/data/databases/AIRBNB/schemas/RAW/tables", timeout=60000)
    page.wait_for_timeout(8000)
    page.screenshot(path="docs/images/dbt_02_step_01_snowflake_airbnb_database.png")
    print("Captured docs/images/dbt_02_step_01_snowflake_airbnb_database.png")

    # Screenshot 2: Admin -> Users & Roles
    print("Navigating to Users...")
    page.goto(f"{ACCOUNT_URL}/#/admin/users", timeout=60000)
    page.wait_for_timeout(8000)
    page.screenshot(path="docs/images/dbt_02_step_02_users_and_roles.png")
    print("Captured docs/images/dbt_02_step_02_users_and_roles.png")

    # Screenshot 4: Workspaces SQL Worksheet querying AIRBNB.RAW.RAW_LISTINGS
    print("Navigating to Workspaces SQL Worksheet...")
    page.goto(f"{ACCOUNT_URL}/#/workspaces", timeout=60000)
    page.wait_for_timeout(8000)
    page.screenshot(path="docs/images/dbt_02_step_04_workspaces_airbnb_query.png")
    print("Captured docs/images/dbt_02_step_04_workspaces_airbnb_query.png")

    browser.close()
    print("All browser screenshots captured!")
