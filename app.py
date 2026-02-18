import streamlit as st
import requests
import json
import PyPDF2
import docx2txt
from io import StringIO
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

# --- Page config (must be first) ---
st.set_page_config(
    page_title="StudyForge AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN CUSTOM CSS ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main header with gradient */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* Subheader */
    .sub-header {
        text-align: center;
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Upload area styling */
    .upload-area {
        background: white;
        border: 2px dashed #E5E7EB;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .upload-area:hover {
        border-color: #667eea;
        background: #F9FAFB;
    }
    
    /* Flashcard container */
    .flashcard-container {
        perspective: 1000px;
        margin: 1rem 0;
    }
    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        cursor: pointer;
        min-height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        transition: transform 0.3s, box-shadow 0.3s;
        transform-style: preserve-3d;
    }
    .flashcard:hover {
        transform: scale(1.02) translateY(-5px);
        box-shadow: 0 25px 30px -5px rgba(102, 126, 234, 0.3);
    }
    .flashcard h2 {
        margin: 0;
        font-weight: 600;
        font-size: 1.5rem;
    }
    
    /* Answer side different color */
    .flashcard-answer {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 50px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(102,126,234,0.4) !important;
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Metrics */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stMetric label {
        color: #6B7280 !important;
        font-weight: 500 !important;
    }
    .stMetric .metric-value {
        color: #1F2937 !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
        border-bottom: 2px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        color: #6B7280;
        border-radius: 0;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        color: #667eea !important;
        border-bottom: 3px solid #667eea !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px;
        height: 8px !important;
    }
    
    /* Expanders for questions */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }
    .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        box-shadow: 0 4px 6px rgba(102,126,234,0.1) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        .flashcard {
            min-height: 200px;
            padding: 1.5rem;
        }
        .flashcard h2 {
            font-size: 1.2rem;
        }
    }
    
    /* Dark mode support (if user's system prefers dark) */
    @media (prefers-color-scheme: dark) {
        .upload-area {
            background: #1F2937;
            border-color: #374151;
        }
        .upload-area:hover {
            background: #111827;
        }
        .stMetric {
            background: #1F2937;
        }
        .stMetric label {
            color: #9CA3AF !important;
        }
        .stMetric .metric-value {
            color: #F9FAFB !important;
        }
        .streamlit-expanderHeader {
            background: #1F2937 !important;
            border-color: #374151 !important;
            color: #F9FAFB !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- Session state initialization (MUST be before any access) ---
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_card' not in st.session_state:
    st.session_state.current_card = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# --- Header with modern styling ---
st.markdown('<h1 class="main-header">📚 StudyForge AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your lecture notes into smart flashcards and practice questions instantly ✨</p>', unsafe_allow_html=True)

# --- Sidebar for additional options (optional) ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")
    st.markdown("**About**")
    st.markdown("StudyForge AI uses cutting-edge models to generate study materials from your notes.")
    st.markdown("---")
    st.markdown("Made with ❤️ in HK")
    st.markdown("Powered by Hugging Face")

# --- Helper functions ---
def extract_text_from_file(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx2txt.process(uploaded_file)
    elif uploaded_file.type == "text/plain":
        text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
    return text

def generate_with_huggingface(prompt, system_prompt=None, temperature=0.7, max_retries=2):
    """Generate content using the new Hugging Face Router API (OpenAI-compatible)."""
    if not HF_TOKEN:
        st.error("Hugging Face API token not found. Please add it to your .env file.")
        return None

    # Correct router endpoint
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Construct messages in OpenAI format
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Reliable, free model (you can change this)
    MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1000,
        "stream": False
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                st.warning(f"API attempt {attempt+1} failed: {error_msg}")
                if response.status_code == 401:
                    st.error("Your Hugging Face token is invalid or expired. Please generate a new one at https://huggingface.co/settings/tokens and update your .env file.")
                    return None
        except Exception as e:
            st.warning(f"Request error (attempt {attempt+1}): {str(e)}")
    return None

def create_intelligent_fallback_flashcards(text):
    sentences = re.split(r'[.!?]+', text)
    flashcards = []
    for sent in sentences:
        sent = sent.strip()
        if len(sent) > 40 and any(kw in sent.lower() for kw in ['define', 'is', 'are', 'refers', 'example', 'because']):
            question = f"What is meant by: {sent[:50]}...?"
            flashcards.append({"front": question, "back": sent})
    if not flashcards:
        for sent in sentences[:10]:
            if len(sent.strip()) > 30:
                flashcards.append({"front": f"Explain: {sent[:50]}...", "back": sent.strip()})
    return flashcards[:10]

def generate_flashcards(text):
    system_prompt = """You are an expert tutor creating **detailed flashcards** from lecture notes. 
Each flashcard must:
- Focus on a **specific key concept**, definition, formula, example, or important fact.
- Avoid generic questions like "What is the lecture about?" or "Who is the instructor?".
- Be concise but precise: the front should be a clear question, the back should be the answer.
- Cover the most important 8-12 points from the notes.

**Example of a good flashcard:**
{"front": "What is the function of the mitochondria in a cell?", "back": "The mitochondria generates ATP through cellular respiration, providing energy for the cell."}

Respond **only** with a JSON array of objects with 'front' and 'back' keys. No other text.
"""
    prompt = f"Lecture notes:\n\n{text[:3500]}\n\nGenerate 8-12 high-quality flashcards based **only** on the content above."
    
    response = generate_with_huggingface(prompt, system_prompt, temperature=0.8)
    
    if response:
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                cards = json.loads(json_match.group())
                if isinstance(cards, list) and all('front' in c and 'back' in c for c in cards):
                    return cards[:15]
            except:
                pass
    return create_intelligent_fallback_flashcards(text)

def create_intelligent_fallback_questions(text):
    sentences = re.split(r'[.!?]+', text)
    questions = []
    for i, sent in enumerate(sentences[:5]):
        sent = sent.strip()
        if len(sent) > 50:
            questions.append({
                "type": "short_answer",
                "question": f"Explain: {sent[:100]}...",
                "answer": sent,
                "explanation": "Directly from notes."
            })
    if not questions:
        questions = [{
            "type": "multiple_choice",
            "question": "What is the main topic?",
            "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
            "answer": "Topic A",
            "explanation": "Based on notes."
        }]
    return questions

def generate_questions(text):
    system_prompt = """You are an expert educator creating **practice questions** from lecture notes.
Requirements:
- Create a mix of multiple-choice (with 4 options), true/false, and short answer questions.
- Each question must directly test understanding of the **actual content** (definitions, relationships, applications).
- Avoid generic metadata questions (e.g., "What is the course number?").
- For multiple-choice, include 4 options labeled A, B, C, D and indicate the correct one in 'answer'.
- Provide a brief 'explanation' for the correct answer.

**Example:**
{"type": "multiple_choice", "question": "What is the primary function of the mitochondria?", "options": ["A) Protein synthesis", "B) ATP production", "C) Lipid storage", "D) DNA replication"], "answer": "B", "explanation": "Mitochondria are known as the powerhouse of the cell because they generate ATP."}

Respond **only** with a JSON array of question objects. No other text.
"""
    prompt = f"Lecture notes:\n\n{text[:3500]}\n\nGenerate 5-7 practice questions based **only** on the content above."
    
    response = generate_with_huggingface(prompt, system_prompt, temperature=0.8)
    
    if response:
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            try:
                qs = json.loads(json_match.group())
                if isinstance(qs, list):
                    return qs[:10]
            except:
                pass
    return create_intelligent_fallback_questions(text)

# --- Main layout with improved spacing ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    # Wrap upload area in a styled container
    with st.container():
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        st.markdown("### 📤 Upload Notes")
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, DOCX, TXT)", 
            type=['pdf', 'docx', 'txt'],
            label_visibility="collapsed"
        )
        st.caption("Supported formats: PDF, DOCX, TXT (max 200MB)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        with st.spinner("🔍 Extracting text..."):
            text = extract_text_from_file(uploaded_file)
            st.success(f"✅ Extracted {len(text)} characters")
        
        # Generate button with prominent styling
        if st.button("🚀 Generate Study Materials", type="primary", use_container_width=True):
            with st.spinner("🧠 Generating flashcards..."):
                st.session_state.flashcards = generate_flashcards(text)
            with st.spinner("📝 Creating practice questions..."):
                st.session_state.questions = generate_questions(text)
            st.balloons()  # Fun success animation
            st.success("✅ Your study materials are ready!")
    
    # Metrics with icons
    if st.session_state.flashcards:
        st.metric("📇 Flashcards", len(st.session_state.flashcards))
    if st.session_state.questions:
        st.metric("❓ Questions", len(st.session_state.questions))

with col2:
    tab1, tab2 = st.tabs(["🎴 Flashcards", "📝 Practice Questions"])
    
    with tab1:
        if st.session_state.flashcards:
            # Navigation controls in a row
            nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])
            with nav_col1:
                if st.button("◀ Previous", disabled=st.session_state.current_card == 0, use_container_width=True):
                    st.session_state.current_card -= 1
                    st.session_state.show_answer = False
            with nav_col3:
                if st.button("Next ▶", disabled=st.session_state.current_card == len(st.session_state.flashcards)-1, use_container_width=True):
                    st.session_state.current_card += 1
                    st.session_state.show_answer = False
            
            # Flashcard display
            card = st.session_state.flashcards[st.session_state.current_card]
            
            # Flip button
            if st.button("🔄 Click to flip", use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
            
            # Card with dynamic class for answer side
            card_class = "flashcard flashcard-answer" if st.session_state.show_answer else "flashcard"
            st.markdown(
                f'<div class="flashcard-container"><div class="{card_class}"><h2>{card["back"] if st.session_state.show_answer else card["front"]}</h2></div></div>',
                unsafe_allow_html=True
            )
            
            # Progress
            st.progress((st.session_state.current_card + 1) / len(st.session_state.flashcards))
            st.caption(f"📌 Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)}")
            
            # Export
            if st.button("💾 Download Flashcards", use_container_width=True):
                json_str = json.dumps(st.session_state.flashcards, indent=2)
                st.download_button(
                    "Download JSON", 
                    json_str, 
                    file_name="flashcards.json", 
                    mime="application/json",
                    use_container_width=True
                )
        else:
            st.info("👆 Upload your notes and generate flashcards to get started!", icon="ℹ️")
    
    with tab2:
        if st.session_state.questions:
            for i, q in enumerate(st.session_state.questions):
                with st.expander(f"**Q{i+1}:** {q['question'][:80]}..."):
                    st.markdown(f"**Type:** `{q.get('type', 'General')}`")
                    st.markdown(f"**Question:** {q['question']}")
                    if q.get('options'):
                        st.markdown("**Options:**")
                        for opt in q['options']:
                            st.markdown(f"- {opt}")
                    if st.button(f"✨ Show Answer", key=f"ans_{i}"):
                        st.success(f"**Answer:** {q.get('answer', 'N/A')}")
                        if q.get('explanation'):
                            st.info(f"💡 {q['explanation']}")
        else:
            st.info("👆 Generate materials to see practice questions!", icon="ℹ️")

# --- Footer with nice separator ---
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1,2,1])
with footer_col2:
    st.markdown(
        "<p style='text-align: center; color: #6B7280;'>"
        "Built with ❤️ using Streamlit & Hugging Face | Free for everyone"
        "</p>", 
        unsafe_allow_html=True
    )