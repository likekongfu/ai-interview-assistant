"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

import { apiRequest } from "@/lib/api";

type ResetPasswordResponse = {
  message: string;
};

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResetPassword = async () => {
    const trimmedUsername = username.trim();

    if (!trimmedUsername || !newPassword || !confirmPassword) {
      toast.error("请完整填写用户名和新密码");
      return;
    }

    if (newPassword.length < 6) {
      toast.error("新密码至少 6 位");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("两次输入的新密码不一致");
      return;
    }

    setLoading(true);

    try {
      await apiRequest<ResetPasswordResponse>("/reset_password", {
        method: "POST",
        body: JSON.stringify({
          username: trimmedUsername,
          new_password: newPassword,
        }),
      });

      toast.success("密码已重置，请重新登录");
      router.push("/login");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "重置密码失败");
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
          重置密码
        </h1>

        <p
          style={{
            color: "#666",
            marginBottom: "30px",
            textAlign: "center",
            lineHeight: 1.7,
          }}
        >
          输入用户名并设置新密码，完成后可使用新密码登录。
        </p>

        <input
          placeholder="请输入用户名"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="请输入新密码"
          value={newPassword}
          onChange={(event) => setNewPassword(event.target.value)}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="请再次输入新密码"
          value={confirmPassword}
          onChange={(event) => setConfirmPassword(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") handleResetPassword();
          }}
          style={{ ...inputStyle, marginBottom: "24px" }}
        />

        <button
          onClick={handleResetPassword}
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
          {loading ? "重置中..." : "确认重置"}
        </button>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginTop: "18px",
            fontSize: "14px",
          }}
        >
          <button
            type="button"
            onClick={() => router.push("/login")}
            style={linkButtonStyle}
          >
            返回登录
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
