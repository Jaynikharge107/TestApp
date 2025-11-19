import streamlit as st
import pandas as pd
import numpy as np
import re

# ----------------------------------------
# Helper Functions
# ----------------------------------------

def clean_colnames(df):
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r"[^\w\s]", "", regex=True)
                  .str.replace(r"\s+", "_", regex=True)
    )
    return df

def strip_money_percent(x):
    if pd.isna(x):
        return x
    s = str(x).strip()
    s = s.replace("₹","").replace("$","").replace(",","")
    s = s.replace("—","").replace("–","").replace("−","-")
    return s

def auto_numeric(series):
    cleaned = series.astype(str).map(strip_money_percent)
    cleaned = cleaned.replace({"nan": None, "": None})
    return pd.to_numeric(cleaned, errors="coerce")

def detect_and_convert_numeric(df):
    df = df.copy()
    obj_cols = df.select_dtypes(include="object").columns
    for col in obj_cols:
        sample = df[col].dropna().astype(str).head(20).tolist()
        numeric_like = 0
        for s in sample:
            s2 = strip_money_percent(s)
            if re.fullmatch(r"-?\d+(\.\d+)?%?$", s2):
                numeric_like += 1
        if numeric_like >= len(sample)//2:
            df[col] = auto_numeric(df[col])
    return df

def convert_dates(df):
    df = df.copy()
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="ignore", infer_datetime_format=True)
        except:
            pass
    return df

def fill_missing(df):
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(include="object").columns
    for col in num_cols:
        df[col].fillna(df[col].median(), inplace=True)
    for col in cat_cols:
        try:
            df[col].fillna(df[col].mode()[0], inplace=True)
        except:
            df[col].fillna("", inplace=True)
    return df

def remove_duplicates(df):
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    return df, removed

def flag_outliers(df):
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        df[f"{col}_is_outlier"] = ((df[col] < low) | (df[col] > high)).astype(int)
    return df

def standardize_text(df):
    df = df.copy()
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip().str.title()
    return df


# ----------------------------------------
# Streamlit UI
# ----------------------------------------

st.title("🧹 Advanced Auto Data Cleaner with Custom Controls")
st.write("Upload any CSV/Excel file and choose exactly what cleaning tasks you want to perform.")

uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:
    st.success("File uploaded successfully!")

    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📌 Raw Data Preview")
    st.dataframe(df.head())

    st.write("---")
    st.subheader("⚙️ Choose Cleaning Steps")

    clean_cols = st.checkbox("Clean Column Names")
    numeric_fix = st.checkbox("Convert Numeric-Like Columns")
    date_fix = st.checkbox("Convert Date Columns")
    missing_fix = st.checkbox("Fill Missing Values")
    dup_fix = st.checkbox("Remove Duplicates")
    outlier_fix = st.checkbox("Flag Outliers")
    text_fix = st.checkbox("Standardize Text Columns")
    select_all = st.checkbox("Select ALL Cleaning Steps")

    if select_all:
        clean_cols = numeric_fix = date_fix = missing_fix = dup_fix = outlier_fix = text_fix = True

    if st.button("🚀 Run Cleaning"):
        df_clean = df.copy()

        if clean_cols:
            df_clean = clean_colnames(df_clean)

        if numeric_fix:
            df_clean = detect_and_convert_numeric(df_clean)

        if date_fix:
            df_clean = convert_dates(df_clean)

        if missing_fix:
            df_clean = fill_missing(df_clean)

        removed = 0
        if dup_fix:
            df_clean, removed = remove_duplicates(df_clean)

        if outlier_fix:
            df_clean = flag_outliers(df_clean)

        if text_fix:
            df_clean = standardize_text(df_clean)

        st.subheader("🧼 Cleaned Data Preview")
        st.dataframe(df_clean.head())

        st.write(f"🗑️ Duplicates removed: **{removed} rows**")

        cleaned_csv = df_clean.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Cleaned CSV",
            data=cleaned_csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv"
        )
