# indian_stock_dashboard_error_free.py

import streamlit as st
import pandas as pd
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px

# ---------------- Streamlit Config ----------------
st.set_page_config(page_title="🇮🇳 Indian Stock Dashboard", page_icon="📈", layout="wide")
st.title("🇮🇳 Indian Stock Market Dashboard")
st.write("Overview of NSE stocks with optional company search, news sentiment, and trend prediction.")

# ---------------- Initialize Sentiment Analyzer ----------------
analyzer = SentimentIntensityAnalyzer()

# ---------------- File Upload / Load ----------------
st.subheader("Upload NSE CSV (Optional if already in main folder)")
uploaded_file = st.file_uploader("Choose your nse_stocks.csv", type=["csv"])

if uploaded_file is not None:
    df_nse = pd.read_csv(uploaded_file)
elif st.checkbox("Use CSV from main folder"):
    try:
        df_nse = pd.read_csv("nse_stocks.csv")
    except FileNotFoundError:
        st.error("CSV not found in main folder. Please upload it.")
        st.stop()
else:
    st.warning("Please upload the CSV or enable the checkbox to use the main folder CSV.")
    st.stop()

# Clean column headers
df_nse.columns = df_nse.columns.str.strip()

# Prepare symbols
df_nse.dropna(subset=['Symbol'], inplace=True)
df_nse['Symbol'] = df_nse['Symbol'].astype(str) + ".NS"

# ---------------- Dropdown for Company Search ----------------
st.subheader("🔍 Search a Company")
company_list = df_nse['Company Name'].tolist()
selected_company = st.selectbox("Select Company:", company_list)
selected_symbol = df_nse[df_nse['Company Name'] == selected_company]['Symbol'].values[0]

# ---------------- Fetch Overview Data ----------------
overview_symbols = df_nse['Symbol'].head(50).tolist()  # Limit for performance

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
            pct_change = ((last_close - prev_close)/prev_close)*100
            data_list.append({
                "Stock": symbol,
                "Price (₹)": round(last_close,2),
                "% Change": round(pct_change,2)
            })
        except:
            continue
    return pd.DataFrame(data_list)

df_overview = fetch_stock_data(overview_symbols)

# ---------------- Top Gainers / Losers ----------------
if not df_overview.empty:
    st.subheader("📈 Top Gainers & Losers (NSE Overview)")
    top_gainers = df_overview.sort_values("% Change", ascending=False).head(5).reset_index(drop=True)
    top_losers = df_overview.sort_values("% Change").head(5).reset_index(drop=True)
    top_gainers.index += 1
    top_losers.index += 1

    st.markdown("**Top Gainers**")
    st.dataframe(top_gainers.style.format({"Price (₹)":"{:.2f}","% Change":"{:.2f}"})
                 .applymap(lambda x: 'color: green;' if isinstance(x,float) else '', subset=["% Change"]))

    st.markdown("**Top Losers**")
    st.dataframe(top_losers.style.format({"Price (₹)":"{:.2f}","% Change":"{:.2f}"})
                 .applymap(lambda x: 'color: red;' if isinstance(x,float) else '', subset=["% Change"]))

    # Heatmap
    st.subheader("🌡️ Stock Performance Heatmap")
    fig = px.scatter(df_overview, x="Stock", y="% Change", size="Price (₹)",
                     color="% Change", color_continuous_scale="RdYlGn",
                     hover_data=["Price (₹)"], size_max=40)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Selected Company Analysis ----------------
try:
    ticker = yf.Ticker(selected_symbol)
    hist = ticker.history(period="1y")
    
    if hist.empty:
        st.warning(f"No historical data for {selected_company}. Showing alternate insights.")
        info = ticker.info
        st.subheader(f"📌 {selected_company} ({selected_symbol}) Current Info")
        st.metric("Current Price (₹)", round(info.get('previousClose',0),2))
        st.metric("Market Cap (₹)", round(info.get('marketCap',0)/1e9,2))
    else:
        last_close = round(hist['Close'][-1],2)
        pct_change = round(((last_close - hist['Close'][-2])/hist['Close'][-2])*100,2)

        st.subheader(f"📌 {selected_company} ({selected_symbol}) Details")
        st.metric("Current Price (₹)", last_close)
        st.metric("% Change", pct_change)

        # News + Sentiment (placeholder)
        st.subheader("📰 Latest News & Sentiment")
        news_headlines = [
            f"{selected_company} shows strong growth potential",
            f"Investors are cautious about {selected_company} short term",
            f"{selected_company} announces new strategic partnership",
            f"{selected_company} stock underperforms analyst expectations"
        ]
        sentiment_scores = [analyzer.polarity_scores(h)["compound"] for h in news_headlines]
        avg_sentiment = round(sum(sentiment_scores)/len(sentiment_scores),2) if sentiment_scores else 0
        label = "Bullish" if avg_sentiment>0.2 else ("Bearish" if avg_sentiment<-0.2 else "Neutral")
        st.metric("Average Sentiment", avg_sentiment, delta=label)

        st.write("**Top Headlines:**")
        for h in news_headlines:
            st.write(f"- {h}")

        # Trend Prediction
        st.subheader("📊 Trend Prediction (Next 30 Days)")
        df_prophet = hist.reset_index()[['Date','Close']].rename(columns={'Date':'ds','Close':'y'})
        # Remove timezone robustly
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds']).dt.tz_localize(None)
        df_prophet = df_prophet.dropna(subset=['y'])

        model = Prophet(daily_seasonality=True)
        model.fit(df_prophet)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig2 = plot_plotly(model, forecast)
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data for {selected_company}: {e}")

# ---------------- Footer ----------------
st.markdown("---")
st.markdown("📌 Data fetched via Yahoo Finance. Sentiment analysis uses VADER. Trend prediction uses Prophet. Prices in INR.")
