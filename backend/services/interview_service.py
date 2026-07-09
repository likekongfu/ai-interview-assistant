from db.crud import get_interview_context


def check_interview_end(interview_id: int) -> bool:
    """判断刷题模式是否应该结束：题数达到上限或连续低分。"""
    history = get_interview_context(interview_id)
    if len(history) >= 15:
        return True

    if len(history) >= 3:
        last_three_answers = history[-3:]
        return all(answer.overall_score < 40 for answer in last_three_answers)

    return False
