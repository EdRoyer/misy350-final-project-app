import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
import uuid
import time

st.set_page_config(
    page_title="Appointment Manager",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

users_path = Path("users.json")
appointments_path = Path("appointments.json")

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

#Sets up sidebar framework for pages
def safe_load_json(path, default):
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except json.JSONDecodeError:
        return default


def save_users():
    with open(users_path, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


def save_appointments():
    with open(appointments_path, "w", encoding="utf-8") as f:
        json.dump(appointments, f, indent=4)


def login_user(user):
    st.session_state.logged_in = True
    st.session_state.user = user
    st.session_state.role = user["role"]
    st.session_state.page = "Dashboard"


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.page = "Dashboard"


def find_user(email, password):
    for user in users:
        if (
            user["email"].strip().lower() == email.strip().lower()
            and user["password"] == password
        ):
            return user
    return None


def get_available_times(selected_date, exclude_appointment_id=None):
    unavailable_times = []

    for appointment in appointments:
        if appointment["appointment_date"] == selected_date.isoformat():
            if exclude_appointment_id and appointment["appointment_id"] == exclude_appointment_id:
                continue
            unavailable_times.append(appointment["appointment_time"])

    return [time_slot for time_slot in all_times if time_slot not in unavailable_times]


def format_time_12hr(time_24):
    return datetime.strptime(time_24, "%H:%M").strftime("%I:%M %p")


users = safe_load_json(users_path, default_users)
appointments = safe_load_json(appointments_path, [])

#CREATE: Book Appointments
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

#Establishes Login/Registration as default page
start = datetime.strptime("09:00", "%H:%M")
end = datetime.strptime("17:00", "%H:%M")
all_times = []

current = start
while current <= end:
    all_times.append(current.strftime("%H:%M"))
    current += timedelta(minutes=30)

# ---------------- LOGIN / REGISTRATION ----------------
if not st.session_state.logged_in:
    st.title("Login / Registration")

    col1, col2 = st.columns(2)

    with col1:
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
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

    with col2:
        st.subheader("Register")
        with st.container(border=True):
            new_email = st.text_input("New Email", key="email_register")
            new_password = st.text_input("New Password", type="password", key="password_register")
            new_full_name = st.text_input("Full Name", key="full_name_register")
            new_role = st.selectbox("Register As", ["Patient", "Doctor"], key="role_register")

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
                            "role": new_role
                        }
                        users.append(new_user)
                        save_users()
                        st.success("Account created successfully!")
                        time.sleep(1)
                        st.rerun()

    st.stop()
    
#Sets up sidebar framework for pages
with st.sidebar:
    st.markdown("### Account Manager")
    st.markdown(f"**Logged in user:** {st.session_state.user['email']}")
    st.markdown(f"**Role:** {st.session_state.role}")

    if st.button("Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"
        st.rerun()

    if st.button("Book Appointment", use_container_width=True):
        st.session_state.page = "Book_Appointment"
        st.rerun()

    if st.button("Reschedule Appointments", use_container_width=True):
        st.session_state.page = "Reschedule_Appointments"
        st.rerun()

    if st.button("Delete Appointments", use_container_width=True):
        st.session_state.page = "Delete_Appointments"
        st.rerun()

    if st.button("Log Out", type="primary", use_container_width=True):
        with st.spinner("Logging out..."):
            time.sleep(1)
            logout_user()
            st.rerun()

#READ: Appointment Dashboard
if st.session_state.role == "Doctor":
    if st.session_state.page == "Dashboard":
        st.title("Doctor Dashboard")
        st.markdown("Welcome! This is the Doctor Dashboard.")
        st.divider()
        st.markdown("## Appointments")

        col1, col2 = st.columns([4, 2])

        with col1:
            event = st.dataframe(
                appointments,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_appointment = appointments[selected_index]

                st.markdown("### Appointment for:")
                st.markdown(
                    f"**Patient:** {selected_appointment['patient_first_name']} {selected_appointment['patient_last_name']}"
                )
                st.markdown(f"**Date:** {selected_appointment['appointment_date']}")
                st.markdown(
                    f"**Time:** {format_time_12hr(selected_appointment['appointment_time'])}"
                )
                st.markdown(f"**Symptoms:** {selected_appointment['symptoms']}")
                st.markdown(f"**Email:** {selected_appointment['email']}")

        with col2:
            with st.container(border=True):
                st.metric("Total Appointments", len(appointments))

    elif st.session_state.page == "Book_Appointment":
        st.header("Book Appointment")

        patient_first_name = st.text_input("First Name of Patient")
        patient_last_name = st.text_input("Last Name of Patient")
        selected_date = st.date_input("Select Appointment Date")
        available_times = get_available_times(selected_date)

        if not available_times:
            st.warning("No available times for this date.")
            selected_time = None
        else:
            selected_time = st.selectbox(
                "Select a time",
                available_times,
                format_func=format_time_12hr
            )

        symptoms = st.text_input("Enter Symptoms")
        patient_email = st.text_input("Enter patient's email")

        if st.button("Book Now", use_container_width=True):
            if not patient_first_name or not patient_last_name or not symptoms or not patient_email:
                st.error("Please fill in all fields.")
            elif not selected_time:
                st.error("Please choose a date with an available time.")
            else:
                with st.spinner("Booking appointment..."):
                    time.sleep(1)

                    appointments.append(
                        {
                            "appointment_id": str(uuid.uuid4()),
                            "patient_first_name": patient_first_name,
                            "patient_last_name": patient_last_name,
                            "appointment_date": selected_date.isoformat(),
                            "appointment_time": selected_time,
                            "symptoms": symptoms,
                            "email": patient_email
                        }
                    )
                    save_appointments()
                    st.success("Appointment scheduled!")
                    time.sleep(1)
                    st.rerun()

    elif st.session_state.page == "Reschedule_Appointments":
        st.header("Reschedule Appointments")

        if not appointments:
            st.info("No appointments to reschedule.")
        else:
            appointment_ids = [appt["appointment_id"] for appt in appointments]
            selected_id = st.selectbox("Select Existing Appointment", appointment_ids)

            current_appointment = next(
                (appt for appt in appointments if appt["appointment_id"] == selected_id),
                None
            )

            new_date = st.date_input("Choose new date")
            available_times = get_available_times(new_date, exclude_appointment_id=selected_id)

            if not available_times:
                st.warning("No available times for this date.")
                new_time = None
            else:
                new_time = st.selectbox(
                    "Choose new time",
                    available_times,
                    format_func=format_time_12hr
                )

            if st.button("Reschedule Appointment"):
                if not new_time:
                    st.error("Please choose a date with an available time.")
                else:
                    with st.spinner("Rescheduling appointment..."):
                        time.sleep(1)
                        current_appointment["appointment_date"] = new_date.isoformat()
                        current_appointment["appointment_time"] = new_time
                        save_appointments()
                        st.success("Appointment rescheduled!")
                        time.sleep(1)
                        st.rerun()
#DELETE: Delete Appoinments
    elif st.session_state.page == "Delete_Appointments":
        st.header("Delete Appointments")

        if not appointments:
            st.info("No appointments to delete.")
        else:
            appointment_ids = [appt["appointment_id"] for appt in appointments]
            selected_id = st.selectbox("Select Appointment to Cancel", appointment_ids)

            if st.button("Cancel Appointment"):
                with st.spinner("Cancelling appointment..."):
                    time.sleep(1)
                    appointments = [appt for appt in appointments if appt["appointment_id"] != selected_id]
                    save_appointments()
                    st.success("Appointment canceled!")
                    time.sleep(1)
                    st.rerun()

elif st.session_state.role == "Patient":
    my_email = st.session_state.user["email"]

    if st.session_state.page == "Dashboard":
        st.title("Patient Dashboard")
        st.markdown("Welcome! This is the Patient Appointment Dashboard.")
        st.divider()
        st.markdown("## My Appointments")

        my_appointments = [appt for appt in appointments if appt["email"] == my_email]

        col1, col2 = st.columns([4, 2])

        with col1:
            event = st.dataframe(
                my_appointments,
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_appointment = my_appointments[selected_index]

                st.markdown("### Appointment for:")
                st.markdown(
                    f"**Patient:** {selected_appointment['patient_first_name']} {selected_appointment['patient_last_name']}"
                )
                st.markdown(f"**Date:** {selected_appointment['appointment_date']}")
                st.markdown(
                    f"**Time:** {format_time_12hr(selected_appointment['appointment_time'])}"
                )
                st.markdown(f"**Symptoms:** {selected_appointment['symptoms']}")

        with col2:
            with st.container(border=True):
                st.metric("My Appointments", len(my_appointments))

    elif st.session_state.page == "Book_Appointment":
        st.header("Book Appointment")

        patient_first_name = st.text_input("First Name")
        patient_last_name = st.text_input("Last Name")
        selected_date = st.date_input("Select Appointment Date")
        available_times = get_available_times(selected_date)

        if not available_times:
            st.warning("No available times for this date.")
            selected_time = None
        else:
            selected_time = st.selectbox(
                "Select a time",
                available_times,
                format_func=format_time_12hr
            )

        symptoms = st.text_input("Enter Symptoms")

        if st.button("Book Now", use_container_width=True):
            if not patient_first_name or not patient_last_name or not symptoms:
                st.error("Please fill in all fields.")
            elif not selected_time:
                st.error("Please choose a date with an available time.")
            else:
                with st.spinner("Booking appointment..."):
                    time.sleep(1)

                    appointments.append(
                        {
                            "appointment_id": str(uuid.uuid4()),
                            "patient_first_name": patient_first_name,
                            "patient_last_name": patient_last_name,
                            "appointment_date": selected_date.isoformat(),
                            "appointment_time": selected_time,
                            "symptoms": symptoms,
                            "email": my_email
                        }
                    )
                    save_appointments()
                    st.success("Appointment scheduled!")
                    time.sleep(1)
                    st.rerun()
#UPDATE: Reschedule Appointments
    elif st.session_state.page == "Reschedule_Appointments":
        st.header("Reschedule Appointments")

        my_appointments = [appt for appt in appointments if appt["email"] == my_email]

        if not my_appointments:
            st.info("You have no appointments to reschedule.")
        else:
            appointment_ids = [appt["appointment_id"] for appt in my_appointments]
            selected_id = st.selectbox("Select Existing Appointment", appointment_ids)

            new_date = st.date_input("Choose new date")
            available_times = get_available_times(new_date, exclude_appointment_id=selected_id)

            if not available_times:
                st.warning("No available times for this date.")
                new_time = None
            else:
                new_time = st.selectbox(
                    "Choose new time",
                    available_times,
                    format_func=format_time_12hr
                )

            if st.button("Reschedule Appointment"):
                if not new_time:
                    st.error("Please choose a date with an available time.")
                else:
                    with st.spinner("Rescheduling appointment..."):
                        time.sleep(1)
                        for appointment in appointments:
                            if appointment["appointment_id"] == selected_id:
                                appointment["appointment_date"] = new_date.isoformat()
                                appointment["appointment_time"] = new_time
                                break

                        save_appointments()
                        st.success("Appointment rescheduled!")
                        time.sleep(1)
                        st.rerun()
#DELETE: Delete Appoinments
    elif st.session_state.page == "Delete_Appointments":
        st.header("Delete Appointments")

        my_appointments = [appt for appt in appointments if appt["email"] == my_email]

        if not my_appointments:
            st.info("You have no appointments to cancel.")
        else:
            appointment_ids = [appt["appointment_id"] for appt in my_appointments]
            selected_id = st.selectbox("Select Appointment to Cancel", appointment_ids)

            if st.button("Cancel Appointment"):
                with st.spinner("Cancelling appointment..."):
                    time.sleep(1)
                    appointments = [appt for appt in appointments if appt["appointment_id"] != selected_id]
                    save_appointments()
                    st.success("Appointment canceled!")
                    time.sleep(1)
                    st.rerun()