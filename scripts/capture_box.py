from playwright.sync_api import sync_playwright
import time

def capture_box_token():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 1000})
        page = context.new_page()
        
        print("[Box] Navigating to developer console...")
        page.goto("https://app.box.com/developers/console", timeout=60000)
        page.wait_for_timeout(4000)
        
        # Check login
        login_input = page.locator("input[name='login'], input[type='email']").first
        if login_input.is_visible():
            print("[Box] Filling login email...")
            login_input.fill("fx369246926@gmail.com")
            page.locator("button:has-text('Next'), button[type='submit']").first.click()
            page.wait_for_timeout(3000)
            
            pwd_input = page.locator("input[name='password'], input[type='password']").first
            if pwd_input.is_visible():
                print("[Box] Filling password...")
                pwd_input.fill("SuperCoffee!2026")
                page.locator("button:has-text('Log In'), button[type='submit']").first.click()
                page.wait_for_timeout(8000)
                
        print("[Box] Current URL:", page.url)
        page.screenshot(path="docs/images/09_step_01_box_console_home.png")
        print("[Box] Saved 09_step_01_box_console_home.png")
        
        # If there is a Custom App card or link, click it
        app_card = page.locator("a[href*='/developers/console/app/'], div:has-text('Snowflake'), div:has-text('App')").first
        if app_card.is_visible():
            print("[Box] Clicking app card...")
            app_card.click()
            page.wait_for_timeout(5000)
            
            # Click Configuration tab if present
            config_tab = page.locator("a:has-text('Configuration'), button:has-text('Configuration'), [role='tab']:has-text('Configuration')").first
            if config_tab.is_visible():
                print("[Box] Clicking Configuration tab...")
                config_tab.click()
                page.wait_for_timeout(4000)
                
            # Scroll down to Developer Token section
            dev_token_sec = page.locator("text='Developer Token'").first
            if dev_token_sec.is_visible():
                dev_token_sec.scroll_into_view_if_needed()
                page.wait_for_timeout(2000)
                
            page.screenshot(path="docs/images/09_step_01_box_developer_token.png")
            print("[Box] Saved 09_step_01_box_developer_token.png")
            
        browser.close()

if __name__ == "__main__":
    capture_box_token()

