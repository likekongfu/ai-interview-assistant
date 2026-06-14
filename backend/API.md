# API 文档

默认后端地址：

```text
http://127.0.0.1:8000
```

受保护接口需要请求头：

```http
Authorization: Bearer <token>
```

## 1. 用户接口

### 注册

```http
POST /register
```

请求：

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

响应：

```json
{
  "message": "注册成功"
}
```

### 登录

```http
POST /login
```

请求：

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

响应：

```json
{
  "token": "jwt-token",
  "username": "zhangsan",
  "user_id": 1
}
```

### 重置密码

```http
POST /reset_password
```

请求：

```json
{
  "username": "zhangsan",
  "new_password": "new-password"
}
```

响应：

```json
{
  "message": "密码重置成功"
}
```

## 2. 刷题接口

### 获取题目

```http
POST /generate_questions
```

请求：

```json
{
  "jd": "题库 Java 后端；题型 简答题；技术方向 Redis"
}
```

响应：

```json
{
  "interview_id": 10,
  "questions": [
    "请解释 Redis 缓存击穿，并说明常见解决方案。"
  ]
}
```

异常：

- 400：题库配置为空。
- 502：LLM 生成失败。

### 提交答案并评分

```http
POST /evaluate_answer
```

请求：

```json
{
  "interview_id": 10,
  "question": "请解释 Redis 缓存击穿。",
  "answer": "热点 key 过期后大量请求打到数据库，可以用互斥锁和逻辑过期解决。"
}
```

响应：

```json
{
  "result": {
    "technical_score": 86,
    "logic_score": 84,
    "experience_score": 82,
    "communication_score": 88,
    "overall_score": 86,
    "feedback": "回答覆盖热点 key、数据库压力和互斥锁方案。"
  }
}
```

异常：

- 400：答案为空或刷题记录不存在。
- 403：无权访问该刷题记录。
- 502：AI 评分失败。

## 3. AI 面试接口

### 上传简历

```http
POST /upload_resume
Content-Type: multipart/form-data
```

请求：

```text
file: resume.pdf | resume.docx | resume.txt
```

响应：

```json
{
  "resume_id": 6
}
```

异常：

- 400：文件格式不支持。
- 400：简历内容为空。

### 开始面试

```http
POST /interview/start?resume_id=6
```

响应：

```json
{
  "interview_id": 15,
  "first_question": "请介绍一次你在项目中使用 Redis 处理缓存问题的经历。"
}
```

### 提交回答并获取追问

```http
POST /follow_up
```

请求：

```json
{
  "resume_id": 6,
  "interview_id": 15,
  "answer": "我会先查 Redis，如果缓存为空再查数据库，并设置短过期时间。"
}
```

响应：

```json
{
  "next_question": "你如何避免缓存击穿？",
  "topic": "Redis 缓存设计",
  "follow_up_count": 1,
  "finished": false,
  "message": null,
  "action": "follow_up",
  "score": 78,
  "reason": "回答有一定技术细节，可以继续追问。"
}
```

面试结束响应：

```json
{
  "next_question": null,
  "topic": null,
  "follow_up_count": 0,
  "finished": true,
  "message": "面试结束",
  "action": "switch_topic",
  "score": 20,
  "reason": "所有 Topic 已完成"
}
```

## 4. 报告接口

### 生成面试报告

```http
POST /interviews/{interview_id}/report/generate
```

响应：

```json
{
  "interview_id": 15,
  "overall_score": 78,
  "summary": "整体表现稳定，但高并发场景细节需要加强。",
  "strengths": ["能够结合项目背景回答"],
  "weaknesses": ["Redis 缓存击穿解释不够完整"],
  "topic_scores": [
    {
      "topic": "Redis",
      "score": 75,
      "comment": "基础理解较好，但解决方案细节不足。"
    }
  ],
  "improvement_suggestions": ["复习缓存穿透、击穿、雪崩"],
  "study_plan": ["第1天：复习 Redis 高频问题"]
}
```

异常：

- 400：面试未完成。
- 403：无权访问。
- 404：面试不存在。

### 查询面试报告

```http
GET /interviews/{interview_id}/report
```

响应同生成报告接口。若报告未生成，返回未生成状态或错误信息，取决于服务层处理。

## 5. 记录接口

### 刷题记录列表

```http
GET /history
```

响应：

```json
[
  {
    "id": 10,
    "jd": "题库 Java 后端；题型 简答题；技术方向 Redis",
    "created_at": "2026-06-12T10:00:00",
    "overall_score": 86,
    "feedback": "回答覆盖热点 key、数据库压力和互斥锁方案。"
  }
]
```

### 刷题记录详情

```http
GET /history/{interview_id}
```

响应：

```json
[
  {
    "question": "请解释 Redis 缓存击穿。",
    "answer": "热点 key 过期后大量请求打到数据库。",
    "technical_score": 86,
    "logic_score": 84,
    "experience_score": 82,
    "communication_score": 88,
    "overall_score": 86,
    "feedback": "回答较完整。"
  }
]
```

### 删除刷题记录

```http
DELETE /history/single_delete/{interview_id}
```

响应：

```json
{
  "message": "删除成功"
}
```

### 批量删除刷题记录

```http
DELETE /history/batch_delete/batch_delete
```

请求：

```json
{
  "ids": [1, 2, 3]
}
```

响应：

```json
{
  "message": "批量删除成功"
}
```

### 面试记录列表

```http
GET /interviews
```

响应：

```json
[
  {
    "id": 15,
    "resume_name": "resume.pdf",
    "status": "finished",
    "overall_score": 78,
    "summary": "整体表现稳定。",
    "topic_count": 5,
    "created_at": "2026-06-12T10:00:00",
    "finished_at": "2026-06-12T10:30:00",
    "report_generated": true
  }
]
```

### 删除面试记录

```http
DELETE /interviews/{interview_id}
```

响应：

```json
{
  "message": "删除成功"
}
```

### 批量删除面试记录

```http
DELETE /interviews/batch_delete
```

请求：

```json
{
  "ids": [15, 16]
}
```

响应：

```json
{
  "message": "批量删除成功",
  "deleted_count": 2
}
```
