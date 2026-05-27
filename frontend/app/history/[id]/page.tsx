"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

export default function DetailPage() {

  const params = useParams()
  const router = useRouter()

  const id = params.id

  const [data, setData] = useState<any[]>([])

  const [loading, setLoading] = useState(true)

  useEffect(() => {

    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
    }

  }, [])

  // 获取详情数据
  const getDetail = async () => {

    try {

      // 取出 token
      const token = localStorage.getItem("token")

      const res = await fetch(
        `http://127.0.0.1:8000/history/${id}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            "Authorization": `Bearer ${token}`
          }
        }
      )

      // token失效
      if (res.status === 401) {
        alert("请重新登录")
        return
      }

      const result = await res.json()

      setData(result)

      setLoading(false)

    } catch (err) {

      console.log(err)

    }

  }

  // 页面进入时请求
  useEffect(() => {

    if (id) {
      getDetail()
    }

  }, [id])

  // 浏览器返回/前进时重新请求
  useEffect(() => {

    const handlePopState = () => {
      getDetail()
    }

    window.addEventListener("popstate", handlePopState)

    return () => {
      window.removeEventListener("popstate", handlePopState)
    }

  }, [])

  if (data.length === 0 && !loading) {

    return (

      <div style={{ padding: "20px" }}>

        <h2>暂无面试记录</h2>

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

      ```
      <div
        style={{
          maxWidth: "1000px",
          margin: "0 auto"
        }}
      >

        {/* 返回按钮 */}

        <button
          onClick={() => router.push("/history")}
          style={{
            marginBottom: "24px",
            padding: "10px 18px",
            border: "none",
            background: "#111827",
            color: "white",
            borderRadius: "10px",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          ← 返回历史记录
        </button>

        {/* 页面标题 */}

        <div
          style={{
            background: "#ffffff",
            borderRadius: "20px",
            padding: "30px",
            marginBottom: "30px",
            boxShadow: "0 2px 10px rgba(0,0,0,0.05)"
          }}
        >

          <h1
            style={{
              fontSize: "36px",
              fontWeight: "bold",
              marginBottom: "10px"
            }}
          >
            AI 面试分析报告
          </h1>

          <p
            style={{
              color: "#6b7280",
              lineHeight: 1.8
            }}
          >
            AI 根据本次模拟面试生成的综合能力分析
          </p>

        </div>

        {

          data.map((item: any, index: number) => (

            <div
              key={index}
              style={{
                background: "#ffffff",
                borderRadius: "20px",
                padding: "30px",
                marginBottom: "30px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.05)"
              }}
            >

              {/* 问题 */}

              <div style={{ marginBottom: "24px" }}>

                <h2
                  style={{
                    fontSize: "22px",
                    fontWeight: "bold",
                    marginBottom: "12px"
                  }}
                >
                  面试问题
                </h2>

                <p
                  style={{
                    lineHeight: 1.8,
                    color: "#374151"
                  }}
                >
                  {item.question}
                </p>

              </div>

              {/* 回答 */}

              <div style={{ marginBottom: "24px" }}>

                <h2
                  style={{
                    fontSize: "22px",
                    fontWeight: "bold",
                    marginBottom: "12px"
                  }}
                >
                  我的回答
                </h2>

                <p
                  style={{
                    lineHeight: 1.8,
                    color: "#374151"
                  }}
                >
                  {item.answer}
                </p>

              </div>

              {/* 综合评分 */}

              <div
                style={{
                  marginBottom: "30px",
                  padding: "24px",
                  borderRadius: "18px",
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
                    fontSize: "56px",
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

              <div style={{ marginBottom: "30px" }}>

                <h2
                  style={{
                    fontSize: "22px",
                    fontWeight: "bold",
                    marginBottom: "24px"
                  }}
                >
                  能力分析
                </h2>

                {/* 技术能力 */}

                <div style={{ marginBottom: "20px" }}>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px"
                    }}
                  >
                    <span>技术能力</span>

                    <span>{item.technical_score}%</span>
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
                        width: `${item.technical_score}%`,
                        height: "100%",
                        background: "#10b981"
                      }}
                    />

                  </div>

                </div>

                {/* 逻辑表达 */}

                <div style={{ marginBottom: "20px" }}>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px"
                    }}
                  >
                    <span>逻辑表达</span>

                    <span>{item.logic_score}%</span>
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
                        width: `${item.logic_score}%`,
                        height: "100%",
                        background: "#3b82f6"
                      }}
                    />

                  </div>

                </div>

                {/* 工程经验 */}

                <div style={{ marginBottom: "20px" }}>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px"
                    }}
                  >
                    <span>工程经验</span>

                    <span>{item.experience_score}%</span>
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
                        width: `${item.experience_score}%`,
                        height: "100%",
                        background: "#f59e0b"
                      }}
                    />

                  </div>

                </div>

                {/* 沟通表达 */}

                <div>

                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      marginBottom: "8px"
                    }}
                  >
                    <span>沟通表达</span>

                    <span>{item.communication_score}%</span>
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
                        width: `${item.communication_score}%`,
                        height: "100%",
                        background: "#8b5cf6"
                      }}
                    />

                  </div>

                </div>

              </div>

              {/* AI评价 */}

              <div
                style={{
                  background: "#f9fafb",
                  border: "1px solid #e5e7eb",
                  borderRadius: "18px",
                  padding: "24px"
                }}
              >

                <h2
                  style={{
                    fontSize: "22px",
                    fontWeight: "bold",
                    marginBottom: "16px"
                  }}
                >
                  AI评价
                </h2>

                <p
                  style={{
                    lineHeight: 2,
                    color: "#374151"
                  }}
                >
                  {item.feedback}
                </p>

              </div>

            </div>

          ))

        }

      </div>
      ```

    </div>

  )

}