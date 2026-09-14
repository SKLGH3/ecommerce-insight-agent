# Ecommerce Insight Agent Frontend

“电商智能问数平台”的 Web 前端，使用 React、TypeScript、Vite、Tailwind CSS 和 pnpm 构建。

## 本地开发

```powershell
pnpm install --frozen-lockfile
pnpm run dev
```

默认访问 `http://localhost:5173`，并把 `/api` 代理到 `http://127.0.0.1:8000`。可在 `.env` 中通过 `VITE_DEV_PROXY_TARGET` 修改开发代理地址。

## 质量检查

```powershell
pnpm run lint
pnpm run build
```

## 容器部署

生产镜像使用 Nginx 托管静态资源，并把 `/api` 反向代理到 Compose 中的 `backend:8000` 服务。建议从项目根目录通过 Docker Compose 构建和启动。
