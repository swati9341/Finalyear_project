import streamlit as st
import streamlit_shadcn_ui as st_shadcn_ui
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Invoice System", layout="wide")


# -----------------------------
# Session State
# -----------------------------
if "token" not in st.session_state:
    st.session_state.token = None

if "user_name" not in st.session_state:
    st.session_state.user_name = "User"   # later you can fetch from backend (/me)


# -----------------------------
# Helpers
# -----------------------------
def auth_headers():
    if not st.session_state.token:
        return {}
    return {"Authorization": f"Bearer {st.session_state.token}"}


def fetch_templates():
    try:
        res = requests.get(f"{BACKEND_URL}/templates/", headers=auth_headers())
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"Error fetching templates: {e}")
        return []


# -----------------------------
# LOGIN/SIGNUP UI
# -----------------------------
def auth_ui():
    st.title("Invoice System - Login/Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.header("Login")
        email = st_shadcn_ui.input("Email", key="login_email")
        password = st_shadcn_ui.input("Password", type="password", key="login_password")

        if st_shadcn_ui.button("Login", key="login_button"):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/auth/login",
                    json={"email": email, "password": password}
                )
                if response.status_code == 200:
                    token = response.json()["access_token"]
                    st.session_state.token = token

                    # ✅ just show user name from email for now
                    st.session_state.user_name = email.split("@")[0].title()

                    st.success("Login successful!")
                    st.rerun()
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
                    response = requests.post(
                        f"{BACKEND_URL}/auth/register",
                        json={
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "password": password
                        }
                    )
                    if response.status_code == 200:
                        st.success("Signup successful! Now login.")
                    else:
                        st.error(f"Signup failed: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")


# -----------------------------
# DASHBOARD UI
# -----------------------------
def dashboard_ui():
    # Top header row
    col1, col2 = st.columns([8, 2])

    with col1:
        st.markdown(f"## Hi, **{st.session_state.user_name}** 👋")
        st.caption("Welcome back! Manage invoices and create new ones easily.")

    with col2:
        if st_shadcn_ui.button("Logout", key="logout_btn"):
            st.session_state.token = None
            st.session_state.user_name = "User"
            st.rerun()

    st.divider()

    tab1, tab2 = st.tabs(["📄 Your Invoices", "➕ Create New Invoice"])

    # -----------------------------
    # TAB 1: Your Invoices
    # -----------------------------
    with tab1:
        st.subheader("Your Invoices")

        # (placeholder for now)
        st.info("Invoices section is ready ✅ (connect backend endpoint GET /invoices next)")

        colA, colB = st.columns([3, 2])
        with colA:
            search = st.text_input("Search invoice (Invoice No / Customer)")
        with colB:
            filter_value = st.selectbox("Filter", ["All", "This Month", "Last 30 Days"])

        demo_invoices = [
            {"Invoice No": "INV-1001", "Customer": "Ravi Kumar", "Date": "2026-01-24", "Total": "₹1200"},
            {"Invoice No": "INV-1002", "Customer": "Aman Singh", "Date": "2026-01-23", "Total": "₹2100"},
        ]

        st.dataframe(demo_invoices, use_container_width=True)

        st.caption("✅ Later: Add View / Download PDF buttons per invoice")

    # -----------------------------
    # TAB 2: Create New Invoice (From Template)
    # -----------------------------
    with tab2:
        st.subheader("Create New Invoice")

        templates = fetch_templates()

        if not templates:
            st.warning("No templates found. Create templates using /templates/create API.")
            st.stop()

        template_map = {t["template_name"]: t for t in templates}
        selected_template_name = st.selectbox("Select Template", list(template_map.keys()))
        selected_template = template_map[selected_template_name]

        st.markdown("### Template Info")
        st.write("**Template Type:**", selected_template["type"])
        st.write("**Mandatory Params:**", selected_template["mandatory_params"])

        st.divider()

        st.markdown("### Enter Invoice Details")

        input_data = {}
        for param in selected_template["mandatory_params"]:
            label = param.replace("_", " ").title()
            input_data[param] = st.text_input(f"{label}", key=f"param_{param}")

        colP1, colP2 = st.columns([2, 2])

        with colP1:
            if st.button("Preview Template HTML"):
                st.code(selected_template["html_content"], language="html")

        with colP2:
            if st.button("Generate Invoice ✅"):
                payload = {
                    "template_id": selected_template["id"],
                    "data": input_data
                }

                st.success("Payload ready ✅")
                st.json(payload)

                st.info("Next: connect this payload to POST /invoices/create-from-template")


# -----------------------------
# Main Entry
# -----------------------------
if not st.session_state.token:
    auth_ui()
else:
    dashboard_ui()
