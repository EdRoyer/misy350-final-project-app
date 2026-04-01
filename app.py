import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config("Doctor's Appointments", layout="wide", initial_sidebar_state="expanded")

if "page" not in st.session_state:
    st.session_state["page"] = "Login/Registration"

with st.sidebar:
    if st.button("Login/Registration", key="log/reg_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Login/Registration"
        st.rerun()

    if st.button("Book Appointment", key="Book_Appointment_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Book_Appointment"
        st.rerun()


#CREATE: Book Appointments
