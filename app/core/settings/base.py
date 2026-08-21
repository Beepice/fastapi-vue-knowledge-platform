from enum import Enum

from pydantic_settings import BaseSettings
from pydantic import SecretStr


class AppEnvTypes(Enum):
    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"

class BaseAppSettings(BaseSettings):
    app_env: AppEnvTypes = AppEnvTypes.prod
    debug: bool | None = None
    database_url: str | None = None
    secret_key: str | None = None

    qwen_api_key: SecretStr
    qwen_embedding_model:str = "text-embedding-v4"
    qwen_api_url:str = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    qwen_question_model:str = "qwen3.5-plus"
    qwen_3_5_plus_url:str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    class Config:
        env_file = ".env"
