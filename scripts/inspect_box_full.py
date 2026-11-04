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
            
    print("Page URL:", page.url)
    
    # Scroll through the whole page
    for i in range(5):
        page.evaluate("window.scrollBy(0, 500)")
        page.wait_for_timeout(500)
        
    # Check all buttons
    for btn in page.locator("button").all():
        txt = btn.inner_text().strip()
        if txt:
            print("Button:", txt)
            
    # Check all inputs and textareas
    for inp in page.locator("input, textarea").all():
        tag = inp.evaluate("el => el.tagName")
        val = inp.get_attribute("value") or inp.inner_text()
        lbl = inp.get_attribute("aria-label") or inp.get_attribute("placeholder") or inp.get_attribute("name")
        print(f"Field ({tag}): label={lbl}, value={val[:30] if val else 'None'}")
        
    page.screenshot(path="docs/images/box_full_config.png", full_page=True)
    browser.close()

