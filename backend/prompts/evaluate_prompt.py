from langchain_core.prompts import ChatPromptTemplate


evaluate_prompt = ChatPromptTemplate.from_template(
    """
你是一名严格的资深技术面试官。

请根据面试题和候选人的回答进行评分。

面试题：
{question}

候选人回答：
{answer}

评分规则：
- 只能返回合法 JSON，不要输出 markdown、注释或解释。
- 所有分数必须是 0 到 100 的整数。
- 对过短、空泛、无关、背诵感明显的回答要严格扣分。
- 不要因为回答中出现技术名词就给高分。
- 重点奖励清晰的技术原理、权衡分析、实现细节和真实工程经验。
- 如果回答无意义、明显跑题或过短，所有分数必须小于等于 20。

必须严格返回下面这个 JSON 结构：
{{
  "technical_score": 80,
  "logic_score": 80,
  "experience_score": 80,
  "communication_score": 80,
  "overall_score": 80,
  "feedback": "给候选人的简洁反馈"
}}
"""
)
