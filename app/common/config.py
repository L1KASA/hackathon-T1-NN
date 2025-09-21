from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    LOG_LEVEL: Annotated[str, Field(validation_alias="LOG_LEVEL")]

    POSTGRES_USER: Annotated[str, Field(validation_alias="POSTGRES_USER")]
    POSTGRES_PASSWORD: Annotated[str, Field(validation_alias="POSTGRES_PASSWORD")]
    POSTGRES_DB: Annotated[str, Field(validation_alias="POSTGRES_DB")]
    POSTGRES_HOST: Annotated[str, Field(validation_alias="POSTGRES_HOST")]
    POSTGRES_PORT: Annotated[int, Field(validation_alias="POSTGRES_PORT")]

    MAX_SKILLS_FOR_EMPLOYEE: Annotated[int, Field(validation_alias="MAX_SKILLS_FOR_EMPLOYEE")]

    @property
    def database_url(self) -> str:
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

settings = Settings()
