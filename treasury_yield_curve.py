import streamlit as st
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime, timedelta

# Configure Streamlit
st.set_page_config(page_title="Treasury Yield Curve", layout="wide")
st.title("Treasury Yield Curve")

# Setup FRED
fred = Fred(api_key=st.secrets["fred_api_key"])

# Dates
today = datetime.today()
fallback_date = today - timedelta(days=1 if today.weekday() > 0 else 3)
today_str = today.strftime('%Y-%m-%d')
start_str = '2024-12-31'
end_str = fallback_date.strftime('%Y-%m-%d')

# FRED tickers
money_market_tickers = {
    "1 mo.": "DTB1",
    "2 mo.": "DTB2",
    "3 mo.": "DTB3",
    "4 mo.": "DTB4WK",
    "6 mo.": "DTB6",
    "1 yr.": "GS1"
}
capital_market_tickers = {
    "2 yr.": "GS2",
    "3 yr.": "GS3",
    "5 yr.": "GS5",
    "7 yr.": "GS7",
    "10 yr.": "GS10",
    "20 yr.": "GS20",
    "30 yr.": "GS30"
}

def get_yields(ticker_dict, target_date):
    data = {}
    for label, code in ticker_dict.items():
        try:
            series = fred.get_series(code, start_date="2024-12-15", end_date=target_date)
            data[label] = round(series.dropna().iloc[-1], 2)
        except Exception:
            data[label] = None
    return data

# Get data
money_market_start = get_yields(money_market_tickers, start_str)
money_market_current = get_yields(money_market_tickers, end_str)
capital_market_start = get_yields(capital_market_tickers, start_str)
capital_market_current = get_yields(capital_market_tickers, end_str)

# Combine & filter missing data for plotting
def filter_valid_yields(x_labels, y_values):
    x_clean, y_clean = [], []
    for x, y in zip(x_labels, y_values):
        if y is not None:
            x_clean.append(x)
            y_clean.append(y)
    return x_clean, y_clean

# Merge 1 yr and 2 yr for continuity
money_x = list(money_market_start.keys()) + ["2 yr."]
money_y_start = list(money_market_start.values()) + [capital_market_start.get("2 yr.")]
money_y_current = list(money_market_current.values()) + [capital_market_current.get("2 yr.")]
money_x_start, money_y_start = filter_valid_yields(money_x, money_y_start)
money_x_current, money_y_current = filter_valid_yields(money_x, money_y_current)

capital_x = ["1 yr."] + list(capital_market_start.keys())
capital_y_start = [money_market_start.get("1 yr.")] + list(capital_market_start.values())
capital_y_current = [money_market_current.get("1 yr.")] + list(capital_market_current.values())
capital_x_start, capital_y_start = filter_valid_yields(capital_x, capital_y_start)
capital_x_current, capital_y_current = filter_valid_yields(capital_x, capital_y_current)

# Plotting
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('black')

# Plot money market
ax.plot(money_x_start, money_y_start, color='skyblue', marker='o', label='Money Market Yield (01/01/2025)')
ax.plot(money_x_current, money_y_current, color='blue', marker='o', label='Money Market Yield (Current)')

# Plot capital market
ax.plot(capital_x_start, capital_y_start, color='sandybrown', marker='s', label='Capital Market Yield (01/01/2025)')
ax.plot(capital_x_current, capital_y_current, color='darkorange', marker='s', label='Capital Market Yield (Current)')

# Labels
ax.set_title("Treasury Yield Curve", fontsize=16, color='white')
ax.set_xlabel("Maturity (months - years)", fontsize=12, color='white')
ax.set_ylabel("Yield (%)", fontsize=12, color='white')
ax.tick_params(axis='x', colors='white', rotation=45)
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()

# Show in Streamlit
st.pyplot(fig)
