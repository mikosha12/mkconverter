import streamlit as st
import pandas as pd
import io
import os
from docx2pdf import convert as docx_to_pdf
from pdf2docx import Converter as PDFtoWordConverter
from tempfile import NamedTemporaryFile

st.set_page_config(page_title="📁 Universal File Converter", layout="centered")
st.title("📁 Universal File Converter")

# --- Step 1: Select Conversion Type ---
st.subheader("1️⃣ Select Conversion Type")

conversion_options = [
    "Excel ➜ CSV",
    "CSV ➜ Excel",
    "Word (.docx) ➜ PDF",
    "PDF ➜ Word (.docx)"
]

conversion_type = st.selectbox("Choose a conversion:", conversion_options)

# --- Step 2: Upload File Based on Selected Conversion ---
st.subheader("2️⃣ Upload Your File")

upload_types = {
    "Excel ➜ CSV": ["xlsx", "xls"],
    "CSV ➜ Excel": ["csv"],
    "Word (.docx) ➜ PDF": ["docx"],
    "PDF ➜ Word (.docx)": ["pdf"]
}

uploaded_file = st.file_uploader("Upload file", type=upload_types[conversion_type])

# --- Step 3: Handle Conversion ---
if uploaded_file:
    file_name = uploaded_file.name
    st.info(f"📄 Uploaded: `{file_name}`")

    # Excel ➜ CSV
    if conversion_type == "Excel ➜ CSV":
        try:
            df = pd.read_excel(uploaded_file)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)

            st.success("✅ Converted Excel to CSV")
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".csv",
                mime="text/csv"
            )
            st.dataframe(df.head(10))

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # CSV ➜ Excel
    elif conversion_type == "CSV ➜ Excel":
        try:
            df = pd.read_csv(uploaded_file)
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, engine='openpyxl')

            st.success("✅ Converted CSV to Excel")
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=file_name.rsplit(".", 1)[0] + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.dataframe(df.head(10))

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Word ➜ PDF
    elif conversion_type == "Word (.docx) ➜ PDF":
        try:
            with NamedTemporaryFile(delete=False, suffix=".docx") as temp_docx:
                temp_docx.write(uploaded_file.read())
                temp_docx_path = temp_docx.name

            output_pdf_path = temp_docx_path.replace(".docx", ".pdf")
            docx_to_pdf(temp_docx_path, output_pdf_path)

            with open(output_pdf_path, "rb") as out_pdf:
                st.success("✅ Converted Word to PDF")
                st.download_button(
                    label="📥 Download PDF",
                    data=out_pdf.read(),
                    file_name=file_name.rsplit(".", 1)[0] + ".pdf",
                    mime="application/pdf"
                )

            os.remove(temp_docx_path)
            os.remove(output_pdf_path)

        except Exception as e:
            st.error(f"❌ Error: {e}")

    # PDF ➜ Word
    elif conversion_type == "PDF ➜ Word (.docx)":
        try:
            with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf.write(uploaded_file.read())
                temp_pdf_path = temp_pdf.name

            output_docx_path = temp_pdf_path.replace(".pdf", ".docx")

            cv = PDFtoWordConverter(temp_pdf_path)
            cv.convert(output_docx_path, start=0, end=None)
            cv.close()

            with open(output_docx_path, "rb") as out_docx:
                st.success("✅ Converted PDF to Word")
                st.download_button(
                    label="📥 Download Word (.docx)",
                    data=out_docx.read(),
                    file_name=file_name.rsplit(".", 1)[0] + ".docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            os.remove(temp_pdf_path)
            os.remove(output_docx_path)

        except Exception as e:
            st.error(f"❌ Error: {e}")
