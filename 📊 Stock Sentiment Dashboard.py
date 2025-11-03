# stock_sentiment_dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px

# --- Streamlit Page Config ---
st.set_page_config(page_title="📊 Stock Sentiment Dashboard",
                   page_icon="💹", layout="wide")

st.title("📊 Stock Sentiment & Market Overview Dashboard")
st.write("Enter stock symbols (comma-separated) to analyze sentiment and daily performance.")

# --- User Input ---
stock_input = st.text_input("Enter stock symbols (e.g., TSLA,AAPL,MSFT,NVDA)")
stock_symbols = [s.strip().upper() for s in stock_input.split(",") if s.strip()]

# --- Initialize Sentiment Analyzer ---
analyzer = SentimentIntensityAnalyzer()

# --- Placeholder for results ---
results = []

# --- Function to fetch news using NewsAPI ---
def fetch_news(stock, api_key=None):
    """Fetch latest headlines for a stock using NewsAPI. 
    If no API key, returns placeholder headlines."""
    if not api_key:
        # Placeholder headlines
        return [
            f"{stock} reports strong quarterly results",
            f"Market experts are bullish on {stock}",
            f"{stock} stock faces regulatory challenges"
        ]
    url = f'https://newsapi.org/v2/everything?q={stock}&sortBy=publishedAt&language=en&apiKey={api_key}'
    r = requests.get(url)
    articles = r.json().get("articles", [])
    return [a["title"] for a in articles[:10]]  # top 10 headlines

# --- Process each stock ---
for stock in stock_symbols:
    try:
        # --- Fetch Stock Info ---
        ticker = yf.Ticker(stock)
        data = ticker.history(period="1d")
        price = data['Close'][-1]
        prev_close = data['Close'][-2] if len(data) > 1 else price
        percent_change = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0

        # --- Fetch news ---
        headlines = fetch_news(stock)  # replace with API key if available

        # --- Sentiment Analysis ---
        sentiment_scores = [analyzer.polarity_scores(headline)["compound"] for headline in headlines]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

        # --- Sentiment Label ---
        if avg_sentiment > 0.2:
            label = "Bullish"
        elif avg_sentiment < -0.2:
            label = "Bearish"
        else:
            label = "Neutral"

        results.append({
            "Stock": stock,
            "Price": round(price,2),
            "% Change": round(percent_change,2),
            "Avg Sentiment": round(avg_sentiment,2),
            "Sentiment Label": label,
            "News Headlines": headlines
        })
    except Exception as e:
        st.error(f"Error fetching data for {stock}: {e}")

# --- Display Results ---
if results:
    st.subheader("📈 Stock Overview")
    df = pd.DataFrame(results)
    
    # Highlight table with color based on sentiment
    def color_sentiment(val):
        if val == "Bullish":
            color = 'green'
        elif val == "Bearish":
            color = 'red'
        else:
            color = 'goldenrod'
        return f'color: {color}; font-weight:bold'

    st.dataframe(df.style.applymap(color_sentiment, subset=["Sentiment Label"]))

    # --- Market Heatmap ---
    st.subheader("🔥 Market Sentiment Heatmap")
    fig = px.scatter(df, x="% Change", y="Avg Sentiment", text="Stock",
                     size=[10]*len(df), color="Sentiment Label",
                     color_discrete_map={"Bullish":"green","Bearish":"red","Neutral":"goldenrod"},
                     size_max=40,
                     labels={"% Change":"% Daily Change","Avg Sentiment":"Average Sentiment Score"})
    st.plotly_chart(fig, use_container_width=True)

    # --- Individual Stock Details ---
    for stock_data in results:
        st.markdown(f"### 📌 {stock_data['Stock']} Details")
        st.metric("Current Price", f"₹{stock_data['Price']}", delta=f"{stock_data['% Change']}%")
        st.write(f"**Average Sentiment:** {stock_data['Avg Sentiment']} ({stock_data['Sentiment Label']})")
        st.write("**Top News Headlines:**")
        for headline in stock_data['News Headlines']:
            st.write(f"- {headline}")
else:
    st.info("Enter valid stock symbols above to see analysis.")
