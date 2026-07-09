from chains.evaluate_chain import evaluate_chain
from services.llm_service import invoke_llm_text
from services.llm_output_parser import parse_json_response



def generate_questions(jd: str, interview_id: int | None = None):
    """根据岗位 JD 生成刷题模式下的 5 道技术面试题。"""
    prompt = f"""
你是一名资深技术面试官。

请根据下面的岗位 JD 生成 5 个技术面试问题。
只能返回合法 JSON，结构如下：
{{
  "questions": [
    "问题 1",
    "问题 2",
    "问题 3",
    "问题 4",
    "问题 5"
  ]
}}

岗位 JD：
{jd}
"""
    return parse_json_response(invoke_llm_text(prompt))


def evaluate_answer_with_ai(question: str, answer: str):
    """对刷题答案进行 AI 评分；低质量回答直接走固定低分兜底。"""
    if is_low_quality_answer(answer):
        return low_quality_score()

    raw_response = evaluate_chain.invoke(
        {
            "question": question,
            "answer": answer,
        }
    )
    return parse_json_response(raw_response)


def generate_follow_up(history, jd):
    """根据刷题/练习历史和岗位 JD 生成一个追问问题。"""
    conversation = ""
    for item in history:
        conversation += f"面试官问题：{item.question}\n候选人回答：{item.answer}\n"

    prompt = f"""
你是一名严格的资深技术面试官。

岗位 JD：
{jd}

完整面试记录：
{conversation}

请基于上下文生成一个追问问题。
要求：
- 不要重复之前问过的问题。
- 只问一个问题。
- 深入技术细节。
- 不要评价候选人。
- 只输出问题文本。
"""
    return invoke_llm_text(prompt)


def is_low_quality_answer(answer: str):
    """判断刷题答案是否过短或明显无效。"""
    normalized = answer.strip().lower()
    invalid_answers = {
        "",
        "1",
        "2",
        "3",
        "no",
        "none",
        "不知道",
        "不会",
        "不清楚",
        "不懂",
    }
    return len(normalized) < 10 or normalized in invalid_answers


def low_quality_score():
    """返回低质量答案的固定低分评分结果。"""
    return {
        "technical_score": 20,
        "logic_score": 20,
        "experience_score": 20,
        "communication_score": 20,
        "overall_score": 20,
        "feedback": "回答过短或缺少有效技术内容，请补充更具体的原理、细节和项目经验。",
    }

