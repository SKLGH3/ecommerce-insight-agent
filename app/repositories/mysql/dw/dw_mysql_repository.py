"""数仓 MySQL 仓储。

所有由模型生成的 SQL 都在这里进行二次只读校验，并受到执行时长和返回行数限制。
"""

import re
from collections.abc import Collection

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf.app_config import app_config
from app.security.sql_guard import SQLGuardPolicy, guard_read_only_sql

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_$]*$")


class DWMySQLRepository:
    """负责读取数仓结构、校验 SQL，并安全执行只读查询。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        """校验并引用元数据标识符，防止表名或字段名注入。"""

        if not _IDENTIFIER_PATTERN.fullmatch(identifier):
            raise ValueError(f"非法数据库标识符：{identifier!r}")
        return f"`{identifier}`"

    async def get_column_types(self, table_name: str) -> dict[str, str]:
        """查询整张表的字段类型，作为 ColumnInfo.type 的真实来源。"""

        table = self._quote_identifier(table_name)
        result = await self.session.execute(text(f"SHOW COLUMNS FROM {table}"))
        return {row["Field"]: row["Type"] for row in result.mappings().fetchall()}

    async def get_column_values(
        self, table_name: str, column_name: str, limit: int = 10
    ) -> list:
        """抽样查询字段示例值，供元数据入库和检索链路复用。"""

        table = self._quote_identifier(table_name)
        column = self._quote_identifier(column_name)
        safe_limit = min(max(int(limit), 1), app_config.sql_safety.max_result_rows)
        sql = text(f"SELECT DISTINCT {column} FROM {table} LIMIT :limit")
        result = await self.session.execute(sql, {"limit": safe_limit})
        return [row[0] for row in result.fetchall()]

    async def get_db_info(self) -> dict[str, str]:
        """读取当前数仓数据库的方言和版本，供 SQL 生成提示词使用。"""

        result = await self.session.execute(text("SELECT VERSION()"))
        version = str(result.scalar())
        if self.session.bind is None:
            raise RuntimeError("数据库 Session 尚未绑定 Engine")
        return {"dialect": self.session.bind.dialect.name, "version": version}

    async def validate(self, sql: str) -> None:
        """用 EXPLAIN 让数据库提前发现语法、表名和字段名错误。"""

        await self.session.execute(text(f"EXPLAIN {sql}"))

    async def run(
        self, sql: str, *, allowed_tables: Collection[str] | None = None
    ) -> list[dict]:
        """二次校验并执行只读 SQL，限制执行时间和最大返回行数。"""

        safety = app_config.sql_safety
        safe_sql = guard_read_only_sql(
            sql,
            allowed_tables=allowed_tables,
            policy=SQLGuardPolicy(
                max_length=safety.max_length,
                max_result_rows=safety.max_result_rows,
                allowed_schemas=(app_config.db_dw.database,),
            ),
        )
        timeout_ms = max(int(safety.max_execution_time_ms), 1)
        await self.session.execute(
            text(f"SET SESSION MAX_EXECUTION_TIME = {timeout_ms}")
        )
        result = await self.session.execute(text(safe_sql))
        rows = result.mappings().fetchmany(safety.max_result_rows + 1)
        if len(rows) > safety.max_result_rows:
            raise ValueError(
                f"查询结果超过安全上限 {safety.max_result_rows} 行，已终止返回"
            )
        return [dict(row) for row in rows]
