import json
import uuid
from datetime import datetime

from constants import ALL_TIMES, APPOINTMENTS_PATH, DEFAULT_USERS, USERS_PATH


def safe_load_json(path, default):
    if not path.exists():
        save_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_users():
    return safe_load_json(USERS_PATH, DEFAULT_USERS)


def load_appointments():
    return safe_load_json(APPOINTMENTS_PATH, [])


def save_users(users):
    save_json(USERS_PATH, users)


def save_appointments(appointments):
    save_json(APPOINTMENTS_PATH, appointments)


def find_user(users, email, password):
    for user in users:
        if (
            user["email"].strip().lower() == email.strip().lower()
            and user["password"] == password
        ):
            return user
    return None


def email_exists(users, email):
    return any(user["email"].strip().lower() == email.strip().lower() for user in users)


def get_available_times(appointments, selected_date, exclude_appointment_id=None):
    unavailable_times = []

    for appointment in appointments:
        if appointment["appointment_date"] == selected_date.isoformat():
            if (
                exclude_appointment_id
                and appointment["appointment_id"] == exclude_appointment_id
            ):
                continue
            unavailable_times.append(appointment["appointment_time"])

    return [time_slot for time_slot in ALL_TIMES if time_slot not in unavailable_times]


def format_time_12hr(time_24):
    return datetime.strptime(time_24, "%H:%M").strftime("%I:%M %p")


def create_appointment(
    first_name, last_name, appointment_date, appointment_time, symptoms, email
):
    return {
        "appointment_id": str(uuid.uuid4()),
        "patient_first_name": first_name,
        "patient_last_name": last_name,
        "appointment_date": appointment_date.isoformat(),
        "appointment_time": appointment_time,
        "symptoms": symptoms,
        "email": email,
    }


def filter_appointments_by_email(appointments, email):
    return [appointment for appointment in appointments if appointment["email"] == email]


def get_appointment_by_id(appointments, appointment_id):
    return next(
        (
            appointment
            for appointment in appointments
            if appointment["appointment_id"] == appointment_id
        ),
        None,
    )


def update_appointment_time(appointments, appointment_id, new_date, new_time):
    appointment = get_appointment_by_id(appointments, appointment_id)
    if appointment:
        appointment["appointment_date"] = new_date.isoformat()
        appointment["appointment_time"] = new_time
    return appointment


def delete_appointment_by_id(appointments, appointment_id):
    return [
        appointment
        for appointment in appointments
        if appointment["appointment_id"] != appointment_id
    ]
