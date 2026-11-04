from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1280, "height": 1200})
    page = context.new_page()
    
    # Listen to network responses
    tokens_captured = []
    def on_response(response):
        if "token" in response.url.lower():
            try:
                data = response.json()
                print(f"Network response from {response.url}:")
                print(data)
                if isinstance(data, dict) and "token" in data:
                    tokens_captured.append(data["token"])
                if isinstance(data, dict) and "access_token" in data:
                    tokens_captured.append(data["access_token"])
            except Exception:
                pass
    page.on("response", on_response)
    
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
            
    # Click Revoke then Generate, or Generate Token
    revoke_btn = page.locator("button[aria-label='Revoke Developer Token']").first
    if revoke_btn.is_visible():
        print("Clicking Revoke...")
        revoke_btn.click()
        page.wait_for_timeout(2000)
        
    token_btn = page.locator("button:has-text('Generate Developer Token'), button:has-text('Generate Token')").first
    if token_btn.is_visible():
        print("Clicking Generate...")
        token_btn.click()
        page.wait_for_timeout(3000)
        
    print("Tokens captured:", tokens_captured)
    if tokens_captured:
        with open("real_box_api_token.txt", "w") as f:
            f.write(tokens_captured[-1])
    browser.close()

