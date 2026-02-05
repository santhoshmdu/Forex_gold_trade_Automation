"""
Gold Trading RPA - Main Orchestrator
=====================================
Runs MT5 login + order placement and TradingView Fibonacci automation
in PARALLEL (two browser windows simultaneously).

Usage:
    python main.py              # Run both in parallel (TradingView + MT5 with orders)
    python main.py --tv-only    # Run only TradingView automation
    python main.py --mt5-only   # Run only MT5 login
    python main.py --sequential # Run one after another (old behavior)
"""

import sys
import threading
import queue
from playwright.sync_api import sync_playwright

from browser import setup_browser
from mt5_login import login_to_mt5
from mt5_orders import place_orders, select_gold_symbol
from chart_steps import (
    navigate_to_tradingview,
    load_symbol,
    set_timeframe,
    select_current_candle,
    select_fib_tool,
    draw_fibonacci,
    configure_fib_levels,
)
from price_extractor import extract_prices
from fib_calculator import calculate_fib_levels, print_fib_results, get_trade_levels
from utils import update_status


# Thread-safe print and shared data
print_lock = threading.Lock()
fib_levels_queue = queue.Queue()  # To pass levels from TV to MT5

def safe_print(msg):
    """Thread-safe printing."""
    with print_lock:
        print(msg)


def run_mt5_workflow(wait_for_levels=False):
    """
    MT5 Login + Order placement workflow.
    If wait_for_levels=True, waits for Fib levels from TradingView before placing orders.
    """
    safe_print("\n[MT5] Starting MT5 workflow...")
    
    with sync_playwright() as playwright:
        browser, context, page = setup_browser(playwright)
        
        try:    
            # Step 1: Login
            success = login_to_mt5(page)
            
            if not success:
                safe_print("[MT5] [FAIL] Login failed!")
                return False, "MT5 login failed"
            
            safe_print("[MT5] [OK] Login successful!")
            
            # Step 2: Select GOLD symbol
            select_gold_symbol(page)
            
            # Step 3: Wait for Fib levels if running in parallel
            if wait_for_levels:
                safe_print("[MT5] Waiting for Fib levels from TradingView...")
                try:
                    fib_levels = fib_levels_queue.get(timeout=120)  # Wait max 2 mins
                    safe_print("[MT5] [OK] Received Fib levels!")
                    
                    # Step 4: Place orders
                    buy_success, sell_success = place_orders(page, fib_levels)
                    
                except queue.Empty:
                    safe_print("[MT5] [FAIL] Timeout waiting for Fib levels!")
                    safe_print("[MT5] Browser will stay open for manual trading...")
            
            # Keep browser open
            safe_print("[MT5] Browser will stay open for trading...")
            page.pause()
            
            return True, "MT5 workflow complete"
            
        except Exception as e:
            safe_print(f"[MT5] [FAIL] Error: {e}")
            return False, str(e)


def run_tradingview_workflow(share_levels=False):
    """
    TradingView Fibonacci workflow.
    If share_levels=True, puts calculated levels in queue for MT5.
    """
    safe_print("\n[TV] Starting TradingView workflow...")
    
    with sync_playwright() as playwright:
        browser, context, page = setup_browser(playwright)
        
        try:
            safe_print("[TV] " + "="*50)
            safe_print("[TV] TRADINGVIEW FIBONACCI AUTOMATION")
            safe_print("[TV] " + "="*50)
            
            navigate_to_tradingview(page)      # Step 1
            load_symbol(page)                   # Step 2
            set_timeframe(page)                 # Step 3
            select_current_candle(page)         # Step 4
            high, low = extract_prices(page)    # Step 5
            select_fib_tool(page)               # Step 6
            draw_fibonacci(page)                # Step 7
            configure_fib_levels(page)          # Step 8
            
            # Step 9: Calculate and display results
            safe_print("\n[TV] [9/9] Calculating Fibonacci levels...")
            levels = calculate_fib_levels(high, low)
            print_fib_results(high, low, levels)
            
            # Share levels with MT5 if parallel mode
            if share_levels:
                fib_levels_queue.put(levels)
                safe_print("[TV] [OK] Sent Fib levels to MT5!")
            
            # Update overlay
            trade = get_trade_levels(levels)
            status = (f"COMPLETE\\nEntry: {trade['entry']:.2f}\\n"
                      f"Above(1.5): {trade['above']:.2f}\\n"
                      f"Below(-0.5): {trade['below']:.2f}")
            update_status(page, status, "")
            
            safe_print("[TV] [OK] TradingView workflow complete!")
            safe_print("[TV] Browser will stay open...")
            
            # Keep browser open
            page.pause()
            
            return True, levels
            
        except Exception as e:
            safe_print(f"[TV] [FAIL] Error: {e}")
            # Still put empty dict so MT5 doesn't hang
            if share_levels:
                fib_levels_queue.put({})
            return False, str(e)


def run_parallel():
    """Run MT5 and TradingView in PARALLEL with order placement."""
    print("="*60)
    print("     GOLD TRADING RPA - PARALLEL MODE")
    print("="*60)
    print("\nStarting TWO browser windows simultaneously:")
    print("  • Window 1: MT5 Web Terminal (Login + Orders)")
    print("  • Window 2: TradingView Fibonacci")
    print("\nWorkflow:")
    print("  1. Both start together")
    print("  2. TradingView calculates Fib levels")
    print("  3. Levels sent to MT5")
    print("  4. MT5 places Buy Stop + Sell Stop orders")
    print("="*60)
    
    # Create threads - MT5 waits for levels, TV shares levels
    mt5_thread = threading.Thread(
        target=run_mt5_workflow, 
        args=(True,),  # wait_for_levels=True
        name="MT5-Thread"
    )
    tv_thread = threading.Thread(
        target=run_tradingview_workflow,
        args=(True,),  # share_levels=True
        name="TV-Thread"
    )
    
    # Start both threads
    mt5_thread.start()
    tv_thread.start()
    
    print("\n[MAIN] Both workflows running in parallel...")
    print("[MAIN] TradingView will send Fib levels to MT5 for orders.")
    print("[MAIN] Close browsers manually when done.\n")
    
    # Wait for both to complete
    mt5_thread.join()
    tv_thread.join()
    
    print("\n" + "="*60)
    print("     ALL WORKFLOWS COMPLETE")
    print("="*60)


def run_sequential():
    """Run MT5 first, then TradingView, then place orders (single browser)."""
    print("="*60)
    print("     GOLD TRADING RPA - SEQUENTIAL MODE")
    print("="*60)
    
    with sync_playwright() as playwright:
        browser, context, page = setup_browser(playwright)
        
        try:
            # Phase 1: MT5 Login
            mt5_success = login_to_mt5(page)
            
            if mt5_success:
                print("\n[OK] MT5 login complete. Proceeding to TradingView...")
                input("\nPress Enter to continue to TradingView...")
            
            # Phase 2: TradingView
            navigate_to_tradingview(page)
            load_symbol(page)
            set_timeframe(page)
            select_current_candle(page)
            high, low = extract_prices(page)
            select_fib_tool(page)
            draw_fibonacci(page)
            configure_fib_levels(page)
            
            levels = calculate_fib_levels(high, low)
            print_fib_results(high, low, levels)
            
            trade = get_trade_levels(levels)
            status = (f"COMPLETE\\nEntry: {trade['entry']:.2f}\\n"
                      f"Above(1.5): {trade['above']:.2f}\\n"
                      f"Below(-0.5): {trade['below']:.2f}")
            update_status(page, status, "")
            
            # Phase 3: Go back to MT5 and place orders
            print("\n[MAIN] Press Enter to go back to MT5 and place orders...")
            input()
            
            page.goto("https://mt5-6.xm-bz.com/terminal")
            page.wait_for_load_state('networkidle')
            
            select_gold_symbol(page)
            place_orders(page, levels)
            
            print("\n* Automation complete. Browser will remain open.")
            page.pause()
            
        finally:
            browser.close()


def run_tradingview_only():
    """Run only TradingView automation."""
    print("="*60)
    print("TRADINGVIEW FIBONACCI (Standalone)")
    print("="*60)
    
    success, result = run_tradingview_workflow(share_levels=False)
    return success


def run_mt5_only():
    """Run only MT5 login (no orders)."""
    print("="*60)
    print("MT5 LOGIN (Standalone)")
    print("="*60)
    
    success, result = run_mt5_workflow(wait_for_levels=False)
    return success


def main():
    """Main entry point with command line argument handling."""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if "--tv-only" in args:
        run_tradingview_only()
    elif "--mt5-only" in args:
        run_mt5_only()
    elif "--sequential" in args:
        run_sequential()
    elif "--help" in args or "-h" in args:
        print(__doc__)
    else:
        # Default: run in parallel with order placement
        run_parallel()


if __name__ == "__main__":
    main()
