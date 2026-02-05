"""
MT5 Web Terminal login module.
Handles authentication to MT5 trading platform.
"""

from playwright.sync_api import Page
import time

from config import CONFIG
from utils import update_status, create_status_overlay


def login_to_mt5(page: Page) -> bool:
    """
    Login to MT5 Web Terminal.
    
    Returns: True if login successful, False otherwise.
    """
    url = CONFIG["mt5_url"]
    login = CONFIG["mt5_login"]
    password = CONFIG["mt5_password"]
    
    print("\n" + "="*60)
    print("MT5 WEB TERMINAL LOGIN")
    print("="*60)
    
    print(f"\n[MT5] Navigating to {url}...")
    page.goto(url)
    
    try:
        # Wait for login form
        print("[MT5] Waiting for login form...")
        page.wait_for_selector('input[name="login"]', timeout=30000)
        
        # Fill credentials
        print("[MT5] Filling credentials...")
        page.fill('input[name="login"]', login)
        page.fill('input[name="password"]', password)
        
        # Submit form
        page.press('input[name="password"]', 'Enter')
        print("[MT5] Submitted login form...")
        
        # Wait for login to complete
        print("[MT5] Waiting for login to complete...")
        time.sleep(10)
        
        # Take verification screenshot
        page.screenshot(path="login_result.png")
        print("[MT5] Screenshot saved to login_result.png")
        print("[MT5] [OK] Login completed!")
        
        return True
        
    except Exception as e:
        print(f"[MT5] [FAIL] Login error: {e}")
        page.screenshot(path="login_error.png")
        return False


def is_mt5_logged_in(page: Page) -> bool:
    """Check if already logged into MT5."""
    try:
        # If login form is not visible, we might be logged in
        page.wait_for_selector('input[name="login"]', timeout=3000)
        return False  # Login form visible = not logged in
    except:
        return True  # No login form = probably logged in
