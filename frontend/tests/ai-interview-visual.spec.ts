import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import fs from "node:fs";

type LoginResponse = {
  token: string;
  username: string;
  user_id: number;
};

type FollowUpResponse = {
  next_question?: string | null;
  topic?: string | null;
  follow_up_count?: number | null;
  finished?: boolean;
  message?: string | null;
  action?: "follow_up" | "switch_topic" | string | null;
  score?: number | null;
  reason?: string | null;
};

const API_BASE_URL = process.env.E2E_API_BASE_URL || "http://127.0.0.1:8000";
const E2E_USERNAME = process.env.E2E_USERNAME || "zhangsan";
const E2E_PASSWORD = process.env.E2E_PASSWORD || "123456";

test.use({
  headless: false,
  launchOptions: {
    slowMo: 800,
  },
});

test("可视化完成一次 AI 模拟面试并观察 Topic 切换", async ({
  page,
  request,
}, testInfo) => {
  test.setTimeout(12 * 60 * 1000);

  await step("登录后端，准备真实 token");
  const session = await loginForSession(request);

  await step("预置前端登录态，清理旧的面试缓存");
  await page.addInitScript((auth: LoginResponse) => {
    localStorage.setItem("token", auth.token);
    localStorage.setItem("username", auth.username);
    localStorage.setItem("user_id", String(auth.user_id));
    localStorage.removeItem("ai_resume_id");
    localStorage.removeItem("ai_resume_name");
    localStorage.removeItem("ai_interview_id");
    localStorage.removeItem("ai_interview_messages");
  }, session);

  await step("打开首页");
  await page.goto("/");
  await expect(page.getByText("AI 模拟面试").first()).toBeVisible();

  await step("从首页进入 AI 模拟面试页面");
  await page.getByTestId("home-ai-interview-button").click();
  await expect(page).toHaveURL(/\/interview/);

  await step("上传测试简历");
  const resumePath = testInfo.outputPath("visual-test-resume.txt");
  fs.writeFileSync(
    resumePath,
    [
      "姓名：张三",
      "目标岗位：AI 应用开发工程师",
      "项目：AI 面试助手",
      "技术栈：Next.js、FastAPI、MySQL、Redis、RAG、LLM Prompt、Topic 动态追问。",
      "经验：负责简历上传、AI 首题生成、追问评分、Topic 切换和面试报告生成。",
    ].join("\n"),
    "utf8"
  );
  await page.getByTestId("resume-file-input").setInputFiles(resumePath);
  await expect(page.getByTestId("start-interview-button")).toBeEnabled({
    timeout: 60_000,
  });

  await step("点击开始面试，等待第一道 AI 问题");
  await page.getByTestId("start-interview-button").click();
  await waitForAiMessageCount(page, 1);

  await step("场景 1：回答“不会”，应强制切换 Topic");
  const cannotAnswer = await submitAnswerAndWait(page, "不会");
  console.log("场景 1 返回：", cannotAnswer);
  expect(cannotAnswer.action).toBe("switch_topic");
  expect(cannotAnswer.score ?? 100).toBeLessThanOrEqual(55);

  await step("场景 2：包含“不会”但有技术方案，不能误判为 cannot_answer");
  const detailedNegative = await submitAnswerAndWait(
    page,
    "不会一直查库，会先查 Redis 缓存；如果缓存为空，再访问数据库，并设置较短过期时间，避免重复请求直接打到数据库。"
  );
  console.log("场景 2 返回：", detailedNegative);
  expect(detailedNegative.reason || "").not.toContain("明确表示不会");
  expect(detailedNegative.score ?? 0).toBeGreaterThan(20);

  await step("场景 3：回答较好时，观察是否提前切换 Topic");
  const strongAnswer = await submitAnswerAndWait(
    page,
    "在实际项目里我会先按链路拆解问题：入口层做参数校验和幂等控制，服务层封装业务规则，缓存层使用 Redis 承接热点数据，数据库层通过索引和分页降低查询压力。对于高并发场景，会结合互斥锁、逻辑过期和异步刷新避免缓存击穿，同时用日志和监控定位慢请求。"
  );
  console.log("场景 3 返回：", strongAnswer);
  expect(strongAnswer.action === "follow_up" || strongAnswer.action === "switch_topic").toBeTruthy();
  expect(strongAnswer.score ?? 0).toBeGreaterThanOrEqual(60);
  expect(strongAnswer.follow_up_count ?? 0).toBeLessThanOrEqual(3);
  expect(strongAnswer.reason || "").not.toContain("明确表示不会");

  await step("场景 4：回答一般时，最多追问 3 次后应切换 Topic");
  const maxFollowUpResponses: FollowUpResponse[] = [];
  for (let index = 1; index <= 4; index += 1) {
    const response = await submitAnswerAndWait(
      page,
      `这个问题我理解是需要结合项目场景处理，我会先分析原因，再根据接口、缓存和数据库情况逐步优化。第 ${index} 次补充。`
    );
    maxFollowUpResponses.push(response);
    console.log(`场景 4 第 ${index} 轮返回：`, response);

    expect(response.follow_up_count ?? 0).toBeLessThanOrEqual(3);

    if (response.action === "switch_topic" || response.finished) {
      break;
    }
  }
  expect(
    maxFollowUpResponses.some(
      (response) =>
        response.action === "switch_topic" ||
        (response.follow_up_count ?? 99) === 0 ||
        response.finished
    )
  ).toBeTruthy();

  await step("场景 5：继续用固定回答推进，直到所有 Topic 结束");
  let finalResponse = maxFollowUpResponses[maxFollowUpResponses.length - 1];
  for (let index = 1; index <= 20 && !finalResponse?.finished; index += 1) {
    finalResponse = await submitAnswerAndWait(
      page,
      index % 2 === 0
        ? "不知道"
        : "我会结合项目里的接口调用、缓存策略、数据库索引和日志监控来分析，并说明这样设计的取舍。"
    );
    console.log(`收尾推进第 ${index} 轮返回：`, finalResponse);
  }

  expect(finalResponse?.finished).toBeTruthy();
  await expect(page.getByTestId("interview-status")).toContainText(/已结束|结束/);

  await step("保持浏览器打开 15 秒，方便观察最终结果");
  await page.waitForTimeout(15_000);
});

async function loginForSession(request: APIRequestContext) {
  const response = await request.post(`${API_BASE_URL}/login`, {
    data: {
      username: E2E_USERNAME,
      password: E2E_PASSWORD,
    },
  });

  if (!response.ok()) {
    throw new Error(
      `E2E 登录失败：${response.status()}。请确认后端已启动，并设置 E2E_USERNAME/E2E_PASSWORD。`
    );
  }

  return (await response.json()) as LoginResponse;
}

async function submitAnswerAndWait(page: Page, answer: string) {
  const aiMessageCount = await page.getByTestId("ai-message").count();

  await page.getByTestId("answer-input").fill(answer);

  const [response] = await Promise.all([
    page.waitForResponse(
      (item) =>
        item.url().includes("/follow_up") && item.request().method() === "POST",
      { timeout: 180_000 }
    ),
    page.getByTestId("submit-answer-button").click(),
  ]);

  const data = (await response.json()) as FollowUpResponse;
  await waitForAiMessageCount(page, aiMessageCount + 1);
  await page.waitForTimeout(1_000);

  return data;
}

async function waitForAiMessageCount(page: Page, count: number) {
  await expect(page.getByTestId("ai-message")).toHaveCount(count, {
    timeout: 180_000,
  });
  await expect(page.getByTestId("ai-message").last()).not.toBeEmpty({
    timeout: 30_000,
  });
}

async function step(message: string) {
  console.log(`\n[E2E] ${message}`);
}
