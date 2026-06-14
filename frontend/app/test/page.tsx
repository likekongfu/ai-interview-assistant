"use client"
/* eslint-disable react-hooks/set-state-in-effect */

import { useCallback, useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"

interface FollowUp {
  question: string
  answer: string
}

interface QuestionItem {
  question: string
  userAnswer?: string
  followUps?: FollowUp[]
}

export default function DetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id

  const [questions, setQuestions] = useState<QuestionItem[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [currentAnswer, setCurrentAnswer] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) router.push("/login")
  }, [router])

  // 获取问题和历史回答
  const getDetail = useCallback(async () => {
    try {
      const token = localStorage.getItem("token")
      const res = await apiFetch(`/history/${id}`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store"
      })
      if (res.status === 401) {
        alert("请重新登录")
        return
      }
      const result = await res.json()
      setQuestions(result)
    } catch (err) {
      console.log(err)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (id) getDetail()
  }, [getDetail, id])

  // 提交答案
  const handleSubmit = async () => {
    const updatedQuestions = [...questions]
    const currentQ = updatedQuestions[currentIndex]
    currentQ.userAnswer = currentAnswer

    // 调用后端 RAG / AI 接口
    const token = localStorage.getItem("token")
    const res = await apiFetch("/chat", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: currentQ.question,
        answer: currentAnswer,
        history: updatedQuestions.slice(0, currentIndex + 1)
      })
    })
    const data = await res.json()

    // 处理 AI 追问
    if (data.follow_up_question) {
      currentQ.followUps = currentQ.followUps || []
      currentQ.followUps.push({ question: data.follow_up_question, answer: "" })
    }

    setQuestions(updatedQuestions)
    setCurrentAnswer("")

    // 自动跳转到下一题（如果有）
    if (currentIndex + 1 < updatedQuestions.length) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  if (loading) {
    return <div style={{ padding: 40, textAlign: "center" }}>加载中...</div>
  }

  if (questions.length === 0) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <h2>暂无面试记录</h2>
        <button onClick={() => router.push("/")} style={{ marginTop: 20 }}>
          开始新面试
        </button>
      </div>
    )
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div style={{ display: "flex", minHeight: "100vh", padding: 40, background: "#f5f7fb" }}>
      
      {/* 左侧：当前题目和回答 */}
      <div style={{ flex: 2, marginRight: 20 }}>
        <h2>第 {currentIndex + 1} 题</h2>
        <p style={{ fontSize: 18, marginBottom: 12 }}>{currentQuestion.question}</p>

        {currentQuestion.followUps?.map((f, idx) => (
          <div key={idx} style={{ marginLeft: 20, marginBottom: 12 }}>
            <p style={{ fontWeight: "bold" }}>追问: {f.question}</p>
            <p>回答: {f.answer}</p>
          </div>
        ))}

        <textarea
          value={currentAnswer}
          onChange={e => setCurrentAnswer(e.target.value)}
          placeholder="请输入你的回答..."
          style={{ width: "100%", height: 100, marginBottom: 12, padding: 8 }}
        />

        <button onClick={handleSubmit} style={{ padding: "10px 18px", background: "#2563eb", color: "white", border: "none", borderRadius: 8 }}>
          提交回答
        </button>
      </div>

      {/* 右侧：历史题目 + 回答 + AI追问 */}
      <div style={{ flex: 1, background: "#111827", color: "white", borderRadius: 12, padding: 20, maxHeight: "90vh", overflowY: "auto" }}>
        <h3>历史题目</h3>
        {questions.map((q, idx) => (
          <div key={idx} style={{ marginBottom: 16, padding: 12, background: idx === currentIndex ? "#374151" : "transparent", borderRadius: 8 }}>
            <p style={{ fontWeight: "bold" }}>{q.question}</p>
            <p>回答: {q.userAnswer || "尚未作答"}</p>
            {q.followUps?.map((f, fIdx) => (
              <div key={fIdx} style={{ marginLeft: 12 }}>
                <p style={{ fontStyle: "italic" }}>追问: {f.question}</p>
                <p>回答: {f.answer || "尚未作答"}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
