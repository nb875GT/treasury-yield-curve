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
start_str = '2024-12-31'  # Use 12/31 data as surrogate for 01/01

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

# Function to get most recent yield as of given date
def get_yields(ticker_dict, target_date):
    data = {}
    for label, code in ticker_dict.items():
        try:
            series = fred.get_series(code, start_date="2024-12-15", end_date=target_date)
            data[label] = round(series.dropna().iloc[-1], 2)
        except:
            data[label] = None
    return data

# Get yield data
money_market_start = get_yields(money_market_tickers, start_str)
money_market_current = get_yields(money_market_tickers, fallback_date.strftime('%Y-%m-%d'))
capital_market_start = get_yields(capital_market_tickers, start_str)
capital_market_current = get_yields(capital_market_tickers, fallback_date.strftime('%Y-%m-%d'))

# Merge points between short and long end
money_x = list(money_market_start.keys()) + ["2 yr."]
money_y_start = list(money_market_start.values()) + [capital_market_start.get("2 yr.")]
money_y_current = list(money_market_current.values()) + [capital_market_current.get("2 yr.")]

capital_x = ["1 yr."] + list(capital_market_start.keys())
capital_y_start = [money_market_start.get("1 yr.")] + list(capital_market_start.values())
capital_y_current = [money_market_current.get("1 yr.")] + list(capital_market_current.values())

# Plot with updated aesthetics
plt.style.use('dark_background')
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
ax.set_facecolor('black')

# Plot lines
ax.plot(money_x, money_y_start, label='Money Market Yield (01/01/2025)', color='skyblue', marker='o', linewidth=2)
ax.plot(money_x, money_y_current, label='Money Market Yield (Current)', color='blue', marker='o', linewidth=2)
ax.plot(capital_x, capital_y_start, label='Capital Market Yield (01/01/2025)', color='sandybrown', marker='s', linewidth=2)
ax.plot(capital_x, capital_y_current, label='Capital Market Yield (Current)', color='darkorange', marker='s', linewidth=2)

# Formatting
ax.set_title("Treasury Yield Curve", fontsize=20, color='white')
ax.set_xlabel("Maturity (months - years)", fontsize=14, color='white')
ax.set_ylabel("Yield (%)", fontsize=14, color='white')
ax.tick_params(axis='x', colors='white', labelrotation=45)
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.3)
ax.legend(loc='upper left', fontsize=10)

# Display
st.pyplot(fig)

