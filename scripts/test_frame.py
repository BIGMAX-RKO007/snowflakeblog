from playwright.sync_api import sync_playwright

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
        print("Found workspaces frame!")
        has_monaco = ws_frame.evaluate("typeof window.monaco !== 'undefined'")
        print("has_monaco in frame:", has_monaco)
        if has_monaco:
            count = ws_frame.evaluate("window.monaco.editor.getModels().length")
            print("Monaco models count in frame:", count)
            if count > 0:
                ws_frame.evaluate("window.monaco.editor.getModels()[0].setValue('SELECT 100 AS result, CURRENT_TIMESTAMP() AS query_time;')")
                print("Text set successfully in Monaco!")
                page.wait_for_timeout(1000)
                # Press Ctrl+Enter inside the frame
                ws_frame.press("body", "Control+Enter")
                page.wait_for_timeout(4000)
                page.screenshot(path="docs/images/test_frame_monaco.png")
                print("Saved docs/images/test_frame_monaco.png")
    else:
        print("workspaces frame not found")
        
    context.close()

