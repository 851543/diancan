"""
配置：从 .env 读数据库、Redis、JWT。
Java 对照：类似 Spring 的 application.yml + @ConfigurationProperties。
"""

# Path 用来拼文件路径，跨 Windows/Linux。Java 对照：Paths.get(...)
from pathlib import Path

# BaseSettings：声明配置字段后，自动从环境变量 / .env 填充。
from pydantic_settings import BaseSettings, SettingsConfigDict

# __file__ = 当前这个 config.py 的路径
# .resolve() = 变成绝对路径
# .parents[2] = 往上两级：app -> backend -> 项目根 diancan
# 所以 ROOT 指向 C:\Users\阿俊\diancan
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    每个字段名会对应环境变量：
      mysql_host  <-  MYSQL_HOST
    没配环境变量时，用等号右边的默认值。
    Java 对照：private String mysqlHost = "127.0.0.1";
    """

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "diancan"
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 1440  # 24 小时
    jwt_algorithm: str = "HS256"

    # 告诉 pydantic：去项目根目录读 .env；多余的键忽略，不要报错
    model_config = SettingsConfigDict(env_file=str(ROOT / ".env"), extra="ignore")

    @property  # 当属性用：settings.database_url，不用写成 settings.database_url()
    def database_url(self) -> str:
        """
        拼 SQLAlchemy 连接串。
        Java 对照：jdbc:mysql://host:port/db
        Python 这边驱动名是 mysql+pymysql。
        f"..." 是格式化字符串，类似 Java 的 String.format 或用 + 拼接。
        """
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


# 整个项目共用这一份配置（单例）。Java 对照：@Bean 注入的一份 AppProperties。
settings = Settings()
