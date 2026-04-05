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

st.set_page_config(page_title="Login/Registration", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

json_path = Path("users.json")

default_users = [
    {
        "email": "max@patient.com",
        "full_name": "Max Smith",
        "password": "123ssag@43AE",
        "role": "Patient"
    },
    {
        "email": "doctor@hospital.com",
        "full_name": "Roger Craig",
        "password": "2468def@56SR",
        "role": "Doctor"
    }
]

if not json_path.exists():
    with open(json_path, "w") as f:
        json.dump(default_users, f, indent=4)

with open(json_path, "r") as f:
    users = json.load(f)

def save_users():
    with open(json_path, "w") as f:
        json.dump(users, f, indent=4)


def login_user(user):
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.role = user["role"]


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None


def find_user(email, password):
    for user in users:
        if (
            user["email"].strip().lower() == email.strip().lower()
            and user["password"] == password
        ):
            return user
    return None


if st.session_state.logged_in:

    #Establishes Dashboard as default page after logging in
    if "page" not in st.session_state:
        st.session_state["page"] = "Dashboard"


else:
    st.title("Login / Registration")

    st.subheader("Log In")
    with st.container(border=True):
        email_input = st.text_input("Email", key="email_login")
        password_input = st.text_input("Password", type="password", key="password_login")

        if st.button("Log In", type="primary", use_container_width=True):
            with st.spinner("Logging in..."):
                time.sleep(1)

                found_user = find_user(email_input, password_input)

                if found_user:
                    login_user(found_user)
                    st.success(f"Welcome back, {found_user['full_name']}!")
                    st.session_state.logged_in = True
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    # ---------- REGISTRATION ----------
    st.subheader("New Patient Account")
    with st.container(border=True):
        new_email = st.text_input("New Email", key="email_register")
        new_password = st.text_input("New Password", type="password", key="password_register")
        new_full_name = st.text_input("Full Name", key="full_name_register")

        if st.button("Create Account", key="register_btn", use_container_width=True):
            with st.spinner("Creating account..."):
                time.sleep(1)

                email_exists = any(
                    user["email"].strip().lower() == new_email.strip().lower()
                    for user in users
                )

                if not new_email or not new_password or not new_full_name:
                    st.error("Please fill in all fields.")
                elif email_exists:
                    st.error("An account with that email already exists.")
                else:
                    new_user = {
                        "email": new_email,
                        "full_name": new_full_name,
                        "password": new_password,
                        "role": "Patient"
                    }
                    users.append(new_user)
                    save_users()
                    st.success("Account created successfully!")
                    st.rerun()

    st.write("---")
    #st.dataframe(users)


# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### Account Manager Sidebar")
    if st.session_state.logged_in:
        st.markdown(f"**Logged in user:** {st.session_state.user['email']}")
        st.markdown(f"**Role:** {st.session_state.role}")


        if st.button("Dashboard", key="Appointment_Dashboard_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "Dashboard"
            st.rerun()
        
        if st.button("Book Appointment", key="Book_Appointment_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "Book_Appointment"
            st.rerun()

        if st.button("Reschedule Appointments", key="Reschedule_Appointment_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "Reschedule_Appointments"
            st.rerun()

        if st.button("Delete Appointments", key="Delete_Appointment_btn", type="primary", use_container_width=True):
            st.session_state["page"] = "Delete_Appointments"
            st.rerun()

    else:
        st.markdown("No user is currently logged in.")


#Doctor Side
if st.session_state.role == "Doctor":
    
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

        patient_email = st.text_input("Enter patient's email")

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
                        "symptoms": symptoms,
                        "email": patient_email
                    }
                )

                with json_path_appointments.open("w",encoding="utf-8") as f:
                        json.dump(appointments,f, indent=4)
                
                st.success("Appointment Scheduled!")

                time.sleep(2)
                st.rerun()
    
    #READ: Appointment Dashboard
    if st.session_state['page'] == "Dashboard":
        st.title("Doctor Dashboard")
        st.markdown("Welcome! This is the Doctor Dashboard.")
        
        st.divider()
        
        st.markdown("## Appointments")

        col1, col2 = st.columns([4,2])
        with col1:
            event = st.dataframe(
                appointments,
                on_select="rerun",
                selection_mode="single-row"
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                
                selected_appointment = appointments[selected_index]
                
                st.markdown("### Appointment for:") 
                st.markdown(f" **Patient:** {selected_appointment["patient_first_name"]} {selected_appointment["patient_last_name"]}")
                st.markdown(f" **Date:** {selected_appointment["appointment_date"]}")
                st.markdown(f" **Time:** {selected_appointment["appointment_time"]}")

        with col2:
            with st.container(border=True):
                st.metric("Total Appointments",len(appointments))

        if st.button("Log Out", type="primary", use_container_width=True):
            with st.spinner("Logging out..."):
                time.sleep(1)
                logout_user()
                st.rerun()

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

    #DELETE: Cancel Appointments
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


#Patient Side
if st.session_state.role == "Patient":
    my_email = ""
    for user in users:
        if user == st.session_state.user:
            my_email = user["email"]
            break
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
                        "symptoms": symptoms,
                        "email": my_email
                    }
                )

                with json_path_appointments.open("w",encoding="utf-8") as f:
                        json.dump(appointments,f, indent=4)
                
                st.success("Appointment Scheduled!")

                time.sleep(2)
                st.rerun()
    
    #READ: Appointment Dashboard
    if st.session_state['page'] == "Dashboard":
        st.title("Patient Dashboard")
        st.markdown("Welcome! This is the Patient Appointment Dashboard.")
            
        st.divider()
        
        st.markdown("## My Appointments")

        my_appointments=[]
        for appointment in appointments:
            if appointment["email"]==my_email:
                my_appointments.append(appointment)

        col1, col2 = st.columns([4,2])
        with col1:
            event = st.dataframe(
                my_appointments,
                on_select="rerun",
                selection_mode="single-row"
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                
                selected_appointment = appointments[selected_index]
                
                st.markdown("### Appointment for:") 
                st.markdown(f" **Patient:** {selected_appointment["patient_first_name"]} {selected_appointment["patient_last_name"]}")
                st.markdown(f" **Date:** {selected_appointment["appointment_date"]}")
                st.markdown(f" **Time:** {selected_appointment["appointment_time"]}")

        with col2:
            with st.container(border=True):
                st.metric("Total Appointments",len(appointments))

            
            
        if st.button("Log Out", type="primary", use_container_width=True):
            with st.spinner("Logging out..."):
                time.sleep(1)
                logout_user()
                st.rerun()            

    #UPDATE: Reschedule Appointments
    if st.session_state['page'] == "Reschedule_Appointments":
        st.header("Reschedule Appointments")

        reschedulable_appointments = []
        for appointment in appointments:
            if appointment["email"] == my_email:
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
    
    #DELETE: Cancel Appointments
    if st.session_state['page'] == "Delete_Appointments":
        st.header("Delete Appointments")

        cancellable_appointments = []
        for appointment in appointments:
            if appointment["email"] == my_email:
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
