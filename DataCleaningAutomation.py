# autoclean_app.py
import streamlit as st
import pandas as pd
import numpy as np
import re
import time
from typing import Tuple

# ---------- CONFIG ----------
SAMPLE_PATH = "/mnt/data/MF Sample data.xlsx"  # sample/demo file (change if needed)
st.set_page_config(layout="wide", page_title="Safe Auto Data Cleaner")

# ---------- HELPERS ----------
def clean_colnames(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r"[^\w\s]", "", regex=True)
                  .str.replace(r"\s+", "_", regex=True)
    )
    return df

def strip_money_percent_and_units(x: str) -> str:
    """Remove currency, commas, percent, and simple units like km/h, mph, km, m, hrs, s."""
    if pd.isna(x):
        return x
    s = str(x).strip()
    # remove currency and commas
    s = re.sub(r"[₹$,]", "", s)
    # common units (space or appended) -> remove but keep numeric sign and decimals
    s = re.sub(r"\b(km/h|kmh|mph|km|m|kwh|kw|rpm|hrs|hr|s|sec|min)\b", "", s, flags=re.I)
    s = s.replace("—", "").replace("–", "").replace("−", "-")
    return s.strip()

def looks_like_number_sample(sample_vals: list) -> int:
    count = 0
    for v in sample_vals:
        s = strip_money_percent_and_units(v or "")
        if re.fullmatch(r"-?\d+(\.\d+)?%?", s):
            count += 1
    return count

def looks_like_date_sample(sample_vals: list) -> int:
    """Simple regex-based date detection (common formats)"""
    date_patterns = [
        r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$",    # 2020-01-05 or 2020/01/05
        r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}$",  # 05-01-2020 or 5/1/20
        r"^[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}$",# Jan 5, 2020
        r"^\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}$", # 5 Jan 2020
    ]
    count = 0
    for v in sample_vals:
        s = str(v).strip()
        for pat in date_patterns:
            if re.match(pat, s):
                count += 1
                break
        # also check for month names inside value (e.g., "Jan", "January")
        if any(m in s.lower() for m in ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]):
            count += 1
    return count

def detect_column_types(df: pd.DataFrame, sample_n: int = 50) -> pd.DataFrame:
    """Return a dataframe with detected types: 'numeric','date','text' with confidence metrics."""
    rows = []
    n_rows = len(df)
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(sample_n).tolist()
        numeric_like = looks_like_number_sample(sample)
        date_like = looks_like_date_sample(sample)
        unique_ratio = df[col].nunique(dropna=True) / max(1, n_rows)
        dtype = str(df[col].dtype)
        # Heuristics:
        # - If dtype is numeric -> numeric
        # - If many numeric_like and low date_like -> numeric
        # - If many date_like and numeric_like is low -> date
        # - Else text
        if np.issubdtype(df[col].dtype, np.number):
            detected = "numeric"
        elif date_like >= max(3, len(sample)//10) and date_like > numeric_like:
            detected = "date"
        elif numeric_like >= max(3, len(sample)//2) and numeric_like > date_like:
            detected = "numeric"
        else:
            detected = "text"
        rows.append({
            "column": col,
            "dtype_before": dtype,
            "detected": detected,
            "numeric_like": numeric_like,
            "date_like": date_like,
            "unique_ratio": round(unique_ratio, 3)
        })
    return pd.DataFrame(rows)

def auto_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).map(strip_money_percent_and_units)
    cleaned = cleaned.replace({"nan": None, "None": None, "": None})
    # remove ending '%' if present
    cleaned = cleaned.str.replace("%", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")

def safe_convert_numeric(df: pd.DataFrame, cols: list, log: list) -> Tuple[pd.DataFrame, list]:
    df = df.copy()
    converted = []
    for col in cols:
        before_nonnull = int(df[col].notna().sum())
        df[col] = auto_numeric(df[col])
        after_nonnull = int(df[col].notna().sum())
        converted.append((col, before_nonnull, after_nonnull))
        log.append(f"Converted '{col}' -> numeric (non-null: {before_nonnull} -> {after_nonnull})")
    return df, converted

def safe_convert_dates(df: pd.DataFrame, cols: list, log: list) -> Tuple[pd.DataFrame, list]:
    df = df.copy()
    converted = []
    for col in cols:
        parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        non_null = int(parsed.notna().sum())
        # only keep parsed column if a meaningful number parsed
        if non_null >= max(3, int(len(df) * 0.05)):  # >=3 or >=5% of rows
            df[col] = parsed
            converted.append((col, non_null))
            log.append(f"Converted '{col}' -> datetime (parsed {non_null} values)")
        else:
            log.append(f"Skipped converting '{col}' to datetime (parsed {non_null} out of {len(df)})")
    return df, converted

def fill_missing(df: pd.DataFrame, numeric_strategy="median", cat_strategy="mode", log: list = None) -> pd.DataFrame:
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(include="object").columns
    for col in num_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            if numeric_strategy == "median":
                val = df[col].median()
            elif numeric_strategy == "mean":
                val = df[col].mean()
            else:
                val = 0
            df[col].fillna(val, inplace=True)
            if log is not None:
                log.append(f"Filled {n_missing} missing values in numeric '{col}' with {numeric_strategy}={val}")
    for col in cat_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            try:
                val = df[col].mode().iloc[0]
            except:
                val = ""
            df[col].fillna(val, inplace=True)
            if log is not None:
                log.append(f"Filled {n_missing} missing values in text '{col}' with mode='{val}'")
    return df

def remove_duplicates(df: pd.DataFrame, log: list = None) -> Tuple[pd.DataFrame,int]:
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    if log is not None:
        log.append(f"Removed {removed} exact duplicate rows")
    return df, removed

def flag_outliers(df: pd.DataFrame, log: list = None) -> Tuple[pd.DataFrame,list]:
    df = df.copy()
    added = []
    num_cols = df.select_dtypes(include=np.number).columns
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        out_col = f"{col}_is_outlier"
        df[out_col] = ((df[col] < low) | (df[col] > high)).astype(int)
        added.append(out_col)
        if log is not None:
            log.append(f"Flagged outliers in '{col}' -> new column '{out_col}'")
    return df, added

def standardize_text(df: pd.DataFrame, log: list = None) -> pd.DataFrame:
    df = df.copy()
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        before = df[col].dropna().astype(str).head(3).tolist()
        df[col] = df[col].astype(str).str.strip().str.title()
        after = df[col].dropna().astype(str).head(3).tolist()
        if log is not None:
            log.append(f"Standardized text in '{col}' (sample: {before} -> {after})")
    return df

# ---------- UI ----------
st.title("⚠️ Safe Auto Data Cleaner — EV-ready")
st.markdown("""
Upload a dataset (CSV / XLSX).  
This app *detects* column types and lets you **confirm or override** before cleaning — prevents wrong conversions (like speed → datetime).  
Sample path used for demo: `SAMPLE_PATH = {}`  
""".format(SAMPLE_PATH))

# Upload / Load
uploaded_file = st.file_uploader("Upload your file (CSV/XLSX). Leave empty to use sample file for preview.", type=["csv","xlsx"])
if uploaded_file is None:
    try:
        df_raw = pd.read_excel(SAMPLE_PATH)
        st.info(f"Using sample dataset at: {SAMPLE_PATH}")
    except Exception:
        df_raw = pd.DataFrame()
        st.warning("No sample found. Upload a dataset to proceed.")
else:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Failed to read uploaded file: {e}")
        df_raw = pd.DataFrame()

if df_raw.empty:
    st.stop()

# Show raw preview
st.subheader("Raw Data (first 5 rows)")
st.dataframe(df_raw.head())

# Detect types
st.subheader("Detected column types (auto)")
det_df = detect_column_types(df_raw)
# allow user override: radio for each column with default = detected
st.write("If a column looks misclassified (e.g., 'speed' detected as date), change it below before cleaning.")
override_cols = {}
cols_ui = []
for i, row in det_df.iterrows():
    col = row['column']
    detected = row['detected']
    cols_ui.append(col)
    override_cols[col] = st.radio(
        f"Column: {col} (detected: {detected})",
        options=["auto", "numeric", "date", "text"],
        index=0 if detected=="text" else (1 if detected=="numeric" else 2) if detected=="date" else 0,
        key=f"col_override_{i}",
        horizontal=True
    )

# Checkboxes and select all logic (safe session_state pattern)
checkbox_keys = ["clean_names", "convert_numeric", "convert_dates", "fill_missing", "remove_dupes", "flag_outliers", "standardize_text"]
for k in checkbox_keys:
    if k not in st.session_state:
        st.session_state[k] = False

col_left, col_right = st.columns([1, 3])
with col_left:
    st.header("Cleaning Steps")
    sel_all = st.checkbox("Select ALL cleaning steps", key="select_all")
    st.session_state["clean_names"] = st.checkbox("Clean column names", key="clean_names", value=st.session_state["clean_names"])
    st.session_state["convert_numeric"] = st.checkbox("Convert numeric-like columns", key="convert_numeric", value=st.session_state["convert_numeric"])
    st.session_state["convert_dates"] = st.checkbox("Convert date columns", key="convert_dates", value=st.session_state["convert_dates"])
    st.session_state["fill_missing"] = st.checkbox("Fill missing values", key="fill_missing", value=st.session_state["fill_missing"])
    st.session_state["remove_dupes"] = st.checkbox("Remove duplicates", key="remove_dupes", value=st.session_state["remove_dupes"])
    st.session_state["flag_outliers"] = st.checkbox("Flag outliers", key="flag_outliers", value=st.session_state["flag_outliers"])
    st.session_state["standardize_text"] = st.checkbox("Standardize text columns", key="standardize_text", value=st.session_state["standardize_text"])

    if sel_all:
        for k in checkbox_keys:
            st.session_state[k] = True

with col_right:
    st.header("Preview & Run")
    st.write("Review auto-detection above, set overrides for any column, pick steps on the left, then Run.")

if st.button("🚀 Run Cleaning (with overrides)"):
    log = []
    df_work = df_raw.copy()

    # 1: Clean column names if requested (do BEFORE mapping overrides to avoid mismatch)
    if st.session_state["clean_names"]:
        before_cols = df_work.columns.tolist()
        df_work = clean_colnames(df_work)
        after_cols = df_work.columns.tolist()
        log.append(f"Cleaned column names: {before_cols} -> {after_cols}")
        # need to remap override keys to cleaned names: recompute det_df and override mapping
        # Build mapping old->new quickly
        mapping = dict(zip(before_cols, after_cols))
        new_override = {}
        for old_col, choice in override_cols.items():
            new_col = mapping.get(old_col, old_col)
            new_override[new_col] = choice
        override_cols = new_override

    # Determine final lists to convert based on detection + overrides
    numeric_cols = []
    date_cols = []
    text_cols = []
    for col, choice in override_cols.items():
        if choice == "auto":
            # use our initial detection (recompute if names changed)
            det_row = det_df[det_df['column'] == col]
            if not det_row.empty:
                picked = det_row.iloc[0]['detected']
            else:
                # fallback: check dtype
                picked = "numeric" if np.issubdtype(df_work[col].dtype, np.number) else "text"
            choice_final = picked
        else:
            choice_final = choice

        if choice_final == "numeric":
            numeric_cols.append(col)
        elif choice_final == "date":
            date_cols.append(col)
        else:
            text_cols.append(col)

    # Simulate processing & show spinner
    with st.spinner("Cleaning in progress (simulating ~5 seconds)..."):
        # Convert numeric columns
        if st.session_state["convert_numeric"] and numeric_cols:
            df_work, converted = safe_convert_numeric(df_work, numeric_cols, log)

        # Convert dates with safe check
        if st.session_state["convert_dates"] and date_cols:
            df_work, date_converted = safe_convert_dates(df_work, date_cols, log)

        # simulate processing time
        time.sleep(5)

        # Fill missing
        if st.session_state["fill_missing"]:
            df_work = fill_missing(df_work, log=log)

        # Remove duplicates
        removed = 0
        if st.session_state["remove_dupes"]:
            df_work, removed = remove_duplicates(df_work, log=log)

        # Flag outliers
        added_out = []
        if st.session_state["flag_outliers"]:
            df_work, added_out = flag_outliers(df_work, log=log)

        # Standardize text
        if st.session_state["standardize_text"]:
            df_work = standardize_text(df_work, log=log)

    st.success("Cleaning completed ✅")

    st.subheader("📝 Change Log (what was done)")
    if log:
        for i, line in enumerate(log, 1):
            st.write(f"{i}. {line}")
    else:
        st.write("No steps performed.")

    st.subheader("Cleaned Data Preview (first 10 rows)")
    st.dataframe(df_work.head(10))

    csv_bytes = df_work.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download cleaned CSV", csv_bytes, "cleaned_dataset.csv", "text/csv")

