from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    GROQ_API_KEY: str
    MISTRAL_API_KEY: str
    GOOGLE_API_KEY: str

    GROQ_MODEL: str
    MISTRAL_MODEL: str
    GEMINI_MODEL: str

    class Config:
        env_file = ".env"


settings = Settings()