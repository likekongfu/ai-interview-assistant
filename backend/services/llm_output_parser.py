import json
import re


def parse_json_response(raw_response: str):
    """解析 LLM 返回的 JSON 文本，兼容 Markdown 包裹和常见格式问题。"""
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
    """去掉 LLM 常见的 ```json 代码块包裹。"""
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _extract_json_text(text: str) -> str:
    """从混合文本中提取最外层 JSON 对象或数组。"""
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
    """修复尾随逗号、Python 布尔值等常见非法 JSON 问题。"""
    repaired = text.strip()
    # LLM 生成代码题时偶尔会输出 "\d"、"\s" 这类 JSON 不认识的转义。
    # 这里把非法反斜杠转义成普通反斜杠，避免整段 JSON 解析失败。
    repaired = re.sub(r'\\(?!["\\/bfnrtu])', r"\\\\", repaired)
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"\bNone\b", "null", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)
    if "'" in repaired and '"' not in repaired:
        repaired = repaired.replace("'", '"')
    return repaired
