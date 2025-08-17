import yfinance as yf
import pandas as pd

def screen_stocks(tickers):
    """
    Screens a list of stock tickers based on volume criteria.

    Args:
        tickers (list): A list of stock ticker symbols to screen.
    """
    print("Starting stock screening process...")

    screened_stocks = []

    for ticker in tickers:
        try:
            # Create a Ticker object
            stock = yf.Ticker(ticker)

            # Get historical data for the last 60 days
            hist = stock.history(period="60d")

            if hist.empty:
                print(f"No data found for {ticker}, skipping.")
                continue

            # Calculate 10-day and 30-day average volumes
            hist['avg_vol_10d'] = hist['Volume'].rolling(window=10).mean()
            hist['avg_vol_30d'] = hist['Volume'].rolling(window=30).mean()

            # Get the most recent data
            latest_data = hist.iloc[-1]
            latest_volume = latest_data['Volume']
            latest_close = latest_data['Close']
            avg_vol_10d = latest_data['avg_vol_10d']
            avg_vol_30d = latest_data['avg_vol_30d']

            # Check if the latest volume is at least 2x the 10-day or 30-day average
            volume_check_10d = latest_volume >= 2 * avg_vol_10d
            volume_check_30d = latest_volume >= 2 * avg_vol_30d

            if volume_check_10d or volume_check_30d:
                print(f"\n--- POTENTIAL OPPORTUNITY: {ticker} ---")
                print(f"  Last Close Price: ${latest_close:.2f}")
                print(f"  Latest Volume: {latest_volume:,.0f}")

                if volume_check_10d:
                    print(f"  10-Day Avg Volume: {avg_vol_10d:,.0f} (Volume is {latest_volume/avg_vol_10d:.2f}x average)")

                if volume_check_30d:
                    print(f"  30-Day Avg Volume: {avg_vol_30d:,.0f} (Volume is {latest_volume/avg_vol_30d:.2f}x average)")

                screened_stocks.append(ticker)

        except Exception as e:
            print(f"Could not process {ticker}. Reason: {e}")

    if not screened_stocks:
        print("\nNo stocks met the screening criteria.")
    else:
        print(f"\nScreening complete. Found {len(screened_stocks)} potential opportunities: {', '.join(screened_stocks)}")


if __name__ == "__main__":
    # List of tickers to screen.
    # Add US, Australian, or other market tickers here.
    # For example: ['AAPL', 'MSFT', 'GOOG', 'BHP.AX', 'CBA.AX']
    tickers_to_screen = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMD', 'GOOG', 'AMZN', 'META']

    screen_stocks(tickers_to_screen)
