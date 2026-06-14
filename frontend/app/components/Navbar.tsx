"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSyncExternalStore } from "react";

import { clearSession } from "@/lib/auth";

function subscribeAuthChange(callback: () => void) {
  window.addEventListener("storage", callback);
  window.addEventListener("auth-change", callback);

  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("auth-change", callback);
  };
}

function getUsernameSnapshot() {
  return localStorage.getItem("username") || "";
}

function getServerUsernameSnapshot() {
  return "";
}

export default function Navbar() {
  const router = useRouter();
  const username = useSyncExternalStore(
    subscribeAuthChange,
    getUsernameSnapshot,
    getServerUsernameSnapshot
  );

  const handleLogout = () => {
    clearSession();
    router.push("/login");
  };

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
          {username ? `欢迎，${username}` : "未登录"}
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
            fontWeight: "bold",
          }}
        >
          退出登录
        </button>
      </div>
    </nav>
  );
}

const navLinkStyle = {
  textDecoration: "none",
  color: "#374151",
  fontWeight: 500,
};
