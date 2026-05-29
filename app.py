import streamlit as st
from groq import Groq
from soul_prompt import SOUL_SYSTEM_PROMPT
from memory_manager import load_memory, save_memory, build_memory_context

st.set_page_config(
    page_title="AI Chatbot",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #ffffff !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: #111 !important;
}

[data-testid="stMainBlockContainer"] {
    max-width: 700px !important;
    padding: 0 1.5rem 7rem !important;
    margin: 0 auto !important;
}

/* Hide all chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stSidebarCollapsedControl"],
#MainMenu, footer { display: none !important; }

/* ── Top bar ── */
.topbar {
    position: sticky;
    top: 0;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid #f0f0f0;
    padding: 1rem 0;
    margin-bottom: 2rem;
    z-index: 100;
}
.topbar-inner {
    display: flex;
    align-items: center;
    gap: 10px;
}
.topbar-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    flex-shrink: 0;
    animation: breathe 3s ease-in-out infinite;
}
@keyframes breathe {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.topbar-title {
    font-size: 0.85rem;
    font-weight: 500;
    color: #111;
    letter-spacing: -0.01em;
}
.topbar-sub {
    font-size: 0.75rem;
    color: #aaa;
    margin-left: auto;
}

/* ── Messages ── */
.msg-group { margin: 1.75rem 0; display: flex; flex-direction: column; gap: 4px; }

.msg-user-wrap { display: flex; justify-content: flex-end; }
.msg-user {
    background: #f4f4f4;
    color: #111;
    font-size: 0.9rem;
    line-height: 1.6;
    padding: 0.65rem 1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 78%;
    word-wrap: break-word;
}

.msg-ai-wrap { display: flex; align-items: flex-start; gap: 10px; }
.msg-ai-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #111;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.msg-ai-avatar span {
    font-size: 11px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.02em;
}
.msg-ai {
    font-size: 0.92rem;
    line-height: 1.75;
    color: #111;
    max-width: 85%;
    padding-top: 3px;
}

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 6rem 2rem;
    gap: 12px;
    text-align: center;
}
.empty-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #f4f4f4;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-bottom: 4px;
}
.empty-title {
    font-size: 1rem;
    font-weight: 500;
    color: #111;
}
.empty-sub {
    font-size: 0.82rem;
    color: #aaa;
    max-width: 280px;
    line-height: 1.5;
}

/* ── Input bar ── */
[data-testid="stBottom"] {
    background: rgba(255,255,255,0.95) !important;
    backdrop-filter: blur(12px) !important;
    border-top: 1px solid #f0f0f0 !important;
    padding: 0.75rem 1.5rem 1rem !important;
}
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] > div {
    background: #f7f7f7 !important;
    border: 1px solid #e8e8e8 !important;
    border-radius: 24px !important;
    box-shadow: none !important;
    transition: border-color 0.15s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #bbb !important;
    background: #fff !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    border-radius: 24px !important;
    color: #111 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1rem !important;
    box-shadow: none !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: #bbb !important; }
[data-testid="stChatInput"] button {
    background: #111 !important;
    border-radius: 50% !important;
    color: #fff !important;
    margin: 4px !important;
}

/* Spinner */
[data-testid="stSpinner"] {
    padding-left: 38px !important;
}
[data-testid="stSpinner"] p {
    font-size: 0.8rem !important;
    color: #bbb !important;
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ── API Key ────────────────────────────────────────────────────────────────────
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") = "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"


if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = load_memory()

memory = st.session_state.memory

st.markdown("""
<div class="topbar">
    <div class="topbar-inner">
        <div class="topbar-dot"></div>
        <span class="topbar-title">AI Assistant</span>
        <span class="topbar-sub">Llama 3 · Groq</span>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">✦</div>
        <div class="empty-title">Start a conversation</div>
        <div class="empty-sub">Ask me anything — I think, reflect, and remember.</div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-group">
            <div class="msg-user-wrap">
                <div class="msg-user">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-group">
            <div class="msg-ai-wrap">
                <div class="msg-ai-avatar"><span>AI</span></div>
                <div class="msg-ai">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)

def chat(user_input: str) -> str:
    memory_ctx = build_memory_context(memory)
    system = SOUL_SYSTEM_PROMPT + ("\n\n" + memory_ctx if memory_ctx else "")
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    history.append({"role": "user", "content": user_input})
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": system}] + history,
            temperature=0.9,
            max_tokens=400,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Something went wrong: {e}"

user_input = st.chat_input("Message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner(""):
        response = chat(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_memory(memory)
    st.rerun()