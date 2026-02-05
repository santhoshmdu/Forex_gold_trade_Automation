"""
Fibonacci calculation functions.
Calculates Fibonacci levels from High/Low prices.
"""


def calculate_fib_levels(high_price: float, low_price: float) -> dict:
    """
    Calculate Fibonacci levels based on High and Low prices.
    
    User's convention (ascending from 0):
    - 1.5 = ABOVE High (highest price)
    - 1   = High (candle high)
    - 0.5 = Entry (midpoint)
    - 0   = Low (candle low)
    - -0.5 = BELOW Low (lowest price)
    
    Formula: Level = Low + (level_value × diff)
    
    Returns: dict of level names to prices
    """
    # Validate and swap if needed (ensure high > low)
    if high_price <= low_price:
        high_price, low_price = low_price, high_price
    
    diff = high_price - low_price
    
    # Calculate using formula: Level = Low + (level × diff)
    levels = {
        "1.5 (Above/Green)": low_price + (1.5 * diff),   # Above High
        "1 (High/Blue)": low_price + (1.0 * diff),       # = High
        "0.5 (Entry/Red)": low_price + (0.5 * diff),     # Midpoint
        "0 (Low/Blue)": low_price + (0.0 * diff),        # = Low
        "-0.5 (Below/Green)": low_price + (-0.5 * diff), # Below Low
    }
    
    return levels


def get_trade_levels(levels: dict) -> dict:
    """Extract just the trade-relevant levels."""
    return {
        "entry": levels["0.5 (Entry/Red)"],
        "above": levels["1.5 (Above/Green)"],
        "below": levels["-0.5 (Below/Green)"],
        "high": levels["1 (High/Blue)"],
        "low": levels["0 (Low/Blue)"],
    }


def print_fib_results(high_price: float, low_price: float, levels: dict) -> None:
    """Print formatted Fibonacci analysis results."""
    # Ensure high > low for display
    if high_price <= low_price:
        high_price, low_price = low_price, high_price
    
    diff = high_price - low_price
    
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
    
    # Display in correct order (highest price to lowest)
    ordered_levels = [
        ("1.5 (Above/Green)", levels["1.5 (Above/Green)"]),
        ("1 (High/Blue)", levels["1 (High/Blue)"]),
        ("0.5 (Entry/Red)", levels["0.5 (Entry/Red)"]),
        ("0 (Low/Blue)", levels["0 (Low/Blue)"]),
        ("-0.5 (Below/Green)", levels["-0.5 (Below/Green)"]),
    ]
    
    for name, price in ordered_levels:
        print(f"    {name}: {price:.2f}")
    
    trade = get_trade_levels(levels)
    print("\n  " + "-"*40)
    print("  TRADE LEVELS:")
    print("  " + "-"*40)
    print(f"    Entry (0.5):  {trade['entry']:.2f}")
    print(f"    Above (1.5):  {trade['above']:.2f}")
    print(f"    Below (-0.5): {trade['below']:.2f}")
    print("="*60)
