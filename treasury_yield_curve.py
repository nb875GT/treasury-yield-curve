# streamlit_app.py
import streamlit as st
import matplotlib.pyplot as plt

# Example yield data (replace with actual or real-time data if needed)
money_market_start = {
    "1 mo.": 4.40, "2 mo.": 4.39, "3 mo.": 4.37, "4 mo.": 4.32, "6 mo.": 4.24, "1 yr.": 4.16
}
money_market_current = {
    "1 mo.": 4.37, "2 mo.": 4.38, "3 mo.": 4.34, "4 mo.": 4.35, "6 mo.": 4.21, "1 yr.": 4.04
}
capital_market_start = {
    "2 yr.": 4.25, "3 yr.": 4.27, "5 yr.": 4.38, "7 yr.": 4.48, "10 yr.": 4.58, "20 yr.": 4.86, "30 yr.": 4.78
}
capital_market_current = {
    "2 yr.": 3.96, "3 yr.": 3.98, "5 yr.": 4.15, "7 yr.": 4.32, "10 yr.": 4.48, "20 yr.": 4.91, "30 yr.": 4.85
}

# Combine for continuity between 1 yr. and 2 yr.
money_x = list(money_market_start.keys()) + ["2 yr."]
money_y_start = list(money_market_start.values()) + [capital_market_start["2 yr."]]
money_y_current = list(money_market_current.values()) + [capital_market_current["2 yr."]]

capital_x = ["1 yr."] + list(capital_market_start.keys())
capital_y_start = [money_market_start["1 yr."]] + list(capital_market_start.values())
capital_y_current = [money_market_current["1 yr."]] + list(capital_market_current.values())

# Streamlit layout
st.set_page_config(page_title="Treasury Yield Curve", layout="wide")
st.title("Treasury Yield Curve")

# Plotting
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

ax.plot(money_x, money_y_start, color='skyblue', marker='o', label='Money Market Yield (01/01/2025)')
ax.plot(money_x, money_y_current, color='blue', marker='o', label='Money Market Yield (Current)')
ax.plot(capital_x, capital_y_start, color='sandybrown', marker='s', label='Capital Market Yield (01/01/2025)')
ax.plot(capital_x, capital_y_current, color='darkorange', marker='s', label='Capital Market Yield (Current)')

ax.set_title("Treasury Yield Curve", fontsize=16, color='white')
ax.set_xlabel("Maturity (months - years)", fontsize=12, color='white')
ax.set_ylabel("Yield (%)", fontsize=12, color='white')
ax.tick_params(axis='x', colors='white', rotation=45)
ax.tick_params(axis='y', colors='white')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(facecolor='black', edgecolor='white')
legend = ax.legend(facecolor='black', edgecolor='white')
for text in legend.get_texts():
    text.set_color("white")


st.pyplot(fig)

