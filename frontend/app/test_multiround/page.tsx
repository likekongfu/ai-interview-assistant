"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

export default function TestMultiInterview() {
  const [questions, setQuestions] = useState([
    {
      question: "请解释一下Transformer架构，并说明它在大语言模型中的作用。",
      answer: "",
    },
  ]);

  const [currentIndex, setCurrentIndex] = useState(0);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const jd = `
AI算法工程师

要求：
熟悉Transformer
熟悉LLM
熟悉LangChain
`;

  const interviewId = 1;

  const submitAnswer = async () => {
    if (!input.trim()) {
      alert("请输入回答");
      return;
    }

    setLoading(true);

    try {
      const currentQuestion =
        questions[currentIndex].question;

      const res = await apiFetch(
        "/follow_up",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            interview_id: interviewId,
            question: currentQuestion,
            answer: input,
            jd: jd,
          }),
        }
      );

      const data = await res.json();

      console.log(data);

      const updatedQuestions = [...questions];

      updatedQuestions[currentIndex].answer =
        input;

      if (data.finished) {
        alert("面试结束");
        setQuestions(updatedQuestions);
        return;
      }

      updatedQuestions.push({
        question: data.follow_up_question,
        answer: "",
      });

      setQuestions(updatedQuestions);

      setCurrentIndex(currentIndex + 1);

      setInput("");
    } catch (err) {
      console.error(err);
      alert("请求失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "1000px",
        margin: "40px auto",
      }}
    >
      <h1>AI多轮面试测试</h1>

      {questions.map((item, index) => (
        <div
          key={index}
          style={{
            marginBottom: "30px",
            padding: "15px",
            border: "1px solid #ddd",
          }}
        >
          <h3>Q{index + 1}</h3>

          <p>{item.question}</p>

          {item.answer && (
            <>
              <h4>A{index + 1}</h4>
              <p>{item.answer}</p>
            </>
          )}
        </div>
      ))}

      {currentIndex < questions.length && (
        <div>
          <textarea
            value={input}
            onChange={(e) =>
              setInput(e.target.value)
            }
            placeholder="请输入你的回答"
            rows={6}
            style={{
              width: "100%",
              border: "1px solid #ccc",
              padding: "10px",
            }}
          />

          <button
            onClick={submitAnswer}
            disabled={loading}
            style={{
              marginTop: "15px",
              padding: "10px 20px",
            }}
          >
            {loading ? "生成中..." : "提交回答"}
          </button>
        </div>
      )}
    </div>
  );
}
