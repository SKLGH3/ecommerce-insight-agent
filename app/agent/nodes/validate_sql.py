"""SQL 校验节点。"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.conf.app_config import app_config
from app.core.log import logger
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.security.sql_guard import SQLGuardPolicy, guard_read_only_sql


async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """执行程序级安全检查和数据库 EXPLAIN 校验。"""

    writer = runtime.stream_writer
    step = "校验SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    sql = state["sql"]
    table_infos = state.get("table_infos", [])
    allowed_tables = {table["name"] for table in table_infos}
    dw_mysql_repository: DWMySQLRepository = runtime.context["dw_mysql_repository"]

    try:
        safe_sql = guard_read_only_sql(
            sql,
            allowed_tables=allowed_tables,
            policy=SQLGuardPolicy(
                max_length=app_config.sql_safety.max_length,
                max_result_rows=app_config.sql_safety.max_result_rows,
                allowed_schemas=(app_config.db_dw.database,),
            ),
        )
        await dw_mysql_repository.validate(safe_sql)
        writer({"type": "progress", "step": step, "status": "success"})
        logger.info(f"SQL 安全检查和 EXPLAIN 校验通过：{safe_sql}")
        return {"sql": safe_sql, "error": None}
    except Exception as exc:
        error = str(exc)
        logger.warning(f"SQL 校验失败：{error}")
        writer({"type": "progress", "step": step, "status": "error"})
        return {"error": error}
