from services.llm_output_parser import parse_json_response


def test_parse_json_response_repairs_invalid_backslash_escape():
    raw = '{"pattern": "\\d+", "ok": true}'

    result = parse_json_response(raw)

    assert result["pattern"] == "\\d+"
