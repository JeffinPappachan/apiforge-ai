from __future__ import annotations

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="APIForge AI",
    page_icon=":hammer_and_wrench:",
    layout="wide"
)

st.title("APIForge AI")
st.caption("Smart DevTool for API Integration")

# ----------------------------
# SESSION STATE
# ----------------------------
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "sdk_code" not in st.session_state:
    st.session_state.sdk_code = ""


# ----------------------------
# BACKEND CALL
# ----------------------------
def call_backend(path: str, payload: dict) -> dict:
    response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


# ----------------------------
# SIDEBAR
# ----------------------------
with st.sidebar:
    st.subheader("Backend")
    st.code(BACKEND_URL)
    st.write("Make sure FastAPI is running before using the UI.")


# ----------------------------
# INPUT
# ----------------------------
url = st.text_input(
    "API documentation URL",
    placeholder="https://docs.example.com/api"
)


# ----------------------------
# BUTTONS
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    analyze_clicked = st.button("Analyze API", use_container_width=True)

with col2:
    generate_clicked = st.button("Generate SDK", use_container_width=True)


# ----------------------------
# ANALYZE API
# ----------------------------
if analyze_clicked:
    if not url.strip():
        st.error("Enter an API documentation URL first.")
    else:
        with st.spinner("Analyzing API documentation..."):
            try:
                st.session_state.analysis = call_backend("/process", {"url": url.strip()})
                st.session_state.sdk_code = ""
                st.success("API analyzed successfully ✅")

            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", "API analysis failed.")
                st.error(detail)

            except Exception as exc:
                st.error(f"Could not reach the backend: {exc}")


# ----------------------------
# DISPLAY ANALYSIS
# ----------------------------
analysis = st.session_state.analysis

if analysis:
    api = analysis["api"]

    st.subheader("Detected API")

    st.markdown(f"**Base URL:** `{api.get('base_url') or 'Not detected'}`")
    st.markdown(f"**Authentication:** `{api.get('auth', 'None')}`")

    with st.expander("API Summary"):
        st.write(analysis.get("summary", ""))

    st.subheader("Extracted Endpoints")

    for endpoint in api.get("endpoints", []):
        with st.container(border=True):
            st.markdown(f"### `{endpoint['method']} {endpoint['path']}`")

            if endpoint.get("description"):
                st.write(endpoint["description"])

            params = endpoint.get("params", [])

            if params:
                formatted_params = [
                    p["name"] if isinstance(p, dict) and "name" in p else str(p)
                    for p in params
                ]
                st.write("Parameters:", ", ".join(formatted_params))
            else:
                st.write("Parameters: None detected")


# ----------------------------
# GENERATE SDK (FIXED LOGIC)
# ----------------------------
if generate_clicked:
    if not analysis:
        st.warning("Please analyze the API first ⚠️")
    else:
        with st.spinner("Generating Python SDK..."):
            try:
                result = call_backend("/generate", analysis["api"])
                st.session_state.sdk_code = result["sdk_code"]
                st.success("SDK generated successfully 🚀")

            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", "SDK generation failed.")
                st.error(detail)

            except Exception as exc:
                st.error(f"Could not reach the backend: {exc}")


# ----------------------------
# DISPLAY SDK
# ----------------------------
if st.session_state.sdk_code:
    st.subheader("Python SDK")

    st.code(st.session_state.sdk_code, language="python")

    st.download_button(
        label="Download sdk.py",
        data=st.session_state.sdk_code,
        file_name="sdk.py",
        mime="text/x-python",
        use_container_width=True,
    )

    st.info("Tip: You can copy and use this SDK directly in your project.")