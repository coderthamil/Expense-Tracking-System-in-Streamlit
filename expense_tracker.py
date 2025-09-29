import streamlit as st
import pandas as pd
import requests
import os
import plotly.express as px
from datetime import datetime

# ---------- Theme Styling ----------
def apply_theme(theme):
    themes = {
        "Black-Yellow": "body {background-color: #000; color: #FFD700;}",
        "Black-Red": "body {background-color: #000; color: #FF0000;}",
        "Ocean": "body {background: linear-gradient(to right, #00c6ff, #0072ff); color: white;}",
        "Sunset": "body {background: linear-gradient(to right, #ff7e5f, #feb47b); color: black;}",
        "Mint": "body {background: linear-gradient(to right, #a8edea, #fed6e3); color: black;}",
        "Lavender": "body {background: linear-gradient(to right, #e0c3fc, #8ec5fc); color: black;}",
        "Dark Mode": "body {background-color: #121212; color: #e0e0e0;}",
        "Light Mode": "body {background-color: #ffffff; color: #000000;}",
        "Gradient Blue": "body {background: linear-gradient(to right, #1e3c72, #2a5298); color: white;}",
        "Gradient Sunset": "body {background: linear-gradient(to right, #ff9966, #ff5e62); color: white;}",
        "Forest": "body {background-color: #2e8b57; color: white;}",
        "Royal": "body {background-color: #4169e1; color: white;}",
        "Steel": "body {background-color: #4682b4; color: white;}",
        "Peach": "body {background-color: #ffe5b4; color: black;}",
        "Slate": "body {background-color: #708090; color: white;}"
    }
    css = themes.get(theme, "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

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
def show_dashboard(df):
    st.subheader("📋 Expense Table")
    st.dataframe(df)

    st.subheader("📈 Expense by Category")
    bar = px.bar(df, x="Category", y="INR_Equivalent", color="Category")
    st.plotly_chart(bar)

    st.subheader("🧁 Expense Distribution")
    pie = px.pie(df, names="Category", values="INR_Equivalent")
    st.plotly_chart(pie)

    st.subheader("📅 Expense Over Time")
    line = px.line(df, x="Date", y="INR_Equivalent", markers=True)
    st.plotly_chart(line)

# ---------- App Starts ----------
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💸 Multi-Currency Expense Tracker")

# Sidebar: Theme + Currency Converter
theme = st.sidebar.selectbox("🎨 Choose Theme", [
    "Black-Yellow", "Black-Red", "Ocean", "Sunset", "Mint", "Lavender", "Dark Mode", "Light Mode",
    "Gradient Blue", "Gradient Sunset", "Forest", "Royal", "Steel", "Peach", "Slate"
])
apply_theme(theme)

st.sidebar.header("💱 Currency Converter")
amount = st.sidebar.number_input("Amount", min_value=0.0)
from_curr = st.sidebar.selectbox("From", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"])
to_curr = st.sidebar.selectbox("To", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"])
converted = convert_currency(amount, from_curr, to_curr)
st.sidebar.write(f"Converted: {converted:.2f} {to_curr}")

# Expense Input
st.header("📝 Add New Expense")
date = st.date_input("Date", value=datetime.today())
desc = st.text_input("Description")
category = st.selectbox("Category", ["Food", "Travel", "Bills", "Shopping", "Other"])
currency = st.selectbox("Currency", ["USD", "INR", "EUR", "JPY", "GBP", "CAD", "AUD", "CNY"])
amount = st.number_input("Amount", min_value=0.0)

if st.button("Add Expense"):
    base_amount = convert_currency(amount, currency, "INR")
    new_entry = pd.DataFrame([[date, desc, category, currency, amount, base_amount]],
                             columns=["Date", "Description", "Category", "Currency", "Amount", "INR_Equivalent"])
    file_path = "expenses.csv"
    write_header = not os.path.exists(file_path)
    new_entry.to_csv(file_path, mode='a', header=write_header, index=False)
    st.success("Expense added!")

# Load Data
if os.path.exists("expenses.csv"):
    df = pd.read_csv("expenses.csv", parse_dates=["Date"])
else:
    df = pd.DataFrame(columns=["Date", "Description", "Category", "Currency", "Amount", "INR_Equivalent"])

# History Panel
st.header("📜 Expense History")
with st.expander("🔍 Filter History"):
    date_range = st.date_input("Select Date Range", [])
    category_filter = st.multiselect("Filter by Category", df["Category"].unique())
    currency_filter = st.multiselect("Filter by Currency", df["Currency"].unique())

    filtered_df = df.copy()
    if date_range and len(date_range) == 2:
        filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(date_range[0])) &
                                  (filtered_df["Date"] <= pd.to_datetime(date_range[1]))]
    if category_filter:
        filtered_df = filtered_df[filtered_df["Category"].isin(category_filter)]
    if currency_filter:
        filtered_df = filtered_df[filtered_df["Currency"].isin(currency_filter)]

st.dataframe(filtered_df)

# Dashboard
st.header("📊 Dashboard")
show_dashboard(filtered_df)