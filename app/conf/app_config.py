"""
应用主配置。

从项目根目录加载 .env 与 conf/app_config.yaml，并转换为类型化配置对象。
"""

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf


@dataclass
class File:
    """文件日志配置。"""

    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    """控制台日志配置。"""

    enable: bool
    level: str


@dataclass
class LoggingConfig:
    """日志总配置。"""

    file: File
    console: Console


@dataclass
class DBConfig:
    """MySQL 连接配置。"""

    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class QdrantConfig:
    """Qdrant 连接配置。"""

    host: str
    port: int
    embedding_size: int


@dataclass
class EmbeddingConfig:
    """Embedding 服务配置。"""

    host: str
    port: int
    model: str


@dataclass
class ESConfig:
    """Elasticsearch 配置。"""

    host: str
    port: int
    index_name: str


@dataclass
class LLMConfig:
    """大模型调用配置。"""

    model_name: str
    api_key: str
    base_url: str


@dataclass
class SQLSafetyConfig:
    """SQL 查询安全策略。"""

    max_length: int
    max_result_rows: int
    max_correction_attempts: int
    max_execution_time_ms: int


@dataclass
class AppConfig:
    """项目级总配置入口。"""

    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig
    sql_safety: SQLSafetyConfig


project_root = Path(__file__).parents[2]
config_file = project_root / "conf" / "app_config.yaml"
load_dotenv(project_root / ".env")
context = OmegaConf.load(config_file)
schema = OmegaConf.structured(AppConfig)
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

if __name__ == "__main__":
    print(app_config.es.host)
