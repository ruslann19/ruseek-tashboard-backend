from dotenv import dotenv_values


class Settings:
    def __init__(self):
        config = dotenv_values(".env")
        self.OPENROUTER_API_KEY = config["OPENROUTER_API_KEY"]
        self.DEEPSEEK_API_KEY = config["DEEPSEEK_API_KEY"]
        # self.GIGACHAT_API_KEY = config["GIGACHAT_API_KEY"]

        db_name = config["DB_NAME"]
        db_host = config["DB_HOST"]
        db_port = config["DB_PORT"]
        db_user = config["DB_USER"]
        db_password = config["DB_PASSWORD"]

        self.DB_URL = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings()
