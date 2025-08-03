from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    remove_bg_api_key: str
    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_password: str
    auth_code: str

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
    