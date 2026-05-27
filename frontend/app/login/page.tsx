"use client";
import toast from "react-hot-toast"
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {

    const router = useRouter();

    const [username, setUsername] = useState("");

    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);

    // 登录
    const handleLogin = async () => {
        localStorage.removeItem("token");

        if (!username || !password) {
            toast.error("请输入账号密码");
            return;
        }

        setLoading(true);

        try {

            const res = await fetch(
                "http://127.0.0.1:8000/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${localStorage.getItem("token")}`
                    },
                    body: JSON.stringify({
                        username,
                        password
                    })
                }
            );

            const data = await res.json();

            console.log(data);

            // 登录失败
            if (!data.token) {
                toast.error(data.message || "用户名或密码错误");
                setLoading(false);
                return;
            }

            // 登录成功
            localStorage.setItem("token", data.token);

            localStorage.setItem("username", data.username);
            localStorage.setItem(
                "user_id",
                String(data.user_id)
            )

            toast.success("登录成功");

            // 跳转首页
            router.push("/");

        } catch (error) {

            console.log(error);

            toast.error("登录失败");

        }

        setLoading(false);

    };

    return (

        <div
            style={{
                minHeight: "100vh",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                background: "#f3f4f6"
            }}
        >

            <div
                style={{
                    width: "460px",
                    background: "#fff",
                    padding: "50px",
                    borderRadius: "20px",
                    boxShadow: "0 4px 20px rgba(0,0,0,0.05)"
                }}
            >

                <h1
                    style={{
                        fontSize: "32px",
                        fontWeight: "bold",
                        marginBottom: "30px",
                        textAlign: "center"
                    }}
                >
                    用户登录
                </h1>
                <p
                    style={{
                        color: "#666",
                        marginTop: "12px",
                        marginBottom: "30px",
                        textAlign: "center"
                    }}
                >
                    AI 模拟真实面试，生成专业点评
                </p>

                {/* 用户名 */}

                <input
                    placeholder="请输入用户名"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    style={{
                        width: "100%",
                        padding: "14px",
                        border: "1px solid #e5e7eb",
                        borderRadius: "10px",
                        marginBottom: "18px",
                        fontSize: "15px",
                        background: "#f8fafc"
                    }}
                />

                {/* 密码 */}

                <input
                    type="password"
                    placeholder="请输入密码"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    style={{
                        width: "100%",
                        padding: "14px",
                        marginBottom: "20px",
                        borderRadius: "10px",
                        border: "1px solid #ddd",
                        fontSize: "16px"
                    }}
                />

                {/* 登录按钮 */}

                <button
                    onClick={handleLogin}
                    style={{
                        width: "100%",
                        padding: "14px",
                        background: "linear-gradient(to right, #0f172a, #1e293b)",
                        color: "#fff",
                        border: "none",
                        borderRadius: "10px",
                        fontSize: "16px",
                        fontWeight: "bold",
                        cursor: "pointer"
                    }}
                >
                    {
                        loading
                            ? "登录中..."
                            : "登录"
                    }
                </button>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        marginTop: "18px",
                        fontSize: "14px"
                    }}
                >
                    <span style={{ color: "#666" }}>
                        还没有账号？
                    </span>

                    <span
                        onClick={() => router.push("/register")}
                        style={{
                            color: "#111827",
                            fontWeight: "bold",
                            cursor: "pointer"
                        }}
                    >
                        去注册
                    </span>
                </div>
            </div>

        </div>


    );
}