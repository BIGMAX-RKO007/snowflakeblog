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
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/homepage", timeout=60000)
    page.wait_for_timeout(5000)
    print("Current URL:", page.url)
    
    # Check if login form exists
    inputs = page.locator("input").all()
    print("Found inputs:", len(inputs))
    for i, inp in enumerate(inputs):
        try:
            print(f"Input {i}: name={inp.get_attribute('name')}, type={inp.get_attribute('type')}, placeholder={inp.get_attribute('placeholder')}")
        except Exception as e:
            pass
            
    # Try filling username if exists
    try:
        user_input = page.locator("input[name='username'], input[type='text'], input[placeholder*='Username'], input[placeholder*='ユーザー名']").first
        if user_input.is_visible():
            print("Filling username...")
            user_input.fill("fanxiao")
            page.wait_for_timeout(1000)
            
            # Click next or check for password
            next_btn = page.locator("button:has-text('Continue'), button:has-text('Next'), button:has-text('次へ'), button[type='submit']").first
            if next_btn.is_visible():
                print("Clicking Next/Continue button...")
                next_btn.click()
                page.wait_for_timeout(2000)
                
            pwd_input = page.locator("input[type='password'], input[name='password']").first
            if pwd_input.is_visible():
                print("Filling password...")
                pwd_input.fill("SuperCoffee!2026")
                page.wait_for_timeout(1000)
                sign_in = page.locator("button[type='submit'], button:has-text('Sign In'), button:has-text('Log In'), button:has-text('ログイン')").first
                if sign_in.is_visible():
                    print("Clicking Sign In...")
                    sign_in.click()
                    page.wait_for_timeout(8000)
                    print("Logged in, current URL:", page.url)
    except Exception as e:
        print("Error during login:", e)

    page.screenshot(path="docs/images/test_sf_after_login.png")
    print("Saved test_sf_after_login.png")
    browser.close()

