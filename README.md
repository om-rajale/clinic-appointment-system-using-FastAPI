# 🏥 Clinic Appointment Management System

A clean **FastAPI + Supabase** REST API for managing clinic appointments, doctor schedules, patient records, and automated reminders — secured with JWT authentication.

---

## Features

| Feature | Description |
|---|---|
| 🔐 JWT Auth | Register / Login with role-based access (patient, doctor, admin) |
| 👨‍⚕️ Doctor Scheduling | Doctors set their specialization, working hours, and slot duration |
| 📅 Appointment Booking | Patients book slots; double-booking prevented at DB level |
| 🔔 Reminders | Background job flags upcoming appointments every 15 minutes |
| 🗂️ Medical Records | Doctors create records linked to patients and appointments |
| 📖 Auto Docs | Swagger UI at `/docs` and ReDoc at `/redoc` |

---

## Tech Stack

- **FastAPI** — modern async Python web framework
- **Supabase** — PostgreSQL database + REST API (via `supabase-py`)
- **JWT** — stateless authentication (`python-jose`)
- **bcrypt** — password hashing (`passlib`)
- **APScheduler** — background reminder job

---

## Project Structure

```
clinic-api/
├── app/
│   ├── main.py            # FastAPI app + lifespan
│   ├── config.py          # Settings from .env
│   ├── database.py        # Supabase client
│   ├── schemas.py         # Pydantic request/response models
│   ├── routers/
│   │   ├── auth.py        # /auth/register, /auth/login
│   │   ├── users.py       # /users/me, /users/ (admin)
│   │   ├── doctors.py     # /doctors/ + /slots
│   │   ├── appointments.py# /appointments/ CRUD
│   │   └── records.py     # /records/ CRUD
│   └── utils/
│       ├── auth.py        # JWT helpers + dependencies
│       └── reminders.py   # Background scheduler
├── supabase_schema.sql    # Paste into Supabase SQL editor
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Set up Supabase

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste the contents of `supabase_schema.sql` → **Run**
3. Go to **Project Settings → API** and copy:
   - Project URL
   - `anon` key
   - `service_role` key

### 2. Configure environment

```bash
cp .env.example .env
# Fill in your Supabase credentials and a strong JWT_SECRET_KEY
```

### 3. Install & run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit **http://localhost:8000/** for the web UI, or **http://localhost:8000/docs** for the interactive API explorer.

---

## API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register (patient/doctor/admin) |
| POST | `/auth/login` | Login → returns JWT token |

### Users
| Method | Endpoint | Who |
|---|---|---|
| GET | `/users/me` | Any logged-in user |
| GET | `/users/` | Admin only |
| DELETE | `/users/{id}` | Admin only |

### Doctors
| Method | Endpoint | Who |
|---|---|---|
| POST | `/doctors/profile` | Doctor creates profile |
| GET | `/doctors/` | Any logged-in user |
| GET | `/doctors/{id}` | Any logged-in user |
| PATCH | `/doctors/profile` | Doctor updates own profile |
| GET | `/doctors/{id}/slots?date=YYYY-MM-DD` | View free slots |

### Appointments
| Method | Endpoint | Who |
|---|---|---|
| POST | `/appointments/` | Patient books |
| GET | `/appointments/my` | Patient sees own |
| GET | `/appointments/schedule` | Doctor sees theirs |
| GET | `/appointments/` | Admin sees all |
| PATCH | `/appointments/{id}` | Doctor confirms/completes; Patient cancels |
| DELETE | `/appointments/{id}` | Patient cancels |

### Medical Records
| Method | Endpoint | Who |
|---|---|---|
| POST | `/records/` | Doctor creates |
| GET | `/records/my` | Patient sees own |
| GET | `/records/patient/{id}` | Doctor/Admin |
| GET | `/records/{id}` | Patient (own) / Doctor / Admin |
| DELETE | `/records/{id}` | Admin only |

---

## Roles & Permissions

```
patient  → book & cancel appointments, view own records
doctor   → manage profile, confirm/complete appointments, create records
admin    → full read access, delete users/records
```

---

## Appointment Reminder

The app checks every **15 minutes** for `confirmed` appointments in the next hour and marks them as `reminder_sent = true`. 

To hook up real notifications, edit `app/utils/reminders.py` and replace the `print()` calls with:
- **Email**: SendGrid, Resend, or Supabase Edge Functions
- **SMS**: Twilio
- **Push**: Firebase Cloud Messaging

---

## Using the API (example flow)

```bash
# 1. Register a patient
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123","full_name":"Alice","role":"patient"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"secret123"}'
# → copy the access_token

# 3. Check available slots
curl http://localhost:8000/doctors/{doctor_id}/slots?date=2025-07-01 \
  -H "Authorization: Bearer <token>"

# 4. Book an appointment
curl -X POST http://localhost:8000/appointments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"doctor_id":"...","scheduled_at":"2025-07-01T10:00:00","reason":"Checkup"}'
```
