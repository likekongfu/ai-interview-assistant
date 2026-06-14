"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

import { apiRequest } from "@/lib/api";

type RegisterResponse = {
  message: string;
};

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    const trimmedUsername = username.trim();

    if (!trimmedUsername || !password) {
      toast.error("请输入用户名和密码");
      return;
    }

    if (trimmedUsername.length < 3) {
      toast.error("用户名至少 3 位");
      return;
    }

    if (password.length < 6) {
      toast.error("密码至少 6 位");
      return;
    }

    setLoading(true);

    try {
      await apiRequest<RegisterResponse>("/register", {
        method: "POST",
        body: JSON.stringify({
          username: trimmedUsername,
          password,
        }),
      });

      toast.success("注册成功，请登录");
      router.push("/login");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "注册失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main
      style={{
        width: "100%",
        minHeight: "100vh",
        background: "#f5f7fb",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "24px",
      }}
    >
      <section
        style={{
          width: "100%",
          maxWidth: "420px",
          background: "#fff",
          borderRadius: "20px",
          padding: "48px",
          boxShadow: "0 10px 30px rgba(0,0,0,0.05)",
        }}
      >
        <h1
          style={{
            textAlign: "center",
            fontSize: "36px",
            marginBottom: "12px",
            fontWeight: "bold",
          }}
        >
          用户注册
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#666",
            marginBottom: "36px",
            fontSize: "16px",
          }}
        >
          创建你的 AI 面试助手账号
        </p>

        <input
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="请输入用户名"
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid #e5e7eb",
            marginBottom: "20px",
            fontSize: "16px",
            outline: "none",
            boxSizing: "border-box",
          }}
        />

        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleRegister();
          }}
          placeholder="请输入密码"
          style={{
            width: "100%",
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid #e5e7eb",
            marginBottom: "24px",
            fontSize: "16px",
            outline: "none",
            boxSizing: "border-box",
          }}
        />

        <button
          onClick={handleRegister}
          disabled={loading}
          style={{
            width: "100%",
            padding: "16px",
            background: loading ? "#6b7280" : "#111827",
            color: "#fff",
            border: "none",
            borderRadius: "12px",
            fontSize: "18px",
            fontWeight: "bold",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "注册中..." : "注册"}
        </button>

        <div
          style={{
            marginTop: "20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ color: "#666", fontSize: "14px" }}>已有账号？</span>
          <button
            type="button"
            onClick={() => router.push("/login")}
            style={{
              border: "none",
              background: "transparent",
              color: "#111827",
              cursor: "pointer",
              fontWeight: "bold",
              padding: 0,
            }}
          >
            去登录
          </button>
        </div>
      </section>
    </main>
  );
}
