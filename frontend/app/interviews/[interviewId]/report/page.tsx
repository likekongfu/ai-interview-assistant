"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import toast from "react-hot-toast";

import Navbar from "@/app/components/Navbar";
import { apiRequest } from "@/lib/api";
import { getCurrentUser, type CurrentUser } from "@/lib/auth";

type TopicScore = {
  topic: string;
  score: number;
  comment: string;
};

type InterviewReport = {
  interview_id: number;
  overall_score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  topic_scores: TopicScore[];
  improvement_suggestions: string[];
  study_plan: string[];
};

type ReportStatus = {
  status: "report_not_generated";
  interview_id: number;
};

function isInterviewReport(data: InterviewReport | ReportStatus): data is InterviewReport {
  return "overall_score" in data;
}

export default function InterviewReportPage() {
  const params = useParams<{ interviewId: string }>();
  const router = useRouter();
  const interviewId = Number(params.interviewId);

  const [report, setReport] = useState<InterviewReport | null>(null);
  const [notGenerated, setNotGenerated] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchReport = useCallback(async (user: CurrentUser) => {
    setLoading(true);
    try {
      const data = await apiRequest<InterviewReport | ReportStatus>(
        `/interviews/${interviewId}/report`,
        {
          token: user.token,
        }
      );

      if ("status" in data && data.status === "report_not_generated") {
        setNotGenerated(true);
        setReport(null);
        return;
      }

      if (!isInterviewReport(data)) {
        setNotGenerated(true);
        setReport(null);
        return;
      }

      setReport(data);
      setNotGenerated(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "获取面试报告失败");
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  useEffect(() => {
    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    const timer = window.setTimeout(() => {
      fetchReport(user);
    }, 0);

    return () => window.clearTimeout(timer);
  }, [fetchReport, router]);

  const handleGenerateReport = async () => {
    const currentUser = getCurrentUser();
    if (!currentUser) return;

    setLoading(true);
    try {
      const data = await apiRequest<InterviewReport>(
        `/interviews/${interviewId}/report/generate`,
        {
          method: "POST",
          token: currentUser.token,
        }
      );
      setReport(data);
      setNotGenerated(false);
      toast.success("面试报告已生成");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "生成面试报告失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />

      <main
        style={{
          minHeight: "calc(100vh - 70px)",
          background: "#f5f7fb",
          padding: "32px 24px",
        }}
      >
        <section style={{ maxWidth: "1120px", margin: "0 auto" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "16px",
              marginBottom: "24px",
            }}
          >
            <div>
              <h1 style={{ margin: 0, fontSize: "34px", color: "#111827" }}>
                面试报告
              </h1>
              <p style={{ margin: "8px 0 0", color: "#6b7280" }}>
                面试 ID：{interviewId}
              </p>
            </div>
            <div style={{ display: "flex", gap: "12px" }}>
              {report && (
                <button onClick={handleGenerateReport} style={outlineButtonStyle}>
                  重新生成报告
                </button>
              )}
              <button onClick={() => router.push("/")} style={outlineButtonStyle}>
                返回首页
              </button>
              <button
                onClick={() => router.push("/interview")}
                style={primaryButtonStyle}
              >
                再来一次面试
              </button>
            </div>
          </div>

          {loading && <StateCard text="正在加载面试报告..." />}

          {!loading && notGenerated && (
            <StateCard
              text="当前面试还没有生成报告。"
              actionText="生成面试报告"
              onAction={handleGenerateReport}
            />
          )}

          {!loading && report && (
            <div style={{ display: "grid", gap: "18px" }}>
              <section style={panelStyle}>
                <div style={{ display: "flex", alignItems: "center", gap: "18px" }}>
                  <div style={scoreCircleStyle}>{report.overall_score}</div>
                  <div>
                    <h2 style={sectionTitleStyle}>综合评价</h2>
                    <p style={paragraphStyle}>{report.summary}</p>
                  </div>
                </div>
              </section>

              <section style={panelStyle}>
                <h2 style={sectionTitleStyle}>各 Topic 得分</h2>
                <div style={{ display: "grid", gap: "12px" }}>
                  {report.topic_scores.map((item) => (
                    <div key={item.topic} style={topicRowStyle}>
                      <div>
                        <div style={{ fontWeight: "bold", color: "#111827" }}>
                          {item.topic}
                        </div>
                        <div style={{ color: "#6b7280", marginTop: "6px" }}>
                          {item.comment}
                        </div>
                      </div>
                      <div style={topicScoreStyle}>{item.score}</div>
                    </div>
                  ))}
                </div>
              </section>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    report.strengths.length > 0
                      ? "repeat(2, minmax(0, 1fr))"
                      : "1fr",
                  gap: "18px",
                }}
              >
                {report.strengths.length > 0 && (
                  <ListPanel title="优点" items={report.strengths} />
                )}
                <ListPanel title="不足" items={report.weaknesses} />
              </div>

              <ListPanel title="改进建议" items={report.improvement_suggestions} />
              <ListPanel title="3 天复习计划" items={report.study_plan} />
            </div>
          )}
        </section>
      </main>
    </>
  );
}

function ListPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <section style={panelStyle}>
      <h2 style={sectionTitleStyle}>{title}</h2>
      <ul style={{ margin: 0, paddingLeft: "20px", color: "#374151" }}>
        {items.map((item, index) => (
          <li key={`${title}-${index}`} style={{ marginBottom: "8px", lineHeight: 1.7 }}>
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}

function StateCard({
  text,
  actionText,
  onAction,
}: {
  text: string;
  actionText?: string;
  onAction?: () => void;
}) {
  return (
    <section style={{ ...panelStyle, textAlign: "center", padding: "56px 24px" }}>
      <p style={{ color: "#6b7280", marginBottom: actionText ? "18px" : 0 }}>
        {text}
      </p>
      {actionText && (
        <button onClick={onAction} style={primaryButtonStyle}>
          {actionText}
        </button>
      )}
    </section>
  );
}

const panelStyle = {
  background: "#fff",
  border: "1px solid #e5e7eb",
  borderRadius: "16px",
  padding: "22px",
  boxShadow: "0 8px 24px rgba(15, 23, 42, 0.05)",
};

const sectionTitleStyle = {
  margin: "0 0 12px",
  color: "#111827",
  fontSize: "20px",
};

const paragraphStyle = {
  margin: 0,
  color: "#374151",
  lineHeight: 1.8,
};

const scoreCircleStyle = {
  width: "86px",
  height: "86px",
  borderRadius: "50%",
  background: "#111827",
  color: "#fff",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: "30px",
  fontWeight: "bold",
  flexShrink: 0,
};

const topicRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  gap: "18px",
  padding: "14px",
  border: "1px solid #e5e7eb",
  borderRadius: "12px",
  background: "#f9fafb",
};

const topicScoreStyle = {
  minWidth: "58px",
  height: "38px",
  borderRadius: "999px",
  background: "#2563eb",
  color: "#fff",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontWeight: "bold",
};

const primaryButtonStyle = {
  border: "none",
  borderRadius: "10px",
  background: "#111827",
  color: "#fff",
  padding: "11px 16px",
  fontWeight: "bold",
  cursor: "pointer",
};

const outlineButtonStyle = {
  border: "1px solid #d1d5db",
  borderRadius: "10px",
  background: "#fff",
  color: "#111827",
  padding: "11px 16px",
  fontWeight: "bold",
  cursor: "pointer",
};
