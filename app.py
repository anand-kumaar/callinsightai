import streamlit as st
from pathlib import Path
from main import run_pipeline
from db.database import get_analysis_stats,get_conversation_stats
import plotly.express as px
import json
from collections import Counter


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
st.divider()
conv_stats=get_conversation_stats()
analysis_stats=get_analysis_stats()

col1,col2,col3,col4=st.columns(4)

col1.metric("Total Call",conv_stats.total_calls)
col2.metric("Avg Call Duration",f"{conv_stats.avg_duration/60:.1f} min")
col3.metric("Top Mood",analysis_stats['mood'][0].mood)
col4.metric("Avg Mood Score", f"{analysis_stats['mood'][0].avg_score:.2f}")




st.subheader("Mood Distribution")
mood_data = {"mood": [r.mood for r in analysis_stats['mood']],
             "count": [r.mood_count for r in analysis_stats['mood']]}
fig = px.bar(mood_data, x="mood", y="count", color="mood")
st.plotly_chart(fig)


st.subheader("Top Keywords")
rows = analysis_stats['keywords']
all_keywords = []
for row in rows:
    all_keywords.extend(json.loads(row.keywords))
keyword_counts = Counter(all_keywords).most_common(10)
kw_data = {"keyword": [k[0] for k in keyword_counts],
           "count": [k[1] for k in keyword_counts]}
fig2 = px.bar(kw_data, x="keyword", y="count")
st.plotly_chart(fig2)
