from langchain_core.messages import AIMessage, HumanMessage


def build_history(messages):
    history = []
    for msg in messages:
        if msg.role == "ai":
            history.append(AIMessage(content=msg.content))
        else:
            history.append(HumanMessage(content=msg.content))
    return history


