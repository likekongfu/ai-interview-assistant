"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

import { apiRequest } from "@/lib/api";
import { clearSession, saveSession } from "@/lib/auth";

type LoginResponse = {
  token: string;
  username: string;
  user_id: number;
};

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password) {
      toast.error("请输入用户名和密码");
      return;
    }

    setLoading(true);
    clearSession();

    try {
      const data = await apiRequest<LoginResponse>("/login", {
        method: "POST",
        body: JSON.stringify({
          username: trimmedUsername,
          password,
        }),
      });

      saveSession(data);
      toast.success("登录成功");
      router.push("/");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "登录失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#f3f4f6",
        padding: "24px",
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: "460px",
          background: "#fff",
          padding: "48px",
          borderRadius: "20px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
        }}
      >
        <h1
          style={{
            fontSize: "32px",
            fontWeight: "bold",
            marginBottom: "12px",
            textAlign: "center",
          }}
        >
          用户登录
        </h1>

        <p
          style={{
            color: "#666",
            marginBottom: "30px",
            textAlign: "center",
          }}
        >
          登录后开始 AI 模拟面试和刷题练习
        </p>

        <input
          placeholder="请输入用户名"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleLogin();
          }}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="请输入密码"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleLogin();
          }}
          style={{ ...inputStyle, marginBottom: "12px" }}
        />

        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            marginBottom: "20px",
            fontSize: "14px",
          }}
        >
          <button
            type="button"
            onClick={() => router.push("/forgot-password")}
            style={linkButtonStyle}
          >
            忘记密码？
          </button>
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px",
            background: loading ? "#6b7280" : "#111827",
            color: "#fff",
            border: "none",
            borderRadius: "10px",
            fontSize: "16px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "登录中..." : "登录"}
        </button>

        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: "18px",
            fontSize: "14px",
          }}
        >
          <span style={{ color: "#666" }}>还没有账号？</span>
          <button
            type="button"
            onClick={() => router.push("/register")}
            style={linkButtonStyle}
          >
            去注册
          </button>
        </div>
      </section>
    </main>
  );
}

const inputStyle = {
  width: "100%",
  boxSizing: "border-box" as const,
  padding: "14px",
  border: "1px solid #e5e7eb",
  borderRadius: "10px",
  marginBottom: "18px",
  fontSize: "15px",
  background: "#f8fafc",
};

const linkButtonStyle = {
  border: "none",
  background: "transparent",
  color: "#111827",
  fontWeight: "bold",
  cursor: "pointer",
  padding: 0,
};
