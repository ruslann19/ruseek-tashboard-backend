import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
        self.DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
        # self.GIGACHAT_API_KEY = config["GIGACHAT_API_KEY"]

        db_name = os.getenv("DB_NAME")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")

        self.DB_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings()
