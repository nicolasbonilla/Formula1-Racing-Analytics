import streamlit as st
import pandas as pd
import os
import requests

def render():
    st.title("🏁 F1 LLM-RAG + Graph + Multi-Model Engine")
    st.markdown("🚀 *Powered by Local Ollama Llama 3, Hybrid Vector/Graph RAG, and Parallel ML Engines.*")

    # FastAPI Backend Endpoint
    API_URL = "http://127.0.0.1:8000"

    # Optional toggle for training execution matching backend QueryRequest schema
    st.sidebar.markdown("---")
    st.sidebar.subheader("🧠 AI Engine Controls")
    run_training_flag = st.sidebar.checkbox("Trigger Training / Auto-Compute", value=False, key="rq6_run_training")

    # ---------------------------------------------------------
    # 1. KNOWLEDGE GRAPH ARTIFACT DISPLAY
    # ---------------------------------------------------------
    graph_png_path = "f1_knowledge_graph.png"
    if os.path.exists(graph_png_path):
        with st.expander("🌐 View Formula 1 Star Schema Knowledge Graph", expanded=False):
            st.image(graph_png_path, caption="F1 Star Schema Knowledge Mapping", use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # 2. HELPER TO RENDER STRUCTURED RESPONSE
    # ---------------------------------------------------------
    def display_response_data(res_data):
        """Presents dict response in systematic UI components instead of raw string JSON."""
        if isinstance(res_data, dict):
            # 1. Display Execution Metrics & Auto-Detected Intent
            intent = res_data.get("detected_intent", {})
            winning_model = str(res_data.get("winning_model", "N/A")).upper()
            model_score = res_data.get("model_score", "N/A")
            
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1:
                st.metric("Detected Target", intent.get("target", "N/A"))
            with m_col2:
                st.metric("Task Mode", intent.get("task", "N/A"))
            with m_col3:
                st.metric("Winning Model", winning_model)
            with m_col4:
                st.metric("Model Score", f"{model_score:.4f}" if isinstance(model_score, float) else str(model_score))

            # 2. Display Context Summary in Expander (Fixed key mapping from 'retrieved_context')
            context_summary = res_data.get("retrieved_context", res_data.get("context_summary", ""))
            if context_summary:
                with st.expander("🔍 View Retrieved Hybrid (Vector + Graph) Context", expanded=False):
                    st.code(context_summary, language="markdown")

            st.markdown("---")

            # 3. Display Main LLM Analysis Response
            llm_text = res_data.get("llm_response", res_data.get("response", res_data.get("answer", "")))
            if llm_text:
                st.markdown(llm_text)
            else:
                st.json(res_data)
        else:
            st.markdown(str(res_data))

    # ---------------------------------------------------------
    # 3. CHAT & RAG ENGINE INTERFACE
    # ---------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict):
                display_response_data(message["content"])
            else:
                st.markdown(message["content"])

    # User Query Input
    if prompt := st.chat_input("Ask an F1 question (e.g., Show all race results for Max Verstappen in 2024)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Querying Graph Engine & Local LLM..."):
                payload = {
                    "prompt": str(prompt),
                    "run_training": bool(run_training_flag)
                }
                
                try:
                    # Increased timeout to 180s to prevent request drops during model training
                    response = requests.post(
                        f"{API_URL}/chat",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=180
                    )
                    if response.status_code == 200:
                        res_data = response.json()
                        display_response_data(res_data)
                        st.session_state.messages.append({"role": "assistant", "content": res_data})
                    else:
                        error_msg = f"⚠️ Backend API returned status code {response.status_code}. Response: {response.text}"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                except Exception as e:
                    error_msg = f"⚠️ Could not reach FastAPI backend at `{API_URL}`. Make sure `uvicorn api.app:app` is running on port 8000.\n\n*Error details:* {e}"
                    st.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})