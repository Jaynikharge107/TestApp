import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from GoogleNews import GoogleNews

st.set_page_config(page_title="Indian Stock Insights", layout="wide")

# ----------------- LOAD NSE DATA -----------------
@st.cache_data
def load_nse_symbols():
    df = pd.read_csv("nse_stocks.csv")
    df.columns = df.columns.str.strip()
    df['Ticker'] = df['Symbol'].astype(str).str.strip() + ".NS"
    df['Company Name'] = df['Company Name'].astype(str).str.strip()
    return df[['Ticker', 'Company Name']]

nse_df = load_nse_symbols()
ticker_list = nse_df['Ticker'].tolist()
ticker_map = dict(zip(nse_df['Ticker'], nse_df['Company Name']))

# ----------------- PRICE FETCHING -----------------
@st.cache_data(ttl=60*10)
def get_prices(tickers, period="1mo"):
    data = yf.download(tickers, period=period, interval="1d", group_by="ticker", progress=False)
    prices = {}
    for t in tickers:
        try:
            if isinstance(data.columns, pd.MultiIndex):
                df = data[t].dropna()
            else:
                df = data
            prices[t] = df
        except KeyError:
            continue
    return prices

def calc_returns(df):
    col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    return df[col].pct_change().dropna()

# ----------------- MOVERS -----------------
def get_top_movers(days=30):
    data = get_prices(ticker_list[:100], period=f"{days}d")  # limit to first 100 to keep fast
    movers = []
    for t, df in data.items():
        if df.empty: continue
        col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        start, end = df[col].iloc[0], df[col].iloc[-1]
        change = (end - start) / start * 100
        movers.append([t, ticker_map.get(t, ""), end, round(change, 2)])
    df = pd.DataFrame(movers, columns=["Ticker", "Company", "Last Price", "% Change"])
    return df.sort_values("% Change", ascending=False)

# ----------------- NEWS & SENTIMENT -----------------
@st.cache_data(ttl=60*30)
def fetch_news(company, limit=8):
    googlenews = GoogleNews(period='7d')
    googlenews.search(company)
    return googlenews.result()[:limit]

def sentiment_summary(news_list):
    analyzer = SentimentIntensityAnalyzer()
    results = []
    for n in news_list:
        text = n.get('title') or ''
        score = analyzer.polarity_scores(text)
        results.append({"Headline": text, "Sentiment": score['compound']})
    return pd.DataFrame(results)

# ----------------- UI -----------------
st.title("🇮🇳 Indian Stock Insights Dashboard")

# --- Sidebar controls ---
st.sidebar.header("Controls")
lookback = st.sidebar.selectbox("Lookback Period (for Movers)", ["7", "14", "30", "90"], index=2)
lookback_days = int(lookback)

search = st.sidebar.text_input("🔍 Search company / symbol")

# --- Display Movers ---
with st.spinner("Fetching top gainers & losers..."):
    movers = get_top_movers(lookback_days)

col1, col2 = st.columns(2)
col1.subheader(f"Top 10 Gainers (Last {lookback_days}D)")
col1.dataframe(movers.head(10))
fig1 = px.bar(movers.head(10), x="Ticker", y="% Change", color="% Change", title="Top Gainers", color_continuous_scale="greens")
col1.plotly_chart(fig1, use_container_width=True)

col2.subheader(f"Top 10 Losers (Last {lookback_days}D)")
col2.dataframe(movers.tail(10))
fig2 = px.bar(movers.tail(10), x="Ticker", y="% Change", color="% Change", title="Top Losers", color_continuous_scale="reds")
col2.plotly_chart(fig2, use_container_width=True)

# --- Heatmap ---
st.markdown("### 🔥 Heatmap of Stock Correlations")
top_n = movers.head(20)['Ticker'].tolist()
prices = get_prices(top_n, period="1mo")
returns = pd.DataFrame({t: calc_returns(df) for t, df in prices.items() if not df.empty})
corr = returns.corr()

fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(corr, cmap="coolwarm", ax=ax)
st.pyplot(fig)

# --- Company Search ---
st.markdown("---")
st.subheader("📈 Company Analysis")

if search:
    # Find closest ticker
    match = nse_df[nse_df['Company Name'].str.contains(search, case=False, na=False)]
    if match.empty:
        match = nse_df[nse_df['Ticker'].str.contains(search.upper(), na=False)]
    if match.empty:
        st.warning("No matching company found.")
    else:
        selected = match.iloc[0]['Ticker']
        st.success(f"Showing results for **{ticker_map[selected]} ({selected})**")

        colA, colB = st.columns(2)
        with colA:
            st.write("Last 30 Days Performance")
            hist_30 = yf.download(selected, period="1mo", interval="1d")
            fig = px.line(hist_30, x=hist_30.index, y="Adj Close", title="Last 30 Days")
            st.plotly_chart(fig, use_container_width=True)
        with colB:
            st.write("Last 7 Days Performance")
            hist_7 = yf.download(selected, period="7d", interval="1d")
            fig = px.line(hist_7, x=hist_7.index, y="Adj Close", title="Last 7 Days")
            st.plotly_chart(fig, use_container_width=True)

        # News & sentiment
        st.subheader("📰 Latest News & Sentiment")
        news = fetch_news(ticker_map[selected])
        if not news:
            st.info("No recent news found.")
        else:
            news_df = sentiment_summary(news)
            st.dataframe(news_df)

            avg_sentiment = news_df["Sentiment"].mean()
            if avg_sentiment > 0.05:
                sentiment_label = "🟢 Positive"
            elif avg_sentiment < -0.05:
                sentiment_label = "🔴 Negative"
            else:
                sentiment_label = "🟡 Neutral"
            st.metric("Overall Sentiment", sentiment_label, f"{avg_sentiment:.2f}")

else:
    st.info("Search a company name or symbol in the sidebar to view insights.")
