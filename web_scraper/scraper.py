import yfinance as yf
import pandas as pd
import pandas_ta as ta

def screen_stocks(stock_list):
    """
    Screens a list of stocks based on a specific trading strategy.

    The strategy identifies stocks in a consolidation phase after a
    significant volume event, with different liquidity rules for US and ASX markets.

    Args:
        stock_list (list): A list of dictionaries, where each dictionary
                           contains a 'ticker' and 'market' ('US' or 'ASX').
    """
    print("--- Starting Market Screening ---")

    liquidity_rules = {
        'US': 1000000,
        'ASX': 300000
    }

    opportunities_found = 0

    for stock_info in stock_list:
        ticker = stock_info['ticker']
        market = stock_info['market']

        try:
            stock = yf.Ticker(ticker)

            # --- 1. Liquidity Check (Daily Data) ---
            daily_data = stock.history(period="5d", interval="1d")
            if daily_data.empty:
                print(f"\n[{ticker}] Could not retrieve daily data. Skipping.")
                continue

            latest_daily_volume = daily_data['Volume'].iloc[-1]
            liquidity_threshold = liquidity_rules.get(market, 0)

            if latest_daily_volume < liquidity_threshold:
                print(f"\n[{ticker}] Skipped: Fails daily volume liquidity check.")
                print(f"  - Daily Volume: {latest_daily_volume:,.0f}")
                print(f"  - Required: > {liquidity_threshold:,.0f}")
                continue

            # --- 2. Indicator Analysis (Hourly Data) ---
            # Fetch ~7 days of hourly data to ensure enough periods for indicators
            hourly_data = stock.history(period="7d", interval="60m")
            if hourly_data.empty:
                print(f"\n[{ticker}] Could not retrieve hourly data. Skipping.")
                continue

            # Calculate RSI
            hourly_data.ta.rsi(length=14, append=True)

            # Calculate Relative Volume (RVOL)
            hourly_data['avg_vol_20h'] = hourly_data['Volume'].rolling(window=20).mean()

            # Get the latest full hour's data
            latest_hour = hourly_data.iloc[-2] # Use -2 to get the last completed hour

            latest_rsi = latest_hour['RSI_14']
            latest_volume = latest_hour['Volume']
            avg_volume_20h = latest_hour['avg_vol_20h']

            if avg_volume_20h == 0: # Avoid division by zero
                rvol = float('inf')
            else:
                rvol = latest_volume / avg_volume_20h

            # --- 3. Final Check ---
            rsi_condition = latest_rsi < 60
            rvol_condition = rvol > 2

            print(f"\n[{ticker}] Analyzing...")
            print(f"  - Daily Volume: {latest_daily_volume:,.0f} (Passes > {liquidity_threshold:,.0f})")
            print(f"  - Hourly RSI(14): {latest_rsi:.2f} (Condition: < 60)")
            print(f"  - Hourly RVOL(20): {rvol:.2f} (Condition: > 2)")

            if rsi_condition and rvol_condition:
                opportunities_found += 1
                print(f"  *** SUCCESS: POTENTIAL OPPORTUNITY FOUND FOR {ticker} ***")
            else:
                print(f"  - Skipped: Did not meet all indicator conditions.")

        except Exception as e:
            print(f"\n[{ticker}] An error occurred: {e}")

    print(f"\n--- Screening Complete: Found {opportunities_found} potential opportunities. ---")


if __name__ == "__main__":
    # Define the list of stocks to screen
    stocks_to_screen = [
        # US Stocks
        {'ticker': 'AAPL', 'market': 'US'},
        {'ticker': 'TSLA', 'market': 'US'},
        {'ticker': 'NVDA', 'market': 'US'},
        {'ticker': 'GME', 'market': 'US'}, # Known for volatility

        # ASX Stocks
        {'ticker': 'CBA.AX', 'market': 'ASX'},
        {'ticker': 'BHP.AX', 'market': 'ASX'},
        {'ticker': 'FMG.AX', 'market': 'ASX'},
    ]

    screen_stocks(stocks_to_screen)
