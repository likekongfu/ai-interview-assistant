from textwrap import dedent


def build_interview_report_prompt(
    interview_id: int,
    topics_text: str,
    conversation_text: str,
):
    return dedent(
        f"""
        你是一名严格、务实的资深技术面试官。

        请根据候选人的完整 AI 模拟面试记录生成结构化面试报告。

        面试 ID：
        {interview_id}

        Topic 记录：
        {topics_text}

        面试对话：
        {conversation_text}

        要求：
        1. 不要过度夸奖，不要写空泛建议。
        2. 必须指出候选人回答中的具体问题。
        3. 建议必须和面试内容、Topic、回答表现相关。
        4. 如果候选人多次回答“不会、不知道、不了解、没接触过”，必须指出知识盲区。
        5. 如果候选人回答较好，也要指出可以继续提升的方向。
        6. topic_scores 必须覆盖 Topic 记录中的每个 topic。
        7. score 必须是 0 到 100 的整数。
        8. 如果候选人大量回答纯数字、重复字符、无明确语义内容，或整体表现低于 60 分，summary 必须明确说明“有效信息不足/无法证明掌握程度”，不要写“有所了解、具备基础、能够描述”等正向评价。
        9. 如果候选人大量回答纯数字、重复字符、无明确语义内容，或整体表现低于 60 分，strengths 必须返回空数组 []，不要强行总结优点。
        10. 只有当候选人确实给出可验证的技术理解、项目经验或清晰方案时，才允许写 strengths。
        11. 只返回合法 JSON，不要输出 markdown，不要输出任何解释。

        返回 JSON 结构：
        {{
          "summary": "整体评价，必须结合具体表现",
          "strengths": ["优点1", "优点2"],
          "weaknesses": ["不足1", "不足2"],
          "topic_scores": [
            {{
              "topic": "Topic 名称",
              "score": 80,
              "comment": "针对该 Topic 的具体评价"
            }}
          ],
          "improvement_suggestions": ["建议1", "建议2"],
          "study_plan": [
            "第1天：复习具体内容",
            "第2天：复习具体内容",
            "第3天：练习具体内容"
          ]
        }}
        """
    ).strip()
