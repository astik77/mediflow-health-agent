import streamlit as st
from config.prompts import SPECIALIST_PROMPTS
from utils.pdf_extractor import extract_text_from_pdf
from config.sample_data import SAMPLE_REPORT
from config.app_config import MAX_UPLOAD_SIZE_MB, PRIMARY_COLOR, SLATE_BORDER


def html(content: str):
    """Safely render HTML without markdown parser converting tags to raw code blocks."""
    st.html(content)


def _detect_biomarkers(text):
    """Detect presence of key biomarker panels for instant feedback."""
    text_lower = text.lower()
    detected = []
    if any(k in text_lower for k in ["hemoglobin", "wbc", "rbc", "platelet", "hematocrit", "cbc"]):
        detected.append("Complete Blood Count (CBC)")
    if any(k in text_lower for k in ["glucose", "creatinine", "bun", "sodium", "potassium"]):
        detected.append("Metabolic Panel")
    if any(k in text_lower for k in ["cholesterol", "hdl", "ldl", "triglycerides", "lipid"]):
        detected.append("Lipid Profile")
    if any(k in text_lower for k in ["alt", "ast", "bilirubin", "alkaline phosphatase"]):
        detected.append("Hepatic Function")
    if any(k in text_lower for k in ["tsh", "t4", "thyroid"]):
        detected.append("Thyroid Panel")
    return detected


def show_analysis_form():
    """Renders the clinical report ingestion and patient intake form."""
    if "current_session" in st.session_state and "report_source" not in st.session_state:
        st.session_state.report_source = "Upload PDF"

    html("""
    <div style="margin-bottom: 1.25rem;">
        <div style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">Lab Report Intake & Diagnostics</div>
        <div style="font-size: 0.88rem; color: #94A3B8; margin-top: 2px;">Provide a digital laboratory panel to generate an evidence-grounded clinical risk stratification.</div>
    </div>
    """)

    report_source = st.radio(
        "Choose Report Source",
        ["📄 Upload Blood Report (PDF)", "🧪 Use Standard Reference Panel"],
        index=0 if st.session_state.get("report_source") == "Upload PDF" else 1,
        horizontal=True,
        key="report_source_radio",
        label_visibility="collapsed",
    )

    is_upload = "Upload Blood Report" in report_source
    st.session_state.report_source = "Upload PDF" if is_upload else "Use Sample PDF"

    pdf_contents = get_report_contents(st.session_state.report_source)

    if pdf_contents:
        render_patient_form(pdf_contents)


def get_report_contents(report_source):
    if report_source == "Upload PDF":
        uploaded_file = st.file_uploader(
            f"Upload Blood Report PDF (Max {MAX_UPLOAD_SIZE_MB}MB)",
            type=["pdf"],
            help=f"Accepts digital medical laboratory reports up to {MAX_UPLOAD_SIZE_MB}MB.",
            label_visibility="collapsed",
        )
        if uploaded_file:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > MAX_UPLOAD_SIZE_MB:
                st.error(f"File size ({file_size_mb:.1f}MB) exceeds the {MAX_UPLOAD_SIZE_MB}MB limit.")
                return None

            if uploaded_file.type != "application/pdf":
                st.error("Invalid format. Please upload a PDF medical laboratory report.")
                return None

            with st.spinner("Extracting laboratory text..."):
                pdf_contents = extract_text_from_pdf(uploaded_file)

            if isinstance(pdf_contents, str) and (
                pdf_contents.startswith(("File size exceeds", "Invalid file type", "Error validating"))
                or pdf_contents.startswith("The uploaded file")
                or "error" in pdf_contents.lower()
            ):
                st.error(pdf_contents)
                return None

            _render_biomarker_feedback(pdf_contents, is_sample=False)
            return pdf_contents
    else:
        _render_biomarker_feedback(SAMPLE_REPORT, is_sample=True)
        return SAMPLE_REPORT
    return None


def _render_biomarker_feedback(content, is_sample=False):
    """Shows detected biomarker chips and preview expander."""
    panels = _detect_biomarkers(content)
    badge_html = "".join(
        [
            f"""<span style="background: rgba(56, 189, 248, 0.12); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.35); padding: 3px 10px; border-radius: 9999px; font-size: 0.78rem; font-weight: 600; display: inline-flex; align-items: center; gap: 4px;">✓ {p}</span>"""
            for p in panels
        ]
    )

    sample_notice = (
        """<div style="font-size: 0.82rem; color: #7DD3FC; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.25); padding: 6px 12px; border-radius: 6px; margin-bottom: 8px;">Standard 5-panel reference panel loaded (CBC, Metabolic, Lipid, Hepatic, Thyroid).</div>"""
        if is_sample
        else ""
    )

    empty_tag = '<span style="color: #94A3B8; font-size: 0.8rem;">Clinical text extracted successfully</span>'
    html(f"""
    <div style="background: #1E293B; border: 1px solid {SLATE_BORDER}; border-radius: 8px; padding: 0.85rem 1rem; margin: 0.85rem 0;">
        {sample_notice}
        <div style="font-size: 0.82rem; font-weight: 600; color: #94A3B8; margin-bottom: 6px;">Detected Biomarker Spectra:</div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">{badge_html if badge_html else empty_tag}</div>
    </div>
    """)

    with st.expander("📄 View Extracted Text Preview"):
        st.text_area("Extracted Content", content, height=180, disabled=True, label_visibility="collapsed")


def render_patient_form(pdf_contents):
    html("""
    <div style="font-size: 0.92rem; font-weight: 700; color: #F8FAFC; margin-top: 0.75rem; margin-bottom: 0.25rem;">Patient Profile</div>
    """)

    with st.form("clinical_intake_form"):
        patient_name = st.text_input(
            "Patient Full Name",
            placeholder="e.g., Alex Mercer",
        )
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1)
        with col2:
            gender = st.selectbox("Biological Sex", ["Male", "Female", "Other"])

        submitted = st.form_submit_button(
            "⚡ Synthesize Clinical Health Intelligence",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            handle_form_submission(patient_name, age, gender, pdf_contents)


def handle_form_submission(patient_name, age, gender, pdf_contents):
    if not patient_name or not patient_name.strip():
        st.error("Please enter the patient's name.")
        return

    if age is None or age < 0:
        st.error("Please enter a valid age.")
        return

    from services.ai_service import generate_analysis

    can_analyze, error_msg = generate_analysis(None, None, check_only=True)
    if not can_analyze:
        st.error(error_msg)
        st.stop()
        return

    with st.spinner("Analyzing report across multi-model cascade..."):
        st.session_state.current_report_text = pdf_contents

        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"],
            f"Analyzing report for patient: **{patient_name.strip()}** ({gender}, {age} yrs)",
        )

        result = generate_analysis(
            {
                "patient_name": patient_name.strip(),
                "age": age,
                "gender": gender,
                "report": pdf_contents,
            },
            SPECIALIST_PROMPTS["comprehensive_analyst"],
        )

        if result["success"]:
            report_metadata = f"__REPORT_TEXT__\n{pdf_contents}\n__END_REPORT_TEXT__"
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], report_metadata, role="system"
            )

            content = result["content"]

            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], content, role="assistant"
            )
            st.rerun()
        else:
            st.error(result.get("error", "Analysis failed."))
            st.stop()
