from supabase import create_client, Client
from app.config import settings

# Use the service role key so our backend can bypass RLS
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)
