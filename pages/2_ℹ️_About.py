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
    page_title="About",
    page_icon="ℹ️",
)

# Custom CSS to add the background image and style containers
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
        background-color: rgba(255, 255, 255, 0.90);
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

st.title("ℹ️ About SG Care Finder")

st.write("""
Welcome to **SG Care Finder**, an intelligent RAG (Retrieval-Augmented Generation) assistant designed to help users navigate Singapore government support schemes, household eligibility criteria, and financial assistance programs accurately.

### Key Features
- 📚 **RAG-Powered Knowledge Base** — Dynamically queries official government scheme PDF documents stored locally.
- 📊 **Structured Table Parsing** — Uses `pdfplumber` to convert complex policy tables into Markdown format, ensuring precise income bracket and per-capita income (PCI) lookups.
- 💬 **Streaming Responses** — Real-time word-by-word AI response generation using OpenAI's `gpt-4o-mini`.
- 🔒 **Password Protected** — Secure authentication gating access to the application.
- 📈 **Token Monitoring** — Live usage metrics tracked directly in the sidebar.

### Tech Stack & Architecture
| Component | Tool / Library |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io/) |
| RAG Framework | [LlamaIndex Core](https://www.llamaindex.ai/) |
| PDF & Table Extractor | `pdfplumber`|
| Language Model | [OpenAI GPT-4o-mini](https://openai.com/) |
| Embeddings | `text-embedding-3-small` |
| Security & Utility | Custom helper functions & Streamlit Secrets |

### Disclaimer
*This application is built for informational and demonstration purposes to assist with Singapore care scheme discovery. Official criteria are subject to prevailing government guidelines.*
""")

# ── Dynamic Status Check ──────────────────────────────────────────────────────
st.divider()
st.subheader("📊 System Overview")

data_dir = "data"
if os.path.exists(data_dir):
    pdf_count = len([f for f in os.listdir(data_dir) if f.endswith(".pdf")])
    st.success(f"System Status: **Online** | Loaded **{pdf_count} policy documents** from `/data`.")
else:
    st.warning("System Status: **Warning** | `/data` directory not detected.")