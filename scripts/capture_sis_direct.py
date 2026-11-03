from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
    )
    context = browser.new_context(viewport={"width": 1280, "height": 1000})
    page = context.new_page()
    
    # Login
    print("[Snowflake] Navigating to login...")
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/homepage", timeout=60000)
    page.wait_for_timeout(4000)
    user_input = page.locator("input[type='text'], input[name='username']").first
    if user_input.is_visible():
        user_input.fill("fanxiao")
        pwd_input = page.locator("input[type='password'], input[name='password']").first
        pwd_input.fill("SuperCoffee!2026")
        page.locator("button[type='submit']").first.click()
        page.wait_for_timeout(8000)
        
    print("[Snowflake] Navigating directly to Streamlit app URL...")
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/streamlit-apps/kkwlxseclagqeaguw4sf", timeout=60000)
    page.wait_for_timeout(10000)
    
    # Screenshot the live dashboard
    page.screenshot(path="docs/images/10_step_04_streamlit_dashboard_live.png")
    print("Saved 10_step_04_streamlit_dashboard_live.png, current URL:", page.url)
    
    # Also navigate to Streamlit list now that permissions are public
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/streamlit-apps", timeout=60000)
    page.wait_for_timeout(5000)
    page.screenshot(path="docs/images/10_step_03_streamlit_app_list.png")
    print("Saved 10_step_03_streamlit_app_list.png")
    
    browser.close()

