"use client";

import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";

interface QAItem {
  question: string;
  answer: string;
}

export default function MultiRoundInterview() {
  const [qaList, setQaList] = useState<QAItem[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 初始化面试
    apiFetch("/start_interview", {
      method: "POST",
      body: JSON.stringify({ jd: "AI算法工程师" }),
      headers: { "Content-Type": "application/json" },
    })
      .then(res => res.json())
      .then(data => setInterviewId(data.interview_id));
  }, []);

  const submitAnswer = async () => {
    if (!interviewId || !currentAnswer.trim()) return;

    setLoading(true);
    const lastQuestion = qaList.length
      ? qaList[qaList.length - 1].question
      : "";

    const res = await apiFetch("/follow_up", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interview_id: interviewId,
        question: lastQuestion,
        answer: currentAnswer,
        jd: "AI算法工程师",
      }),
    });
    const data = await res.json();

    setQaList(prev => [
      ...prev,
      { question: lastQuestion, answer: currentAnswer },
      data.follow_up_question
        ? { question: data.follow_up_question, answer: "" }
        : null,
    ].filter(Boolean) as QAItem[]);

    setCurrentAnswer("");
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">AI 多轮面试</h1>
      <div className="space-y-4">
        {qaList.map((qa, idx) => (
          <div key={idx} className="p-4 border rounded">
            <div className="font-bold">Q{idx + 1}: {qa.question}</div>
            <div className="mt-1 text-gray-700">
              A{idx + 1}: {qa.answer || "等待回答..."}
            </div>
          </div>
        ))}
      </div>

      {qaList.length && !qaList[qaList.length - 1].answer ? (
        <div className="mt-4">
          <textarea
            className="w-full p-2 border rounded"
            placeholder="请输入你的回答"
            value={currentAnswer}
            onChange={e => setCurrentAnswer(e.target.value)}
          />
          <button
            className="mt-2 px-4 py-2 bg-blue-600 text-white rounded"
            onClick={submitAnswer}
            disabled={loading}
          >
            {loading ? "提交中..." : "提交回答"}
          </button>
        </div>
      ) : null}
    </div>
  );
}
