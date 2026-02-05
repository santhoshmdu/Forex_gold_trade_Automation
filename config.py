"""
Configuration settings for TradingView Fibonacci Automation.
"""

CONFIG = {
    # =========================================================================
    # MT5 WEB TERMINAL SETTINGS
    # =========================================================================
    "mt5_url": "https://mt5-6.xm-bz.com/terminal",
    "mt5_login": "309693342",
    "mt5_password": "Trade@1122",
    "mt5_symbol": "GOLD.i#",
    "mt5_lot_size": 0.01,
    
    # Order settings
    "buy_stop": {
        "type": "Buy Stop",
        "tp_level": "1.5",   # Take Profit at 1.5 (Above High)
        "sl_level": "0.5",   # Stop Loss at 0.5 (Entry)
    },
    "sell_stop": {
        "type": "Sell Stop",
        "tp_level": "-0.5",  # Take Profit at -0.5 (Below Low)
        "sl_level": "0.5",   # Stop Loss at 0.5 (Entry)
    },
    
    # =========================================================================
    # TRADINGVIEW SETTINGS
    # =========================================================================
    "tradingview_url": "https://www.tradingview.com/chart/",
    "symbol": "XAUUSD",
    "timeframe": "30",
    "use_current_candle": True,   # True = use current/latest candle, False = navigate to target_time
    "target_time": "05:30",       # Only used if use_current_candle is False
    
    # Fibonacci levels to enable
    "desired_fib_levels": {"0", "-0.5", "0.5", "1.5", "1"},
    
    # Valid gold price range for validation
    "gold_price_range": (2000, 8000),
    
    # =========================================================================
    # BROWSER SETTINGS
    # =========================================================================
    "browser_args": ["--start-maximized", "--force-device-scale-factor=0.85"],
    
    # Timing (in seconds)
    "delays": {
        "short": 0.5,
        "medium": 1.0,
        "long": 3.0,
        "page_load": 6.0,
    }
}
