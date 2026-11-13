import base64
import streamlit as st
from helper_functions.utility import check_password

# Helper function to convert local image to Base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load the background image from the 'assets' folder
bg_base64 = get_base64_image("assets/background.jpg")

# region <--------- Streamlit Page Configuration --------->

st.set_page_config(
    layout="centered",
    page_title="AI Chatbot",
    page_icon="🤖",
)

# Custom CSS with Light and Dark Mode Support
st.markdown(
    f"""
    <style>
    /* Fully responsive background image styling */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_base64}");
        background-size: cover;  /* Fixed typo from 100% 100%0 */
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* --- LIGHT MODE STYLING (Default) --- */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.92);
        padding: 3rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        margin-top: 3rem;
        color: #0f172a;
    }}

    div[data-testid="stTextInput"] {{
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-top: 20px;
        margin-bottom: 20px;
    }}

    div[data-testid="stTextInput"] input {{
        border: 1px solid #cbd5e1 !important;
        border-radius: 6px !important;
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-size: 16px !important;
    }}

    div[data-testid="stTextInput"] input:focus {{
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2) !important;
    }}

    /* --- DARK MODE OVERRIDES --- */
    @media (prefers-color-scheme: dark) {{
        .block-container {{
            background-color: rgba(15, 23, 42, 0.90) !important;
            color: #f8fafc !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}

        div[data-testid="stTextInput"] {{
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        div[data-testid="stTextInput"] input {{
            background-color: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #475569 !important;
        }}
    }}

    /* General Button Styling */
    div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
        border-radius: 6px;
        font-weight: 600;
        padding: 8px 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Do not continue if check_password is not True.
if not check_password():
    st.stop()

# endregion <--------- Streamlit Page Configuration --------->

st.title("SG Care Finder Chatbot")

st.write(
    "SG Care Finder is an AI-powered conversational assistant designed to help "
    "Singaporeans effortlessly navigate and access national support schemes. "
    "By parsing official policy documents and structured tables—ranging from "
    "ComCare and Silver Support to GST Vouchers, MediFund, and CHAS cards—the "
    "chatbot delivers fast, accurate, and personalized guidance, ensuring citizens "
    "can easily find the financial and social assistance they are entitled to."
)

st.markdown("---")

st.write("""
### Navigation Guide
Navigate using the **sidebar** to explore:

- 💬 **Chatbot** — Have a conversation with the AI assistant
- ℹ️ **About** — Understand the Key Features and Components
- ⚙️ **Methodology** — Understand the underlying architecture, RAG pipelines, and table-parsing logic
- 📤 **Upload Doc** — Manage and ingest new support scheme documents into the knowledge base
- ℹ️ **User Guide** — How to use the chatbot
""")