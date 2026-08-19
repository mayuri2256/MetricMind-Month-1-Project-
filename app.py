import json
from pathlib import Path

import plotly.express as px
import streamlit as st

from src.audit import write_audit_event
from src.semantic_engine import MetricMindEngine

st.set_page_config(page_title="MetricMind", page_icon="📊", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "sales.csv"
METRICS_PATH = Path(__file__).parent / "semantic_layer" / "metrics.yml"

@st.cache_resource
def get_engine():
    return MetricMindEngine(DATA_PATH, METRICS_PATH)


st.title("MetricMind")
st.caption("Governed conversational BI — Month 1 prototype")
engine = get_engine()

question = st.text_input(
    "Ask a business question",
    value="Why did European margins drop last quarter?",
)

if st.button("Analyze", type="primary") or question:
    result = engine.execute(question)
    write_audit_event(result)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Metric", result["parsed"]["metric"].title())
    if result["parsed"]["metric"] == "margin":
        col_b.metric("Value", f"{result['value']:.1%}")
    else:
        col_b.metric("Value", f"${result['value']:,.0f}")
    col_c.metric("Governed", "Yes")

    st.subheader(result["headline"])
    st.write("The answer was generated from an approved semantic metric, not arbitrary SQL.")
    chart_frame = __import__("pandas").DataFrame(result["data"])
    if result["chart_type"] == "bar" and not chart_frame.empty:
        x_col = chart_frame.columns[0]
        y_col = chart_frame.columns[-1]
        figure = px.bar(chart_frame, x=x_col, y=y_col, title="Governed result")
        st.plotly_chart(figure, use_container_width=True)
    st.dataframe(chart_frame, use_container_width=True)
    with st.expander("View semantic API payload"):
        st.json(result["payload"])
    with st.expander("View parser decision"):
        st.json(result["parsed"])
