from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "topicos"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
