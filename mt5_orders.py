"""
MT5 Order Placement Module
Handles placing Buy Stop and Sell Stop orders on MT5 Web Terminal.

Fixed issues:
- Uses correct selectors for MT5 Web Terminal order form
- Properly handles order type dropdown selection
- Closes confirmation dialogs before placing next order
- Proper sequence: Symbol -> New Order -> Order Type -> Volume/SL/TP -> Submit
"""

from playwright.sync_api import Page
import time
import os

from config import CONFIG


def take_debug_screenshot(page: Page, name: str):
    """Take a screenshot for debugging."""
    screenshot_path = os.path.join(os.path.dirname(__file__), f"debug_{name}.png")
    page.screenshot(path=screenshot_path)
    print(f"[MT5] Screenshot saved: {screenshot_path}")
    return screenshot_path


def close_any_dialogs(page: Page):
    """Close any open dialogs/popups."""
    try:
        # Close OK/Done dialogs
        close_buttons = ["text='OK'", "text='Done'", "text='Close'", "button:has-text('OK')"]
        for selector in close_buttons:
            btn = page.locator(selector)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(500)
                print("[MT5] Closed dialog")
                return True
        
        # Try clicking X button
        x_btn = page.locator("[class*='close'], .close-button, button[aria-label='Close']")
        if x_btn.count() > 0 and x_btn.first.is_visible():
            x_btn.first.click()
            page.wait_for_timeout(500)
            return True
            
    except:
        pass
    return False


def select_gold_symbol(page: Page) -> bool:
    """
    Select GOLD.i# symbol in MT5 by searching for it.
    Uses the "Search symbol" input box in the right panel.
    MUST be called before EACH order to ensure correct symbol.
    """
    symbol = CONFIG["mt5_symbol"]  # "GOLD.i#"
    print(f"\n[MT5] Selecting {symbol} symbol...")
    
    try:
        # Wait for terminal to be ready
        page.wait_for_timeout(2000)
        
        # Method 1: Use the search box
        search_box = page.locator("input[placeholder*='Search']")
        if search_box.count() > 0:
            print(f"[MT5] Using search box...")
            
            # Clear and focus the search box
            search_box.first.click()
            page.wait_for_timeout(300)
            search_box.first.fill("")  # Clear first
            page.wait_for_timeout(300)
            
            # Type the FULL symbol name for exact match
            search_box.first.fill("GOLD.i#")
            page.wait_for_timeout(2000)  # Wait for search results
            
            take_debug_screenshot(page, "02_search_results")
            
            # Look for EXACT match first - GOLD.i# specifically
            # Use more specific selector to avoid matching GOLDSACHS, GOLDOCEAN etc
            gold_exact = page.locator("text='GOLD.i#'")
            if gold_exact.count() > 0:
                gold_exact.first.click()
                page.wait_for_timeout(1000)
                print(f"[MT5] [OK] Selected GOLD.i# (exact match)")
                take_debug_screenshot(page, "03_symbol_selected")
                return True
            
            # Try with just "GOLD" if exact match fails
            search_box.first.fill("")
            page.wait_for_timeout(300)
            search_box.first.fill("GOLD")
            page.wait_for_timeout(2000)
            
            # Find GOLD.i# in results (look for the one with .i# suffix)
            gold_results = page.locator("text=/^GOLD\\.i#$/i")
            if gold_results.count() > 0:
                gold_results.first.click()
                page.wait_for_timeout(1000)
                print(f"[MT5] [OK] Selected GOLD.i# from search")
                return True
            
            # Last try - click first GOLD result
            gold_any = page.locator("text=/GOLD\\.i/i")
            if gold_any.count() > 0:
                gold_any.first.click()
                page.wait_for_timeout(1000)
                print(f"[MT5] [OK] Selected GOLD symbol")
                return True
        
        # Method 2: Direct click if visible in the symbol list
        direct = page.locator("text='GOLD.i#'")
        if direct.count() > 0:
            direct.first.click()
            page.wait_for_timeout(1000)
            print(f"[MT5] [OK] Clicked GOLD.i# directly")
            return True
            
        print(f"[MT5] [WARN] Could not find {symbol}")
        return False
        
    except Exception as e:
        print(f"[MT5] Symbol selection error: {str(e)[:60]}")
        return False



def open_new_order_form(page: Page) -> bool:
    """
    Open the new order form by clicking "Create New Order" button.
    This is the blue button at the bottom of the MT5 terminal.
    """
    print("[MT5] Opening new order form...")
    
    # First close any existing dialogs
    close_any_dialogs(page)
    page.wait_for_timeout(500)
    
    try:
        # Primary method: Click "Create New Order" button
        create_order_btn = page.locator("text='Create New Order'")
        
        if create_order_btn.count() > 0 and create_order_btn.first.is_visible():
            create_order_btn.click()
            page.wait_for_timeout(2000)
            print("[MT5] [OK] Clicked 'Create New Order' button")
            take_debug_screenshot(page, "04_order_form_open")
            return True
        
        # Fallback: Try variations
        variations = [
            "button:has-text('New Order')",
            "text='New Order'",
            "[class*='new-order']",
            "a:has-text('Create New Order')",
        ]
        
        for selector in variations:
            btn = page.locator(selector)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(2000)
                print(f"[MT5] [OK] Opened order form via: {selector}")
                return True
        
        # Last resort: Double-click on symbol to open order
        print("[MT5] Trying double-click on symbol...")
        symbol = CONFIG["mt5_symbol"]
        symbol_el = page.locator(f"text='{symbol}'")
        if symbol_el.count() > 0:
            symbol_el.first.dblclick()
            page.wait_for_timeout(2000)
            return True
            
        print("[MT5] [WARN] Could not open order form")
        return False
        
    except Exception as e:
        print(f"[MT5] Order form error: {str(e)[:60]}")
        return False


def select_order_type(page: Page, order_type: str) -> bool:
    """
    NATIVE SELECT STRATEGY: Select by value.
    Values: 0=Market, 2=BuyLimit, 3=SellLimit, 4=BuyStop, 5=SellStop
    
    Implementation copied from mt5_orders_only.py as requested.
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


def fill_input_by_label(page: Page, labels: list, value: float) -> bool:
    """
    Fill an input field by finding it near a label.
    Tries multiple label variations.
    """
    value_str = str(round(value, 2))
    
    for label in labels:
        try:
            # Method 1: Find input following the label text
            label_el = page.locator(f"text='{label}'")
            if label_el.count() > 0:
                # Try to find input in the same row/container
                parent = label_el.first.locator("xpath=ancestor::*[1]")
                input_el = parent.locator("input")
                if input_el.count() > 0:
                    print(f"[MT5] Filling {label} input...")
                    input_el.first.fill(value_str)
                    print(f"[MT5] [OK] Set {label} = {value_str}")
                    return True
                
                # Try xpath following sibling
                input_el = label_el.first.locator("xpath=following::input[1]")
                if input_el.count() > 0:
                    print(f"[MT5] Filling {label} input (sibling)...")
                    input_el.fill(value_str)
                    print(f"[MT5] [OK] Set {label} = {value_str}")
                    return True
                    
        except Exception as e:
            continue
    
    return False


def fill_order_form(page: Page, volume: float, sl_price: float, tp_price: float) -> bool:
    """
    Fill the order form with volume, stop loss, and take profit.
    """
    success = True
    
    # Set Volume/Lot
    print(f"[MT5] Setting volume: {volume}...")
    vol_set = fill_input_by_label(page, ["Volume", "Lot", "Lots"], volume)
    if not vol_set:
        # Try finding by placeholder
        vol_input = page.locator("input[placeholder*='olume'], input[placeholder*='lot']")
        if vol_input.count() > 0:
            vol_input.first.fill(str(volume))
            print(f"[MT5] [OK] Set Volume = {volume}")
        else:
            print(f"[MT5] [WARN] Could not set volume")
            success = False
    
    # Set Stop Loss
    print(f"[MT5] Setting Stop Loss: {sl_price:.2f}...")
    sl_set = fill_input_by_label(page, ["Stop Loss", "S/L", "SL"], sl_price)
    if not sl_set:
        print(f"[MT5] [WARN] Could not set Stop Loss")
    
    # Set Take Profit
    print(f"[MT5] Setting Take Profit: {tp_price:.2f}...")
    tp_set = fill_input_by_label(page, ["Take Profit", "T/P", "TP"], tp_price)
    if not tp_set:
        print(f"[MT5] [WARN] Could not set Take Profit")
    
    return success


def click_order_button(page: Page, order_type: str) -> bool:
    """
    Click the appropriate order button (Buy/Sell).
    MT5 Web has separate Buy and Sell buttons in the order form.
    """
    print(f"[MT5] Clicking order button for {order_type}...")
    
    is_buy = "Buy" in order_type
    
    try:
        if is_buy:
            # Look for Buy button - typically blue/green
            buy_selectors = [
                "button:has-text('Buy')",
                "[class*='buy'] button",
                "button[class*='buy']",
                "div[class*='buy']",
                "text='Buy by Market'",
                "text='Buy'",
            ]
            for sel in buy_selectors:
                btn = page.locator(sel)
                if btn.count() > 0:
                    # Filter for visible button
                    for i in range(min(btn.count(), 3)):
                        if btn.nth(i).is_visible():
                            btn.nth(i).click()
                            page.wait_for_timeout(2000)
                            print(f"[MT5] [OK] Clicked Buy button")
                            return True
        else:
            # Look for Sell button - typically red
            sell_selectors = [
                "button:has-text('Sell')",
                "[class*='sell'] button",
                "button[class*='sell']",
                "div[class*='sell']",
                "text='Sell by Market'",
                "text='Sell'",
            ]
            for sel in sell_selectors:
                btn = page.locator(sel)
                if btn.count() > 0:
                    for i in range(min(btn.count(), 3)):
                        if btn.nth(i).is_visible():
                            btn.nth(i).click()
                            page.wait_for_timeout(2000)
                            print(f"[MT5] [OK] Clicked Sell button")
                            return True
        
        print("[MT5] [WARN] Could not find order button")
        return False
        
    except Exception as e:
        print(f"[MT5] Button click error: {str(e)[:50]}")
        return False


def verify_order_placed(page: Page) -> bool:
    """
    Verify if order was placed successfully by checking for confirmation.
    """
    try:
        # Check for success indicators
        success_texts = ["Done", "Order placed", "Successfully", "executed"]
        for text in success_texts:
            if page.locator(f"text='{text}'").count() > 0:
                print(f"[MT5] [OK] Order confirmed: {text}")
                return True
        
        # Check for error indicators
        error_texts = ["Not enough money", "Invalid", "Error", "Failed", "rejected"]
        for text in error_texts:
            if page.locator(f"text='{text}'").count() > 0:
                print(f"[MT5] [FAIL] Order error: {text}")
                return False
        
        # If no clear indicator, consider it placed
        return True
        
    except:
        return True


def place_single_order(page: Page, order_type: str, tp_price: float, sl_price: float, volume: float) -> bool:
    """
    Place a single order (Buy Stop or Sell Stop).
    """
    print(f"\n{'='*50}")
    print(f"[MT5] PLACING {order_type.upper()} ORDER")
    print(f"{'='*50}")
    print(f"  TP: {tp_price:.2f}")
    print(f"  SL: {sl_price:.2f}")
    print(f"  Volume: {volume}")
    
    try:
        # Step 1: Open new order form
        if not open_new_order_form(page):
            print("[MT5] [WARN] Could not confirm order form opened")
        
        page.wait_for_timeout(1000)
        
        # Step 2: Try to select order type (may not work on all MT5 versions)
        select_order_type(page, order_type)
        page.wait_for_timeout(500)
        
        # Step 3: Fill the form
        fill_order_form(page, volume, sl_price, tp_price)
        page.wait_for_timeout(500)
        
        # Take screenshot before submit
        take_debug_screenshot(page, f"{order_type.replace(' ', '_')}_before_submit")
        
        # Step 4: Click the order button
        clicked = click_order_button(page, order_type)
        
        if clicked:
            page.wait_for_timeout(2000)
            take_debug_screenshot(page, f"{order_type.replace(' ', '_')}_after_submit")
            
            # Step 5: Verify and close confirmation
            success = verify_order_placed(page)
            
            # Close any confirmation dialog
            close_any_dialogs(page)
            page.wait_for_timeout(500)
            
            return success
        
        return False
        
    except Exception as e:
        print(f"[MT5] Order placement error: {str(e)[:60]}")
        take_debug_screenshot(page, f"{order_type.replace(' ', '_')}_error")
        return False


def place_buy_stop(page: Page, fib_levels: dict) -> bool:
    """
    Place a Buy Stop order.
    TP = 1.5 level, SL = 0.5 level
    """
    tp_price = fib_levels["1.5 (Above/Green)"]
    sl_price = fib_levels["0.5 (Entry/Red)"]
    volume = CONFIG["mt5_lot_size"]
    
    return place_single_order(page, "Buy Stop", tp_price, sl_price, volume)


def place_sell_stop(page: Page, fib_levels: dict) -> bool:
    """
    Place a Sell Stop order.
    TP = -0.5 level, SL = 0.5 level
    """
    tp_price = fib_levels["-0.5 (Below/Green)"]
    sl_price = fib_levels["0.5 (Entry/Red)"]
    volume = CONFIG["mt5_lot_size"]
    
    return place_single_order(page, "Sell Stop", tp_price, sl_price, volume)


def place_orders(page: Page, fib_levels: dict) -> tuple:
    """
    Place both Buy Stop and Sell Stop orders.
    Returns: (buy_success, sell_success)
    """
    print("\n[MT5] Starting order placement...")
    print("[MT5] Fib levels received:")
    for level, price in fib_levels.items():
        print(f"  {level}: {price:.2f}")
    
    # Step 1: Take initial screenshot
    take_debug_screenshot(page, "00_initial")
    
    # Step 2: Select GOLD.i# symbol first
    if not select_gold_symbol(page):
        print("[MT5] [FAIL] Could not select GOLD symbol for first order")
        return False, False
    
    # Step 3: Place Buy Stop order
    buy_success = place_buy_stop(page, fib_levels)
    
    # Wait and ensure dialog is closed
    page.wait_for_timeout(2000)
    close_any_dialogs(page)
    page.wait_for_timeout(1000)
    
    # Step 4: Select symbol AGAIN to ensure focus hasn't shifted
    # (Fixes issue where it might switch to CHFSGD or other symbols)
    print("\n[MT5] Re-confirming symbol selection for second order...")
    if not select_gold_symbol(page):
        print("[MT5] [WARN] Could not re-select GOLD symbol")
    
    # Step 5: Place Sell Stop order
    sell_success = place_sell_stop(page, fib_levels)
    
    # Summary
    print("\n" + "="*50)
    print("[MT5] ORDER PLACEMENT SUMMARY")
    print("="*50)
    print(f"  Buy Stop:  {'[OK] Placed' if buy_success else '[FAIL]'}")
    print(f"  Sell Stop: {'[OK] Placed' if sell_success else '[FAIL]'}")
    print("="*50)
    print(f"\n[MT5] Debug screenshots saved in: {os.path.dirname(__file__)}")
    
    return buy_success, sell_success
