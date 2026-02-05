"""
TradingView XAUUSD Fibonacci Automation
========================================
Automates the process of drawing Fibonacci retracement on TradingView
for the XAUUSD trading pair.

Steps:
1. Open TradingView chart
2. Load XAUUSD symbol
3. Set 30-minute timeframe
4. Select current/active candle
5. Extract High/Low prices
6. Select Fibonacci tool
7. Draw Fibonacci on chart
8. Configure Fibonacci levels
9. Calculate and display trade levels
"""

from playwright.sync_api import sync_playwright, Page
import time
import re


# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG = {
    "symbol": "XAUUSD",
    "timeframe": "30",
    "use_current_candle": False,   # True = use current candle, False = navigate to target_time
    "target_time": "05:30",       # Only used if use_current_candle is False
    "url": "https://www.tradingview.com/chart/",
    "desired_fib_levels": {"0", "-0.5", "0.5", "1.5", "1"},
    "gold_price_range": (2000, 8000),  # Valid price range for gold
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_status_overlay(page: Page) -> None:
    """Create an on-screen status overlay for visual feedback."""
    page.evaluate("""
        const box = document.createElement('div');
        box.id = 'rpa-status';
        box.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 15px 20px;
            background: rgba(0, 0, 0, 0.9);
            color: #00ff00;
            z-index: 99999;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            border-radius: 8px;
            border: 2px solid #00ff00;
            box-shadow: 0 0 15px rgba(0,255,0,0.3);
            min-width: 300px;
        `;
        box.innerText = 'RPA Automation Starting...';
        document.body.appendChild(box);
    """)


def update_status(page: Page, msg: str, step: str = "") -> None:
    """Update the on-screen status overlay and print to console."""
    safe_msg = str(msg).replace("'", "\\'").replace('"', '\\"').replace('\n', '\\n')
    if step:
        safe_msg = f"{step}\\n{safe_msg}"
    try:
        page.evaluate(f"document.getElementById('rpa-status').innerText = '{safe_msg}';")
    except:
        pass
    print(f"  {msg}")


def get_viewport_center(page: Page) -> tuple:
    """Get the center coordinates of the viewport."""
    viewport = page.viewport_size or {"width": 1920, "height": 1080}
    return viewport['width'] // 2, viewport['height'] // 2


def click_chart(page: Page, x: int = 500, y: int = 400) -> None:
    """Click on the chart to ensure focus."""
    page.mouse.click(x, y)
    time.sleep(0.5)


# =============================================================================
# STEP FUNCTIONS
# =============================================================================

def step1_navigate_to_tradingview(page: Page) -> None:
    """Step 1: Navigate to TradingView and accept cookies."""
    print("[1/9] Navigating to TradingView...")
    
    page.goto(CONFIG["url"])
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Accept cookies if present
    try:
        page.get_by_role("button", name="Accept").click(timeout=2000)
    except:
        pass
    
    create_status_overlay(page)


def step2_load_symbol(page: Page) -> bool:
    """Step 2: Load XAUUSD symbol."""
    print(f"\n[2/9] Loading {CONFIG['symbol']} symbol...")
    update_status(page, f"Loading {CONFIG['symbol']}...", "Step 2/9")
    
    click_chart(page)
    time.sleep(0.5)
    
    page.keyboard.type(CONFIG["symbol"], delay=100)
    time.sleep(1.5)
    page.keyboard.press("Enter")
    time.sleep(6)
    
    # Verify symbol loaded
    if CONFIG["symbol"] not in page.content():
        update_status(page, "ERROR: Symbol not loaded!", "Step 2/9")
        print("  WARNING: Symbol may not have loaded correctly")
        return False
    
    update_status(page, f"{CONFIG['symbol']} loaded successfully!", "Step 2/9")
    click_chart(page)
    return True


def step3_set_timeframe(page: Page) -> None:
    """Step 3: Set timeframe to 30 minutes."""
    print(f"\n[3/9] Setting timeframe to {CONFIG['timeframe']} minutes...")
    update_status(page, f"Changing to {CONFIG['timeframe']}m timeframe...", "Step 3/9")
    
    click_chart(page)
    page.keyboard.press(",")
    time.sleep(1)
    page.keyboard.type(CONFIG["timeframe"], delay=100)
    time.sleep(0.5)
    page.keyboard.press("Enter")
    time.sleep(4)
    
    update_status(page, f"Timeframe set to {CONFIG['timeframe']}m", "Step 3/9")


def step4_select_current_candle(page: Page) -> bool:
    """
    Step 4: Select target candle for Fibonacci calculation.
    
    Default: Uses the CURRENT/ACTIVE candle (live candle at execution time)
    If use_current_candle is False: Navigates to the specific time in target_time
    """
    use_current = CONFIG.get("use_current_candle", True)
    
    if use_current:
        print(f"\n[4/9] Selecting CURRENT candle...")
        update_status(page, "Selecting current candle...", "Step 4/9")
        
        click_chart(page)
        time.sleep(0.5)
        
        # Press End key to ensure we're at the latest candle
        page.keyboard.press("End")
        time.sleep(1)
        
        update_status(page, "Current candle selected", "Step 4/9")
        print("  [OK] Current/active candle selected")
        return True
    
    # Alternative: Navigate to specific time
    print(f"\n[4/9] Navigating to {CONFIG['target_time']} candle...")
    update_status(page, f"Jumping to {CONFIG['target_time']}...", "Step 4/9")
    
    click_chart(page)
    page.keyboard.press("Alt+g")
    time.sleep(3)
    
    try:
        # Find time input field
        time_inputs = page.locator("input:visible").all()
        time_field = None
        
        for inp in time_inputs:
            if ":" in inp.input_value():
                time_field = inp
                break
        
        if not time_field:
            time_field = time_inputs[1] if len(time_inputs) >= 2 else time_inputs[0]
        
        time_field.click()
        time.sleep(0.5)
        page.keyboard.press("Control+a")
        time.sleep(0.3)
        page.keyboard.type(CONFIG["target_time"], delay=100)
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(4)
        
        update_status(page, f"Jumped to {CONFIG['target_time']}", "Step 4/9")
        return True
        
    except Exception as e:
        update_status(page, "Time nav issue (continuing)", "Step 4/9")
        print(f"  Note: {str(e)[:50]}")
        return False


def step5_extract_prices(page: Page) -> tuple:
    """Step 5: Extract High/Low prices from the chart."""
    print("\n[5/9] Reading candle High/Low prices...")
    update_status(page, "Reading candle data...", "Step 5/9")
    
    cx, cy = get_viewport_center(page)
    page.mouse.move(cx, cy)
    time.sleep(3)
    
    high_price, low_price = None, None
    min_price, max_price = CONFIG["gold_price_range"]
    
    # Method 1: Try legend text
    try:
        page.wait_for_selector("div[data-name='legend']", timeout=3000)
        legend_text = page.locator("div[data-name='legend']").text_content()
        
        h_match = re.search(r'H\s*([\d,]+\.?\d*)', legend_text)
        l_match = re.search(r'L\s*([\d,]+\.?\d*)', legend_text)
        
        if h_match and l_match:
            high_price = float(h_match.group(1).replace(',', ''))
            low_price = float(l_match.group(1).replace(',', ''))
            update_status(page, f"Found H={high_price} L={low_price}", "Step 5/9")
            return high_price, low_price
    except:
        pass
    
    # Method 2: Scan page content
    try:
        body_text = page.locator("body").inner_text()
        h_vals = re.findall(r'[Hh][\s:]([\d,]+\.\d+)', body_text)
        l_vals = re.findall(r'[Ll][\s:]([\d,]+\.\d+)', body_text)
        
        valid_h = [float(x.replace(',', '')) for x in h_vals 
                   if min_price < float(x.replace(',', '')) < max_price]
        valid_l = [float(x.replace(',', '')) for x in l_vals 
                   if min_price < float(x.replace(',', '')) < max_price]
        
        if valid_h and valid_l:
            high_price = max(valid_h)
            low_price = min(valid_l)
            update_status(page, f"Scanned H={high_price} L={low_price}", "Step 5/9")
            return high_price, low_price
    except:
        pass
    
    # Method 3: Manual input
    update_status(page, "Auto-extraction failed. Check console.", "Step 5/9")
    print("\n" + "="*60)
    print("MANUAL INPUT REQUIRED")
    print("Could not automatically extract prices from chart.")
    print("Please look at the chart legend and enter the values.")
    print("="*60)
    
    try:
        high_input = input("Enter HIGH price (e.g., 2750.50): ").strip()
        low_input = input("Enter LOW price (e.g., 2740.00): ").strip()
        high_price = float(high_input.replace(',', ''))
        low_price = float(low_input.replace(',', ''))
        print(f"  Using manual values: H={high_price}, L={low_price}")
        update_status(page, f"Manual H={high_price} L={low_price}", "Step 5/9")
    except (ValueError, EOFError):
        print("  Invalid input. Using defaults: H=2750.00, L=2740.00")
        high_price, low_price = 2750.00, 2740.00
        update_status(page, f"Default H={high_price} L={low_price}", "Step 5/9")
    
    return high_price, low_price


def step6_select_fib_tool(page: Page) -> bool:
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
    
    # Method 2: Ctrl+K shortcut
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
    
    # Method 3: Manual selection
    print("\n  *** MANUAL ACTION REQUIRED ***")
    print("  Please select 'Fib Retracement' tool from the left toolbar manually.")
    update_status(page, "SELECT FIB TOOL MANUALLY!", "Step 6/9")
    try:
        input("  Press Enter after selecting Fib tool: ")
        return True
    except:
        return False


def step7_draw_fibonacci(page: Page) -> None:
    """Step 7: Draw Fibonacci on the chart."""
    print("\n[7/9] Drawing Fibonacci on candle...")
    update_status(page, "Drawing Fibonacci...", "Step 7/9")
    
    cx, cy = get_viewport_center(page)
    offset = 100
    
    # Draw from bottom to top
    page.mouse.move(cx, cy + offset)
    time.sleep(0.5)
    page.mouse.down()
    time.sleep(0.3)
    page.mouse.move(cx, cy - offset, steps=30)
    time.sleep(0.5)
    page.mouse.up()
    time.sleep(2)
    
    update_status(page, "Fib drawn on chart", "Step 7/9")


def step8_configure_levels(page: Page) -> None:
    """Step 8: Configure Fibonacci levels."""
    print("\n[8/9] Configuring Fibonacci levels...")
    update_status(page, "Opening settings...", "Step 8/9")
    
    cx, cy = get_viewport_center(page)
    page.mouse.click(cx, cy)
    time.sleep(1)
    page.mouse.dblclick(cx, cy)
    time.sleep(2.5)
    
    try:
        page.wait_for_selector("div[data-name='tab-content-style']", timeout=6000)
        update_status(page, "Configuring levels...", "Step 8/9")
        
        style_tab = page.locator("div[data-name='tab-content-style']")
        inputs = style_tab.locator("input[type='text']").all()
        checkboxes = style_tab.locator("input[type='checkbox']").all()
        
        print(f"  Found {len(inputs)} level inputs")
        
        for i, inp in enumerate(inputs):
            level_val = inp.input_value().strip()
            should_enable = level_val in CONFIG["desired_fib_levels"]
            
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
        
    except Exception as e:
        update_status(page, "Settings error (check manually)", "Step 8/9")
        print(f"  Settings config error: {str(e)[:60]}")


def step9_calculate_levels(page: Page, high_price: float, low_price: float) -> dict:
    """Step 9: Calculate and display Fibonacci levels."""
    print("\n[9/9] Calculating Fibonacci levels...")
    
    # Validate prices
    if high_price is None or low_price is None:
        print("  ERROR: Price values missing, using defaults.")
        high_price, low_price = 2750.00, 2740.00
    
    # Ensure high > low
    if high_price <= low_price:
        print(f"  WARNING: Invalid range. Swapping H={high_price}, L={low_price}")
        high_price, low_price = low_price, high_price
    
    diff = high_price - low_price
    
    # Calculate levels (user's convention: 1=High, 0=Low)
    levels = {
        "1 (High/Blue)": high_price,
        "0.5 (Entry/Red)": high_price - (0.5 * diff),
        "0 (Low/Blue)": low_price,
        "1.5 (Above/Green)": high_price + (0.5 * diff),
        "-0.5 (Below/Green)": low_price - (0.5 * diff),
    }
    
    # Display results
    print("\n" + "="*60)
    print("         FIBONACCI ANALYSIS COMPLETE")
    print("="*60)
    print(f"\n  Candle Data:")
    print(f"    HIGH:  {high_price:.2f}")
    print(f"    LOW:   {low_price:.2f}")
    print(f"    Range: {diff:.2f}")
    print("\n  " + "-"*40)
    print("  FIBONACCI LEVELS (High to Low):")
    print("  " + "-"*40)
    
    for name, price in sorted(levels.items(), key=lambda x: x[1], reverse=True):
        print(f"    {name}: {price:.2f}")
    
    print("\n  " + "-"*40)
    print("  TRADE LEVELS:")
    print("  " + "-"*40)
    print(f"    Entry (0.5):  {levels['0.5 (Entry/Red)']:.2f}")
    print(f"    Above (1.5):  {levels['1.5 (Above/Green)']:.2f}")
    print(f"    Below (-0.5): {levels['-0.5 (Below/Green)']:.2f}")
    print("="*60)
    
    # Update overlay
    try:
        status = (f"COMPLETE\\nEntry: {levels['0.5 (Entry/Red)']:.2f}\\n"
                  f"Above(1.5): {levels['1.5 (Above/Green)']:.2f}\\n"
                  f"Below(-0.5): {levels['-0.5 (Below/Green)']:.2f}")
        update_status(page, status, "")
    except:
        pass
    
    return levels


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def run():
    """Main function to run the TradingView Fibonacci automation."""
    print("="*60)
    print("TradingView XAUUSD Fibonacci Automation")
    print("="*60)
    
    with sync_playwright() as p:
        # Launch browser
        try:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome",
                args=["--start-maximized", "--force-device-scale-factor=0.85"]
            )
        except:
            browser = p.chromium.launch(
                headless=False,
                args=["--start-maximized", "--force-device-scale-factor=0.85"]
            )
        
        context = browser.new_context(viewport=None)
        page = context.new_page()
        
        # Execute steps
        step1_navigate_to_tradingview(page)
        step2_load_symbol(page)
        step3_set_timeframe(page)
        step4_select_current_candle(page)
        high_price, low_price = step5_extract_prices(page)
        step6_select_fib_tool(page)
        step7_draw_fibonacci(page)
        step8_configure_levels(page)
        step9_calculate_levels(page, high_price, low_price)
        
        print("\n* Automation complete. Browser will remain open.")
        print("  Press Ctrl+C to exit or close browser manually.\n")
        
        # Keep browser open for inspection
        page.pause()


if __name__ == "__main__":
    run()
