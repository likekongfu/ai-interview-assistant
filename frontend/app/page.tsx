"use client";

import { useRouter } from "next/navigation";
import Navbar from "./components/Navbar";

export default function Home() {
  const router = useRouter();

  return (
    <>
      <Navbar />

      <main
        style={{
          maxWidth: "1200px",
          margin: "80px auto",
          padding: "20px",
        }}
      >
        <h1
          style={{
            fontSize: "48px",
            fontWeight: "bold",
            textAlign: "center",
            marginBottom: "20px",
          }}
        >
          AI 面试助手
        </h1>

        <p
          style={{
            textAlign: "center",
            color: "#666",
            marginBottom: "60px",
          }}
        >
          选择适合你的面试练习模式
        </p>

        <div
          style={{
            display: "flex",
            gap: "30px",
            justifyContent: "center",
          }}
        >
          <section
            style={{
              width: "450px",
              background: "#fff",
              borderRadius: "20px",
              padding: "40px",
              boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
            }}
          >
            <h2
              style={{
                fontSize: "28px",
                marginBottom: "20px",
              }}
            >
              AI 模拟面试
            </h2>

            <p
              style={{
                lineHeight: "1.8",
                color: "#666",
                minHeight: "120px",
              }}
            >
              AI 根据你的回答动态追问，自主控制面试轮次，模拟真实技术面试流程。
            </p>

            <button
              data-testid="home-ai-interview-button"
              onClick={() => router.push("/interview")}
              style={{
                width: "100%",
                padding: "14px",
                background: "#111827",
                color: "#fff",
                border: "none",
                borderRadius: "12px",
                cursor: "pointer",
                fontSize: "16px",
                fontWeight: "bold",
              }}
            >
              开始 AI 面试
            </button>
          </section>

          <section
            style={{
              width: "450px",
              background: "#fff",
              borderRadius: "20px",
              padding: "40px",
              boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
            }}
          >
            <h2
              style={{
                fontSize: "28px",
                marginBottom: "20px",
              }}
            >
              快速刷题
            </h2>

            <p
              style={{
                lineHeight: "1.8",
                color: "#666",
                minHeight: "120px",
              }}
            >
              根据 JD 生成 5 道核心面试题，快速检测知识掌握程度，适合面试前冲刺。
            </p>

            <button
              data-testid="home-practice-button"
              onClick={() => router.push("/practice")}
              style={{
                width: "100%",
                padding: "14px",
                background: "#2563eb",
                color: "#fff",
                border: "none",
                borderRadius: "12px",
                cursor: "pointer",
                fontSize: "16px",
                fontWeight: "bold",
              }}
            >
              开始刷题
            </button>
          </section>
        </div>
      </main>
    </>
  );
}
