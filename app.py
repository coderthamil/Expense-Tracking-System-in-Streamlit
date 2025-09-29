import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px
from datetime import datetime

# ---------- Global Theme Dictionary ----------
themes = {
    "Black-Red": {"gradient": "linear-gradient(135deg, #060A31, #FF0000)", "glow": "#FF0000"},
    "Black-Yellow": {"gradient": "linear-gradient(135deg, #000000, #FFD700)", "glow": "#FFD700"},
    "Black-Blue": {"gradient": "linear-gradient(135deg, #000000, #00BFFF)", "glow": "#00BFFF"},
    "Black-Green": {"gradient": "linear-gradient(135deg, #000000, #39ff14)", "glow": "#39ff14"},
    "Red-Dead": {"gradient": "linear-gradient(135deg, #3b0000, #8b0000)", "glow": "#ff4c4c"},
    "Yellow-Blue": {"gradient": "linear-gradient(135deg, #FFD700, #0072ff)", "glow": "#00c6ff"},
    "Blue-Red": {"gradient": "linear-gradient(135deg, #0b0b0b, #fd0000)", "glow": "#ff0000"},
    "Ocean": {"gradient": "linear-gradient(135deg, #00c6ff, #0072ff)", "glow": "#00ffff"},
    "Sunset": {"gradient": "linear-gradient(135deg, #ff7e5f, #feb47b)", "glow": "#ffcc70"},
    "Mint": {"gradient": "linear-gradient(135deg, #a8edea, #fed6e3)", "glow": "#00ffcc"},
    "Lavender": {"gradient": "linear-gradient(135deg, #e0c3fc, #8ec5fc)", "glow": "#cc99ff"},
    "Dark Mode": {"gradient": "linear-gradient(135deg, #0f0f0f, #1c1c1c)", "glow": "#888888"},
    "Light Mode": {"gradient": "linear-gradient(135deg, #ffffff, #eeeeee)", "glow": "#999999"},
    "Gradient Blue": {"gradient": "linear-gradient(135deg, #1e3c72, #2a5298)", "glow": "#66ccff"},
    "Gradient Sunset": {"gradient": "linear-gradient(135deg, #ff9966, #ff5e62)", "glow": "#ff9966"},
    "Forest": {"gradient": "linear-gradient(135deg, #2e8b57, #006400)", "glow": "#00ff99"},
    "Royal": {"gradient": "linear-gradient(135deg, #4169e1, #00008b)", "glow": "#6699ff"},
    "Steel": {"gradient": "linear-gradient(135deg, #4682b4, #708090)", "glow": "#a0c4ff"},
    "Peach": {"gradient": "linear-gradient(135deg, #ffe5b4, #ffdab9)", "glow": "#ffcc99"},
    "Slate": {"gradient": "linear-gradient(135deg, #708090, #2f4f4f)", "glow": "#cccccc"},
    "Skyline": {"gradient": "linear-gradient(135deg, #2980b9, #6dd5fa)", "glow": "#00ccff"},
    "Coral": {"gradient": "linear-gradient(135deg, #ff7e5f, #feb47b)", "glow": "#ff6666"},
    "Emerald": {"gradient": "linear-gradient(135deg, #2ecc71, #27ae60)", "glow": "#00ff99"},
    "Rose": {"gradient": "linear-gradient(135deg, #ffafbd, #ffc3a0)", "glow": "#ff99cc"},
    "Sand": {"gradient": "linear-gradient(135deg, #fceabb, #f8b500)", "glow": "#ffcc66"},
    "Midnight": {"gradient": "linear-gradient(135deg, #232526, #414345)", "glow": "#ffffff"}
}

# ---------- Theme Styling ----------
def apply_theme(theme, font, text_color, placeholder_color):
    selected = themes.get(theme, {"gradient": "#000000", "glow": "#00ffff"})
    st.markdown(f"""
        <style>
        .stApp {{
            background: {selected['gradient']};
            font-family: {font};
            color: {text_color};
        }}
        h1, h2, h3, h4, h5, h6, p, label {{
            color: {text_color} !important;
            text-shadow: 0 0 5px {selected['glow']};
        }}
        input::placeholder, textarea::placeholder {{
            color: {placeholder_color} !important;
        }}
        .glass {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 10px {selected['glow']};
            animation: flipIn 1s ease;
        }}
        @keyframes flipIn {{
            from {{ transform: rotateY(90deg); opacity: 0; }}
            to {{ transform: rotateY(0deg); opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)
    return selected["glow"]

# ---------- Currency Conversion ----------
def convert_currency(amount, from_curr, to_curr):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
        response = requests.get(url).json()
        rate = response["rates"].get(to_curr, 1)
        return amount * rate
    except:
        return amount

# ---------- Dashboard Charts ----------
def show_dashboard(df, chart_color):
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📋 Expense Table")
    st.dataframe(df)

    st.subheader("📈 Expense by Category")
    bar = px.bar(df, x="Category", y="INR_Equivalent", color="Category", color_discrete_sequence=[chart_color])
    st.plotly_chart(bar)

    st.subheader("🧁 Expense Distribution")
    pie = px.pie(df, names="Category", values="INR_Equivalent", color_discrete_sequence=[chart_color])
    st.plotly_chart(pie)

    st.subheader("📅 Expense Over Time")
    line = px.line(df, x="Date", y="INR_Equivalent", markers=True, color_discrete_sequence=[chart_color])
    st.plotly_chart(line)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- App Starts ----------
st.set_page_config(page_title="💸 Expense Tracker", layout="wide")
st.markdown("<h1 style='text-align:center;'>💸 Multi-Currency Expense Tracker</h1>", unsafe_allow_html=True)

# Sidebar: Theme + Font + Colors
theme = st.sidebar.selectbox("🎨 Choose Theme", list(themes.keys()))
font_style = st.sidebar.selectbox("🖋️ Font Style", ["Arial", "Verdana", "Georgia", "Courier New", "Comic Sans MS", "Trebuchet MS", "Lucida Console"])
text_color = st.sidebar.color_picker("🔤 Text Color", "#ffffff")
placeholder_color = st.sidebar.color_picker("🔘 Placeholder Color", "#cccccc")
chart_color = st.sidebar.color_picker("📊 Chart Color", "#00c6ff")

glow_color = apply_theme(theme, font_style, text_color, placeholder_color)

# Sidebar: Currency Converter
st.sidebar.header("💱 Currency Converter")
amount = st.sidebar.number_input("Amount", min_value=0.0, key="converter_amount")
from_curr = st.sidebar.selectbox("From", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"], key="converter_from")
to_curr = st.sidebar.selectbox("To", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"], key="converter_to")
converted = convert_currency(amount, from_curr, to_curr)
st.sidebar.markdown(f"<div style='color:{glow_color}; font-size:18px;'>Converted: {converted:.2f} {to_curr}</div>", unsafe_allow_html=True)

# Expense Input
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.header("📝 Add New Expense")
date = st.date_input("Date", value=datetime.today(), key="expense_date")
desc = st.text_input("Description", key="expense_desc")
category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"], key="expense_category")
currency = st.selectbox("Currency", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"], key="expense_currency")
amount = st.number_input("Amount", min_value=0.0, key="expense_amount")

if st.button("Add Expense", key="add_expense_btn"):
    base_amount = convert_currency(amount, currency, "INR")
    new_entry = pd.DataFrame([[date, desc, category, currency, amount, base_amount]],
                             columns=["Date", "Description", "Category", "Currency", "Amount", "INR_Equivalent"])
    file_path = "expenses.csv"
    write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0
    new_entry.to_csv(file_path, mode='a', header=write_header, index=False)
    st.success("Expense added!")
st.markdown('</div>', unsafe_allow_html=True)

# Load Data
if os.path.exists("expenses.csv"):
    df = pd.read_csv("expenses.csv", parse_dates=["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Description", "Category", "Currency", "Amount", "INR_Equivalent"])

# History Panel
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.header("📜 Expense History")
with st.expander("🔍 Filter History"):
    date_range = st.date_input("Select Date Range", [], key="filter_date_range")
    category_filter = st.multiselect("Filter by Category", df["Category"].unique(), key="filter_category")
    currency_filter = st.multiselect("Filter by Currency", df["Currency"].unique(), key="filter_currency")

filtered_df = df.copy()
if date_range and len(date_range) == 2:
    filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
                              (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]
if category_filter:
    filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
if currency_filter:
    filtered_df = filtered_df[filtered_df["Currency"].isin(currency_filter)]

st.dataframe(filtered_df)
st.markdown('</div>', unsafe_allow_html=True)

# Dashboard
st.header("📊 Dashboard")
show_dashboard(filtered_df, chart_color)