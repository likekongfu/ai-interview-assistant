"use client";

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"


export default function Navbar() {

  const router = useRouter()

  const [username, setUsername] = useState("")

  useEffect(() => {

  const name = localStorage.getItem("username")

  if (name) {
    setUsername(name)
  }

}, [])

  const handleLogout = () => {

    localStorage.removeItem("token")
    localStorage.removeItem("username")

    router.push("/login")

  }

  return (

    <div
      style={{
        width: "100%",
        height: "70px",
        background: "#ffffff",
        borderBottom: "1px solid #e5e7eb",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "0 40px",
        position: "sticky",
        top: 0,
        zIndex: 1000
      }}
    >

      {/* 左侧 */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "40px"
        }}
      >

        <div
          style={{
            fontSize: "24px",
            fontWeight: "bold",
            color: "#111827"
          }}
        >
          AI面试助手
        </div>

        <Link
          href="/"
          style={{
            textDecoration: "none",
            color: "#374151",
            fontWeight: 500
          }}
        >
          首页
        </Link>

        <Link
          href="/history"
          style={{
            textDecoration: "none",
            color: "#374151",
            fontWeight: 500
          }}
        >
          历史记录
        </Link>

      </div>

      {/* 右侧 */}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "20px"
        }}
      >

        <div
          style={{
            color: "#6b7280"
          }}
        >
          欢迎，{username}
        </div>

        <button
          onClick={handleLogout}
          style={{
            padding: "10px 18px",
            background: "#111827",
            color: "#ffffff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          退出登录
        </button>

      </div>

    </div>

  )

}