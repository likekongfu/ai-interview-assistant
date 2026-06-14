"use client";

import Navbar from "../components/Navbar";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { apiFetch } from "@/lib/api";

type PracticeQuestion = {
  question: string;
};

type PracticeFeedback = {
  technical_score?: number;
  logic_score?: number;
  experience_score?: number;
  communication_score?: number;
  overall_score?: number;
  feedback?: string;
};

type ApiErrorBody = {
  detail?: string | Array<{ msg?: string }>;
  message?: string;
};

export default function PracticePage() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [questions, setQuestions] = useState<PracticeQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [feedbacks, setFeedbacks] = useState<Record<number, PracticeFeedback>>({});
  const [currentIndex, setCurrentIndex] = useState(0);
  const [gradingIndex, setGradingIndex] = useState<number | null>(null);
  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [level, setLevel] = useState("中级");
  const [showJDPanel, setShowJDPanel] = useState(true);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const token = localStorage.getItem("token");
      const storedUserId = localStorage.getItem("user_id");
      if (!token) {
        router.push("/login");
        return;
      }

      if (!storedUserId) return;

      setUserId(storedUserId);
      const savedQuestions = localStorage.getItem(`questions_${storedUserId}`);
      const savedAnswers = localStorage.getItem(`answers_${storedUserId}`);
      const savedFeedbacks = localStorage.getItem(`feedbacks_${storedUserId}`);
      const savedIndex = localStorage.getItem(`currentIndex_${storedUserId}`);
      const savedInterviewId = localStorage.getItem(`interviewId_${storedUserId}`);
      const savedJd = localStorage.getItem(`jd_${storedUserId}`);

      if (savedQuestions) {
        setQuestions(JSON.parse(savedQuestions));
        setShowJDPanel(false);
      }
      if (savedAnswers) setAnswers(JSON.parse(savedAnswers));
      if (savedFeedbacks) setFeedbacks(JSON.parse(savedFeedbacks));
      if (savedIndex) setCurrentIndex(Number(savedIndex));
      if (savedInterviewId) setInterviewId(Number(savedInterviewId));
      if (savedJd) setJd(savedJd);
    }, 0);

    return () => window.clearTimeout(timer);
  }, [router]);

  async function generateQuestions() {
    const token = localStorage.getItem("token");
    if (!jd.trim()) {
      toast.error("请输入题库、题型或技术方向");
      return;
    }

    setLoading(true);
    setQuestions([]);
    setAnswers({});
    setFeedbacks({});
    setCurrentIndex(0);

    try {
      const res = await apiFetch("/generate_questions", {
        method: "POST",
        token,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ jd: `${level}：${jd}` }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        throw new Error(getErrorMessage(data, "生成题目失败"));
      }

      const qList = Array.isArray(data.questions)
        ? data.questions.map((question: string) => ({ question }))
        : [];

      setQuestions(qList);
      setInterviewId(data.interview_id);
      if (userId) {
        localStorage.setItem(`questions_${userId}`, JSON.stringify(qList));
        localStorage.setItem(`interviewId_${userId}`, String(data.interview_id));
        localStorage.setItem(`jd_${userId}`, jd);
      }
      setShowJDPanel(false);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "生成题目失败");
    } finally {
      setLoading(false);
    }
  }

  async function evaluateAnswer(question: string, index: number) {
    const token = localStorage.getItem("token");
    if (!answers[index]?.trim()) {
      toast.error("请先输入答案");
      return;
    }

    setGradingIndex(index);
    try {
      const res = await apiFetch("/evaluate_answer", {
        method: "POST",
        token,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          interview_id: interviewId,
          question,
          answer: answers[index],
        }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        if (res.status === 400 && userId) resetPracticeSession(userId);
        throw new Error(getErrorMessage(data, "评分失败，请重新生成题目"));
      }

      setFeedbacks((prev) => {
        const next = { ...prev, [index]: data.result };
        if (userId) localStorage.setItem(`feedbacks_${userId}`, JSON.stringify(next));
        return next;
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "评分失败");
    } finally {
      setGradingIndex(null);
    }
  }

  function resetPracticeSession(targetUserId: string) {
    localStorage.removeItem(`interviewId_${targetUserId}`);
    localStorage.removeItem(`questions_${targetUserId}`);
    localStorage.removeItem(`answers_${targetUserId}`);
    localStorage.removeItem(`feedbacks_${targetUserId}`);
    localStorage.removeItem(`currentIndex_${targetUserId}`);

    setInterviewId(null);
    setQuestions([]);
    setAnswers({});
    setFeedbacks({});
    setCurrentIndex(0);
    setShowJDPanel(true);
  }

  function updateAnswer(value: string) {
    const next = { ...answers, [currentIndex]: value };
    setAnswers(next);
    if (userId) localStorage.setItem(`answers_${userId}`, JSON.stringify(next));
  }

  function switchQuestion(index: number) {
    setCurrentIndex(index);
    if (userId) localStorage.setItem(`currentIndex_${userId}`, String(index));
  }

  const finishedCount = Object.keys(feedbacks).length;
  const totalCount = questions.length;
  const avgTechnical = totalFeedbackScore(feedbacks, "technical_score");
  const avgLogic = totalFeedbackScore(feedbacks, "logic_score");
  const avgExpression = totalFeedbackScore(feedbacks, "communication_score");
  const avgExperience = totalFeedbackScore(feedbacks, "experience_score");
  const currentQuestion = questions[currentIndex];
  const currentFeedback = feedbacks[currentIndex];

  return (
    <>
      <Navbar />
      <main
        style={{
          display: "flex",
          gap: "20px",
          maxWidth: "1400px",
          margin: "40px auto",
          padding: "0 16px",
          fontFamily: "Arial",
        }}
      >
        <aside
          style={{
            width: "280px",
            position: "sticky",
            top: "20px",
            maxHeight: "80vh",
            overflowY: "auto",
          }}
        >
          <h2 style={{ fontSize: "22px", marginBottom: "16px" }}>题目列表</h2>
          {questions.map((item, index) => (
            <button
              key={`${item.question}-${index}`}
              data-testid="practice-question-item"
              onClick={() => switchQuestion(index)}
              style={{
                width: "100%",
                textAlign: "left",
                padding: "12px",
                marginBottom: "10px",
                borderRadius: "8px",
                cursor: "pointer",
                background: currentIndex === index ? "#111827" : "#f5f5f5",
                color: currentIndex === index ? "#fff" : "#111",
                border: feedbacks[index] ? "2px solid #22c55e" : "1px solid #ccc",
              }}
            >
              {feedbacks[index] ? "已评分" : "未作答"} 第 {index + 1} 题
            </button>
          ))}

          {totalCount > 0 && (
            <div style={{ marginTop: "20px" }}>
              <h3 style={{ fontSize: "18px" }}>AI 实时评价</h3>
              <ProgressBar label="技术深度" value={avgTechnical} color="#2563eb" />
              <ProgressBar label="表达能力" value={avgExpression} color="#22c55e" />
              <ProgressBar label="逻辑清晰度" value={avgLogic} color="#f97316" />
              <ProgressBar label="项目经验" value={avgExperience} color="#facc15" />
            </div>
          )}

          {finishedCount === totalCount && totalCount > 0 && interviewId && (
            <button
              data-testid="practice-report-button"
              onClick={() => router.push(`/history/${interviewId}`)}
              style={{
                marginTop: "20px",
                width: "100%",
                padding: "12px",
                borderRadius: "8px",
                background: "#111827",
                color: "#fff",
                cursor: "pointer",
                border: "none",
                fontWeight: "bold",
              }}
            >
              查看刷题报告
            </button>
          )}
        </aside>

        <section style={{ flex: 1 }}>
          <div style={{ marginBottom: "20px" }}>
            <button
              onClick={() => setShowJDPanel((value) => !value)}
              style={{
                marginBottom: "10px",
                padding: "8px 16px",
                borderRadius: "8px",
                background: "#2563eb",
                color: "#fff",
                border: "none",
                cursor: "pointer",
              }}
            >
              {showJDPanel ? "收起题库配置" : "展开题库配置"}
            </button>

            {showJDPanel && (
              <div style={{ background: "#fff", padding: "20px", borderRadius: "12px" }}>
                <label style={{ display: "block", marginBottom: "8px" }}>题目难度</label>
                <select
                  data-testid="practice-level-select"
                  value={level}
                  onChange={(event) => setLevel(event.target.value)}
                  style={{ marginBottom: "10px", padding: "8px", borderRadius: "8px" }}
                >
                  <option>初级</option>
                  <option>中级</option>
                  <option>高级</option>
                </select>
                <textarea
                  data-testid="practice-jd-input"
                  rows={4}
                  placeholder="请输入题库、题目类型、技术方向，例如：题库 Java 后端，题型 简答题，技术方向 Redis..."
                  value={jd}
                  onChange={(event) => setJd(event.target.value)}
                  style={{
                    width: "100%",
                    marginBottom: "10px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                    padding: "10px",
                  }}
                />
                <button
                  data-testid="practice-generate-button"
                  onClick={generateQuestions}
                  disabled={loading}
                  style={{
                    background: loading ? "#9ca3af" : "#111827",
                    color: "#fff",
                    padding: "10px 20px",
                    borderRadius: "8px",
                    cursor: loading ? "not-allowed" : "pointer",
                    border: "none",
                  }}
                >
                  {loading ? "生成中..." : "获取题目列表"}
                </button>
              </div>
            )}
          </div>

          {currentQuestion && (
            <div style={{ background: "#fff", padding: "20px", borderRadius: "12px" }}>
              <h3>
                第 {currentIndex + 1} 题 / 共 {questions.length} 题
              </h3>
              <p style={{ fontWeight: "bold", fontSize: "18px" }}>
                {currentQuestion.question}
              </p>
              <textarea
                data-testid="practice-answer-input"
                rows={8}
                value={answers[currentIndex] || ""}
                placeholder="请输入你的答案..."
                onChange={(event) => updateAnswer(event.target.value)}
                style={{
                  width: "100%",
                  marginTop: "10px",
                  marginBottom: "10px",
                  borderRadius: "8px",
                  border: "1px solid #ccc",
                  padding: "12px",
                }}
              />
              <button
                data-testid="practice-submit-button"
                onClick={() => evaluateAnswer(currentQuestion.question, currentIndex)}
                disabled={gradingIndex === currentIndex}
                style={{
                  marginTop: "12px",
                  background: gradingIndex === currentIndex ? "#9ca3af" : "#2563eb",
                  color: "#fff",
                  padding: "10px 18px",
                  borderRadius: "8px",
                  border: "none",
                  cursor: gradingIndex === currentIndex ? "not-allowed" : "pointer",
                }}
              >
                {gradingIndex === currentIndex ? "评分中..." : "提交并评分"}
              </button>

              {currentFeedback && (
                <div
                  data-testid="practice-feedback"
                  style={{
                    marginTop: "16px",
                    padding: "16px",
                    borderRadius: "10px",
                    background: "#f9fafb",
                    border: "1px solid #e5e7eb",
                    color: "#374151",
                    lineHeight: 1.7,
                  }}
                >
                  <strong>AI 解析 / 参考答案 / 得分</strong>
                  <div>综合得分：{currentFeedback.overall_score ?? 0}</div>
                  <div>{currentFeedback.feedback || "暂无解析"}</div>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </>
  );
}

function totalFeedbackScore(
  feedbacks: Record<number, PracticeFeedback>,
  key: keyof PracticeFeedback
) {
  const vals = Object.values(feedbacks).map((item) => Number(item[key]) || 0);
  if (vals.length === 0) return 0;
  return Math.round(vals.reduce((sum, value) => sum + value, 0) / vals.length);
}

function ProgressBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  return (
    <div style={{ marginBottom: "10px" }}>
      <div style={{ fontSize: "14px", marginBottom: "4px" }}>
        {label} ({value}/100)
      </div>
      <div
        style={{
          width: "100%",
          height: "8px",
          background: "#e5e7eb",
          borderRadius: "4px",
        }}
      >
        <div
          style={{
            width: `${value}%`,
            height: "100%",
            background: color,
            borderRadius: "4px",
          }}
        />
      </div>
    </div>
  );
}

function getErrorMessage(data: ApiErrorBody | null, fallback: string) {
  if (!data) return fallback;
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail.map((item) => item?.msg || JSON.stringify(item)).join("；");
  }
  if (typeof data.message === "string") return data.message;
  return fallback;
}
