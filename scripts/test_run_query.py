from playwright.sync_api import sync_playwright
import time

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        viewport={"width": 1280, "height": 980},
        args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/workspaces/ws/USER%24/PUBLIC/DEFAULT%24", timeout=60000)
    page.wait_for_timeout(6000)
    
    ws_frame = next((f for f in page.frames if "workspaces-wave1" in f.url), None)
    if ws_frame:
        # Click on editor area
        editor = ws_frame.locator(".monaco-editor, textarea").first
        if editor.is_visible():
            print("Clicking editor...")
            editor.click()
            page.wait_for_timeout(500)
            
            # Select all and replace with our query
            ws_frame.press(".monaco-editor, textarea", "Control+A")
            page.wait_for_timeout(300)
            ws_frame.keyboard.type("SELECT CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_WAREHOUSE();")
            page.wait_for_timeout(1000)
            
            # Find and click Run button or press Ctrl+Enter
            run_btn = ws_frame.locator("button[aria-label*='Run'], button:has-text('Run')").first
            if run_btn.is_visible():
                print("Clicking Run button...")
                run_btn.click()
            else:
                print("Pressing Control+Enter...")
                ws_frame.keyboard.press("Control+Enter")
                
            page.wait_for_timeout(5000)
            page.screenshot(path="docs/images/test_query_result.png")
            print("Saved docs/images/test_query_result.png")
            
    context.close()

