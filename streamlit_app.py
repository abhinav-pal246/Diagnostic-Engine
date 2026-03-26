from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage
from graph.graph import diagnostic_graph
from utils.export import export_pdf, export_pptx

st.set_page_config(page_title="McKinsey Diagnostic Engine", layout="wide", page_icon="📊")
st.title("📊 McKinsey Rapid Diagnostic Engine")
st.divider()

# ── Session state init ─────────────────────────────────────────
for key, default in {
    "research_output": "",
    "financial_output": "",
    "benchmarking_output": "",
    "trends_output": "",
    "synthesis_output": "",
    "awaiting_review": False,
    "report_ready": False,
    "thread_id": "thread_1",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Input ──────────────────────────────────────────────────────
query = st.text_input("Enter company or problem", placeholder="e.g. Analyze Tata Steel's operational efficiency")

if st.button("🚀 Run Diagnostic") and query:
    # Reset everything
    st.session_state.research_output = ""
    st.session_state.financial_output = ""
    st.session_state.benchmarking_output = ""
    st.session_state.trends_output = ""
    st.session_state.synthesis_output = ""
    st.session_state.awaiting_review = False
    st.session_state.report_ready = False
    st.session_state.thread_id = f"thread_{abs(hash(query))}"

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

    with st.spinner("Running all agents in parallel..."):
        try:
            # stream_mode="values" gives full state after every node write
            for chunk in diagnostic_graph.stream(initial_state, config, stream_mode="values"):
                if chunk.get("research_output"):
                    st.session_state.research_output = chunk["research_output"]
                if chunk.get("financial_output"):
                    st.session_state.financial_output = chunk["financial_output"]
                if chunk.get("benchmarking_output"):
                    st.session_state.benchmarking_output = chunk["benchmarking_output"]
                if chunk.get("trends_output"):
                    st.session_state.trends_output = chunk["trends_output"]

            st.session_state.awaiting_review = True

        except Exception as e:
            st.error(f"Error: {e}")

    st.rerun()

# ── Human review ───────────────────────────────────────────────
if st.session_state.awaiting_review:
    st.subheader("🔍 Review Research Before Synthesis")

    with st.expander("📋 Research findings", expanded=True):
        st.write(st.session_state.research_output or "⚠️ No output")

    with st.expander("💰 Financial snapshot", expanded=True):
        st.write(st.session_state.financial_output or "⚠️ No output")

    with st.expander("📊 Competitive benchmark", expanded=True):
        st.write(st.session_state.benchmarking_output or "⚠️ No output")

    with st.expander("📈 Industry trends", expanded=True):
        st.write(st.session_state.trends_output or "⚠️ No output")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve — Generate Report"):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            with st.spinner("Generating McKinsey report..."):
                try:
                    for chunk in diagnostic_graph.stream(None, config, stream_mode="values"):
                        if chunk.get("synthesis_output"):
                            st.session_state.synthesis_output = chunk["synthesis_output"]

                    st.session_state.awaiting_review = False
                    st.session_state.report_ready = True

                except Exception as e:
                    st.error(f"Synthesis error: {e}")
            st.rerun()

    with col2:
        if st.button("🔄 Start Over"):
            for key in ["research_output", "financial_output", "benchmarking_output",
                        "trends_output", "synthesis_output"]:
                st.session_state[key] = ""
            st.session_state.awaiting_review = False
            st.session_state.report_ready = False
            st.rerun()

# ── Final report ───────────────────────────────────────────────
if st.session_state.report_ready and st.session_state.synthesis_output:
    st.divider()
    st.subheader("📄 McKinsey Diagnostic Report")
    st.markdown(st.session_state.synthesis_output)

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Export PDF"):
            try:
                path = export_pdf(query or "Diagnostic", st.session_state.synthesis_output)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download PDF", f,
                                       file_name="diagnostic.pdf",
                                       mime="application/pdf")
            except Exception as e:
                st.error(f"PDF error: {e}")

    with col2:
        if st.button("📊 Export PPTX"):
            try:
                path = export_pptx(query or "Diagnostic", st.session_state.synthesis_output)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download PPTX", f,
                                       file_name="diagnostic.pptx",
                                       mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
            except Exception as e:
                st.error(f"PPTX error: {e}")