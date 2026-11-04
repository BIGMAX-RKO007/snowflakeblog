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
            
    fetch_btn = page.locator("button:has-text('Fetch Secret')").first
    if fetch_btn.is_visible():
        fetch_btn.click()
        page.wait_for_timeout(2000)
        
    dialogs = page.locator("[role='dialog'], .modal, div[class*='modal']").all()
    with open("secret_dialog.txt", "w", encoding="utf-8") as f:
        for d in dialogs:
            f.write(d.inner_text() + "\n---\n")
    print("Written to secret_dialog.txt")
    browser.close()
