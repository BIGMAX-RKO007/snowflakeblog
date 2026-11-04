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
            
    print("Logged in, waiting for download button...")
    page.wait_for_timeout(4000)
    
    # Listen for download event
    with page.expect_download() as download_info:
        # Click more options or download button
        download_btn = page.locator("button[data-resin-target='download'], button:has-text('Download'), button[aria-label*='Download']").first
        if download_btn.is_visible():
            download_btn.click()
        else:
            # Click more options dropdown
            more_btn = page.locator("button[aria-label*='More Options'], button:has-text('More Options')").first
            if more_btn.is_visible():
                more_btn.click()
                page.wait_for_timeout(1000)
                page.locator("button:has-text('Download'), [role='menuitem']:has-text('Download')").first.click()
                
    download = download_info.value
    download.save_as("docs/target_box_file.pdf")
    print("Successfully downloaded PDF to docs/target_box_file.pdf!")
    browser.close()

