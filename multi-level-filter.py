import streamlit as st
import pandas as pd
import zipfile
import os
import tempfile
import io
import re

st.set_page_config(page_title="Multi-File CSV Filter", layout="wide")
st.title("\U0001F4E6 Multi-File Filter")

# --- Upload Section ---
st.markdown("### \U0001F4C2 Upload Your Files")
uploaded_files = st.file_uploader(
    "Drop ZIP or CSV files here",
    type=["csv", "zip"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# --- Instructions if no files uploaded ---
if not uploaded_files:
    st.markdown("""
    ### \U0001F527 What You Can Do:
    - \U0001F4C4 **Upload** one or more CSV files, or a ZIP file containing multiple CSVs  
    - \U0001F50E **Search through hundreds of files** simultaneously.
    - \U0001F4BD **Great for large datasets** handling right up to multiple 200MB+ files  
    - \U0001F4CB **Apply light to heavy filters** up to the first 10 columns  
    - \u2B07 **Download results instantly** once matched
    - \U0001F4BE **ZIP and CSV** can be uploaded together.
    - \U0001F440 **Apply custom regular expressions** done per filter value

     ### \U0001F3C6 Who Can Use This:
    - \U0001F4B0 **eCommerce sellers** (Amazon, Shopify): filter product/sales data  
    - \U0001F393 **Researchers/academics** clean/filter CSVs for studies  
    - \U0001F3AF **Marketers** filter campaign data, leads, or tracking results  
    - \U0001F9E0 **Data analysts/freelancers** quick filtering/cleaning before analysis               
    - \U0001F4B9 **Financial traders** filter large market data files 
                
    ### \U0001F525 Supported:
    - \u26A1 ZIP with multiple CSVs  
    - \U0001F4C4 Individual CSVs  
    - \U0001F503 With or without headers
    
    ### \U0001F525 Contact:
    - \U0001F9F2 For bespoke code contact: Ali Khan  
    - \U0001F4E7 alikhan111@gmail.com  
    - \U0001F9E0 Abily to handle multiple large files at the same time.      
    
    """)

# --- File Extraction ---
all_files = []

if uploaded_files:
    with tempfile.TemporaryDirectory() as tmpdir:
        for uploaded in uploaded_files:
            if uploaded.name.endswith(".zip"):
                try:
                    with zipfile.ZipFile(uploaded, 'r') as zip_ref:
                        zip_ref.extractall(tmpdir)
                        for filename in os.listdir(tmpdir):
                            if filename.endswith(".csv"):
                                filepath = os.path.join(tmpdir, filename)
                                with open(filepath, 'rb') as f:
                                    content = f.read()
                                    all_files.append((filename, content))
                except zipfile.BadZipFile:
                    st.error(f"❌ {uploaded.name} is not a valid ZIP file.")
            elif uploaded.name.endswith(".csv"):
                content = uploaded.read()
                all_files.append((uploaded.name, content))

if all_files:
    has_header = st.checkbox("CSV files have a header row?", value=True)
    match_type = st.radio(
        "Match type:",
        ["Exact Match", "Contains Match (case-insensitive)"]
    )
    regex_mode = st.checkbox("Enable Regex Filtering (Advanced Users)", value=False)

    # Validate that all headers match
    header_set = set()
    for name, content in all_files:
        try:
            file = io.StringIO(content.decode('utf-8', errors='ignore'))
            df = pd.read_csv(file) if has_header else pd.read_csv(file, header=None)
            if not has_header:
                df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
            header_set.add(tuple(df.columns))
        except Exception as e:
            st.error(f"Error reading file {name}: {e}")
            st.stop()

    if len(header_set) > 1:
        st.error("❌ CSV files do not have matching headers. Please ensure all uploaded files share the same column structure.")
        st.stop()

    column_names = list(header_set.pop())

    if 'filters' not in st.session_state:
        st.session_state.filters = []

    def add_filter(index=None):
        new_filter = {'col': None, 'val': ''}
        if index is None:
            st.session_state.filters.append(new_filter)
        else:
            st.session_state.filters.insert(index, new_filter)

    def remove_filter(index):
        if 0 <= index < len(st.session_state.filters):
            st.session_state.filters.pop(index)
            st.rerun()

    if not st.session_state.filters:
        add_filter()

    with st.expander("🔍 Filter Criteria"):
        for i, f in enumerate(st.session_state.filters):
            cols = st.columns([3.5, 3.5, 0.7, 0.7, 0.7])
            selected_col = cols[0].selectbox("", column_names, index=column_names.index(f['col']) if f['col'] in column_names else 0, key=f"col_{i}", label_visibility="collapsed")
            input_val = cols[1].text_input("", value=f['val'], key=f"val_{i}", label_visibility="collapsed")

            if cols[2].button("⬆️", key=f"up_{i}") and i > 0:
                st.session_state.filters[i - 1], st.session_state.filters[i] = st.session_state.filters[i], st.session_state.filters[i - 1]
                st.rerun()

            if cols[3].button("⬇️", key=f"down_{i}") and i < len(st.session_state.filters) - 1:
                st.session_state.filters[i + 1], st.session_state.filters[i] = st.session_state.filters[i], st.session_state.filters[i + 1]
                st.rerun()

            if cols[4].button("❌", key=f"remove_{i}"):
                remove_filter(i)

            st.session_state.filters[i]['col'] = selected_col
            st.session_state.filters[i]['val'] = input_val

        st.markdown("---")
        if st.button("➕ Add Filter"):
            add_filter()
            st.rerun()

    def read_and_filter_csv(file_bytes, filters, has_header, match_type, regex_mode):
        try:
            file = io.StringIO(file_bytes.decode('utf-8', errors='ignore'))
            df = pd.read_csv(file) if has_header else pd.read_csv(file, header=None)
            if not has_header:
                df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
            original_count = len(df)

            for f in filters:
                col_name = f['col']
                val = f['val']
                if col_name in df.columns and val:
                    series = df[col_name].astype(str)

                    if match_type == "Exact Match":
                        if '*' in val:
                            regex_pattern = '^' + re.escape(val).replace('\\*', '.*') + '$'
                            try:
                                df = df[series.str.contains(regex_pattern, case=False, na=False, regex=True)]
                            except re.error:
                                st.warning(f"⚠️ Invalid wildcard pattern in: {val}")
                        elif regex_mode:
                            try:
                                df = df[series.str.contains(val, case=False, na=False, regex=True)]
                            except re.error:
                                st.warning(f"⚠️ Invalid regex: {val}")
                        else:
                            df = df[series.str.strip() == val.strip()]

                    elif match_type == "Contains Match (case-insensitive)":
                        if val.startswith('[') and val.endswith(']'):
                            exact_val = val[1:-1].strip()
                            df = df[series.str.strip() == exact_val]
                        elif regex_mode:
                            try:
                                df = df[series.str.contains(val, case=False, na=False, regex=True)]
                            except re.error:
                                st.warning(f"⚠️ Invalid regex: {val}")
                        else:
                            df = df[series.str.contains(val, case=False, na=False)]

            match_count = len(df)
            return df, original_count, match_count
        except Exception as e:
            st.error(f"Error processing file: {e}")
            return pd.DataFrame(), 0, 0

    def process_files(file_list, filters, has_header, match_type, regex_mode):
        total_entries = 0
        total_matches = 0
        all_filtered = []

        for name, content in file_list:
            df, total, match = read_and_filter_csv(content, filters, has_header, match_type, regex_mode)
            if not df.empty:
                all_filtered.append(df)
            total_entries += total
            total_matches += match

        return all_filtered, total_entries, total_matches

    if any(f['val'] for f in st.session_state.filters):
        filtered_data, total, matched = process_files(all_files, st.session_state.filters, has_header, match_type, regex_mode)

        if filtered_data:
            result_df = pd.concat(filtered_data, ignore_index=True)
            st.success(f"✅ Total Rows Scanned: {total} | Matches Found: {matched}")

            st.markdown("### 📊 Filtered Results Preview (First 5 Rows):")
            st.dataframe(result_df.head(5), use_container_width=True)
            st.caption("⚠️ Full filtered data is available in the download.")

            csv_output = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📅 Download Full Filtered CSV", csv_output, file_name="filtered_output.csv")
        else:
            st.warning("⚠️ No matches found.")
    else:
        st.info("ℹ️ Please enter at least one filter value to begin filtering.")

else:
    st.info("ℹ️ Upload CSV or ZIP files to begin.")
