import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import os

# 🔑 API
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.1-8b-instant"

# 🎨 Page config
st.set_page_config(page_title="AI Trading Dashboard", layout="wide")

# 🧠 Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🎯 Sidebar (like Zerodha)
st.sidebar.title("📊 Trading Panel")
stock_symbol = st.sidebar.text_input("Enter Stock (e.g., TCS)", "TCS")
analyze_btn = st.sidebar.button("Analyze")

st.sidebar.markdown("---")
st.sidebar.write("### 🤖 AI Assistant")
ai_query = st.sidebar.text_input("Ask AI...")

# 📊 Get stock data
def get_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="6mo")

# 📉 RSI
def compute_rsi(data):
    delta = data["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 📈 Moving Average
def moving_avg(data):
    return data["Close"].rolling(window=20).mean()

# 📊 Candlestick Chart
def plot_chart(data, symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Candles"
    ))

    fig.add_trace(go.Scatter(
        x=data.index,
        y=moving_avg(data),
        mode='lines',
        name='MA (20)'
    ))

    fig.update_layout(title=f"{symbol} Chart", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# 🤖 AI
def chat_llm(query):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a trading expert. Give short and clear advice."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

# 🚀 MAIN DASHBOARD
st.title("📊 AI Trading Dashboard (Zerodha Style)")

if analyze_btn:
    symbol = stock_symbol.upper() + ".NS"
    data = get_data(symbol)

    if data.empty:
        st.error("Stock not found")
    else:
        price = data["Close"].iloc[-1]
        rsi = compute_rsi(data).iloc[-1]
        ma = moving_avg(data).iloc[-1]

        # Layout columns
        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Price", f"₹{price:.2f}")
        col2.metric("📉 RSI", f"{rsi:.2f}")
        col3.metric("📈 MA(20)", f"{ma:.2f}")

        # Signal
        if rsi > 70:
            signal = "SELL ⚠️"
        elif rsi < 30:
            signal = "BUY 🟢"
        else:
            signal = "HOLD 🤝"

        st.subheader(f"📌 Signal: {signal}")

        # Chart
        plot_chart(data, stock_symbol.upper())

# 🤖 AI Assistant
if ai_query:
    reply = chat_llm(ai_query)
    st.sidebar.write("💡 AI:", reply)