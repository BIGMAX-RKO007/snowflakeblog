from playwright.sync_api import sync_playwright
import time

def login_snowflake(page):
    print("[Snowflake] Navigating to homepage...")
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/homepage", timeout=60000)
    page.wait_for_timeout(5000)
    
    # Check if login form is displayed
    user_input = page.locator("input[type='text'], input[name='username']").first
    if user_input.is_visible():
        print("[Snowflake] Logging in...")
        user_input.fill("fanxiao")
        pwd_input = page.locator("input[type='password'], input[name='password']").first
        pwd_input.fill("SuperCoffee!2026")
        page.locator("button[type='submit'], button:has-text('Sign In'), button:has-text('Log In'), button:has-text('ログイン')").first.click()
        page.wait_for_timeout(8000)
    print("[Snowflake] Current URL after login:", page.url)

def test_snowflake():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 1000})
        page = context.new_page()
        
        login_snowflake(page)
        
        # 1. Navigate to Streamlit apps
        print("[Snowflake] Navigating to Streamlit apps...")
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/streamlit-apps", timeout=60000)
        page.wait_for_timeout(8000)
        page.screenshot(path="docs/images/10_step_03_streamlit_app_list.png")
        print("[Snowflake] Saved 10_step_03_streamlit_app_list.png")
        
        # Check if DEV_DEMO_DASHBOARD is visible and click it
        app_item = page.locator("text='DEV_DEMO_DASHBOARD'").first
        if app_item.is_visible():
            print("[Snowflake] Found DEV_DEMO_DASHBOARD, clicking...")
            app_item.click()
            page.wait_for_timeout(10000)
            page.screenshot(path="docs/images/10_step_04_streamlit_dashboard_live.png")
            print("[Snowflake] Saved 10_step_04_streamlit_dashboard_live.png")
            
            # Try finding selectbox inside the Streamlit iframe
            # Streamlit runs inside an iframe in Snowsight
            for frame in page.frames:
                try:
                    selectbox = frame.locator("div[data-baseweb='select']").first
                    if selectbox.is_visible():
                        print("[Snowflake] Found selectbox in frame:", frame.name)
                        selectbox.click()
                        page.wait_for_timeout(1500)
                        # click Electronics
                        opt = frame.locator("li:has-text('Electronics'), [role='option']:has-text('Electronics')").first
                        if opt.is_visible():
                            opt.click()
                            page.wait_for_timeout(3000)
                            page.screenshot(path="docs/images/10_step_05_streamlit_interactive_filter.png")
                            print("[Snowflake] Saved 10_step_05_streamlit_interactive_filter.png")
                            break
                except Exception as e:
                    print("Frame search error:", e)
        else:
            print("[Snowflake] DEV_DEMO_DASHBOARD text not found on page")
            
        browser.close()

if __name__ == "__main__":
    test_snowflake()

