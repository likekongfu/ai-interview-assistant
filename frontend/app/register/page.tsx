"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

export default function RegisterPage() {

  const router = useRouter()

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleRegister = async () => {

    if (!username || !password) {
      alert("请输入用户名和密码")
      return
    }

    try {

      setLoading(true)

      const res = await fetch(
        "http://127.0.0.1:8000/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            username,
            password
          })
        }
      )

      const result = await res.json()

      setLoading(false)

      if (result.message === "用户名已存在") {
        alert("用户名已存在")
        return
      }

      alert("注册成功")

      router.push("/login")

    } catch (err) {

      console.log(err)

      setLoading(false)

      alert("注册失败")

    }

  }

  return (

    <div
      style={{
        width: "100%",
        height: "100vh",
        background: "#f5f7fb",
        display: "flex",
        justifyContent: "center",
        alignItems: "center"
      }}
    >

      <div
        style={{
          width: "420px",
          background: "#fff",
          borderRadius: "20px",
          padding: "50px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.05)"
        }}
      >

        <h1
          style={{
            textAlign: "center",
            fontSize: "42px",
            marginBottom: "20px",
            fontWeight: "bold"
          }}
        >
          用户注册
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#666",
            marginBottom: "40px",
            fontSize: "16px"
          }}
        >
          创建你的 AI 面试账号
        </p>

        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="请输入用户名"
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid #e5e7eb",
            marginBottom: "20px",
            fontSize: "16px",
            outline: "none",
            boxSizing: "border-box"
          }}
        />

        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="请输入密码"
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid #e5e7eb",
            marginBottom: "24px",
            fontSize: "16px",
            outline: "none",
            boxSizing: "border-box"
          }}
        />

        <button
          onClick={handleRegister}
          style={{
            width: "100%",
            padding: "16px",
            background: "linear-gradient(135deg,#111827,#1f2937)",
            color: "#fff",
            border: "none",
            borderRadius: "12px",
            fontSize: "18px",
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
          {
            loading
              ? "注册中..."
              : "注册"
          }
        </button>

        <div
          style={{
            marginTop: "20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >

          <span
            style={{
              color: "#666",
              fontSize: "14px"
            }}
          >
            已有账号？
          </span>

          <span
            onClick={() => router.push("/login")}
            style={{
              color: "#111827",
              cursor: "pointer",
              fontWeight: "bold"
            }}
          >
            去登录
          </span>

        </div>

      </div>

    </div>

  )

}