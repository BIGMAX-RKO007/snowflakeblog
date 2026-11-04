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
            
    # Click generate token
    token_btn = page.locator("button:has-text('Generate Developer Token'), button:has-text('Generate Token')").first
    if token_btn.is_visible():
        token_btn.click()
        page.wait_for_timeout(3000)
        
    # Find Developer Token input container
    dev_token_input = page.locator("input[aria-label='Developer Token']").first
    print("Dev token input type:", dev_token_input.get_attribute("type"))
    
    # Click the end icon (the eye/key icon) next to it
    end_icon = page.locator(".devcon-configuration__dev-token-masked-input svg, .devcon-configuration__dev-token-masked-input .bp_base_text_input_module_endIcon--eee42").first
    if end_icon.is_visible():
        print("Clicking endIcon to unmask...")
        end_icon.click()
        page.wait_for_timeout(1000)
        
    # Read value again
    val = dev_token_input.input_value()
    print("Input value after click:", val[:10] + "..." if val else "None", "Length:", len(val) if val else 0)
    
    with open("box_real_token.txt", "w", encoding="utf-8") as f:
        f.write(val)
        
    page.screenshot(path="docs/images/09_step_01_box_developer_token.png")
    print("Saved 09_step_01_box_developer_token.png")
    browser.close()

