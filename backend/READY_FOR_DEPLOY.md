# Docker 部署就绪检查

## 当前结论

```text
READY FOR DOCKER DEPLOY: YES, CONFIG VERIFIED
```

说明：Docker Compose 配置语法已通过验证；镜像构建未完成验证，原因是当前机器 Docker daemon 未启动，不是配置文件语法错误。

## 已完成内容

- 后端已支持 `LLM_PROVIDER=ollama` 和 `LLM_PROVIDER=deepseek`。
- 服务器默认使用 DeepSeek API。
- 本地仍可切换回 Ollama。
- Docker Compose 不包含 Ollama 服务，适合 1G 内存 Debian 11 服务器。
- 已新增后端 Dockerfile。
- 已新增前端 Dockerfile。
- 已新增根目录 `docker-compose.yml`。
- 已新增 `nginx/nginx.conf`。
- 已新增根目录 `.env.example`。
- 已更新 `backend/.env.example`。
- 已新增 `DEPLOYMENT_DEBIAN.md`。

## 服务组成

`docker-compose.yml` 包含：

- `frontend`
- `backend`
- `mysql`
- `nginx`

不包含：

- `ollama`

## 已验证

后端测试：

```text
18 passed
```

Compose 语法：

```bash
docker compose --env-file .env.example config
```

结果：

```text
通过
```

Docker build：

```bash
docker compose --env-file .env.example build
```

结果：

```text
未完成
```

原因：

```text
Docker daemon 未启动：dockerDesktopLinuxEngine 不存在
```

启动 Docker Desktop 或在 Debian 服务器安装 Docker 后，再执行 build 即可继续验证。

## DeepSeek 配置

服务器 `.env` 推荐：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

如果缺少 `DEEPSEEK_API_KEY`，后端在调用 LLM 时会抛出明确错误。

## 本地 Ollama 配置

本地开发 `.env` 可改为：

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
```

如果在 Docker 容器中访问宿主机 Ollama：

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Debian 11 部署命令

```bash
cp .env.example .env
vim .env
docker compose up -d --build
docker compose logs -f
```

停止：

```bash
docker compose down
```

删除数据库数据卷：

```bash
docker compose down -v
```

## 剩余风险

- 1G 内存服务器直接构建前端镜像可能 OOM，建议增加 swap 或在本地构建镜像后推送。
- 生产环境必须替换 `.env.example` 中的占位密码和 `SECRET_KEY`。
- DeepSeek API 依赖外网访问能力。
