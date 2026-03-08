import { expect, test } from "@playwright/test";

test("chat page smoke", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=Desktop Prototype")).toBeVisible();
  await page.fill("textarea", "Smoke test message");
  await page.click("button:has-text('Send')");
  await expect(page.locator("text=Smoke test message")).toBeVisible();
});
