import streamlit as st
import json
import os
from pathlib import Path
from datetime import date, datetime, timedelta
import uuid
import time
import re

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

if load_dotenv:
    load_dotenv()

st.set_page_config(
    page_title="Appointment Manager",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

users_path = Path("users.json")
appointments_path = Path("appointments.json")
ai_logs_path = Path("ai-assistant/ai_logs.json")

default_users = [
    {
        "id": "9a5c647f-8d92-41bc-bb4a-695638b26bbb",
        "email": "max@patient.com",
        "full_name": "Max Smith",
        "password": "123ssag@43AE",
        "role": "Patient"
    },
    {
        "id": "c60d6ac8-2ed0-4e52-b62c-1101543c3e8c",
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


def load_logs(filepath):
    json_path = Path(filepath)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_logs(filepath, logs):
    json_path = Path(filepath)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


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


def normalize_text(value):
    return value.strip()


def normalize_email(value):
    return value.strip().lower()


def is_valid_email(email):
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None


def ensure_user_ids():
    changed = False

    for user in users:
        if "id" not in user:
            user["id"] = str(uuid.uuid4())
            changed = True

    if changed:
        save_users()


def get_registered_patients():
    return [user for user in users if user["role"] == "Patient"]


def split_full_name(full_name):
    parts = full_name.split(maxsplit=1)
    first_name = parts[0] if parts else ""
    last_name = parts[1] if len(parts) > 1 else ""
    return first_name, last_name


def parse_appointment_datetime(appointment):
    return datetime.strptime(
        f"{appointment['appointment_date']} {appointment['appointment_time']}",
        "%Y-%m-%d %H:%M"
    )


def sort_appointments(appointment_list):
    return sorted(appointment_list, key=parse_appointment_datetime)


def filter_appointments_by_timeframe(appointment_list, timeframe):
    today_iso = date.today().isoformat()

    if timeframe == "Upcoming":
        return [
            appointment
            for appointment in appointment_list
            if appointment["appointment_date"] >= today_iso
        ]

    if timeframe == "Past":
        return [
            appointment
            for appointment in appointment_list
            if appointment["appointment_date"] < today_iso
        ]

    return appointment_list


def appointment_label(appointment):
    patient_name = (
        f"{appointment['patient_first_name']} {appointment['patient_last_name']}"
    )
    appointment_time = format_time_12hr(appointment["appointment_time"])
    return f"{patient_name} - {appointment['appointment_date']} at {appointment_time}"


def appointment_display_rows(appointment_list, include_email=False):
    rows = []

    for appointment in appointment_list:
        row = {
            "Patient": (
                f"{appointment['patient_first_name']} "
                f"{appointment['patient_last_name']}"
            ),
            "Date": appointment["appointment_date"],
            "Time": format_time_12hr(appointment["appointment_time"]),
            "Symptoms": appointment["symptoms"]
        }

        if include_email:
            row["Email"] = appointment["email"]

        rows.append(row)

    return rows


def appointment_selectbox(label, appointment_list):
    appointment_options = {
        appointment_label(appointment): appointment["appointment_id"]
        for appointment in appointment_list
    }
    selected_label = st.selectbox(label, list(appointment_options.keys()))
    return appointment_options[selected_label]


def show_appointment_details(appointment, include_email=False):
    st.markdown("### Appointment for:")
    st.markdown(
        f"**Patient:** {appointment['patient_first_name']} {appointment['patient_last_name']}"
    )
    st.markdown(f"**Date:** {appointment['appointment_date']}")
    st.markdown(
        f"**Time:** {format_time_12hr(appointment['appointment_time'])}"
    )
    st.markdown(f"**Symptoms:** {appointment['symptoms']}")

    if include_email:
        st.markdown(f"**Email:** {appointment['email']}")


def validate_required_fields(fields):
    return all(normalize_text(field) for field in fields)


def date_is_valid(selected_date):
    return selected_date >= date.today()


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


def build_prompt(context_hint):
    return (
        "You are an AI assistant inside a healthcare appointment manager app. "
        "Help users understand how to book, view, reschedule, and cancel appointments. "
        "Use the supplied appointment context when answering questions about counts, "
        "next appointments, roles, and navigation. Do not provide medical diagnosis "
        "or treatment advice. If a user describes urgent symptoms, tell them to "
        "contact emergency services or a medical professional. "
        "If the user asks about previous messages, use the chat history. "
        f"Context: {context_hint}"
    )



def get_openai_client():
    api_key = None

    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return None

    return OpenAI(api_key=api_key)

def get_ai_response(client, chat_history, context_hint):
    prompt_message = {
        "role": "system",
        "content": build_prompt(context_hint)
    }
    messages = [prompt_message] + chat_history

    ai_response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        temperature=1
    )

    return ai_response.choices[0].message.content


def get_user_appointments():
    if st.session_state.role == "Doctor":
        return sort_appointments(appointments)

    user_email = st.session_state.user["email"]
    return sort_appointments(
        [appointment for appointment in appointments if appointment["email"] == user_email]
    )


def get_next_appointment(user_appointments):
    upcoming_appointments = filter_appointments_by_timeframe(
        user_appointments,
        "Upcoming"
    )

    if not upcoming_appointments:
        return None

    return sort_appointments(upcoming_appointments)[0]


def build_chatbot_context_hint():
    user_appointments = get_user_appointments()
    next_appointment = get_next_appointment(user_appointments)
    role = st.session_state.role
    user_email = st.session_state.user["email"]

    if next_appointment:
        next_appointment_text = appointment_label(next_appointment)
    else:
        next_appointment_text = "No upcoming appointments."

    return (
        f"Logged in role: {role}. "
        f"Logged in email: {user_email}. "
        f"Visible appointment count: {len(user_appointments)}. "
        f"Total system appointments: {len(appointments)}. "
        f"Next visible appointment: {next_appointment_text}. "
        "Sidebar pages: Dashboard, Book Appointment, Reschedule Appointments, "
        "Delete Appointments, Chatbot, Log Out. "
        "Appointments are available every 30 minutes from 9:00 AM through 5:00 PM."
    )


def chatbot_response(message):
    cleaned_message = message.strip().lower()
    user_appointments = get_user_appointments()
    next_appointment = get_next_appointment(user_appointments)

    if not cleaned_message:
        return "Ask me about booking, rescheduling, canceling, or viewing appointments."

    if any(word in cleaned_message for word in ["hello", "hi", "hey"]):
        return (
            "Hi! I can help you find where to book, reschedule, cancel, "
            "or review appointments in this app."
        )

    if "book" in cleaned_message or "schedule" in cleaned_message:
        return (
            "Use the Book Appointment page from the sidebar. "
            "Choose a future date, pick an available time, enter symptoms, "
            "then click Book Now."
        )

    if "reschedule" in cleaned_message or "change" in cleaned_message:
        return (
            "Use Reschedule Appointments from the sidebar. Select the appointment, "
            "choose a new future date and available time, then save the change."
        )

    if "cancel" in cleaned_message or "delete" in cleaned_message:
        return (
            "Use Delete Appointments from the sidebar. Select the appointment, "
            "review the details, check the confirmation box, then click Cancel Appointment."
        )

    if "next" in cleaned_message or "upcoming" in cleaned_message:
        if next_appointment:
            return f"Your next appointment is {appointment_label(next_appointment)}."
        return "I do not see any upcoming appointments for your account."

    if "how many" in cleaned_message or "count" in cleaned_message:
        if st.session_state.role == "Doctor":
            return f"There are {len(appointments)} total appointments in the system."
        return f"You have {len(user_appointments)} appointment(s)."

    if "time" in cleaned_message or "available" in cleaned_message:
        return (
            "Appointments are offered every 30 minutes from 9:00 AM through 5:00 PM. "
            "Already-booked times are removed from the time dropdown."
        )

    if "dashboard" in cleaned_message or "view" in cleaned_message:
        return (
            "Use the Dashboard page to view appointments. You can filter by All, "
            "Upcoming, or Past and select a row to see details."
        )

    if "doctor" in cleaned_message and st.session_state.role == "Doctor":
        return (
            "As a doctor, you can view all appointments, book for registered patients, "
            "reschedule any appointment, and cancel appointments."
        )

    if "patient" in cleaned_message:
        return (
            "Patients can view, book, reschedule, and cancel appointments connected "
            "to their own logged-in email."
        )

    return (
        "I can help with appointments, booking, rescheduling, cancellations, "
        "available times, and dashboard navigation."
    )


def show_chatbot_page():
    st.title("Appointment Chatbot")
    st.markdown("Ask about appointments, booking, rescheduling, cancellations, or dashboard navigation.")
    client = get_openai_client()

    if OpenAI is None:
        st.warning("The openai package is not installed, so the local appointment helper is being used.")
    elif not get_openai_client():
        st.warning("OPENAI_API_KEY was not found, so the local appointment helper is being used.")

    if "chat_messages" not in st.session_state:
        logs = load_logs(ai_logs_path)
        st.session_state.chat_messages = [
            {
                "role": log["role"],
                "content": log["content"]
            }
            for log in logs
            if "role" in log and "content" in log
        ]

        if not st.session_state.chat_messages:
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Hi! I can help you use the appointment manager. "
                        "What would you like to do?"
                    )
                }
            ]

    for chat_message in st.session_state.chat_messages:
        with st.chat_message(chat_message["role"]):
            st.markdown(chat_message["content"])

    prompt = st.chat_input("Ask the appointment assistant")

    if prompt:
        st.session_state.chat_messages.append(
            {"role": "user", "content": prompt}
        )

        if client:
            try:
                response = get_ai_response(
                    client=client,
                    chat_history=st.session_state.chat_messages,
                    context_hint=build_chatbot_context_hint()
                )
            except Exception as error:
                response = (
                    "I could not reach the OpenAI assistant right now, so I used "
                    f"the local appointment helper instead. {chatbot_response(prompt)}"
                )
                st.warning(f"OpenAI request failed: {error}")
        else:
            response = chatbot_response(prompt)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response}
        )
        save_logs(ai_logs_path, st.session_state.chat_messages)
        st.rerun()


users = safe_load_json(users_path, default_users)
appointments = safe_load_json(appointments_path, [])
ensure_user_ids()

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
                    clean_email = normalize_email(new_email)
                    clean_full_name = normalize_text(new_full_name)
                    clean_password = normalize_text(new_password)

                    email_exists = any(
                        user["email"].strip().lower() == clean_email
                        for user in users
                    )

                    if not clean_email or not clean_password or not clean_full_name:
                        st.error("Please fill in all fields.")
                    elif not is_valid_email(clean_email):
                        st.error("Please enter a valid email address.")
                    elif email_exists:
                        st.error("An account with that email already exists.")
                    else:
                        new_user = {
                            "id": str(uuid.uuid4()),
                            "email": clean_email,
                            "full_name": clean_full_name,
                            "password": clean_password,
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

    if st.button("Chatbot", use_container_width=True):
        st.session_state.page = "Chatbot"
        st.rerun()

    if st.button("Log Out", type="primary", use_container_width=True):
        with st.spinner("Logging out..."):
            time.sleep(1)
            logout_user()
            st.rerun()

if st.session_state.page == "Chatbot":
    show_chatbot_page()
    st.stop()

#READ: Appointment Dashboard
if st.session_state.role == "Doctor":
    if st.session_state.page == "Dashboard":
        st.title("Doctor Dashboard")
        st.markdown("Welcome! This is the Doctor Dashboard.")
        st.divider()
        st.markdown("## Appointments")
        timeframe_filter = st.selectbox(
            "Show appointments",
            ["All", "Upcoming", "Past"],
            key="doctor_timeframe_filter"
        )
        filtered_appointments = filter_appointments_by_timeframe(
            appointments,
            timeframe_filter
        )
        sorted_appointments = sort_appointments(filtered_appointments)

        col1, col2 = st.columns([4, 2])

        with col1:
            event = st.dataframe(
                appointment_display_rows(sorted_appointments, include_email=True),
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_appointment = sorted_appointments[selected_index]
                show_appointment_details(selected_appointment, include_email=True)

        with col2:
            with st.container(border=True):
                st.metric("Total Appointments", len(appointments))

    elif st.session_state.page == "Book_Appointment":
        st.header("Book Appointment")
        registered_patients = get_registered_patients()

        if not registered_patients:
            st.warning("No registered patients are available.")
            st.stop()

        selected_patient = st.selectbox(
            "Select Patient",
            registered_patients,
            format_func=lambda patient: f"{patient['full_name']} ({patient['email']})"
        )
        default_first_name, default_last_name = split_full_name(
            selected_patient["full_name"]
        )
        patient_first_name = st.text_input(
            "First Name of Patient",
            value=default_first_name
        )
        patient_last_name = st.text_input(
            "Last Name of Patient",
            value=default_last_name
        )
        selected_date = st.date_input("Select Appointment Date", min_value=date.today())
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
        patient_email = selected_patient["email"]

        if st.button("Book Now", use_container_width=True):
            clean_first_name = normalize_text(patient_first_name)
            clean_last_name = normalize_text(patient_last_name)
            clean_symptoms = normalize_text(symptoms)
            clean_email = normalize_email(patient_email)

            if not validate_required_fields(
                [clean_first_name, clean_last_name, clean_symptoms, clean_email]
            ):
                st.error("Please fill in all fields.")
            elif not date_is_valid(selected_date):
                st.error("Please choose today or a future date.")
            elif not selected_time:
                st.error("Please choose a date with an available time.")
            else:
                with st.spinner("Booking appointment..."):
                    time.sleep(1)

                    appointments.append(
                        {
                            "appointment_id": str(uuid.uuid4()),
                            "patient_first_name": clean_first_name,
                            "patient_last_name": clean_last_name,
                            "appointment_date": selected_date.isoformat(),
                            "appointment_time": selected_time,
                            "symptoms": clean_symptoms,
                            "email": clean_email
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
            sorted_appointments = sort_appointments(appointments)
            selected_id = appointment_selectbox(
                "Select Existing Appointment",
                sorted_appointments
            )

            current_appointment = next(
                (appt for appt in appointments if appt["appointment_id"] == selected_id),
                None
            )
            show_appointment_details(current_appointment, include_email=True)

            new_date = st.date_input("Choose new date", min_value=date.today())
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
                if not date_is_valid(new_date):
                    st.error("Please choose today or a future date.")
                elif not new_time:
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
            sorted_appointments = sort_appointments(appointments)
            selected_id = appointment_selectbox(
                "Select Appointment to Cancel",
                sorted_appointments
            )
            current_appointment = next(
                (appt for appt in appointments if appt["appointment_id"] == selected_id),
                None
            )
            show_appointment_details(current_appointment, include_email=True)
            confirm_delete = st.checkbox("I understand this will cancel the appointment.")

            if st.button("Cancel Appointment"):
                if not confirm_delete:
                    st.warning("Please confirm before canceling this appointment.")
                else:
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
        timeframe_filter = st.selectbox(
            "Show appointments",
            ["All", "Upcoming", "Past"],
            key="patient_timeframe_filter"
        )

        my_appointments = sort_appointments(
            filter_appointments_by_timeframe(
                [appt for appt in appointments if appt["email"] == my_email],
                timeframe_filter
            )
        )

        col1, col2 = st.columns([4, 2])

        with col1:
            event = st.dataframe(
                appointment_display_rows(my_appointments),
                on_select="rerun",
                selection_mode="single-row",
                use_container_width=True
            )

            if event.selection.rows:
                selected_index = event.selection.rows[0]
                selected_appointment = my_appointments[selected_index]
                show_appointment_details(selected_appointment)

        with col2:
            with st.container(border=True):
                st.metric("My Appointments", len(my_appointments))

    elif st.session_state.page == "Book_Appointment":
        st.header("Book Appointment")

        patient_first_name = st.text_input("First Name")
        patient_last_name = st.text_input("Last Name")
        selected_date = st.date_input("Select Appointment Date", min_value=date.today())
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
            clean_first_name = normalize_text(patient_first_name)
            clean_last_name = normalize_text(patient_last_name)
            clean_symptoms = normalize_text(symptoms)

            if not validate_required_fields(
                [clean_first_name, clean_last_name, clean_symptoms]
            ):
                st.error("Please fill in all fields.")
            elif not date_is_valid(selected_date):
                st.error("Please choose today or a future date.")
            elif not selected_time:
                st.error("Please choose a date with an available time.")
            else:
                with st.spinner("Booking appointment..."):
                    time.sleep(1)

                    appointments.append(
                        {
                            "appointment_id": str(uuid.uuid4()),
                            "patient_first_name": clean_first_name,
                            "patient_last_name": clean_last_name,
                            "appointment_date": selected_date.isoformat(),
                            "appointment_time": selected_time,
                            "symptoms": clean_symptoms,
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

        my_appointments = sort_appointments(
            [appt for appt in appointments if appt["email"] == my_email]
        )

        if not my_appointments:
            st.info("You have no appointments to reschedule.")
        else:
            selected_id = appointment_selectbox(
                "Select Existing Appointment",
                my_appointments
            )
            current_appointment = next(
                (appt for appt in appointments if appt["appointment_id"] == selected_id),
                None
            )
            show_appointment_details(current_appointment)

            new_date = st.date_input("Choose new date", min_value=date.today())
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
                if not date_is_valid(new_date):
                    st.error("Please choose today or a future date.")
                elif not new_time:
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

        my_appointments = sort_appointments(
            [appt for appt in appointments if appt["email"] == my_email]
        )

        if not my_appointments:
            st.info("You have no appointments to cancel.")
        else:
            selected_id = appointment_selectbox(
                "Select Appointment to Cancel",
                my_appointments
            )
            current_appointment = next(
                (appt for appt in appointments if appt["appointment_id"] == selected_id),
                None
            )
            show_appointment_details(current_appointment)
            confirm_delete = st.checkbox("I understand this will cancel the appointment.")

            if st.button("Cancel Appointment"):
                if not confirm_delete:
                    st.warning("Please confirm before canceling this appointment.")
                else:
                    with st.spinner("Cancelling appointment..."):
                        time.sleep(1)
                        appointments = [appt for appt in appointments if appt["appointment_id"] != selected_id]
                        save_appointments()
                        st.success("Appointment canceled!")
                        time.sleep(1)
                        st.rerun()
