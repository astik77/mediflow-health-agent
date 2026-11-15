import streamlit as st
from datetime import datetime, timedelta
from config.app_config import SESSION_TIMEOUT_MINUTES
import hmac
import hashlib


class SessionManager:
    @staticmethod
    def _get_secret_key() -> bytes:
        try:
            secret = st.secrets.get("SUPABASE_KEY", "mediflow_clinical_salt")
        except Exception:
            secret = "mediflow_clinical_salt"
        return secret.encode("utf-8")

    @staticmethod
    def generate_auth_token(user_id: str, refresh_token: str = "") -> str:
        """Create a cryptographically signed auth token containing user_id and refresh_token."""
        if not refresh_token and "refresh_token" in st.session_state:
            refresh_token = st.session_state.refresh_token or ""
        payload = f"{user_id}::{refresh_token}"
        sig = hmac.new(SessionManager._get_secret_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload}::{sig}"

    @staticmethod
    def verify_auth_token(token: str):
        """Verify the cryptographic signature of an auth token. Returns (user_id, refresh_token) or (None, None)."""
        if not token or "::" not in token:
            return None, None
        parts = token.split("::")
        if len(parts) != 3:
            return None, None
        user_id, refresh_token, sig = parts
        payload = f"{user_id}::{refresh_token}"
        expected_sig = hmac.new(SessionManager._get_secret_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if hmac.compare_digest(sig, expected_sig):
            return user_id, refresh_token
        return None, None

    @staticmethod
    def init_session():
        """Initialize or validate session with persistent URL & token support."""
        if "session_initialized" not in st.session_state:
            st.session_state.session_initialized = True

        if "auth_service" not in st.session_state:
            from auth.auth_service import AuthService
            st.session_state.auth_service = AuthService()

        # Restore user session from persistent token in query params if not in session_state
        if "user" not in st.session_state or not st.session_state.user:
            auth_token = st.query_params.get("auth")
            if auth_token:
                user_id, refresh_token = SessionManager.verify_auth_token(auth_token)
                if refresh_token:
                    success, user_data, new_rt = st.session_state.auth_service.restore_session_from_token(refresh_token)
                    if success and user_data:
                        st.session_state.user = user_data
                        st.session_state.authenticated = True
                        if new_rt:
                            st.session_state.refresh_token = new_rt
                            new_token = SessionManager.generate_auth_token(user_data["id"], new_rt)
                            if st.query_params.get("auth") != new_token:
                                st.query_params["auth"] = new_token
                    else:
                        # Stale or invalid token - clear it cleanly
                        try:
                            del st.query_params["auth"]
                        except KeyError:
                            pass

        # Maintain URL state when user is active
        if st.session_state.get("user") and st.session_state.get("refresh_token"):
            current_token = SessionManager.generate_auth_token(
                st.session_state.user["id"], st.session_state.refresh_token
            )
            if st.query_params.get("auth") != current_token:
                st.query_params["auth"] = current_token

            # Restore active session from URL query params
            stored_session_id = st.query_params.get("session_id")
            if stored_session_id:
                curr_id = (
                    st.session_state.get("current_session", {}).get("id")
                    if isinstance(st.session_state.get("current_session"), dict)
                    else None
                )
                if curr_id != stored_session_id:
                    success, session = st.session_state.auth_service.get_session(stored_session_id)
                    if success and session and session.get("user_id") == st.session_state.user["id"]:
                        st.session_state.current_session = session

        # Check session timeout
        if "last_activity" in st.session_state:
            idle_time = datetime.now() - st.session_state.last_activity
            if idle_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                SessionManager.logout()
                st.error("Session expired due to inactivity. Please sign in again.")
                st.rerun()

        st.session_state.last_activity = datetime.now()

    @staticmethod
    def clear_session_state():
        """Clear all session state data."""
        keys_to_keep = ["session_initialized"]
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]

    @staticmethod
    def is_authenticated():
        """Check if user is authenticated."""
        return bool(st.session_state.get("user"))

    @staticmethod
    def create_chat_session():
        """Create a new chat session and persist it in the URL."""
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        success, session = st.session_state.auth_service.create_session(st.session_state.user["id"])
        if success and session:
            st.query_params["session_id"] = session["id"]
        return success, session

    @staticmethod
    def get_user_sessions():
        """Get user's chat sessions."""
        if not SessionManager.is_authenticated():
            return False, []
        return st.session_state.auth_service.get_user_sessions(st.session_state.user["id"])

    @staticmethod
    def delete_session(session_id):
        """Delete a chat session."""
        if not SessionManager.is_authenticated():
            return False, "Not authenticated"
        if st.query_params.get("session_id") == session_id:
            try:
                del st.query_params["session_id"]
            except KeyError:
                pass
        return st.session_state.auth_service.delete_session(session_id)

    @staticmethod
    def logout():
        """Logout user and clear URL & memory session."""
        try:
            st.query_params.clear()
        except Exception:
            pass
        if "auth_service" in st.session_state:
            st.session_state.auth_service.sign_out()
        SessionManager.clear_session_state()

    @staticmethod
    def login(email, password):
        """Handle user login and set persistent session token."""
        if "auth_service" not in st.session_state:
            from auth.auth_service import AuthService
            st.session_state.auth_service = AuthService()

        success, user_data = st.session_state.auth_service.sign_in(email, password)

        if success and user_data and "id" in user_data:
            st.session_state.user = user_data
            st.session_state.authenticated = True
            rt = st.session_state.get("refresh_token", "")
            if rt:
                token = SessionManager.generate_auth_token(user_data["id"], rt)
                st.query_params["auth"] = token

        return success, user_data
