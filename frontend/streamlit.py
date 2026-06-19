from __future__ import annotations

import requests
import streamlit as st
import pandas as pd


API_BASE = "http://localhost:8000"


st.set_page_config(
    page_title="RAG Document Q&A",
    page_icon="📄",
    layout="wide",
)

st.title("RAG Document Q&A System")
st.caption("Ask questions about the AWS Customer Agreement")


with st.sidebar:
    st.header("Document Management")

    if st.button("Ingest PDF", use_container_width=True):
        with st.spinner("Ingesting document..."):
            try:
                resp = requests.post(f"{API_BASE}/ingest", timeout=120)
                if resp.status_code == 200:
                    st.success(resp.json().get("message", "Done"))
                else:
                    st.error(resp.json().get("detail", "Ingestion failed"))
            except requests.ConnectionError:
                st.error("Cannot reach backend. Is FastAPI running?")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()
    st.info(
        "**Steps:**\n"
        "1. Start the FastAPI backend\n"
        "2. Click **Ingest PDF** (once)\n"
        "3. Ask questions in the Chat tab"
    )


tab_chat, tab_analytics = st.tabs(["Chat", "Analytics Dashboard"])


with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("Source Chunks"):
                    for i, chunk in enumerate(msg["sources"], 1):
                        st.markdown(f"**Chunk {i}:**")
                        st.text(chunk)
                        st.divider()

    if question := st.chat_input("Ask a question about the AWS Customer Agreement..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/ask",
                        json={"question": question},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        answer = data["answer"]
                        sources = data.get("sources", [])

                        st.markdown(answer)

                        if sources:
                            with st.expander("Source Chunks"):
                                for i, chunk in enumerate(sources, 1):
                                    st.markdown(f"**Chunk {i}:**")
                                    st.text(chunk)
                                    st.divider()

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                            }
                        )
                    else:
                        error_msg = resp.json().get("detail", "Unknown error")
                        st.error(f"{error_msg}")

                except requests.ConnectionError:
                    st.error(
                        "Cannot reach backend. "
                        "Make sure FastAPI is running on http://localhost:8000"
                    )
                except Exception as e:
                    st.error(f"Error: {e}")


with tab_analytics:
    st.header("Analytics Dashboard")

    if st.button("Refresh Analytics", use_container_width=True):
        st.rerun()

    try:
        resp = requests.get(f"{API_BASE}/analytics", timeout=30)
        if resp.status_code == 200:
            data = resp.json()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Queries", data["total_queries"])
            with col2:
                avg_lat = data.get("average_latency")
                st.metric(
                    "Avg Latency",
                    f"{avg_lat:.2f}s" if avg_lat is not None else "N/A",
                )
            with col3:
                rate = data.get("success_rate")
                st.metric(
                    "Success Rate",
                    f"{rate:.1f}%" if rate is not None else "N/A",
                )

            st.divider()

            st.subheader("Most Frequent Questions")
            freq = data.get("most_frequent_questions", [])
            if freq:
                df_freq = pd.DataFrame(freq)
                st.dataframe(
                    df_freq,
                    use_container_width=True,
                    hide_index=True,
                )
                st.bar_chart(
                    df_freq.set_index("question")["frequency"],
                )
            else:
                st.info("No queries recorded yet.")

            st.divider()

            st.subheader("No-Answer Queries")
            no_ans = data.get("no_answer_queries", [])
            if no_ans:
                for q in no_ans:
                    st.markdown(f"- {q}")
            else:
                st.success("All queries were answered successfully!")

        else:
            st.error("Failed to fetch analytics.")

    except requests.ConnectionError:
        st.warning(
            "Cannot reach backend. Start FastAPI to view analytics."
        )
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
