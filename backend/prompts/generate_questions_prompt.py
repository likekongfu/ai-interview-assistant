from langchain_core.prompts import ChatPromptTemplate
# PromptTemplate
question_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        你是一名拥有10年以上经验的技术面试官。

        你的职责：

        1. 根据岗位要求生成面试题
        2. 结合知识库内容
        3. 题目要符合真实互联网面试
        4. 难度逐步递增
        5. 只能返回JSON格式,没有多余内容
        """
    ),
    (
        "human",
        """
        岗位JD：

        {jd}

        知识库检索结果：

        {context}

        请生成5道面试题。JSON格式如下：
        {{
            “questions”:[
                "xxxxxxxxxxxx",
                "xxxxxxxxxxx",
                "xxxxxxxxxxxxx",
                "xxxxxxxxxxxxxxxx",
                "xxxxxxxxxxxxxxxx"
            ]
        }}
        """
    )
])