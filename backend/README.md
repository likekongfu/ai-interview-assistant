# AI Interview Assistant

AI Interview Assistant 是一个面向求职者的 AI 面试与刷题系统。项目围绕“准备技术面试”这个场景，提供刷题练习、简历驱动的 AI 模拟面试、动态 Follow Up、Topic 切换、结构化面试报告和历史记录闭环。

项目适合作为 AI 应用开发岗 Portfolio：它不是简单调用大模型，而是包含用户鉴权、文件解析、Prompt 编排、结构化 JSON 输出解析、数据库持久化、前后端交互、E2E 测试和报告生成。

## 解决的问题

- 求职者不知道如何围绕简历准备技术面试。
- 刷题后缺少即时反馈和结构化评分。
- 模拟面试容易僵硬，传统固定追问次数体验差。
- 面试后缺少可复盘的报告、Topic 得分和复习建议。

## 目标用户

- 准备 Java / 后端 / AI 应用开发岗位的求职者。
- 需要模拟技术面试和复盘报告的学生或转岗开发者。
- 希望展示 AI 应用工程能力的开发者。

## 功能演示

### 刷题

- 输入题库 / 题目类型 / 技术方向。
- 获取题目列表。
- 输入答案并提交。
- AI 返回评分、解析和反馈。
- 保存刷题记录。
- 支持查看刷题记录详情和删除记录。

### AI 面试

- 上传 PDF / DOCX / TXT 简历。
- 后端解析简历文本。
- 创建 AI 面试会话。
- AI 基于简历生成第一题。
- 用户回答后持续 Follow Up。
- 根据回答质量动态切换 Topic。
- 所有 Topic 完成后结束面试。

### 面试报告

- 面试结束后生成结构化报告。
- 包含综合评分、Topic 得分、优势、不足、改进建议和复习计划。
- 报告可从面试记录页再次查看。

### 历史记录

- 刷题记录：查看练习记录、详情、删除。
- 面试记录：查看 AI 面试历史，点击进入报告页。

## 技术架构

### Frontend

- Next.js 16
- React 19
- TypeScript
- Playwright E2E
- react-hot-toast

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT 鉴权
- pdfplumber
- python-docx

### Database

- MySQL
- Chroma 向量库

### LLM

- Ollama
- LangChain
- Prompt 分层
- JSON 输出解析与兜底

## 本地启动

### 1. 后端

```bash
cd backend
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv python-jose langchain langchain-core langchain-ollama langchain-chroma chromadb pdfplumber python-docx pydantic pytest
uvicorn main:app --reload
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

### 3. Ollama

```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

## Docker 启动

当前仓库尚未提供正式 `Dockerfile`、`docker-compose.yml`、`nginx.conf`。生产部署前建议补齐：

```bash
docker compose up -d --build
```

建议服务拆分：

- frontend：Next.js
- backend：FastAPI
- mysql：MySQL
- chroma：向量数据库或本地挂载
- nginx：反向代理和静态资源入口

## 环境变量说明

后端 `.env` 示例：

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

前端建议环境变量：

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## 项目截图占位

建议上传 GitHub 前补充以下截图：

- 首页
- 登录页
- 刷题页面
- 刷题记录页面
- AI 面试页面
- 面试报告页面
- 面试记录页面

## 项目亮点

- 简历驱动的 AI 模拟面试。
- 动态 Topic 切换，避免固定追问导致体验僵硬。
- cannot_answer 和无效回答检测，避免对“不会”强行追问。
- 面试结束后生成结构化报告，支持复盘。
- 刷题和面试双链路闭环。
- 用户鉴权和记录隔离。
- Playwright 覆盖关键 UI 链路。
- pytest 覆盖刷题接口、报告服务和异常场景。

## 测试

```bash
cd backend
D:\miniconda\envs\ai_project\python.exe -m pytest
```

```bash
cd frontend
npm run lint
npm run test:e2e
```

当前结果：

```text
pytest: 18 passed
Playwright E2E: 7 passed
```

## 当前状态

- Portfolio 展示：可以。
- 本地内测：可以。
- 商业生产上线：暂不建议直接上线。

上线前建议补充 Docker、Nginx、Alembic、CI、日志脱敏、文件大小限制和生产环境安全配置。
