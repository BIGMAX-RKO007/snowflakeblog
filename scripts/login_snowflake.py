from playwright.sync_api import sync_playwright

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
        viewport={"width": 1440, "height": 900}
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/workspaces/ws/USER%24/PUBLIC/DEFAULT%24", timeout=60000)
    page.wait_for_timeout(4000)
    
    # Fill login form if present
    u_inp = page.locator("input[name='username'], input[type='text']").first
    if u_inp.is_visible():
        print("Filling login credentials...")
        u_inp.fill("fanxiao")
        p_inp = page.locator("input[name='password'], input[type='password']").first
        p_inp.fill("SuperCoffee!2026")
        page.locator("button[type='submit'], button:has-text('Sign In')").first.click()
        page.wait_for_timeout(10000)
        
    print("Logged in URL:", page.url)
    page.screenshot(path="docs/images/snowflake_after_login.png")
    print("Saved docs/images/snowflake_after_login.png")
    context.close()

