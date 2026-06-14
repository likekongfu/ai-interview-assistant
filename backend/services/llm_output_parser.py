import json
import re


def parse_json_response(raw_response: str):
    text = str(raw_response).strip()
    text = _strip_markdown_fence(text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        json_text = _extract_json_text(text)
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return json.loads(_repair_common_json_issues(json_text))


def _strip_markdown_fence(text: str) -> str:
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_text(text: str) -> str:
    object_start = text.find("{")
    object_end = text.rfind("}")
    array_start = text.find("[")
    array_end = text.rfind("]")

    object_candidate = (
        text[object_start : object_end + 1]
        if object_start != -1 and object_end != -1 and object_end > object_start
        else ""
    )
    array_candidate = (
        text[array_start : array_end + 1]
        if array_start != -1 and array_end != -1 and array_end > array_start
        else ""
    )

    if object_candidate and (not array_candidate or object_start < array_start):
        return object_candidate
    if array_candidate:
        return array_candidate

    raise json.JSONDecodeError("No JSON object or array found", text, 0)


def _repair_common_json_issues(text: str) -> str:
    repaired = text.strip()
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"\bNone\b", "null", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)
    if "'" in repaired and '"' not in repaired:
        repaired = repaired.replace("'", '"')
    return repaired
