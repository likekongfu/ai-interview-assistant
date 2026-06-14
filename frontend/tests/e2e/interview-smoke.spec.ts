import { expect, test } from "@playwright/test";

test("首页可以进入 AI 模拟面试基础页面", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText("AI 模拟面试").first()).toBeVisible();

  await page.goto("/interview");

  await expect(page.getByText("上传简历", { exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "开始面试" })).toBeVisible();
});
