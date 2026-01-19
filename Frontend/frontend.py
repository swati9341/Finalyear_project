import streamlit as st
import streamlit_shadcn_ui as st_shadcn_ui
import requests

st.title("Invoice System - Login/Signup")

# Backend URL - adjust if needed
BACKEND_URL = "http://localhost:8000"

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
                st.success("Login successful!")
                st.write(f"Access Token: {token}")  # In a real app, store securely
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.header("Signup")
    name = st_shadcn_ui.input("Name", key="signup_name")  # Note: Backend doesn't use name, but keeping for UI
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