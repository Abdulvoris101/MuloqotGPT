from typing import Listfrom aiogram.enums import chat_typefrom pydantic_settings import BaseSettings, SettingsConfigDictimport osfrom dotenv import load_dotenvload_dotenv()class Settings(BaseSettings):    API_KEY: str    BOT_TOKEN: str    PASSWORD: str    BOT_USERNAME: str = "muloqotgpt_bot"    HOST_GROUP_ID: int = -1001941889065    IMAGE_GEN_GROUP_ID: int = -1002143676390    COMMENTS_GROUP_ID: int = -1002112530699    SUBSCRIPTION_CHANNEL_ID: int = -4112946370    REQUIRED_CHANNEL_ID: int = -1001515179618    ERROR_CHANNEL_ID: int = -1001980262190    EVENT_CHANNEL_ID: int = -1002132597784    ALLOWED_GROUPS: List[int] = [HOST_GROUP_ID, IMAGE_GEN_GROUP_ID]    AVAILABLE_GROUP_TYPES: List[chat_type.ChatType] = [chat_type.ChatType.GROUP,                                                       chat_type.ChatType.SUPERGROUP]    IMAGE_GENERATION_WORDS: List[str] = ["generate", "imagine"]    WEB_URL: str    ENV_DIR: str    DB_URL: str    REDIS_URL: str    POSTGRES_DB_USER: str    POSTGRES_DB_PASSWORD: str    REDIS_HOST: str    POSTGRES_TIMEZONE: str = "Asia/Tashkent"    class Config:        env_file = os.environ.get("ENV_DIR")        env_file_encoding = 'utf-8'settings = Settings()