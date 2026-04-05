import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import time

st.set_page_config("Doctor's Appointments", page_icon=":gem:" , layout="wide", initial_sidebar_state="expanded")


json_path_appointments = Path("appointments.json")

if json_path_appointments.exists():
    with open(json_path_appointments, "r") as f:
        appointments = json.load(f)
else:
    appointments = []

#Sets up date ranges for use in pages
start = datetime.strptime("09:00", "%H:%M")
end = datetime.strptime("17:00", "%H:%M")
all_times = []
current = start
while current <= end:
    all_times.append(current.strftime("%H:%M"))
    current += timedelta(minutes=30)


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
#ROLES = {"Patient": "Max"


#CREATE: Book Appointments
if st.session_state['page'] == "Book_Appointment":
    st.header("Book Appointment")
    patient_first_name = st.text_input("First Name of Patient",key="first_name")
    patient_last_name = st.text_input("Last Name of Patient",key="last_name")

    selected_date = st.date_input("Select Appointment Date",key="selected_date")
    


    unavailable_times = []
    for appointment in appointments:
        if appointment["appointment_date"] == selected_date.isoformat():
            unavailable_times.append(appointment["appointment_time"])
    
    available_times = []
    for appointment in all_times:
        if appointment not in unavailable_times:
            available_times.append(appointment)


    if not available_times:
        st.warning("No available times for this date")
    else:
        selected_time = st.selectbox("Select a time", available_times, key="selected_time")

    symptoms = st.text_input("Enter Symptoms", key="symptoms")


    book_now_btn = st.button("Book Now", key="book_now_btn", use_container_width=True)

    if book_now_btn:
        with st.spinner("Booking appointment..."):
            time.sleep(2)
            
            new_appointment_id = str(uuid.uuid4())
            
            appointments.append(
                {
                    "appointment_id": new_appointment_id,
                    "patient_first_name": patient_first_name,
                    "patient_last_name": patient_last_name,
                    "appointment_date": selected_date.isoformat(),
                    "appointment_time": selected_time,
                    "symptoms": symptoms
                }
            )

            with json_path_appointments.open("w",encoding="utf-8") as f:
                    json.dump(appointments,f, indent=4)
            
            st.success("Appointment Scheduled!")

            time.sleep(2)
            st.rerun()


#READ: Appointment Dashboard


#UPDATE: Reschedule Appointments
if st.session_state['page'] == "Reschedule_Appointments":
    st.header("Reschedule Appointments")

    

    reschedulable_appointments = []
    for appointment in appointments:
        reschedulable_appointments.append(appointment["appointment_id"])

    selected_rescheduling = st.selectbox("Select Existing Appointment",reschedulable_appointments,key="selected_rescheduling")
    
    new_date = st.date_input("Choose new date",key="new_date")
    
    unavailable_times = []
    for appointment in appointments:
        if appointment["appointment_date"] == new_date.isoformat():
            unavailable_times.append(appointment["appointment_time"])
    
    available_times = []
    for appointment in all_times:
        if appointment not in unavailable_times:
            available_times.append(appointment)


    new_time = st.selectbox("Choose new time",available_times,key="new_time")

    reschedule_appointment_btn = st.button("Reschedule Appointment",key="reschedule_appointment_btn")

    if reschedule_appointment_btn:
        with st.spinner("Rescheduling appointment..."):
            time.sleep(2)

            for appointment in appointments:
                if appointment["appointment_id"] == selected_rescheduling:
                    appointment["appointment_date"] = new_date.isoformat()
                    appointment["appointment_time"] = new_time
                    break
                
            st.success("Appointment Rescheduled!")
                
            with json_path_appointments.open("w",encoding="utf-8") as f:
                json.dump(appointments,f, indent=4)
                
            time.sleep(2)
            st.rerun()
                



#DELETE: Delete Appoinments
if st.session_state['page'] == "Delete_Appointments":
    st.header("Delete Appointments")

    cancellable_appointments = []
    for appointment in appointments:
        cancellable_appointments.append(appointment["appointment_id"])

    selected_cancellation = st.selectbox("Select Appointment to Cancel",cancellable_appointments)

    cancel_appointment_btn = st.button("Cancel Appointment",key="cancel_appointment_btn")

    if cancel_appointment_btn:
        with st.spinner("Cancelling appointment..."):
            time.sleep(2)
            for appointment in appointments:
                if appointment["appointment_id"] == selected_cancellation:
                    appointments.remove(appointment)
                    break
            st.success("Appointment Canceled!")
            with json_path_appointments.open("w",encoding="utf-8") as f:
                json.dump(appointments,f, indent=4)
            time.sleep(2)
            st.rerun()

        