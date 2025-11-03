# global_stock_dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px


# --- Streamlit Page Config ---
st.set_page_config(page_title="🌎 Global Stock Dashboard", page_icon="💹", layout="wide")
st.title("🌎 Global Stock Market Dashboard (All Prices in ₹)")
st.write("Track major global stocks and indices with top gainers/losers. Optional: analyze any individual stock sentiment.")

# --- Initialize currency converter & sentiment analyzer ---
c = CurrencyRates()
analyzer = SentimentIntensityAnalyzer()

# --- Exchange rates ---
try:
    USD_INR = c.get_rate('USD', 'INR')
    EUR_INR = c.get_rate('EUR', 'INR')
    JPY_INR = c.get_rate('JPY', 'INR')
except:
    USD_INR, EUR_INR, JPY_INR = 83, 90, 0.61  # fallback rates

# --- Define global stocks (symbol, market) ---
global_stocks = {
    "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "FB", "BRK-B", "JPM", "V"],
    "India": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "KOTAKBANK.NS"],
    "Europe": ["SAP.DE", "SIE.DE", "ASML.AS", "NESN.SW", "ROG.SW"],
    "Asia": ["7203.T", "6758.T", "9984.T", "0005.HK", "0700.HK"]  # Toyota, Sony, SoftBank, HSBC, Tencent
}

# --- Optional stock search ---
search_stock = st.text_input("🔍 Enter a stock symbol to analyze sentiment (Optional)").upper().strip()

# --- Fetch stock prices and % change ---
all_data = []

for region, stocks in global_stocks.items():
    for symbol in stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if hist.empty:
                continue
            last_close = hist['Close'][-1]
            prev_close = hist['Close'][-2]
            percent_change = ((last_close - prev_close)/prev_close)*100

            # Convert to INR
            if region == "US":
                last_close_inr = last_close * USD_INR
            elif region == "Europe":
                last_close_inr = last_close * EUR_INR
            elif region == "Asia":
                last_close_inr = last_close * JPY_INR
            else:
                last_close_inr = last_close  # Already INR

            all_data.append({
                "Stock": symbol,
                "Region": region,
                "Price (₹)": round(last_close_inr,2),
                "% Change": round(percent_change,2)
            })
        except Exception as e:
            continue

df = pd.DataFrame(all_data)

# --- Display Top Gainers / Losers ---
if not df.empty:
    st.subheader("📈 Top 5 Gainers & Losers (Global)")
    top_gainers = df.sort_values("% Change", ascending=False).head(5)
    top_losers = df.sort_values("% Change").head(5)
    st.markdown("**Top Gainers**")
    st.dataframe(top_gainers.style.applymap(lambda x: 'color: green;' if isinstance(x, float) else '', subset=["% Change"]))
    st.markdown("**Top Losers**")
    st.dataframe(top_losers.style.applymap(lambda x: 'color: red;' if isinstance(x, float) else '', subset=["% Change"]))

    # --- Market Heatmap ---
    st.subheader("🌡️ Market Performance Heatmap")
    fig = px.scatter(df, x="Stock", y="% Change", color="Region",
                     size="Price (₹)", hover_data=["Price (₹)"], 
                     color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig, use_container_width=True)

# --- Optional Sentiment Analysis ---
if search_stock:
    st.subheader(f"📰 Sentiment Analysis for {search_stock}")

    # Fetch news (placeholder for demo)
    headlines = [
        f"{search_stock} shows strong growth potential",
        f"Investors are cautious about {search_stock} short term",
        f"{search_stock} announces new strategic partnership",
        f"{search_stock} stock underperforms analyst expectations"
    ]

    sentiment_scores = [analyzer.polarity_scores(h)["compound"] for h in headlines]
    avg_sentiment = sum(sentiment_scores)/len(sentiment_scores) if sentiment_scores else 0

    if avg_sentiment > 0.2:
        label = "Bullish"
    elif avg_sentiment < -0.2:
        label = "Bearish"
    else:
        label = "Neutral"

    st.metric("Average Sentiment Score", round(avg_sentiment,2), delta=label)
    st.write("**Top News Headlines:**")
    for h in headlines:
        st.write(f"- {h}")

else:
    st.info("Optional: Enter a stock symbol above to see sentiment analysis.")

# --- Footer ---
st.markdown("---")
st.markdown("📌 Data fetched via Yahoo Finance. Currency converted to INR. Sentiment analysis uses VADER.")
