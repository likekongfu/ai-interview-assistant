AI 面试助手 🚀
一个基于大语言模型的面试模拟与评估工具，帮助开发者高效准备面试、生成岗位定制化题目并获得 AI 智能评分反馈。
✨ 项目亮点
🎯 AI 生成题目：基于岗位 JD 智能生成真实面试问题，告别盲目刷题
🤖 AI 智能评分：多维度分析回答质量，提供技术水平与逻辑表达反馈
📝 历史记录：自动保存所有面试过程与评分结果，方便复盘提升
🔐 多用户系统：JWT 鉴权与用户数据完全隔离，保障隐私安全
📸 功能截图
首页 & 面试模拟
历史记录
智能评分详情
🛠️ 技术栈
前端：Next.js + Tailwind CSS
后端：FastAPI + Python
AI 能力：大语言模型接口
数据库：（可根据实际情况补充，如 SQLite / PostgreSQL）
鉴权：JWT 令牌认证
🚀 快速开始
1. 克隆项目
bash
运行
git clone <你的仓库地址>
cd ai-interview-assistant
2. 前端启动
bash
运行
cd frontend
npm install
npm run dev
3. 后端启动
bash
运行
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
📖 核心功能说明
1. 题目生成
输入目标岗位的 JD 或关键词，AI 会自动生成符合岗位要求的面试题目，覆盖技术基础、工程实践、场景分析等多个维度。
2. 面试与评分
用户在页面输入回答后，AI 会从以下维度进行多维度评估：
技术能力：知识点掌握的准确性与完整性
逻辑表达：回答的条理性与结构化程度
工程经验：是否结合实际场景展开说明
沟通表达：语言的清晰度与专业度
3. 历史记录
所有面试记录与评分结果会自动保存，支持查看详情、复盘回答，追踪自己的面试准备进度。
4. 多用户系统
基于 JWT 的身份认证
不同用户数据完全隔离
支持登录、退出登录操作
📂 项目结构
plaintext
ai-interview-assistant/
├── frontend/    # Next.js 前端项目
├── backend/     # FastAPI 后端项目
└── README.md    # 项目说明文档