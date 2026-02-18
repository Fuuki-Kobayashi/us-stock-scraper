from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POLYGON_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///data/stocks.db"
    SURGE_THRESHOLD_PCT: float = 20.0

    model_config = {
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
