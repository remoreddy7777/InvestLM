
import streamlit as st
import pandas as pd
import PyPDF2
import requests
import json
import time

# Page setup
st.set_page_config(
    page_title="InvestLM - Investment Analysis Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom UI styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%); }
    h1, h2, h3 { color: #00d4ff !important; font-weight: 600 !important; }
    p, label, .stMarkdown { color: #e0e0e0 !important; }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #1e1e2f !important; color: #ffffff !important;
        border: 1px solid #00d4ff !important; border-radius: 8px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #0099cc 100%) !important;
        color: #ffffff !important; border: none !important; border-radius: 8px !important;
        padding: 0.5rem 2rem !important; font-weight: 600 !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4) !important;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "text_result" not in st.session_state:
    st.session_state.text_result = ""

# Backend URL (use your live ngrok URL)
API_URL = "https://jessia-confabulatory-eula.ngrok-free.dev/query"

# --- Header ---
st.markdown("<h1 style='text-align: center;'>📊 InvestLM</h1>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Investment Analysis & Research Platform</h5>", unsafe_allow_html=True)

# --- Sidebar for model options ---
st.sidebar.title("⚙️ Configuration")
analysis_type = st.sidebar.selectbox(
    "Select Analysis Type",
    ["Text Simplification", "Sentiment Analysis", "Financial Metrics", "Risk Assessment", "Market Trends"]
)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 500, 2000, 1000)

# --- Main Section ---
st.markdown("### 📝 Text Input for AI Analysis")
st.markdown("Enter or upload your investment-related text for analysis")

col1, col2 = st.columns([3, 1])

with col1:
    text_input = st.text_area(
        "Input Text",
        placeholder="Enter or paste company reports, news articles, or financial statements...",
        height=250,
        key="text_input_area"
    )

    uploaded_file = st.file_uploader(
        "Upload a .txt, .csv, or .pdf file",
        type=["txt", "csv", "pdf"],
        key="file_uploader"
    )

    # Extract text from uploaded file
    if uploaded_file is not None:
        file_text = ""
        if uploaded_file.type == "text/plain":
            file_text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            file_text = df.to_string(index=False)
        elif uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                file_text += page.extract_text() or ""

        if file_text:
            st.success("✅ File uploaded successfully!")
            text_input = file_text

with col2:
    st.markdown("#### ⚙️ Quick Actions")

    if st.button("🤖 Process with AI", use_container_width=True):
        if not text_input:
            st.warning("⚠️ Please enter or upload text to analyze")
        else:
            with st.spinner("🔄 Processing with Finance-Llama..."):
                try:
                    # Create system message and task
                    if analysis_type == "Text Simplification":
                        system_msg = "Simplify complex financial texts without losing key details."
                        task_prompt = f"Simplify this text:\n\n{text_input}"
                    elif analysis_type == "Sentiment Analysis":
                        system_msg = "Analyze financial sentiment objectively."
                        task_prompt = f"Perform sentiment analysis on:\n\n{text_input}"
                    elif analysis_type == "Financial Metrics":
                        system_msg = "Extract key financial metrics from the text."
                        task_prompt = f"Identify financial metrics in:\n\n{text_input}"
                    elif analysis_type == "Risk Assessment":
                        system_msg = "Identify potential financial and market risks."
                        task_prompt = f"Assess the risk in:\n\n{text_input}"
                    else:
                        system_msg = "Identify important market patterns and trends."
                        task_prompt = f"Find market trends in:\n\n{text_input}"

                    payload = {
                        "query": task_prompt,
                        "system_message": system_msg,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }

                    response = requests.post(API_URL, json=payload)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.text_result = data.get("response", "No response returned.")
                        st.success("✅ Analysis complete!")
                    else:
                        st.error(f"⚠️ Backend error {response.status_code}: {response.text}")

                except Exception as e:
                    st.error(f"🚨 Request failed: {e}")

    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.text_result = ""
        st.rerun()

# --- Results Section ---
if st.session_state.text_result:
    st.markdown("---")
    st.markdown(f"### 🧾 {analysis_type} Output")
    st.text_area(
        "Result",
        value=st.session_state.text_result,
        height=300,
        key="text_output"
    )

    st.download_button(
        label="📥 Download Result",
        data=st.session_state.text_result,
        file_name=f"{analysis_type.lower().replace(' ', '_')}_output.txt",
        mime="text/plain",
        use_container_width=True
    )