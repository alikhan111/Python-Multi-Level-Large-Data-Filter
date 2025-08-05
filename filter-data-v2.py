import streamlit as st
import pandas as pd
import requests
import io
import re

# Configuration
BACKEND_URL = "http://your-backend-url:8000"  # Replace with your actual backend URL
MAX_STREAMLIT_SIZE = 200 * 1024 * 1024  # 200MB

st.set_page_config(page_title="Large CSV Filter", layout="wide")
st.title("\U0001F4E6 Large CSV Filter (Cloud Powered)")

# --- Upload Section ---
st.markdown("### \U0001F4C2 Upload Your CSV File")
uploaded_file = st.file_uploader(
    "Drop a CSV file here (any size)",
    type=["csv"],
    accept_multiple_files=False,
    label_visibility="collapsed"
)

if uploaded_file:
    file_size = uploaded_file.size
    if file_size > MAX_STREAMLIT_SIZE:
        st.info("ℹ️ Large file detected - Using cloud processing backend")
        use_backend = True
    else:
        use_backend = False

    has_header = st.checkbox("CSV has a header row?", value=True)
    match_type = st.radio(
        "Match type:",
        ["Exact Match", "Contains Match (case-insensitive)"]
    )
    regex_mode = st.checkbox("Enable Regex Filtering (Advanced)", value=False)

    # Filter UI (same as before)
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
        # Get columns for filter dropdown
        try:
            if use_backend:
                # For large files, get just the header
                sample_bytes = uploaded_file.read(1024*1024)  # Read first 1MB to get headers
                uploaded_file.seek(0)
                sample_str = io.StringIO(sample_bytes.decode('utf-8', errors='ignore'))
                df_sample = pd.read_csv(sample_str) if has_header else pd.read_csv(sample_str, header=None)
                if not has_header:
                    df_sample.columns = [f"Column {i+1}" for i in range(df_sample.shape[1])]
                column_names = list(df_sample.columns)
            else:
                # For small files, read the whole file
                content = uploaded_file.read()
                uploaded_file.seek(0)
                file = io.StringIO(content.decode('utf-8', errors='ignore'))
                df = pd.read_csv(file) if has_header else pd.read_csv(file, header=None)
                if not has_header:
                    df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
                column_names = list(df.columns)
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

        # Render filters (same as before)
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

    # Process when filters are applied
    if any(f['val'] for f in st.session_state.filters):
        if use_backend:
            # Send to backend for processing
            with st.spinner("Processing large file in the cloud..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                    data = {
                        'has_header': has_header,
                        'match_type': match_type,
                        'regex_mode': regex_mode,
                        'filters': st.session_state.filters
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/filter-csv",
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Total Rows Scanned: {result['original_count']} | Matches Found: {result['match_count']}")
                        
                        # Display preview
                        df_preview = pd.read_csv(io.StringIO(result['csv_data']))
                        st.markdown("### 📊 Filtered Results Preview (First 5 Rows):")
                        st.dataframe(df_preview.head(5), use_container_width=True)
                        
                        # Download button
                        st.download_button(
                            "📅 Download Full Filtered CSV",
                            data=result['csv_data'],
                            file_name="filtered_output.csv"
                        )
                    else:
                        st.error(f"Backend error: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error processing file: {e}")
        
        else:
            # Process small files locally
            content = uploaded_file.read()
            uploaded_file.seek(0)
            file = io.StringIO(content.decode('utf-8', errors='ignore'))
            df = pd.read_csv(file) if has_header else pd.read_csv(file, header=None)
            if not has_header:
                df.columns = [f"Column {i+1}" for i in range(df.shape[1])]
            
            original_count = len(df)
            
            # Apply filters
            for f in st.session_state.filters:
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
            
            if match_count > 0:
                st.success(f"✅ Total Rows Scanned: {original_count} | Matches Found: {match_count}")
                st.markdown("### 📊 Filtered Results Preview (First 5 Rows):")
                st.dataframe(df.head(5), use_container_width=True)
                
                csv_output = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📅 Download Full Filtered CSV",
                    csv_output,
                    file_name="filtered_output.csv"
                )
            else:
                st.warning("⚠️ No matches found.")
else:
    st.info("ℹ️ Upload a CSV file to begin filtering.")
