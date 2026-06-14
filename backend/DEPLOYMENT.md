# 部署文档

## 当前部署文件检查

| 文件 | 当前状态 | 说明 |
| --- | --- | --- |
| Backend Dockerfile | 未发现 | 上线前需要补齐 |
| Frontend Dockerfile | 未发现 | 上线前需要补齐 |
| docker-compose.yml | 未发现 | 上线前需要补齐 |
| nginx.conf | 未发现 | 上线前需要补齐 |
| .env.example | 未发现 | 上线前需要补齐 |
| frontend/.gitignore | 已存在 | 已忽略 node_modules、.next、.env 等 |
| backend/.gitignore | 未发现 | 建议补齐 |

## 本地部署步骤

### 1. 准备 MySQL

创建数据库：

```sql
CREATE DATABASE ai_interview DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 准备 Ollama

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### 3. 配置后端环境变量

在 `backend/.env` 中配置：

```env
SECRET_KEY=change-me

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=ai_interview

POOL_SIZE=5
MAX_OVERFLOW=10
POOL_TIMEOUT=30
POOL_RECYCLE=1800
SQL_ECHO=false

OLLAMA_MODEL=qwen2.5:7b

CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=interview_docs
EMBEDDING_MODEL=nomic-embed-text
TOP_K=3

MAX_FOLLOW_UP=3
```

### 4. 启动后端

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run build
npm run start
```

## Docker 启动命令

当前项目尚未提供 Docker 文件，因此以下为建议目标命令：

```bash
docker compose up -d --build
```

建议 `docker-compose.yml` 服务：

```yaml
services:
  mysql:
    image: mysql:8

  backend:
    build: ./backend
    depends_on:
      - mysql

  frontend:
    build: ./frontend
    depends_on:
      - backend

  nginx:
    image: nginx:stable
    depends_on:
      - frontend
      - backend
```

## 数据库初始化

当前后端启动时会执行：

```python
Base.metadata.create_all(bind=engine)
```

这适合开发环境，不适合生产环境。生产建议：

1. 引入 Alembic。
2. 将当前模型生成第一版 migration。
3. 上线时执行：

```bash
alembic upgrade head
```

## Nginx 配置说明

建议 Nginx 负责：

- 代理前端页面到 Next.js。
- 代理 `/api` 或后端路径到 FastAPI。
- 配置 HTTPS。
- 限制上传大小。
- 配置静态资源缓存。

示例方向：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://frontend:3000;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
    }
}
```

## 常见问题

### 1. 登录后请求 401

检查：

- 前端是否保存 token。
- `SECRET_KEY` 是否一致。
- 请求头是否包含 `Authorization: Bearer <token>`。

### 2. LLM 无响应

检查：

- Ollama 是否启动。
- `OLLAMA_MODEL` 是否存在。
- 模型名称是否和 `.env` 一致。

### 3. MySQL 连接失败

检查：

- `DB_HOST`
- `DB_PORT`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`

### 4. SQL 日志过多

设置：

```env
SQL_ECHO=false
```

### 5. 文件上传失败

当前只支持：

- PDF
- DOCX
- TXT

空文件会被拒绝。

## 生产环境部署建议

上线前建议完成：

- 补齐 Dockerfile。
- 补齐 docker-compose.yml。
- 补齐 nginx.conf。
- 补齐 .env.example。
- 补齐 backend/.gitignore。
- 引入 Alembic。
- 配置 HTTPS。
- 配置生产 CORS 白名单。
- 限制上传文件大小。
- 日志脱敏。
- CI 中自动执行 pytest、lint、E2E。
- 将真实 `.env` 从 GitHub 中移除。
