from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1280, "height": 1200})
    page = context.new_page()
    page.goto("https://app.box.com/developers/console/app/2717878/configuration", timeout=60000)
    page.wait_for_timeout(3000)
    
    login_input = page.locator("input[name='login'], input[type='email']").first
    if login_input.is_visible():
        login_input.fill("fx369246926@gmail.com")
        page.locator("button:has-text('Next'), button[type='submit']").first.click()
        page.wait_for_timeout(3000)
        pwd_input = page.locator("input[name='password'], input[type='password']").first
        if pwd_input.is_visible():
            pwd_input.fill("SuperCoffee!2026")
            page.locator("button:has-text('Log In'), button[type='submit']").first.click()
            page.wait_for_timeout(8000)
            
    # Click Fetch Secret
    fetch_btn = page.locator("button:has-text('Fetch Secret')").first
    if fetch_btn.is_visible():
        print("Clicking Fetch Secret...")
        fetch_btn.click()
        page.wait_for_timeout(3000)
        
    # Check all inputs now
    for inp in page.locator("input").all():
        lbl = inp.get_attribute("aria-label") or inp.get_attribute("id")
        val = inp.get_attribute("value")
        if val and len(val) > 10:
            print(f"Input: {lbl} -> {val}")
            
    page.screenshot(path="docs/images/09_step_01_box_credentials_revealed.png")
    print("Saved 09_step_01_box_credentials_revealed.png")
    browser.close()

