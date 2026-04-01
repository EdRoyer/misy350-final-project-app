import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config("Doctor's Appointments", page_icon=":gem:" , layout="wide", initial_sidebar_state="expanded")

appointments = []

json_path_appointments = Path("appointments.json")

if json_path_appointments.exists():
    with open(json_path_appointments, "r") as f:
        requests = json.load(f)

#Establishes Login/Registration as default page
if "page" not in st.session_state:
    st.session_state["page"] = "Login/Registration"

#Sets up sidebar framework for pages
with st.sidebar:
    if st.button("Login/Registration", key="log/reg_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Login/Registration"
        st.rerun()

    if st.button("Book Appointment", key="Book_Appointment_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Book_Appointment"
        st.rerun()

    if st.button("Appointment Dashboard", key="Appointment_Dashboard_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Appointment_Dashboard"
        st.rerun()

    if st.button("Reschedule Appointments", key="Reschedule_Appointment_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Reschedule_Appointments"
        st.rerun()

    if st.button("Delete Appointments", key="Delete_Appointment_btn", type="primary", use_container_width=True):
        st.session_state["page"] = "Delete_Appointments"
        st.rerun()


st.markdown("# Patient Appointment Tracker")

#Login/Registration:
#I'm thinking u can represent this as two tabs within the page, with login as the default, but it's up to you.



#CREATE: Book Appointments
if st.session_state['page'] == "Book_Appointment":
    st.header("Book Appointment")

    appointment_date = st.date_input("Select Appointment Date")
    
    available_times = []

    appointment_time = st.selectbox("Select Appointment Time", ["select time", available_times])
   
    symptoms = st.text_input("Enter Symptoms", key="symptoms")

    book_now_btn = st.button("Book Now", key="book_now_btn", use_container_width=True)

    #if book_now_btn:
        





#READ: Appointment Dashboard


#UPDATE: Reschedule Appointments
if st.session_state['page'] == "Reschedule_Appointments":
    st.header("Reschedule Appointments")


#DELETE: Delete Appoinments
if st.session_state['page'] == "Delete_Appointments":
    st.header("Delete Appointments")