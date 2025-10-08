import os
import streamlit as st
from dotenv import load_dotenv

# Try to load .env for local development
load_dotenv()

def get_secret(key: str):
    # Use Streamlit secrets if running in the cloud
    if hasattr(st, "secrets") and key in st.secrets:
        return st.secrets[key]
    # Otherwise, fall back to local .env
    return os.getenv(key)