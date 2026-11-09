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
    page_title="User Guide",
    page_icon="📖",
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

st.title("📖 User Guide — SG Care Finder")

st.write("""
Welcome to **SG Care Finder**! This step-by-step user guide helps you quickly get started, personalize your profile, navigate available Singapore care schemes, and manage your session effectively.

---

### 1️⃣ Step 1: Getting Started & Onboarding
When you launch the main application page:
1. **Enter Password**: Complete the password authentication prompt to access the application.
2. **Complete Onboarding Form**:
   - **Age**: Input your age (e.g., `40`) to let the assistant filter age-dependent subsidies (e.g., Silver Support, CHAS card tiers).
   - **Focus Area**: Select your primary area of interest from the dropdown menu (e.g., *Financial Assistance*, *Healthcare & Medical Subsidies*, *Senior & Retirement Support*, or *GST Vouchers*).
3. Click **Start Chatting 🚀** to begin your session.

---

### 2️⃣ Step 2: Asking Questions & Getting Tailored Assistance
- **Type Custom Queries**: Use the text input box at the bottom to ask natural language questions regarding Singapore social support schemes (e.g., *"What is the household per-capita income limit for CHAS Blue?"* or *"Am I eligible for ComCare?"*).
- **Click Follow-Up Chips**: After each AI response, click any of the **💡 Follow-up question** buttons rendered below the message to immediately send targeted follow-up queries without typing.

---

### 3️⃣ Step 3: Managing Your Session (Sidebar Settings)
Expand the sidebar (`<` icon on the top-left) to access convenience tools:
- 👤 **Profile Context**: View your active age and focus area currently guiding the assistant.
- ⚙️ **System Prompt Tuning**: Modify the default instructions or tone on the fly if needed.
- 📈 **Token Consumption**: Monitor real-time estimated token usage for your conversation.
- 🔄 **Restart Onboarding**: Reset your profile details (age/focus category) and start a new onboarding workflow.
- 🗑️ **Clear Conversation**: Instantly wipe the current chat history.

---

### 💡 Tips for Best Results
- **Specific Criteria**: State key household context (e.g., household size, gross income) for accurate per-capita income (PCI) assessments.
- **Scheme Names**: The chatbot natively understands major Singapore frameworks including **ComCare**, **CHAS**, **MediFund**, **Silver Support**, **GST Vouchers**, and **CPF** schemes.
""")

st.divider()
st.subheader("📊 System Overview")

data_dir = "data"
if os.path.exists(data_dir):
    pdf_count = len([f for f in os.listdir(data_dir) if f.endswith(".pdf")])
    st.success(f"System Status: **Online** | Loaded **{pdf_count} policy documents** from `/data`.")
else:
    st.warning("System Status: **Warning** | `/data` directory not detected.")