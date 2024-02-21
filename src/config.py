from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    'config',
)


class DataBaseConfig:
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    ECHO: bool

    @property
    def default_asyncpg_url(self) -> str:
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Config(DataBaseConfig, BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")


config = Config()
