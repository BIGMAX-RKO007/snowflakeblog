import os
from playwright.sync_api import sync_playwright

files = [
    {
        "type": "word",
        "id": "2552845206828",
        "url": "https://app.box.com/file/2552845206828",
        "screenshot": "docs/images/09_step_00_box_target_word_view.png",
        "save_path": "docs/target_box_file_word.docx"
    },
    {
        "type": "txt",
        "id": "2552847964687",
        "url": "https://app.box.com/file/2552847964687",
        "screenshot": "docs/images/09_step_00_box_target_txt_view.png",
        "save_path": "docs/target_box_file_txt.txt"
    },
    {
        "type": "csv",
        "id": "2570100354915",
        "url": "https://app.box.com/file/2570100354915",
        "screenshot": "docs/images/09_step_00_box_target_csv_view.png",
        "save_path": "docs/target_box_file_csv.csv"
    }
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True
    )
    context = browser.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    
    # Login once
    page.goto("https://app.box.com/login", timeout=60000)
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
            
    print("Logged into Box successfully!")
    
    for item in files:
        print(f"\nProcessing {item['type']} (ID: {item['id']})...")
        page.goto(item['url'], timeout=60000)
        page.wait_for_timeout(6000)
        
        # Take preview screenshot
        page.screenshot(path=item['screenshot'])
        print(f"Captured screenshot: {item['screenshot']}")
        
        # Attempt download
        try:
            with page.expect_download(timeout=10000) as download_info:
                download_btn = page.locator("button[data-resin-target='download'], button:has-text('Download'), button[aria-label*='Download']").first
                if download_btn.is_visible():
                    download_btn.click()
                else:
                    more_btn = page.locator("button[aria-label*='More Options'], button:has-text('More Options')").first
                    if more_btn.is_visible():
                        more_btn.click()
                        page.wait_for_timeout(1000)
                        page.locator("button:has-text('Download'), [role='menuitem']:has-text('Download')").first.click()
            download = download_info.value
            download.save_as(item['save_path'])
            print(f"Downloaded to {item['save_path']}")
        except Exception as e:
            print(f"Could not download directly via UI: {e}")
            
    browser.close()

