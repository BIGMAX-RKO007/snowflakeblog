from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto("https://app.box.com/file/2552846615916", timeout=60000)
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
            
    print("Page Title:", page.title())
    print("Page URL:", page.url)
    
    # Wait for PDF viewer or preview to load
    page.wait_for_timeout(5000)
    page.screenshot(path="docs/images/09_step_00_box_target_pdf_view.png")
    print("Saved docs/images/09_step_00_box_target_pdf_view.png")
    
    # Check page texts
    text_content = page.locator("body").inner_text()
    for line in text_content.split("\n")[:30]:
        if line.strip():
            print("Line:", line.strip())
            
    browser.close()

