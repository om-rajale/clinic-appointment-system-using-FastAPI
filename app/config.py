from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_service_key: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    app_name: str = "Clinic Appointment System"
    debug: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
