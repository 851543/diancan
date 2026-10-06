"""配置：从项目根目录 .env 读取。"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# core -> app -> backend -> 项目根
ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "production"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "diancan"
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440
    jwt_algorithm: str = "HS256"
    cors_origins: str = ""
    admin_username: str = ""
    admin_password: str = ""

    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.app_env.strip().lower() == "production"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [x.strip() for x in self.cors_origins.split(",") if x.strip()]
        if origins:
            return origins
        if self.is_production:
            return []
        return ["*"]


settings = Settings()
