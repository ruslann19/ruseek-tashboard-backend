import os

from dotenv import load_dotenv

load_dotenv()


class RunningModes:
    def __init__(self):
        self.dev = "dev"
        self.prod = "prod"

    @property
    def values(self):
        return list(self.__dict__.values())


running_modes = RunningModes()


class Settings:
    def __init__(self):
        self.RUNNING_MODE = os.getenv("RUNNING_MODE")

        self.FRONTEND_HOST = os.getenv("FRONTEND_HOST")

        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        self.ROUTERAI_API_KEY = os.getenv("ROUTERAI_API_KEY")

        db_name = os.getenv("DB_NAME")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        self.DB_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings()


# RUNNING_MODE должен соответствовать определённому значению из списка
assert settings.RUNNING_MODE in running_modes.values
