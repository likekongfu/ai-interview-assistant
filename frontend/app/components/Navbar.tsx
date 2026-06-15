"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { clearSession, getCurrentUser } from "@/lib/auth";

function getUsernameFromSession() {
  const user = getCurrentUser();
  return user?.username || "";
}

export default function Navbar() {
  const router = useRouter();
  const [username, setUsername] = useState("");

  useEffect(() => {
    const syncAuthState = () => {
      setUsername(getUsernameFromSession());
    };

    syncAuthState();
    window.addEventListener("storage", syncAuthState);
    window.addEventListener("auth-change", syncAuthState);

    return () => {
      window.removeEventListener("storage", syncAuthState);
      window.removeEventListener("auth-change", syncAuthState);
    };
  }, []);

  const handleLogin = () => {
    router.push("/login");
  };

  const handleLogout = () => {
    clearSession();
    setUsername("");
    router.push("/login");
  };

  const isLoggedIn = Boolean(username);

  return (
    <nav
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
        zIndex: 1000,
        boxSizing: "border-box",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "40px" }}>
        <div style={{ fontSize: "24px", fontWeight: "bold", color: "#111827" }}>
          AI 面试助手
        </div>

        <Link href="/" style={navLinkStyle}>
          首页
        </Link>

        <Link href="/history" style={navLinkStyle}>
          刷题记录
        </Link>

        <Link href="/interview-records" style={navLinkStyle}>
          面试记录
        </Link>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        <div style={{ color: "#6b7280" }}>
          {isLoggedIn ? `欢迎，${username}` : "未登录"}
        </div>

        {isLoggedIn ? (
          <button onClick={handleLogout} style={authButtonStyle}>
            退出登录
          </button>
        ) : (
          <button onClick={handleLogin} style={authButtonStyle}>
            登录
          </button>
        )}
      </div>
    </nav>
  );
}

const navLinkStyle = {
  textDecoration: "none",
  color: "#374151",
  fontWeight: 500,
};

const authButtonStyle = {
  padding: "10px 18px",
  background: "#111827",
  color: "#ffffff",
  border: "none",
  borderRadius: "8px",
  cursor: "pointer",
  fontWeight: "bold",
};
