from playwright.sync_api import sync_playwright
import requests
import json
import os

def run():
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
        
        # Look for Developer Token section
        token_btn = page.locator("button:has-text('Generate Developer Token'), button:has-text('Generate Token')").first
        if token_btn.is_visible():
            print("Clicking Generate Token button...")
            token_btn.scroll_into_view_if_needed()
            token_btn.click()
            page.wait_for_timeout(3000)
            
        page.screenshot(path="docs/images/09_step_01_box_developer_token.png")
        print("Captured docs/images/09_step_01_box_developer_token.png")
        
        # Read the developer token input field
        token = None
        for inp in page.locator("input").all():
            val = inp.get_attribute("value")
            if val and len(val) > 25 and not val.startswith("8y6dhg"):
                token = val
                break
                
        print("Token acquired:", token[:8] + "..." if token else "None")
        browser.close()
        
        if token:
            with open("box_token.txt", "w", encoding="utf-8") as f:
                f.write(token)
            
            headers = {"Authorization": f"Bearer {token}"}
            # 1. Fetch user info
            r_user = requests.get("https://api.box.com/2.0/users/me", headers=headers)
            user_data = r_user.json()
            print("User info status:", r_user.status_code)
            print("User name:", user_data.get("name"), "Login:", user_data.get("login"))
            
            # 2. Fetch root folder items
            r_folder = requests.get("https://api.box.com/2.0/folders/0/items", headers=headers)
            folder_data = r_folder.json()
            print("Folder items status:", r_folder.status_code)
            entries = folder_data.get("entries", [])
            print(f"Total entries in root folder: {len(entries)}")
            for item in entries:
                print(f" - [{item.get('type')}] ID: {item.get('id')} | Name: {item.get('name')}")
                
            with open("box_root_items.json", "w", encoding="utf-8") as f:
                json.dump(folder_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run()
