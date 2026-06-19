-- ============================================
-- CLINIC APPOINTMENT MANAGEMENT SYSTEM
-- Supabase SQL Schema
-- Run this in your Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── USERS TABLE ──────────────────────────────
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,                   -- bcrypt hashed
    full_name   TEXT NOT NULL,
    phone       TEXT,
    role        TEXT NOT NULL DEFAULT 'patient'  -- 'patient' | 'doctor' | 'admin'
                CHECK (role IN ('patient', 'doctor', 'admin')),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── DOCTORS TABLE ─────────────────────────────
CREATE TABLE doctors (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialization  TEXT NOT NULL,
    bio             TEXT,
    available_days  TEXT[] DEFAULT ARRAY['Monday','Tuesday','Wednesday','Thursday','Friday'],
    start_time      TIME DEFAULT '09:00',        -- daily start time
    end_time        TIME DEFAULT '17:00',        -- daily end time
    slot_duration   INT DEFAULT 30,              -- minutes per appointment
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── APPOINTMENTS TABLE ────────────────────────
CREATE TABLE appointments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id       UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    scheduled_at    TIMESTAMPTZ NOT NULL,
    duration_mins   INT DEFAULT 30,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'confirmed', 'cancelled', 'completed')),
    reason          TEXT,
    notes           TEXT,                        -- doctor's notes (set on completion)
    reminder_sent   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    -- Prevent double-booking: same doctor, same time slot
    UNIQUE (doctor_id, scheduled_at)
);

-- ── MEDICAL RECORDS TABLE ─────────────────────
CREATE TABLE medical_records (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id       UUID NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_id  UUID REFERENCES appointments(id) ON DELETE SET NULL,
    diagnosis       TEXT NOT NULL,
    prescription    TEXT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── INDEXES ───────────────────────────────────
CREATE INDEX idx_appointments_patient   ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor    ON appointments(doctor_id);
CREATE INDEX idx_appointments_status    ON appointments(status);
CREATE INDEX idx_appointments_time      ON appointments(scheduled_at);
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id);

-- ── ROW LEVEL SECURITY (RLS) ──────────────────
-- Disable RLS since we use service-role key from backend
-- (Enable and customize if you prefer RLS-based access control)
ALTER TABLE users            DISABLE ROW LEVEL SECURITY;
ALTER TABLE doctors          DISABLE ROW LEVEL SECURITY;
ALTER TABLE appointments     DISABLE ROW LEVEL SECURITY;
ALTER TABLE medical_records  DISABLE ROW LEVEL SECURITY;
