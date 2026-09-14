"""问数接口请求体定义。"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class QuerySchema(BaseModel):
    """`/api/query` 请求体，限制问题长度并自动去除首尾空白。"""

    query: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=2, max_length=1000),
        Field(description="需要分析的自然语言问题"),
    ]
