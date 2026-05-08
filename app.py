import streamlit as st
from pathlib import Path
from main import run_pipeline
from db.database import get_analysis_stats, get_conversation_stats, get_distinct_conv_id, get_conversation_by_id
import plotly.express as px
import json
from collections import Counter

st.set_page_config(page_title="Call InsightAI", layout="wide", page_icon="📞")

st.title("📞 Call InsightAI")

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
            with st.spinner("Analysing calls. This may take a few minutes"):
                run_pipeline(str(zip_file_path))
            st.success("Analysis Complete")
        else:
            st.warning("Please upload a file first")
    else:
        if dataset_path:
            with st.spinner("Analysing calls. This may take a few minutes"):
                run_pipeline(dataset_path)
            st.success("Analysis Complete")
        else:
            st.warning("Please enter a dataset URL")

st.divider()
st.header("📊 Dashboard")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("From")
with col2:
    end_date = st.date_input("To")

st.divider()

start = start_date.strftime("%Y-%m-%d") if start_date else None
end = end_date.strftime("%Y-%m-%d") if end_date else None

conv_stats = get_conversation_stats(start, end)
analysis_stats = get_analysis_stats(start, end)
conv_ids = get_distinct_conv_id(start, end)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Calls", conv_stats.total_calls)
col2.metric("Avg Call Duration", f"{conv_stats.avg_duration/60:.1f} min")
col3.metric("Top Mood", analysis_stats['mood'][0].mood)
col4.metric("Avg Mood Score", f"{analysis_stats['mood'][0].avg_score:.2f}")

st.divider()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Mood Distribution")
    mood_data = {
        "mood": [r.mood for r in analysis_stats['mood']],
        "count": [r.mood_count for r in analysis_stats['mood']]
    }
    fig = px.bar(mood_data, x="mood", y="count", color="mood",
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Top Keywords")
    all_keywords = []
    for row in analysis_stats['keywords']:
        all_keywords.extend(json.loads(row.keywords))
    keyword_counts = Counter(all_keywords).most_common(10)
    kw_data = {
        "keyword": [k[0] for k in keyword_counts],
        "count": [k[1] for k in keyword_counts]
    }
    fig2 = px.bar(kw_data, x="keyword", y="count",
                  color_discrete_sequence=["#636EFA"])
    fig2.update_layout(xaxis_tickangle=-45, xaxis_title="", yaxis_title="Count")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("💬 Conversation Viewer")


col_select, col_empty = st.columns([1, 2])
with col_select:
    selected = st.selectbox("Select Conversation", [row.conversation_id for row in conv_ids])

rows = get_conversation_by_id(selected)
agent_row = next((r for r in rows if r.speaker == "agent"), None)
customer_row = next((r for r in rows if r.speaker == "customer"), None)

col1, col2 = st.columns(2)

with col1:
    if agent_row:
        st.markdown("**🎧 Agent**")
        with st.container(height=300):
            st.write(agent_row.transcript)
        if agent_row.mood:
            st.caption(f"Mood: {agent_row.mood} | Score: {agent_row.mood_score:.2f}")
            st.caption(f"Keywords: {', '.join(json.loads(agent_row.keywords))}")
        else:
            st.caption("No analysis available")

with col2:
    if customer_row:
        st.markdown("**📞 Customer**")
        with st.container(height=300):
            st.write(customer_row.transcript)
        if customer_row.mood:
            st.caption(f"Mood: {customer_row.mood} | Score: {customer_row.mood_score:.2f}")
            st.caption(f"Keywords: {', '.join(json.loads(customer_row.keywords))}")
        else:
            st.caption("No analysis available")