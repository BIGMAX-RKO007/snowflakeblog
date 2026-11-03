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
    
    print("Frames count:", len(page.frames))
    for i, f in enumerate(page.frames):
        print(f"Frame {i}: url={f.url}")
        
    ces = page.locator("[contenteditable='true'], textarea, [role='textbox']").all()
    print("Editable elements count:", len(ces))
    for i, el in enumerate(ces):
        try:
            tag = el.evaluate("e => e.tagName")
            cls = el.get_attribute("class")
            print(f"Element {i}: tag={tag}, class={cls}")
        except Exception as e:
            pass
            
    # Try clicking the center of the editor area (e.g. x=500, y=300)
    page.mouse.click(500, 300)
    page.wait_for_timeout(1000)
    page.keyboard.type("SELECT 99999 AS test_click;")
    page.wait_for_timeout(1000)
    page.screenshot(path="docs/images/test_typed.png")
    print("Captured test_typed.png")
    
    context.close()

