import base64
import os
import shutil
import pdfplumber
import streamlit as st
from llama_index.core import (
    Document,
    Settings,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from helper_functions.llm import count_tokens
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
    page_title="Chatbot",
    page_icon="💬",
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

        /* Text inputs and form elements in dark mode */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stNumberInput"] input, 
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {{
            background-color: #0f172a !important;
            color: #f8fafc !important;
            border-color: #475569 !important;
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

st.title("💬 SG Care Finder Chatbot")

# ── Function to load PDFs and extract both text and structured tables ──
def load_pdfs_with_tables(data_dir="data"):
    documents = []
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        return documents

    pdf_files = [f for f in os.listdir(data_dir) if f.endswith(".pdf")]
    
    for filename in pdf_files:
        filepath = os.path.join(data_dir, filename)
        text_content = f"Source Document: {filename}\n\n"

        with pdfplumber.open(filepath) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text_content += f"--- Page {page_num} ---\n"

                # 1. Extract normal text content
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"

                # 2. Extract tables and format them cleanly as Markdown tables
                tables = page.extract_tables()
                for table in tables:
                    text_content += "\n[Extracted Table]\n"
                    for row in table:
                        clean_row = [
                            str(cell).replace("\n", " ").strip() if cell else ""
                            for cell in row
                        ]
                        text_content += "| " + " | ".join(clean_row) + " |\n"
                    text_content += "\n"

        documents.append(
            Document(text=text_content, metadata={"file_name": filename})
        )

    return documents

# ── Initialize LlamaIndex RAG Engine with Automatic Refresh Check ──
@st.cache_resource
def initialize_rag():
    Settings.llm = OpenAI(model="gpt-4o-mini")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    data_dir = "data"
    persist_dir = "./storage"
    
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        return None

    # Check if any PDF in data/ is newer than the storage folder index files
    needs_rebuild = False
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        try:
            storage_mtime = os.path.getmtime(persist_dir)
            for f in os.listdir(data_dir):
                if f.endswith(".pdf"):
                    pdf_path = os.path.join(data_dir, f)
                    if os.path.getmtime(pdf_path) > storage_mtime:
                        needs_rebuild = True
                        break
        except Exception:
            needs_rebuild = True
    else:
        needs_rebuild = True

    if not needs_rebuild:
        try:
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
        except Exception:
            needs_rebuild = True

    if needs_rebuild:
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir, ignore_errors=True)
            
        documents = load_pdfs_with_tables(data_dir)
        if not documents:
            return None
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=persist_dir)
            
    return index.as_query_engine(similarity_top_k=5, streaming=True)

persist_dir = "./storage"
is_cached_load = os.path.exists(persist_dir) and os.listdir(persist_dir)

if is_cached_load:
    query_engine = initialize_rag()
else:
    with st.status("🤖 Initializing RAG Knowledge Base for the first time...", expanded=True) as status:
        st.write("📄 Parsing PDF documents and tables via pdfplumber...")
        st.write("🧠 Generating embeddings and building vector index...")
        st.write("💾 Saving index to disk...")
        query_engine = initialize_rag()
        status.update(label="✅ RAG Knowledge Base ready!", state="complete", expanded=False)

# ── Initialize Session State ──
if "onboarding_done" not in st.session_state:
    st.session_state.onboarding_done = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_chip_query" not in st.session_state:
    st.session_state.selected_chip_query = None

# Function to dynamically generate chips based on the assistant's latest response
def generate_dynamic_chips(response_text, user_age, help_category):
    try:
        chip_prompt = (
            f"User Profile: Age {user_age}, Focus Area: {help_category}.\n"
            f"Assistant Response Content: '{response_text}'\n\n"
            f"Task: Generate exactly 3 short follow-up questions directly related to the response above.\n"
            f"RULES:\n"
            f"1. Make each follow-up question clear and helpful regarding Singapore social/financial support.\n"
            f"2. Keep each question concise.\n"
            f"3. Return ONLY the 3 questions separated by vertical bars (|), with no extra text or numbering."
        )
        chip_completion = OpenAI(model="gpt-4o-mini").complete(chip_prompt)
        raw_chips = str(chip_completion).strip().split("|")
        suggested_chips = [c.strip() for c in raw_chips if c.strip()][:3]
        
        if len(suggested_chips) < 3:
            raise ValueError("Insufficient chips generated")
        return suggested_chips
    except Exception:
        return [
            "What are the eligibility details?",
            "What documents do I need to prepare?",
            "How do I apply for this?"
        ]

# ── Guided Onboarding Flow (Before Chat Starts) ──
if not st.session_state.onboarding_done:
    st.markdown("### 👋 Welcome to SG Care Finder")
    st.write(
        "I am your AI-powered assistant designed to help Singaporeans navigate national support schemes "
        "(such as ComCare, Silver Support, GST Vouchers, MediFund, and CHAS cards). "
        "To give you the most accurate and personalized guidance, please share a few quick details below:"
    )
    
    with st.form("onboarding_form"):
        user_age = st.number_input("Your Age", min_value=1, max_value=120, value=40, step=1)
        help_category = st.selectbox(
            "What kind of help are you looking for?",
            [
                "General Support & Overview",
                "Financial Assistance (ComCare / Calamity)",
                "Healthcare & Medical Subsidies (CHAS / MediFund)",
                "Senior & Retirement Support (Silver Support / CPF)",
                "Cost of Living & Cash Vouchers (GST Vouchers)"
            ]
        )
        submit_button = st.form_submit_button("Start Chatting 🚀")
        
        if submit_button:
            st.session_state.onboarding_done = True
            st.session_state.user_age = user_age
            st.session_state.user_needs = help_category
            
            intro_msg = (
                f"Hello! I've noted that you are **{user_age} years old** and looking for assistance with **{help_category}**. "
                f"How can I help you explore your eligible support schemes today?"
            )
            
            intro_chips = [
                "What schemes am I eligible for?",
                "What are the income criteria?",
                "How do I submit an application?"
            ]
            st.session_state.messages.append({"role": "assistant", "content": intro_msg, "chips": intro_chips})
            st.rerun()

else:
    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.info(f"👤 **Profile:** Age {st.session_state.get('user_age', 'N/A')}\n\n🎯 **Focus:** {st.session_state.get('user_needs', 'General')}")
        
        base_system_prompt = st.text_area(
            "System Prompt",
            value=(
                "You are SG Care Finder, a helpful AI assistant dedicated to guiding Singaporeans on government support schemes, "
                "grants, subsidies, and assistance programs (such as ComCare, CHAS, Silver Support, MediFund, GST Vouchers, and CPF support).\n"
                "GUIDELINES:\n"
                "1. Always answer questions regarding Singapore assistance schemes, eligibility criteria, required documents, application steps, and general guidance.\n"
                "2. Fully answer any follow-up questions or suggestions selected by the user to help them understand their options.\n"
                "3. Only decline queries that are completely unrelated to Singapore assistance programs or general citizen support (e.g., coding, fiction, recipe generation).\n"
                "4. Strictly base your answers ONLY on the retrieved policy document context. If the requested information or scheme is not found in the uploaded documents, state clearly: 'I cannot find information on that scheme in the uploaded policy documents.' Do not use outside knowledge or general training memory."
            ),
            height=180,
        )
        
        if st.button("🔄 Restart Onboarding"):
            st.session_state.onboarding_done = False
            st.session_state.messages = []
            st.rerun()

        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

        if not query_engine:
            st.warning("⚠️ No PDFs found in the `data/` folder.")
        else:
            st.success("📚 RAG Knowledge Base Active (Table Parsing Enabled)")

        if st.session_state.get("messages"):
            total_tokens = sum(
                count_tokens(m["content"]) for m in st.session_state.messages
            )
            st.metric("Estimated Tokens Used", total_tokens)

    # ── Chat history ──────────────────────────────────────────
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Render dynamic suggestion chips vertically (1 column) on the last assistant message
            if message["role"] == "assistant" and idx == len(st.session_state.messages) - 1 and "chips" in message:
                st.write("")
                st.caption("💡 Follow-up questions:")
                for chip_idx, chip_label in enumerate(message["chips"]):
                    if st.button(chip_label, key=f"chip_{idx}_{chip_idx}", use_container_width=True):
                        st.session_state.selected_chip_query = chip_label
                        st.rerun()

    # ── Handle Input (either from chat input box or clicked chip button) ──
    user_input = st.chat_input("Type your message here...")
    
    if st.session_state.selected_chip_query:
        user_input = st.session_state.selected_chip_query
        st.session_state.selected_chip_query = None  # Reset after consuming

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            if query_engine:
                user_age = st.session_state.get("user_age", "N/A")
                user_needs = st.session_state.get("user_needs", "General")
                
                profile_context = f"\n[User Context: Age {user_age}, Seeking assistance with: {user_needs}]"
                Settings.llm.system_prompt = base_system_prompt + profile_context
                
                streaming_response = query_engine.query(user_input)
                response = st.write_stream(streaming_response.response_gen)
                
                # Generate dynamic follow-up chips strictly based on the response content that was just streamed
                suggested_chips = generate_dynamic_chips(response, user_age, user_needs)
            else:
                response = "Please make sure your PDF files are placed inside the `data/` folder."
                st.write(response)
                suggested_chips = []

        st.session_state.messages.append({"role": "assistant", "content": response, "chips": suggested_chips})
        st.rerun()