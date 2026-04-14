import streamlit as st
from openai import OpenAI
import yfinance as yf
import pandas as pd
import os

# 🔑 Groq client (FREE)
import os

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# 🧠 Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🎨 UI
st.title("🤖 AI Trading Agent")

# 📜 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ⌨️ Input
user_input = st.chat_input("Ask about stocks, calculate, or chat...")

# 🧮 Calculator
def calculator(query):
    try:
        return str(eval(query))
    except:
        return "Error in calculation"

# 📊 Get stock price
def get_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        price = data["Close"].iloc[-1]
        return price
    except:
        return None

# 📉 RSI Calculation
def calculate_rsi(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

# 🤖 LLM Chat
def chat_llm(messages):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content

# 🧠 Agent Logic
def agent(user_input):
    user_input_lower = user_input.lower()

    # 🧮 Calculator
    if any(op in user_input for op in ["+", "-", "*", "/"]):
        return calculator(user_input)

    # 📊 Stock price
    elif "price" in user_input_lower:
        words = user_input.split()
        for word in words:
            if word.isupper():
                symbol = word + ".NS"
                price = get_stock_price(symbol)

                if price:
                    return f"📊 Current price of {word}: ₹{price:.2f}"
                else:
                    return "Stock not found"

        return "Please provide stock symbol (e.g., TCS, INFY)"

    # 📉 Stock analysis (RSI)
    elif "analyze" in user_input_lower:
        words = user_input.split()
        for word in words:
            if word.isupper():
                symbol = word + ".NS"
                price = get_stock_price(symbol)
                rsi = calculate_rsi(symbol)

                if price:
                    if rsi > 70:
                        status = "Overbought ⚠️"
                    elif rsi < 30:
                        status = "Oversold 🟢"
                    else:
                        status = "Neutral"

                    return f"""
📊 Stock: {word}
💰 Price: ₹{price:.2f}
📉 RSI: {rsi:.2f}

📌 Interpretation: {status}
"""
                else:
                    return "Stock not found"

        return "Please provide stock symbol (e.g., TCS, INFY)"

    # 📈 AI Stock Advice
    elif "stock" in user_input_lower or "invest" in user_input_lower:
        return chat_llm([
            {"role": "system", "content": "You are a stock market expert. Give simple advice."},
            {"role": "user", "content": user_input}
        ])

    # 🤖 Default chat
    else:
        return chat_llm(st.session_state.messages + [{"role": "user", "content": user_input}])

# 🚀 Run App
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)

    reply = agent(user_input)

    print("DEBUG:", reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    with st.chat_message("assistant"):
        st.write(reply)