"""电商智能问数平台的 LangGraph 状态定义。"""

from typing import NotRequired, TypedDict

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo


class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]


class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list
    description: str
    alias: list[str]


class TableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]


class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str


class DBInfoState(TypedDict):
    dialect: str
    version: str


class DataAgentState(TypedDict):
    """一次问数链路中的共享状态。"""

    query: str
    keywords: NotRequired[list[str]]
    retrieved_column_infos: NotRequired[list[ColumnInfo]]
    retrieved_metric_infos: NotRequired[list[MetricInfo]]
    retrieved_value_infos: NotRequired[list[ValueInfo]]
    table_infos: NotRequired[list[TableInfoState]]
    metric_infos: NotRequired[list[MetricInfoState]]
    date_info: NotRequired[DateInfoState]
    db_info: NotRequired[DBInfoState]
    sql: NotRequired[str]
    error: NotRequired[str | None]
    correction_attempts: NotRequired[int]
