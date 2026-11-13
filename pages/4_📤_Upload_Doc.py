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
    page_title="Upload Document",
    page_icon="📤",
)

# Custom CSS with Light and Dark Mode Support
st.markdown(
    f"""
    <style>
    /* Fully responsive background image styling */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{bg_base64}");
        background-size: cover;  /* Scales dynamically without tiling */
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

    /* --- DARK MODE OVERRIDES --- */
    @media (prefers-color-scheme: dark) {{
        .block-container {{
            background-color: rgba(15, 23, 42, 0.90) !important;
            color: #f8fafc !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Do not continue if check_password is not True.
if not check_password():
    st.stop()

# endregion <--------- Streamlit Page Configuration --------->

st.title("📤 Upload New Policy Document")
st.markdown("Upload official Singapore government scheme PDFs directly into the knowledge base repository. Once uploaded, the chatbot and RAG engine will automatically include them in future queries.")

st.divider()

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ── File Uploader Widget ──────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Choose a PDF file to add to the knowledge base", 
    type=["pdf"],
    help="Select a single PDF policy document."
)

if uploaded_file is not None:
    file_path = os.path.join(DATA_DIR, uploaded_file.name)
    
    # Check if file already exists
    file_exists = os.path.exists(file_path)
    
    if st.button("📥 Save & Ingest Document", type="primary"):
        with st.spinner(f"Saving '{uploaded_file.name}' to `{DATA_DIR}/`..."):
            # Save the uploaded file to the local data directory
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Clear Streamlit's cache so initialize_rag() in chatbot.py re-scans the folder
        st.cache_resource.clear()
        
        if file_exists:
            st.success(f"✅ Successfully updated **{uploaded_file.name}**! The RAG cache has been cleared and your chatbot is now ready to reference the latest information.")
        else:
            st.success(f"✅ Successfully added **{uploaded_file.name}** to the knowledge base! The RAG cache has been refreshed.")

st.divider()

# ── Manage / View Existing Documents ──────────────────────────────────────────
st.subheader("📂 Current Knowledge Base Repository")

if os.path.exists(DATA_DIR):
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
    
    if pdf_files:
        st.info(f"Total active documents in repository: **{len(pdf_files)}**")
        
        # Display list with an option to delete if needed
        for pdf in sorted(pdf_files):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"📄 {pdf}")
            with col2:
                if st.button("🗑️ Delete", key=f"del_{pdf}"):
                    target_path = os.path.join(DATA_DIR, pdf)
                    if os.path.exists(target_path):
                        os.remove(target_path)
                        st.cache_resource.clear() # Clear cache when file is removed
                        st.rerun()
    else:
        st.warning("⚠️ No PDF files currently found in the `data/` folder.")
else:
    st.error("❌ The `data/` directory does not exist.")