import tomllib
from functools import cached_property
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from worklog.log import get_logger

log = get_logger(__name__)


PROJECT_DIR = Path(__file__).parent.parent
log.info(f"PROJECT_DIR: {PROJECT_DIR}")
with open(f"{PROJECT_DIR}/pyproject.toml", "rb") as f:
    PYPROJECT_CONTENT = tomllib.load(f)["tool"]["poetry"]


class Settings(BaseSettings):
    SECRET_KEY: str
    ENVIRONMENT: Literal["DEV", "TEST", "PROD"] = "DEV"
    ALGORITHM: str = "HS256"
    SECURITY_BCRYPT_ROUNDS: int = 12
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]

    PROJECT_NAME: str = PYPROJECT_CONTENT["name"]
    VERSION: str = PYPROJECT_CONTENT["version"]
    DESCRIPTION: str = PYPROJECT_CONTENT["description"]

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    TEST_POSTGRES_HOST: str = "postgres"
    TEST_POSTGRES_USER: str = "postgres"
    TEST_POSTGRES_PASSWORD: str = "postgres"
    TEST_POSTGRES_PORT: int = 5432
    TEST_POSTGRES_DB: str = "postgres"

    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    @computed_field
    @cached_property
    def DEFAULT_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.DEFAULT_DATABASE_USER,
                password=self.DEFAULT_DATABASE_PASSWORD,
                host=self.DEFAULT_DATABASE_HOSTNAME,
                port=self.DEFAULT_DATABASE_PORT,
                path=self.DEFAULT_DATABASE_DB,
            )
        )

    @computed_field
    @cached_property
    def TEST_SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.TEST_DATABASE_USER,
                password=self.TEST_DATABASE_PASSWORD,
                host=self.TEST_DATABASE_HOSTNAME,
                port=self.TEST_DATABASE_PORT,
                path=self.TEST_DATABASE_DB,
            )
        )

    def resolve_database_url(self) -> str:
        log.debug("Resolving database URL based on ENVIRONMENT %s", self.ENVIRONMENT)
        if self.ENVIRONMENT == "TEST":
            return self.TEST_SQLALCHEMY_DATABASE_URI
        if self.ENVIRONMENT == "DEV" or self.ENVIRONMENT == "PROD":
            return self.DEFAULT_SQLALCHEMY_DATABASE_URI
        log.debug(
            "Invalid environment %s. Available: DEV, TEST, PROD", self.ENVIRONMENT
        )
        raise ValueError("Invalid environment")

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env", case_sensitive=True
    )


settings: Settings = Settings()  # type: ignore
