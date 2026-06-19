"""
Appointment Reminder Scheduler
Runs a background job every 15 minutes that flags appointments
scheduled within the next hour as reminder_sent=True.

In production, replace the print() calls with email/SMS sending
(e.g. SendGrid, Twilio, Supabase Edge Functions).
"""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from app.database import supabase


def send_reminders():
    """Find upcoming appointments and mark reminders sent."""
    now = datetime.now(timezone.utc)
    window_start = now.isoformat()
    window_end   = (now + timedelta(hours=1)).isoformat()

    result = (
        supabase.table("appointments")
        .select("id, patient_id, doctor_id, scheduled_at")
        .eq("status", "confirmed")
        .eq("reminder_sent", False)
        .gte("scheduled_at", window_start)
        .lte("scheduled_at", window_end)
        .execute()
    )

    for appt in (result.data or []):
        # TODO: replace with real email/SMS integration
        print(
            f"[REMINDER] Appointment {appt['id']} "
            f"for patient {appt['patient_id']} "
            f"at {appt['scheduled_at']}"
        )
        supabase.table("appointments").update({"reminder_sent": True}).eq("id", appt["id"]).execute()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(send_reminders, "interval", minutes=15, id="reminder_job")
    scheduler.start()
    return scheduler
