# indian_stock_dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px
import requests
import datetime

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="🇮🇳 Indian Stock Dashboard", page_icon="📈", layout="wide")
st.title("🇮🇳 Indian Stock Market Dashboard")
st.write("Overview of all NSE stocks with optional company search, news sentiment, and trend prediction.")

# ---------------- Initialize Sentiment Analyzer ----------------
analyzer = SentimentIntensityAnalyzer()

# ---------------- Load NSE Stock Symbols ----------------
# For demonstration, using top NSE symbols; in real project, download NSE listed companies CSV
nse_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"
]

# ---------------- Fetch Stock Prices ----------------
def fetch_stock_data(symbols):
    data_list = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                continue
            last_close = hist['Close'][-1]
            prev_close = hist['Close'][-2]
            pct_change = ((last_close - prev_close) / prev_close) * 100
            data_list.append({
                "Stock": symbol,
                "Price (₹)": round(last_close,2),
                "% Change": round(pct_change,2)
            })
        except:
            continue
    return pd.DataFrame(data_list)

df_overview = fetch_stock_data(nse_stocks)

# ---------------- Display Top Gainers / Losers ----------------
if not df_overview.empty:
    st.subheader("📈 Top Gainers & Losers (NSE)")
    top_gainers = df_overview.sort_values("% Change", ascending=False).head(5)
    top_losers = df_overview.sort_values("% Change").head(5)

    st.markdown("**Top Gainers**")
    st.dataframe(top_gainers.style.applymap(lambda x: 'color: green;' if isinstance(x, float) else '', subset=["% Change"]))
    st.markdown("**Top Losers**")
    st.dataframe(top_losers.style.applymap(lambda x: 'color: red;' if isinstance(x, float) else '', subset=["% Change"]))

    # ---------------- Heatmap ----------------
    st.subheader("🌡️ Stock Performance Heatmap")
    fig = px.scatter(df_overview, x="Stock", y="% Change", size="Price (₹)",
                     color="% Change", color_continuous_scale="RdYlGn",
                     hover_data=["Price (₹)"], size_max=40)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Optional Company Search ----------------
search_stock = st.text_input("🔍 Search any NSE stock symbol (Optional)").upper().strip()
if search_stock:
    try:
        ticker = yf.Ticker(search_stock)
        hist = ticker.history(period="1y")  # 1 year historical
        if hist.empty:
            st.error("Stock symbol not found or no data available.")
        else:
            last_close = hist['Close'][-1]
            st.subheader(f"📌 {search_stock} Details")
            st.metric("Current Price (₹)", round(last_close,2))
            pct_change = ((last_close - hist['Close'][-2]) / hist['Close'][-2]) * 100
            st.metric("% Change", round(pct_change,2))

            # ---------------- Latest News (Placeholder, replace with NewsAPI) ----------------
            st.subheader("📰 Latest News & Sentiment")
            news_headlines = [
                f"{search_stock} shows strong growth potential",
                f"Investors are cautious about {search_stock} short term",
                f"{search_stock} announces new strategic partnership",
                f"{search_stock} stock underperforms analyst expectations"
            ]
            sentiment_scores = [analyzer.polarity_scores(h)["compound"] for h in news_headlines]
            avg_sentiment = sum(sentiment_scores)/len(sentiment_scores) if sentiment_scores else 0
            if avg_sentiment > 0.2:
                label = "Bullish"
            elif avg_sentiment < -0.2:
                label = "Bearish"
            else:
                label = "Neutral"
            st.metric("Average Sentiment", round(avg_sentiment,2), delta=label)
            st.write("**Top Headlines:**")
            for h in news_headlines:
                st.write(f"- {h}")

            # ---------------- Trend Prediction ----------------
            st.subheader("📊 Trend Prediction (Next 30 Days)")
            df_prophet = hist.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
            model = Prophet(daily_seasonality=True)
            model.fit(df_prophet)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            fig2 = plot_plotly(model, forecast)
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data for {search_stock}: {e}")
else:
    st.info("Optional: Enter a stock symbol above to see detailed analysis, news sentiment, and trend prediction.")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("📌 Data fetched via Yahoo Finance. Sentiment analysis uses VADER. Trend prediction uses Prophet.")
