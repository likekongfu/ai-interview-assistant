# 数据库文档

## 数据库概览

当前项目使用 MySQL 存储用户、刷题记录、AI 面试记录、面试消息、Topic 和报告数据。

向量检索使用 Chroma，路径由 `CHROMA_DB_PATH` 控制。

## 表列表

### users

用户表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK | 用户 ID |
| username | String(255), unique, not null | 用户名 |
| password | String(255), not null | PBKDF2 哈希密码 |

索引：

- `PRIMARY KEY (id)`
- `UNIQUE (username)`

### interviews

刷题模式记录表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, index | 刷题记录 ID |
| jd | Text | 题库 / 题型 / 技术方向文本 |
| user_id | Integer | 所属用户 ID |
| created_at | TIMESTAMP | 创建时间 |

索引：

- `PRIMARY KEY (id)`
- `INDEX (id)`

关系：

- `users.id` 逻辑关联 `interviews.user_id`
- `interviews.id` 关联 `interview_answers.interview_id`

### interview_answers

刷题答案与评分表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, index | 答案 ID |
| interview_id | Integer, FK | 对应 `interviews.id` |
| question | Text | 题目 |
| answer | Text | 用户答案 |
| technical_score | Integer | 技术分 |
| logic_score | Integer | 逻辑分 |
| experience_score | Integer | 经验分 |
| communication_score | Integer | 表达分 |
| overall_score | Integer | 综合分 |
| feedback | Text | AI 反馈 |
| created_at | TIMESTAMP | 创建时间 |

索引：

- `PRIMARY KEY (id)`
- `INDEX (id)`

关系：

- `interview_answers.interview_id -> interviews.id`

### resumes

简历表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, autoincrement | 简历 ID |
| user_id | Integer, FK, not null | 所属用户 |
| file_name | String(255) | 文件名 |
| resume_text | Text | 解析后的简历文本 |
| created_at | DateTime | 创建时间 |

关系：

- `resumes.user_id -> users.id`
- `ai_interview_info.resume_id -> resumes.id`

### ai_interview_info

AI 面试主表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, index | AI 面试 ID |
| user_id | Integer, FK, not null | 所属用户 |
| resume_id | Integer, FK, not null | 简历 ID |
| status | String(20), not null | `in_progress` 或 `finished` |
| created_at | DateTime | 创建时间 |
| finished_at | DateTime, nullable | 结束时间 |

关系：

- `ai_interview_info.user_id -> users.id`
- `ai_interview_info.resume_id -> resumes.id`
- `interview_topics.interview_id -> ai_interview_info.id`
- `interview_messages.interview_id -> ai_interview_info.id`
- `interview_reports.interview_id -> ai_interview_info.id`

### interview_topics

AI 面试 Topic 表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, index | Topic ID |
| interview_id | Integer, FK, not null | AI 面试 ID |
| topic | String(255), not null | Topic 名称 |
| topic_order | Integer, not null | Topic 顺序 |
| follow_up_count | Integer | 当前 Topic 追问次数 |
| finished | Boolean | 是否完成 |
| created_at | TIMESTAMP | 创建时间 |

关系：

- `interview_topics.interview_id -> ai_interview_info.id`
- `interview_messages.topic_id -> interview_topics.id`

### interview_messages

AI 面试消息表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK | 消息 ID |
| interview_id | Integer, FK | AI 面试 ID |
| role | String | `ai` 或 `human` |
| content | Text | 消息内容 |
| created_at | DateTime | 创建时间 |
| topic_id | Integer, FK, nullable | Topic ID |

关系：

- `interview_messages.interview_id -> ai_interview_info.id`
- `interview_messages.topic_id -> interview_topics.id`

### interview_reports

AI 面试报告表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | Integer, PK, index | 报告 ID |
| interview_id | Integer, FK, not null | AI 面试 ID |
| overall_score | Integer, not null | 综合分 |
| summary | Text, not null | 总结 |
| strengths | Text, not null | 优势 JSON |
| weaknesses | Text, not null | 不足 JSON |
| topic_scores_json | Text, not null | Topic 得分 JSON |
| improvement_suggestions | Text, not null | 建议 JSON |
| study_plan | Text, not null | 学习计划 JSON |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

索引与约束：

- `PRIMARY KEY (id)`
- `UNIQUE (interview_id)`

关系：

- `interview_reports.interview_id -> ai_interview_info.id`

## ER 关系说明

```text
users 1 ------ N resumes
users 1 ------ N interviews
users 1 ------ N ai_interview_info

interviews 1 ------ N interview_answers

resumes 1 ------ N ai_interview_info

ai_interview_info 1 ------ N interview_topics
ai_interview_info 1 ------ N interview_messages
ai_interview_info 1 ------ 1 interview_reports

interview_topics 1 ------ N interview_messages
```

## 当前数据库风险

- 暂未接入 Alembic，表结构变更依赖 `Base.metadata.create_all`。
- `interviews.user_id` 未声明数据库级外键，仅逻辑关联。
- 部分级联删除由代码完成，生产环境建议统一用迁移脚本和数据库约束管理。
