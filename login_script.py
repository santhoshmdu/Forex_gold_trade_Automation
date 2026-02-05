from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        # User requested 'chrome', trying to use Google Chrome if available, otherwise Chromium
        # To use system Chrome: channel="chrome"
        # If this fails, remove the channel argument to use Playwright's bundled Chromium
        try:
            browser = p.chromium.launch(headless=False, channel="chrome")
        except Exception as e:
            print(f"Could not launch Chrome (channel='chrome'): {e}")
            print("Falling back to bundled Chromium...")
            browser = p.chromium.launch(headless=False)
            
        page = browser.new_page()
        
        url = "https://mt5-6.xm-bz.com/terminal"
        print(f"Navigating to {url}...")
        page.goto(url)
        
        # Wait for the page to load and the login modal to appear
        # The modal usually appears automatically or after a specific button press.
        # We'll wait for the login input to be visible.
        print("Waiting for login form...")
        try:
            # Standard MT5 Web Terminal selectors (based on generic MetaQuotes WebTerminal structure)
            # Login Input
            page.wait_for_selector('input[name="login"]', timeout=30000)
            
            print("Filling credentials...")
            page.fill('input[name="login"]', '309693342')
            page.fill('input[name="password"]', 'Trade@1122')
            
            # Server Selection
            # Sometimes the server is a dropdown or an input.
            # Based on the URL 'mt5-6.xm-bz.com', generic server might be pre-selected.
            # If there's a server input, we might need to interact with it.
            # Let's check if the server matches.
            
            # Button to connect
            # Usually strict text like "Connect to account" or "OK" or "Login"
            # We'll try generic submit or specific button classes if known.
            # Common selector for MT5 web submit: button[type="submit"] OR specific class
            
            # Press Enter to submit (often works)
            page.press('input[name="password"]', 'Enter')
            print("Submitted login form...")
            
            # Alternative: Click the button explicitly if Enter doesn't work
            # page.click('button.submit_selector_here')

            # Wait for success indicator
            # e.g., removal of login form or appearance of 'Trade' tab / balance
            print("Waiting for login to complete...")
            time.sleep(10) # Simple wait for visual verification by user
            
            # Take a screenshot
            page.screenshot(path="login_result.png")
            print("Screenshot saved to login_result.png")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="login_error.png")
        
        print("Script finished. Browser will remain open for a few seconds...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    run()
