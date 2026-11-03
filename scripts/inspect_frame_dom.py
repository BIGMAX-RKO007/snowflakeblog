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
        print("Frames inside ws_frame:", len(ws_frame.child_frames))
        for cf in ws_frame.child_frames:
            print("Child frame:", cf.url)
            
        textareas = ws_frame.locator("textarea").all()
        print("Textareas:", len(textareas))
        for t in textareas:
            print("Textarea class:", t.get_attribute("class"))
            
        ces = ws_frame.locator("[contenteditable='true']").all()
        print("Contenteditable:", len(ces))
        for c in ces:
            print("CE class:", c.get_attribute("class"), "tag:", c.evaluate("e => e.tagName"))
            
        buttons = ws_frame.locator("button").all()
        print("Buttons in ws_frame:", len(buttons))
        for b in buttons[:15]:
            t = b.inner_text().strip().replace("\n", " ")
            aria = b.get_attribute("aria-label") or ""
            print(f"Button: text='{t}', aria='{aria}'")
            
    context.close()

