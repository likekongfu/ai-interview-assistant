"use client";

import { useCallback, useEffect, useState, type MouseEvent } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";

import Navbar from "../components/Navbar";
import { apiRequest } from "@/lib/api";
import { getCurrentUser, type CurrentUser } from "@/lib/auth";

type InterviewRecord = {
  id: number;
  resume_name: string;
  status: string;
  overall_score: number | null;
  summary: string | null;
  topic_count: number;
  created_at: string;
  finished_at: string | null;
  report_generated: boolean;
};

export default function InterviewRecordsPage() {
  const router = useRouter();
  const [records, setRecords] = useState<InterviewRecord[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);

  const fetchRecords = useCallback(async (user: CurrentUser) => {
    setLoading(true);
    try {
      const data = await apiRequest<InterviewRecord[]>("/interviews", {
        token: user.token,
      });
      setRecords(Array.isArray(data) ? data : []);
      setSelectedIds([]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "获取面试记录失败");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    const timer = window.setTimeout(() => {
      fetchRecords(user);
    }, 0);

    return () => window.clearTimeout(timer);
  }, [fetchRecords, router]);

  async function handleDelete(
    event: MouseEvent<HTMLButtonElement>,
    id: number
  ) {
    event.stopPropagation();

    if (!window.confirm("确定删除这条面试记录吗？")) return;

    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    setDeleting(true);
    try {
      await apiRequest(`/interviews/${id}`, {
        method: "DELETE",
        token: user.token,
      });
      setRecords((current) => current.filter((item) => item.id !== id));
      setSelectedIds((current) => current.filter((itemId) => itemId !== id));
      toast.success("删除成功");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "删除失败");
    } finally {
      setDeleting(false);
    }
  }

  async function handleBatchDelete() {
    if (selectedIds.length === 0) return;
    if (!window.confirm(`确定删除选中的 ${selectedIds.length} 条面试记录吗？`)) {
      return;
    }

    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    setDeleting(true);
    try {
      await apiRequest("/interviews/batch_delete", {
        method: "DELETE",
        token: user.token,
        body: JSON.stringify({ ids: selectedIds }),
      });
      setRecords((current) =>
        current.filter((item) => !selectedIds.includes(item.id))
      );
      setSelectedIds([]);
      toast.success("批量删除成功");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "批量删除失败");
    } finally {
      setDeleting(false);
    }
  }

  function toggleSelected(id: number) {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((itemId) => itemId !== id)
        : [...current, id]
    );
  }

  function toggleSelectAll(checked: boolean) {
    setSelectedIds(checked ? records.map((item) => item.id) : []);
  }

  return (
    <>
      <Navbar />

      <main
        style={{
          maxWidth: "1080px",
          margin: "32px auto",
          padding: "16px",
        }}
      >
        <header style={{ marginBottom: "28px" }}>
          <h1
            style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: "#111827",
              marginBottom: "10px",
            }}
          >
            面试记录
          </h1>
          <p style={{ color: "#6b7280", fontSize: "15px" }}>
            查看 AI 模拟面试历史，点击记录进入对应面试报告。
          </p>
        </header>

        {selectedIds.length > 0 && (
          <div
            style={{
              background: "#111827",
              color: "#fff",
              padding: "12px 16px",
              borderRadius: "12px",
              marginBottom: "16px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  cursor: "pointer",
                  fontWeight: "bold",
                }}
              >
                <input
                  type="checkbox"
                  checked={records.length > 0 && selectedIds.length === records.length}
                  onChange={(event) => toggleSelectAll(event.target.checked)}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                全选
              </label>

              <div>已选择 {selectedIds.length} 条记录</div>
            </div>

            <button
              onClick={handleBatchDelete}
              disabled={deleting}
              style={{
                background: deleting ? "#9ca3af" : "#ef4444",
                border: "none",
                color: "#fff",
                padding: "9px 14px",
                borderRadius: "8px",
                cursor: deleting ? "not-allowed" : "pointer",
                fontWeight: "bold",
              }}
            >
              {deleting ? "删除中..." : "批量删除"}
            </button>
          </div>
        )}

        <section style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {loading && <EmptyState title="正在加载面试记录..." description="请稍等" />}

          {!loading &&
            records.map((item) => {
              const score = item.overall_score;
              const scoreColor =
                score === null
                  ? "#6b7280"
                  : score >= 80
                    ? "#22c55e"
                    : score >= 60
                      ? "#f59e0b"
                      : "#ef4444";

              return (
                <article
                  key={item.id}
                  data-testid="interview-record-card"
                  onClick={() => router.push(`/interviews/${item.id}/report`)}
                  onMouseEnter={(event) => {
                    event.currentTarget.style.transform = "translateY(-3px)";
                    event.currentTarget.style.boxShadow =
                      "0 10px 30px rgba(0,0,0,0.08)";
                    event.currentTarget.style.background = "#fafafa";
                  }}
                  onMouseLeave={(event) => {
                    event.currentTarget.style.transform = "translateY(0)";
                    event.currentTarget.style.boxShadow =
                      "0 2px 10px rgba(0,0,0,0.04)";
                    event.currentTarget.style.background = "#fff";
                  }}
                  style={{
                    position: "relative",
                    background: "#fff",
                    borderRadius: "16px",
                    padding: "20px 22px",
                    border: "1px solid #e5e7eb",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "16px",
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    boxShadow: "0 2px 10px rgba(0,0,0,0.04)",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(item.id)}
                    onClick={(event) => event.stopPropagation()}
                    onChange={() => toggleSelected(item.id)}
                    style={{
                      position: "absolute",
                      top: "18px",
                      left: "18px",
                      width: "18px",
                      height: "18px",
                      cursor: "pointer",
                    }}
                  />

                  <button
                    onClick={(event) => handleDelete(event, item.id)}
                    data-testid="interview-record-delete-button"
                    disabled={deleting}
                    style={{
                      position: "absolute",
                      top: "14px",
                      right: "16px",
                      border: "none",
                      background: "transparent",
                      color: "#6b7280",
                      cursor: deleting ? "not-allowed" : "pointer",
                      fontSize: "18px",
                      fontWeight: "bold",
                      opacity: deleting ? 0.4 : 0.7,
                      transition: "0.2s",
                    }}
                    onMouseEnter={(event) => {
                      event.currentTarget.style.opacity = "1";
                      event.currentTarget.style.transform = "scale(1.15)";
                    }}
                    onMouseLeave={(event) => {
                      event.currentTarget.style.opacity = deleting ? "0.4" : "0.7";
                      event.currentTarget.style.transform = "scale(1)";
                    }}
                    aria-label="删除面试记录"
                  >
                    ×
                  </button>

                  <div style={{ display: "flex", gap: "16px", flex: 1 }}>
                    <div
                      style={{
                        width: "44px",
                        height: "44px",
                        borderRadius: "12px",
                        background: "#111827",
                        color: "#fff",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "15px",
                        fontWeight: "bold",
                        flexShrink: 0,
                      }}
                    >
                      AI
                    </div>

                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          fontSize: "18px",
                          fontWeight: "bold",
                          color: "#111827",
                          marginBottom: "6px",
                          lineHeight: 1.4,
                        }}
                      >
                        面试 #{item.id}
                      </div>

                      <div
                        style={{
                          color: "#6b7280",
                          lineHeight: 1.65,
                          fontSize: "14px",
                          marginBottom: "10px",
                        }}
                      >
                        {item.summary
                          ? truncateText(item.summary, 90)
                          : item.report_generated
                            ? "报告已生成，点击查看详情。"
                            : "报告尚未生成，点击进入报告页生成。"}
                      </div>

                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "10px",
                          flexWrap: "wrap",
                        }}
                      >
                        <MetaText text={`简历：${item.resume_name || "未知简历"}`} />
                        <Separator />
                        <MetaText text={`Topic：${item.topic_count}`} />
                        <Separator />
                        <StatusBadge status={item.status} />
                        <Separator />
                        <MetaText text={formatDate(item.created_at)} />
                        <Separator />
                        <span
                          style={{
                            color: "#2563eb",
                            fontWeight: "bold",
                            fontSize: "14px",
                          }}
                        >
                          查看报告
                        </span>
                      </div>
                    </div>
                  </div>

                  <div
                    style={{
                      background: scoreColor,
                      color: "#fff",
                      padding: "9px 16px",
                      borderRadius: "999px",
                      fontWeight: "bold",
                      fontSize: "16px",
                      minWidth: "78px",
                      textAlign: "center",
                      flexShrink: 0,
                      boxShadow: "0 4px 14px rgba(0,0,0,0.08)",
                    }}
                  >
                    {score === null ? "未评分" : `${score} 分`}
                  </div>
                </article>
              );
            })}

          {!loading && records.length === 0 && (
            <EmptyState
              title="暂无面试记录"
              description="上传简历并完成一次 AI 模拟面试后，这里会展示你的面试报告入口。"
            />
          )}
        </section>
      </main>
    </>
  );
}

function StatusBadge({ status }: { status: string }) {
  const finished = status === "finished";
  return (
    <span
      style={{
        color: finished ? "#047857" : "#b45309",
        background: finished ? "#ecfdf5" : "#fffbeb",
        borderRadius: "999px",
        padding: "4px 10px",
        fontSize: "13px",
        fontWeight: "bold",
      }}
    >
      {finished ? "已结束" : "进行中"}
    </span>
  );
}

function MetaText({ text }: { text: string }) {
  return <span style={{ color: "#9ca3af", fontSize: "14px" }}>{text}</span>;
}

function Separator() {
  return <span style={{ color: "#d1d5db" }}>·</span>;
}

function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div
      style={{
        background: "#fff",
        borderRadius: "24px",
        padding: "80px 20px",
        textAlign: "center",
        border: "1px solid #e5e7eb",
      }}
    >
      <div
        style={{
          width: "64px",
          height: "64px",
          margin: "0 auto 20px",
          borderRadius: "18px",
          background: "#111827",
          color: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontWeight: "bold",
          fontSize: "22px",
        }}
      >
        AI
      </div>
      <h2
        style={{
          fontSize: "28px",
          fontWeight: "bold",
          color: "#111827",
          marginBottom: "10px",
        }}
      >
        {title}
      </h2>
      <p style={{ color: "#6b7280", fontSize: "16px" }}>{description}</p>
    </div>
  );
}

function truncateText(value: string, maxLength: number) {
  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value;
}

function formatDate(value: string) {
  return value ? value.replace("T", " ").slice(0, 16) : "未知时间";
}
