"""MySQL 异步客户端管理器。"""

import asyncio

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.conf.app_config import DBConfig, app_config


class MySQLClientManager:
    """管理 MySQL Engine 和 Session 工厂。"""

    def __init__(self, config: DBConfig):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker | None = None
        self.config = config

    def _get_url(self) -> URL:
        """使用 URL.create 安全处理密码中的特殊字符。"""

        return URL.create(
            drivername="mysql+asyncmy",
            username=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database,
            query={"charset": "utf8mb4"},
        )

    def init(self) -> None:
        """初始化 Engine 和 Session 工厂；重复调用不会重复创建连接池。"""

        if self.engine is not None:
            return
        self.engine = create_async_engine(
            self._get_url(), pool_size=10, pool_pre_ping=True
        )
        self.session_factory = async_sessionmaker(
            self.engine, autoflush=True, expire_on_commit=False
        )

    async def close(self) -> None:
        """释放连接池资源。"""

        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None


meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)

if __name__ == "__main__":
    dw_mysql_client_manager.init()

    async def test():
        """执行一次简单查询，验证 MySQL 连接与结果结构。"""

        assert dw_mysql_client_manager.session_factory is not None
        async with dw_mysql_client_manager.session_factory() as session:
            result = await session.execute(text("SELECT * FROM fact_order LIMIT 10"))
            rows = result.mappings().fetchall()
            print(type(rows), type(rows[0]), rows[0]["order_id"])

    asyncio.run(test())
