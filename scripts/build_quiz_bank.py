"""构建 quiz-bank.js 题库文件。"""
import json, os

questions = []

def q(qid, topic, stem, A, B, C, D, ans, expl, kp, diff):
    questions.append(dict(id=qid, topic=topic, stem=stem,
        options=[dict(key="A",text=A),dict(key="B",text=B),dict(key="C",text=C),dict(key="D",text=D)],
        correct_answer=ans, explanation=expl, knowledge_point=kp, difficulty=diff))

# ==================== Python (15) ====================
q("py_001","Python","在 Python 3 中执行 a=[1,2]; b=a; b.append(3); print(a)，输出？","[1, 2]","[1, 2, 3]","[1, 2, 3, 3]","报错：list 不可变","B","B 正确。a 和 b 引用同一个 list 对象，b.append(3) 修改了该对象，a 也会看到变化。A 忽略引用共享；C 误以为 append 追加两次；D 混淆 list(可变)和 tuple(不可变)。","Python 可变对象与引用共享","easy")
q("py_002","Python","Python 中 is 和 == 的区别？","is 比较值，== 比较内存地址","is 比较内存地址，== 默认调用 __eq__ 比较值","两者完全等价","is 用于可变，== 用于不可变","B","B 正确。is 判断是否指向同一对象，== 默认调用 __eq__ 比较值。A 说反了；C 如 a=[1];b=[1] 则 a is b 为 False 但 a==b 为 True；D 是误解。","Python is 与 ==","easy")
q("py_003","Python","以下关于默认参数哪项正确？\ndef add_item(item, target=[]):\n    target.append(item)\n    return target","每次调用 target 是新的空列表","target 只在函数定义时创建一次，多次调用共享同一个列表","抛出 SyntaxError","只有第一次调用使用默认值","B","B 正确。默认参数在定义时只求值一次，后续复用同一对象。应使用 target=None 再判空创建新列表。A 常见误解；C/D 与实际行为不符。","Python 可变默认参数陷阱","medium")
q("py_004","Python","FastAPI 接口需调用大模型 API(约 3 秒)，哪种策略最合适？","async def + httpx.AsyncClient 异步调用","def 同步函数 + requests","threading.Thread 每个请求新建线程","multiprocessing.Process 每个请求新建进程","A","A 正确。I/O 密集用 async/await，等待时处理其他请求。B 阻塞线程；C 受 GIL 限制；D 进程开销更大。","async/await 在 AI 应用中实践","medium")
q("py_005","Python","关于 Python 装饰器哪项正确？","只能在类的方法上使用","本质是接收函数并返回新函数的高阶函数","装饰后原函数 __name__ 不变","一个函数只能用一个装饰器","B","B 正确。装饰器是高阶函数。A 任何函数可用；C 变成 wrapper 名需 @functools.wraps；D 可叠加多个。","Python 装饰器原理","easy")
q("py_006","Python","Python 3 中：\nimport copy\na=[[1,2],[3,4]]\nb=copy.copy(a)\nb[0].append(5)\nprint(a[0])\n输出？","[1, 2]","[1, 2, 5]","[[1, 2, 5], [3, 4]]","报错","B","B 正确。浅拷贝只复制外层，内层列表共享引用。b[0].append(5) 影响 a[0]。需完全独立应用 deepcopy。","Python 浅拷贝与深拷贝","medium")
q("py_007","Python","关于 Python 生成器哪项正确？","生成器用 return 返回值","生成器一次性加载所有值到内存","生成器用 yield，惰性求值并保存状态","生成器只能迭代一次","C","C 正确。生成器惰性求值适合大文件、流式数据。A 混淆 return/yield；B 是列表行为；D 重新调用创建新生成器。","Python 生成器与惰性求值","easy")
q("py_008","Python","以下哪个可作为 dict 的 key？","[1, 2, 3]","{'a': 1}","(1, 2, 3)","{1, 2, 3}","C","C 正确。tuple 不可变(可哈希)可作为 key。A list 可变；B dict 可变；D set 可变。dict key 必须可哈希。","Python 可哈希对象","easy")
q("py_009","Python","关于 Python GIL 哪项正确？","GIL 使 Python 完全无法并发","GIL 是 CPython 全局解释器锁，同一时刻只有一个线程执行字节码。I/O 密集用多线程，CPU 密集用多进程","所有 Python 实现都有 GIL","async/await 可绕过 GIL","B","B 正确。GIL 只存在于 CPython。async/await 协程并发不绕过 GIL，CPU 密集仍需多进程。","Python GIL 与并发模型选择","medium")
q("py_010","Python","Python try/except/else/finally 执行顺序？","finally 只在有异常时执行","else 在 try 无异常时执行，finally 无论如何都执行","else 和 finally 不能同时用","finally 在 except 之前执行","B","B 正确。无异常→else→finally；有异常→except→finally。finally 总是执行常用于资源释放。","Python 异常处理执行流程","easy")
q("py_011","Python","关于闭包，以下输出什么？\ndef outer(x):\n    def inner(y):\n        return x+y\n    return inner\nf=outer(10)\nprint(f(5))","报错：x 未定义","15","5","None","B","B 正确。inner 记住了 outer 作用域中的 x=10，调用 f(5) 返回 15。闭包=内部函数引用外部函数变量。","Python 闭包与 LEGB 作用域","medium")
q("py_012","Python","关于上下文管理器哪项正确？","with 只能用于文件操作","with 通过 __enter__ 和 __exit__ 管理资源，无论是否异常 __exit__ 都会执行","不能用类实现","__exit__ 只在无异常时执行","B","B 正确。with 确保资源正确释放，__exit__ 必然调用。文件、DB 连接、锁等都可用上下文管理器。","Python 上下文管理器原理","medium")
q("py_013","Python","@staticmethod 和 @classmethod 的区别？","没有区别","@classmethod 第一个参数是 cls(类本身)，可访问类属性；@staticmethod 没有隐含参数，类似普通函数只是放在类命名空间","@staticmethod 可访问实例属性","@classmethod 只能用于继承","B","B 正确。classmethod 接收 cls 可访问类变量；staticmethod 不接收 self 或 cls。","Python classmethod vs staticmethod","medium")
q("py_014","Python","__slots__ 的作用？","提高方法调用速度","限制实例只能有指定属性，阻止自动创建 __dict__，节省内存。适合创建大量小对象的场景","限制类只能被继承一次","给类添加装饰器","B","B 正确。__slots__ 省去 __dict__ 开销。大量实例时内存节省显著。但失去动态添加属性的灵活性。","Python __slots__ 内存优化","medium")
q("py_015","Python","asyncio 中 create_task 和 await 直接调用的区别？","完全相同","create_task 立即调度协程并发执行返回 Task；直接 await 阻塞等待完成后才继续。前者并发后者顺序","create_task 只能用于 CPU 密集","await 比 create_task 更快","B","B 正确。create_task 提交到事件循环并发跑，适合同时发多个 API 请求；直接 await 是顺序等待。","asyncio create_task 并发调度","hard")

# ==================== FastAPI 与后端 (13) ====================
q("be_001","FastAPI 与后端","FastAPI 的 Depends 依赖注入，哪项正确？","Depends 只能获取数据库会话","Depends 可用于获取 DB 会话、校验用户、解析参数等多种场景","Depends 是 FastAPI 独有的","Depends 只能用在第一层参数中","B","B 正确。Depends 可用于 DB 会话、鉴权、参数校验等横切关注点，还可嵌套。A 过于狭隘；C 其他框架也有类似机制；D 可嵌套依赖。","FastAPI 依赖注入","easy")
q("be_002","FastAPI 与后端","设计 AI 回答生成接口，哪种做法正确？","在 async def 中用 time.sleep(5) 模拟延迟","在 async def 中用 await asyncio.sleep(5)，并用异步 HTTP 客户端调用大模型 API","所有接口用 def 同步函数，FastAPI 自动优化","用 BackgroundTasks 直接返回结果","B","B 正确。异步接口需用异步库才能发挥事件循环优势。A time.sleep 是阻塞调用会卡事件循环；C 同步 def 放线程池大量并发性能下降；D BackgroundTasks 不能直接返回结果。","FastAPI 异步接口正确用法","medium")
q("be_003","FastAPI 与后端","关于 JWT 鉴权，哪项正确？","JWT 一旦签发无法失效","JWT 无状态，服务端不需要存 session，签名保证未被篡改","JWT payload 是加密的，客户端无法读取","JWT 必须存储在数据库中","B","B 正确。JWT 核心优势是无状态。A 可通过黑名单提前失效；C payload 只是 Base64 编码不是加密；D 与无状态理念相反。","JWT 鉴权原理","easy")
q("be_004","FastAPI 与后端","FastAPI 中大模型调用偶尔超时，哪种异常处理最合适？","让异常直接抛出，客户端自行处理","用 @app.exception_handler 统一捕获，返回结构化错误响应","每个接口 try/except 逐个捕获返回不同 HTML","middleware 静默吞掉所有异常","B","B 正确。统一异常处理便于前端展示和日志追踪。A 用户看到不友好 500；C 不符合 DRY 原则；D 掩盖问题导致排查困难。","FastAPI 全局异常处理","medium")
q("be_005","FastAPI 与后端","Pydantic 在 FastAPI 中的主要作用？","仅用于数据库 ORM 模型定义","请求参数校验、响应模型约束和数据序列化，在业务逻辑前拦截不合法数据","用于前端 CSS 样式管理","仅生成 API 文档，不影响数据校验","B","B 正确。Pydantic 是 FastAPI 数据校验核心，自动校验类型和约束，同时驱动 OpenAPI 文档。A 混淆 Pydantic 和 SQLAlchemy；C/D 低估其作用。","Pydantic 数据校验","easy")
q("be_006","FastAPI 与后端","FastAPI 中间件（Middleware）的主要作用？","替代 Depends 做参数校验","在请求到达路由前和响应返回前执行通用逻辑，如日志、CORS、请求计时","管理数据库连接池","生成 API 文档","B","B 正确。中间件是请求/响应链上的横切关注点，适合日志、认证、CORS 头等。A Depends 才是参数校验；C 由 SQLAlchemy 管理；D 由 FastAPI 自动生成。","FastAPI 中间件机制","easy")
q("be_007","FastAPI 与后端","FastAPI 中 CORS 配置通常在哪里处理？","在每个路由函数中手动设置响应头","使用 CORSMiddleware 中间件统一配置允许的源、方法和头","在 Pydantic 模型中定义","不需要配置，FastAPI 自动处理跨域","B","B 正确。FastAPI 通过 CORSMiddleware 统一处理跨域，配置 allow_origins、allow_methods 等。A 繁琐且易遗漏；C Pydantic 不管 CORS；D 默认不允许跨域。","FastAPI CORS 配置","easy")
q("be_008","FastAPI 与后端","FastAPI 中 BackgroundTasks 适合什么场景？","返回结果前必须完成的操作","响应返回后执行的轻量后处理，如发送邮件通知、写入日志","替代 Celery 做分布式任务队列","处理用户请求的主业务逻辑","B","B 正确。BackgroundTasks 在响应返回后执行轻量任务，适合发邮件、写日志等。A 会阻塞响应；C 重量级任务应用 Celery 等；D 主逻辑应在路由中处理。","FastAPI BackgroundTasks","medium")
q("be_009","FastAPI 与后端","FastAPI 中如何实现接口限流？","FastAPI 内置限流功能，设置参数即可","通常通过中间件或依赖注入结合 Redis 计数器实现，FastAPI 本身不内置限流","在 Pydantic 模型中配置 max_rate","数据库存储限流规则","B","B 正确。FastAPI 不内置限流，需自行实现或使用 slowapi 等库。常见方案：Redis 滑动窗口 + Depends 校验。","FastAPI 接口限流方案","medium")
q("be_010","FastAPI 与后端","FastAPI 路由中路径参数和查询参数的区别？","没有区别","路径参数是 URL 路径的一部分(如 /users/{id})，查询参数在 ? 之后(如 ?page=1)。路径参数通常必填，查询参数通常可选","路径参数只能是数字","查询参数必须用 POST 方法传递","B","B 正确。路径参数是 RESTful URL 的组成部分，查询参数用于过滤/分页等可选参数。A 有明确区别；C 可以是字符串；D 查询参数一般用 GET。","FastAPI 路径参数与查询参数","easy")
q("be_011","FastAPI 与后端","FastAPI 中依赖注入可以嵌套吗？","不能嵌套","可以嵌套——一个 Depends 函数可以依赖另一个 Depends 的结果，形成依赖链。框架自动解析并注入","只能嵌套一层","嵌套会降低性能不能使用","B","B 正确。FastAPI 依赖注入支持嵌套：get_db→get_current_user(db)→权限校验。框架按拓扑序解析，缓存同请求内的重复依赖。","FastAPI 依赖注入嵌套","medium")
q("be_012","FastAPI 与后端","AI 应用中设计流式接口(SSE)的 FastAPI 实现要点？","使用 return 直接返回结果","使用 StreamingResponse 包装异步生成器，设置 media_type='text/event-stream'。生成器内逐块 yield SSE 格式数据","使用 WebSocket 替代，SSE 已过时","用 multipart/form-data 上传","B","B 正确。FastAPI 的 StreamingResponse + async generator 是实现 SSE 的标准方案。yield 大模型逐 token 输出，前端 EventSource 接收。","FastAPI StreamingResponse SSE 流式接口","medium")
q("be_013","FastAPI 与后端","FastAPI 中如何实现请求日志追踪？","不需要日志","使用 Middleware 记录每个请求的 method、path、耗时、状态码，配合 request_id 实现全链路追踪","只能靠 print 调试","FastAPI 自动生成完整日志","B","B 正确。通过 Middleware 在请求进入时记录开始时间、生成 request_id，响应时记录耗时。结合 structlog 或 loguru 输出结构化日志，方便排查问题。","FastAPI 请求日志与链路追踪","easy")

# ==================== MySQL 与 Redis (12) ====================
q("db_001","MySQL 与 Redis","MySQL 中哪种情况会导致索引失效？","WHERE column = 'value'","对索引列使用函数，如 WHERE YEAR(create_time) = 2024","WHERE column IN (1,2,3)","WHERE column BETWEEN 1 AND 10","B","B 正确。对索引列使用函数导致无法使用索引，需全表扫描。应改写为范围查询。A/C/D 都能正常使用索引。","MySQL 索引失效场景","medium")
q("db_002","MySQL 与 Redis","以下哪种场景最适合用 Redis 缓存？","存储用户密码","缓存高频热点数据(如热门帖子、模型配置)，减少 DB 压力","替代 MySQL 做持久化存储","存储大于 100MB 的文件","B","B 正确。Redis 作为内存缓存适合高频读低延迟场景。A 密码应哈希存 DB；C Redis 不适合替代关系型 DB；D 大文件应用对象存储。","Redis 缓存适用场景","easy")
q("db_003","MySQL 与 Redis","MySQL MVCC 主要用于解决什么？","提高写入速度","实现事务隔离，读不阻塞写、写不阻塞读","压缩存储空间","自动创建索引","B","B 正确。MVCC 通过保存多版本数据实现非锁定一致性读，是 InnoDB REPEATABLE READ 的核心机制。","MySQL MVCC 原理","medium")
q("db_004","MySQL 与 Redis","AI 应用中哪个场景适合 Redis 分布式锁？","保证同一时刻只有一个 Worker 处理同一任务","存储聊天历史","替换 MySQL 做用户表主存储","生成自增主键","A","A 正确。分布式锁是 Redis 经典场景，SETNX+过期时间确保互斥。B 适合 DB 或消息队列；C Redis 不适合关系型存储；D 自增用 AUTO_INCREMENT。","Redis 分布式锁","easy")
q("db_005","MySQL 与 Redis","什么是缓存穿透？哪种防护最有效？","缓存服务器宕机，防护是增加节点","大量请求查不存在的数据绕过缓存打 DB，防护是布隆过滤器或缓存空值","缓存集中过期导致请求落 DB，防护是随机化过期时间","单个热点 key 过期，防护是互斥锁","B","B 正确。缓存穿透=查不存在的数据。用布隆过滤器预判或缓存 null(短过期)。A 是服务不可用；C 是缓存雪崩；D 是缓存击穿。三者易混淆。","缓存穿透/击穿/雪崩","medium")
q("db_006","MySQL 与 Redis","MySQL 聚簇索引的特点？","一张表可以有多个聚簇索引","聚簇索引的叶子节点存储完整行数据，InnoDB 中主键默认就是聚簇索引","聚簇索引存储在独立文件中","聚簇索引比非聚簇索引查询慢","B","B 正确。InnoDB 表数据按主键(聚簇索引)的 B+Tree 组织，叶子节点存整行数据。二级索引叶子节点存主键值，查询需回表。","MySQL 聚簇索引与二级索引","medium")
q("db_007","MySQL 与 Redis","MySQL 死锁的常见原因和排查方法？","死锁只发生在单条 SQL 中","两个事务互相等待对方持有的锁导致。排查可用 SHOW ENGINE INNODB STATUS 查看最近死锁信息","死锁无法避免只能重启数据库","死锁只在 MyISAM 引擎发生","B","B 正确。死锁是多事务循环等待锁资源。InnoDB 自动检测并回滚代价小的事务。排查用 SHOW ENGINE INNODB STATUS。","MySQL 死锁排查","hard")
q("db_008","MySQL 与 Redis","MySQL 慢查询如何定位和优化？","只能靠猜测优化","开启 slow_query_log 记录慢 SQL，用 EXPLAIN 分析执行计划，根据 type/rows/Extra 字段判断是否走索引","直接加更多索引即可","升级 MySQL 版本解决所有慢查询","B","B 正确。慢查询优化流程：开启慢日志→定位慢 SQL→EXPLAIN 分析→优化索引/改写 SQL。EXPLAIN 的 type 列直接反映效率。","MySQL 慢查询定位与 EXPLAIN","medium")
q("db_009","MySQL 与 Redis","Redis Stream 适合什么场景？","替代 MySQL 做主存储","轻量级消息队列，支持消费者组、消息确认和持久化，适合 AI 应用中的异步任务分发","存储用户密码","替代 Redis String 做缓存","B","B 正确。Redis Stream 是 Redis 5.0+ 的消息队列数据结构，支持消费者组、ACK 机制、消息回溯。适合轻量异步任务。","Redis Stream 消息队列","medium")
q("db_010","MySQL 与 Redis","Redis 哨兵(Sentinel)的主要功能？","提升单机 Redis 的读写性能","监控主从节点，在主节点故障时自动完成故障转移(Failover)，实现高可用","替代 Redis 集群做数据分片","提供 SQL 查询接口","B","B 正确。Sentinel 实现 Redis 高可用：监控、通知、自动故障转移。A 提升性能靠集群分片；C 集群做分片 Sentinel 做高可用。","Redis 哨兵高可用","easy")
q("db_011","MySQL 与 Redis","MySQL 中 LEFT JOIN 和 INNER JOIN 的区别？","没有区别","INNER JOIN 只返回两表匹配的行，LEFT JOIN 返回左表全部行，右表无匹配时填充 NULL","LEFT JOIN 只返回左表有右表没有的行","INNER JOIN 比 LEFT JOIN 总是慢","B","B 正确。INNER JOIN=交集，LEFT JOIN=左表全量+右表匹配。实际开发中查询「所有用户及其订单(含无订单用户)」必须用 LEFT JOIN。","MySQL JOIN 类型与选择","easy")
q("db_012","MySQL 与 Redis","MySQL 索引的最左前缀原则是指什么？","索引必须从最左边的列开始创建","联合索引 (a,b,c) 中，查询条件必须包含 a 才能利用索引；跳过 a 直接查 b 或 c 索引失效","索引只能建在表的最左列","索引名字必须以 left_ 开头","B","B 正确。联合索引按列顺序组织，查询从最左列开始匹配。联合索引(a,b,c)：WHERE a=1 可用；WHERE b=1 不可用；WHERE a=1 AND c=3 只用 a。","MySQL 最左前缀原则","medium")

# ==================== 大模型工程化 (12) ====================
q("llm_001","大模型工程化","temperature=0 和 temperature=1 的区别？","temperature=0 完全随机，=1 完全确定","temperature 越接近 0 越确定(适合代码/分类)，越接近 1 越多样(适合创意)","控制输出长度","计费参数","B","B 正确。低值更确定适合结构化输出，高值更随机适合创意。A 说反；C 混淆 max_tokens；D 错误。","temperature 参数","easy")
q("llm_002","大模型工程化","Function Calling 的核心原理？","模型直接执行 Python 函数","模型返回结构化 JSON 表示函数名和参数，由开发者代码实际执行，结果传回模型","模型自动安装 Python 包","模型翻译 SQL 语句","B","B 正确。Function Calling 本质是模型输出意图和参数的 JSON，调用方执行并返回结果，是 Agent 工具调用的基础。","Function Calling 原理","medium")
q("llm_003","大模型工程化","遇到 429 限流错误，哪种重试策略最合理？","立即重试直到成功","指数退避：等 1s、2s、4s、8s 逐步增加间隔","放弃请求直接报错","同时发起 10 个并行请求提高命中率","B","B 正确。指数退避是限流标准策略，逐步增加等待避免雪崩，生产环境还应加 jitter。A 可能触发更严格限流；C 体验差；D 加剧限流。","API 限流与重试策略","medium")
q("llm_004","大模型工程化","关于 Few-shot Prompting，哪项正确？","提供 0 个示例","提供几个输入输出示例帮助模型理解格式，是提升输出质量的有效手段","只适用文本分类","示例越多越好没上限","B","B 正确。Few-shot 通过示例引导模型。A 是 Zero-shot；C 适用各种任务；D 示例过多增加 token 消耗且超上下文窗口有害。","Few-shot Prompting","easy")
q("llm_005","大模型工程化","语义缓存的主要目的？","加快模型推理速度","对相似问题缓存复用，减少重复调用 API，降低延迟和成本","替代向量数据库","提高输出随机性","B","B 正确。语义缓存通过 Embedding 相似度判断语义相近问题，命中后直接返回缓存回答。FAQ、客服场景效果显著。","语义缓存","medium")
q("llm_006","大模型工程化","如何估算一次 API 调用的 token 消耗？","只能等账单出来才知道","1 个中文字约 1.5-2 tokens，1 个英文单词约 1.3 tokens。可用 tiktoken 等库精确计算，或使用 API 返回的 usage 字段","按字符数 1:1 计算","每次调用固定消耗 1000 tokens","B","B 正确。token 计算规则因模型而异。tiktoken 可本地预估，API 响应中 usage 字段给出实际消耗。A 有预估方法；C 中文不等于 1:1；D 每次不同。","Token 计算与成本估算","easy")
q("llm_007","大模型工程化","大模型 API 调用中 fallback 策略指什么？","调用失败后放弃","主模型不可用时自动切换到备用模型(如 DeepSeek→OpenAI)，保证服务可用性","降低 temperature 提高稳定性","增加 prompt 长度","B","B 正确。fallback 是容错核心：主模型超时/限流/错误时自动切备用模型，保证业务连续性。","大模型 Fallback 容错策略","easy")
q("llm_008","大模型工程化","什么是大模型的幻觉？如何检测？","模型输出总是错误的","模型生成看似合理但与事实不符的内容。检测方法包括：事实性校验(对比知识库)、引用溯源、置信度评估","模型运行时的内存错误","API 返回的 HTTP 错误","B","B 正确。幻觉是 LLM 的核心挑战之一，常见检测：RAG 引用对比、NLI 模型校验、输出不确定性评估。A 过于绝对；C/D 不是幻觉概念。","大模型幻觉检测","medium")
q("llm_009","大模型工程化","JSON Mode 和 Structured Output 的区别？","完全相同","JSON Mode 保证输出合法 JSON 但不保证 Schema；Structured Output 严格遵循预定义的 JSON Schema，字段类型和必填项都必须匹配","JSON Mode 比 Structured Output 更严格","两者都不保证 JSON 格式","B","B 正确。JSON Mode 只保证合法 JSON，Structured Output 进一步约束 Schema 结构。后者更适合生产环境的数据提取。","JSON Mode vs Structured Output","medium")
q("llm_010","大模型工程化","评估大模型输出质量，哪个指标最关注「回答是否忠实于给定上下文」？","BLEU","Faithfulness(忠实度)，衡量回答是否基于提供的上下文而非模型自身知识","Perplexity(困惑度)","ROUGE","B","B 正确。Faithfulness 是 RAG 场景核心指标，判断回答是否严格依据检索到的文档。A BLEU 用于机器翻译；C 评估语言模型本身；D ROUGE 用于摘要。","大模型评估指标 Faithfulness","medium")
q("llm_011","大模型工程化","Prompt 中 System Prompt 和 User Prompt 的分工？","可以混用无区别","System Prompt 设定角色、规则和全局约束，优先级高；User Prompt 是具体任务输入。两者分层设计可防注入并提高稳定性","System Prompt 只能写一句话","User Prompt 用于设定角色","B","B 正确。分层设计是 Prompt 工程基础：System 设定角色，User 传具体任务。分离后用户输入更难覆盖系统指令，是防注入的重要手段。","System Prompt vs User Prompt 分层设计","easy")
q("llm_012","大模型工程化","大模型 API 调用中 max_tokens 参数设置过小的后果？","响应更快质量更高","输出被截断，可能 JSON 不完整导致解析失败。应合理估计输出长度并设置足够余量","自动扩展无影响","只影响费用不影响结果","B","B 正确。max_tokens 限制输出长度，过小会导致截断——结构化输出场景尤其致命(JSON 不完整)。建议设置 1.5-2 倍余量。","max_tokens 参数与输出截断","easy")

# ==================== RAG (12) ====================
q("rag_001","RAG","RAG 的基本流程？","提问→随机返回文档","提问→检索相关文档→文档+问题送大模型→生成基于文档的回答","提问→大模型从训练数据回忆答案","提问→翻译多语言→分别搜索→合并","B","B 正确。RAG 核心是先检索、后生成，用外部知识库补充模型知识盲区减少幻觉。A 忽略检索相关性；C 是纯 LLM；D 不是标准 RAG。","RAG 基本原理","easy")
q("rag_002","RAG","文档分块大小如何影响检索效果？","不影响","太小丢失上下文，太大引入噪声，应根据文档类型和 Embedding 模型 token 限制选择","越大越好","越小越好","B","B 正确。chunk size 是关键参数：太小语义不完整，太大稀释关键信息。常见 512-1024 tokens 是经验起点需按场景调优。","RAG 文档分块策略","medium")
q("rag_003","RAG","混合检索的目的？","同时用两个大模型","结合 BM25 关键词检索和向量语义检索互补——BM25 擅长精确匹配，向量擅长语义理解","中英文分别检索","检索时训练 Embedding","B","B 正确。混合检索=BM25+向量，通过 RRF 融合排序。纯向量可能漏精确术语，纯 BM25 不理解同义表达。","RAG 混合检索与 RRF","medium")
q("rag_004","RAG","ReRank 重排序的作用？","替换向量检索","用更精细模型(Cross-Encoder)对初检候选重新打分，提升最终文档质量","随机打乱增加多样性","压缩文档省 token","B","B 正确。向量检索召回 Top-K(高召回)，Cross-Encoder 精排(高精度)，取 Top-N 送 LLM。A/C/D 不是 ReRank。","RAG ReRank 重排序","medium")
q("rag_005","RAG","Embedding 模型选择策略哪项合理？","所有语言用英文模型","根据文档语言和领域选择匹配模型，中文优先用支持中文的模型","越大越好不考虑延迟成本","用 Word2Vec 替代现代模型","B","B 正确。选模型要考虑语言匹配、领域适配、延迟和成本。A 跨语言效果差；C 忽略部署限制；D Word2Vec 无法捕捉上下文语义。","Embedding 模型选择","easy")
q("rag_006","RAG","Query 改写的目的是什么？","翻译成英文","将用户口语化、不完整的查询改写为更适合检索的规范表达，可包括指代消解、省略补全、关键词提取","压缩查询减少 token","加密用户查询","B","B 正确。Query 改写是 RAG 的关键前置步骤：多轮对话中将「它呢」补全为「Python 的 GIL 呢」。A/C/D 不是 Query 改写的目的。","RAG Query 改写与扩展","medium")
q("rag_007","RAG","HyDE(Hypothetical Document Embeddings)的原理？","用真实文档的 Embedding 直接检索","先用 LLM 生成一个假设性回答文档，再对该假设文档做 Embedding 用于检索，解决用户查询和文档之间语义鸿沟","混合多种 Embedding 模型","将文档翻译后再检索","B","B 正确。HyDE 核心：query→LLM 生成假设文档→embed 假设文档→检索真实文档。弥补短 query 和长文档的向量空间不对齐。","RAG HyDE 假设文档嵌入","medium")
q("rag_008","RAG","Self-RAG 相比传统 RAG 的改进是什么？","不需要检索了","模型在生成过程中自主判断是否需要检索、检索结果是否相关、生成内容是否有据可依，通过反思 token 控制检索和生成质量","使用更大的 Embedding 模型","只检索一次","B","B 正确。Self-RAG 通过特殊 token(Retrieve/Relevance/Support 等)让模型自我反思检索和生成质量。A 仍需检索；C 不是核心创新。","Self-RAG 反思增强检索","hard")
q("rag_009","RAG","RAG 中上下文压缩的作用？","减少文档数量","对检索到的文档内容进行摘要或关键信息提取，去除冗余，在有限的上下文窗口中塞入更多有效信息","压缩 Embedding 维度","减少模型参数","B","B 正确。上下文压缩对检索结果做精简，保留与 query 最相关的片段，避免 token 浪费。","RAG 上下文压缩","medium")
q("rag_010","RAG","RAGAS 评估框架主要评估哪些维度？","只评估检索速度","Faithfulness(忠实度)、Answer Relevance(答案相关性)、Context Precision(上下文精确度)、Context Recall(上下文召回率)等多个维度","只评估生成语法的正确性","评估 Embedding 模型的训练损失","B","B 正确。RAGAS 是 RAG 系统的主流评估框架，从检索和生成两个角度多维度打分。A/C 太片面；D 不是 RAGAS 的功能。","RAGAS 评估框架","medium")
q("rag_011","RAG","RAG 中多轮对话如何处理上下文？","每轮独立检索，忽略历史","将对话历史压缩为上下文摘要或改写当前 query(指代消解)，再检索。例如用户问「它怎么实现」→改写为「Python 的 GIL 怎么实现」","把所有历史消息都拼接到检索 query 中","多轮对话不需要特殊处理","B","B 正确。多轮 RAG 核心挑战是上下文理解。标准做法：用 LLM 对当前 query 做指代消解和上下文补全，生成独立的检索 query。","RAG 多轮对话上下文处理","medium")
q("rag_012","RAG","RAG 检索结果中 Top-K 选多大合适？","越大越好","Top-K 是精度和效率的平衡——K 太小召回不足，K 太大增加噪声和 token 消耗。典型值 3-10，需根据文档长度和 LLM 窗口调优","固定为 1","固定为 100","B","B 正确。K=1 可能漏关键信息，K=100 引入大量噪声。实践中先设 K=5-8 做基准，按场景调优。配合 ReRank 可先取较大 K(如 20)再精选 Top-N。","RAG Top-K 检索参数调优","medium")

# ==================== Agent 与 LangChain (12) ====================
q("ag_001","Agent 与 LangChain","ReAct 范式的核心思想？","先执行所有工具再一次性生成答案","交替思考(推理)和行动(调工具)，观察结果后继续循环直到完成","模型只生成文本，工具由定时器触发","一次只能调一个工具","B","B 正确。ReAct=Thought→Action→Observation 循环，让 Agent 自主决策和纠错。A 是 Plan-then-Execute；C/D 误解 Agent 能力。","Agent ReAct 范式","medium")
q("ag_002","Agent 与 LangChain","Tool 参数 Schema 的作用？","只是文档注释","告诉模型参数名、类型、含义，是 Function Calling 正确执行的关键","用于前端表单渲染","决定计费方式","B","B 正确。Tool Schema 是模型理解工具的唯一接口，决定调用成功率。A 严重低估其作用；C/D 不是 Schema 目的。","Agent 工具 Schema","easy")
q("ag_003","Agent 与 LangChain","LangGraph 相比传统 Chain 的优势？","只能文本处理","支持有状态、有分支、有循环的图工作流，条件路由、Human-in-the-Loop、检查点回放","不需要定义节点","替代大模型不调 API","B","B 正确。LangGraph 用 StateGraph 建模节点+边+条件分支+循环，是线性 Chain 到复杂 Agent 工作流的关键升级。","LangGraph 图工作流","medium")
q("ag_004","Agent 与 LangChain","Prompt 注入攻击的防护？","用参数化查询防 SQL 注入","输入过滤、System/User 指令分层隔离、输出审查","只是理论风险","HTTPS 完全防止","B","B 正确。Prompt 注入是 LLM 特有威胁，攻击者通过输入绕过系统指令。需多层防护。A 是 SQL 注入；C 低估风险；D HTTPS 只加密传输。","Prompt 注入防护","medium")
q("ag_005","Agent 与 LangChain","Agent 对话记忆管理，哪项正确？","永远保留全部历史","根据上下文窗口限制，用滑动窗口或摘要记忆管理消息，保留关键信息控 token 消耗","Agent 不需要记忆","存 Redis 但不传模型","B","B 正确。记忆管理要平衡上下文和 token 限制。A 超 token 限制；C 忽略多轮对话需求；D 存了不用无意义。","Agent 记忆管理","easy")
q("ag_006","Agent 与 LangChain","Plan-and-Execute 与 ReAct 范式的主要区别？","没有区别","Plan-and-Execute 先生成完整执行计划再逐步执行，ReAct 每一步都重新思考。前者适合步骤明确的复杂任务","Plan-and-Execute 不需要工具调用","ReAct 比 Plan-and-Execute 总是更好","B","B 正确。Plan-and-Execute=先规划再执行，适合多步骤任务；ReAct=边想边做，适合动态不确定场景。各有优劣。","Agent Plan-and-Execute 范式","medium")
q("ag_007","Agent 与 LangChain","LangGraph 中子图(Subgraph)的作用？","降低图的可读性","将复杂工作流拆分为可复用的子模块，例如将文档检索封装为子图，在主工作流中作为节点使用","子图只能运行一次","子图只能用于文本处理","B","B 正确。子图=模块化复用，类似函数封装。例如把 RAG 检索流程封装为子图，在多个 Agent 工作流中复用。","LangGraph 子图与模块化","medium")
q("ag_008","Agent 与 LangChain","LangGraph 检查点(Checkpoint)的作用？","保存模型权重","保存工作流每一步的状态快照，支持断点续传、回溯到历史状态和 Human-in-the-Loop 审批","加快图编译速度","替代数据库存储","B","B 正确。检查点是 LangGraph 的持久化机制：保存每个节点执行后的状态，支持暂停→人工审批→继续、回退查看不同路径结果。","LangGraph 检查点机制","medium")
q("ag_009","Agent 与 LangChain","LangSmith/LangFuse 这类可观测性平台的核心价值？","替代大模型 API","追踪 LLM 调用链路的每一步(延迟、token、输入输出)，帮助调试 Prompt、定位瓶颈和监控成本","训练新的 Embedding 模型","替代 LangChain","B","B 正确。LLM 可观测性平台提供全链路追踪：每次 LLM 调用的延迟、token 消耗、输入输出快照。","LLM 可观测性 LangSmith/LangFuse","easy")
q("ag_010","Agent 与 LangChain","Agent 工具调用的权限控制怎么做？","所有工具对所有用户开放","根据用户角色限制可调用工具集合，在 Tool 定义层或 Agent 路由层做白名单校验。敏感操作需额外人工确认","只在前端控制即可","模型自动判断权限","B","B 正确。Agent 安全的核心是工具权限控制：角色→可用工具白名单，敏感操作 Human-in-the-Loop 确认。A 安全风险；C 前端不可信。","Agent 工具权限控制","medium")
q("ag_011","Agent 与 LangChain","Agent 中如何防止无限循环调用工具？","依赖模型自己判断停止","设置 max_iterations 最大步数限制，同时监控是否陷入重复调用同一工具的死循环模式，超限或检测到循环则强制终止","限制每个工具只能调用一次","模型不会无限循环","B","B 正确。Agent 常见坑是陷入循环。防护：max_iterations 硬限制 + 重复模式检测。A 不可靠；C 过度限制；D 乐观了。","Agent 循环检测与步数限制","medium")
q("ag_012","Agent 与 LangChain","LangGraph 中条件路由(Conditional Edge)的实现方式？","所有边都是固定的","通过定义一个返回节点名称的函数，根据当前状态动态决定下一步走哪个节点。例如根据检索结果相关性决定走生成节点还是重新检索节点","条件路由只能在两个节点间选择","条件路由需要人工实时干预","B","B 正确。条件路由是 LangGraph 核心：add_conditional_edges 接收 router 函数(state→next_node_name)，根据状态动态路由。","LangGraph 条件路由","medium")

# ==================== Docker 与部署 (8) ====================
q("dk_001","Docker 与部署","多阶段构建的主要目的？","同时构建多个不相关镜像","构建阶段用完整工具链，运行阶段只复制必要产物，减小镜像体积","多 CPU 架构运行","提高构建速度","B","B 正确。多阶段构建分离构建环境和运行环境，编译依赖不进入最终镜像。A 是多 Dockerfile；C 是 multi-arch。","Docker 多阶段构建","easy")
q("dk_002","Docker 与部署","docker-compose depends_on 的作用？","保证被依赖服务完全就绪后才启动","控制启动顺序但不保证应用就绪，需配合 healthcheck","共享网络命名空间","合并为一个容器","B","B 正确。depends_on 只控顺序，不等待应用就绪。DB 容器启动了但 MySQL 还在初始化，需 healthcheck + condition: service_healthy。A 是常见误解。","Docker Compose depends_on","medium")
q("dk_003","Docker 与部署","Nginx 反向代理的主要作用？","替代后端处理业务","接收请求转发后端，提供负载均衡、SSL 终结、静态资源服务","只压缩图片","替代 Docker","B","B 正确。Nginx 是 AI 应用部署常见组件：反向代理 FastAPI/Streamlit、HTTPS、限流、静态文件、WebSocket 代理。","Nginx 反向代理","easy")
q("dk_004","Docker 与部署","容器启动后立即退出，最可能原因？","Docker 版本过旧","主进程(PID 1)执行完毕退出，容器生命周期与主进程绑定","宿主机内存不足","镜像名含大写字母","B","B 正确。容器以 PID 1 进程生命周期为准。CMD/ENTRYPOINT 命令执行完就退出则容器停止。用 docker logs 排查。","Docker 容器生命周期","easy")
q("dk_005","Docker 与部署","Docker 健康检查(HEALTHCHECK)的作用？","检查镜像是否有病毒","定期探测容器内服务是否正常运行，配合 docker-compose 的 condition: service_healthy 实现正确的启动依赖","检查 Docker 引擎版本","监控宿主机 CPU 使用率","B","B 正确。HEALTHCHECK 让 Docker 知道服务是否真正就绪(如 HTTP 200 响应)，配合 depends_on condition 解决「容器启动了但服务未就绪」的问题。","Docker HEALTHCHECK 健康检查","easy")
q("dk_006","Docker 与部署","Docker 容器优雅关闭(Graceful Shutdown)的正确做法？","直接 kill -9 强制终止","应用监听 SIGTERM 信号，收到后停止接收新请求、等待现有请求处理完成、关闭资源连接后再退出。Docker stop 默认先发 SIGTERM 等待 10s 再 SIGKILL","Docker 会自动处理，不需要应用配合","重启容器","B","B 正确。优雅关闭确保不丢失正在处理的请求。docker stop→SIGTERM→应用处理完→退出；超时则 SIGKILL。","Docker 优雅关闭 Graceful Shutdown","medium")
q("dk_007","Docker 与部署","CI/CD 流程中 Docker 镜像的常见实践？","每次部署手动构建镜像上传","代码推送触发自动构建→运行测试→构建 Docker 镜像→推送到镜像仓库→部署到服务器。使用多阶段构建减小镜像体积","直接在生产服务器上改代码","不需要 CI/CD，手动部署更可靠","B","B 正确。标准 CI/CD：Git push→自动 build/test→docker build→push registry→deploy。多阶段构建保证镜像小且安全。","CI/CD Docker 镜像构建流程","easy")
q("dk_008","Docker 与部署","Docker 中 COPY 和 ADD 指令的区别？","完全相同","COPY 只复制本地文件到镜像；ADD 额外支持自动解压 tar 文件和 URL 下载。推荐优先使用 COPY(更透明)","ADD 是旧指令已被废弃","COPY 不能复制目录","B","B 正确。Dockerfile 最佳实践：默认用 COPY(行为明确)，需要 tar 自动解压时用 ADD。A/D 不准确；C ADD 未废弃但应谨慎使用。","Dockerfile COPY vs ADD","easy")

# ==================== 项目实战 (8) ====================
q("prj_001","项目实战","为何建议大模型调用封装成独立 Service 层？","路由层调用更快","便于复用、测试和替换模型——切换模型只需改 Service，路由无感知","路由不能处理异步","仅是风格偏好","B","B 正确。分层架构核心价值是关注点分离。路由处理 HTTP，Service 处理业务。模型切换、缓存、重试等不影响 API 接口。","AI 项目分层架构","easy")
q("prj_002","项目实战","如何设计数据库表记录用户答题？","所有数据存一个 JSON 字段","设计答题记录表(user_id, topic, stem, selected, correct, is_correct, time)，便于统计分析","纯前端 localStorage","仅 Redis 不落库","B","B 正确。结构化存储方便查询薄弱点、正确率趋势、高频错题等。A JSON 不利查询统计；C 无法跨设备；D Redis 不适合长期持久化。","AI 应用数据库设计","easy")
q("prj_003","项目实战","流式输出 SSE 在 AI 应用中的优势？","比 WebSocket 更快","用户逐步看到生成内容，提升感知速度，适合单向数据流(服务端→客户端)","替代 HTTP POST","替代数据库","B","B 正确。SSE 单向推送，浏览器原生支持，适合 AI 文本流式输出。WebSocket 双向通信更复杂。","AI 应用流式输出 SSE","medium")
q("prj_004","项目实战","防止 SQL 注入的最佳实践？","字符串拼接 SQL","参数化查询或 ORM 处理用户输入","前端 JS 过滤特殊字符","HTTPS 加密","B","B 正确。参数化查询将 SQL 结构与数据分离从根本上防注入。A 最危险；C 前端过滤可绕过；D HTTPS 是传输加密不防 SQL 注入。","安全加固 SQL 注入防护","easy")
q("prj_005","项目实战","AI 应用中 WebSocket 和 SSE 如何选择？","都一样","SSE 适合服务端→客户端单向流式推送(如 ChatGPT 逐字输出)，WebSocket 适合双向实时通信(如多人协作、聊天)。SSE 更简单，WebSocket 更灵活","SSE 比 WebSocket 更快","WebSocket 只能在浏览器中使用","B","B 正确。SSE 单向推送 HTTP 协议适合 AI 文本流式输出；WebSocket 双向全双工适合需要客户端频繁发消息的场景。","AI 应用 SSE vs WebSocket 选型","medium")
q("prj_006","项目实战","灰度发布在 AI 应用中的作用？","将所有流量一次性切到新版本","逐步将部分用户流量导向新版本模型或接口，观察效果和稳定性后再全量切换。降低新模型上线风险","压缩部署包大小","提高数据库查询速度","B","B 正确。灰度发布(金丝雀部署)是 AI 应用上线新模型的常见策略：10%→30%→100% 逐步切流，对比新旧模型质量、延迟和错误率。","AI 应用灰度发布策略","medium")
q("prj_007","项目实战","AI 应用中多模型接入的最佳实践？","每个模型硬编码一套调用逻辑","定义统一的模型调用接口(Adapter 模式)，不同模型各自实现适配器，业务层通过统一接口调用，切换模型只需改配置","只用一个模型不考虑切换","在前端直接调用各模型 API","B","B 正确。Adapter 模式解耦业务和模型：定义 LLMProvider 接口→各模型实现→配置切换。便于 A/B 测试、降级和成本优化。A 难维护；C 缺灵活性；D 不安全。","AI 应用多模型接入 Adapter 模式","medium")
q("prj_008","项目实战","AI 应用从开发到上线的完整流程？","写好代码直接部署","需求分析→技术选型→原型开发→Prompt 调优→接口联调→测试(功能/压力/AI 准确性)→Docker 容器化→CI/CD→灰度发布→监控与迭代","只需要关注模型效果","先上线再慢慢改","B","B 正确。AI 应用上线比传统应用多一个维度：模型效果验证和 Prompt 迭代。灰度发布对新模型上线尤其重要。","AI 应用完整上线流程","easy")
q("prj_009","项目实战","AI 应用日志和监控应关注哪些指标？","只看服务器 CPU 和内存","业务指标(QPS、正确率、用户留存) + LLM 指标(延迟、token 消耗、首 token 时间、错误率) + 基础设施指标(CPU/内存/网络)","只看 LLM 的错误率","不需要监控","B","B 正确。AI 应用监控需三层：业务层、LLM 层、基础设施层。缺一不可。A/C 片面；D 极不推荐。","AI 应用全链路监控指标","medium")

# ==================== 补充 7 题 → 100 ====================
q("py_016","Python","Python 中 __init__.py 文件的作用？","仅作为标识文件无实际作用","将目录标记为 Python 包，可包含包初始化代码和 __all__ 列表控制 from package import * 的行为","必须包含所有模块的 import 语句","已废弃不再需要","B","B 正确。__init__.py 将目录变为包，可写初始化逻辑和定义 __all__。Python 3.3+ 支持隐式命名空间包但显式 __init__.py 仍是最佳实践。A 低估其作用；C 不是必须；D 未废弃。","Python __init__.py 与包管理","easy")
q("llm_013","大模型工程化","Chain of Thought(CoT)提示的作用？","减少输出长度","引导模型逐步推理而非直接给答案，显著提升复杂推理任务(数学、逻辑、多步规划)的准确率","提高输出速度","替代 Function Calling","B","B 正确。CoT 通过「让我们一步步思考」等提示引导模型展示推理过程。对数学题、逻辑推理等效果显著。A/C/D 不准确。","Chain of Thought 思维链提示","medium")
q("rag_013","RAG","向量数据库选型应考虑哪些因素？","只看价格","延迟(QPS)、召回精度、扩展性、部署方式(云/本地)、是否支持混合检索和过滤。如 Chroma 适合原型，Milvus 适合生产大规模场景","所有向量库功能一样","只用 Chroma 就够了","B","B 正确。向量库选型需权衡：Chroma 轻量易上手适合开发；Milvus/Qdrant 性能强大适合生产；Pinecone 全托管省运维。根据数据量、QPS 和预算选择。","向量数据库选型","medium")
q("ag_013","Agent 与 LangChain","LangChain 中 Chain 和 Agent 的核心区别？","没有区别","Chain 是预定义的固定执行流程(DAG)，Agent 是动态决策的——模型根据当前状态自主选择调用哪个工具和下一步做什么","Chain 比 Agent 更快","Agent 不需要 LLM","B","B 正确。Chain=固定流程适合已知步骤任务；Agent=动态决策适合需要推理和适应性的场景。Agent 内部通常也包含 Chain 作为工具。","LangChain Chain vs Agent","medium")
q("dk_009","Docker 与部署","Docker 网络模式 bridge 和 host 的区别？","没有区别","bridge 是默认模式，容器有独立网络命名空间通过 NAT 通信；host 模式容器直接使用宿主机网络栈，性能更高但端口冲突风险大","host 模式更安全","bridge 模式不能访问外网","B","B 正确。开发环境一般用 bridge；需要极致网络性能(如高频 API 调用)时可考虑 host，但注意端口冲突。A/C/D 不准确。","Docker 网络模式 bridge vs host","easy")
q("prj_010","项目实战","AI 应用的接口响应时间过长应如何排查？","直接加服务器","分层排查：前端→网络→网关→应用→LLM API→数据库。用分布式追踪(如 Jaeger)定位瓶颈，常见原因：LLM 调用慢(加缓存/换模型)、DB 慢查询(加索引)、串行改并行","只优化 LLM prompt","只加 Redis 缓存","B","B 正确。分层排查是核心方法论。AI 应用瓶颈通常在 LLM 调用(占 80%+ 耗时)，优化方向：语义缓存、流式输出、异步并发、模型降级。A/C/D 都是单一手段不够全面。","AI 应用性能排查与优化","medium")
q("prj_011","项目实战","AI 应用面试中常问的项目难点，以下哪项最可能被问到？","只问用了什么框架","如何处理大模型的不稳定性(幻觉、超时、格式错误)？如何设计高可用的 LLM 调用链路？如何评估和迭代 Prompt 质量？","只问数据库表设计","只问前端页面实现","B","B 正确。AI 应用开发岗面试核心关注：LLM 稳定性保障(重试/降级/缓存)、Prompt 工程迭代方法、RAG 效果优化、成本控制。A/C/D 太片面不是 AI 岗位重点。","AI 应用开发面试核心考点","easy")

# ==================== 生成 JS 文件 ====================
print(f"Total questions: {len(questions)}")

# Build JS content
lines = ['/**', ' * AI 应用开发选择题固定题库（100 题）', ' * 覆盖 8 大专题，适合 AI 应用开发岗面试准备', ' */', '', 'const quizBank = [']

for i, q in enumerate(questions):
    opts = ','.join(f'{{key:"{o["key"]}",text:{json.dumps(o["text"],ensure_ascii=False)}}}' for o in q["options"])
    stem = json.dumps(q["stem"], ensure_ascii=False)
    expl = json.dumps(q["explanation"], ensure_ascii=False)
    kp = json.dumps(q["knowledge_point"], ensure_ascii=False)
    topic_str = f'// {q["topic"]}' if i == 0 or questions[i-1]["topic"] != q["topic"] else ''
    if topic_str:
        lines.append(f'  {topic_str}')
    lines.append(f'  {{id:{json.dumps(q["id"])},topic:{json.dumps(q["topic"],ensure_ascii=False)},stem:{stem},options:[{opts}],correct_answer:{json.dumps(q["correct_answer"])},explanation:{expl},knowledge_point:{kp},difficulty:{json.dumps(q["difficulty"])}}},')

lines.append('];')
lines.append('')
lines.append('module.exports = { quizBank };')
lines.append('')

output = '\n'.join(lines)

outpath = r'd:\ai_interview_assistant\miniprogram\data\quiz-bank.js'
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(output)

# Stats
from collections import Counter
topic_counts = Counter(q["topic"] for q in questions)
diff_counts = Counter(q["difficulty"] for q in questions)
print(f"Written {len(questions)} questions to {outpath}")
for t, c in topic_counts.most_common():
    print(f"  {t}: {c}")
print(f"  easy: {diff_counts.get('easy',0)}  medium: {diff_counts.get('medium',0)}  hard: {diff_counts.get('hard',0)}")
