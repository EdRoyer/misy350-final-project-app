from datetime import datetime, timedelta
from pathlib import Path


USERS_PATH = Path("users.json")
APPOINTMENTS_PATH = Path("appointments.json")

ROLE_PATIENT = "Patient"
ROLE_DOCTOR = "Doctor"

PAGE_DASHBOARD = "Dashboard"
PAGE_BOOK = "Book_Appointment"
PAGE_RESCHEDULE = "Reschedule_Appointments"
PAGE_DELETE = "Delete_Appointments"

DEFAULT_USERS = [
    {
        "email": "max@patient.com",
        "full_name": "Max Smith",
        "password": "123ssag@43AE",
        "role": ROLE_PATIENT,
    },
    {
        "email": "doctor@hospital.com",
        "full_name": "Roger Craig",
        "password": "2468def@56SR",
        "role": ROLE_DOCTOR,
    },
]


def build_time_slots():
    start = datetime.strptime("09:00", "%H:%M")
    end = datetime.strptime("17:00", "%H:%M")
    current = start
    times = []

    while current <= end:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)

    return times


ALL_TIMES = build_time_slots()
