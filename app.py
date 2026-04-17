"""
TalentScout Hiring Assistant - Main Streamlit Application.
An intelligent chatbot for candidate screening in tech recruitment.
"""

import streamlit as st
from config import APP_NAME, APP_TAGLINE, APP_VERSION
from llm_service import LLMService
from conversation_manager import ConversationManager, ConversationState
from candidate_store import save_candidate
from utils import format_collected_info


# ─── Page Configuration ───────────────────────────────────────────────
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styling for Notion-like feel */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, "Apple Color Emoji", Arial, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
        color: #37352f;
    }

    /* Header */
    .main-header {
        text-align: left;
        padding: 2rem 0 1rem;
        border-bottom: 1px solid rgba(55, 53, 47, 0.09);
        margin-bottom: 2rem;
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #37352f;
        letter-spacing: -0.03em;
    }
    .main-header p {
        font-size: 1rem;
        color: rgba(55, 53, 47, 0.6);
        margin: 0.25rem 0 0;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f7f6f3;
        border-right: 1px solid rgba(55, 53, 47, 0.09);
    }
    .sidebar-section {
        background: #ffffff;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(55, 53, 47, 0.09);
        box-shadow: rgba(15, 15, 15, 0.05) 0px 0px 0px 1px, rgba(15, 15, 15, 0.1) 0px 2px 4px;
    }
    .sidebar-section h3 {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(55, 53, 47, 0.5);
        margin-bottom: 0.75rem;
    }

    /* Progress bar */
    .progress-container {
        background: rgba(55, 53, 47, 0.09);
        border-radius: 999px;
        height: 6px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    .progress-fill {
        background: #37352f;
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 4px !important;
        border: 1px solid rgba(55, 53, 47, 0.09) !important;
        background-color: #ffffff;
        box-shadow: none;
    }

    /* Primary button override */
    .stButton > button {
        border-radius: 4px;
        border: 1px solid rgba(55, 53, 47, 0.16);
        color: #37352f;
        background-color: #ffffff;
        font-weight: 500;
        transition: background-color 0.1s ease;
    }
    .stButton > button:hover {
        background-color: rgba(55, 53, 47, 0.04);
        border-color: rgba(55, 53, 47, 0.16);
        color: #37352f;
    }

    /* Footer */
    .footer {
        text-align: left;
        padding: 1rem 0;
        color: rgba(55, 53, 47, 0.5);
        font-size: 0.75rem;
        border-top: 1px solid rgba(55, 53, 47, 0.09);
        margin-top: 3rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ─────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = None
    if "llm_service" not in st.session_state:
        st.session_state.llm_service = None
    if "data_saved" not in st.session_state:
        st.session_state.data_saved = False
    if "error" not in st.session_state:
        st.session_state.error = None


def initialize_services():
    """Initialize LLM service and conversation manager."""
    try:
        llm_service = LLMService()
        conv_manager = ConversationManager(llm_service)
        st.session_state.llm_service = llm_service
        st.session_state.conversation_manager = conv_manager
        st.session_state.error = None
        return True
    except ValueError as e:
        st.session_state.error = str(e)
        return False


def reset_conversation():
    """Reset the conversation to start fresh."""
    st.session_state.messages = []
    st.session_state.conversation_manager = None
    st.session_state.llm_service = None
    st.session_state.initialized = False
    st.session_state.data_saved = False
    st.session_state.error = None


# ─── Sidebar ──────────────────────────────────────────────────────────
def render_sidebar():
    """Render the sidebar with branding, controls, and candidate info."""
    with st.sidebar:
        st.markdown(f"## {APP_NAME}")
        st.caption(f"{APP_TAGLINE} • v{APP_VERSION}")
        st.divider()

        # New session button
        if st.button("New Session", use_container_width=True):
            reset_conversation()
            st.rerun()

        conv_mgr = st.session_state.conversation_manager
        if conv_mgr is None:
            return

        # Progress
        progress = conv_mgr.get_progress_percentage()
        st.markdown(f"""
        <div class="sidebar-section">
            <h3>Screening Progress</h3>
            <div class="progress-container">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <p style="font-size:0.8rem; margin:0.25rem 0 0; color:#6b7280;">
                {conv_mgr.get_current_state_description()} — {progress}%
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Candidate info summary
        if conv_mgr.candidate_data:
            st.markdown('<div class="sidebar-section"><h3>Candidate Info</h3>', unsafe_allow_html=True)
            info = format_collected_info(conv_mgr.candidate_data)
            st.text(info)
            st.markdown('</div>', unsafe_allow_html=True)

        # Sentiment indicator
        sentiment = conv_mgr.get_latest_sentiment()
        st.markdown(f"""
        <div class="sidebar-section">
            <h3>Candidate Sentiment</h3>
            <p style="font-size: 1.5rem; text-align: center; margin: 0;">
                {sentiment['emoji']}
            </p>
            <p style="font-size: 0.8rem; text-align: center; color: #6b7280; margin: 0;">
                {sentiment['label'].capitalize()} ({sentiment['polarity']})
            </p>
        </div>
        """, unsafe_allow_html=True)

        # GDPR Notice
        st.divider()
        st.caption(
            "**Data Privacy**: All candidate data is handled in compliance "
            "with GDPR standards. Data is stored securely and can be deleted "
            "upon request."
        )


# ─── Main Chat Interface ─────────────────────────────────────────────
def render_chat():
    """Render the main chat interface."""
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_NAME}</h1>
        <p>{APP_TAGLINE} — Technology Recruitment Screening</p>
    </div>
    """, unsafe_allow_html=True)

    # Error state
    if st.session_state.error:
        st.error(st.session_state.error)
        st.info("Please add your VoidAI API key to the `.env` file and restart the application.")
        st.code("VOIDAI_API_KEY=your_key_here", language="text")
        return

    conv_mgr = st.session_state.conversation_manager

    # Generate greeting on first load
    if not st.session_state.initialized and conv_mgr:
        with st.spinner("Starting your screening session..."):
            greeting = conv_mgr.get_greeting()
            st.session_state.messages.append({"role": "assistant", "content": greeting})
            st.session_state.initialized = True

    # Display chat history
    for message in st.session_state.messages:
        avatar = "assistant" if message["role"] == "assistant" else "user"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Check if conversation has ended
    if conv_mgr and conv_mgr.state == ConversationState.ENDED:
        # Save data once
        if not st.session_state.data_saved:
            try:
                save_candidate(
                    conv_mgr.candidate_data,
                    conv_mgr.tech_answers,
                    conv_mgr.sentiment_history,
                )
                st.session_state.data_saved = True
            except Exception:
                pass  # Silently handle save errors

        st.info("This screening session has ended. Click **New Session** in the sidebar to start over.")
        return

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user", avatar="user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.chat_message("assistant", avatar="assistant"):
            with st.spinner("Thinking..."):
                response = conv_mgr.process_input(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Rerun to update sidebar
        st.rerun()

    # Footer
    st.markdown(
        '<div class="footer">Built by TalentScout • Powered by AI</div>',
        unsafe_allow_html=True,
    )


# ─── Entry Point ──────────────────────────────────────────────────────
def main():
    """Main application entry point."""
    init_session_state()

    # Initialize services if not done
    if st.session_state.conversation_manager is None and st.session_state.error is None:
        initialize_services()

    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
