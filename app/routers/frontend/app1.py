import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

# ==============================
# PAGE CONFIG
# ==============================

st.set_page_config(
    page_title="Clinic Management System",
    page_icon="🏥",
    layout="wide"
)

# ==============================
# CUSTOM CSS
# ==============================

st.markdown("""
<style>

.stApp{
    background: linear-gradient(
        to right,
        #eef2ff,
        #f8fafc
    );
}

.main-title{
    text-align:center;
    padding:20px;
    border-radius:15px;
    color:white;
    font-size:40px;
    font-weight:bold;
    background:linear-gradient(
        90deg,
        #4f46e5,
        #7c3aed
    );
}

.metric-card{
    background:white;
    padding:20px;
    border-radius:15px;
    text-align:center;
    box-shadow:0px 4px 12px rgba(0,0,0,0.15);
}

section[data-testid="stSidebar"]{
    background:linear-gradient(
        180deg,
        #4f46e5,
        #7c3aed
    );
}

section[data-testid="stSidebar"] *{
    color:white;
}

.stButton button{
    background:#4f46e5;
    color:white;
    border-radius:10px;
    border:none;
    font-weight:bold;
    width:100%;
}

.stButton button:hover{
    background:#7c3aed;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================

if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ==============================
# HELPERS
# ==============================

def get_headers():
    return {
        "Authorization":
        f"Bearer {st.session_state.token}"
    }

# ==============================
# HEADER
# ==============================

st.markdown("""
<div class='main-title'>
🏥 Clinic Appointment Management System
</div>
""", unsafe_allow_html=True)

st.write("")

# ==============================
# LOGIN / REGISTER
# ==============================

if st.session_state.token is None:

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    # ==========================
    # REGISTER
    # ==========================

    if menu == "Register":

        st.subheader("📝 Create Account")

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name"
            )

            email = st.text_input(
                "Email"
            )

            phone = st.text_input(
                "Phone"
            )

        with col2:

            password = st.text_input(
                "Password",
                type="password"
            )

            role = st.selectbox(
                "Role",
                [
                    "patient",
                    "doctor",
                    "admin"
                ]
            )

        if st.button("Register"):

            payload = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "password": password,
                "role": role
            }

            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=payload
            )

            if response.status_code == 201:

                st.success(
                    "Registration Successful"
                )

            else:

                st.error(
                    response.text
                )

    # ==========================
    # LOGIN
    # ==========================

    else:

        st.subheader("🔐 Login")

        email = st.text_input(
            "Email"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            payload = {
                "email": email,
                "password": password
            }

            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=payload
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.token = data["access_token"]
                st.session_state.role = data["role"]
                st.session_state.user_id = data["user_id"]

                st.success(
                    "Login Successful"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid Credentials"
                )

# ==============================
# DASHBOARD
# ==============================

else:

    headers = get_headers()

    profile_response = requests.get(
        f"{BASE_URL}/users/me",
        headers=headers
    )

    if profile_response.status_code != 200:

        st.error("Session Expired")

        st.session_state.token = None

        st.stop()

    profile = profile_response.json()

    st.sidebar.markdown(f"""
### 👋 Welcome

**{profile['full_name']}**

Role: **{profile['role']}**
""")

    if st.sidebar.button("Logout"):

        st.session_state.token = None
        st.session_state.role = None
        st.session_state.user_id = None

        st.rerun()

    # ==========================
    # DASHBOARD STATS
    # ==========================

    try:

        doctors = requests.get(
            f"{BASE_URL}/doctors/",
            headers=headers
        ).json()

        appointments = requests.get(
            f"{BASE_URL}/appointments/",
            headers=headers
        ).json()

        records = requests.get(
            f"{BASE_URL}/records/",
            headers=headers
        ).json()

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>👨‍⚕️ Doctors</h3>
            <h1>{len(doctors)}</h1>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>📅 Appointments</h3>
            <h1>{len(appointments)}</h1>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class='metric-card'>
            <h3>📋 Records</h3>
            <h1>{len(records)}</h1>
            </div>
            """, unsafe_allow_html=True)

    except:
        pass

    st.write("")

    # ==========================
    # NAVIGATION
    # ==========================

    page = st.sidebar.radio(
        "Navigation",
        [
            "Profile",
            "Doctors",
            "Appointments",
            "Records",
            "Admin"
        ]
    )

    # ==========================
    # PROFILE
    # ==========================

    if page == "Profile":

        st.subheader("👤 My Profile")

        st.json(profile)

    # ==========================
    # DOCTORS
    # PART 2 STARTS HERE
    # ==========================
    # ==========================
    # DOCTORS PAGE
    # ==========================

    elif page == "Doctors":

        st.subheader("👨‍⚕️ Doctors")

        tab1, tab2 = st.tabs([
            "Doctor List",
            "Create Profile"
        ])

        with tab1:

            response = requests.get(
                f"{BASE_URL}/doctors/",
                headers=headers
            )

            if response.status_code == 200:

                doctors = response.json()

                if doctors:
                    st.dataframe(
                        pd.DataFrame(doctors),
                        use_container_width=True
                    )
                else:
                    st.info("No Doctors Found")

        with tab2:

            if st.session_state.role != "doctor":

                st.warning(
                    "Only Doctors Can Create Profile"
                )

            else:

                specialization = st.text_input(
                    "Specialization"
                )

                bio = st.text_area(
                    "Bio"
                )

                available_days = st.multiselect(
                    "Available Days",
                    [
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday"
                    ]
                )

                start_time = st.text_input(
                    "Start Time",
                    "09:00"
                )

                end_time = st.text_input(
                    "End Time",
                    "17:00"
                )

                slot_duration = st.number_input(
                    "Slot Duration (mins)",
                    min_value=5,
                    value=30
                )

                if st.button(
                    "Create Doctor Profile"
                ):

                    payload = {
                        "specialization":
                        specialization,
                        "bio":
                        bio,
                        "available_days":
                        available_days,
                        "start_time":
                        start_time,
                        "end_time":
                        end_time,
                        "slot_duration":
                        slot_duration
                    }

                    response = requests.post(
                        f"{BASE_URL}/doctors/profile",
                        json=payload,
                        headers=headers
                    )

                    if response.status_code in [200,201]:

                        st.success(
                            "Doctor Profile Created"
                        )

                    else:

                        st.error(
                            response.text
                        )

    # ==========================
    # APPOINTMENTS
    # ==========================

    elif page == "Appointments":

        st.subheader("📅 Appointments")

        tab1, tab2 = st.tabs([
            "View Appointments",
            "Book Appointment"
        ])

        with tab1:

            response = requests.get(
                f"{BASE_URL}/appointments/",
                headers=headers
            )

            if response.status_code == 200:

                appointments = response.json()

                if appointments:

                    st.dataframe(
                        pd.DataFrame(
                            appointments
                        ),
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No Appointments Found"
                    )

            if st.session_state.role == "patient":

                st.divider()

                appointment_id = st.text_input(
                    "Appointment ID"
                )

                if st.button(
                    "Cancel Appointment"
                ):

                    response = requests.delete(
                        f"{BASE_URL}/appointments/{appointment_id}",
                        headers=headers
                    )

                    if response.status_code == 200:

                        st.success(
                            "Appointment Cancelled"
                        )

                    else:

                        st.error(
                            response.text
                        )

        with tab2:

            if st.session_state.role != "patient":

                st.warning(
                    "Only Patients Can Book"
                )

            else:

                doctor_response = requests.get(
                    f"{BASE_URL}/doctors/",
                    headers=headers
                )

                doctors = doctor_response.json()

                if doctors:

                    doctor_map = {
                        f"{d['full_name']} ({d['specialization']})":
                        d["id"]
                        for d in doctors
                    }

                    selected_doctor = st.selectbox(
                        "Select Doctor",
                        list(
                            doctor_map.keys()
                        )
                    )

                    appointment_date = st.date_input(
                        "Date"
                    )

                    appointment_time = st.time_input(
                        "Time"
                    )

                    reason = st.text_area(
                        "Reason"
                    )

                    if st.button(
                        "Book Appointment"
                    ):

                        datetime_string = (
                            f"{appointment_date}"
                            f"T{appointment_time}"
                        )

                        payload = {
                            "doctor_id":
                            doctor_map[
                                selected_doctor
                            ],
                            "scheduled_at":
                            datetime_string,
                            "reason":
                            reason
                        }

                        response = requests.post(
                            f"{BASE_URL}/appointments/",
                            json=payload,
                            headers=headers
                        )

                        if response.status_code in [200,201]:

                            st.success(
                                "Appointment Booked"
                            )

                        else:

                            st.error(
                                response.text
                            )

    # ==========================
    # MEDICAL RECORDS
    # ==========================

    elif page == "Records":

        st.subheader(
            "📋 Medical Records"
        )

        tab1, tab2 = st.tabs([
            "View Records",
            "Create Record"
        ])

        with tab1:

            response = requests.get(
                f"{BASE_URL}/records/",
                headers=headers
            )

            if response.status_code == 200:

                records = response.json()

                if records:

                    st.dataframe(
                        pd.DataFrame(
                            records
                        ),
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No Records Found"
                    )

        with tab2:

            if st.session_state.role != "doctor":

                st.warning(
                    "Only Doctors Can Create Records"
                )

            else:

                patient_id = st.text_input(
                    "Patient ID"
                )

                appointment_id = st.text_input(
                    "Appointment ID (Optional)"
                )

                diagnosis = st.text_area(
                    "Diagnosis"
                )

                prescription = st.text_area(
                    "Prescription"
                )

                notes = st.text_area(
                    "Notes"
                )

                if st.button(
                    "Create Record"
                ):

                    payload = {
                        "patient_id":
                        patient_id,
                        "appointment_id":
                        appointment_id
                        if appointment_id
                        else None,
                        "diagnosis":
                        diagnosis,
                        "prescription":
                        prescription,
                        "notes":
                        notes
                    }

                    response = requests.post(
                        f"{BASE_URL}/records/",
                        json=payload,
                        headers=headers
                    )

                    if response.status_code in [200,201]:

                        st.success(
                            "Record Created"
                        )

                    else:

                        st.error(
                            response.text
                        )

    # ==========================
    # ADMIN PANEL
    # ==========================

    elif page == "Admin":

        if st.session_state.role != "admin":

            st.warning(
                "Admin Access Only"
            )

        else:

            st.subheader(
                "⚙️ Admin Dashboard"
            )

            response = requests.get(
                f"{BASE_URL}/users/",
                headers=headers
            )

            if response.status_code == 200:

                users = response.json()

                if users:

                    st.dataframe(
                        pd.DataFrame(users),
                        use_container_width=True
                    )

            st.divider()

            st.subheader(
                "Delete User"
            )

            user_id = st.text_input(
                "User ID"
            )

            if st.button(
                "Delete User"
            ):

                response = requests.delete(
                    f"{BASE_URL}/users/{user_id}",
                    headers=headers
                )

                if response.status_code in [200,204]:

                    st.success(
                        "User Deleted"
                    )

                else:

                    st.error(
                        response.text
                    )