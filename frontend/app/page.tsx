"use client";
import toast from "react-hot-toast"
import Navbar from "./components/Navbar"
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function App() {

  const router = useRouter()
  const [userId, setUserId] = useState("")

  useEffect(() => {

    const token = localStorage.getItem("token")

    const storedUserId =
      localStorage.getItem("user_id")

    if (!token) {
      router.push("/login")
      return
    }

    if (storedUserId) {

      setUserId(storedUserId)

      // 恢复题目
      const savedQuestions =
        localStorage.getItem(
          `questions_${storedUserId}`
        )

      if (savedQuestions) {
        setQuestions(JSON.parse(savedQuestions))
      }

      // 恢复回答
      const savedAnswers =
        localStorage.getItem(
          `answers_${storedUserId}`
        )

      if (savedAnswers) {
        setAnswers(JSON.parse(savedAnswers))
      }

      // 恢复题号
      const savedIndex =
        localStorage.getItem(
          `currentIndex_${storedUserId}`
        )

      if (savedIndex) {
        setCurrentIndex(Number(savedIndex))
      }

      // 恢复JD
      const savedJd =
        localStorage.getItem(
          `jd_${storedUserId}`
        )

      if (savedJd) {
        setJd(savedJd)
      }

      // 恢复 interviewId
      const savedInterviewId =
        localStorage.getItem(
          `interviewId_${storedUserId}`
        )

      if (savedInterviewId) {
        setInterviewId(Number(savedInterviewId))
      }

    }

  }, [])

  // 面试ID
  const [interviewId, setInterviewId] = useState(null);

  // JD
  const [jd, setJd] = useState("");

  // 面试题
  const [questions, setQuestions] = useState([]);

  // 当前题目索引
  const [currentIndex, setCurrentIndex] = useState(0);

  // loading
  const [loading, setLoading] = useState(false);

  // 回答
  const [answers, setAnswers] = useState({});

  // AI评分
  const [feedbacks, setFeedbacks] = useState({});

  // 当前评分中的题目
  const [gradingIndex, setGradingIndex] = useState(null);

  // 难度
  const [level, setLevel] = useState("中级");

  // 生成题目
  const generateQuestions = async () => {
    const token = localStorage.getItem("token");
    if (!jd.trim()) {
      toast.error("请输入岗位JD");
      return;
    }

    setLoading(true);

    // 清空旧数据
    setQuestions([]);
    setAnswers({});
    setFeedbacks({});
    setCurrentIndex(0);

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/generate_questions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            jd,
            level
          })
        }
      );

      const data = await res.json();

      setInterviewId(data.interview_id);

      localStorage.setItem(
        `interviewId_${userId}`,
        String(data.interview_id)
      )

      setQuestions(data.question);

      localStorage.setItem(
        `questions_${userId}`,
        JSON.stringify(data.question)
      )

      localStorage.setItem(
        `jd_${userId}`,
        jd
      )

    } catch (error) {

      console.log(error);

      toast.error("生成失败");

    }

    setLoading(false);
  };

  // AI评分
  const evaluateAnswer = async (question, index) => {
    const token = localStorage.getItem("token");

    if (!answers[index]) {
      toast.error("请先输入回答");
      return;
    }

    setGradingIndex(index);

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/evaluate_answer",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            interview_id: interviewId,
            question: question,
            answer: answers[index]
          })
        }
      );

      const data = await res.json();

      setFeedbacks({
        ...feedbacks,
        [index]: data.result
      });

    } catch (error) {

      console.log(error);

      toast.error("评分失败");

    }

    setGradingIndex(null);
  };

  return (
    <>
      <Navbar />

      <div
        style={{
          maxWidth: "1000px",
          margin: "60px auto",
          padding: "20px",
          fontFamily: "Arial",
          background: "#f8fafc",
          minHeight: "100vh"
        }}
      >

        {/* 标题 */}

        <div
          style={{
            marginBottom: "40px"
          }}
        >

          <h1
            style={{
              fontSize: "48px",
              fontWeight: "bold",
              marginBottom: "10px",
              color: "#111827"
            }}
          >
            AI 面试助手
          </h1>

          <p
            style={{
              color: "#6b7280",
              fontSize: "18px"
            }}
          >
            输入岗位JD，AI自动生成面试题并进行智能评分
          </p>

        </div>

        {/* JD区域 */}

        <div
          style={{
            background: "#fff",
            padding: "30px",
            borderRadius: "20px",
            boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
            marginBottom: "40px"
          }}
        >

          {/* 难度 */}

          <div
            style={{
              marginBottom: "20px"
            }}
          >

            <p
              style={{
                marginBottom: "10px",
                fontWeight: "bold",
                color: "#374151"
              }}
            >
              面试难度
            </p>

            <select
              value={level}
              onChange={(e) => setLevel(e.target.value)}
              style={{
                padding: "10px",
                borderRadius: "8px",
                border: "1px solid #ddd",
                fontSize: "15px"
              }}
            >
              <option>初级</option>
              <option>中级</option>
              <option>高级</option>
            </select>

          </div>

          {/* JD输入 */}

          <textarea
            rows="8"
            placeholder="请输入岗位JD..."
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            style={{
              width: "100%",
              padding: "18px",
              borderRadius: "14px",
              border: "1px solid #d1d5db",
              fontSize: "16px",
              outline: "none",
              resize: "vertical",
              lineHeight: "1.8"
            }}
          />

          {/* 按钮 */}

          <button
            onClick={generateQuestions}
            style={{
              marginTop: "20px",
              padding: "14px 28px",
              background: "#111827",
              color: "#fff",
              border: "none",
              borderRadius: "12px",
              fontSize: "16px",
              fontWeight: "bold",
              cursor: "pointer"
            }}
          >
            {loading ? "AI生成中..." : "生成面试题"}
          </button>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "20px",
              marginTop: "40px"
            }}
          >

            <div
              style={{
                background: "#ffffff",
                padding: "24px",
                borderRadius: "16px",
                border: "1px solid #e5e7eb"
              }}
            >
              <div
                style={{
                  fontSize: "36px",
                  marginBottom: "12px"
                }}
              >
                🤖
              </div>

              <div
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  marginBottom: "10px"
                }}
              >
                AI生成题目
              </div>

              <div
                style={{
                  color: "#6b7280",
                  lineHeight: 1.7
                }}
              >
                基于岗位JD智能生成真实面试问题
              </div>
            </div>

            <div
              style={{
                background: "#ffffff",
                padding: "24px",
                borderRadius: "16px",
                border: "1px solid #e5e7eb"
              }}
            >
              <div
                style={{
                  fontSize: "36px",
                  marginBottom: "12px"
                }}
              >
                📊
              </div>

              <div
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  marginBottom: "10px"
                }}
              >
                AI智能评分
              </div>

              <div
                style={{
                  color: "#6b7280",
                  lineHeight: 1.7
                }}
              >
                多维度分析回答质量与技术水平
              </div>
            </div>

            <div
              style={{
                background: "#ffffff",
                padding: "24px",
                borderRadius: "16px",
                border: "1px solid #e5e7eb"
              }}
            >
              <div
                style={{
                  fontSize: "36px",
                  marginBottom: "12px"
                }}
              >
                📝
              </div>

              <div
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  marginBottom: "10px"
                }}
              >
                历史记录
              </div>

              <div
                style={{
                  color: "#6b7280",
                  lineHeight: 1.7
                }}
              >
                自动保存所有面试过程与评分结果
              </div>
            </div>

            <div
              style={{
                background: "#ffffff",
                padding: "24px",
                borderRadius: "16px",
                border: "1px solid #e5e7eb"
              }}
            >
              <div
                style={{
                  fontSize: "36px",
                  marginBottom: "12px"
                }}
              >
                🔒
              </div>

              <div
                style={{
                  fontSize: "18px",
                  fontWeight: "bold",
                  marginBottom: "10px"
                }}
              >
                多用户系统
              </div>

              <div
                style={{
                  color: "#6b7280",
                  lineHeight: 1.7
                }}
              >
                JWT鉴权与用户数据完全隔离
              </div>
            </div>

          </div>

        </div>

        {/* 当前题目 */}

        {
          Array.isArray(questions) && questions[currentIndex] && (

            <div
              style={{
                background: "#fff",
                borderRadius: "20px",
                padding: "30px",
                boxShadow: "0 4px 20px rgba(0,0,0,0.05)"
              }}
            >

              <h2
                style={{
                  marginBottom: "20px",
                  color: "#111827"
                }}
              >
                第 {currentIndex + 1} 题
              </h2>

              <p
                style={{
                  fontSize: "22px",
                  fontWeight: "bold",
                  marginBottom: "30px",
                  lineHeight: "1.8"
                }}
              >
                {questions[currentIndex].question}
              </p>

              {/* 回答输入 */}

              <textarea
                rows="6"
                placeholder="请输入你的回答..."
                value={answers[currentIndex] || ""}
                onChange={(e) => {

                  const newAnswers = {
                    ...answers,
                    [currentIndex]: e.target.value
                  }

                  setAnswers(newAnswers)

                  localStorage.setItem(
                    `answers_${userId}`,
                    JSON.stringify(newAnswers)
                  )

                }}
                style={{
                  width: "100%",
                  padding: "18px",
                  borderRadius: "12px",
                  border: "1px solid #d1d5db",
                  fontSize: "16px",
                  lineHeight: "1.8",
                  marginBottom: "20px"
                }}
              />

              {/* 提交按钮 */}

              <button
                onClick={() =>
                  evaluateAnswer(
                    questions[currentIndex].question,
                    currentIndex
                  )
                }
                style={{
                  padding: "12px 24px",
                  background: "#2563eb",
                  color: "#fff",
                  border: "none",
                  borderRadius: "10px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: "pointer"
                }}
              >
                {
                  gradingIndex === currentIndex
                    ? "AI评分中..."
                    : "提交回答"
                }
              </button>

              {/* AI评分 */}

              {feedbacks[currentIndex] && (

                <div
                  style={{
                    background: "#fff",
                    padding: "30px",
                    borderRadius: "20px",
                    marginTop: "30px",
                    boxShadow: "0 4px 20px rgba(0,0,0,0.05)"
                  }}
                >

                  <h2>AI评分结果</h2>

                  <p>
                    技术能力：
                    {feedbacks[currentIndex]?.technical_score}
                  </p>

                  <p>
                    逻辑表达：
                    {feedbacks[currentIndex]?.logic_score}
                  </p>

                  <p>
                    工程经验：
                    {feedbacks[currentIndex]?.experience_score}
                  </p>

                  <p>
                    沟通表达：
                    {feedbacks[currentIndex]?.communication_score}
                  </p>

                  <p
                    style={{
                      color:
                        feedbacks[currentIndex]?.overall_score >= 80
                          ? "green"
                          : feedbacks[currentIndex]?.overall_score >= 60
                            ? "orange"
                            : "red",
                      fontWeight: "bold",
                      fontSize: "24px"
                    }}
                  >
                    综合评分：
                    {feedbacks[currentIndex]?.overall_score}
                  </p>

                  <p>
                    AI评价：
                    {feedbacks[currentIndex]?.feedback}
                  </p>

                </div>

              )}

              {/* 上一题 下一题 */}

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: "30px"
                }}
              >

                <button
                  onClick={() => {

                    if (currentIndex > 0) {
                      const prevIndex = currentIndex - 1

                      setCurrentIndex(prevIndex)

                      localStorage.setItem(
                        `currentIndex_${userId}`,
                        String(prevIndex)
                      )
                    }

                  }}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "10px",
                    border: "1px solid #ddd",
                    background: "#fff",
                    cursor: "pointer"
                  }}
                >
                  上一题
                </button>

                <button
                  onClick={() => {

                    if (currentIndex < questions.length - 1) {
                      const nextIndex = currentIndex + 1

                      setCurrentIndex(nextIndex)

                      localStorage.setItem(
                        `currentIndex_${userId}`,
                        String(nextIndex)
                      )
                    }

                  }}
                  style={{
                    padding: "10px 20px",
                    borderRadius: "10px",
                    border: "none",
                    background: "#111827",
                    color: "#fff",
                    cursor: "pointer"
                  }}
                >
                  下一题
                </button>

              </div>

              {/* 面试结束 */}

              {
                currentIndex === questions.length - 1 &&
                feedbacks[currentIndex] && (

                  <div
                    style={{
                      marginTop: "40px",
                      textAlign: "center"
                    }}
                  >

                    <h2>
                      面试完成 🎉
                    </h2>

                  </div>

                )
              }

            </div>

          )
        }

      </div>
    </>
  );
}

export default App;