# 系统架构文档

## 系统架构图

```mermaid
flowchart TD
    U[User Browser<br/>用户浏览器]
    F[Next.js Frontend<br/>React / TypeScript]
    B[FastAPI Backend<br/>Routes / Services / Schemas]
    M[(MySQL<br/>业务数据)]
    C[(Chroma<br/>向量检索)]
    O[Ollama LLM<br/>题目生成 / 评分 / 追问 / 报告]

    U -->|HTTP 页面访问| F
    F -->|HTTP + JSON<br/>登录 / 刷题 / Follow Up / 报告| B
    F -->|HTTP + Multipart Upload<br/>PDF / DOCX / TXT 简历| B

    B -->|SQLAlchemy ORM<br/>用户 / 记录 / Topic / 报告| M
    B -->|Embedding Query<br/>简历与上下文检索| C
    B -->|LangChain Invoke<br/>Prompt + JSON 输出| O

    O -->|JSON / Text Response| B
    C -->|Relevant Documents| B
    M -->|Query Result| B
    B -->|JSON Response| F
    F -->|页面渲染 / Toast / 路由跳转| U
```

## 后端分层图

```mermaid
flowchart TD
    R[Routes<br/>auth / generate / evaluate / upload_resume / start_interview / follow_up / report / history / interview_records]
    S[Services<br/>auth_service / interview_start_service / interview_flow_service / report_service / model_service / rag_service]
    CH[Chains<br/>question_chain / evaluate_chain / first_question_chain / follow_up_chain / report_chain]
    P[Prompts<br/>面试 / 评分 / 追问 / 报告 Prompt]
    DB[DB Layer<br/>crud.py / database.py]
    MD[Models<br/>SQLAlchemy ORM]
    SC[Schemas<br/>Pydantic Request / Response]

    R -->|请求校验 / 鉴权| SC
    R -->|业务调用| S
    S -->|LLM 编排| CH
    CH -->|Prompt 模板| P
    S -->|数据读写| DB
    DB -->|ORM| MD
```

## AI 面试流程图

```mermaid
flowchart TD
    A[上传简历] --> B[解析 PDF / DOCX / TXT]
    B --> C[保存 resumes]
    C --> D[创建 ai_interview_info]
    D --> E[基于简历生成 Topic 列表]
    E --> F[保存 interview_topics]
    F --> G[生成第一题]
    G --> H[保存 AI 消息]
    H --> I[用户回答]
    I --> J[保存 Human 消息]
    J --> K[LLM 判断 action / score / reason]
    K --> L{是否切换 Topic?}

    L -->|否 follow_up| M[生成追问 next_question]
    M --> H

    L -->|是 switch_topic| N[标记当前 Topic finished]
    N --> O{是否还有下一个 Topic?}
    O -->|有| P[切换下一个 Topic]
    P --> G
    O -->|无| Q[标记面试 finished]
    Q --> R[生成面试报告]
    R --> S[保存 interview_reports]
```

## 刷题流程图

```mermaid
flowchart TD
    A[进入刷题页] --> B[输入题库 / 题型 / 技术方向]
    B --> C[POST /generate_questions]
    C --> D[创建 interviews 刷题记录]
    D --> E[LLM 生成题目列表]
    E --> F[前端展示题目]
    F --> G[用户输入答案]
    G --> H[POST /evaluate_answer]
    H --> I[AI 评分]
    I --> J[保存 interview_answers]
    J --> K[展示解析 / 参考答案 / 得分]
    K --> L[进入刷题记录 /history]
    L --> M[查看详情 /history/{id}]
    M --> N[删除记录]
```

## Topic 切换机制

Topic 切换由 LLM 判断和代码兜底共同完成。

LLM 输出结构：

```json
{
  "action": "follow_up 或 switch_topic",
  "score": 0,
  "reason": "判断原因",
  "next_question": "如果继续追问，则给出下一题"
}
```

代码兜底规则：

- `action == "switch_topic"`：切换到下一个 Topic。
- `score >= 85`：回答质量较高，提前切换。
- `score <= 55` 且 `follow_up_count >= 1`：低分切换。
- `follow_up_count >= MAX_FOLLOW_UP`：强制切换。
- `cannot_answer == true`：候选人明确不会，强制切换。
- LLM 输出解析失败：继续追问，但最多不超过 `MAX_FOLLOW_UP`。

当前 `MAX_FOLLOW_UP` 从 `.env` 读取，并在代码层限制最大值为 3。

## Follow Up 机制

Follow Up 基于以下上下文生成：

- 当前 Topic
- 用户最近回答
- 当前 Topic 历史消息
- LLM 输出的 action / score / reason
- 代码层兜底规则

目标：

- 深入追问技术细节。
- 验证项目经验真实性。
- 避免重复问题。
- 避免对明显不会的问题继续追问。

## cannot_answer 机制

系统不会简单用 `includes("不会")` 判断。

判定为 cannot_answer 的典型情况：

- 回答很短。
- 主要表达不会、不知道、不清楚、不了解、没接触过。

不会判定为 cannot_answer 的情况：

- “不会一直查库，会先查 Redis 缓存”
- “这样不会导致缓存击穿”
- “我们不会这样处理”
- 回答中包含方案、项目经验、技术细节。

## 报告生成机制

```mermaid
flowchart TD
    A[POST /interviews/{id}/report/generate] --> B[查询 AI 面试]
    B --> C{是否属于当前用户?}
    C -->|否| X[403 Forbidden]
    C -->|是| D{面试是否完成?}
    D -->|否| Y[400 Bad Request]
    D -->|是| E[查询 Topic 和消息]
    E --> F[聚合回答表现]
    F --> G[调用 LLM 生成报告 JSON]
    G --> H{JSON 是否合法?}
    H -->|否| I[使用兜底报告]
    H -->|是| J[解析报告字段]
    I --> K[代码层修正分数和无效回答]
    J --> K
    K --> L[保存 interview_reports]
    L --> M[返回报告 JSON]
```

报告包含：

- 综合评分
- 总结
- 优势
- 不足
- Topic 得分
- 改进建议
- 复习计划

## 数据表关系图

```mermaid
erDiagram
    users ||--o{ resumes : owns
    users ||--o{ interviews : practices
    users ||--o{ ai_interview_info : attends

    interviews ||--o{ interview_answers : contains

    resumes ||--o{ ai_interview_info : starts

    ai_interview_info ||--o{ interview_topics : has
    ai_interview_info ||--o{ interview_messages : records
    ai_interview_info ||--|| interview_reports : generates

    interview_topics ||--o{ interview_messages : groups

    users {
        int id PK
        string username
        string password
    }

    interviews {
        int id PK
        text jd
        int user_id
        timestamp created_at
    }

    interview_answers {
        int id PK
        int interview_id FK
        text question
        text answer
        int overall_score
        text feedback
    }

    resumes {
        int id PK
        int user_id FK
        string file_name
        text resume_text
    }

    ai_interview_info {
        int id PK
        int user_id FK
        int resume_id FK
        string status
        datetime created_at
        datetime finished_at
    }

    interview_topics {
        int id PK
        int interview_id FK
        string topic
        int topic_order
        int follow_up_count
        boolean finished
    }

    interview_messages {
        int id PK
        int interview_id FK
        int topic_id FK
        string role
        text content
    }

    interview_reports {
        int id PK
        int interview_id FK
        int overall_score
        text summary
        text topic_scores_json
    }
```

## 表职责说明

- `interviews`：刷题模式主记录。
- `interview_answers`：刷题答案和评分。
- `ai_interview_info`：AI 面试主记录。
- `interview_topics`：AI 面试 Topic 状态。
- `interview_messages`：AI 面试对话消息。
- `interview_reports`：AI 面试报告。
- `resumes`：简历文件解析结果。
- `users`：用户与登录信息。
