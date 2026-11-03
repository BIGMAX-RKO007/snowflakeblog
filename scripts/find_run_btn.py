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
    page.wait_for_timeout(5000)
    
    ws_frame = next((f for f in page.frames if "workspaces-wave1" in f.url), None)
    if ws_frame:
        buttons = ws_frame.locator("button").all()
        for b in buttons:
            box = b.bounding_box()
            if box and box["y"] < 120 and box["x"] < 400:
                print("Button in ws_frame:", b.inner_text(), b.get_attribute("aria-label"), b.get_attribute("data-testid"), box)
            
    context.close()
