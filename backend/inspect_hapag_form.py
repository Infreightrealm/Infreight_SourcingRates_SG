"""Hapag-Lloyd form inspector."""
import os
import asyncio
from dotenv import load_dotenv
load_dotenv("backend/.env")
from carriers.hapag_lloyd_connector import HapagLloydConnector

async def inspect():
    if not os.getenv("HAPAG_LLOYD_USERNAME"):
        os.environ["HAPAG_LLOYD_USERNAME"] = "BOOKINGSG@IN-FREIGHT.COM"
    if not os.getenv("HAPAG_LLOYD_PASSWORD"):
        os.environ["HAPAG_LLOYD_PASSWORD"] = "IFSGb2020"

    # Set current_request to US_CA so it loads the correct profile and credentials
    class MockRequest:
        hapag_region = "US_CA"
    
    connector = HapagLloydConnector()
    connector.current_request = MockRequest()
    
    us_user = os.getenv("HAPAG_LLOYD_USERNAME_US_CA")
    us_pass = os.getenv("HAPAG_LLOYD_PASSWORD_US_CA")
    if us_user and us_pass:
        os.environ["HAPAG_LLOYD_USERNAME"] = us_user
        os.environ["HAPAG_LLOYD_PASSWORD"] = us_pass
    else:
        print("Warning: HAPAG_LLOYD_USERNAME_US_CA is not set. Defaulting to ROW credentials.")
    
    try:
        print("Logging in...")
        login_success = await connector.login()
        print(f"Login success: {login_success}")
        if not login_success:
            return

        # Settle
        await asyncio.sleep(5)

        # Dump details of all inputs on the active form
        print("\nDumping all input elements:")
        inputs_data = await connector.page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input, select, button'));
            return inputs.map((el, idx) => {
                const rect = el.getBoundingClientRect();
                return {
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    type: el.type,
                    name: el.name,
                    placeholder: el.placeholder || '',
                    value: el.value || '',
                    innerText: el.innerText || '',
                    textContent: el.textContent || '',
                    className: el.className,
                    ariaLabel: el.getAttribute('aria-label') || '',
                    visible: rect.width > 0 && rect.height > 0,
                    parentText: el.parentElement ? el.parentElement.textContent.slice(0, 100).trim() : ''
                };
            });
        }''')

        for idx, inp in enumerate(inputs_data):
            if inp["visible"]:
                print(f"[{idx}] TAG: {inp['tag']} | ID: '{inp['id']}' | TYPE: '{inp['type']}' | PLACEHOLDER: '{inp['placeholder']}' | CLASS: '{inp['className']}' | PARENT_TEXT: '{inp['parentText'][:50]}'")

        # Screenshot the form page
        os.makedirs("scratch", exist_ok=True)
        img_path = os.path.join("scratch", "hapag_form_inspect.png")
        html_path = os.path.join("scratch", "hapag_form_inspect.html")
        
        await connector.page.screenshot(path=img_path)
        print(f"\nScreenshot saved to: {img_path}")
        
        content = await connector.page.content()
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"HTML saved to: {html_path}")

    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(inspect())
