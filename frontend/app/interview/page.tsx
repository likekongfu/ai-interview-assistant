"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

import Navbar from "./../components/Navbar";
import { apiFetch, apiRequest } from "@/lib/api";
import { getCurrentUser, type CurrentUser } from "@/lib/auth";

type ChatMessage = {
  role: "ai" | "user";
  content: string;
};

type UploadResumeResponse = {
  resume_id: number;
};

type StartInterviewResponse = {
  interview_id: number;
  first_question: string;
};

type FollowUpResponse = {
  next_question?: string | null;
  topic?: string | null;
  follow_up_count?: number | null;
  finished?: boolean;
  message?: string | null;
};

type ReportLookupResponse = {
  status?: string;
  interview_id: number;
  interview_status?: string;
  finished?: boolean;
};

const RESUME_ID_STORAGE_KEY = "ai_resume_id";
const RESUME_NAME_STORAGE_KEY = "ai_resume_name";
const INTERVIEW_ID_STORAGE_KEY = "ai_interview_id";
const MESSAGE_STORAGE_KEY = "ai_interview_messages";
const FINISHED_STORAGE_KEY = "ai_interview_finished";

export default function AiInterviewPage() {
  const router = useRouter();
  const chatRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const typingTimerRef = useRef<number | null>(null);

  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
  const [resumeId, setResumeId] = useState<number | null>(null);
  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [resumeName, setResumeName] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answer, setAnswer] = useState("");
  const [uploading, setUploading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [sending, setSending] = useState(false);
  const [typing, setTyping] = useState(false);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    const restoreTimer = window.setTimeout(() => {
      clearLegacyInterviewStorage();
      setCurrentUser(user);
      setResumeId(readNumberFromStorage(userStorageKey(user.userId, RESUME_ID_STORAGE_KEY)));
      setInterviewId(
        readNumberFromStorage(userStorageKey(user.userId, INTERVIEW_ID_STORAGE_KEY))
      );
      setResumeName(
        readStringFromStorage(userStorageKey(user.userId, RESUME_NAME_STORAGE_KEY))
      );
      setMessages(readMessagesFromStorage(userStorageKey(user.userId, MESSAGE_STORAGE_KEY)));
      setFinished(
        readBooleanFromStorage(userStorageKey(user.userId, FINISHED_STORAGE_KEY))
      );
    }, 0);

    return () => window.clearTimeout(restoreTimer);
  }, [router]);

  useEffect(() => {
    return () => {
      if (typingTimerRef.current) {
        window.clearTimeout(typingTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!currentUser || !interviewId) return;

    const user = currentUser;
    let cancelled = false;

    async function syncInterviewStatus() {
      try {
        const data = await apiRequest<ReportLookupResponse>(
          `/interviews/${interviewId}/report`,
          {
            token: user.token,
          }
        );

        if (cancelled) return;

        if (data.finished || data.interview_status === "finished") {
          setFinished(true);
          localStorage.setItem(
            userStorageKey(user.userId, FINISHED_STORAGE_KEY),
            "true"
          );
          return;
        }

        setFinished(false);
        localStorage.removeItem(userStorageKey(user.userId, FINISHED_STORAGE_KEY));
      } catch {
        setResumeId(null);
        setResumeName("");
        setInterviewId(null);
        setAnswer("");
        setFinished(false);
        setTyping(false);
        setMessages([]);
        localStorage.removeItem(userStorageKey(user.userId, RESUME_ID_STORAGE_KEY));
        localStorage.removeItem(userStorageKey(user.userId, RESUME_NAME_STORAGE_KEY));
        localStorage.removeItem(userStorageKey(user.userId, INTERVIEW_ID_STORAGE_KEY));
        localStorage.removeItem(userStorageKey(user.userId, MESSAGE_STORAGE_KEY));
        localStorage.removeItem(userStorageKey(user.userId, FINISHED_STORAGE_KEY));
        toast.error("当前账号无权访问本地缓存的面试记录，已清空本地面试状态");
      }
    }

    syncInterviewStatus();

    return () => {
      cancelled = true;
    };
  }, [currentUser, interviewId]);

  function scrollChatToBottom(behavior: ScrollBehavior = "auto") {
    const chat = chatRef.current;
    if (!chat) return;

    chat.scrollTo({
      top: chat.scrollHeight,
      behavior,
    });
  }

  useEffect(() => {
    scrollChatToBottom("smooth");
  }, [messages]);

  const saveMessages = (nextMessages: ChatMessage[]) => {
    setMessages(nextMessages);
    if (currentUser) {
      localStorage.setItem(
        userStorageKey(currentUser.userId, MESSAGE_STORAGE_KEY),
        JSON.stringify(nextMessages)
      );
    }
  };

  function clearCurrentInterviewState() {
    if (!currentUser) return;

    if (typingTimerRef.current) {
      window.clearTimeout(typingTimerRef.current);
      typingTimerRef.current = null;
    }

    setResumeId(null);
    setResumeName("");
    setInterviewId(null);
    setAnswer("");
    setFinished(false);
    setTyping(false);
    setMessages([]);
    localStorage.removeItem(userStorageKey(currentUser.userId, RESUME_ID_STORAGE_KEY));
    localStorage.removeItem(userStorageKey(currentUser.userId, RESUME_NAME_STORAGE_KEY));
    localStorage.removeItem(userStorageKey(currentUser.userId, INTERVIEW_ID_STORAGE_KEY));
    localStorage.removeItem(userStorageKey(currentUser.userId, MESSAGE_STORAGE_KEY));
    localStorage.removeItem(userStorageKey(currentUser.userId, FINISHED_STORAGE_KEY));
  }

  const streamAiMessage = (content: string, baseMessages: ChatMessage[]) => {
    setTyping(true);

    return new Promise<void>((resolve) => {
      let index = 0;
      const stepSize = Math.max(1, Math.ceil(content.length / 120));

      const tick = () => {
        index = Math.min(content.length, index + stepSize);
        const streamedMessages = [
          ...baseMessages,
          {
            role: "ai" as const,
            content: content.slice(0, index),
          },
        ];

        setMessages(streamedMessages);
        scrollChatToBottom("auto");

        if (index >= content.length) {
          if (currentUser) {
            localStorage.setItem(
              userStorageKey(currentUser.userId, MESSAGE_STORAGE_KEY),
              JSON.stringify(streamedMessages)
            );
          }
          setTyping(false);
          resolve();
          return;
        }

        typingTimerRef.current = window.setTimeout(tick, 18);
      };

      tick();
    });
  };

  const handleUploadResume = async (file: File | null) => {
    if (!file) return;
    if (!currentUser) {
      router.push("/login");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);

    try {
      const response = await apiFetch("/upload_resume", {
        method: "POST",
        token: currentUser.token,
        body: formData,
      });

      const data = (await response.json().catch(() => null)) as
        | UploadResumeResponse
        | { detail?: string; message?: string }
        | null;

      if (!response.ok || !data || !("resume_id" in data)) {
        const errorData = data && !("resume_id" in data) ? data : null;
        throw new Error(getUploadErrorMessage(errorData, response.status));
      }

      setResumeId(data.resume_id);
      setResumeName(file.name);
      setInterviewId(null);
      setFinished(false);
      saveMessages([]);

      localStorage.setItem(
        userStorageKey(currentUser.userId, RESUME_ID_STORAGE_KEY),
        String(data.resume_id)
      );
      localStorage.setItem(userStorageKey(currentUser.userId, RESUME_NAME_STORAGE_KEY), file.name);
      localStorage.removeItem(userStorageKey(currentUser.userId, INTERVIEW_ID_STORAGE_KEY));
      localStorage.removeItem(userStorageKey(currentUser.userId, FINISHED_STORAGE_KEY));

      toast.success("简历上传成功");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "简历上传失败");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleStartInterview = async () => {
    if (!currentUser) {
      router.push("/login");
      return;
    }

    if (!resumeId) {
      toast.error("请先上传简历");
      return;
    }

    setStarting(true);
    setFinished(false);
    localStorage.removeItem(userStorageKey(currentUser.userId, FINISHED_STORAGE_KEY));
    saveMessages([]);

    try {
      const data = await apiRequest<StartInterviewResponse>(
        `/interview/start?resume_id=${resumeId}`,
        {
          method: "POST",
          token: currentUser.token,
        }
      );

      setInterviewId(data.interview_id);
      localStorage.setItem(
        userStorageKey(currentUser.userId, INTERVIEW_ID_STORAGE_KEY),
        String(data.interview_id)
      );
      await streamAiMessage(data.first_question, []);
      toast.success("面试已开始");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "无法开始面试");
    } finally {
      setStarting(false);
    }
  };

  const handleSendAnswer = async () => {
    if (!currentUser) {
      router.push("/login");
      return;
    }

    if (!resumeId || !interviewId) {
      toast.error("请先上传简历并开始面试");
      return;
    }

    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer) {
      toast.error("请输入回答");
      return;
    }

    const userMessage: ChatMessage = {
      role: "user",
      content: trimmedAnswer,
    };
    const pendingMessages = [...messages, userMessage];

    saveMessages(pendingMessages);
    setAnswer("");
    setSending(true);

    try {
      const data = await apiRequest<FollowUpResponse>("/follow_up", {
        method: "POST",
        token: currentUser.token,
        body: JSON.stringify({
          resume_id: resumeId,
          interview_id: interviewId,
          answer: trimmedAnswer,
        }),
      });

      if (data.finished) {
        await streamAiMessage(data.message || "面试结束", pendingMessages);
        setFinished(true);
        localStorage.setItem(
          userStorageKey(currentUser.userId, FINISHED_STORAGE_KEY),
          "true"
        );
        toast.success("面试已结束");
        return;
      }

      await streamAiMessage(
        data.next_question || "请继续补充你的回答。",
        pendingMessages
      );
    } catch (error) {
      if (error instanceof Error && error.message.includes("无权")) {
        clearCurrentInterviewState();
        toast.error("当前账号无权访问该面试，已清空本地面试状态");
        return;
      }
      saveMessages(messages);
      toast.error(error instanceof Error ? error.message : "提交回答失败");
    } finally {
      setSending(false);
    }
  };

  const handleResetSession = () => {
    if (typingTimerRef.current) {
      window.clearTimeout(typingTimerRef.current);
      typingTimerRef.current = null;
    }

    setResumeId(null);
    setResumeName("");
    setInterviewId(null);
    setAnswer("");
    setFinished(false);
    setTyping(false);
    saveMessages([]);
    if (currentUser) {
      localStorage.removeItem(userStorageKey(currentUser.userId, RESUME_ID_STORAGE_KEY));
      localStorage.removeItem(userStorageKey(currentUser.userId, RESUME_NAME_STORAGE_KEY));
      localStorage.removeItem(userStorageKey(currentUser.userId, INTERVIEW_ID_STORAGE_KEY));
      localStorage.removeItem(userStorageKey(currentUser.userId, FINISHED_STORAGE_KEY));
    }
    toast.success("已清空当前面试");
  };

  const busy = uploading || starting || sending || typing;
  const canStart = Boolean(resumeId) && !busy;
  const canAnswer = Boolean(interviewId) && !finished && !busy;

  return (
    <>
      <Navbar />

      <main
        style={{
          height: "calc(100vh - 70px)",
          background: "#f5f7fb",
          padding: "24px",
          fontFamily: "Arial, Helvetica, sans-serif",
          boxSizing: "border-box",
          overflow: "hidden",
        }}
      >
        <section
          style={{
            maxWidth: "1120px",
            height: "100%",
            margin: "0 auto",
            display: "grid",
            gridTemplateColumns: "minmax(280px, 360px) minmax(0, 1fr)",
            gap: "24px",
            alignItems: "stretch",
          }}
        >
          <aside
            style={{
              background: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "18px",
              padding: "24px",
              boxShadow: "0 8px 24px rgba(15, 23, 42, 0.05)",
              overflowY: "auto",
            }}
          >
            <div style={{ marginBottom: "24px" }}>
              <h1
                style={{
                  fontSize: "30px",
                  lineHeight: 1.2,
                  margin: "0 0 10px",
                  color: "#111827",
                }}
              >
                AI 模拟面试
              </h1>
              <p
                style={{
                  margin: 0,
                  color: "#6b7280",
                  lineHeight: 1.7,
                  fontSize: "15px",
                }}
              >
                上传简历后，AI 会基于你的经历生成第一题，并根据回答持续追问。
              </p>
            </div>

            <label
              style={{
                display: "block",
                border: "1px dashed #9ca3af",
                borderRadius: "14px",
                padding: "22px",
                background: "#f9fafb",
                cursor: uploading ? "not-allowed" : "pointer",
                marginBottom: "16px",
              }}
            >
              <input
                data-testid="resume-file-input"
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                disabled={uploading}
                onChange={(event) =>
                  handleUploadResume(event.target.files?.[0] || null)
                }
                style={{ display: "none" }}
              />
              <div
                style={{
                  fontWeight: "bold",
                  color: "#111827",
                  marginBottom: "8px",
                }}
              >
                {uploading ? "正在上传简历..." : "上传简历"}
              </div>
              <div style={{ color: "#6b7280", fontSize: "14px" }}>
                支持 PDF、DOCX、TXT
              </div>
            </label>

            <div
              style={{
                minHeight: "52px",
                borderRadius: "12px",
                background: resumeId ? "#ecfdf5" : "#f3f4f6",
                color: resumeId ? "#047857" : "#6b7280",
                padding: "12px 14px",
                marginBottom: "16px",
                fontSize: "14px",
                lineHeight: 1.5,
                wordBreak: "break-word",
              }}
            >
              {resumeId
                ? `已上传：${resumeName || `简历 #${resumeId}`}`
                : "还未上传简历"}
            </div>

            <button
              data-testid="start-interview-button"
              onClick={handleStartInterview}
              disabled={!canStart}
              style={{
                width: "100%",
                padding: "14px",
                border: "none",
                borderRadius: "12px",
                background: canStart ? "#111827" : "#9ca3af",
                color: "#fff",
                fontWeight: "bold",
                fontSize: "16px",
                cursor: canStart ? "pointer" : "not-allowed",
                marginBottom: "12px",
              }}
            >
              {starting ? "正在生成第一题..." : "开始面试"}
            </button>

            <button
              data-testid="reset-interview-button"
              onClick={handleResetSession}
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #e5e7eb",
                borderRadius: "12px",
                background: "#fff",
                color: "#374151",
                fontWeight: "bold",
                cursor: "pointer",
              }}
            >
              重新开始
            </button>

            {finished && interviewId && (
              <button
                data-testid="generate-report-button"
                onClick={() => router.push(`/interviews/${interviewId}/report`)}
                disabled={false}
                style={{
                  width: "100%",
                  padding: "12px",
                  border: "none",
                  borderRadius: "12px",
                  background: "#2563eb",
                  color: "#fff",
                  fontWeight: "bold",
                  cursor: "pointer",
                  marginTop: "12px",
                }}
              >
                查看面试报告
              </button>
            )}

            <div
              style={{
                marginTop: "22px",
                display: "grid",
                gap: "10px",
                color: "#4b5563",
                fontSize: "14px",
              }}
            >
              <StatusRow label="简历" active={Boolean(resumeId)} />
              <StatusRow label="面试" active={Boolean(interviewId)} />
              <StatusRow
                label="状态"
                active={!finished}
                text={finished ? "已结束" : "进行中"}
              />
            </div>
          </aside>

          <section
            style={{
              background: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "18px",
              boxShadow: "0 8px 24px rgba(15, 23, 42, 0.05)",
              display: "flex",
              flexDirection: "column",
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "18px 22px",
                borderBottom: "1px solid #e5e7eb",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "16px",
                flexShrink: 0,
              }}
            >
              <div>
                <div style={{ fontWeight: "bold", color: "#111827" }}>
                  面试对话
                </div>
                <div
                  style={{
                    color: "#6b7280",
                    fontSize: "13px",
                    marginTop: "4px",
                  }}
                >
                  {interviewId
                    ? `面试 ID：${interviewId}`
                    : "上传简历并点击开始面试后，AI 会立即提问"}
                </div>
              </div>
              <div
                data-testid="interview-status"
                style={{
                  borderRadius: "999px",
                  padding: "7px 12px",
                  background: finished
                    ? "#fef2f2"
                    : interviewId
                      ? "#ecfdf5"
                      : "#f3f4f6",
                  color: finished
                    ? "#b91c1c"
                    : interviewId
                      ? "#047857"
                      : "#6b7280",
                  fontSize: "13px",
                  fontWeight: "bold",
                  whiteSpace: "nowrap",
                }}
              >
                {finished ? "已结束" : interviewId ? "面试中" : "待开始"}
              </div>
            </div>

            <div
              data-testid="chat-messages"
              ref={chatRef}
              style={{
                flex: 1,
                minHeight: 0,
                padding: "24px",
                overflowY: "auto",
                background: "#fafafa",
              }}
            >
              {messages.length === 0 ? (
                <EmptyChat />
              ) : (
                <div style={{ display: "grid", gap: "18px" }}>
                  {messages.map((message, index) => (
                    <ChatBubble key={`${message.role}-${index}`} message={message} />
                  ))}
                  {sending && !typing && (
                    <ChatBubble
                      message={{
                        role: "ai",
                        content: "正在思考下一个追问...",
                      }}
                      muted
                    />
                  )}
                </div>
              )}
            </div>

            <div
              style={{
                padding: "18px",
                borderTop: "1px solid #e5e7eb",
                background: "#fff",
                flexShrink: 0,
              }}
            >
              <textarea
                data-testid="answer-input"
                rows={3}
                placeholder={
                  interviewId
                    ? "请输入你的回答，支持结合项目经历、技术细节和取舍分析..."
                    : "请先上传简历并开始面试"
                }
                value={answer}
                disabled={!canAnswer}
                onChange={(event) => setAnswer(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                    handleSendAnswer();
                  }
                }}
                style={{
                  width: "100%",
                  resize: "none",
                  boxSizing: "border-box",
                  border: "1px solid #d1d5db",
                  borderRadius: "14px",
                  padding: "14px",
                  fontSize: "15px",
                  lineHeight: 1.7,
                  outline: "none",
                  background: canAnswer ? "#fff" : "#f9fafb",
                  color: "#111827",
                  marginBottom: "12px",
                }}
              />

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <span style={{ color: "#9ca3af", fontSize: "13px" }}>
                  Ctrl / Cmd + Enter 快速提交
                </span>
                <button
                  data-testid="submit-answer-button"
                  onClick={handleSendAnswer}
                  disabled={!canAnswer}
                  style={{
                    minWidth: "120px",
                    padding: "12px 18px",
                    border: "none",
                    borderRadius: "12px",
                    background: canAnswer ? "#2563eb" : "#9ca3af",
                    color: "#fff",
                    fontWeight: "bold",
                    cursor: canAnswer ? "pointer" : "not-allowed",
                  }}
                >
                  {sending || typing ? "生成中..." : "提交回答"}
                </button>
              </div>
            </div>
          </section>
        </section>
      </main>
    </>
  );
}

function EmptyChat() {
  return (
    <div
      style={{
        height: "100%",
        minHeight: "360px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        color: "#6b7280",
        lineHeight: 1.8,
      }}
    >
      <div>
        <div
          style={{
            width: "54px",
            height: "54px",
            borderRadius: "16px",
            background: "#111827",
            color: "#fff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto 16px",
            fontWeight: "bold",
          }}
        >
          AI
        </div>
        上传简历并点击开始面试后，第一题会显示在这里。
      </div>
    </div>
  );
}

function ChatBubble({
  message,
  muted = false,
}: {
  message: ChatMessage;
  muted?: boolean;
}) {
  const isAi = message.role === "ai";

  return (
    <div
      data-testid={isAi ? "ai-message" : "user-message"}
      style={{
        display: "flex",
        justifyContent: isAi ? "flex-start" : "flex-end",
        gap: "10px",
      }}
    >
      {isAi && <Avatar label="AI" />}
      <div
        style={{
          maxWidth: "76%",
          borderRadius: isAi ? "16px 16px 16px 4px" : "16px 16px 4px 16px",
          padding: "13px 15px",
          background: isAi ? "#fff" : "#2563eb",
          color: isAi ? "#111827" : "#fff",
          border: isAi ? "1px solid #e5e7eb" : "1px solid #2563eb",
          lineHeight: 1.7,
          whiteSpace: "pre-wrap",
          opacity: muted ? 0.7 : 1,
          boxShadow: "0 2px 10px rgba(15, 23, 42, 0.04)",
        }}
      >
        {message.content}
      </div>
      {!isAi && <Avatar label="我" dark />}
    </div>
  );
}

function Avatar({ label, dark = false }: { label: string; dark?: boolean }) {
  return (
    <div
      style={{
        width: "34px",
        height: "34px",
        borderRadius: "12px",
        background: dark ? "#2563eb" : "#111827",
        color: "#fff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "13px",
        fontWeight: "bold",
        flexShrink: 0,
      }}
    >
      {label}
    </div>
  );
}

function StatusRow({
  label,
  active,
  text,
}: {
  label: string;
  active: boolean;
  text?: string;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between" }}>
      <span>{label}</span>
      <span style={{ color: active ? "#047857" : "#9ca3af", fontWeight: "bold" }}>
        {text || (active ? "已就绪" : "待完成")}
      </span>
    </div>
  );
}

function readNumberFromStorage(key: string) {
  if (typeof window === "undefined") return null;
  const value = localStorage.getItem(key);
  return value ? Number(value) : null;
}

function readStringFromStorage(key: string) {
  if (typeof window === "undefined") return "";
  return localStorage.getItem(key) || "";
}

function readBooleanFromStorage(key: string) {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(key) === "true";
}

function readMessagesFromStorage(key: string): ChatMessage[] {
  if (typeof window === "undefined") return [];

  try {
    const rawMessages = localStorage.getItem(key);
    return rawMessages ? JSON.parse(rawMessages) : [];
  } catch {
    return [];
  }
}

function userStorageKey(userId: string, key: string) {
  return `ai_user_${userId}_${key}`;
}

function clearLegacyInterviewStorage() {
  if (typeof window === "undefined") return;

  [
    RESUME_ID_STORAGE_KEY,
    RESUME_NAME_STORAGE_KEY,
    INTERVIEW_ID_STORAGE_KEY,
    MESSAGE_STORAGE_KEY,
    FINISHED_STORAGE_KEY,
  ].forEach((key) => localStorage.removeItem(key));
}

function getUploadErrorMessage(
  data: { detail?: string; message?: string } | null,
  status: number
) {
  return data?.detail || data?.message || `简历上传失败，状态码：${status}`;
}
