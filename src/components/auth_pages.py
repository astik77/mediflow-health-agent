import streamlit as st
from auth.session_manager import SessionManager
from config.app_config import APP_ICON, APP_NAME, APP_TAGLINE, get_logo_base64
from utils.validators import validate_signup_fields
import time


def show_login_page():
    if "form_type" not in st.session_state:
        st.session_state["form_type"] = "login"

    current_form = st.session_state["form_type"]

    # Subtle clinical ambient glow & micro-grid background styling
    st.html(
        """
        <style>
            .stApp {
                background-color: #0B0F19 !important;
                background-image: 
                    radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.09) 0%, transparent 65%),
                    radial-gradient(circle at 85% 90%, rgba(45, 212, 191, 0.04) 0%, transparent 50%),
                    radial-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 1px) !important;
                background-size: 100% 100%, 100% 100%, 28px 28px !important;
                background-attachment: fixed !important;
            }

            /* Frosted glass authentication card */
            div[data-testid="stForm"] {
                background: rgba(30, 41, 59, 0.7) !important;
                backdrop-filter: blur(14px) !important;
                -webkit-backdrop-filter: blur(14px) !important;
                border: 1px solid rgba(51, 65, 85, 0.9) !important;
                border-radius: 14px !important;
                padding: 1.75rem 1.5rem !important;
                box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(56, 189, 248, 0.06) !important;
            }

            /* Remove any border/box around logo images */
            img {
                border: none !important;
                outline: none !important;
                box-shadow: none !important;
            }

            iframe[data-testid="stHtmlFrameIframe"],
            div[data-testid="stHtml"] iframe {
                border: none !important;
                outline: none !important;
            }
        </style>
        """
    )

    # Check if localStorage has persisted session token and URL lacks ?auth=
    st.html("""
    <script>
        try {
            const token = localStorage.getItem('mediflow_auth_token');
            if (token && !window.location.search.includes('auth=')) {
                const url = new URL(window.location.href);
                url.searchParams.set('auth', token);
                window.location.replace(url.toString());
            }
        } catch(e) {}
    </script>
    """)

    logo_src = get_logo_base64()
    st.html(
        f"""
        <div style="text-align: center; padding: 2rem 1rem 1.25rem 1rem; max-width: 480px; margin: 0 auto;">
            <div style="max-width: 280px; margin: 0 auto 0.75rem auto; background: transparent; border: none; outline: none;">
                <img src="{logo_src}" style="width: 100%; height: auto; display: block; border: none; outline: none; box-shadow: none; mix-blend-mode: screen; filter: drop-shadow(0 0 28px rgba(56, 189, 248, 0.35));" alt="MediFlow">
            </div>
            <p style="color: #38BDF8; font-size: 0.92rem; font-weight: 600; margin: 0 0 0.5rem 0;">
                {APP_TAGLINE}
            </p>
            <p style="color: #94A3B8; font-size: 0.88rem; margin: 0;">
                {"Welcome back — please enter your credentials to continue." if current_form == 'login' else "Register to start analyzing laboratory panels."}
            </p>
        </div>
        """
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if current_form == "login":
            show_login_form()
        else:
            show_signup_form()

        st.html("<div style='height: 12px;'></div>")
        toggle_text = (
            "Don't have an account? Sign up"
            if current_form == "login"
            else "Already have an account? Log in"
        )
        if st.button(toggle_text, use_container_width=True, type="secondary"):
            st.session_state["form_type"] = "signup" if current_form == "login" else "login"
            st.rerun()


def show_login_form():
    with st.form("login_form"):
        email = st.text_input("Email Address", placeholder="doctor@hospital.org", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

        submitted = st.form_submit_button("Sign In to MediFlow", use_container_width=True, type="primary")
        if submitted:
            if email and password:
                with st.spinner("Authenticating..."):
                    success, result = SessionManager.login(email.strip(), password)
                    if success:
                        st.success("Authentication successful! Loading workspace...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Sign in failed: {result}")
            else:
                st.error("Please enter both email address and password.")


def show_signup_form():
    with st.form("signup_form"):
        new_name = st.text_input("Full Name", placeholder="Dr. Alex Rivera", key="signup_name")
        new_email = st.text_input("Email Address", placeholder="alex@clinic.org", key="signup_email")
        new_password = st.text_input("Password", type="password", placeholder="At least 8 characters", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="signup_password2")

        st.html(
            """
            <div style="font-size: 0.78rem; color: #94A3B8; background: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 8px 12px; margin: 8px 0;">
                <span style="font-weight: 600; color: #F8FAFC;">Security requirements:</span> 8+ characters · 1 uppercase letter · 1 lowercase letter · 1 number
            </div>
            """
        )

        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        if submitted:
            validation_result = validate_signup_fields(new_name, new_email, new_password, confirm_password)

            if not validation_result[0]:
                st.error(validation_result[1])
                return

            with st.spinner("Provisioning clinical user account..."):
                success, response = st.session_state.auth_service.sign_up(
                    new_email.strip(), new_password, new_name.strip()
                )

                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = response
                    rt = st.session_state.get("refresh_token", "")
                    token = SessionManager.generate_auth_token(response["id"], rt)
                    st.query_params["auth"] = token
                    st.success("Account created successfully! Redirecting...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"Registration failed: {response}")
