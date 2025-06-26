import streamlit as st
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime, timedelta
import numpy as np

# Configure Streamlit
st.set_page_config(page_title="Treasury Yield Curve", layout="wide")
st.title("Treasury Yield Curve")

# Setup FRED
fred = Fred(api_key=st.secrets["fred_api_key"])

# Dates
today = datetime.today()
fallback_date = today - timedelta(days=1 if today.weekday() > 0 else 3)
today_str = today.strftime('%Y-%m-%d')
start_target = datetime(2025, 1, 1)
start_search_range = [start_target - timedelta(days=i) for i in range(5)]  # fallback up to 5 days before
end_str = fallback_date.strftime('%Y-%m-%d')

# Tickers
money_market_tickers = {
    "1 mo.": "DTB1", "2 mo.": "DTB2", "3 mo.": "DTB3", "4 mo.": "DTB4WK",
    "6 mo.": "DTB6", "1 yr.": "GS1"
}
capital_market_tickers = {
    "2 yr.": "GS2", "3 yr.": "GS3", "5 yr.": "GS5", "7 yr.": "GS7",
    "10 yr.": "GS10", "20 yr.": "GS20", "30 yr.": "GS30"
}

def find_latest_available(ticker, date_list):
    for date in date_list:
        try:
            series = fred.get_series(ticker, start_date=date.strftime('%Y-%m-%d'), end_date=date.strftime('%Y-%m-%d'))
            if not series.empty:
                return round(series.iloc[-1], 2)
        except:
            continue
    return np.nan

def get_yields(ticker_dict, date_ref_list):
    data = {}
    for label, code in ticker_dict.items():
        data[label] = find_latest_available(code, date_ref_list)
    return data

# Fetch data
start_dates = [d for d in start_search_range]
money_market_start = get_yields(money_market_tickers, start_dates)
money_market_current = get_yields(money_market_tickers, [fallback_date])
capital_market_start = get_yields(capital_market_tickers, start_dates)
capital_market_current = get_yields(capital_market_tickers, [fallback_date])

# Combine and clean for plotting
money_x = list(money_market_start.keys()) + ["2 yr."]
money_y_start = list(money_market_start.values()) + [capital_market_start.get("2 yr.")]
money_y_current = list(money_market_current.values()) + [capital_market_current.get("2 yr.")]

capital_x = ["1 yr."] + list(capital_market_start.keys())
capital_y_start = [money_market_start.get("1 yr.")] + list(capital_market_start.values())
capital_y_current = [money_market_current.get("1 yr.")] + list(capital_market_current.values())

# Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('black')

# Convert None to np.nan for safety
money_y_start = [np.nan if v is None else v for v in money_y_start]
money_y_current = [np.nan if v is None else v for v in money_y_current]
capital_y_start = [np.nan if v is None else v for v in capital_y_start]
capital_y_current = [np.nan if v is None else v for v in capital_y_current]

# Plot
ax.plot(money_x, money_y_start, color='skyblue', marker='o', label='Money Market Yield (01/01/2025 approx)')
ax.plot(money_x, money_y_current, color='blue', marker='o', label='Money Market Yield (Current)')
ax.plot(capital_x, capital_y_start, color='sandybrown', marker='s', label='Capital Market Yield (01/01/2025 approx)')
ax.plot(capital_x, capital_y_current, color='darkorange', marker='s', label='Capital Market Yield (Current)')

# Labels
ax.set_title("Treasury Yield Curve", fontsize=16, color='white')
ax.set_xlabel("Maturity (months - years)", fontsize=12, color='white')
ax.set_ylabel("Yield (%)", fontsize=12, color='white')
ax.tick_params(axis='x', colors='white', rotation=45)
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

# Display
st.pyplot(fig)
