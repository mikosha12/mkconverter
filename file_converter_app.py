import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📁 File Converter", layout="centered")

st.title("🔄 Excel ⇄ CSV File Converter")

# --- Stylish Toggle Buttons Using Columns ---
st.subheader("Step 1: Choose Conversion Direction")

if "conversion_type" not in st.session_state:
    st.session_state.conversion_type = "Excel ➜ CSV"

col1, col2 = st.columns(2)

with col1:
    if st.button("📤 Excel ➜ CSV"):
        st.session_state.conversion_type = "Excel ➜ CSV"

with col2:
    if st.button("📥 CSV ➜ Excel"):
        st.session_state.conversion_type = "CSV ➜ Excel"

st.markdown(f"**🟢 Selected:** `{st.session_state.conversion_type}`")

# --- File Upload Based on Selection ---
st.subheader("Step 2: Upload Your File")

file_types = ["xlsx", "xls"] if st.session_state.conversion_type == "Excel ➜ CSV" else ["csv"]
uploaded_file = st.file_uploader("Upload file here", type=file_types)

# --- File Conversion Logic ---
if uploaded_file:
    file_name = uploaded_file.name
    st.info(f"📄 Uploaded File: `{file_name}`")

    if st.session_state.conversion_type == "Excel ➜ CSV":
        try:
            df = pd.read_excel(uploaded_file)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)

            st.success("✅ Successfully converted Excel to CSV!")
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".csv",
                mime="text/csv"
            )
            st.dataframe(df.head(10))

        except Exception as e:
            st.error(f"❌ Error: {e}")

    elif st.session_state.conversion_type == "CSV ➜ Excel":
        try:
            df = pd.read_csv(uploaded_file)
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')

            st.success("✅ Successfully converted CSV to Excel!")
            st.download_button(
                label="📥 Download Excel (.xlsx)",
                data=excel_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.dataframe(df.head(10))

        except Exception as e:
            st.error(f"❌ Error: {e}")

