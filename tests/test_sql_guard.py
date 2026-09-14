import pytest

from app.security.sql_guard import SQLGuardPolicy, SQLSafetyError, guard_read_only_sql

POLICY = SQLGuardPolicy(
    max_length=2_000,
    max_result_rows=100,
    allowed_schemas=("dw",),
)
ALLOWED_TABLES = {"fact_order", "dim_region"}


def guard(sql: str) -> str:
    return guard_read_only_sql(
        sql,
        allowed_tables=ALLOWED_TABLES,
        policy=POLICY,
    )


def test_select_is_normalized_and_limited():
    result = guard("SELECT order_id FROM fact_order")
    assert "LIMIT 100" in result.upper()


def test_cte_can_reference_authorized_table():
    result = guard(
        "WITH orders AS (SELECT region_id FROM fact_order) "
        "SELECT region_id FROM orders"
    )
    assert result.upper().startswith("WITH")
    assert "LIMIT 100" in result.upper()


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM fact_order",
        "UPDATE fact_order SET quantity = 0",
        "DROP TABLE fact_order",
        "INSERT INTO fact_order (order_id) VALUES ('x')",
    ],
)
def test_write_statements_are_rejected(sql: str):
    with pytest.raises(SQLSafetyError):
        guard(sql)


def test_multiple_statements_are_rejected():
    with pytest.raises(SQLSafetyError, match="一条 SQL"):
        guard("SELECT * FROM fact_order; SELECT * FROM dim_region")


def test_unknown_table_is_rejected():
    with pytest.raises(SQLSafetyError, match="未授权"):
        guard("SELECT * FROM secret_customer")


def test_system_schema_is_rejected():
    with pytest.raises(SQLSafetyError, match="系统数据库"):
        guard("SELECT * FROM information_schema.tables")



def test_cross_database_access_is_rejected():
    with pytest.raises(SQLSafetyError, match="跨数据库"):
        guard("SELECT * FROM another_db.fact_order")


def test_large_limit_is_capped():
    result = guard("SELECT * FROM fact_order LIMIT 99999")
    assert "LIMIT 100" in result.upper()
    assert "99999" not in result


def test_small_limit_is_preserved():
    result = guard("SELECT * FROM fact_order LIMIT 10")
    assert "LIMIT 10" in result.upper()


def test_dynamic_limit_is_rejected():
    with pytest.raises(SQLSafetyError, match="LIMIT"):
        guard("SELECT * FROM fact_order LIMIT @row_count")


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT SLEEP(10) FROM fact_order",
        "SELECT LOAD_FILE('/etc/passwd') FROM fact_order",
        "SELECT * FROM fact_order INTO OUTFILE '/tmp/orders.csv'",
    ],
)
def test_high_risk_read_side_effects_are_rejected(sql: str):
    with pytest.raises(SQLSafetyError):
        guard(sql)
