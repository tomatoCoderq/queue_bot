from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent


class SQLiteSettings(BaseSettings):
    
    DB_NAME: str = Field(default="app.db")
    DB_URL: str = Field(default="-1")
    
    @field_validator("DB_URL", mode="before")
    def assemble_async_db_connection(cls, v, values):
        if isinstance(v, str):
            return v
        info = values.data
        return (
            f"sqlite+aiosqlite:///{PROJECT_ROOT / info['DB_NAME']}"
        )
        
# class DatabaseSettings(BaseSettings):
#     DB_DB: str = Field(default="findar")
#     DB_USER: str = Field(default="postgres")
#     DB_PASSWORD: str = Field(default="postgres")
#     DB_HOST: str = Field(default="localhost")
#     DB_PORT: int = Field(default=5432)
#     DB_URL: Optional[str] = Field(default=None)
    
#     @field_validator("DB_URL", mode="before")
#     def assemble_async_db_connection(cls, v, values):
#         if isinstance(v, str):
#             return v
#         info = values.data
#         return (
            
#             f"postgresql://{info['DB_USER']}:"
#             f"{info['DB_PASSWORD']}@"
#             f"{info['DB_HOST']}:"
#             f"{info['DB_PORT']}/"
#             f"{info['DB_DB']}"
#         )

#     model_config = SettingsConfigDict(
#         env_file=str(PROJECT_ROOT / ".env"),
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#         extra="ignore",
#     )
    
class APISettings(BaseSettings):
    API_HOST: str = Field(default="localhost")
    API_PORT: int = Field(default=8000)
    
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

class TelegramSettings(BaseSettings):
    TOKEN: str = Field(default="invalid_token")
    ADMIN_ID: int = Field(default=0)
    
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

class Settings(BaseSettings):
    database: SQLiteSettings = SQLiteSettings()
    api: APISettings = APISettings()
    telegram: TelegramSettings = TelegramSettings()
    
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()