# 电商智能问数平台（Ecommerce Insight Agent）

面向电商数据分析场景的智能问数项目。用户输入自然语言问题后，系统通过元数据检索、指标与字段召回、受控 NL2SQL、数据库 `EXPLAIN` 校验和只读执行，实时返回分析结果。

本项目基于开源项目 `didilili/shopkeeper-agent` 二次开发，保留原 MIT License。改造说明见 [NOTICE.md](NOTICE.md)。

## 核心能力

- **自然语言问数**：把中文业务问题转换为 MySQL 查询。
- **混合元数据检索**：MySQL 保存结构化元数据，Qdrant 提供语义召回，Elasticsearch 提供字段值检索。
- **SQL 安全闭环**：AST 解析、单语句与只读限制、授权表限制、系统库拦截、自动限制返回行数。
- **失败修正机制**：生成 SQL 未通过安全检查或 `EXPLAIN` 时，有限次数修正；超过阈值立即终止，绝不执行未验证 SQL。
- **数据库纵深防御**：使用只读数仓账号、查询超时、结果行数上限、动态标识符校验。
- **流式交互**：FastAPI + SSE 实时展示 LangGraph 每一步执行状态。
- **一键容器化**：Docker Compose 启动 MySQL、Elasticsearch、Kibana、Qdrant、Embedding、后端和前端。

## 技术架构

```text
React / Nginx
      │ SSE
      ▼
FastAPI ── LangGraph Agent
      │        ├─ 元数据检索：MySQL + Qdrant + Elasticsearch
      │        ├─ LLM：OpenAI-compatible API
      │        └─ SQL Guard：sqlglot + EXPLAIN
      ▼
MySQL DW（只读账号、超时与行数限制）
```

## 目录结构

```text
ecommerce-insight-agent/
├── app/                    # 后端业务代码
│   ├── agent/              # LangGraph 状态、节点与工作流
│   ├── api/                # FastAPI 路由、Schema、依赖与生命周期
│   ├── clients/            # MySQL、Qdrant、ES、Embedding 客户端
│   ├── repositories/       # 数据访问层
│   ├── security/           # SQL 安全策略
│   └── services/           # 应用服务
├── conf/                   # 应用与元数据配置
├── docker/                 # Compose、数据库初始化和 ES 镜像
├── frontend/               # React + Vite 前端
├── prompts/                # Agent Prompt 模板
├── tests/                  # 自动化测试
├── Dockerfile              # 后端生产镜像
└── main.py                 # FastAPI 入口
```

## 快速启动（推荐）

### 1. 准备配置

```powershell
Copy-Item .env.example .env
```

至少修改：

```dotenv
LLM_API_KEY=你的真实密钥
MYSQL_ROOT_PASSWORD=强随机密码
MYSQL_APP_PASSWORD=强随机密码
MYSQL_READONLY_PASSWORD=强随机密码
```

默认模型接口为硅基流动兼容接口，也可通过 `LLM_MODEL_NAME` 和 `LLM_BASE_URL` 接入其他 OpenAI-compatible 服务。

### 2. 准备 Embedding 模型

模型应位于：

```text
docker/embedding/bge-large-zh-v1.5
```

下载示例：

```powershell
uv run hf download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5
```

如果本机已有模型，可以创建目录联接，避免复制约 1.3 GB 文件：

```powershell
New-Item -ItemType Junction `
  -Path .\docker\embedding\bge-large-zh-v1.5 `
  -Target D:\path\to\bge-large-zh-v1.5
```

### 3. 启动完整环境

请先启动 Docker Desktop，然后在项目根目录执行：

```powershell
docker compose --env-file .env -f docker/docker-compose.yaml up -d --build
```

访问地址：

- 前端：`http://localhost:3000`
- 后端文档：`http://localhost:8000/docs`
- 后端健康检查：`http://localhost:8000/health`
- Kibana：`http://localhost:5601`
- Elasticsearch：`http://localhost:9200`
- Qdrant：`http://localhost:6333/dashboard`

首次启动会初始化示例元数据库和电商数仓。MySQL 初始化脚本只在空数据卷第一次执行；修改数据库初始化脚本后，如需重建，请先确认数据可删除，再执行 `docker compose down -v`。

### 4. 构建元数据知识库

容器启动后执行：

```powershell
docker compose --env-file .env -f docker/docker-compose.yaml exec backend `
  uv run --no-sync python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

## 本地开发

要求：Python `3.12` 或 `3.13`、uv、Node.js、pnpm、Docker Desktop。

### 后端

```powershell
Copy-Item .env.example .env
uv sync --group dev
uv run fastapi dev main.py
```

### 前端

```powershell
Set-Location frontend
pnpm install --frozen-lockfile
pnpm run dev
```

Vite 默认把 `/api` 代理到 `http://127.0.0.1:8000`。

## SQL 安全策略

可通过 `.env` 调整：

```dotenv
SQL_MAX_LENGTH=20000
SQL_MAX_RESULT_ROWS=1000
SQL_MAX_CORRECTION_ATTEMPTS=2
SQL_MAX_EXECUTION_TIME_MS=15000
```

安全层不替代数据库权限。生产环境仍必须使用 `DW_DB_USER` 指定的只读账号，并限制其只能读取获准的业务 Schema。

## 质量检查

```powershell
uv run ruff check .
uv run pytest
python -m compileall -q app main.py

Set-Location frontend
pnpm run lint
pnpm run build
```

## 二次开发建议

1. 将示例数仓替换为你的真实只读数仓或只读副本。
2. 按业务维护 `conf/meta_config.yaml` 中的表、字段和指标定义。
3. 增加登录鉴权、租户隔离、查询审计与敏感字段脱敏。
4. 将 LLM 密钥放入密钥管理服务，不要提交 `.env`。
5. 为生产数据库配置网络白名单、只读权限与资源限额。

## License

本项目遵循 [MIT License](LICENSE)。上游版权和二次开发说明见 [NOTICE.md](NOTICE.md)。
