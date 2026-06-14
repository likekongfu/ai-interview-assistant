from langchain_core.output_parsers import StrOutputParser

from prompts.evaluate_prompt import evaluate_prompt
from services.llm_service import get_llm


evaluate_chain = evaluate_prompt | get_llm() | StrOutputParser()
