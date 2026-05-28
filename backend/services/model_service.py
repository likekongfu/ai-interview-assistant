import json, asyncio
from langchain_ollama import OllamaLLM
from core.config import OLLAMA_MODEL

model = OllamaLLM(model=OLLAMA_MODEL)


def stream_generate_questions(jd: str, interview_id: int):
    prompt = f"""
你是资深技术面试官。
根据以下JD生成5个技术面试问题。
直接返回纯文本，格式如下：
1. xxx
2. xxx
3. xxx
不要JSON、markdown、解释。
JD:{jd}
"""

    async def question_stream():
        # 先发 interview_id
        yield json.dumps({"type": "meta", "interview_id": interview_id}) + "\n"

        for chunk in model.stream(prompt):
            if chunk:
                yield json.dumps(
                    {"type": "content", "data": chunk}, ensure_ascii=False
                ) + "\n"
                await asyncio.sleep(0)

    return question_stream()


def evaluate_answer_with_ai(question: str, answer: str):
    invalid_answers = ["1", "2", "3", "不会", "不知道", "不懂", "无"]
    if len(answer.strip()) < 10 or answer.strip() in invalid_answers:
        return {
            "technical_score": 20,
            "logic_score": 20,
            "experience_score": 20,
            "communication_score": 20,
            "overall_score": 20,
            "feedback": "回答过短或无意义，请详细作答。",
        }
    prompt = f"""
你是一名严格的大厂面试官。
请根据下面的面试题和候选人的回答进行评分。
【面试题】
{question}
候选人回答】
{answer}
评分规则：
1. 如果回答出现以下情况：
- 少于10个字
- 纯数字
- 乱码
- 无意义内容
- 与问题无关
- “不知道”
- “不会”
- “1”
- “2”
- 随机字符
则必须判定为低质量回答。
此时直接返回：
{{
  "technical_score": 20,
  "logic_score": 20,
  "experience_score": 20,
  "communication_score": 20,
  "overall_score": 20,
  "feedback": "回答无意义或过短，请认真作答。"
}}
2. 如果回答正常：
请从以下维度评分：
1. technical_score（技术能力）
2. logic_score（逻辑表达）
3. engineering_score（工程经验）
4. communication_score（沟通表达）
5. overall_score（综合评分）
进行严格评分。
注意：
不要因为回答里出现技术名词就给高分。
必须真正解释原理、细节、场景。
评分标准：
- 90以上：高级工程师水平
- 80-89：中高级
- 70-79：合格
- 60-69：基础薄弱
- 60以下：回答错误或明显不会
如果回答过短、无意义、错误：
必须低于40分。
如果回答只有一句话，
或者没有技术细节，
综合分不得高于50。
返回格式：
[
  {{
    "technical_score":90,
    "logic_score":80,
    "experience_score":70,
    "communication_score":85,
    "overall_score":82,
    "feedback":"回答不错"
  }}
]
严格返回JSON数组。
不要markdown。
不要解释。
"""
    response = json.loads(model.invoke(prompt))
    return response[0]
