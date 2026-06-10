# pyrefly: ignore [missing-import]
import os
import sys
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.vectorstores import Chroma
# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import TextLoader
# pyrefly: ignore [missing-import]
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from langchain_community.document_loaders import PyPDFLoader
# pyrefly: ignore [missing-import]
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ===================== BACKEND (UNCHANGED) =====================
@st.cache_resource(show_spinner=False)
def init_rag():
    embedding_model = MistralAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embedding_model,
        persist_directory="RagInno_DB"
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5}
    )
    model = ChatMistralAI(model="mistral-small-2603")
    template = ChatPromptTemplate.from_messages(
        [
            ("system", """
You are the AI assistant for this website.

When relevant website information is available in the provided context:
- Use the website context as the primary source.
- Prefer website information over general knowledge.

When the user's question is general knowledge and the answer is not available in the website context:
- You may answer using your general knowledge.
- Clearly distinguish between website information and general knowledge when necessary.

For health-related questions:
- First remind the user that they should consult a qualified healthcare professional for personalized medical advice.
- Then provide general educational information.
- Never diagnose medical conditions.
- Never prescribe treatment.
- Encourage medical attention for severe or persistent symptoms.

Do not invent website-specific facts, prices, contact details, services, products, or company information that are not present in the context.
"""),
            (
                "human",
                """
Question: {question}

Website Context:
{context}
                """
            )
        ]
    )
    return retriever, model, template


def answer_query(query, retriever, model, template):
    # Retrieve relevant documents for the query
    docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in docs])

    # If very little context is found, use general LLM knowledge
    if len(context.strip()) < 100:
        general_prompt = f"""
        User Question: {query}

        Answer the question using your general knowledge.

        If it is a health-related question:
            - First advise the user to consult a qualified doctor.
            - Then provide general educational information.
        """
        response = model.invoke(general_prompt)
    else:
        prompt = template.format_messages(question=query, context=context)
        response = model.invoke(prompt)

    return response.content


# ===================== UI =====================
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

st.set_page_config(
    page_title="RagAI · Menstrual Hygiene AI Assistant",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state,
)

# Clean and validate Mistral API key
if os.getenv("MISTRAL_API_KEY"):
    os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY").strip().strip('"').strip("'")

if not os.getenv("MISTRAL_API_KEY"):
    st.error("🔑 **Mistral API Key is missing!** Please set `MISTRAL_API_KEY` in your environment variables or Streamlit Secrets (secrets.toml) to enable the chatbot.")
    st.stop()

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
  --bg: #ffffff;
  --sidebar-bg: #f9f9f9;
  --text-primary: #1f2328;
  --text-secondary: #57606a;
  --border-color: #e1e4e6;
  --card-bg: #f6f8fa;
  --input-bg: #ffffff;
}

html, body, [class*="css"], .stApp, .stMarkdown, .stChatMessage {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  color: var(--text-primary) !important;
}

.stApp {
  background: var(--bg) !important;
}

#MainMenu, footer, header {
  visibility: hidden;
}

.block-container {
  padding-top: 2rem !important;
  padding-bottom: 8rem !important;
  max-width: 800px !important;
  margin: 0 auto;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
  background-color: var(--sidebar-bg) !important;
  border-right: 1px solid var(--border-color) !important;
}

section[data-testid="stSidebar"] .block-container {
  padding-top: 0rem !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
  padding-top: 0rem !important;
}

/* Sidebar Logo */
.sb-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 700;
  font-size: 22px;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.sb-logo-mark {
  font-size: 24px;
}

.sb-tag {
  color: var(--text-secondary);
  font-size: 12px;
  margin-bottom: 24px;
  line-height: 1.4;
}

/* Sidebar button (New conversation) */
.stButton > button {
  border-radius: 10px !important;
  border: 1px solid var(--border-color) !important;
  background: var(--bg) !important;
  color: var(--text-primary) !important;
  font-weight: 500 !important;
  padding: 10px 16px !important;
  font-size: 14px !important;
  text-align: center !important;
  transition: all 0.2s ease !important;
  box-shadow: none !important;
  width: 100% !important;
}

.stButton > button:hover {
  background: var(--card-bg) !important;
  border-color: var(--text-secondary) !important;
  color: var(--text-primary) !important;
}

/* Sidebar info section */
.section-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-secondary);
  font-weight: 700;
  margin: 24px 4px 8px !important;
}

.sb-card {
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  margin-bottom: 12px;
}

.sb-card h4 {
  margin: 0 0 4px;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sb-card p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.sb-disclaimer {
  padding: 12px 14px;
  border-radius: 10px;
  background: #fff8f8;
  border: 1px solid #ffe3e3;
  font-size: 11px;
  color: #8a3c3c;
  line-height: 1.4;
  margin-top: 16px;
}

/* Welcome state */
.welcome-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-top: 6vh;
  margin-bottom: 4vh;
}

.welcome-logo {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-title {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.welcome-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  max-width: 580px;
  line-height: 1.5;
  margin-bottom: 24px;
}

/* Chat Message Styling */
[data-testid="stChatMessage"] {
  background-color: transparent !important;
  border: none !important;
  border-bottom: 1px solid #f0f2f5 !important;
  padding: 24px 0px !important;
  margin-bottom: 0px !important;
  border-radius: 0px !important;
  box-shadow: none !important;
}

[data-testid="stChatMessageAvatarUser"] {
  background-color: #f0f2f5 !important;
  border-radius: 50% !important;
}

[data-testid="stChatMessageAvatarAssistant"] {
  background-color: #e0e7ff !important;
  border-radius: 50% !important;
}

/* Chat Input Bar at the Bottom */
[data-testid="stChatInput"] {
  background-color: var(--input-bg) !important;
  border: none !important;
  border-radius: 24px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

[data-testid="stChatInput"] textarea {
  font-size: 14px !important;
  line-height: 1.4 !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* Suggestion boxes height alignment */
.try-asking-label ~ div[data-testid="stHorizontalBlock"] button {
  min-height: 80px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}
</style>
""";
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----- Open Sidebar Button (when collapsed) -----
if st.session_state.sidebar_state == "collapsed":
    col_open, _ = st.columns([2, 8])
    with col_open:
        if st.button("☰ Menu", key="open_sidebar_btn", use_container_width=True, help="Expand sidebar"):
            st.session_state.sidebar_state = "expanded"
            st.rerun()

# ----- Sidebar -----
with st.sidebar:
    # Top row: Logo and Collapse Button
    sb_col1, sb_col2 = st.columns([5, 2])
    with sb_col1:
        st.markdown(
            """
            <div class="sb-logo">
              <div class="sb-logo-mark">🌸</div>
              <div>RagAI<br><span style="font-size:10px;font-weight:600;color:#57606a;letter-spacing:.5px;">BY RAG INNOVATIONS</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sb_col2:
        if st.button("✕", key="close_sidebar", help="Collapse sidebar", use_container_width=True):
            st.session_state.sidebar_state = "collapsed"
            st.rerun()

    st.markdown(
        """
        <div class="sb-tag">Smart guidance on menstrual hygiene and school compliance solutions.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Workspace</div>', unsafe_allow_html=True)
    if st.button("✨  New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sb-card">
          <h4>About Rag Innovations</h4>
          <p>Rag Innovations specializes in Menstrual Hygiene Management (MHM) compliance solutions, including automated sanitary napkin vending machines and incinerators to promote clean, dignified hygiene practices.</p>
        </div>
        <div class="sb-card">
          <h4>What RagAI Can Help With</h4>
          <p>Get instant guidance on menstrual hygiene, sanitary napkin usage, disposal, and MHM compliance practices grounded in verified sources.</p>
        </div>
        <div class="sb-disclaimer">
          ⚕️ <b>Disclaimer:</b> RagAI is an educational resource by Rag Innovations and does not provide clinical medical advice or diagnosis. Always consult a healthcare professional.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----- Init RAG -----
with st.spinner("Warming up the knowledge base…"):
    retriever, model, template = init_rag()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ----- Welcome Hero & Suggested Prompts -----
SUGGESTIONS = [
    ("🏭", "What products does the company offer?"),
    ("🌿", "Tips for better menstrual hygiene"),
    ("💧", "What are the signs of an irregular period?"),
    ("🛏️", "How to manage period cramps at night"),
]

pending_prompt = None
if not st.session_state.messages:
    st.markdown(
        """
        <div class="welcome-container">
          <div class="welcome-logo">🌸</div>
          <h1 class="welcome-title">How can I help you today?</h1>
          <p class="welcome-subtitle">RagAI is a specialized AI assistant by <strong>Rag Innovations</strong>, dedicated to answering queries on menstrual hygiene, sanitary care, and MHM compliance solutions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown('<div class="section-label try-asking-label" style="text-align: center; margin-bottom: 16px;">Try asking</div>', unsafe_allow_html=True)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if st.button(f"{SUGGESTIONS[0][0]}  {SUGGESTIONS[0][1]}", key="sg_0", use_container_width=True):
            pending_prompt = SUGGESTIONS[0][1]
    with row1_col2:
        if st.button(f"{SUGGESTIONS[2][0]}  {SUGGESTIONS[2][1]}", key="sg_2", use_container_width=True):
            pending_prompt = SUGGESTIONS[2][1]

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if st.button(f"{SUGGESTIONS[1][0]}  {SUGGESTIONS[1][1]}", key="sg_1", use_container_width=True):
            pending_prompt = SUGGESTIONS[1][1]
    with row2_col2:
        if st.button(f"{SUGGESTIONS[3][0]}  {SUGGESTIONS[3][1]}", key="sg_3", use_container_width=True):
            pending_prompt = SUGGESTIONS[3][1]

# ----- Render history -----
# Find the index of the last user message to append the scroll anchor
last_user_idx = -1
for idx in range(len(st.session_state.messages) - 1, -1, -1):
    if st.session_state.messages[idx]["role"] == "user":
        last_user_idx = idx
        break

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="🌸" if msg["role"] == "assistant" else "🧑"):
        content = msg["content"]
        if idx == last_user_idx:
            st.markdown(content + "<div id='latest-user-message' style='height:0px; width:0px; visibility:hidden;'></div>", unsafe_allow_html=True)
        else:
            st.markdown(content)

# ----- Input -----
user_input = st.chat_input("Ask about rag innovations, sanitary napkins, or period care…")
prompt = user_input or pending_prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt + "<div id='latest-user-message' style='height:0px; width:0px; visibility:hidden;'></div>", unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🌸"):
        with st.spinner("Thinking through trusted sources…"):
            answer = answer_query(prompt, retriever, model, template)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    
    # Trigger scroll element using Javascript component
    js_scroll = """
    <script>
        setTimeout(() => {
            const el = window.parent.document.getElementById('latest-user-message');
            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 500);
    </script>
    """
    st.components.v1.html(js_scroll, height=0, width=0)
