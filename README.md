# Gold Trading RPA

Automated robotic process automation (RPA) tool for Gold (XAUUSD) trading. This project combines TradingView analysis with MetaTrader 5 (MT5) order execution, running both workflows in parallel.

## 🚀 Key Features

- **Parallel Execution:** Runs TradingView chart analysis and MT5 order placement simultaneously in two browser windows for faster execution.
- **TradingView Automation:**
  - Navigates to the XAUUSD chart.
  - Selects the 30-minute timeframe.
  - Identifies the High and Low of the current candle.
  - Draws Fibonacci retracement levels.
  - Calculates key levels (0, 0.5, 1, 1.5, -0.5).
- **MetaTrader 5 Automation:**
  - Logs deeply into the MT5 Web Terminal.
  - Selects the target symbol (`GOLD.i#`).
  - Places pending orders based on TradingView data:
    - **Buy Stop:** Entry @ High, SL @ 0.5 Fib, TP @ 1.5 Fib.
    - **Sell Stop:** Entry @ Low, SL @ 0.5 Fib, TP @ -0.5 Fib.
- **Configurable:** All settings (credentials, lot sizes, URLs) are managed centrally in `config.py`.

## 🛠️ Prerequisites

- Python 3.8+
- Google Chrome (or Chromium-based browser)
- MetaTrader 5 Account

## 📦 Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/santhoshmdu/Forex_gold_trade_Automation.git
    cd Forex_gold_trade_Automation
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers:**
    ```bash
    playwright install
    ```

## ⚙️ Configuration

Open `config.py` and update the following settings with your details:

```python
CONFIG = {
    # MT5 Credentials
    "mt5_login": "YOUR_LOGIN_ID",
    "mt5_password": "YOUR_PASSWORD",
    "mt5_symbol": "GOLD.i#",  # Update based on your broker's symbol name
    "mt5_lot_size": 0.01,

    # ... other settings
}
```

## ▶️ Usage

### Run Default (Parallel Mode)

Runs both TradingView analysis and MT5 order placement simultaneously. This is the recommended mode.

```bash
python main.py
```

### Run TradingView Only

Performs only the chart analysis without placing orders.

```bash
python main.py --tv-only
```

### Run MT5 Only

Logs into MT5 but does not place orders (useful for testing login).

```bash
python main.py --mt5-only
```

### Run Sequential Mode

Runs MT5 login first, then TradingView analysis, then returns to MT5 for order placement.

```bash
python main.py --sequential
```

## ⚠️ Disclaimer

This tool is for educational purposes only. Forex and Gold trading carry a high level of risk and may not be suitable for all investors. The authors are not responsible for any financial losses incurred while using this software. Use at your own risk.
