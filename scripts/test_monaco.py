from playwright.sync_api import sync_playwright
import time

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

def test_monaco():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            viewport={"width": 1280, "height": 980},
            args=["--window-position=1280,0", "--window-size=1280,1040", "--no-first-run", "--no-default-browser-check"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/worksheets", timeout=60000)
        page.wait_for_timeout(6000)
        
        # Check if monaco exists
        has_monaco = page.evaluate("typeof window.monaco !== 'undefined'")
        print("has_monaco on page:", has_monaco)
        
        # Click on worksheet if there's one
        ws_item = page.locator("text='SQL Worksheet', [data-testid='worksheet-list-item']").first
        if ws_item.is_visible():
            ws_item.click()
            page.wait_for_timeout(5000)
            
        has_monaco2 = page.evaluate("typeof window.monaco !== 'undefined'")
        print("has_monaco after click:", has_monaco2)
        if has_monaco2:
            model_count = page.evaluate("window.monaco.editor.getModels().length")
            print("Monaco models count:", model_count)
            if model_count > 0:
                page.evaluate("window.monaco.editor.getModels()[0].setValue('SELECT 12345 AS test_result;')")
                print("Set Monaco text successfully!")
                page.wait_for_timeout(1000)
                # Press Ctrl+Enter
                page.keyboard.press("Control+Enter")
                page.wait_for_timeout(4000)
                page.screenshot(path="docs/images/test_monaco_run.png")
                print("Captured test_monaco_run.png")
                
        context.close()

if __name__ == "__main__":
    test_monaco()

