# autoclean_app.py
import streamlit as st
import pandas as pd
import numpy as np
import re
import time

# ---------- CONFIG ----------
SAMPLE_PATH = "/mnt/data/MF Sample data.xlsx"  # local sample file (your uploaded file)
st.set_page_config(layout="wide", page_title="Advanced Auto Data Cleaner")

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

def strip_money_percent(x):
    if pd.isna(x):
        return x
    s = str(x).strip()
    for ch in ["₹", "$", ","]:
        s = s.replace(ch, "")
    for dash in ["—", "–", "−"]:
        s = s.replace(dash, "-")
    return s

def auto_numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).map(strip_money_percent)
    cleaned = cleaned.replace({"nan": None, "None": None, "": None})
    return pd.to_numeric(cleaned, errors="coerce")

def detect_and_convert_numeric(df: pd.DataFrame, log: list) -> (pd.DataFrame, list):
    df = df.copy()
    converted = []
    obj_cols = df.select_dtypes(include="object").columns.tolist()
    for col in obj_cols:
        sample = df[col].dropna().astype(str).head(30).tolist()
        if not sample:
            continue
        numeric_like = 0
        for s in sample:
            s2 = strip_money_percent(s)
            if re.fullmatch(r"-?\d+(\.\d+)?%?", s2):
                numeric_like += 1
        # heuristic: if half or at least 3 samples look numeric, convert
        if numeric_like >= max(3, len(sample)//2):
            before_nonnull = df[col].notna().sum()
            df[col] = auto_numeric(df[col])
            after_nonnull = df[col].notna().sum()
            converted.append((col, before_nonnull, after_nonnull))
            log.append(f"Converted '{col}' from object -> numeric (non-null: {before_nonnull} -> {after_nonnull})")
    return df, converted

def convert_dates(df: pd.DataFrame, log: list) -> (pd.DataFrame, list):
    df = df.copy()
    converted = []
    for col in df.columns:
        if df[col].dtype == "object":
            parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            non_null_parsed = parsed.notna().sum()
            if non_null_parsed >= max(3, int(len(df) * 0.05)):  # >=5% or >=3 rows
                df[col] = parsed
                converted.append((col, non_null_parsed))
                log.append(f"Parsed column '{col}' to datetime (parsed {non_null_parsed} values)")
    return df, converted

def fill_missing(df: pd.DataFrame, log: list) -> pd.DataFrame:
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(include="object").columns
    for col in num_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            median = df[col].median()
            df[col].fillna(median, inplace=True)
            log.append(f"Filled {n_missing} missing values in numeric '{col}' with median={median}")
    for col in cat_cols:
        n_missing = int(df[col].isna().sum())
        if n_missing:
            try:
                mode = df[col].mode().iloc[0]
                df[col].fillna(mode, inplace=True)
                log.append(f"Filled {n_missing} missing values in categorical '{col}' with mode='{mode}'")
            except Exception:
                df[col].fillna("", inplace=True)
                log.append(f"Filled {n_missing} missing values in categorical '{col}' with empty string")
    return df

def remove_duplicates(df: pd.DataFrame, log: list) -> (pd.DataFrame, int):
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    if removed:
        log.append(f"Removed {removed} exact duplicate rows")
    else:
        log.append("No exact duplicate rows found")
    return df, removed

def flag_outliers(df: pd.DataFrame, log: list) -> (pd.DataFrame, list):
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    added_cols = []
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        out_col = f"{col}_is_outlier"
        df[out_col] = ((df[col] < low) | (df[col] > high)).astype(int)
        added_cols.append(out_col)
        log.append(f"Flagged outliers for '{col}' -> new column '{out_col}' (low={low:.3f}, high={high:.3f})")
    return df, added_cols

def standardize_text(df: pd.DataFrame, log: list) -> pd.DataFrame:
    df = df.copy()
    text_cols = df.select_dtypes(include="object").columns.tolist()
    for col in text_cols:
        before_sample = df[col].dropna().astype(str).head(3).tolist()
        df[col] = df[col].astype(str).str.strip().str.title()
        after_sample = df[col].dropna().astype(str).head(3).tolist()
        log.append(f"Standardized text in '{col}' (sample before -> after): {before_sample} -> {after_sample}")
    return df

# ---------- UI ----------
st.title("🧹 Advanced Auto Data Cleaner — Custom Controls & Step Log")
st.markdown("Upload any CSV/XLSX file. Use the checkboxes to choose cleaning steps. "
            "Or use **Select ALL** to run all steps. A 5s delay simulates real processing and shows the change log.")

# initialize session_state safely
checkbox_keys = ["clean_cols", "numeric_fix", "date_fix", "missing_fix", "dup_fix", "outlier_fix", "text_fix"]
for k in ["select_all"] + checkbox_keys:
    if k not in st.session_state:
        st.session_state[k] = False

# two-column layout
col_left, col_right = st.columns([1, 3])

with col_left:
    st.header("Cleaning Steps")
    # create select_all checkbox widget and capture its value
    select_all = st.checkbox("Select ALL cleaning steps", value=st.session_state.get("select_all", False), key="select_all")
    # create individual checkboxes (Streamlit manages their state)
    st.session_state["clean_cols"] = st.checkbox("Clean column names", key="clean_cols", value=st.session_state["clean_cols"])
    st.session_state["numeric_fix"] = st.checkbox("Convert numeric-like columns", key="numeric_fix", value=st.session_state["numeric_fix"])
    st.session_state["date_fix"] = st.checkbox("Convert date columns", key="date_fix", value=st.session_state["date_fix"])
    st.session_state["missing_fix"] = st.checkbox("Fill missing values", key="missing_fix", value=st.session_state["missing_fix"])
    st.session_state["dup_fix"] = st.checkbox("Remove duplicates", key="dup_fix", value=st.session_state["dup_fix"])
    st.session_state["outlier_fix"] = st.checkbox("Flag outliers", key="outlier_fix", value=st.session_state["outlier_fix"])
    st.session_state["text_fix"] = st.checkbox("Standardize text columns", key="text_fix", value=st.session_state["text_fix"])

    # Apply Select ALL behavior AFTER widgets are created
    if select_all:
        for k in checkbox_keys:
            st.session_state[k] = True
    else:
        # if Select ALL is unchecked, keep user's manual selections
        # (if you want to force uncheck all when select_all False, uncomment below)
        # for k in checkbox_keys:
        #     st.session_state[k] = False
        pass

with col_right:
    st.header("Data Upload & Preview")
    uploaded_file = st.file_uploader("Upload dataset (CSV / XLSX). Leave empty to use sample.", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(".csv"):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Failed to read uploaded file: {e}")
            df_raw = pd.DataFrame()
    else:
        # try load sample file for demo
        try:
            df_raw = pd.read_excel(SAMPLE_PATH)
            st.info(f"Using sample dataset: {SAMPLE_PATH}")
        except Exception as e:
            st.warning("No file uploaded and sample not found. Upload a file to continue.")
            df_raw = pd.DataFrame()

    st.subheader("Raw Data (first 5 rows)")
    st.dataframe(df_raw.head())

    run_button = st.button("🚀 Run Selected Cleaning Steps")

# ---------- RUN cleaning ----------
if run_button:
    if df_raw.empty:
        st.error("No data available to clean. Upload a file or place sample at the configured path.")
    else:
        change_log = []
        df_work = df_raw.copy()

        with st.spinner("Running cleaning steps (simulating processing, please wait ~5 seconds)..."):
            # Step 1: clean column names
            if st.session_state["clean_cols"]:
                before_cols = df_work.columns.tolist()
                df_work = clean_colnames(df_work)
                after_cols = df_work.columns.tolist()
                change_log.append(f"Cleaned column names: {before_cols} -> {after_cols}")

            # Step 2: numeric conversion
            if st.session_state["numeric_fix"]:
                df_work, converted = detect_and_convert_numeric(df_work, change_log)
                if converted:
                    for c, b, a in converted:
                        # descriptive entry already added in detect_and_convert_numeric
                        pass

            # Step 3: date conversion
            if st.session_state["date_fix"]:
                df_work, date_conv = convert_dates(df_work, change_log)
                if date_conv:
                    for c, n in date_conv:
                        pass

            # simulate processing time so user sees spinner and log
            time.sleep(5)

            # Step 4: fill missing
            if st.session_state["missing_fix"]:
                df_work = fill_missing(df_work, change_log)

            # Step 5: remove duplicates
            removed = 0
            if st.session_state["dup_fix"]:
                df_work, removed = remove_duplicates(df_work, change_log)

            # Step 6: flag outliers
            added_outcols = []
            if st.session_state["outlier_fix"]:
                df_work, added_outcols = flag_outliers(df_work, change_log)

            # Step 7: standardize text
            if st.session_state["text_fix"]:
                df_work = standardize_text(df_work, change_log)

        st.success("Cleaning completed ✅")

        # Show Change Log
        st.subheader("📝 Change Log (what was done)")
        if change_log:
            for i, line in enumerate(change_log, 1):
                st.write(f"{i}. {line}")
        else:
            st.write("No cleaning steps selected.")

        # Show cleaned preview and allow download
        st.subheader("Cleaned Data Preview (first 10 rows)")
        st.dataframe(df_work.head(10))

        cleaned_csv = df_work.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Cleaned CSV", cleaned_csv, file_name="cleaned_dataset.csv", mime="text/csv")
