import unittest
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services.report_service import generate_ai_interview_report


def make_interview(status="finished", user_id=1):
    return SimpleNamespace(id=10, user_id=user_id, status=status)


def make_topic(topic_id=1, topic="FastAPI", finished=True, follow_up_count=2):
    return SimpleNamespace(
        id=topic_id,
        topic=topic,
        finished=finished,
        follow_up_count=follow_up_count,
        topic_order=topic_id,
    )


def make_message(role, content, topic_id=1):
    return SimpleNamespace(role=role, content=content, topic_id=topic_id)


def make_saved_report():
    return SimpleNamespace(
        interview_id=10,
        overall_score=80,
        summary="整体表现稳定。",
        strengths='["能说明项目背景"]',
        weaknesses='["Redis 细节不足"]',
        topic_scores_json='[{"topic":"FastAPI","score":80,"comment":"掌握较好"}]',
        improvement_suggestions='["补充项目难点案例"]',
        study_plan='["第1天：复习 FastAPI","第2天：复习 Redis","第3天：模拟表达"]',
    )


class AIInterviewReportServiceTest(unittest.TestCase):
    @patch("services.report_service.save_interview_report")
    @patch("services.report_service.invoke_llm_text")
    @patch("services.report_service.get_messages_by_interview")
    @patch("services.report_service.get_topics_by_interview")
    @patch("services.report_service.get_report_by_interview_id")
    @patch("services.report_service.get_ai_interview_by_id")
    def test_generate_report_success(
        self,
        mock_get_interview,
        mock_get_report,
        mock_get_topics,
        mock_get_messages,
        mock_model,
        mock_save,
    ):
        mock_get_interview.return_value = make_interview()
        mock_get_report.return_value = None
        mock_get_topics.return_value = [make_topic()]
        mock_get_messages.return_value = [
            make_message("ai", "请介绍 FastAPI 依赖注入"),
            make_message("human", "FastAPI 依赖注入可以复用鉴权和数据库连接。"),
        ]
        mock_model.return_value = """
        {
          "summary": "整体表现较稳定。",
          "strengths": ["能结合 FastAPI 项目回答"],
          "weaknesses": ["异步机制解释还不够完整"],
          "topic_scores": [
            {"topic": "FastAPI", "score": 82, "comment": "掌握较好"}
          ],
          "improvement_suggestions": ["补充异步机制和中间件案例"],
          "study_plan": ["第1天：复习 FastAPI", "第2天：复习 Redis", "第3天：练习表达"]
        }
        """
        mock_save.return_value = make_saved_report()

        result = generate_ai_interview_report(interview_id=10, user_id=1)

        self.assertEqual(result["interview_id"], 10)
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 100)
        mock_save.assert_called_once()

    @patch("services.report_service.save_interview_report")
    @patch("services.report_service.invoke_llm_text")
    @patch("services.report_service.get_messages_by_interview")
    @patch("services.report_service.get_topics_by_interview")
    @patch("services.report_service.get_report_by_interview_id")
    @patch("services.report_service.get_ai_interview_by_id")
    def test_generate_report_is_idempotent(
        self,
        mock_get_interview,
        mock_get_report,
        mock_get_topics,
        mock_get_messages,
        mock_model,
        mock_save,
    ):
        mock_get_interview.return_value = make_interview()
        mock_get_report.return_value = make_saved_report()
        mock_get_topics.return_value = [make_topic()]
        mock_get_messages.return_value = [
            make_message("ai", "请介绍 FastAPI"),
            make_message("human", "111111"),
        ]
        mock_model.return_value = "not json"
        mock_save.return_value = make_saved_report()

        result = generate_ai_interview_report(interview_id=10, user_id=1)

        self.assertEqual(result["interview_id"], 10)
        mock_model.assert_called_once()
        mock_save.assert_called_once()

    @patch("services.report_service.get_ai_interview_by_id")
    def test_generate_report_interview_not_found(self, mock_get_interview):
        mock_get_interview.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            generate_ai_interview_report(interview_id=404, user_id=1)

        self.assertEqual(ctx.exception.status_code, 404)

    @patch("services.report_service.get_report_by_interview_id")
    @patch("services.report_service.get_ai_interview_by_id")
    def test_generate_report_rejects_unfinished_interview(
        self,
        mock_get_interview,
        mock_get_report,
    ):
        mock_get_interview.return_value = make_interview(status="in_progress")
        mock_get_report.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            generate_ai_interview_report(interview_id=10, user_id=1)

        self.assertEqual(ctx.exception.status_code, 400)

    @patch("services.report_service.save_interview_report")
    @patch("services.report_service.invoke_llm_text")
    @patch("services.report_service.get_messages_by_interview")
    @patch("services.report_service.get_topics_by_interview")
    @patch("services.report_service.get_report_by_interview_id")
    @patch("services.report_service.get_ai_interview_by_id")
    def test_generate_report_falls_back_when_llm_returns_invalid_json(
        self,
        mock_get_interview,
        mock_get_report,
        mock_get_topics,
        mock_get_messages,
        mock_model,
        mock_save,
    ):
        mock_get_interview.return_value = make_interview()
        mock_get_report.return_value = None
        mock_get_topics.return_value = [make_topic(topic="Redis 缓存")]
        mock_get_messages.return_value = [
            make_message("ai", "请说明 Redis 缓存击穿"),
            make_message("human", "不知道"),
        ]
        mock_model.return_value = "这不是 JSON"
        mock_save.return_value = make_saved_report()

        result = generate_ai_interview_report(interview_id=10, user_id=1)

        self.assertEqual(result["interview_id"], 10)
        mock_save.assert_called_once()

    @patch("services.report_service.save_interview_report")
    @patch("services.report_service.invoke_llm_text")
    @patch("services.report_service.get_messages_by_interview")
    @patch("services.report_service.get_topics_by_interview")
    @patch("services.report_service.get_report_by_interview_id")
    @patch("services.report_service.get_ai_interview_by_id")
    def test_invalid_numeric_answers_hide_strengths(
        self,
        mock_get_interview,
        mock_get_report,
        mock_get_topics,
        mock_get_messages,
        mock_model,
        mock_save,
    ):
        mock_get_interview.return_value = make_interview()
        mock_get_report.return_value = None
        mock_get_topics.return_value = [
            make_topic(topic_id=1, topic="Redis 缓存"),
            make_topic(topic_id=2, topic="Netty NIO"),
        ]
        mock_get_messages.return_value = [
            make_message("ai", "请介绍 Redis 缓存设计", topic_id=1),
            make_message("human", "111111111", topic_id=1),
            make_message("ai", "请介绍 Netty NIO 设计", topic_id=2),
            make_message("human", "111111111", topic_id=2),
        ]
        mock_model.return_value = """
        {
          "summary": "候选人回答无效",
          "strengths": ["具备一定知识面"],
          "weaknesses": ["回答为纯数字"],
          "topic_scores": [
            {"topic": "Redis 缓存", "score": 80, "comment": "掌握较好"},
            {"topic": "Netty NIO", "score": 80, "comment": "掌握较好"}
          ],
          "improvement_suggestions": ["补充基础知识"],
          "study_plan": ["第1天：复习基础", "第2天：练习表达", "第3天：模拟面试"]
        }
        """
        mock_save.return_value = make_saved_report()

        result = generate_ai_interview_report(interview_id=10, user_id=1)

        self.assertEqual(result["strengths"], [])
        self.assertIn("无明确语义", result["summary"])
        self.assertTrue(all(item["score"] == 20 for item in result["topic_scores"]))
        mock_save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
