
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from prompts.generate_questions_prompt import question_prompt
from services.rag_service import get_retriever
from services.llm_service import get_llm

# 获取 Retriever 和 LLM
retriever = get_retriever()   # 返回 VectorStoreRetriever
llm = get_llm()               # 返回 Chat/Completion LLM

# 1️⃣ 执行检索，把 Document list 转成字符串
def format_docs(docs):
    """
    将 VectorStoreRetriever 返回的文档列表拼成字符串
    """
    return "\n".join([doc.page_content for doc in docs])


# 3️⃣ 构建 Runnable pipeline
question_chain = (
    {
        "context": retriever | format_docs,
        "jd": RunnablePassthrough()
    }
    | question_prompt
    | llm
    | StrOutputParser()
)
