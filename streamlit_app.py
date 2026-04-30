import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from graph.graph import diagnostic_graph
from utils.export import export_pdf, export_pptx

st.set_page_config(page_title="Company Diagnostic Engine", layout="wide")
st.title("Company Rapid Diagnostic Engine")

query = st.text_input(
    "Enter company or problem",
    placeholder="e.g. Analyze Tata Steel's operational efficiency"
)

if "state" not in st.session_state:
    st.session_state.state = None
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "thread_1"
if "awaiting_review" not in st.session_state:
    st.session_state.awaiting_review = False

if st.button("Run Diagnostic") and query:
    initial_state = {
        "query": query,
        "research_output": "",
        "financial_output": "",
        "benchmarking_output": "",
        "trends_output": "",
        "synthesis_output": "",
        "messages": [HumanMessage(content=query)],
        "completed_agents": [],
    }

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.spinner("Running agents..."):
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.info(" Research...")
        with col2: st.info(" Financial...")
        with col3: st.info(" Benchmarking...")
        with col4: st.info(" Trends...")

        # Run until interrupt (before synthesis)
        result = diagnostic_graph.invoke(initial_state, config)
        st.session_state.state = result
        st.session_state.awaiting_review = True

    col1.success(" Research done")
    col2.success(" Financial done")
    col3.success(" Benchmarking done")
    col4.success(" Trends done")

# Human review section
if st.session_state.awaiting_review and st.session_state.state:
    state = st.session_state.state
    st.divider()
    st.subheader("Review Research Before Synthesis")

    with st.expander(" Research findings"):
        st.write(state.get("research_output", ""))
    with st.expander(" Financial snapshot"):
        st.write(state.get("financial_output", ""))
    with st.expander(" Competitive benchmark"):
        st.write(state.get("benchmarking_output", ""))
    with st.expander(" Industry trends"):
        st.write(state.get("trends_output", ""))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(" Approve — Generate Report"):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            with st.spinner("Synthesizing Company report..."):
                final = diagnostic_graph.invoke(None, config)
                st.session_state.state = final
                st.session_state.awaiting_review = False
            st.rerun()
    with col_b:
        if st.button(" Re-run Research"):
            st.session_state.awaiting_review = False
            st.session_state.state = None
            st.rerun()

# Final report
if (
    st.session_state.state
    and not st.session_state.awaiting_review
    and st.session_state.state.get("synthesis_output")
):
    st.divider()
    st.subheader("Company Diagnostic Report")
    st.markdown(st.session_state.state["synthesis_output"])

    st.divider()
    col_x, col_y = st.columns(2)
    with col_x:
        if st.button(" Export PDF"):
            path = export_pdf(
                st.session_state.state["query"],
                st.session_state.state["synthesis_output"]
            )
            with open(path, "rb") as f:
                st.download_button("Download PDF", f, file_name="diagnostic.pdf")
    with col_y:
        if st.button(" Export PPTX"):
            path = export_pptx(
                st.session_state.state["query"],
                st.session_state.state["synthesis_output"]
            )
            with open(path, "rb") as f:
                st.download_button("Download PPTX", f, file_name="diagnostic.pptx")