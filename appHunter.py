# Login
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config(page_title="Login/Registration", layout="centered")


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"





users = [
        {
        "patient": "Max",
        "email": "Max@patient.com",
        "full_name": "Max Smith",
        "password": "123ssag@43AE",
        "role": "patient",
        "registered_at": "..."
    }
    {"doctor":"Roger"
     "email": "doctor@"
]

json_path = Path("users.json")
if json_path.exists():
    with open(json_path, "r") as f:
        users = json.load(f)
if st.session_state["role"] == "instructor":
    st.markdown("Welcome! This is the instructor Dashboard")


elif st.session_state['role'] == "Admin":
    st.markdown("Welcome! This is the Admin Dashboard")

    if st.button("Log out", type="primary", use_container_width= True):
        with st.spinner("loggin out..."):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["page"]= "login"
            time.sleep(4)
            st.rerun()


else:

    # --- LOGIN --
    st.subheader("Log In")
    with st.container(border=True):
        email_input = st.text_input("Email", key= "email_login")
        password_input = st.text_input("Password", type="password",key="password_login")
        
        if st.button("Log In", type="primary", use_container_width=True):
            with st.spinner("Logging in..."):
                time.sleep(2) # Fake backend delay
                
                # Find user
                found_user = None
                for user in users:
                    if user["email"].strip().lower() == email_input.strip().lower() and user["password"] == password_input:
                        found_user = user
                        break
                
                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user["role"]


                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    # --- REGISTRATION ---
    st.subheader("New Instructor Account")
    with st.container(border=True):
        new_email = st.text_input("Email", key= "email_register")
        new_password = st.text_input("Password", type="password", key= "password_edit")
        
        if st.button("Create Account", key = "register_btn"):
            with st.spinner("Creating account..."):
                time.sleep(2) # Fake backend delay
                # ... (Assume validation logic here) ...
                users.append({
                    "id": str(uuid.uuid4()),
                    "email": new_email,
                    "password": new_password,
                    "role": "Instructor"
                })
                with open(json_path, "w") as f:
                    json.dump(users,f)
                st.success("Account created!")
                st.rerun()

    st.write("---")
    st.dataframe(users)

with st.sidebar:
    st.markdown("Course Manager Sidebar")
    if  st.session_state["logged_in"] == True:
        user = st.session_state["user"]
        st.markdown(f"Loged User Email: {user['email']}")
