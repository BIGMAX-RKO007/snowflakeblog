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

    # Click Data -> Databases on left menu
    page.locator("button[aria-label*='Data'], a[href*='/data']").first.click()
    page.wait_for_timeout(4000)

    # Click on AIRBNB database
    airbnb_link = page.locator("text='AIRBNB'").first
    if airbnb_link.is_visible():
        airbnb_link.click()
        page.wait_for_timeout(4000)

    # Click on DEV schema
    dev_link = page.locator("text='DEV'").first
    if dev_link.is_visible():
        dev_link.click()
        page.wait_for_timeout(4000)

    # Click on Views tab
    views_tab = page.locator("button:has-text('Views'), [role='tab']:has-text('Views')").first
    if views_tab.is_visible():
        views_tab.click()
        page.wait_for_timeout(4000)

    page.screenshot(path="docs/images/dbt_03_step_02_snowflake_dev_views.png")
    print("Updated docs/images/dbt_03_step_02_snowflake_dev_views.png")

    # Navigate to Worksheets
    page.locator("button[aria-label*='Worksheets'], a[href*='/worksheets'], [data-testid='workspaces-nav-item']").first.click()
    page.wait_for_timeout(4000)

    # Click first worksheet
    first_row = page.locator("div[role='row']").nth(1)
    if first_row.is_visible():
        first_row.click()
        page.wait_for_timeout(5000)

    page.screenshot(path="docs/images/dbt_03_step_03_snowflake_worksheet_query.png")
    print("Updated docs/images/dbt_03_step_03_snowflake_worksheet_query.png")

    browser.close()

