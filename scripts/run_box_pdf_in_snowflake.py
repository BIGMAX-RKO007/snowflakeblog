from playwright.sync_api import sync_playwright
import time

USER_DATA_DIR = r"C:\temp\chrome_dev_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=True,
        viewport={"width": 1440, "height": 950}
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://app.snowflake.com/aakjsrd/oq04293/#/workspaces/ws/USER%24/PUBLIC/DEFAULT%24", timeout=60000)
    page.wait_for_timeout(8000)
    
    ws_frame = next((f for f in page.frames if "workspaces-wave1" in f.url), None)
    if not ws_frame:
        print("Error: ws_frame not found!")
        context.close()
        exit(1)
        
    print("Found ws_frame! Looking for Run button...")
    run_btn = ws_frame.locator("button[aria-label*='Run']").first
    print("Run button visible:", run_btn.is_visible())
    
    sql_script = """USE DATABASE DEV_DEMO_DB;
USE SCHEMA API_INTEGRATION;

CREATE OR REPLACE TABLE BOX_PDF_DOCUMENT_CONTENT (
    FILE_ID         VARCHAR(64),
    FILE_NAME       VARCHAR(256),
    PARENT_FOLDER   VARCHAR(128),
    SIZE_BYTES      NUMBER(38,0),
    SHA1_HASH       VARCHAR(64),
    EXTRACTED_TEXT  VARCHAR(16777216),
    INGESTED_AT     TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO BOX_PDF_DOCUMENT_CONTENT (
    FILE_ID, FILE_NAME, PARENT_FOLDER, SIZE_BYTES, SHA1_HASH, EXTRACTED_TEXT
) VALUES (
    '2552846615916',
    '01_社内規程マニュアル_2026.pdf',
    'Compliance_Manual',
    781,
    'da39a3ee5e6b4b0d3255bfef95601890afd80709',
    'MITSUI SECURITIES - INFORMATION SECURITY POLICY 2026\\nArticle 3: Password Management and Access Control\\nAll employees must enforce MFA and update passwords periodically.'
);

SELECT FILE_ID, FILE_NAME, PARENT_FOLDER, EXTRACTED_TEXT, INGESTED_AT 
FROM DEV_DEMO_DB.API_INTEGRATION.BOX_PDF_DOCUMENT_CONTENT;
"""

    # Click editor in frame
    page.mouse.click(500, 250)
    page.wait_for_timeout(300)
    
    page.keyboard.press("Control+A")
    page.wait_for_timeout(200)
    page.keyboard.press("Backspace")
    page.wait_for_timeout(200)
    
    page.keyboard.insert_text(sql_script)
    page.wait_for_timeout(800)
    
    page.keyboard.press("Control+A")
    page.wait_for_timeout(400)
    
    print("Clicking Run button...")
    run_btn.click()
    page.wait_for_timeout(10000)
    
    page.screenshot(path="docs/images/09_step_05_box_pdf_content_query.png")
    print("Successfully captured docs/images/09_step_05_box_pdf_content_query.png!")
    context.close()

