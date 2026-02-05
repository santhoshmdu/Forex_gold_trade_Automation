"""
Price extraction functions.
Extracts High/Low prices from TradingView chart.
"""

from playwright.sync_api import Page
import re
import time

from config import CONFIG
from utils import update_status, get_viewport_center


def extract_from_legend(page: Page) -> tuple:
    """
    Extract prices from the chart legend.
    Returns: (high_price, low_price) or (None, None) if failed.
    """
    try:
        page.wait_for_selector("div[data-name='legend']", timeout=3000)
        legend_text = page.locator("div[data-name='legend']").text_content()
        
        h_match = re.search(r'H\s*([\d,]+\.?\d*)', legend_text)
        l_match = re.search(r'L\s*([\d,]+\.?\d*)', legend_text)
        
        if h_match and l_match:
            high = float(h_match.group(1).replace(',', ''))
            low = float(l_match.group(1).replace(',', ''))
            return high, low
    except:
        pass
    return None, None


def extract_from_page_scan(page: Page) -> tuple:
    """
    Scan page content for price patterns.
    Returns: (high_price, low_price) or (None, None) if failed.
    """
    min_price, max_price = CONFIG["gold_price_range"]
    
    try:
        body_text = page.locator("body").inner_text()
        h_vals = re.findall(r'[Hh][\s:]([\d,]+\.\d+)', body_text)
        l_vals = re.findall(r'[Ll][\s:]([\d,]+\.\d+)', body_text)
        
        valid_h = [float(x.replace(',', '')) for x in h_vals 
                   if min_price < float(x.replace(',', '')) < max_price]
        valid_l = [float(x.replace(',', '')) for x in l_vals 
                   if min_price < float(x.replace(',', '')) < max_price]
        
        if valid_h and valid_l:
            return max(valid_h), min(valid_l)
    except:
        pass
    return None, None


def get_manual_input() -> tuple:
    """
    Prompt user for manual price input.
    Returns: (high_price, low_price)
    """
    print("\n" + "="*60)
    print("MANUAL INPUT REQUIRED")
    print("Could not automatically extract prices from chart.")
    print("Please look at the chart legend and enter the values.")
    print("="*60)
    
    try:
        high_input = input("Enter HIGH price (e.g., 2750.50): ").strip()
        low_input = input("Enter LOW price (e.g., 2740.00): ").strip()
        high = float(high_input.replace(',', ''))
        low = float(low_input.replace(',', ''))
        print(f"  Using manual values: H={high}, L={low}")
        return high, low
    except (ValueError, EOFError):
        print("  Invalid input. Using defaults: H=2750.00, L=2740.00")
        return 2750.00, 2740.00


def extract_prices(page: Page) -> tuple:
    """
    Main function to extract High/Low prices.
    Tries multiple methods with fallbacks.
    Returns: (high_price, low_price)
    """
    print("\n[5/9] Reading candle High/Low prices...")
    update_status(page, "Reading candle data...", "Step 5/9")
    
    cx, cy = get_viewport_center(page)
    page.mouse.move(cx, cy)
    time.sleep(3)
    
    # Try legend extraction
    high, low = extract_from_legend(page)
    if high and low:
        update_status(page, f"Found H={high} L={low}", "Step 5/9")
        return high, low
    
    # Try page scan
    high, low = extract_from_page_scan(page)
    if high and low:
        update_status(page, f"Scanned H={high} L={low}", "Step 5/9")
        return high, low
    
    # Fall back to manual input
    update_status(page, "Auto-extraction failed. Check console.", "Step 5/9")
    high, low = get_manual_input()
    update_status(page, f"Manual H={high} L={low}", "Step 5/9")
    return high, low
