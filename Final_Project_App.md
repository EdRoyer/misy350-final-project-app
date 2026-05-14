# Final Project App

## Origin Prompt

1. ##Study what the app does.
2. ##Record the prompt that generated this analysis in the correct order in the document it creates, under a section such as Origin Prompt.
3. ##Study what the app currently does.
4. ##Record the prompt that generated this analysis in the correct order in the document it creates, under Origin Prompt.
5. ##Create a plan for structural changes.
6. ##Save the plan.
7. ##Include the original prompt as a section in the plan for historical recordkeeping.
8. ##Place the prompt in the correct order in the document it creates, under Origin Prompt.
9. #Save each plan version with a date if the plan goes through multiple rounds.
10. #Implement only the structural changes.
11. #If any change affects another layer, explain why.
12. #Place the prompt in the correct order in the document it creates, under Origin Prompt.
13. #Make a feature analysis to create a separate plan.
14. #This plan needs to address missing features, improvements, UI design, Streamlit pages, routing, st.session_state, user actions, and feedback messages.
15. #Include the original prompt as a section in the plan.
16. #Place the prompt in the correct order in the document it creates, under Origin Prompt.
17. #Keep dated records of each plan version.
18. #Implement the planned changes.
19. #Record follow-up prompts that lead to additional changes.
20. #For each refinement, document what changed, why it changed, and which layer was affected.
21. #Add chatbot into code.
22. #Add similar code to app.py from dotenv import load_dotenv and from openai import OpenAI.

## Plan Version Recordkeeping

#Each plan update should be saved as a new dated version instead of replacing the earlier version. Use the format `Plan Version N - YYYY-MM-DD`, and include the original prompt or refinement prompt that caused that version.

#Record follow-up prompts under `Origin Prompt` when they lead to additional planning, implementation, or documentation changes.

## Refinement Log

### 2026-05-10 - Structural Refactor

#Affected layer: UI layer, data access layer, routing/session structure.

### 2026-05-10 - Feature Analysis Plan Version 2

#What changed: The feature plan was expanded to cover missing features, improvements, UI design, Streamlit pages, routing, `st.session_state`, user actions, and feedback messages.

#Why it changed: The first feature plan focused mostly on feature gaps, so the plan needed fuller coverage of the actual Streamlit user experience.

#Affected layer: Planning/documentation layer, UI design layer, routing/session design layer.

### 2026-05-10 - Planned Feature Implementation

#What changed: The nested project app added future-date restrictions, readable appointment selectors, sorted appointment dashboards, dashboard timeframe filters, stronger validation, normalized inputs, doctor patient selection, user IDs for new accounts, appointment detail previews, and delete confirmation.

#Why it changed: These updates implemented the planned missing features and user-experience improvements while preserving the appointment-manager workflow.

#Affected layer: UI layer, validation layer, data-handling layer, user-action flow, feedback-message layer.

### 2026-05-10 - Recordkeeping Updates

#What changed: The project document added prompt history, dated plan versions, original-prompt sections, follow-up prompt tracking, and this refinement log.

#Why it changed: The document needs to preserve historical context for how plans and implementation changes were requested and refined.

#Affected layer: Documentation layer.

### 2026-05-10 - Chatbot Feature

#What changed: The nested project app added an Appointment Chatbot page, a sidebar route to the chatbot, chat history stored in `st.session_state`, and rule-based chatbot responses for booking, rescheduling, cancellation, dashboard navigation, available times, counts, and next appointments.

#Why it changed: The app needed an interactive helper so users can ask common appointment-management questions without leaving the Streamlit interface.

#Affected layer: UI layer, routing layer, `st.session_state` layer, feedback/help-message layer.

### 2026-05-10 - OpenAI Chatbot Integration

#What changed: The nested project app added optional `dotenv` and OpenAI client setup, an OpenAI-backed chatbot response path, an appointment-specific system prompt, appointment context hints, and JSON chat log loading/saving under `ai-assistant/ai_logs.json`.

#Why it changed: The chatbot needed to support an OpenAI API-powered assistant similar to the provided sample code while still falling back to the local helper if packages or `OPENAI_API_KEY` are missing.

#Affected layer: AI service layer, environment/configuration layer, chat persistence layer, UI feedback layer.

## Structural Change Plan

### Plan Version 1 - 2026-05-10

#### Original Prompt

#Create a plan for structural changes.

#### Plan

#1. Separate data logic.
#Move JSON loading, JSON saving, user lookup, appointment filtering, and appointment create/update/delete helpers into a dedicated data layer such as `data_store.py`.

#2. Create role-based page functions.
#Break the large nested Doctor and Patient sections into focused functions such as `show_login_page()`, `show_sidebar()`, `show_doctor_dashboard()`, `show_patient_dashboard()`, `show_doctor_booking()`, and `show_patient_booking()`.

#3. Reduce duplicate appointment code.
#Create reusable helpers for rendering appointment details, selecting available times, creating appointment dictionaries, deleting appointments by ID, updating appointment date/time, and filtering appointments by email.

#4. Add constants.
#Move repeated role names and page names into constants such as `ROLE_DOCTOR`, `ROLE_PATIENT`, `PAGE_DASHBOARD`, `PAGE_BOOK`, `PAGE_RESCHEDULE`, and `PAGE_DELETE`.

#5. Improve validation.
#Add validation for required fields, email format, past appointment dates, doctor-entered patient emails, and optional password requirements.

#6. Improve data model consistency.
#Make user IDs consistent across default users and registered users. Consider linking appointments to `user_id` instead of relying only on email.

#7. Make the main app flow smaller.
#Restructure `app.py` so it mostly initializes the app, loads data, initializes session state, shows login when needed, shows the sidebar after login, and routes to the correct role/page view.

#8. Optionally add a `pages/` folder.
#If the project grows, split UI code into files such as `pages/login.py`, `pages/doctor.py`, and `pages/patient.py`. For this class project, `data_store.py`, `constants.py`, and page functions may be enough.

## Feature Analysis Plan

### Plan Version 1 - 2026-05-10

#### Original Prompt

#Make a feature analysis to create a separate plan.

#### Current Feature Baseline

#The app currently supports login, registration, role-based dashboards, appointment booking, appointment rescheduling, appointment deletion, local JSON storage, and basic prevention of double-booked appointment times.

#Doctors can view and manage all appointments. Patients can view and manage only appointments connected to their own email address.

#### Feature Gaps

#1. Appointment date rules.
#The app allows past appointment dates. A feature update should prevent users from booking or rescheduling appointments before the current date.

#2. Patient email validation for doctors.
#Doctors can book appointments for any typed email, even if that email does not belong to a registered patient. A feature update should decide whether doctors must select from registered patients or may still enter external patient emails.

#3. User account consistency.
#Registered users do not receive an `id`, while the existing `users.json` records already include IDs. A feature update should create IDs for all new users and optionally connect appointments to user IDs.

#4. Appointment display clarity.
#Appointment selectors currently show raw appointment IDs. A feature update should display readable labels such as patient name, date, and time while still using the appointment ID internally.

#5. Dashboard filtering and sorting.
#Dashboards show appointment data directly from JSON order. A feature update should sort appointments by date/time and optionally add filters for upcoming appointments, past appointments, patient email, or date.

#6. Form validation.
#The app only checks whether required fields are blank. A feature update should validate email format, trim extra spaces, and prevent blank-looking values.

#7. Authentication safety.
#Passwords are stored in plain text. For a class project this may be acceptable, but a feature update could hash passwords before saving them.

#8. Appointment status.
#Deleting appointments removes history. A feature update could add appointment statuses such as `Scheduled`, `Cancelled`, and `Completed` instead of removing records immediately.

#### Feature Plan

#1. Add safer appointment date handling.
#Set minimum selectable dates for booking and rescheduling. Add a validation check before saving as a backup.

#2. Improve appointment selection labels.
#Replace raw ID dropdown labels with readable appointment summaries while preserving appointment IDs internally.

#3. Add stronger form validation.
#Create validation helpers for required text, email format, and normalized input values.

#4. Improve dashboard organization.
#Sort appointments by date and time. Add simple upcoming/past grouping if needed.

#5. Add consistent user IDs.
#Assign IDs to new registered users and optionally add a migration helper for users missing IDs.

#6. Decide doctor booking rules.
#Choose whether doctors should select an existing patient or enter any patient email. If selecting existing patients, add a patient dropdown sourced from registered patient accounts.

#7. Consider appointment status.
#Add a status field if appointment history matters. Keep hard delete only if the assignment expects simple CRUD deletion.

#8. Consider password hashing.
#If the project needs a more realistic login system, hash passwords when users register and verify hashes during login.

#### Recommended Feature Order

#1. Appointment date rules.
#2. Readable appointment selectors.
#3. Form validation.
#4. Dashboard sorting.
#5. User ID consistency.
#6. Doctor patient-selection workflow.
#7. Appointment status.
#8. Password hashing.

### Plan Version 2 - 2026-05-10

#### Original Prompt

#Make a feature analysis to create a separate plan.

#### Version 2 Refinement Prompt

#This plan needs to address missing features, improvements, UI design, Streamlit pages, routing, st.session_state, user actions, and feedback messages.

#### Purpose

#This version expands the feature plan beyond data and appointment behavior. It covers the full Streamlit user experience: missing features, interface improvements, page organization, route handling, session state, user actions, and feedback messages.

#### Missing Features

#1. Prevent past appointment dates.
#Booking and rescheduling should only allow today or future dates. Add a minimum date to `st.date_input()` and validate again before saving.

#2. Improve doctor patient selection.
#Doctors should either select a registered patient from a dropdown or clearly enter an external patient email. The preferred class-project option is a dropdown of registered patient accounts.

#3. Add readable appointment selectors.
#Reschedule and delete pages should show appointment labels such as `Max Smith - 2026-04-06 at 5:00 PM` instead of raw appointment IDs.

#4. Add appointment sorting and filtering.
#Dashboards should sort appointments by date and time. Optional filters can include upcoming appointments, past appointments, appointment date, patient email, and status.

#5. Add user ID consistency.
#New users should receive an `id` value during registration. Existing users without IDs should be handled safely.

#6. Add appointment status if history matters.
#Instead of only deleting records, the app could support `Scheduled`, `Cancelled`, and `Completed`. Keep hard delete if the assignment requires simple CRUD behavior.

#7. Add stronger validation.
#Validate email format, required text fields, trimmed input, duplicate appointment slots, and blank-looking values.

#### Improvements

#1. Reduce repeated UI logic.
#Reuse booking, rescheduling, deletion, appointment detail, and appointment selector helpers.

#2. Normalize form input.
#Trim spaces from names, emails, and symptoms before saving.

#3. Improve JSON resilience.
#Keep safe loading behavior, but consider showing an error if JSON is corrupted instead of silently returning defaults.

#4. Improve dashboard readability.
#Hide technical IDs from the main dataframe when possible, or show friendlier column labels.

#5. Improve role permissions.
#Keep patient actions scoped to their own email. Keep doctor actions global, but make doctor-only actions visually clear.

#### UI Design Plan

#1. Login and registration page.
#Keep the two-column layout, but clarify the page title and labels. Use concise success and error messages.

#2. Sidebar navigation.
#Keep role, email, and navigation buttons visible. Highlight or clearly indicate the current page if practical.

#3. Dashboard pages.
#Use metrics for appointment counts. Show appointment details after row selection. Sort the table so upcoming appointments are easy to scan.

#4. Booking page.
#Group patient identity, date/time, and symptoms in a clear order. Keep the primary action as `Book Now`.

#5. Reschedule page.
#how a readable appointment selector first, then the new date/time controls. Display the current appointment details before changes.

#6. Delete page.
#Show a readable appointment selector and appointment details before cancellation. Consider requiring a checkbox confirmation before deleting.

#### Streamlit Pages And Routing

#1. Keep the current single-file Streamlit route model for now.
#The app already routes using `st.session_state.page`, which is enough for this project.

#2. Add page constants for any new pages.
#If new pages are added, define constants in `constants.py` before using them in the sidebar or router.

#3. Keep route handling centralized.
#`route_page()` should remain the only place that decides which role-specific page function to show.

#4. Add pages only when needed.
#Possible future pages include `Profile`, `All Patients`, `Appointment History`, or `Settings`.

#### st.session_state Plan

#1. Preserve login state.
#Continue using `logged_in`, `user`, `role`, and `page`.

#2. Add temporary state only when needed.
#Possible additions include selected appointment ID, active filters, confirmation state, or success messages after reruns.

#3. Reset page on login and logout.
#Continue sending users to the dashboard after login and clearing user state after logout.

#4. Avoid storing full appointment data in session state.
#Keep appointment records in JSON and reload them each run so the saved files remain the source of truth.

#### User Actions Plan

#1. Account actions.
#Users can log in, register, and log out.

#2. Dashboard actions.
#Users can select an appointment row to view details.

#3. Booking actions.
#Patients can book for themselves. Doctors can book for a patient, ideally using a registered-patient selector.

#4. Rescheduling actions.
#Users select an appointment, choose a new date/time, and save the change.

#5. Delete or cancel actions.
#Users select an appointment and cancel it. Add confirmation if accidental deletion is a concern.

#6. Filtering actions.
#Users can narrow dashboard results by date, status, or patient, depending on role.

#### Feedback Messages Plan

#1. Login feedback.
#Show success on login and clear error text for invalid credentials.

#2. Registration feedback.
#Show errors for missing fields, invalid email, or duplicate email. Show success when the account is created.

#3. Booking feedback.
#Show warnings when no appointment times are available. Show errors for invalid fields. Show success when the appointment is scheduled.

#4. Rescheduling feedback.
#Show warnings when the selected date has no available times. Show success when the appointment is rescheduled.

#5. Delete feedback.
#Show confirmation or warning before deletion. Show success when an appointment is canceled.

#6. Empty-state feedback.
#Show clear messages when there are no appointments to view, reschedule, or delete.

#### Recommended Implementation Order

#1. Add readable appointment selector labels.
#2. Add date restrictions and validation.
#3. Add stronger form validation and input normalization.
#4. Improve dashboard sorting and display labels.
#5. Improve doctor patient selection.
#6. Add optional delete confirmation.
#7. Add optional filters.
#8. Add optional appointment status/history.
#9. Add optional user ID cleanup.
