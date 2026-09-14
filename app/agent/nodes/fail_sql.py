"""SQL 连续校验失败后的终止节点。"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def fail_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """达到最大修正次数后终止执行，绝不把未校验 SQL 发送到数据库。"""

    writer = runtime.stream_writer
    step = "终止SQL执行"
    message = state.get("error") or "SQL 未通过安全校验"
    logger.error(f"SQL 达到最大修正次数，已阻止执行：{message}")
    writer({"type": "progress", "step": step, "status": "error"})
    raise ValueError(f"SQL 连续校验失败，已阻止执行：{message}")
