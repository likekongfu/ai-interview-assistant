# Debian 11 Docker 部署说明

## 部署目标

本部署方案面向 1G 内存 Debian 11 服务器，默认使用 DeepSeek API，不在服务器部署 Ollama。

服务组成：

- `frontend`：Next.js 前端，端口 3000，仅供 nginx 内部访问。
- `backend`：FastAPI 后端，端口 8000，仅供 nginx 内部访问。
- `mysql`：MySQL 8，使用 Docker volume 持久化。
- `nginx`：统一入口，监听 80 端口。

## 1. 准备服务器环境

安装 Docker 和 Compose：

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

重新登录 SSH 后验证：

```bash
docker version
docker compose version
```

## 2. 准备环境变量

在项目根目录复制示例文件：

```bash
cp .env.example .env
```

修改 `.env`：

```env
SECRET_KEY=请替换成足够长的随机字符串

DB_HOST=mysql
MYSQL_HOST=mysql
DB_PORT=3306
DB_USER=ai_interview
DB_PASSWORD=请替换成强密码
DB_NAME=ai_interview
MYSQL_ROOT_PASSWORD=请替换成root强密码

LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的DeepSeek API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

NEXT_PUBLIC_API_BASE_URL=/api
```

注意：

- 不要把真实 `.env` 提交到 GitHub。
- 服务器默认不要启用 Ollama。
- 本地开发如需 Ollama，可把 `LLM_PROVIDER` 改为 `ollama`。

## 3. 构建并启动

```bash
docker compose up -d --build
```

查看服务状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mysql
docker compose logs -f nginx
```

停止服务：

```bash
docker compose down
```

停止并删除 MySQL 数据卷：

```bash
docker compose down -v
```

## 4. 访问地址

浏览器访问：

```text
http://服务器IP/
```

后端接口会通过 nginx 的 `/api` 前缀转发：

```text
http://服务器IP/api
```

## 5. 本地 Docker 启动

本地同样复制环境变量：

```bash
cp .env.example .env
```

如果使用 DeepSeek：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key
NEXT_PUBLIC_API_BASE_URL=/api
```

如果使用本地 Ollama：

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:7b
```

然后启动：

```bash
docker compose up -d --build
```

## 6. 常见问题

### 后端连接不上 MySQL

检查：

- `.env` 中 `DB_HOST` 或 `MYSQL_HOST` 是否为 `mysql`。
- MySQL 是否健康：`docker compose ps`。
- 密码是否和 `DB_PASSWORD` 一致。

### DeepSeek 调用失败

检查：

- `DEEPSEEK_API_KEY` 是否配置。
- 服务器是否能访问 `https://api.deepseek.com`。
- `DEEPSEEK_MODEL` 是否可用。

### 前端请求失败

检查：

- `NEXT_PUBLIC_API_BASE_URL=/api`。
- nginx 是否正常运行。
- 浏览器 Network 中请求是否走 `/api`。

### 上传文件失败

nginx 已配置：

```nginx
client_max_body_size 20m;
```

如需更大简历文件，可调整该值。

## 7. 生产建议

- 使用 HTTPS 和域名。
- 使用更强的 `SECRET_KEY`。
- 不要开放 MySQL 端口到公网。
- 定期备份 Docker volume：`mysql_data`。
- 给服务器增加 swap，避免 1G 内存构建时 OOM。
- 建议在本地或 CI 先完成镜像构建，再推送到服务器运行。
