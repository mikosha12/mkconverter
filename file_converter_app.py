import streamlit as st
import pandas as pd
import io
import os
import requests
import tempfile
from pdf2docx import Converter

st.set_page_config(page_title="📁 Universal File Converter", layout="centered")
st.title("📁 Universal File Converter")

# --- Step 1: Select Conversion Type ---
st.subheader("1️⃣ Select Conversion Type")

conversion_options = [
    "Excel ➔ CSV",
    "CSV ➔ Excel",
    "Word (.docx) ➔ PDF",
    "PDF ➔ Word (.docx)"
]

conversion_type = st.selectbox("Choose a conversion:", conversion_options)

# --- Step 2: Upload File Based on Selected Conversion ---
st.subheader("2️⃣ Upload Your File")

upload_types = {
    "Excel ➔ CSV": ["xlsx", "xls"],
    "CSV ➔ Excel": ["csv"],
    "Word (.docx) ➔ PDF": ["docx"],
    "PDF ➔ Word (.docx)": ["pdf"]
}

uploaded_file = st.file_uploader("Upload file", type=upload_types[conversion_type])

# --- ConvertAPI DOCX to PDF Helper ---
def convert_docx_to_pdf_via_api(file, api_secret):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    convert_url = f"https://v2.convertapi.com/convert/docx/to/pdf?Secret={api_secret}"

    with open(temp_file_path, "rb") as docx_file:
        response = requests.post(convert_url, files={"File": docx_file})

    os.remove(temp_file_path)

    if response.status_code == 200:
        file_url = response.json()["Files"][0]["Url"]
        download_response = requests.get(file_url)
        if download_response.status_code == 200:
            return download_response.content
        else:
            raise Exception("Failed to download converted PDF.")
    else:
        raise Exception("API conversion failed.")

# --- Step 3: Handle Conversion ---
if uploaded_file:
    file_name = uploaded_file.name
    st.info(f"📄 Uploaded: `{file_name}`")

    try:
        if conversion_type == "Excel ➔ CSV":
            df = pd.read_excel(uploaded_file)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.success("✅ Converted Excel to CSV")
            st.download_button(
                label="📅 Download CSV",
                data=csv_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".csv",
                mime="text/csv"
            )
            st.dataframe(df.head(10))

        elif conversion_type == "CSV ➔ Excel":
            df = pd.read_csv(uploaded_file)
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')
            st.success("✅ Converted CSV to Excel")
            st.download_button(
                label="📅 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.dataframe(df.head(10))

        elif conversion_type == "Word (.docx) ➔ PDF":
            api_key = st.secrets["convertapi"]["secret"]
            result = convert_docx_to_pdf_via_api(uploaded_file, api_key)
            st.success("✅ Converted DOCX to PDF via API")
            st.download_button(
                label="📅 Download PDF",
                data=result,
                file_name=file_name.rsplit(".", 1)[0] + ".pdf",
                mime="application/pdf"
            )

        elif conversion_type == "PDF ➔ Word (.docx)":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(uploaded_file.read())
                temp_pdf_path = temp_pdf.name

            output_docx_path = temp_pdf_path.replace(".pdf", ".docx")

            cv = Converter(temp_pdf_path)
            cv.convert(output_docx_path, start=0, end=None)
            cv.close()

            with open(output_docx_path, "rb") as out_docx:
                st.success("✅ Converted PDF to DOCX")
                st.download_button(
                    label="📅 Download Word",
                    data=out_docx.read(),
                    file_name=file_name.rsplit(".", 1)[0] + ".docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            os.remove(temp_pdf_path)
            os.remove(output_docx_path)

    except Exception as e:
        st.error(f"❌ Error: {e}")
