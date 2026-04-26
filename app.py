import streamlit as st
from pathlib import Path
from main import run_pipeline

st.title("Call InsightAI")

source_type = st.selectbox("Select data source", ["HuggingFace Dataset", "ZIP File"])

if source_type == "ZIP File":
    uploaded_file = st.file_uploader("Upload zip file")
    if uploaded_file is not None:
        with open("temp_upload.zip", "wb") as f:
            f.write(uploaded_file.getbuffer())

else:
    dataset_path = st.text_input("Enter the HF dataset URL")

if st.button("Analyse"):
    if source_type == "ZIP File":
        zip_file_path = Path("temp_upload.zip")
        if zip_file_path.exists():
            run_pipeline(str(zip_file_path))
        else:
            st.warning("Please upload a file first")
    else:
        if dataset_path:
            run_pipeline(dataset_path)
        else:
            st.warning("Please enter a dataset URL")