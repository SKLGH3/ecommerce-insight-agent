"""FastAPI 应用入口。"""

import uuid

from fastapi import FastAPI, Request

from app.api.lifespan import lifespan
from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var

app = FastAPI(
    title="电商智能问数平台",
    description="基于元数据检索与受控 NL2SQL 的电商数据分析服务",
    version="0.2.0",
    lifespan=lifespan,
)
app.include_router(query_router)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """为每个 HTTP 请求注入独立 request_id。"""

    request_id_ctx_var.set(uuid.uuid4())
    return await call_next(request)


@app.get("/health", tags=["system"])
async def health_check():
    """供 Docker 与外部负载均衡器探测进程存活状态。"""

    return {"status": "ok", "service": "ecommerce-insight-agent"}
