"use client"

import Navbar from "../components/Navbar"
import { useCallback, useEffect, useState, type MouseEvent } from "react"
import { useRouter } from "next/navigation"
import toast from "react-hot-toast"
import { apiFetch } from "@/lib/api"

export default function HistoryPage() {

  const router = useRouter()

  type PracticeHistoryItem = {
    id: number
    jd?: string
    feedback?: string
    overall_score: number
    created_at: string
  }

  const [list, setList] = useState<PracticeHistoryItem[]>([])

  const [selectedIds, setSelectedIds] = useState<number[]>([])

  // 获取历史记录
  const fetchHistory = useCallback(async () => {

    try {

      const token = localStorage.getItem("token")

      if (!token) {
        router.push("/login")
        return
      }

      const res = await apiFetch("/history", {
        token,
        cache: "no-store"
      })

      // token失效
      if (res.status === 401) {

        localStorage.removeItem("token")

        router.push("/login")

        return
      }

      const data = await res.json()

      setList(Array.isArray(data) ? data : [])

    } catch (error) {

      console.log(error)

      toast.error("获取历史记录失败")

    }

  }, [router])

  useEffect(() => {

    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
      return
    }

    const timer = window.setTimeout(() => {
      fetchHistory()
    }, 0)

    // 浏览器返回时刷新
    const handlePopState = () => {

      fetchHistory()

      router.refresh()

    }

    window.addEventListener("popstate", handlePopState)

    return () => {

      window.removeEventListener("popstate", handlePopState)
      window.clearTimeout(timer)

    }

  }, [fetchHistory, router])

  // 删除记录
  const handleDelete = async (
    e: MouseEvent<HTMLButtonElement>,
    id: number
  ) => {

    e.stopPropagation()

    const ok = window.confirm("确定删除这条记录？")

    if (!ok) return

    try {

      const token = localStorage.getItem("token")

      const res = await apiFetch(`/history/single_delete/${id}`, {
        method: "DELETE",
        token
      })

      if (res.ok) {

        setList(list.filter(item => item.id !== id))

        toast.success("删除成功")

      } else {

        toast.error("删除失败")

      }

    } catch (error) {

      console.log(error)

      toast.error("删除失败")

    }

  }

  // 批量删除

  const handleBatchDelete = async () => {

    try {

      const token =
        localStorage.getItem("token")

      const res = await apiFetch("/history/batch_delete/batch_delete", {
        method: "DELETE",
        token,
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ids: selectedIds
        })
      })

      if (res.ok) {

        setList(

          list.filter(
            item =>
              !selectedIds.includes(item.id)
          )

        )

        setSelectedIds([])

        toast.success("批量删除成功")

      } else {

        toast.error("删除失败")

      }

    } catch (error) {

      console.log(error)

      toast.error("删除失败")

    }

  }

  return (
    <>
      <Navbar />

      <div
        style={{
          maxWidth: "1080px",
          margin: "32px auto",
          padding: "16px"
        }}
      >

        {/* 页面标题 */}

        <div
          style={{
            marginBottom: "28px"
          }}
        >

          <h1
            style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#111827",
              marginBottom: "10px"
            }}
          >
            刷题记录
          </h1>

          <p
            style={{
              color: "#6b7280",
              fontSize: "15px"
            }}
          >
            查看刷题练习的题目、评分与反馈记录
          </p>

        </div>

        {
          selectedIds.length > 0 && (

            <div
              style={{
                background: "#111827",
                color: "#fff",
                padding: "12px 16px",
                borderRadius: "12px",
                marginBottom: "16px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}
            >

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "14px"
                }}
              >

                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    cursor: "pointer",
                    fontWeight: "bold"
                  }}
                >

                  <input
                    type="checkbox"

                    checked={
                      list.length > 0 &&
                      selectedIds.length === list.length
                    }

                    onChange={(e) => {

                      if (e.target.checked) {

                        setSelectedIds(
                          list.map(item => item.id)
                        )

                      } else {

                        setSelectedIds([])

                      }

                    }}

                    style={{
                      width: "18px",
                      height: "18px",
                      cursor: "pointer"
                    }}
                  />

                  全选

                </label>

                <div>
                  已选择 {selectedIds.length} 条记录
                </div>

              </div>

              <button
                onClick={handleBatchDelete}
                style={{
                  background: "#ef4444",
                  border: "none",
                  color: "#fff",
                  padding: "9px 14px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontWeight: "bold"
                }}
              >
                批量删除
              </button>

            </div>

          )
        }

        {/* 历史记录列表 */}

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px"
          }}
        >

          {
          list.map((item) => {

              // 分数颜色
              const scoreColor =
                item.overall_score >= 80
                  ? "#22c55e"
                  : item.overall_score >= 60
                    ? "#f59e0b"
                    : "#ef4444"

              return (

                <div
                  key={item.id}
                  data-testid="practice-history-card"
                  onClick={() =>
                    router.push(`/history/${item.id}`)
                  }
                  onMouseEnter={(e: MouseEvent<HTMLDivElement>) => {

                    e.currentTarget.style.transform =
                      "translateY(-3px)"

                    e.currentTarget.style.boxShadow =
                      "0 10px 30px rgba(0,0,0,0.08)"

                    e.currentTarget.style.background =
                      "#fafafa"

                  }}
                  onMouseLeave={(e: MouseEvent<HTMLDivElement>) => {

                    e.currentTarget.style.transform =
                      "translateY(0)"

                    e.currentTarget.style.boxShadow =
                      "0 2px 10px rgba(0,0,0,0.04)"

                    e.currentTarget.style.background =
                      "#fff"

                  }}
                  style={{
                    position: "relative",

                    background: "#fff",

                    borderRadius: "16px",

                    padding: "20px 22px",

                    border: "1px solid #e5e7eb",

                    display: "flex",

                    justifyContent: "space-between",

                    alignItems: "center",

                    gap: "16px",

                    cursor: "pointer",

                    transition: "all 0.2s ease",

                    boxShadow:
                      "0 2px 10px rgba(0,0,0,0.04)"
                  }}
                >
                  <input
                    type="checkbox"

                    checked={
                      selectedIds.includes(item.id)
                    }

                    onClick={(e) => {
                      e.stopPropagation()
                    }}

                    onChange={() => {

                      if (
                        selectedIds.includes(item.id)
                      ) {

                        setSelectedIds(
                          selectedIds.filter(
                            id => id !== item.id
                          )
                        )

                      } else {

                        setSelectedIds([
                          ...selectedIds,
                          item.id
                        ])

                      }

                    }}

                    style={{
                      position: "absolute",
                      top: "18px",
                      left: "18px",
                      width: "18px",
                      height: "18px",
                      cursor: "pointer"
                    }}
                  />

                  {/* 删除按钮 */}

                  <button
                    onClick={(e) =>
                      handleDelete(e, item.id)
                    }
                    data-testid="practice-history-delete-button"
                    style={{
                      position: "absolute",

                      top: "14px",

                      right: "16px",

                      border: "none",

                      background: "transparent",

                      color: "#6b7280",

                      cursor: "pointer",

                      fontSize: "18px",

                      fontWeight: "bold",

                      opacity: 0.7,

                      transition: "0.2s"
                    }}
                    onMouseEnter={(e: MouseEvent<HTMLButtonElement>) => {
                      e.currentTarget.style.opacity = "1"
                      e.currentTarget.style.transform =
                        "scale(1.15)"
                    }}
                    onMouseLeave={(e: MouseEvent<HTMLButtonElement>) => {
                      e.currentTarget.style.opacity = "0.7"
                      e.currentTarget.style.transform =
                        "scale(1)"
                    }}
                    aria-label="删除刷题记录"
                  >
                    ×
                  </button>

                  {/* 左边内容 */}

                  <div
                    style={{
                      display: "flex",
                      gap: "18px",
                      flex: 1
                    }}
                  >

                    {/* 图标 */}

                    <div
                      style={{
                        width: "44px",
                        height: "44px",
                        borderRadius: "12px",
                        background: "#111827",
                        color: "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "18px",
                        flexShrink: 0
                      }}
                    >
                      🤖
                    </div>

                    {/* 文本 */}

                    <div
                      style={{
                        flex: 1
                      }}
                    >

                      {/* JD */}

                      <div
                        style={{
                          fontSize: "18px",
                          fontWeight: "bold",
                          color: "#111827",
                          marginBottom: "6px",
                          lineHeight: "1.45"
                        }}
                      >
                        {
                          item.jd && item.jd.length > 50
                            ? item.jd.slice(0, 50) + "..."
                            : item.jd||""
                        }
                      </div>

                      {/* AI评价 */}

                      <div
                        style={{
                          color: "#6b7280",
                          lineHeight: "1.65",
                          fontSize: "14px",
                          marginBottom: "10px"
                        }}
                      >
                        {
                          item.feedback
                            ? item.feedback.slice(0, 90) + "..."
                            : "暂无评价"
                        }
                      </div>

                      {/* 底部信息 */}

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                          flexWrap: "wrap"
                        }}
                      >

                        <span
                          style={{
                            color: "#9ca3af",
                            fontSize: "13px"
                          }}
                        >
                          {
                            item.created_at
                              .replace("T", " ")
                              .slice(0, 16)
                          }
                        </span>

                        <span
                          style={{
                            color: "#d1d5db"
                          }}
                        >
                          •
                        </span>

                        <span
                          style={{
                            color: "#2563eb",
                            fontWeight: "bold",
                            fontSize: "13px"
                          }}
                        >
                          查看详情
                        </span>

                      </div>

                    </div>

                  </div>

                  {/* 右边分数 */}

                  <div
                    style={{
                      background: scoreColor,

                      color: "#fff",

                      padding: "9px 16px",

                      borderRadius: "999px",

                      fontWeight: "bold",

                      fontSize: "16px",

                      minWidth: "78px",

                      textAlign: "center",

                      flexShrink: 0,

                      boxShadow:
                        "0 4px 14px rgba(0,0,0,0.08)"
                    }}
                  >
                    {item.overall_score} 分
                  </div>

                </div>

              )

            })
          }

          {/* 空状态 */}

          {
            list.length === 0 && (

              <div
                style={{
                  background: "#fff",

                  borderRadius: "24px",

                  padding: "80px 20px",

                  textAlign: "center",

                  border: "1px solid #e5e7eb"
                }}
              >

                <div
                  style={{
                    fontSize: "60px",
                    marginBottom: "20px"
                  }}
                >
                  🤖
                </div>

                <h2
                  style={{
                    fontSize: "28px",
                    fontWeight: "bold",
                    color: "#111827",
                    marginBottom: "10px"
                  }}
                >
                  暂无刷题记录
                </h2>

                <p
                  style={{
                    color: "#6b7280",
                    fontSize: "16px"
                  }}
                >
                  快去首页生成题目，开始一次刷题练习吧
                </p>

              </div>

            )
          }

        </div>

      </div>
    </>
  )

}
