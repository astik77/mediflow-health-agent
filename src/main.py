import streamlit as st
from auth.session_manager import SessionManager
from components.auth_pages import show_login_page
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from config.app_config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_ICON, PRIMARY_COLOR, SECONDARY_COLOR
from services.ai_service import get_chat_response

# Must be the first Streamlit command
st.set_page_config(
    page_title="MediFlow - Health Management Agent",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
SessionManager.init_session()


def html(content: str):
    """Safely render HTML without markdown parser converting tags to raw code blocks."""
    st.html(content)


# Global Design System: Dark Slate & Sky Blue Styling
html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F8FAFC;
    }

    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.15s ease-in-out !important;
    }

    .stButton > button[kind="primary"] {
        background-color: #0284C7 !important;
        border: 1px solid #38BDF8 !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(56, 189, 248, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #0369A1 !important;
        border-color: #7DD3FC !important;
    }

    .stButton > button[kind="secondary"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: #38BDF8 !important;
        color: #38BDF8 !important;
        background-color: #0F172A !important;
    }

    .stTextInput input, .stNumberInput input, .stSelectbox select {
        border-radius: 8px !important;
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #F8FAFC !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    }

    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: #F8FAFC !important;
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }

    /* Clinical chat message container */
    div[data-testid="stChatMessage"] {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 1.15rem 1.35rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    }
</style>
""")


def show_welcome_screen():
    """Dark Slate & Sky Blue hero section."""
    html(f"""
    <div style="background: #1E293B; border: 1px solid #334155; border-radius: 14px; padding: 2.75rem 2rem; text-align: center; margin: 1rem auto 2rem auto; max-width: 900px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);">
        <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 14px; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; color: #38BDF8; margin-bottom: 1rem;">
            <span>{APP_ICON}</span> Clinical Diagnostics & Intelligence
        </div>
        <h1 style="font-size: 2.35rem; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em; margin: 0 0 0.5rem 0;">{APP_NAME}</h1>
        <p style="font-size: 1.05rem; font-weight: 600; color: #38BDF8; margin: 0 0 0.75rem 0;">{APP_TAGLINE}</p>
        <p style="font-size: 0.92rem; color: #94A3B8; max-width: 680px; margin: 0 auto 2rem auto; line-height: 1.6;">{APP_DESCRIPTION}</p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin: 1.5rem auto 2rem auto; text-align: left;">
            <div style="background: #0F172A; border: 1px solid #334155; padding: 1.15rem; border-radius: 8px;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">⚡</div>
                <div style="font-weight: 700; color: #F8FAFC; font-size: 0.92rem; margin-bottom: 3px;">120B Multi-Model Cascade</div>
                <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.45;">High-precision clinical synthesis with automated 4-tier model fallback resilience.</div>
            </div>
            <div style="background: #0F172A; border: 1px solid #334155; padding: 1.15rem; border-radius: 8px;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">🩸</div>
                <div style="font-weight: 700; color: #F8FAFC; font-size: 0.92rem; margin-bottom: 3px;">Biomarker Spectrum Mapping</div>
                <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.45;">Automated extraction across CBC, Metabolic, Lipid, Hepatic, and Thyroid profiles.</div>
            </div>
            <div style="background: #0F172A; border: 1px solid #334155; padding: 1.15rem; border-radius: 8px;">
                <div style="font-size: 1.25rem; margin-bottom: 4px;">🛡️</div>
                <div style="font-weight: 700; color: #F8FAFC; font-size: 0.92rem; margin-bottom: 3px;">Evidence-Grounded RAG</div>
                <div style="font-size: 0.82rem; color: #94A3B8; line-height: 1.45;">Context-bound follow-up clinical Q&A grounded strictly in patient lab values.</div>
            </div>
        </div>
    </div>
    """)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Initialize Analysis Session", use_container_width=True, type="primary"):
            success, session = SessionManager.create_chat_session()
            if success:
                st.session_state.current_session = session
                st.rerun()
            else:
                st.error("Failed to create session. Please try again.")


def show_chat_history():
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session["id"]
    )

    if success:
        first_assistant_seen = False
        for msg in messages:
            if msg.get("role") == "system":
                continue

            content = msg.get("content", "")
            if msg.get("role") == "assistant" and content:
                import re
                content = re.sub(r"\n*---\s*\n*\*?(?:Synthesis|Analysis) generated using.*", "", content, flags=re.IGNORECASE).strip()

            if msg["role"] == "user":
                # Check if it is the initial report intake notice or a follow-up question
                if "Analyzing report for patient" in content:
                    html(f"""
                    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #334155; border-radius: 8px; padding: 8px 14px; margin: 0.85rem 0; font-size: 0.86rem; color: #94A3B8; display: flex; align-items: center; gap: 8px;">
                        <span>📋</span>
                        <span>{content}</span>
                    </div>
                    """)
                else:
                    # User Follow-up Question Block (Slate & Sky Blue accent)
                    html(f"""
                    <div style="background: #1E293B; border: 1px solid #334155; border-right: 4px solid #38BDF8; border-radius: 8px; padding: 0.9rem 1.25rem; margin: 1rem 0 1rem auto; max-width: 85%;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #38BDF8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                            <span>👤</span> Follow-Up Inquiry
                        </div>
                        <div style="color: #F8FAFC; font-size: 0.95rem; line-height: 1.55;">
                            {content}
                        </div>
                    </div>
                    """)
            else:
                # Assistant message: Check if this is the Primary Clinical Diagnosis vs Follow-up Q&A
                is_primary_diagnosis = (not first_assistant_seen) or ("AI Generated Diagnosis" in content) or ("Potential Health Risks" in content)

                if is_primary_diagnosis and not first_assistant_seen:
                    first_assistant_seen = True
                    # Primary Diagnosis Header (Clinical Teal / Emerald Theme)
                    html("""
                    <div style="background: rgba(13, 148, 136, 0.12); border: 1px solid rgba(45, 212, 191, 0.4); border-left: 5px solid #2DD4BF; border-radius: 8px; padding: 0.75rem 1.25rem; margin-top: 1.25rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 1.25rem;">🩺</span>
                                <span style="font-weight: 800; color: #2DD4BF; font-size: 0.92rem; letter-spacing: 0.03em;">
                                    AI GENERATED CLINICAL DIAGNOSIS & RISK STRATIFICATION
                                </span>
                            </div>
                            <span style="font-size: 0.72rem; background: rgba(45, 212, 191, 0.2); color: #2DD4BF; border: 1px solid rgba(45, 212, 191, 0.4); padding: 3px 10px; border-radius: 9999px; font-weight: 700;">
                                PRIMARY REPORT
                            </span>
                        </div>
                    </div>
                    """)
                    with st.chat_message("assistant", avatar="🩺"):
                        st.markdown(content)
                else:
                    # Clean Follow-up Answer
                    with st.chat_message("assistant", avatar="🩺"):
                        st.markdown(content)
        return messages
    return []


def handle_chat_input(messages):
    if prompt := st.chat_input("Ask a follow-up question regarding this report..."):
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"], prompt, role="user"
        )

        context_text = st.session_state.get("current_report_text", "")

        if not context_text and messages:
            for msg in messages:
                if msg.get("role") == "system" and "__REPORT_TEXT__" in msg.get("content", ""):
                    content = msg.get("content", "")
                    start_idx = content.find("__REPORT_TEXT__\n") + len("__REPORT_TEXT__\n")
                    end_idx = content.find("\n__END_REPORT_TEXT__")
                    if start_idx > len("__REPORT_TEXT__\n") - 1 and end_idx > start_idx:
                        context_text = content[start_idx:end_idx]
                        st.session_state.current_report_text = context_text
                        break

        with st.spinner("Synthesizing context-grounded response..."):
            response = get_chat_response(prompt, context_text, messages)

            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], response, role="assistant"
            )
            st.rerun()


def show_user_greeting():
    """Clean dark clinical top navigation bar."""
    if st.session_state.user:
        display_name = st.session_state.user.get("name") or st.session_state.user.get("email", "")
        html(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.65rem 1rem; background: #1E293B; border: 1px solid #334155; border-radius: 8px; margin-bottom: 1.25rem;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">🩺</span>
                <span style="font-weight: 800; color: #F8FAFC; font-size: 0.98rem; letter-spacing: -0.01em;">{APP_NAME}</span>
                <span style="font-size: 0.72rem; background: rgba(56, 189, 248, 0.1); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 1px 7px; border-radius: 4px; font-weight: 600;">CLINICAL AI</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span style="height: 7px; width: 7px; background-color: #10B981; border-radius: 50%; display: inline-block;"></span>
                <span style="font-size: 0.85rem; font-weight: 500; color: #CBD5E1;">{display_name}</span>
            </div>
        </div>
        """)


def main():
    SessionManager.init_session()

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    # Sync auth token to browser localStorage for seamless reloads and new tabs
    auth_token = st.query_params.get("auth")
    if auth_token:
        html(f"""
        <script>
            try {{
                localStorage.setItem('mediflow_auth_token', '{auth_token}');
            }} catch(e) {{}}
        </script>
        """)

    show_user_greeting()
    show_sidebar()

    if st.session_state.get("current_session"):
        session_title = st.session_state.current_session.get("title", "Clinical Session")
        html(f"""
        <div style="margin-bottom: 1rem;">
            <h2 style="font-weight: 800; color: #F8FAFC; font-size: 1.4rem; margin: 0;">📊 {session_title}</h2>
            <span style="font-size: 0.82rem; color: #94A3B8;">Active Diagnostic Session</span>
        </div>
        """)

        messages = show_chat_history()

        if messages:
            with st.expander("🔄 Re-analyze / Submit Updated Report", expanded=False):
                show_analysis_form()

            handle_chat_input(messages)
        else:
            show_analysis_form()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()
