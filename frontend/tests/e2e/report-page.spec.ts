import { expect, test } from "@playwright/test";

test("前端可以展示面试报告", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("token", "test-token");
    localStorage.setItem("username", "zhangsan");
    localStorage.setItem("user_id", "1");
  });

  await page.route("**/interviews/123/report", async (route) => {
    if (route.request().resourceType() === "document") {
      await route.continue();
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        interview_id: 123,
        overall_score: 78,
        summary: "整体表现稳定，但 Redis 高并发细节仍需加强。",
        strengths: ["能够说明项目背景", "对 FastAPI 有一定理解"],
        weaknesses: ["Redis 缓存击穿解释不够完整", "回答缺少量化项目经验"],
        topic_scores: [
          {
            topic: "FastAPI",
            score: 82,
            comment: "掌握较好，但异步机制可以继续加强",
          },
          {
            topic: "Redis",
            score: 65,
            comment: "基础概念了解，但高并发场景回答不足",
          },
        ],
        improvement_suggestions: [
          "复习 Redis 缓存穿透、击穿、雪崩",
          "准备 2 个项目难点案例",
        ],
        study_plan: [
          "第1天：复习 FastAPI 依赖注入和中间件",
          "第2天：复习 Redis 高频问题",
          "第3天：练习项目介绍话术",
        ],
      }),
    });
  });

  await page.goto("/interviews/123/report");

  await expect(page.getByRole("heading", { name: "面试报告" })).toBeVisible();
  await expect(page.getByText("78")).toBeVisible();
  await expect(page.getByText("整体表现稳定，但 Redis 高并发细节仍需加强。")).toBeVisible();
  await expect(page.getByText("FastAPI", { exact: true })).toBeVisible();
  await expect(page.getByText("Redis 缓存击穿解释不够完整")).toBeVisible();
  await expect(page.getByText("第3天：练习项目介绍话术")).toBeVisible();
});
