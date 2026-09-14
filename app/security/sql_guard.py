"""只读 SQL 校验与规范化。

LLM 输出属于不可信输入。这个模块在 SQL 到达数据库之前执行程序级检查，
确保只允许单条只读查询，并限制可访问的业务表和最大返回行数。
"""

from dataclasses import dataclass
from typing import Collection

from sqlglot import exp, parse
from sqlglot.errors import ParseError


class SQLSafetyError(ValueError):
    """SQL 不符合只读安全策略。"""


@dataclass(frozen=True)
class SQLGuardPolicy:
    """SQL 安全策略参数。"""

    dialect: str = "mysql"
    max_length: int = 20_000
    max_result_rows: int = 1_000
    allowed_schemas: tuple[str, ...] = ()


_FORBIDDEN_NODE_KEYS = {
    "alter",
    "attach",
    "cache",
    "command",
    "copy",
    "create",
    "delete",
    "detach",
    "drop",
    "grant",
    "insert",
    "into",
    "load_data",
    "lock",
    "merge",
    "pragma",
    "revoke",
    "set",
    "transaction",
    "truncate",
    "truncate_table",
    "uncache",
    "update",
    "use",
}
_FORBIDDEN_FUNCTIONS = {"BENCHMARK", "LOAD_FILE", "SLEEP"}
_SYSTEM_SCHEMAS = {"information_schema", "mysql", "performance_schema", "sys"}


def guard_read_only_sql(
    sql: str,
    *,
    allowed_tables: Collection[str] | None = None,
    policy: SQLGuardPolicy | None = None,
) -> str:
    """校验并规范化单条只读 SQL。

    返回可执行的规范化 SQL，并将最外层 LIMIT 限制到策略允许的最大行数。
    """

    current_policy = policy or SQLGuardPolicy()
    candidate = sql.strip()

    if not candidate:
        raise SQLSafetyError("SQL 不能为空")
    if len(candidate) > current_policy.max_length:
        raise SQLSafetyError(
            f"SQL 长度超过限制：{len(candidate)} > {current_policy.max_length}"
        )
    if "\x00" in candidate:
        raise SQLSafetyError("SQL 包含非法空字符")

    try:
        statements = [
            statement
            for statement in parse(candidate, read=current_policy.dialect)
            if statement is not None
        ]
    except ParseError as exc:
        raise SQLSafetyError(f"SQL 解析失败：{exc}") from exc

    if len(statements) != 1:
        raise SQLSafetyError("只允许提交一条 SQL 语句")

    expression = statements[0]
    if not isinstance(expression, exp.Query):
        raise SQLSafetyError("只允许 SELECT 或 WITH 查询")

    for node in expression.walk():
        node_key = str(getattr(node, "key", "")).lower()
        if node_key in _FORBIDDEN_NODE_KEYS:
            raise SQLSafetyError(f"检测到禁止的 SQL 操作：{node_key.upper()}")

    for function in expression.find_all(exp.Func):
        if isinstance(function, exp.Anonymous):
            function_name = function.name.upper()
        else:
            function_name = function.sql_name().upper()
        if function_name in _FORBIDDEN_FUNCTIONS:
            raise SQLSafetyError(f"禁止调用高风险函数：{function_name}")

    cte_names = {
        cte.alias_or_name.lower()
        for cte in expression.find_all(exp.CTE)
        if cte.alias_or_name
    }
    referenced_tables: set[str] = set()
    for table in expression.find_all(exp.Table):
        table_name = table.name.lower()
        if table_name in cte_names:
            continue

        database_name = table.db.lower() if table.db else ""
        if database_name in _SYSTEM_SCHEMAS:
            raise SQLSafetyError(f"禁止访问系统数据库：{database_name}")
        allowed_schemas = {name.lower() for name in current_policy.allowed_schemas}
        if database_name and allowed_schemas and database_name not in allowed_schemas:
            raise SQLSafetyError(f"禁止跨数据库访问：{database_name}")
        referenced_tables.add(table_name)

    if allowed_tables is not None:
        allowed = {name.rsplit(".", 1)[-1].lower() for name in allowed_tables}
        unknown = sorted(referenced_tables - allowed)
        if unknown:
            raise SQLSafetyError(f"SQL 引用了未授权的数据表：{', '.join(unknown)}")

    if not referenced_tables:
        raise SQLSafetyError("查询必须访问已授权的业务数据表")

    expression = _cap_outer_limit(expression, current_policy.max_result_rows)
    return expression.sql(dialect=current_policy.dialect)


def _cap_outer_limit(expression: exp.Query, max_rows: int) -> exp.Query:
    """确保最外层查询存在不超过 max_rows 的 LIMIT。"""

    if max_rows <= 0:
        raise SQLSafetyError("最大返回行数必须大于 0")

    limit = expression.args.get("limit")
    if limit is None:
        return expression.limit(max_rows, copy=True)

    limit_expression = limit.expression
    if isinstance(limit_expression, exp.Literal) and limit_expression.is_int:
        if int(limit_expression.this) <= max_rows:
            return expression
        return expression.limit(max_rows, copy=True)

    raise SQLSafetyError("LIMIT 必须是整数常量")
