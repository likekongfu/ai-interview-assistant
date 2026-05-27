"use client"
import Navbar from ".././components/Navbar"
import { useEffect, useState } from "react"

import { useRouter } from "next/navigation"

export default function HistoryPage() {

  const router = useRouter()

  useEffect(() => {

    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
    }

  }, [])

  const [list, setList] = useState<any[]>([])

  const fetchHistory = async () => {

    try {

      const token = localStorage.getItem("token")

      if (!token) {
        router.push("/login")
        return
      }

      const res = await fetch(
        "http://127.0.0.1:8000/history",
        {
          headers: {
            Authorization: `Bearer ${token}`
          },
          cache: "no-store"
        }
      )

      // token失效
      if (res.status === 401) {

        localStorage.removeItem("token")

        router.push("/login")

        return
      }

      const data = await res.json()

      // 防止map报错
      setList(Array.isArray(data) ? data : [])

    } catch (error) {

      console.log(error)

    }

  }

  useEffect(() => {

    fetchHistory()

    // 浏览器返回时重新刷新
    const handlePopState = () => {

      fetchHistory()

      router.refresh()

    }

    window.addEventListener("popstate", handlePopState)

    return () => {

      window.removeEventListener("popstate", handlePopState)

    }

  }, [])

  return (
    <>
      <Navbar />

      <div
        style={{

          padding: "30px",

          background: "#f5f7fb",

          minHeight: "100vh"

        }}
      >

        <h1
          style={{
            fontSize: "34px",
            marginBottom: "24px",
            fontWeight: "bold",
            color: "#111827"
          }}
        >
          历史面试记录
        </h1>

        <div
          style={{
            display: "grid",

            gridTemplateColumns:
              "repeat(auto-fill, minmax(420px, 1fr))",

            gap: "24px"
          }}
        >
          {

            list.map((item: any) => (

              <div
                key={item.id}
                onMouseEnter={(e: any) => {

                  e.currentTarget.style.transform = "translateY(-5px)"

                  e.currentTarget.style.boxShadow =
                    "0 10px 30px rgba(0,0,0,0.08)"
                }}

                onMouseLeave={(e: any) => {

                  e.currentTarget.style.transform = "translateY(0)"

                  e.currentTarget.style.boxShadow =
                    "0 2px 8px rgba(0,0,0,0.05)"
                }}
                onClick={() => router.push(`/history/${item.id}`)}
                style={{

                  background: "#fff",

                  borderRadius: "20px",

                  padding: "28px",

                  cursor: "pointer",

                  border: "1px solid #e5e7eb",

                  boxShadow: "0 4px 20px rgba(0,0,0,0.04)",

                  transition: "all 0.2s ease"

                }}
              >

                <h2
                  style={{
                    fontSize: "30px",
                    fontWeight: "bold",
                    color: "#111827",
                    marginBottom: "20px"
                  }}
                >
                  {item.jd}
                </h2>

                <div
                  style={{
                    marginTop: "10px"
                  }}
                >

                  <div
                    style={{
                      color: "#6b7280",
                      fontSize: "14px"
                    }}
                  >
                    综合评分
                  </div>

                  <div
                    style={{
                      fontSize: "42px",

                      fontWeight: "bold",

                      marginTop: "6px",

                      color:
                        item.overall_score >= 75
                          ? "#22c55e"
                          : item.overall_score >= 60
                            ? "#f59e0b"
                            : "#ef4444"
                    }}
                  >
                    {item.overall_score}
                  </div>

                </div>

                <p
                  style={{
                    color: "#6b7280",

                    lineHeight: "28px",

                    marginTop: "20px",

                    fontSize: "16px"
                  }}
                >
                  {
                    item.feedback
                      ? item.feedback.slice(0, 60) + "..."
                      : "暂无评价"
                  }
                </p>

                <div
                  style={{
                    marginTop: "24px",

                    display: "flex",

                    justifyContent: "space-between",

                    alignItems: "center"
                  }}
                >

                  <span
                    style={{
                      color: "#9ca3af",
                      fontSize: "14px"
                    }}
                  >
                    {item.created_at.replace("T", " ").slice(0, 16)}
                  </span>

                  <span
                    style={{
                      fontWeight: "bold",
                      color: "#111827"
                    }}
                  >
                    查看详情 →
                  </span>

                </div>


              </div>

            ))

          }
        </div>
      </div>
    </>
  )

}