from langchain_core.messages import AIMessage, HumanMessage


def build_history(messages):
    """把数据库消息转换成 LangChain 可识别的对话历史对象。"""
    history = []
    for msg in messages:
        if msg.role == "ai":
            history.append(AIMessage(content=msg.content))
        else:
            history.append(HumanMessage(content=msg.content))
    return history


