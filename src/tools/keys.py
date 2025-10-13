import os
from dotenv import load_dotenv

# Load .env file if present (useful for local testing)
load_dotenv()

def get_secret(key: str):
    """
    Retrieve secrets safely from:
    1. GitHub Actions environment variables
    2. .env file (local development)
    3. Streamlit secrets (if available)
    """
    # 1️⃣ Try environment variable (used by GitHub Actions)
    if os.getenv(key):
        return os.getenv(key)

    # 2️⃣ Try Streamlit secrets, if running in Streamlit context
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass  # Streamlit not available or no secrets.toml

    # 3️⃣ If nothing found, raise error
    raise ValueError(f"❌ Secret '{key}' not found in environment or Streamlit secrets.")
