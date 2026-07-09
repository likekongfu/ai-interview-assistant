"""
AI 应用开发选择题生成 Prompt。

支持 8 大专题，每个专题拆分为多个子 JD（面试知识点），
出题时按 count 均衡分配到各子 JD，保证题型多样性。
"""

# ============================================================
# 专题定义
# ============================================================

SUPPORTED_QUIZ_TOPICS = (
    "Python",
    "FastAPI 与后端",
    "MySQL 与 Redis",
    "大模型工程化",
    "RAG",
    "Agent 与 LangChain",
    "Docker 与部署",
    "项目实战",
)

# ============================================================
# 各专题的子 JD 拆分（名称、知识点范围）
# ============================================================

TOPIC_JD_MAP: dict[str, list[dict]] = {
    "Python": [
        {
            "name": "数据结构与对象模型",
            "knowledge": "list/tuple/dict/set 特性与选择、可变与不可变对象、哈希机制、成员查询、时间复杂度、元素去重",
        },
        {
            "name": "引用、拷贝与内存管理",
            "knowledge": "is vs ==、__eq__、浅拷贝与深拷贝、嵌套对象拷贝、参数传递与可变参数副作用、引用计数与垃圾回收",
        },
        {
            "name": "函数与面向对象",
            "knowledge": "*args/**kwargs、lambda、LEGB 作用域、闭包、装饰器、functools.wraps、实例/类/静态方法",
        },
        {
            "name": "迭代、资源管理与异常",
            "knowledge": "迭代器与生成器、yield、上下文管理器、with/__enter__/__exit__、try/except/else/finally 执行流程",
        },
        {
            "name": "并发与异步编程",
            "knowledge": "GIL、进程/线程/协程区别、CPU 密集与 IO 密集、async/await、asyncio 事件循环、阻塞调用排查",
        },
    ],
    "FastAPI 与后端": [
        {
            "name": "FastAPI 核心机制",
            "knowledge": "路由与路径参数、请求体与 Pydantic 校验、依赖注入（Depends）、中间件、生命周期事件",
        },
        {
            "name": "接口设计与鉴权",
            "knowledge": "RESTful 设计、状态码语义、OAuth2/JWT 鉴权流程、Cookie/Session vs Token、CORS 配置",
        },
        {
            "name": "异步与性能",
            "knowledge": "async/await 在 FastAPI 中的意义、阻塞调用对事件循环的影响、并发 vs 并行、后台任务",
        },
        {
            "name": "后端稳定性",
            "knowledge": "全局异常处理、参数校验与 422、超时与重试、限流思路、健康检查、日志与链路追踪",
        },
    ],
    "MySQL 与 Redis": [
        {
            "name": "MySQL 索引",
            "knowledge": "B+Tree 原理、聚簇索引与二级索引、最左前缀原则、覆盖索引、索引失效场景、EXPLAIN",
        },
        {
            "name": "MySQL 事务与锁",
            "knowledge": "ACID、隔离级别、脏读/幻读/不可重复读、MVCC、行锁/表锁/间隙锁、死锁排查",
        },
        {
            "name": "SQL 优化",
            "knowledge": "慢查询定位、大表分页优化、JOIN 优化、子查询 vs JOIN、批量写入、分库分表思路",
        },
        {
            "name": "Redis 缓存",
            "knowledge": "常用数据结构、缓存穿透/击穿/雪崩、过期与淘汰策略、缓存一致性方案（Cache-Aside/Write-Through）",
        },
        {
            "name": "Redis 分布式能力",
            "knowledge": "分布式锁（SETNX）、RedLock、消息队列（Stream/List）、布隆过滤器、主从/哨兵/集群",
        },
    ],
    "大模型工程化": [
        {
            "name": "Prompt 与参数",
            "knowledge": "System/User Prompt 设计、Few-shot/CoT 策略、temperature/top_p 影响、token 计算与截断",
        },
        {
            "name": "结构化输出与工具调用",
            "knowledge": "Function Calling 原理、JSON Mode vs Structured Output、工具调用错误处理、Pydantic 输出解析",
        },
        {
            "name": "稳定性与容错",
            "knowledge": "限流与指数退避重试、超时控制、fallback 策略、降级方案、幻觉检测思路",
        },
        {
            "name": "成本与评估",
            "knowledge": "token 成本估算、语义缓存/精确缓存、评测指标（准确率/召回/相关性）、人工 vs 自动评估",
        },
    ],
    "RAG": [
        {
            "name": "文档处理",
            "knowledge": "文档解析（PDF/Word/HTML）、分块策略（固定/语义/递归）、元数据保留、表格处理",
        },
        {
            "name": "Embedding 与向量检索",
            "knowledge": "Embedding 模型选择、相似度（余弦/L2/内积）、向量库（Chroma/Milvus）、索引（HNSW/IVF）",
        },
        {
            "name": "混合检索与重排",
            "knowledge": "BM25+向量混合检索、RRF 融合、ReRank（Cross-Encoder）、多路召回策略",
        },
        {
            "name": "RAG 优化",
            "knowledge": "Query 改写与扩展、HyDE、Small-to-Big 检索、Self-RAG、上下文压缩、多轮对话 RAG",
        },
        {
            "name": "RAG 评估",
            "knowledge": "检索评估（Recall/Precision/MRR/NDCG）、生成评估（Faithfulness/Answer Relevance）、RAGAS 框架",
        },
    ],
    "Agent 与 LangChain": [
        {
            "name": "Agent 基础",
            "knowledge": "ReAct 范式、Plan-and-Execute、Agent 决策循环、思考-行动-观察、自主性层级",
        },
        {
            "name": "工具调用",
            "knowledge": "Tool 定义与注册、参数 Schema、工具调用错误处理与重试、权限控制",
        },
        {
            "name": "状态与记忆",
            "knowledge": "短期/长期记忆、消息窗口管理、摘要记忆、向量记忆、对话状态管理",
        },
        {
            "name": "LangGraph 工作流",
            "knowledge": "StateGraph、节点与边、条件路由、子图、Human-in-the-Loop、检查点与回放",
        },
        {
            "name": "安全与可观测性",
            "knowledge": "Prompt 注入防护、工具调用沙箱、输出审查、LangSmith/LangFuse 追踪、token 监控",
        },
    ],
    "Docker 与部署": [
        {
            "name": "Docker 基础",
            "knowledge": "镜像分层、Dockerfile 最佳实践（多阶段构建）、常用命令、数据卷与挂载",
        },
        {
            "name": "Compose 与网络",
            "knowledge": "docker-compose.yml 结构、service 定义、网络模式（bridge/host）、depends_on/healthcheck",
        },
        {
            "name": "Nginx 与 HTTPS",
            "knowledge": "反向代理配置、负载均衡策略、SSL 证书、静态资源服务、WebSocket 代理",
        },
        {
            "name": "生产环境排障",
            "knowledge": "容器资源限制、日志收集、优雅关闭、健康检查、常见启动失败原因排查",
        },
    ],
    "项目实战": [
        {
            "name": "项目架构",
            "knowledge": "前后端分离架构、微服务 vs 单体、API 网关、消息队列、技术选型依据",
        },
        {
            "name": "模型调用",
            "knowledge": "多模型接入与切换、流式输出（SSE/WebSocket）、上下文窗口管理、多模态处理",
        },
        {
            "name": "数据库与鉴权",
            "knowledge": "ORM 设计、数据库迁移、连接池管理、JWT 完整鉴权流程、RBAC 权限模型",
        },
        {
            "name": "部署与排障",
            "knowledge": "CI/CD 流程、环境变量管理、日志与监控、线上问题定位、灰度发布",
        },
        {
            "name": "项目优化",
            "knowledge": "接口响应优化、缓存策略、异步任务解耦、安全加固（SQL注入/XSS/CSRF）、代码可维护性",
        },
    ],
}


def build_quiz_prompt(topic: str, count: int, difficulty: str, jd: str = "") -> str:
    """构造 AI 应用开发选择题生成 Prompt（精简版，减少 token 消耗）。"""

    jd_section = f"\n岗位 JD 参考：\n{jd.strip()}\n" if jd and jd.strip() else ""
    topic_rules = _build_topic_rules(topic, count)

    return f"""
你是 AI 应用开发面试官，生成「{topic}」方向单选题 {count} 道，难度 {difficulty}。
难度：easy=基础概念；medium=分析理解；hard=原理/场景判断。
{jd_section}
{topic_rules}
只输出合法 JSON，不要 Markdown、注释或额外文字。JSON 结构：
{{
  "questions": [
    {{
      "id": "qN",
      "stem": "题干",
      "options": [{{"key":"A","text":"..."}},{{"key":"B","text":"..."}},{{"key":"C","text":"..."}},{{"key":"D","text":"..."}}],
      "correct_answer": "B",
      "explanation": "80字内说明正确原因和其他选项主要错误",
      "knowledge_point": "知识点",
      "difficulty": "{difficulty}"
    }}
  ]
}}
要求：每题必须恰好 A/B/C/D 四项，correct_answer 只能是 A/B/C/D；只有一个正确答案；题干上下文充分；避免多答案模糊题、否定题、冷门 API、重复题；代码题结果唯一且不要用 Markdown 围栏。
单题只考一个明确判断点，不要把多个知识点揉成“大而全”题干；不要使用“以下描述正确的是/错误的是”这类宽泛题；3 个干扰项必须明确错误，不能只是描述其他正确事实；如果多个选项都有正确成分，内部重写。
内部自检但不要输出自检过程：答案唯一、解析一致、JSON 合法、题目不重复。
""".strip()


def build_single_quiz_prompt(
    topic: str,
    question_index: int,
    total_count: int,
    difficulty: str,
    jd: str = "",
    exclude_stems: list[str] | None = None,
) -> str:
    """构造单题生成 Prompt，用于并发生成，减少单次 LLM 输出长度。"""

    jd_section = f"\n岗位 JD 参考：{jd.strip()}" if jd and jd.strip() else ""
    topic_rule = _build_single_topic_rule(topic, question_index)
    exclude_section = ""
    if exclude_stems:
        examples = "；".join(stem[:40] for stem in exclude_stems if stem)
        if examples:
            exclude_section = f"\n避免与这些已出题题干重复：{examples}"

    return f"""
生成 1 道「{topic}」AI 应用开发面试单选题，难度 {difficulty}，题号 q{question_index}/{total_count}。
{topic_rule}{jd_section}{exclude_section}
只输出合法 JSON 对象，不要 Markdown、注释或额外文字。
格式：
{{
  "id": "q{question_index}",
  "stem": "题干，不要包含 A/B/C/D 选项",
  "options": [{{"key":"A","text":"选项"}},{{"key":"B","text":"选项"}},{{"key":"C","text":"选项"}},{{"key":"D","text":"选项"}}],
  "correct_answer": "A",
  "explanation": "80字内解释正确答案和主要干扰项错误点",
  "knowledge_point": "知识点",
  "difficulty": "{difficulty}"
}}
要求：A/B/C/D 恰好四项；correct_answer 只能是 A/B/C/D；只有一个正确答案；不要省略号或占位选项；题干不要混入选项；代码题结果必须唯一。
质量要求：题干只考一个明确判断点，不要把多个知识点揉成“大而全”综合题；不要使用“以下描述正确的是/错误的是”这类宽泛题；3 个干扰项必须有明确错误，不能只是描述其他正确事实；如果多个选项都有正确成分，必须重写。
""".strip()


def _build_topic_rules(topic: str, count: int) -> str:
    """根据 topic 查找子 JD 并生成分布规则。"""

    jds = TOPIC_JD_MAP.get(topic)
    if not jds:
        return ""

    jd_count = len(jds)

    if count == jd_count:
        dist = f"每题对应一个 JD：q1→JD 1 ... q{count}→JD {jd_count}。"
    elif count < jd_count:
        dist = f"优先覆盖前 {count} 个 JD（JD 1-JD {count}），各出一道。"
    else:
        dist = f"从 {jd_count} 个 JD 轮转出题，不连续出同类：q1→JD 1 ... q{jd_count}→JD {jd_count}, q{jd_count+1}→JD 1..."

    jd_lines = []
    for i, jd in enumerate(jds, 1):
        jd_lines.append(f"JD {i}「{jd['name']}」：{jd['knowledge']}")

    jd_text = "\n".join(jd_lines)

    return f"""子 JD：
{jd_text}
分布规则：{dist}
至少 1 道代码分析题 + 1 道工程场景题。""".strip()


def _build_single_topic_rule(topic: str, question_index: int) -> str:
    """为单题选择一个子 JD，保证并发生成时题型分布相对均衡。"""

    jds = TOPIC_JD_MAP.get(topic)
    if not jds:
        return ""

    jd = jds[(question_index - 1) % len(jds)]
    extra = ""
    if question_index == 1:
        extra = "题型：代码分析题优先。"
    elif question_index == 2:
        extra = "题型：工程场景题优先。"

    return f"考查 JD「{jd['name']}」：{jd['knowledge']}。{extra}"
