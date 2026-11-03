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
        sql_btn = ws_frame.locator("button:has-text('SQL file')").first
        if sql_btn.is_visible():
            print("Clicking 'SQL file' button...")
            sql_btn.click()
            page.wait_for_timeout(5000)
            
            # Let's inspect what appeared
            print("Child frames now:", len(ws_frame.child_frames))
            textareas = ws_frame.locator("textarea, .monaco-editor, [contenteditable='true']").all()
            print("Found editor elements:", len(textareas))
            
            page.screenshot(path="docs/images/test_sql_file_opened.png")
            print("Saved docs/images/test_sql_file_opened.png")
            
    context.close()

