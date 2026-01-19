import streamlit as st
import streamlit_shadcn_ui as st_shadcn_ui
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.title("Invoice System - Login/Signup")

# Backend URL - loaded from .env file
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state for token
if "token" not in st.session_state:
    st.session_state.token = None

tab1, tab2 = st.tabs(["Login", "Signup"])

with tab1:
    st.header("Login")
    email = st_shadcn_ui.input("Email", key="login_email")
    password = st_shadcn_ui.input("Password", type="password", key="login_password")
    if st_shadcn_ui.button("Login", key="login_button"):
        try:
            response = requests.post(f"{BACKEND_URL}/auth/login", json={"email": email, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token
                st.success("Login successful!")
                st.rerun()  # Refresh to show logged-in state
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.header("Signup")
    name = st_shadcn_ui.input("Name", key="signup_name")
    email = st_shadcn_ui.input("Email", key="signup_email")
    phone = st_shadcn_ui.input("Phone", key="signup_phone")
    password = st_shadcn_ui.input("Password", type="password", key="signup_password")
    confirm_password = st_shadcn_ui.input("Confirm Password", type="password", key="signup_confirm")
    if st_shadcn_ui.button("Signup", key="signup_button"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        else:
            try:
                response = requests.post(f"{BACKEND_URL}/auth/register", json={"name": name, "email": email, "phone": phone, "password": password})
                if response.status_code == 200:
                    st.success("Signup successful!")
                else:
                    st.error("Signup failed")
            except Exception as e:
                st.error(f"Error: {e}")

# If logged in, show a simple message or additional features
if st.session_state.token:
    st.header("Welcome! You are logged in.")
    st.write("Token stored securely in session state.")
    # Example: Add invoice creation here later
    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()