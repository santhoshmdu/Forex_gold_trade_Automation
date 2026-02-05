
from playwright.sync_api import sync_playwright, Page
import time
import os
from mt5_login import login_to_mt5

# Hardcoded CONFIG for standalone test
CONFIG = {
    "mt5_symbol": "GOLD.i#",
    "mt5_lot_size": 0.01
}

# Sample Fib levels for testing
SAMPLE_LEVELS = {
    "0 (High/Blue)": 5560.00,
    "0.5 (Entry/Red)": 5550.00,
    "1 (Low/Blue)": 5540.00,
    "1.5 (Above/Green)": 5565.00,
    "-0.5 (Below/Green)": 5535.00,
}

# --- COPIED & MODIFIED HELPERS ---

def take_debug_screenshot(page: Page, name: str):
    screenshot_path = os.path.join(os.path.dirname(__file__), f"debug_TEST_{name}.png")
    page.screenshot(path=screenshot_path)
    print(f"[MT5-TEST] Saved: {screenshot_path}")

def close_any_dialogs(page: Page):
    try:
        close_buttons = ["text='OK'", "text='Done'", "text='Close'", "button:has-text('OK')"]
        for selector in close_buttons:
            if page.locator(selector).count() > 0:
                page.locator(selector).first.click()
                page.wait_for_timeout(500)
                return True
        x_btn = page.locator("[class*='close'], .close-button")
        if x_btn.count() > 0:
            x_btn.first.click()
            return True
    except:
        pass
    return False

def select_gold_symbol(page: Page) -> bool:
    print(f"\n[MT5] Selecting GOLD.i#...")
    try:
        page.wait_for_timeout(2000)
        search = page.locator("input[placeholder*='Search']")
        if search.count() > 0:
            search.first.click()
            search.first.fill("GOLD.i#")
            page.wait_for_timeout(2000)
            
            if page.locator("text='GOLD.i#'").count() > 0:
                page.locator("text='GOLD.i#'").first.click()
                print("[OK] Selected GOLD.i#")
                return True
        return False
    except Exception as e:
        print(f"Symbol Error: {e}")
        return False

def select_order_type(page: Page, order_type: str) -> bool:
    """
    NATIVE SELECT STRATEGY: Select by value.
    Values: 0=Market, 2=BuyLimit, 3=SellLimit, 4=BuyStop, 5=SellStop
    """
    print(f"[MT5] Selecting order type: {order_type}...")
    
    value_map = {
        "Market Execution": "0", "Buy Limit": "2", "Sell Limit": "3",
        "Buy Stop": "4", "Sell Stop": "5", "Buy Stop Limit": "6", "Sell Stop Limit": "7"
    }
    
    val = value_map.get(order_type)
    if not val:
        print(f"  [ERROR] Unknown order type: {order_type}")
        return False

    try:
        # Wait for dialog to settle
        page.wait_for_timeout(1500)
        
        # 1. Target the native <select> element
        select_locator = page.locator("select").first
        select_locator.wait_for(state="visible", timeout=5000)
        
        if select_locator.count() > 0:
            print(f"  [MT5] Selecting value '{val}' for '{order_type}'")
            select_locator.select_option(value=val)
            page.wait_for_timeout(1000)
            
            # Explicitly trigger change event
            select_locator.evaluate("el => el.dispatchEvent(new Event('change', { bubbles: true }))")
            page.wait_for_timeout(1000)
            
            # Verification
            header = select_locator.evaluate("el => el.options[el.selectedIndex].text")
            print(f"  [MT5] UI now shows selected text: {header}")
            
            if order_type.lower() in header.lower():
                print(f"[MT5] [OK] Successfully selected {order_type}")
                return True
        
        print(f"  [FAIL] Could not find <select> element or value '{val}'")
        return False
        
    except Exception as e:
        print(f"Type Error: {e}")
        return False

def fill_order_form(page, volume, sl, tp):
    print(f"[MT5] Filling Form: Vol={volume}, SL={sl}, TP={tp}")
    try:
        page.wait_for_timeout(500)
        # 1. Volume - look for input next to "Volume" text
        vol_label = page.locator("text='Volume'")
        if vol_label.count() > 0:
            # Try to find the input after the label
            vol_input = vol_label.first.locator("xpath=following::input[1]")
            if vol_input.count() > 0:
                print(f"  [MT5] Filling Volume: {volume}")
                vol_input.fill(str(volume))
            else:
                # Fallback
                page.locator("input[placeholder*='lot'], input[placeholder*='olume']").first.fill(str(volume))
            
        # 2. SL/TP - find siblings of labels
        for label, val in [("Stop Loss", sl), ("Take Profit", tp)]:
            lbl = page.locator(f"text='{label}'")
            if lbl.count() > 0:
                inp = lbl.first.locator("xpath=following::input[1]")
                if inp.count() > 0:
                    inp.fill(str(round(val, 2)))
    except Exception as e:
        print(f"Fill Error: {e}")

def click_submit(page, order_type):
    try:
        txt = "Buy" if "Buy" in order_type else "Sell"
        btn = page.locator(f"button:has-text('{txt}'), text='{txt} by Market'")
        if btn.count() > 0:
            btn.first.click()
            print(f"[OK] Clicked {txt}")
            return True
        return False
    except:
        return False

def run_order_test():
    print("="*60)
    print("MT5 ORDER PLACEMENT TEST (Standalone)")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized", "--force-device-scale-factor=0.85"]
        )
        context = browser.new_context(viewport=None)
        page = context.new_page()
        
        try:
            if not login_to_mt5(page):
                return
            
            if not select_gold_symbol(page):
                return
                
            # Place Buy Stop
            # 1. Open Form using F9 shortcut
            close_any_dialogs(page)
            print("[MT5] Opening New Order dialog (F9)...")
            page.keyboard.press("F9")
            page.wait_for_timeout(2000)
            
            # 2. Select Type
            if not select_order_type(page, "Buy Stop"):
                print("[MT5] [FAIL] Could not select Buy Stop")
                return
            
            # 3. Fill & Submit
            fill_order_form(page, 0.01, 5550.00, 5565.00)
            click_submit(page, "Buy Stop")
            page.wait_for_timeout(2000)
            close_any_dialogs(page)
            
            # Place Sell Stop
            select_gold_symbol(page) # Re-select
            print("[MT5] Opening New Order dialog (F9)...")
            page.keyboard.press("F9")
            page.wait_for_timeout(2000)
            
            if not select_order_type(page, "Sell Stop"):
                print("[MT5] [FAIL] Could not select Sell Stop")
                return
                
            fill_order_form(page, 0.01, 5550.00, 5535.00)
            click_submit(page, "Sell Stop")
            
            print("\nTest complete. Browser remaining open...")
            page.pause()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            page.pause()

if __name__ == "__main__":
    run_order_test()
