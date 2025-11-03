# global_stock_dashboard_full.py

import streamlit as st
import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="🌎 Global Stock Dashboard", page_icon="💹", layout="wide")
st.title("🌎 Global Stock Dashboard (Prices in ₹)")
st.write("Track top global stocks & search any stock symbol worldwide. Optional sentiment analysis included.")

# ---------------- Initialize ----------------
c = CurrencyRates()
analyzer = SentimentIntensityAnalyzer()

# ---------------- Exchange Rates ----------------
try:
    USD_INR = c.get_rate('USD', 'INR')
    EUR_INR = c.get_rate('EUR', 'INR')
    JPY_INR = c.get_rate('JPY', 'INR')
except:
    USD_INR, EUR_INR, JPY_INR = 83, 90, 0.61  # fallback rates

# ---------------- Preloaded Popular Stocks ----------------
# Major global stocks for dashboard overview
global_stocks = {
    "US": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "JPM", "V"],
    "India": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "HINDUNILVR.NS", "KOTAKBANK.NS"],
    "Europe": ["SAP.DE", "SIE.DE", "ASML.AS", "NESN.SW", "ROG.SW"],
    "Asia": ["7203.T", "6758.T", "9984.T", "0005.HK", "0700.HK"]  # Toyota, Sony, SoftBank, HSBC, Tencent
}

# ---------------- Optional Search ----------------
search_stock = st.text_input("🔍 Search any stock symbol worldwide (Optional)").upper().strip()

# ---------------- Fetch Preloaded Stocks ----------------
preload_data = []

for region, symbols in global_stocks.items():
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if hist.empty:
                continue
            last_close = hist['Close'][-1]
            prev_close = hist['Close'][-2]
            percent_change = ((last_close - prev_close) / prev_close) * 100

            # Convert to INR
            if region == "US":
                price_inr = last_close * USD_INR
            elif region == "Europe":
                price_inr = last_close * EUR_INR
            elif region == "Asia":
                price_inr = last_close * JPY_INR
            else:
                price_inr = last_close  # Already INR

            preload_data.append({
                "Stock": symbol,
                "Region": region,
                "Price (₹)": round(price_inr, 2),
                "% Change": round(percent_change, 2)
            })
        except:
            continue

df_preload = pd.DataFrame(preload_data)

# ---------------- Display Top Gainers & Losers ----------------
if not df_preload.empty:
    st.subheader("📈 Top 5 Gainers & Losers (Preloaded Global Stocks)")
    top_gainers = df_preload.sort_values("% Change", ascending=False).head(5)
    top_losers = df_preload.sort_values("% Change").head(5)

    st.markdown("**Top Gainers**")
    st.dataframe(top_gainers.style.applymap(lambda x: 'color: green;' if isinstance(x, float) else '', subset=["% Change"]))
    st.markdown("**Top Losers**")
    st.dataframe(top_losers.style.applymap(lambda x: 'color: red;' if isinstance(x, float) else '', subset=["% Change"]))

    # ---------------- Market Heatmap ----------------
    st.subheader("🌡️ Market Heatmap")
    fig = px.scatter(df_preload, x="Stock", y="% Change", color="Region",
                     size="Price (₹)", hover_data=["Price (₹)"], 
                     color_discrete_sequence=px.colors.qualitative.Set1,
                     size_max=40)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Optional Sentiment Analysis ----------------
if search_stock:
    st.subheader(f"📰 Sentiment Analysis for {search_stock}")
    try:
        # Fetch stock info to confirm validity
        ticker = yf.Ticker(search_stock)
        info = ticker.history(period="1d")
        if info.empty:
            st.error("Stock symbol not found or no data available.")
        else:
            # Placeholder headlines (replace with NewsAPI for real data)
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
    except:
        st.error("Error fetching data for this stock.")

else:
    st.info("Optional: Enter a stock symbol above to see sentiment analysis.")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("📌 Data fetched via Yahoo Finance. Currency converted to INR. Sentiment analysis uses VADER.")
