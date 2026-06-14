from langchain_core.output_parsers import StrOutputParser
from services.llm_service import get_llm
from prompts.follow_up_prompt import follow_up_prompt

followup_chain = (
    follow_up_prompt
    | get_llm()
    | StrOutputParser()
)