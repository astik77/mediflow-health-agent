import streamlit as st
from auth.session_manager import SessionManager
from components.footer import show_footer
from config.app_config import ANALYSIS_DAILY_LIMIT, PRIMARY_COLOR


def html(content: str):
    """Safely render HTML without markdown parser converting tags to raw code blocks."""
    st.html(content)


def show_sidebar():
    with st.sidebar:
        html("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
            <span style="font-size: 1.2rem;">💬</span>
            <span style="font-weight: 700; color: #F8FAFC; font-size: 1.05rem;">Diagnostic History</span>
        </div>
        """)

        if st.button("➕ New Diagnostic Session", use_container_width=True, type="primary"):
            if st.session_state.user and "id" in st.session_state.user:
                success, session = SessionManager.create_chat_session()
                if success:
                    st.session_state.current_session = session
                    st.rerun()
                else:
                    st.error("Failed to create session.")
            else:
                st.error("Session expired. Please log in again.")
                SessionManager.logout()
                st.rerun()

        # Quota progress meter
        if "analysis_count" not in st.session_state:
            st.session_state.analysis_count = 0

        remaining = max(0, ANALYSIS_DAILY_LIMIT - st.session_state.analysis_count)
        pct = int((remaining / ANALYSIS_DAILY_LIMIT) * 100)
        quota_color = "#38BDF8" if remaining > 3 else ("#F59E0B" if remaining > 0 else "#EF4444")

        html(f"""
        <div style="background: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 10px 12px; margin: 0.75rem 0 1rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: #94A3B8; margin-bottom: 6px;">
                <span>Daily Analysis Quota</span>
                <span style="color: {quota_color}; font-weight: 700;">{remaining}/{ANALYSIS_DAILY_LIMIT}</span>
            </div>
            <div style="background: #1E293B; height: 5px; border-radius: 9999px; overflow: hidden;">
                <div style="background: {quota_color}; width: {pct}%; height: 100%; border-radius: 9999px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """)

        html("<hr style='margin: 0.5rem 0 1rem 0; border: none; border-top: 1px solid #334155;'>")
        show_session_list()

        html("<hr style='margin: 1rem 0 0.5rem 0; border: none; border-top: 1px solid #334155;'>")
        if st.button("Sign Out", use_container_width=True, type="secondary"):
            html("<script>try{localStorage.removeItem('mediflow_auth_token');}catch(e){}</script>")
            SessionManager.logout()
            st.rerun()

        show_footer(in_sidebar=True)


def show_session_list():
    if st.session_state.user and "id" in st.session_state.user:
        success, sessions = SessionManager.get_user_sessions()
        if success:
            if sessions:
                html("<div style='font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Previous Reports</div>")
                render_session_list(sessions)
            else:
                html("<div style='font-size: 0.85rem; color: #64748B; text-align: center; padding: 1rem 0;'>No previous reports found.</div>")


def render_session_list(sessions):
    if "delete_confirmation" not in st.session_state:
        st.session_state.delete_confirmation = None

    for session in sessions:
        render_session_item(session)


def render_session_item(session):
    if not session or not isinstance(session, dict) or "id" not in session:
        return

    session_id = session["id"]
    current_session = st.session_state.get("current_session", {})
    current_session_id = current_session.get("id") if isinstance(current_session, dict) else None
    is_active = current_session_id == session_id

    icon = "🩺" if is_active else "📄"

    with st.container():
        title_col, delete_col = st.columns([5, 1])

        with title_col:
            button_label = f"{icon} {session['title']}"
            if st.button(
                button_label,
                key=f"session_{session_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_session = session
                st.query_params["session_id"] = session["id"]
                st.rerun()

        with delete_col:
            if st.button("🗑️", key=f"delete_{session_id}", help="Delete this session"):
                if st.session_state.delete_confirmation == session_id:
                    st.session_state.delete_confirmation = None
                else:
                    st.session_state.delete_confirmation = session_id
                st.rerun()

        if st.session_state.delete_confirmation == session_id:
            html("<div style='background: #450A0A; border: 1px solid #991B1B; border-radius: 6px; padding: 8px 10px; margin: 4px 0 8px 0; font-size: 0.82rem; color: #FECACA;'>Delete this session permanently?</div>")
            left_btn, right_btn = st.columns(2)
            with left_btn:
                if st.button("Yes, delete", key=f"confirm_delete_{session_id}", type="primary", use_container_width=True):
                    handle_delete_confirmation(session_id, current_session_id)
            with right_btn:
                if st.button("Cancel", key=f"cancel_delete_{session_id}", use_container_width=True):
                    st.session_state.delete_confirmation = None
                    st.rerun()


def handle_delete_confirmation(session_id, current_session_id):
    if not session_id:
        st.error("Invalid session ID.")
        return

    success, error = SessionManager.delete_session(session_id)
    if success:
        st.session_state.delete_confirmation = None
        if current_session_id and current_session_id == session_id:
            st.session_state.current_session = None
        st.rerun()
    else:
        st.error(f"Failed to delete session: {error}")
