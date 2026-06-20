from PIL import ExifTags
from PIL import ExifTags
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://clinic-appointment-system-using-fastapi.onrender.com/"

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────

st.set_page_config(
    page_title="MediCare Clinic",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────

st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a8a 0%, #312e81 100%);
    color: white;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] .stRadio label {
    color: #c7d2fe !important;
    font-size: 0.95rem;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2) !important;
}

/* ── Metric Cards ── */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    border-left: 5px solid;
    margin-bottom: 12px;
}

/* ── Section Header ── */
.section-header {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 4px;
}

.section-sub {
    color: #64748b;
    font-size: 0.92rem;
    margin-bottom: 20px;
}

/* ── Card ── */
.info-card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
}

/* Primary (default) button */
.stButton > button[kind="primary"],
div.stButton > button:first-child {
    background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    color: white !important;
    border: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > textarea,
.stNumberInput > div > input,
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #fafbff !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
}

/* ── Divider ── */
hr {
    border: none;
    border-top: 1.5px solid #e2e8f0;
    margin: 24px 0;
}

/* ── Alerts ── */
.stSuccess, .stError, .stWarning, .stInfo {
    border-radius: 10px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* ── Tags ── */
.role-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-patient  { background:#dbeafe; color:#1d4ed8; }
.badge-doctor   { background:#d1fae5; color:#065f46; }
.badge-admin    { background:#fce7f3; color:#9d174d; }

/* ── Login card ── */
.login-wrap {
    max-width: 440px;
    margin: 40px auto;
    background: white;
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.1);
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #1e3a8a, #4f46e5);
    border-radius: 18px;
    padding: 32px 36px;
    color: white;
    margin-bottom: 28px;
}
.hero h1 { font-size: 1.8rem; font-weight: 700; margin: 0 0 6px; }
.hero p  { font-size: 0.95rem; opacity: 0.85; margin: 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────

for key, default in [
    ("token", None),
    ("role", None),
    ("user_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def role_badge(role):
    cls = {"patient": "badge-patient", "doctor": "badge-doctor", "admin": "badge-admin"}.get(role, "badge-patient")
    return f'<span class="role-badge {cls}">{role}</span>'


# ─────────────────────────────────────────
# AUTH PAGES
# ─────────────────────────────────────────

if st.session_state.token is None:

    # ── Sidebar brand
    st.sidebar.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-size:2.4rem;">🏥</div>
        <div style="font-size:1.2rem; font-weight:700; margin-top:4px;">MediCare</div>
        <div style="font-size:0.78rem; opacity:0.7; margin-top:2px;">Clinic Management</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio("", ["🔐  Login", "📝  Register"], label_visibility="collapsed")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # ── Hero
    st.markdown("""
    <div class="hero">
        <h1>🏥 MediCare Clinic Portal</h1>
        <p>Seamless appointment scheduling, medical records & patient management — all in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    # ────── REGISTER ──────
    if "Register" in menu:

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 📝 Create your account")
            st.markdown("<br>", unsafe_allow_html=True)

            full_name = st.text_input("Full Name", placeholder="Dr. Jane Smith")
            email     = st.text_input("Email", placeholder="jane@clinic.com")
            phone     = st.text_input("Phone", placeholder="+91 98765 43210")
            password  = st.text_input("Password", type="password", placeholder="••••••••")

            role = st.selectbox(
                "I am a …",
                ["patient", "doctor", "admin"],
                format_func=lambda x: {"patient": "🧑‍🤝‍🧑 Patient", "doctor": "🩺 Doctor", "admin": "⚙️ Admin"}[x],
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True):
                if not all([full_name, email, phone, password]):
                    st.warning("Please fill in all fields.")
                else:
                    resp = requests.post(f"{BASE_URL}/auth/register", json={
                        "full_name": full_name, "email": email,
                        "phone": phone, "password": password, "role": role,
                    })
                    if resp.status_code == 201:
                        st.success("🎉 Account created! Head to Login to get started.")
                    else:
                        st.error(resp.text)

            st.markdown("</div>", unsafe_allow_html=True)

    # ────── LOGIN ──────
    else:

        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 🔐 Sign in to your account")
            st.markdown("<br>", unsafe_allow_html=True)

            email    = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Sign In →", use_container_width=True):
                resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.token   = data["access_token"]
                    st.session_state.role    = data["role"]
                    st.session_state.user_id = data["user_id"]
                    st.success("✅ Signed in! Redirecting …")
                    st.rerun()
                else:
                    st.error("❌ Incorrect email or password. Please try again.")

            st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────

else:

    headers = get_headers()

    profile_resp = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if profile_resp.status_code != 200:
        st.error("⚠️ Session expired. Please log in again.")
        st.stop()

    profile = profile_resp.json()
    role    = st.session_state.role

    # ── Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align:center; padding:20px 10px 10px;">
        <div style="font-size:2.6rem;">{'🩺' if role=='doctor' else '🧑‍🤝‍🧑' if role=='patient' else '⚙️'}</div>
        <div style="font-size:1rem; font-weight:700; margin-top:6px;">{profile['full_name']}</div>
        <div style="margin-top:4px;">{role_badge(role)}</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    nav_options = ["🏠 Overview", "👤 Profile", "🩺 Doctors", "📅 Appointments", "📋 Records"]
    if role == "admin":
        nav_options.append("⚙️ Admin")

    page = st.sidebar.radio("Navigation", nav_options, label_visibility="collapsed")

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        for k in ("token", "role", "user_id"):
            st.session_state[k] = None
        st.rerun()

    st.sidebar.markdown("""
    <div style="font-size:0.72rem; opacity:0.55; text-align:center; margin-top:20px; padding:0 10px;">
        MediCare v2.0 · Powered by FastAPI
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════
    # OVERVIEW
    # ══════════════════════════════════

    if "Overview" in page:

        st.markdown(f"""
        <div class="hero">
            <h1>Good day, {profile['full_name'].split()[0]}! 👋</h1>
            <p>Here's a snapshot of what's happening in your clinic today.</p>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats
        appt_resp = requests.get(f"{BASE_URL}/appointments/", headers=headers)
        rec_resp  = requests.get(f"{BASE_URL}/records/",      headers=headers)
        doc_resp  = requests.get(f"{BASE_URL}/doctors/",      headers=headers)

        appts   = appt_resp.json()  if appt_resp.status_code  == 200 else []
        records = rec_resp.json()   if rec_resp.status_code   == 200 else []
        doctors = doc_resp.json()   if doc_resp.status_code   == 200 else []

        c1, c2, c3, c4 = st.columns(4)

        def stat_card(col, icon, label, value, color):
            col.markdown(f"""
            <div class="metric-card" style="border-left-color:{color};">
                <div style="font-size:1.8rem;">{icon}</div>
                <div style="font-size:1.7rem; font-weight:700; color:{color}; margin:4px 0;">{value}</div>
                <div style="font-size:0.82rem; color:#64748b;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        stat_card(c1, "📅", "My Appointments",  len(appts),   "#3b82f6")
        stat_card(c2, "📋", "Medical Records",  len(records), "#10b981")
        stat_card(c3, "🩺", "Available Doctors", len(doctors), "#8b5cf6")
        stat_card(c4, "✅", "Confirmed Appts",
                  len([a for a in appts if a.get("status") == "confirmed"]), "#f59e0b")

        if appts:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">📅 Recent Appointments</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Your latest 5 scheduled visits</div>', unsafe_allow_html=True)
            df = pd.DataFrame(appts).head(5)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ══════════════════════════════════
    # PROFILE
    # ══════════════════════════════════

    elif "Profile" in page:

        st.markdown('<div class="section-header">👤 My Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Your account details</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([1, 2])

        with c1:
            icon = "🩺" if role == "doctor" else ("⚙️" if role == "admin" else "🧑‍🤝‍🧑")
            st.markdown(f"""
            <div class="info-card" style="text-align:center; padding:36px 20px;">
                <div style="font-size:4rem;">{icon}</div>
                <div style="font-size:1.25rem; font-weight:700; margin-top:10px;">{profile['full_name']}</div>
                <div style="margin-top:8px;">{role_badge(role)}</div>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:8px;">{profile.get('email','')}</div>
                <div style="color:#94a3b8; font-size:0.85rem;">{profile.get('phone','')}</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("#### Account Information")
            st.divider()

            fields = [
                ("Full Name",  profile.get("full_name", "—")),
                ("Email",      profile.get("email",     "—")),
                ("Phone",      profile.get("phone",     "—")),
                ("Role",       profile.get("role",      "—").capitalize()),
                ("User ID",    profile.get("id",        "—")),
            ]

            for label, value in fields:
                fc1, fc2 = st.columns([1, 2])
                fc1.markdown(f"**{label}**")
                fc2.markdown(str(value))

            st.markdown("</div>", unsafe_allow_html=True)

    # ══════════════════════════════════
    # DOCTORS
    # ══════════════════════════════════

    elif "Doctors" in page:

        st.markdown('<div class="section-header">🩺 Doctors Directory</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">All registered doctors and their availability</div>', unsafe_allow_html=True)

        doc_resp = requests.get(f"{BASE_URL}/doctors/", headers=headers)

        if doc_resp.status_code == 200:
            doctors = doc_resp.json()
            if doctors:
                df = pd.DataFrame(doctors)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Small summary metrics
                col1, col2 = st.columns(2)
                col1.metric("Total Doctors", len(doctors))
                if "specialization" in df.columns:
                    col2.metric("Specializations", df["specialization"].nunique())
            else:
                st.info("🔍 No doctors registered yet.")
        else:
            st.error("Could not load doctors.")

        # Doctor profile creation
        if role == "doctor":
            st.markdown("---")
            st.markdown('<div class="section-header">➕ Create Doctor Profile</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-sub">Set up your professional details and availability</div>', unsafe_allow_html=True)

            with st.form("doctor_profile_form"):
                c1, c2 = st.columns(2)

                with c1:
                    specialization = st.text_input("Specialization 🏷️", placeholder="Cardiology")
                    fee = st.number_input("Consultation Fee (₹) 💰", min_value=0, step=50)
                    duration = st.number_input("Slot Duration (mins) ⏱️", value=30, step=5)

                with c2:
                    available_days = st.multiselect(
                        "Available Days 📆",
                        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                        default=["Monday","Tuesday","Wednesday","Thursday","Friday"],
                    )
                    start_time = st.text_input("Start Time 🌅", "09:00")
                    end_time   = st.text_input("End Time 🌇", "17:00")

                submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

                if submitted:
                    resp = requests.post(f"{BASE_URL}/doctors/profile", headers=headers, json={
                        "specialization": specialization,
                        "consultation_fee": fee,
                        "available_days": available_days,
                        "start_time": start_time,
                        "end_time": end_time,
                        "slot_duration": duration,
                    })
                    if resp.ok:
                        st.success("✅ Doctor profile saved successfully!")
                    else:
                        st.error(resp.text)

    # ══════════════════════════════════
    # APPOINTMENTS
    # ══════════════════════════════════

    elif "Appointments" in page:

        st.markdown('<div class="section-header">📅 Appointments</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">View and manage your scheduled appointments</div>', unsafe_allow_html=True)

        appt_resp = requests.get(f"{BASE_URL}/appointments/", headers=headers)

        tab1, tab2 = (st.tabs(["📋 My Appointments", "➕ Book New"]) if role == "patient"
                      else st.tabs(["📋 Appointments", "🗑️ Cancel"]))

        with tab1:
            if appt_resp.status_code == 200:
                appointments = appt_resp.json()
                if appointments:
                    df = pd.DataFrame(appointments)

                    # Status colour hint
                    status_icons = {"confirmed": "✅", "pending": "⏳", "cancelled": "❌"}

                    if "status" in df.columns:
                        df["status"] = df["status"].apply(
                            lambda s: f"{status_icons.get(s, '❓')} {s.capitalize()}"
                        )

                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.caption(f"Showing {len(appointments)} appointment(s)")
                else:
                    st.info("📭 No appointments yet. Book one using the tab above!")
            else:
                st.error("Could not load appointments.")

        with tab2:
            if role == "patient":
                st.markdown("#### Book a New Appointment")

                doc_resp = requests.get(f"{BASE_URL}/doctors/", headers=headers)
                doctors  = doc_resp.json() if doc_resp.ok else []

                if doctors:
                    with st.form("book_appointment"):
                        doctor_map = {d["full_name"]: d["id"] for d in doctors}

                        selected_doctor = st.selectbox("Select Doctor 🩺", list(doctor_map.keys()))
                        c1, c2 = st.columns(2)
                        selected_date = c1.date_input("Date 📆", min_value=datetime.today().date())
                        selected_time = c2.time_input("Time ⏰")
                        reason = st.text_area("Reason for Visit 📝", placeholder="Brief description of symptoms…")

                        if st.form_submit_button("📩 Book Appointment", use_container_width=True):
                            resp = requests.post(f"{BASE_URL}/appointments/", headers=headers, json={
                                "doctor_id":    doctor_map[selected_doctor],
                                "scheduled_at": f"{selected_date}T{selected_time}",
                                "reason":       reason,
                            })
                            if resp.ok:
                                st.success("🎉 Appointment booked successfully!")
                            else:
                                st.error(resp.text)
                else:
                    st.warning("No doctors available to book with right now.")

            else:
                st.markdown("#### Cancel an Appointment")
                with st.form("cancel_form"):
                    appointment_id = st.text_input("Appointment ID 🆔", placeholder="Enter the appointment ID")
                    if st.form_submit_button("🗑️ Cancel Appointment", use_container_width=True):
                        resp = requests.delete(f"{BASE_URL}/appointments/{appointment_id}", headers=headers)
                        if resp.ok:
                            st.success("✅ Appointment cancelled.")
                        else:
                            st.error(resp.text)

    # ══════════════════════════════════
    # RECORDS
    # ══════════════════════════════════

    elif "Records" in page:

        st.markdown('<div class="section-header">📋 Medical Records</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Health history and clinical notes</div>', unsafe_allow_html=True)

        rec_resp = requests.get(f"{BASE_URL}/records/", headers=headers)

        if rec_resp.status_code == 200:
            records = rec_resp.json()
            if records:
                st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
                st.caption(f"Total records: {len(records)}")
            else:
                st.info("📭 No medical records found.")
        else:
            st.error("Could not load records.")

        if role == "doctor":
            st.markdown("---")
            st.markdown('<div class="section-header">📝 Add Medical Record</div>', unsafe_allow_html=True)
            

            with st.form("create_record"):
                patient_id = st.text_input("Patient ID 🆔", placeholder="Enter patient's user ID")
                diagnosis  = st.text_area("Diagnosis 🔬", placeholder="Clinical findings…")
                treatment  = st.text_area("Treatment Plan 💊", placeholder="Prescribed medications, procedures…")

                if st.form_submit_button("💾 Save Record", use_container_width=True):
                    resp = requests.post(f"{BASE_URL}/records/", headers=headers, json={
                        "patient_id": patient_id,
                        "diagnosis":  diagnosis,
                        "treatment":  treatment,
                    })
                    if resp.ok:
                        st.success("✅ Medical record saved!")
                    else:
                        st.error(resp.text)

    # ══════════════════════════════════
    # ADMIN
    # ══════════════════════════════════

    elif "Admin" in page:

        if role != "admin":
            st.error("🚫 Admin access only.")
            st.stop()

        st.markdown('<div class="section-header">⚙️ Admin Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Manage all platform users</div>', unsafe_allow_html=True)

        user_resp = requests.get(f"{BASE_URL}/users/", headers=headers)

        if user_resp.status_code == 200:
            users = user_resp.json()

            if users:
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Users", len(users))
                col2.metric("Patients", len([u for u in users if u.get("role") == "patient"]))
                col3.metric("Doctors",  len([u for u in users if u.get("role") == "doctor"]))

                st.markdown("<br>", unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
            else:
                st.info("No users found.")
        else:
            st.error("Could not load users.")

        st.markdown("---")
        st.markdown("#### 🗑️ Remove User")

        with st.form("delete_user"):
            user_id = st.text_input("User ID to Delete", placeholder="Paste the user ID here")
            confirm = st.checkbox("I understand this action is permanent")

            if st.form_submit_button("Delete User", use_container_width=True):
                if not confirm:
                    st.warning("⚠️ Please confirm before deleting.")
                elif not user_id:
                    st.warning("Please provide a user ID.")
                else:
                    resp = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
                    if resp.status_code in [200, 204]:
                        st.success("✅ User removed successfully.")
                    else:
                        st.error(resp.text)
