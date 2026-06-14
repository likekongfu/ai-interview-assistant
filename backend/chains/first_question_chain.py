from prompts.interview_prompt import question_prompt,topic_prompt,judge_prompt
from services.llm_service import get_llm
from langchain_core.output_parsers import StrOutputParser
llm=get_llm()
first_question_chain=(
    question_prompt|llm|StrOutputParser()
)

topic_chain = (
    topic_prompt|llm|StrOutputParser()
)

judge_chain = (
    judge_prompt|llm|StrOutputParser()
)