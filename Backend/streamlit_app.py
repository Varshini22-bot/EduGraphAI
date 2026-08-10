import streamlit as st
import requests

# ----------------------------------
# Page Configuration
# ----------------------------------

st.set_page_config(
    page_title="Knowledge Graph Learning Assistant",
    page_icon="📚",
    layout="wide"
)

# ----------------------------------
# Sidebar Statistics
# ----------------------------------

try:
    stats = requests.get(
        "http://127.0.0.1:8000/stats"
    ).json()

    st.sidebar.header("📊 Graph Statistics")

    st.sidebar.write(
        f"Nodes: {stats['nodes']}"
    )

    st.sidebar.write(
        f"Relationships: {stats['relationships']}"
    )

except:
    st.sidebar.warning(
        "FastAPI server not running."
    )

# ----------------------------------
# Main Title
# ----------------------------------

st.title("📚 Knowledge Graph Learning Assistant")

st.write(
    "Ask any topic from your knowledge graph."
)

# ----------------------------------
# Input Box
# ----------------------------------

topic = st.text_input(
    "Enter Topic"
)

# ----------------------------------
# Search Button
# ----------------------------------

if st.button("Generate Answer"):

    if topic.strip() == "":

        st.warning(
            "Please enter a topic."
        )

    else:

        try:

            response = requests.get(
                "http://127.0.0.1:8000/ask",
                params={"query": topic}
            )

            data = response.json()

            # --------------------------
            # Graph Context
            # --------------------------

            st.subheader("🔗 Graph Context")

            for item in data["graph_context"]:

                st.write(
                    f"{item['relation']} → {item['related']}"
                )

            # --------------------------
            # Answer
            # --------------------------

            st.subheader("🤖 Generated Answer")

            st.write(
                data["answer"]
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )