import streamlit as st
import pandas as pd
import numpy as np
import re
import time

SAMPLE_PATH = "/mnt/data/MF Sample data.xlsx"   # your uploaded file path (for demo)

# -------------------------
# Helper functions (same as before, with small additions)
# -------------------------
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

def detect_and_convert_numeric(df, log):
    df = df.copy()
    obj_cols = df.select_dtypes(include="object").columns
    converted = []
    for col in obj_cols:
        sample = df[col].dropna().astype(str).head(20).tolist()
        if not sample:
            continue
        numeric_like = 0
        for s in sample:
            s2 = strip_money_percent(s)
            if re.fullmatch(r"-?\d+(\.\d+)?%?$", s2):
                numeric_like += 1
        if numeric_like >= max(3, len(sample)//2):   # heuristic
            before_nonnull = df[col].notna().sum()
            df[col] = auto_numeric(df[col])
            after_nonnull = df[col].notna().sum()
            converted.append((col, before_nonnull, after_nonnull))
            log.append(f"Converted column '{col}' from object -> numeric (non-null: {before_nonnull} -> {after_nonnull})")
    return df, converted

def convert_dates(df, log):
    df = df.copy()
    converted = []
    for col in df.columns:
        if df[col].dtype == "object":
            # try parse
            parsed = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
            # if significant number parsed -> convert
            non_null_parsed = parsed.notna().sum()
            if non_null_parsed >= max(3, int(len(df) * 0.05)):  # >= 5% rows or >=3 rows
                df[col] = parsed
                converted.append((col, non_null_parsed))
                log.append(f"Parsed column '{col}' as datetime (parsed {non_null_parsed} values)")
    return df, converted

def fill_missing(df, log):
    df = df.copy()
    # numeric median, categorical mode
    num_cols = df.select_dtypes(include=np.number).columns
    cat_cols = df.select_dtypes(include="object").columns
    for col in num_cols:
        n_missing = df[col].isna().sum()
        if n_missing:
            median = df[col].median()
            df[col].fillna(median, inplace=True)
            log.append(f"Filled {n_missing} missing values in numeric column '{col}' with median = {median}")
    for col in cat_cols:
        n_missing = df[col].isna().sum()
        if n_missing:
            try:
                mode = df[col].mode().iloc[0]
                df[col].fillna(mode, inplace=True)
                log.append(f"Filled {n_missing} missing values in categorical column '{col}' with mode = '{mode}'")
            except Exception:
                df[col].fillna("", inplace=True)
                log.append(f"Filled {n_missing} missing values in categorical column '{col}' with empty string")
    return df

def remove_duplicates(df, log):
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df)
    if removed:
        log.append(f"Removed {removed} exact duplicate rows")
    else:
        log.append("No exact duplicate rows found")
    return df, removed

def flag_outliers(df, log):
    df = df.copy()
    num_cols = df.select_dtypes(include=np.number).columns
    added = []
    for col in num_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        out_col = f"{col}_is_outlier"
        df[out_col] = ((df[col] < low) | (df[col] > high)).astype(int)
        added.append(out_col)
        log.append(f"Flagged outliers in '{col}' -> new column '{out_col}' (low={low:.3f}, high={high:.3f})")
    return df, added

def standardize_text(df, log):
    df = df.copy()
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        before_sample = df[col].dropna().astype(str).head(3).tolist()
        df[col] = df[col].astype(str).str.strip().str.title()
        after_sample = df[col].dropna().astype(str).head(3).tolist()
        log.append(f"Standardized text in '{col}' (sample before -> after): {before_sample} -> {after_sample}")
    return df

# -------------------------
# UI
# -------------------------
st.set_page_config(layout="wide")
st.title("🧹 Advanced Auto Data Cleaner — Custom Controls & Step Log")

uploaded_file = st.file_uploader("Upload dataset (CSV/XLSX) or leave empty to use sample", type=["csv","xlsx"])
use_sample = False
if uploaded_file is None:
    st.info("No file uploaded — using sample dataset for demo. (You can still upload your own file.)")
    use_sample = True

# ===== Replace your old checkbox block with this safe version =====
# initialize checkbox keys only once
checkbox_keys = ["clean_cols", "numeric_fix", "date_fix", "missing_fix", "dup_fix", "outlier_fix", "text_fix"]

for k in ["select_all"] + checkbox_keys:
    if k not in st.session_state:
        st.session_state[k] = False

col1, col2 = st.columns([1, 3])
with col1:
    st.header("Cleaning Steps")

   # Create the Select ALL widget first (rendered by Streamlit)
    select_all = st.checkbox("Select ALL", value=st.session_state.get("select_all", False), key="select_all")

    # Render the individual checkboxes using session_state as default values
    # Important: use key param so Streamlit can manage widget-state. Don't assign st.session_state[...] = st.checkbox(...)
    st.session_state["clean_cols"]   = st.checkbox("Clean column names", key="clean_cols", value=st.session_state["clean_cols"])
    st.session_state["numeric_fix"]  = st.checkbox("Convert numeric-like columns", key="numeric_fix", value=st.session_state["numeric_fix"])
    st.session_state["date_fix"]     = st.checkbox("Convert date columns", key="date_fix", value=st.session_state["date_fix"])
    st.session_state["missing_fix"]  = st.checkbox("Fill missing values", key="missing_fix", value=st.session_state["missing_fix"])
    st.session_state["dup_fix"]      = st.checkbox("Remove duplicates", key="dup_fix", value=st.session_state["dup_fix"])
    st.session_state["outlier_fix"]  = st.checkbox("Flag outliers", key="outlier_fix", value=st.session_state["outlier_fix"])
    st.session_state["text_fix"]     = st.checkbox("Standardize text columns", key="text_fix", value=st.session_state["text_fix"])

    # Now apply the select-all/unselect-all logic (after widgets are created)
    if select_all:
        # set all to True
        for k in checkbox_keys:
            st.session_state[k] = True
    else:
        # optional: if user unchecks Select ALL, uncheck everything
        # remove the following block if you want manual selections to remain after unchecking Select ALL
        for k in checkbox_keys:
            if st.session_state[k] and not select_all:
                st.session_state[k] = False


col1, col2 = st.columns([1,3])
with col1:
    st.header("Cleaning Steps")
    st.session_state["select_all"] = st.checkbox("Select ALL", key="select_all")
    # when select_all toggled, set other checkboxes accordingly
    if st.session_state["select_all"]:
        st.session_state["clean_cols"] = True
        st.session_state["numeric_fix"] = True
        st.session_state["date_fix"] = True
        st.session_state["missing_fix"] = True
        st.session_state["dup_fix"] = True
        st.session_state["outlier_fix"] = True
        st.session_state["text_fix"] = True
    # individual controls (bound to session_state keys)
    st.session_state["clean_cols"] = st.checkbox("Clean column names", key="clean_cols", value=st.session_state["clean_cols"])
    st.session_state["numeric_fix"] = st.checkbox("Convert numeric-like columns", key="numeric_fix", value=st.session_state["numeric_fix"])
    st.session_state["date_fix"] = st.checkbox("Convert date columns", key="date_fix", value=st.session_state["date_fix"])
    st.session_state["missing_fix"] = st.checkbox("Fill missing values", key="missing_fix", value=st.session_state["missing_fix"])
    st.session_state["dup_fix"] = st.checkbox("Remove duplicates", key="dup_fix", value=st.session_state["dup_fix"])
    st.session_state["outlier_fix"] = st.checkbox("Flag outliers", key="outlier_fix", value=st.session_state["outlier_fix"])
    st.session_state["text_fix"] = st.checkbox("Standardize text columns", key="text_fix", value=st.session_state["text_fix"])

with col2:
    st.header("Preview / Action")
    if use_sample:
        try:
            df = pd.read_excel(SAMPLE_PATH)
        except Exception as e:
            st.error(f"Could not load sample file at {SAMPLE_PATH}: {e}")
            df = pd.DataFrame()
    else:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

    st.subheader("Raw Data (first 5 rows)")
    st.dataframe(df.head())

    run_button = st.button("🚀 Run Selected Cleaning Steps")

if run_button:
    # Prepare log
    change_log = []
    df_work = df.copy()

    # small delay to simulate processing and make UX clear
    with st.spinner("Running cleaning steps (this will take ~5 seconds)..."):
        # Step 1: clean colnames
        if st.session_state["clean_cols"]:
            before_cols = df_work.columns.tolist()
            df_work = clean_colnames(df_work)
            after_cols = df_work.columns.tolist()
            change_log.append(f"Cleaned column names: {before_cols} -> {after_cols}")

        # Step 2: numeric conversion
        if st.session_state["numeric_fix"]:
            df_work, conv = detect_and_convert_numeric(df_work, change_log)

        # Step 3: date conversion
        if st.session_state["date_fix"]:
            df_work, dconv = convert_dates(df_work, change_log)

        # simulate time (user requested 5 sec)
        time.sleep(5)

        # Step 4: fill missing
        if st.session_state["missing_fix"]:
            df_work = fill_missing(df_work, change_log)

        # Step 5: remove duplicates
        removed = 0
        if st.session_state["dup_fix"]:
            df_work, removed = remove_duplicates(df_work, change_log)

        # Step 6: flag outliers
        if st.session_state["outlier_fix"]:
            df_work, added_outcols = flag_outliers(df_work, change_log)

        # Step 7: standardize text
        if st.session_state["text_fix"]:
            df_work = standardize_text(df_work, change_log)

    st.success("Cleaning completed ✅")

    # Show Change Log
    st.subheader("📝 Change Log (what was done)")
    if change_log:
        for i, line in enumerate(change_log, start=1):
            st.write(f"{i}. {line}")
    else:
        st.write("No cleaning steps were selected, so nothing was changed.")

    # Show cleaned preview and allow download
    st.subheader("Cleaned Data Preview (first 8 rows)")
    st.dataframe(df_work.head(8))

    cleaned_csv = df_work.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download cleaned CSV", cleaned_csv, file_name="cleaned_dataset.csv", mime="text/csv")
