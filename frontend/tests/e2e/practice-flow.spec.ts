import { expect, test } from "@playwright/test";

const API_BASE = "http://127.0.0.1:8000";

function login(page: import("@playwright/test").Page) {
  return page.addInitScript(() => {
    localStorage.setItem("token", "test-token");
    localStorage.setItem("username", "zhangsan");
    localStorage.setItem("user_id", "1");
  });
}

test("刷题完整链路：获取题目、提交评分、查看记录、进入详情并删除", async ({
  page,
}) => {
  await login(page);

  const historyItems = [
    {
      id: 3001,
      jd: "中级：题库 Java 后端；题型 简答题；技术方向 Redis",
      feedback: "能够说明缓存击穿现象，并给出互斥锁方案。",
      overall_score: 86,
      created_at: "2026-06-12T10:00:00",
    },
  ];
  let shouldShowHistory = false;

  await page.route(`${API_BASE}/generate_questions`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        interview_id: 3001,
        questions: ["请解释 Redis 缓存击穿，并说明常见解决方案。"],
      }),
    });
  });

  await page.route(`${API_BASE}/evaluate_answer`, async (route) => {
    shouldShowHistory = true;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        result: {
          technical_score: 86,
          logic_score: 84,
          experience_score: 82,
          communication_score: 88,
          overall_score: 86,
          feedback: "解析：回答覆盖热点 key、数据库压力和互斥锁方案。",
        },
      }),
    });
  });

  await page.route(`${API_BASE}/history`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(shouldShowHistory ? historyItems : []),
    });
  });

  await page.route(`${API_BASE}/history/3001`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          question: "请解释 Redis 缓存击穿，并说明常见解决方案。",
          answer: "热点 key 过期后大量请求打到数据库，可以用互斥锁和逻辑过期解决。",
          technical_score: 86,
          logic_score: 84,
          experience_score: 82,
          communication_score: 88,
          overall_score: 86,
          feedback: "解析：回答覆盖热点 key、数据库压力和互斥锁方案。",
        },
      ]),
    });
  });

  await page.route(`${API_BASE}/history/single_delete/3001`, async (route) => {
    shouldShowHistory = false;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ message: "删除成功" }),
    });
  });

  await page.goto("/practice");
  await page.getByTestId("practice-level-select").selectOption("中级");
  await page
    .getByTestId("practice-jd-input")
    .fill("题库 Java 后端；题型 简答题；技术方向 Redis");
  await page.getByTestId("practice-generate-button").click();

  await expect(page.getByTestId("practice-question-item")).toHaveCount(1);
  await page.getByTestId("practice-question-item").first().click();
  await page
    .getByTestId("practice-answer-input")
    .fill("热点 key 过期后大量请求打到数据库，可以用互斥锁和逻辑过期解决。");
  await page.getByTestId("practice-submit-button").click();

  await expect(page.getByTestId("practice-feedback")).toContainText("86");
  await expect(page.getByTestId("practice-feedback")).toContainText("解析");

  await page.goto("/history");
  const card = page.getByTestId("practice-history-card").first();
  await expect(card).toBeVisible();
  await expect(card).toContainText("Redis");

  await card.click();
  await expect(page).toHaveURL(/\/history\/3001/);
  await expect(page.getByText("Redis")).toBeVisible();

  await page.goto("/history");
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByTestId("practice-history-delete-button").first().click();
  await expect(page.getByTestId("practice-history-card")).toHaveCount(0);
});

test("未登录访问刷题页会跳转登录页", async ({ page }) => {
  await page.goto("/practice");

  await expect(page).toHaveURL(/\/login/);
});

test("刷题异常场景：空答案、AI评分失败、网络失败、删除不存在记录", async ({
  page,
}) => {
  await login(page);

  await page.route(`${API_BASE}/generate_questions`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        interview_id: 3002,
        questions: ["请解释 JVM 内存模型。"],
      }),
    });
  });

  await page.goto("/practice");
  await page.getByTestId("practice-jd-input").fill("题库 Java；题型 简答；技术方向 JVM");
  await page.getByTestId("practice-generate-button").click();
  await expect(page.getByTestId("practice-question-item")).toHaveCount(1);

  await page.getByTestId("practice-submit-button").click();
  await expect(page.getByText("请先输入答案")).toBeVisible();

  await page.route(`${API_BASE}/evaluate_answer`, async (route) => {
    await route.fulfill({
      status: 502,
      contentType: "application/json",
      body: JSON.stringify({ detail: "AI评分失败，请稍后重试" }),
    });
  });
  await page.getByTestId("practice-answer-input").fill("这是一次有效回答。");
  await page.getByTestId("practice-submit-button").click();
  await expect(page.getByText("AI评分失败，请稍后重试")).toBeVisible();

  await page.unroute(`${API_BASE}/generate_questions`);
  await page.route(`${API_BASE}/generate_questions`, async (route) => {
    await route.abort("failed");
  });
  await page.evaluate(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;
    localStorage.removeItem(`interviewId_${userId}`);
    localStorage.removeItem(`questions_${userId}`);
    localStorage.removeItem(`answers_${userId}`);
    localStorage.removeItem(`feedbacks_${userId}`);
    localStorage.removeItem(`currentIndex_${userId}`);
  });
  await page.goto("/practice");
  await page.getByTestId("practice-jd-input").fill("题库 Redis；题型 简答；技术方向 缓存");
  await page.getByTestId("practice-generate-button").click();
  await expect(page.getByText(/生成题目失败|Failed to fetch|fetch/)).toBeVisible();

  await page.route(`${API_BASE}/history`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 404,
          jd: "不存在的记录",
          feedback: "待删除",
          overall_score: 0,
          created_at: "2026-06-12T10:00:00",
        },
      ]),
    });
  });
  await page.route(`${API_BASE}/history/single_delete/404`, async (route) => {
    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "刷题记录不存在" }),
    });
  });

  await page.goto("/history");
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByTestId("practice-history-delete-button").first().click();
  await expect(page.getByText("删除失败")).toBeVisible();
});
