import base64
import os
import streamlit as st
from helper_functions.utility import check_password

# Helper function to convert local image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load the background image from the assets folder
bg_base64 = get_base64_image("assets/background.jpg")

# region <--------- Streamlit Page Configuration --------->

st.set_page_config(
    layout="centered",
    page_title="Methodology",
    page_icon="📖",
)

# Custom CSS to add the background image and style containers (Matching chatbot.py)
st.markdown(
    f"""
    <style>
    /* Fully responsive background image styling */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_base64}");
        background-size: 100% 100%;  /* Forces the image to scale dynamically with window size */
        background-position: center;   /* Centers the image */
        background-repeat: no-repeat;  /* Prevents tiling */
        background-attachment: fixed;  /* Keeps it locked in place on scroll */
    }}

    /* Semi-transparent white card for the main content container to ensure readability */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.92);
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        margin-top: 3rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Do not continue if check_password is not True.
if not check_password():
    st.stop()

# endregion <--------- Streamlit Page Configuration --------->

st.title("📖 System Methodology & Architecture")
st.markdown("Detailed technical overview of how the **SG Care Finder Chatbot** processes policy documents, handles financial tables, and retrieves relevant government assistance schemes.")

st.divider()

# ── Section 1: End-to-End RAG Pipeline ────────────────────────────────────────
st.subheader("🔄 End-to-End RAG Workflow")
st.markdown("""
The application operates on a lightweight, modular **Retrieval-Augmented Generation (RAG)** architecture designed to eliminate hallucinations and precisely match household income criteria against official scheme documents.
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1. Ingestion")
    st.caption("Scans local `data/` folder for official policy PDFs.")
with col2:
    st.markdown("### 2. Indexing")
    st.caption("Generates vector embeddings via OpenAI.")
with col3:
    st.markdown("### 3. Generation")
    st.caption("Streams answers using GPT-4o-mini & top context.")

st.divider()

# ── Section 2: Core Technical Components ──────────────────────────────────────
st.subheader("🛠️ Technical Stack & Implementation Details")

with st.expander("📄 1. Advanced Table Parsing (`pdfplumber`)", expanded=True):
    st.markdown("""
    * **The Challenge:** Standard PDF text extractors strip away layout borders and column alignments, destroying critical data inside government income tables and per-capita income (PCI) tiers.
    * **The Solution:** The app uses **`pdfplumber`** to inspect page layouts, isolate tabular data structures, and convert rows and columns directly into clean **Markdown table syntax** (`| Header | Header |`).
    * **The Benefit:** Large language models understand Markdown tables with exceptionally high accuracy, enabling precise lookups for household income caps and subsidy tiers.
    """)

with st.expander("🧠 2. Vector Indexing & Embeddings (`LlamaIndex` + OpenAI)", expanded=False):
    st.markdown("""
    * **Embedding Model:** `text-embedding-3-small` (optimized for semantic search efficiency and speed).
    * **Framework:** Lightweight modular LlamaIndex core components (`llama-index-core`, `llama-index-llms-openai`, `llama-index-embeddings-openai`).
    * **Storage:** In-memory `VectorStoreIndex` built dynamically upon app startup for fast query evaluation without heavy database dependencies.
    """)

with st.expander("⚡ 3. High-Context Retrieval (`similarity_top_k=5`)", expanded=False):
    st.markdown("""
    * By default, vector search engines retrieve only the top 1 or 2 chunks, which often cuts off multi-page policy tables.
    * The query engine is configured with **`similarity_top_k=5`**, ensuring that a wider context window of relevant policy sections and tables is pulled and passed into the prompt context.
    """)

with st.expander("🤖 4. Response Generation (`gpt-4o-mini`)", expanded=False):
    st.markdown("""
    * Powered by OpenAI's **`gpt-4o-mini`** model.
    * Employs real-time **streaming responses** (`st.write_stream`) so users see answers generate instantly word-by-word.
    * System prompt governance ensures responses remain anchored strictly to Singapore government support schemes and verified document contents.
    """)

st.divider()

# ── Section 3: Data Status Check ──────────────────────────────────────────────
st.subheader("📂 Knowledge Base Status")

data_dir = "data"
if os.path.exists(data_dir):
    pdf_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    if pdf_files:
        st.success(f"✅ Active Knowledge Base: **{len(pdf_files)} PDF files loaded** from `/data` directory.")
        with st.expander("View Loaded Source Files"):
            for pdf in pdf_files:
                st.text(f"• {pdf}")
    else:
        st.warning("⚠️ The `/data` directory exists, but no PDF files were found inside.")
else:
    st.error("❌ The `/data` directory is missing.")