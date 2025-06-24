import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from tiingo import TiingoClient

# Tiingo API configuration
config = {
    'session': True,
    'api_key': '87ea448a4e01f7ee751f5ea680ce9a25e10b18a9'  # Replace with your actual API key
}
client = TiingoClient(config)

# Set Streamlit page config
st.set_page_config(page_title="TLT Monthly Return Clustering", layout="wide", initial_sidebar_state="auto")

# Title
st.title("K-Means Clustering of TLT Monthly Returns")

# Date range setup
start_date = '2014-06-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

# Download data from Tiingo
try:
    df = client.get_dataframe("TLT", startDate=start_date, endDate=end_date, frequency='daily')
    df.index = df.index.tz_localize(None)
except Exception as e:
    st.error(f"Failed to fetch data from Tiingo: {e}")
    st.stop()

# Calculate monthly returns
monthly_prices = df['adjClose'].resample('ME').last()
monthly_returns = monthly_prices.pct_change().dropna() * 100

if monthly_returns.empty:
    st.error("Monthly returns could not be calculated. Check the price data.")
    st.stop()

monthly_returns_df = monthly_returns.to_frame(name='Return')
monthly_returns_df['Month'] = monthly_returns_df.index.month
monthly_returns_df['MonthName'] = monthly_returns_df.index.month_name()
monthly_returns_df['Year'] = monthly_returns_df.index.year

# Monthly averages
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_avg = monthly_returns_df.groupby('MonthName')['Return'].mean().reindex(month_order).fillna(0)
monthly_avg_values = monthly_avg.values.reshape(-1, 1)

# KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
labels = kmeans.fit_predict(monthly_avg_values)

# Color coding
colors = ['green' if val >= 0 else 'red' for val in monthly_avg.values]

# Most recent month info
try:
    most_recent_month = monthly_returns_df.index[-1].month_name()
    most_recent_return = monthly_returns_df.iloc[-1]['Return']
    historical_avg = monthly_avg[most_recent_month]
    difference = most_recent_return - historical_avg
except Exception as e:
    st.error(f"Error retrieving most recent return data: {e}")
    st.stop()

# Subtitle string
subtitle_str = ', '.join([
    f"{month[:3]}: {val:.2f}%" for month, val in zip(monthly_avg.index, monthly_avg.values)
])

# Plot
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')
bars = ax.bar(monthly_avg.index, monthly_avg.values, color=colors)
ax.axhline(0, color='white', linewidth=0.8)

recent_idx = monthly_avg.index.tolist().index(most_recent_month)
bars[recent_idx].set_edgecolor('white')
bars[recent_idx].set_linewidth(2)
ax.text(recent_idx, monthly_avg.iloc[recent_idx] + 0.2,
        f"{most_recent_return:.2f}%\n({'+' if difference > 0 else ''}{difference:.2f}%)",
        ha='center', va='bottom', fontsize=10, fontweight='bold', color='white')

ax.set_title("K-Means Clustering of Average Monthly Returns for TLT (Last 10 Years)",
             color='white', fontsize=16, pad=20)
ax.set_xlabel(subtitle_str, color='white', fontsize=10, labelpad=20)
ax.set_ylabel("Average Return (%)", color='white')
ax.tick_params(colors='white')
plt.xticks(rotation=45)
ax.grid(axis='y', linestyle='--', alpha=0.3, color='white')
plt.tight_layout()

# Show in Streamlit
st.pyplot(fig)

# Optional: Display data tables
with st.expander("Show Monthly Average Returns"):
    st.dataframe(monthly_avg.round(2))

with st.expander("Show Raw Monthly Returns"):
    st.dataframe(monthly_returns_df[['Return', 'MonthName', 'Year']].sort_index(ascending=False))

