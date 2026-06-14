"use client"

import { useCallback, useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { apiFetch } from "@/lib/api"

export default function DetailPage() {

  const params = useParams()
  const router = useRouter()

  const id = params.id

  type HistoryDetailItem = {
    question: string
    answer: string
    overall_score: number
    technical_score: number
    logic_score: number
    experience_score: number
    communication_score: number
    feedback: string
  }

  type ScoreKey = "technical" | "logic" | "experience" | "communication"

  const [data, setData] = useState<HistoryDetailItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
    }
  }, [router])

  const getDetail = useCallback(async () => {

    try {

      const token = localStorage.getItem("token")

      const res = await apiFetch(`/history/${id}`, {
        method: "GET",
        cache: "no-store",
        token
      })

      if (res.status === 401) {
        alert("请重新登录")
        router.push("/login")
        return
      }

      const result = await res.json()

      setData(Array.isArray(result) ? result : [])

      setLoading(false)

    } catch (err) {

      console.log(err)

      setLoading(false)

    }

  }, [id, router])

  useEffect(() => {

    if (id) {
      const timer = window.setTimeout(() => {
        getDetail()
      }, 0)

      return () => window.clearTimeout(timer)
    }

  }, [getDetail, id])

  useEffect(() => {

    const handlePopState = () => {
      getDetail()
    }

    window.addEventListener("popstate", handlePopState)

    return () => {
      window.removeEventListener("popstate", handlePopState)
    }

  }, [getDetail])

  // loading
  if (loading) {

    return (

      <div
        style={{
          minHeight: "100vh",
          background: "#f5f7fb",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column"
        }}
      >

        <div
          style={{
            fontSize: "64px",
            marginBottom: "20px"
          }}
        >
          🤖
        </div>

        <div
          style={{
            fontSize: "20px",
            fontWeight: "bold",
            color: "#111827"
          }}
        >
          正在加载面试记录...
        </div>

      </div>

    )

  }

  // 空状态
  if (data.length === 0) {

    return (

      <div
        style={{
          minHeight: "100vh",
          background: "#f5f7fb",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column"
        }}
      >

        <div
          style={{
            fontSize: "72px",
            marginBottom: "20px"
          }}
        >
          🤖
        </div>

        <h2
          style={{
            fontSize: "36px",
            fontWeight: "bold",
            marginBottom: "12px",
            color: "#111827"
          }}
        >
          暂无面试记录
        </h2>

        <p
          style={{
            color: "#6b7280",
            marginBottom: "32px",
            fontSize: "16px"
          }}
        >
          当前面试记录不存在或已被删除
        </p>

        <div
          style={{
            display: "flex",
            gap: "14px"
          }}
        >



          <button
            onClick={() => router.push("/")}
            style={{
              padding: "12px 22px",
              border: "none",
              background: "#2563eb",
              color: "white",
              borderRadius: "12px",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "15px"
            }}
          >
            开始新面试
          </button>

        </div>

      </div>

    )

  }

  return (

    <div
      style={{
        minHeight: "100vh",
        background: "#f5f7fb",
        padding: "40px"
      }}
    >

      <div
        style={{
          maxWidth: "1000px",
          margin: "0 auto"
        }}
      >




        {/* 页面标题 */}

        <div
          style={{
            background: "#ffffff",
            borderRadius: "24px",
            padding: "32px",
            marginBottom: "30px",
            boxShadow: "0 2px 10px rgba(0,0,0,0.05)"
          }}
        >

          <h1
            style={{
              fontSize: "38px",
              fontWeight: "bold",
              marginBottom: "12px",
              color: "#111827"
            }}
          >
            AI 刷题分析报告
          </h1>

          <p
            style={{
              color: "#6b7280",
              lineHeight: 1.8,
              fontSize: "16px"
            }}
          >
            AI 根据本次模拟面试生成的综合能力分析
          </p>

        </div>

        {

          data.map((item, index) => (

            <div
              key={index}
              style={{
                background: "#ffffff",
                borderRadius: "24px",
                padding: "32px",
                marginBottom: "30px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.05)"
              }}
            >

              {/* 问题 */}

              <div style={{ marginBottom: "28px" }}>

                <h2
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    marginBottom: "14px",
                    color: "#111827"
                  }}
                >
                  面试问题
                </h2>

                <p
                  style={{
                    lineHeight: 1.9,
                    color: "#374151",
                    fontSize: "16px"
                  }}
                >
                  {item.question}
                </p>

              </div>

              {/* 回答 */}

              <div style={{ marginBottom: "28px" }}>

                <h2
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    marginBottom: "14px",
                    color: "#111827"
                  }}
                >
                  我的回答
                </h2>

                <p
                  style={{
                    lineHeight: 1.9,
                    color: "#374151",
                    fontSize: "16px"
                  }}
                >
                  {item.answer}
                </p>

              </div>

              {/* 综合评分 */}

              <div
                style={{
                  marginBottom: "32px",
                  padding: "28px",
                  borderRadius: "20px",
                  background: "#f9fafb",
                  border: "1px solid #e5e7eb"
                }}
              >

                <div
                  style={{
                    color: "#6b7280",
                    marginBottom: "12px"
                  }}
                >
                  综合评分
                </div>

                <div
                  style={{
                    fontSize: "60px",
                    fontWeight: "bold",
                    color:
                      item.overall_score >= 75
                        ? "#10b981"
                        : item.overall_score >= 60
                          ? "#f59e0b"
                          : "#ef4444"
                  }}
                >
                  {item.overall_score}
                </div>

              </div>

              {/* 能力分析 */}

              <div style={{ marginBottom: "32px" }}>

                <h2
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    marginBottom: "24px",
                    color: "#111827"
                  }}
                >
                  能力分析
                </h2>

                {
                  (["technical", "logic", "experience", "communication"] as ScoreKey[]).map((key) => {

                    const labelMap: Record<ScoreKey, string> = {
                      technical: "技术能力",
                      logic: "逻辑表达",
                      experience: "工程经验",
                      communication: "沟通表达"
                    }

                    const colorMap: Record<ScoreKey, string> = {
                      technical: "#10b981",
                      logic: "#3b82f6",
                      experience: "#f59e0b",
                      communication: "#8b5cf6"
                    }

                    const score = item[`${key}_score`]

                    return (

                      <div
                        style={{
                          marginBottom: "22px"
                        }}
                        key={key}
                      >

                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            marginBottom: "10px"
                          }}
                        >
                          <span>{labelMap[key]}</span>

                          <span>{score}%</span>
                        </div>

                        <div
                          style={{
                            width: "100%",
                            height: "12px",
                            background: "#e5e7eb",
                            borderRadius: "999px",
                            overflow: "hidden"
                          }}
                        >

                          <div
                            style={{
                              width: `${score}%`,
                              height: "100%",
                              background: colorMap[key]
                            }}
                          />

                        </div>

                      </div>

                    )

                  })
                }

              </div>

              {/* AI评价 */}

              <div
                style={{
                  background: "#f9fafb",
                  border: "1px solid #e5e7eb",
                  borderRadius: "20px",
                  padding: "28px"
                }}
              >

                <h2
                  style={{
                    fontSize: "24px",
                    fontWeight: "bold",
                    marginBottom: "18px",
                    color: "#111827"
                  }}
                >
                  AI评价
                </h2>

                <p
                  style={{
                    lineHeight: 2,
                    color: "#374151",
                    fontSize: "16px"
                  }}
                >
                  {item.feedback}
                </p>

              </div>

            </div>

          ))

        }

      </div>

    </div>

  )

}
