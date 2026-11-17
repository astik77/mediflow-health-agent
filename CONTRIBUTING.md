# Contributing to MediFlow 🩺

Thank you for your interest in contributing to **MediFlow (Evidence-Grounded Longitudinal Health Intelligence)**! This document provides guidelines and instructions for developers, contributors, and collaborators.

---

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Project Subsystems & Guidelines](#project-subsystems--guidelines)
  - [1. LLM Cascade & Prompts](#1-llm-cascade--prompts)
  - [2. Clinical RAG & Vector Engine](#2-clinical-rag--vector-engine)
  - [3. Frontend Design System (Dark Slate & Sky Blue/Teal)](#3-frontend-design-system-dark-slate--sky-blueteal)
  - [4. Supabase Database & Session Security](#4-supabase-database--session-security)
- [Coding Standards](#coding-standards)
- [Continuous Deployment (CI/CD)](#continuous-deployment-cicd)
- [Team & Contact](#team--contact)

---

## Code of Conduct

Please follow respectful, collaborative, and inclusive practices. We are dedicated to providing a harassment-free environment for everyone.

---

## Prerequisites

- **Python**: 3.10 or 3.11
- **Streamlit**: 1.42.0+
- **Database**: A free [Supabase](https://supabase.com/) project
- **LLM Provider**: A free [Groq Cloud](https://console.groq.com/) API key
- **OS**: Windows, macOS, or Linux

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/astik77/mediflow-health-agent.git
   cd mediflow-health-agent
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Local Secrets**:
   Create a `.streamlit/secrets.toml` file in the repository root (do **never** commit this file):
   ```toml
   SUPABASE_URL = "https://your-supabase-project.supabase.co"
   SUPABASE_KEY = "your-supabase-publishable-key"
   GROQ_API_KEY = "gsk_your_groq_api_key"
   ```

5. **Provision Supabase Schema**:
   Run the SQL DDL script located at `public/db/script.sql` in your Supabase SQL Editor to initialize `users`, `chat_sessions`, and `chat_messages` with Row-Level Security (RLS).

6. **Launch local development server**:
   ```bash
   streamlit run src/main.py
   ```

---

## Development Workflow

### Branching Convention
- `main`: Production-ready code (automatically deployed to Streamlit Cloud).
- `feature/<feature-name>`: New capabilities (e.g. `feature/lipid-ratio-chart`).
- `fix/<issue-name>`: Bug fixes (e.g. `fix/auth-token-rotation`).
- `docs/<doc-name>`: Documentation and presentation materials.

### Commit Messages
We follow conventional commits:
- `feat: add automated thyroid spectrum parser`
- `fix: prevent session dropped on F5 reload under RLS`
- `docs: update system architecture diagram`
- `style: optimize clinical teal contrast ratios`

---

## Project Subsystems & Guidelines

### 1. LLM Cascade & Prompts
* Location: `src/agents/model_manager.py`, `src/config/prompts.py`
* All model additions must integrate through the 4-tier fallback cascade (`gpt-oss-120b` ➔ `qwen3.8-27b` ➔ `gpt-oss-20b` ➔ `allam-2-7b`).
* Any changes to prompt templates must maintain the structured diagnostic schema and avoid outputting synthetic watermarks.

### 2. Clinical RAG & Vector Engine
* Location: `src/agents/chat_agent.py`, `src/utils/pdf_extractor.py`
* Extracted document chunks must strictly isolate patient lab numbers and reference ranges to prevent hallucination.
* Vector embeddings must use `sentence-transformers/all-MiniLM-L6-v2` with FAISS-CPU for minimal cloud memory footprint.

### 3. Frontend Design System (Dark Slate & Sky Blue/Teal)
* Location: `.streamlit/config.toml`, `src/main.py`, `src/components/`
* Use native `st.html()` for styled elements rather than multi-line markdown strings to avoid CommonMark raw code block parsing bugs.
* Maintain the dark clinical palette:
  - Background Canvas: `#0B0F19`
  - Cards & Modals: `#1E293B`
  - Primary Accent: `#38BDF8` (Sky Blue)
  - Clinical Glow: `#2DD4BF` (Teal)
  - Text: `#F8FAFC` / `#94A3B8`

### 4. Supabase Database & Session Security
* Location: `src/auth/auth_service.py`, `src/auth/session_manager.py`
* Tables must strictly enforce Row-Level Security (`auth.uid() = id`).
* Session preservation across browser reloads relies on cryptographically signed HMAC-SHA256 tokens in `st.query_params["auth"]` and Supabase refresh token rotation.
* Avoid `.single()` queries when 0-row states are possible; use `.execute()` and check array lengths.

---

## Coding Standards

- **PEP 8 Compliance**: Use 4 spaces for indentation, clean type annotations, and descriptive function naming.
- **Path Resolution**: Never hardcode Windows or Linux file paths. Always use `pathlib.Path` relative to `__file__`.
- **Secrets Protection**: Double check that `.gitignore` prevents tracking `.streamlit/secrets.toml` or any personal credentials.

---

## Continuous Deployment (CI/CD)

The project is connected to **Streamlit Community Cloud**:
- **Live URL**: [https://mediflow-health-management.streamlit.app/](https://mediflow-health-management.streamlit.app/)
- When a commit is merged or pushed to `main`, Streamlit Cloud automatically initiates a zero-downtime hot reload.
- Always verify your changes run without errors locally via `python -m py_compile src/main.py` before pushing to `main`.

---

## Team & Contact

MediFlow is developed by:
- **Astik Saini** – *AI & LLM Pipeline Architect*
- **Meet Goyal** – *Cloud Database & Security Architect*
- **Gaurav Singh** – *Clinical RAG & Vector Systems Engineer*
- **Shubham Kumar** – *Full-Stack & UI/UX Systems Engineer*

If you have questions, feedback, or suggestions, please open an issue on the GitHub repository or contact the project maintainers.
