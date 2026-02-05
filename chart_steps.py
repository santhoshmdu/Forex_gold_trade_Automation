"""
TradingView chart interaction steps.
"""

from playwright.sync_api import Page
import time

from config import CONFIG
from utils import update_status, click_chart, create_status_overlay, get_viewport_center


def navigate_to_tradingview(page: Page) -> None:
    """Step 1: Navigate to TradingView and setup."""
    print("[1/9] Navigating to TradingView...")
    
    page.goto(CONFIG["tradingview_url"])
    page.wait_for_load_state('networkidle')
    time.sleep(CONFIG["delays"]["long"])
    
    # Accept cookies if present
    try:
        page.get_by_role("button", name="Accept").click(timeout=2000)
    except:
        pass
    
    create_status_overlay(page)


def load_symbol(page: Page) -> bool:
    """Step 2: Load the trading symbol."""
    symbol = CONFIG["symbol"]
    print(f"\n[2/9] Loading {symbol} symbol...")
    update_status(page, f"Loading {symbol}...", "Step 2/9")
    
    click_chart(page)
    time.sleep(CONFIG["delays"]["short"])
    
    page.keyboard.type(symbol, delay=100)
    time.sleep(1.5)
    page.keyboard.press("Enter")
    time.sleep(CONFIG["delays"]["page_load"])
    
    if symbol not in page.content():
        update_status(page, "ERROR: Symbol not loaded!", "Step 2/9")
        return False
    
    update_status(page, f"{symbol} loaded successfully!", "Step 2/9")
    click_chart(page)
    return True


def set_timeframe(page: Page) -> None:
    """Step 3: Set the chart timeframe."""
    tf = CONFIG["timeframe"]
    print(f"\n[3/9] Setting timeframe to {tf} minutes...")
    update_status(page, f"Changing to {tf}m timeframe...", "Step 3/9")
    
    click_chart(page)
    page.keyboard.press(",")
    time.sleep(CONFIG["delays"]["medium"])
    page.keyboard.type(tf, delay=100)
    time.sleep(CONFIG["delays"]["short"])
    page.keyboard.press("Enter")
    time.sleep(4)
    
    update_status(page, f"Timeframe set to {tf}m", "Step 3/9")


def select_current_candle(page: Page) -> bool:
    """
    Step 4: Select target candle for Fibonacci calculation.
    
    Default: Uses the CURRENT/ACTIVE candle (live candle at execution time)
    If use_current_candle is False: Navigates to the specific time in target_time
    """
    use_current = CONFIG.get("use_current_candle", True)  # Default to current candle
    
    if use_current:
        print(f"\n[4/9] Selecting CURRENT candle...")
        update_status(page, "Selecting current candle...", "Step 4/9")
        
        # Ensure chart is focused and scroll to latest
        click_chart(page)
        time.sleep(CONFIG["delays"]["short"])
        
        # Press End key to ensure we're at the latest candle
        page.keyboard.press("End")
        time.sleep(CONFIG["delays"]["medium"])
        
        update_status(page, "Current candle selected", "Step 4/9")
        print("  [OK] Current/active candle selected")
        return True
    
    # Alternative: Navigate to specific time (if use_current_candle is False)
    target = CONFIG["target_time"]
    print(f"\n[4/9] Navigating to {target} candle...")
    update_status(page, f"Jumping to {target}...", "Step 4/9")
    
    click_chart(page)
    page.keyboard.press("Alt+g")
    time.sleep(CONFIG["delays"]["long"])
    
    try:
        time_inputs = page.locator("input:visible").all()
        time_field = None
        
        for inp in time_inputs:
            if ":" in inp.input_value():
                time_field = inp
                break
        
        if not time_field:
            time_field = time_inputs[1] if len(time_inputs) >= 2 else time_inputs[0]
        
        time_field.click()
        time.sleep(CONFIG["delays"]["short"])
        page.keyboard.press("Control+a")
        time.sleep(0.3)
        page.keyboard.type(target, delay=100)
        time.sleep(CONFIG["delays"]["medium"])
        page.keyboard.press("Enter")
        time.sleep(CONFIG["delays"]["medium"])
        page.keyboard.press("Enter")
        time.sleep(4)
        
        update_status(page, f"Jumped to {target}", "Step 4/9")
        return True
        
    except Exception as e:
        update_status(page, "Time nav issue (continuing)", "Step 4/9")
        print(f"  Note: {str(e)[:50]}")
        return False


def select_fib_tool(page: Page) -> bool:
    """Step 6: Select Fibonacci Retracement tool."""
    print("\n[6/9] Selecting Fibonacci Retracement tool...")
    update_status(page, "Opening tool search...", "Step 6/9")
    
    # Method 1: '/' shortcut
    try:
        click_chart(page)
        page.keyboard.press("/")
        time.sleep(1.5)
        page.keyboard.type("Fib Retracement", delay=80)
        time.sleep(2)
        page.keyboard.press("Enter")
        time.sleep(1)
        update_status(page, "Fib tool selected!", "Step 6/9")
        return True
    except Exception as e:
        print(f"  Method 1 failed: {str(e)[:40]}")
    
    # Method 2: Ctrl+K
    try:
        click_chart(page)
        page.keyboard.press("Control+k")
        time.sleep(1.5)
        page.keyboard.type("Fib Retracement", delay=80)
        time.sleep(2)
        page.keyboard.press("Enter")
        time.sleep(1)
        update_status(page, "Fib tool selected (Ctrl+K)!", "Step 6/9")
        return True
    except Exception as e:
        print(f"  Method 2 failed: {str(e)[:40]}")
    
    # Method 3: Manual
    print("\n  *** MANUAL ACTION REQUIRED ***")
    print("  Please select 'Fib Retracement' tool from the left toolbar.")
    update_status(page, "SELECT FIB TOOL MANUALLY!", "Step 6/9")
    try:
        input("  Press Enter after selecting Fib tool: ")
        return True
    except:
        return False


def draw_fibonacci(page: Page) -> None:
    """Step 7: Draw Fibonacci on the chart."""
    print("\n[7/9] Drawing Fibonacci on candle...")
    update_status(page, "Drawing Fibonacci...", "Step 7/9")
    
    cx, cy = get_viewport_center(page)
    offset = 100
    
    page.mouse.move(cx, cy + offset)
    time.sleep(CONFIG["delays"]["short"])
    page.mouse.down()
    time.sleep(0.3)
    page.mouse.move(cx, cy - offset, steps=30)
    time.sleep(CONFIG["delays"]["short"])
    page.mouse.up()
    time.sleep(2)
    
    update_status(page, "Fib drawn on chart", "Step 7/9")


def configure_fib_levels(page: Page) -> bool:
    """
    Step 8: Configure Fibonacci levels in settings.
    
    NOTE: This step is OPTIONAL. It only adjusts which levels are visible
    on the chart. The calculations are done independently in step 9.
    
    Returns: True if configured successfully, False if skipped.
    """
    print("\n[8/9] Configuring Fibonacci levels (optional)...")
    update_status(page, "Opening settings...", "Step 8/9")
    
    cx, cy = get_viewport_center(page)
    
    # Try to select the Fib drawing
    page.mouse.click(cx, cy)
    time.sleep(1)
    
    # Double-click to open settings dialog
    page.mouse.dblclick(cx, cy)
    time.sleep(2.5)
    
    try:
        # Wait for settings dialog
        page.wait_for_selector("div[data-name='tab-content-style']", timeout=4000)
        update_status(page, "Configuring levels...", "Step 8/9")
        
        style_tab = page.locator("div[data-name='tab-content-style']")
        inputs = style_tab.locator("input[type='text']").all()
        checkboxes = style_tab.locator("input[type='checkbox']").all()
        
        desired = CONFIG["desired_fib_levels"]
        print(f"  Found {len(inputs)} level inputs")
        
        for i, inp in enumerate(inputs):
            level_val = inp.input_value().strip()
            should_enable = level_val in desired
            
            if i < len(checkboxes):
                is_enabled = checkboxes[i].is_checked()
                
                if should_enable and not is_enabled:
                    checkboxes[i].click()
                    print(f"  ✓ Enabled level {level_val}")
                elif not should_enable and is_enabled:
                    checkboxes[i].click()
                    print(f"  ✗ Disabled level {level_val}")
        
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(2)
        update_status(page, "Levels configured!", "Step 8/9")
        return True
        
    except Exception as e:
        # This step is optional - calculations work regardless
        print(f"  ⚠ Could not open settings dialog (this is OK)")
        print(f"  → You can manually configure levels later if needed")
        update_status(page, "Skipped (optional step)", "Step 8/9")
        
        # Press Escape to close any partial dialogs
        try:
            page.keyboard.press("Escape")
        except:
            pass
        
        return False
