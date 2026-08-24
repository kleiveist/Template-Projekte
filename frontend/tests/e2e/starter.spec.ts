import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function openStarter(page: Page): Promise<void> {
  await page.goto("/", { waitUntil: "networkidle" });
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

test("renders the generated profile and exercises its backend boundary", async ({ page }) => {
  await openStarter(page);

  const title = page.getByRole("heading", { level: 1 });
  await expect(page).toHaveTitle((await title.textContent()) ?? "");
  await expect(page.getByRole("heading", { name: "Profile summary" })).toBeVisible();

  const retry = page.getByRole("button", { name: "Check again" });
  if ((await retry.count()) === 1) {
    const backendStatus = page.locator("#backend-status");
    const healthyBackend = /^[a-z0-9-]+-backend: ok$/;
    await expect(backendStatus).toHaveText(healthyBackend);
    await retry.click();
    await expect(backendStatus).toHaveText(healthyBackend);
  } else {
    await expect(page.getByRole("heading", { name: "Backend disabled" })).toBeVisible();
  }
});

test("has no automatically detectable accessibility violations", async ({ page }) => {
  await openStarter(page);

  const results = await new AxeBuilder({ page }).analyze();

  expect(results.violations).toEqual([]);
});
