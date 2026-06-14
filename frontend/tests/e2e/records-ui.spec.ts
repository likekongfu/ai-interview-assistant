import { expect, test } from "@playwright/test";

const API_BASE = "http://127.0.0.1:8000";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("token", "test-token");
    localStorage.setItem("username", "zhangsan");
    localStorage.setItem("user_id", "1");
  });
});

test("面试记录列表可以跳转到对应报告页", async ({ page }) => {
  await page.route(`${API_BASE}/interviews`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          id: 101,
          resume_name: "jianli.docx",
          status: "finished",
          overall_score: 82,
          summary: "整体表现稳定，Redis 和 FastAPI 仍可继续加强。",
          topic_count: 5,
          created_at: "2026-06-12T09:00:00",
          finished_at: "2026-06-12T09:30:00",
          report_generated: true,
        },
      ]),
    });
  });

  await page.route(`${API_BASE}/interviews/101/report`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        interview_id: 101,
        overall_score: 82,
        summary: "整体表现稳定，能够结合项目描述技术方案。",
        strengths: ["能够结合项目背景回答"],
        weaknesses: ["高并发细节还可以更深入"],
        topic_scores: [
          {
            topic: "Redis",
            score: 80,
            comment: "基础掌握较好，缓存异常场景可继续加强。",
          },
        ],
        improvement_suggestions: ["复习缓存穿透、击穿、雪崩"],
        study_plan: ["第1天：复习 Redis 高频场景"],
      }),
    });
  });

  await page.goto("/interview-records");

  const firstCard = page.getByTestId("interview-record-card").first();
  await expect(firstCard).toBeVisible();

  await firstCard.click();
  await expect(page).toHaveURL(/\/interviews\/101\/report/);
  await expect(page.getByText("82")).toBeVisible();
});

test("刷题记录列表可以进入详情并删除记录", async ({ page }) => {
  let historyItems = [
    {
      id: 201,
      jd: "Java 后端开发，熟悉 Redis 和 JVM",
      feedback: "技术理解较好，但项目细节需要加强。",
      overall_score: 76,
      created_at: "2026-06-12T10:00:00",
    },
  ];

  await page.route(`${API_BASE}/history`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(historyItems),
    });
  });

  await page.route(`${API_BASE}/history/201`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify([
        {
          question: "请解释 Redis 缓存击穿。",
          answer: "热点 key 过期后大量请求打到数据库。",
          technical_score: 76,
          logic_score: 74,
          experience_score: 70,
          communication_score: 78,
          overall_score: 76,
          feedback: "能够说明核心现象，但解决方案还可以更完整。",
        },
      ]),
    });
  });

  await page.route(`${API_BASE}/history/single_delete/201`, async (route) => {
    historyItems = [];
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ message: "deleted" }),
    });
  });

  await page.goto("/history");

  const firstCard = page.getByTestId("practice-history-card").first();
  await expect(firstCard).toBeVisible();

  await firstCard.click();
  await expect(page).toHaveURL(/\/history\/201/);
  await expect(page.getByText("Redis")).toBeVisible();

  await page.goto("/history");
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByTestId("practice-history-delete-button").first().click();
  await expect(page.getByTestId("practice-history-card")).toHaveCount(0);
});
