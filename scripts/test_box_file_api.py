import requests
from playwright.sync_api import sync_playwright

def get_token():
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
                
        # Generate token
        token_btn = page.locator("button:has-text('Generate Developer Token'), button:has-text('Generate Token')").first
        if token_btn.is_visible():
            token_btn.scroll_into_view_if_needed()
            token_btn.click()
            page.wait_for_timeout(3000)
            
        page.screenshot(path="docs/images/09_step_01_box_developer_token.png")
        
        # Read token value from input
        for inp in page.locator("input").all():
            v = inp.get_attribute("value")
            if v and len(v) > 25 and not v.startswith("8y6dhg") and v != "*******************":
                browser.close()
                return v
                
        # If masked, click unmask/eye or copy
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        copy_btn = page.locator("button[aria-label*='Copy'], button:has-text('Copy')").all()
        for b in copy_btn:
            b.click()
            clip = page.evaluate("navigator.clipboard.readText()")
            if clip and len(clip) > 25 and not clip.startswith("8y6dhg"):
                browser.close()
                return clip
        browser.close()
    return None

token = get_token()
print("Token acquired:", token[:8] + "..." if token else "None")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    # 1. Get file metadata
    r = requests.get("https://api.box.com/2.0/files/2552846615916", headers=headers)
    print("File metadata status:", r.status_code)
    meta = r.json()
    print("File Name:", meta.get("name"))
    print("File Size:", meta.get("size"))
    print("SHA1:", meta.get("sha1"))
    print("Parent Folder:", meta.get("parent"))
    
    # 2. Download file content
    r_content = requests.get("https://api.box.com/2.0/files/2552846615916/content", headers=headers)
    print("File content status:", r_content.status_code, "Length:", len(r_content.content))
    with open("target_box_file.pdf", "wb") as f:
        f.write(r_content.content)
    print("Saved target_box_file.pdf!")

