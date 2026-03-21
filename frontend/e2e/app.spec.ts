import { test, expect, type Page } from "@playwright/test";

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Wait for the dashboard to finish loading (skeleton cards disappear, real cards appear). */
async function waitForDashboardLoaded(page: Page) {
  // Wait for at least one zone card link to appear (they link to /zone/<id>)
  await page.locator("a.card-body-link").first().waitFor({ timeout: 15_000 });
}

/** Collect any browser console errors during a callback. */
async function collectConsoleErrors(page: Page, fn: () => Promise<void>): Promise<string[]> {
  const errors: string[] = [];
  const handler = (msg: import("@playwright/test").ConsoleMessage) => {
    if (msg.type() === "error") errors.push(msg.text());
  };
  page.on("console", handler);
  await fn();
  page.off("console", handler);
  return errors;
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard Page
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Dashboard Page", () => {
  test.beforeEach(async ({ page }) => {
    // Clear pinned zones so tests start clean
    await page.goto("/");
    await page.evaluate(() => {
      localStorage.removeItem("pinned_zones");
      localStorage.removeItem("zone_order");
    });
    await page.reload();
    await waitForDashboardLoaded(page);
  });

  test("page loads and renders forecast zone cards", async ({ page }) => {
    // Should see the dashboard heading
    await expect(page.locator("h2")).toContainText("Marine Forecast Dashboard");

    // Should render multiple zone cards (API returns 14 zones)
    const cards = page.locator("a.card-body-link");
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(10); // at least most zones rendered
  });

  test("cards display zone names and forecast text", async ({ page }) => {
    // Check that zone names are visible in card titles
    const titles = page.locator(".card-title");
    const count = await titles.count();
    expect(count).toBeGreaterThan(0);

    // Check first card has non-empty title text
    const firstTitle = await titles.first().textContent();
    expect(firstTitle?.trim().length).toBeGreaterThan(0);

    // Check forecast preview text is rendered
    const previews = page.locator(".forecast-preview");
    const previewCount = await previews.count();
    expect(previewCount).toBeGreaterThan(0);

    const firstPreview = await previews.first().textContent();
    expect(firstPreview?.trim().length).toBeGreaterThan(0);
  });

  test("advisory badges appear on cards that have advisories", async ({ page }) => {
    // There should be at least one active advisory badge (PZZ131, PZZ132, PZZ134 have advisories)
    const activeBadges = page.locator('.badge-danger:has-text("Active Advisory")');
    await expect(activeBadges.first()).toBeVisible();

    // There should also be clear badges on some cards
    const clearBadges = page.locator('.badge-ok:has-text("Clear")');
    await expect(clearBadges.first()).toBeVisible();
  });

  test("status bar shows zone count and last update time", async ({ page }) => {
    const statusBar = page.locator(".status-bar");
    await expect(statusBar).toBeVisible();

    // Should show zone count (e.g. "14 zones")
    await expect(statusBar).toContainText("zone");

    // Should show last updated time indicator
    await expect(statusBar).toContainText("🕐");
  });

  test("pin button is visible on cards", async ({ page }) => {
    // Pin buttons should exist on every card
    const pinButtons = page.locator("button.pin-btn");
    const count = await pinButtons.count();
    expect(count).toBeGreaterThan(0);

    // First pin button should have appropriate aria-label
    const firstPin = pinButtons.first();
    await expect(firstPin).toHaveAttribute("aria-pressed", "false");
    await expect(firstPin).toHaveAttribute("aria-label", /Pin zone/i);
  });

  test("drag handle is visible on cards", async ({ page }) => {
    const dragHandles = page.locator(".drag-handle");
    const count = await dragHandles.count();
    expect(count).toBeGreaterThan(0);

    // Drag handle should have sortable role description
    await expect(dragHandles.first()).toHaveAttribute("aria-roledescription", "sortable");
  });

  test("cards are grouped by region with section headers", async ({ page }) => {
    // Look for region section labels
    const salishSea = page.locator('.section-label:has-text("Salish Sea")');
    const coastal = page.locator('.section-label:has-text("Coastal")');

    await expect(salishSea).toBeVisible();
    await expect(coastal).toBeVisible();
  });

  test("refresh button works and triggers reload", async ({ page }) => {
    const refreshBtn = page.locator('button:has-text("Refresh")');
    await expect(refreshBtn).toBeVisible();

    // Click refresh
    await refreshBtn.click();

    // Button should briefly show "Refreshing…" state (disabled)
    // Then return to enabled state
    await expect(refreshBtn).toBeEnabled({ timeout: 15_000 });

    // Cards should still be visible after refresh
    await waitForDashboardLoaded(page);
  });

  test("pin button toggles pinned state", async ({ page }) => {
    const firstPinBtn = page.locator("button.pin-btn").first();

    // Initially unpinned
    await expect(firstPinBtn).toHaveAttribute("aria-pressed", "false");

    // Click to pin
    await firstPinBtn.click();

    // Should now show pinned section
    const pinnedLabel = page.locator('.section-label:has-text("Pinned")');
    await expect(pinnedLabel).toBeVisible();
  });

  test("no console errors on dashboard load", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await page.goto("/");
    await waitForDashboardLoaded(page);

    // Filter out known non-issues (e.g., favicon 404)
    const realErrors = errors.filter(
      (e) => !e.includes("favicon") && !e.includes("vite.svg"),
    );
    expect(realErrors).toEqual([]);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Zone Detail Page
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Zone Detail Page", () => {
  test("navigates to zone detail when clicking a card", async ({ page }) => {
    await page.goto("/");
    await waitForDashboardLoaded(page);

    // Click the first zone card link
    const firstCardLink = page.locator("a.card-body-link").first();
    const href = await firstCardLink.getAttribute("href");
    expect(href).toMatch(/^\/zone\/PZZ\d+$/);

    await firstCardLink.click();

    // Should navigate to the zone detail page
    await expect(page).toHaveURL(/\/zone\/PZZ\d+$/);
  });

  test("shows zone name, forecast text, and timestamps", async ({ page }) => {
    // Navigate directly to a known zone
    await page.goto("/zone/PZZ135");

    // Wait for forecast to load
    await page.locator(".forecast-text-full").waitFor({ timeout: 10_000 });

    // Zone name should be visible
    const heading = page.locator("h2");
    await expect(heading).toContainText("Puget Sound");

    // Zone ID should be shown
    await expect(page.locator(".page-header p")).toContainText("PZZ135");

    // Full forecast text should be present
    const forecastText = page.locator(".forecast-text-full");
    await expect(forecastText).toBeVisible();
    const text = await forecastText.textContent();
    expect(text!.length).toBeGreaterThan(50);

    // Timestamps should be shown in the status bar
    const statusBar = page.locator(".status-bar");
    await expect(statusBar).toContainText("Issued:");
    await expect(statusBar).toContainText("Expires:");
    await expect(statusBar).toContainText("Fetched:");
  });

  test("shows advisory card when zone has advisory", async ({ page }) => {
    // PZZ131 has an active advisory
    await page.goto("/zone/PZZ131");
    await page.locator(".forecast-text-full").waitFor({ timeout: 10_000 });

    // Advisory card should be visible
    const advisoryCard = page.locator(".card-advisory");
    await expect(advisoryCard).toBeVisible();

    // Advisory badge should show "Active Advisory"
    await expect(page.locator('.badge-danger:has-text("Active Advisory")')).toBeVisible();

    // Advisory body text should be present
    const advisoryBody = page.locator(".advisory-body");
    await expect(advisoryBody).toContainText("SMALL CRAFT ADVISORY");
  });

  test("back link navigates to dashboard", async ({ page }) => {
    await page.goto("/zone/PZZ135");
    await page.locator(".forecast-text-full").waitFor({ timeout: 10_000 });

    // Click back link
    const backLink = page.locator('a.detail-back:has-text("Back to Dashboard")');
    await expect(backLink).toBeVisible();
    await backLink.click();

    // Should be back on dashboard
    await expect(page).toHaveURL("/");
    await waitForDashboardLoaded(page);
  });

  test("shows error for invalid zone", async ({ page }) => {
    await page.goto("/zone/INVALID999");

    // Should show an error message
    const errorMsg = page.locator(".error-msg");
    await expect(errorMsg).toBeVisible({ timeout: 10_000 });
    await expect(errorMsg).toContainText("Error");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Settings Page
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Settings Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/settings");
    // Wait for settings to load (cache status section appears)
    await page.locator('text="Cache Status"').waitFor({ timeout: 10_000 });
  });

  test("page loads and shows Cache Status section", async ({ page }) => {
    await expect(page.locator("h2")).toContainText("Server Settings");
    await expect(page.locator('text="Cache Status"')).toBeVisible();

    // Should show health status badge
    const healthBadge = page.locator(".badge").first();
    await expect(healthBadge).toBeVisible();
  });

  test("shows Configuration section with editable fields", async ({ page }) => {
    await expect(page.locator('text="Configuration"')).toBeVisible();

    // Cache interval dropdown
    const cacheSelect = page.locator("select.input").first();
    await expect(cacheSelect).toBeVisible();

    // Log Level dropdown
    const logLevelLabel = page.locator('text="Log Level"');
    await expect(logLevelLabel).toBeVisible();
  });

  test("Cache Interval dropdown is functional", async ({ page }) => {
    const cacheSelect = page.locator("select.input").first();
    await expect(cacheSelect).toBeVisible();

    // Should have options (30, 60, 90, etc.)
    const options = cacheSelect.locator("option");
    const count = await options.count();
    expect(count).toBeGreaterThanOrEqual(4);

    // Change value
    await cacheSelect.selectOption("120");
    await expect(cacheSelect).toHaveValue("120");
  });

  test("MCP Server toggle is present", async ({ page }) => {
    // MCP Server has a segmented radio control
    const mcpLabel = page.locator('text="MCP Server"');
    await expect(mcpLabel).toBeVisible();

    // Should have a radiogroup with Enabled/Disabled labels
    const radioGroup = page.locator('.segmented-control[role="radiogroup"]');
    await expect(radioGroup).toBeVisible();

    // Should have two radio inputs (name="mcp_enabled")
    const radios = page.locator('input[type="radio"][name="mcp_enabled"]');
    expect(await radios.count()).toBe(2);

    // Labels should say "Enabled" and "Disabled"
    await expect(radioGroup.locator("text=Enabled")).toBeVisible();
    await expect(radioGroup.locator("text=Disabled")).toBeVisible();
  });

  test("Log Level dropdown is present and has correct options", async ({ page }) => {
    // Find all select elements; the second one should be Log Level
    const selects = page.locator("select.input");
    const selectCount = await selects.count();
    expect(selectCount).toBeGreaterThanOrEqual(2);

    // The log level select should contain standard options
    const logSelect = selects.nth(1);
    const optionTexts = await logSelect.locator("option").allTextContents();
    expect(optionTexts).toContain("DEBUG");
    expect(optionTexts).toContain("INFO");
    expect(optionTexts).toContain("WARNING");
    expect(optionTexts).toContain("ERROR");
    expect(optionTexts).toContain("CRITICAL");
  });

  test("NOAA Base URL input is present", async ({ page }) => {
    const urlInput = page.locator('input[type="text"]').first();
    await expect(urlInput).toBeVisible();
    // Should contain a URL value
    const val = await urlInput.inputValue();
    expect(val).toMatch(/^https?:\/\//);
  });

  test("CORS Origins input is present", async ({ page }) => {
    // Should be the second text input
    const textInputs = page.locator('input[type="text"]');
    const count = await textInputs.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });

  test("tooltips/descriptions appear below settings fields", async ({ page }) => {
    // Settings fields have description text rendered via .setting-description
    const descriptions = page.locator(".setting-description");
    const count = await descriptions.count();
    expect(count).toBeGreaterThan(0);

    // First description should have meaningful text
    const firstDesc = await descriptions.first().textContent();
    expect(firstDesc?.trim().length).toBeGreaterThan(0);
  });

  test("reset icon appears when a value changes from default", async ({ page }) => {
    // Initially no reset buttons visible
    const resetBtns = page.locator("button.reset-btn");
    const initialCount = await resetBtns.count();

    // Change cache interval to trigger reset button
    const cacheSelect = page.locator("select.input").first();
    const originalValue = await cacheSelect.inputValue();

    // Pick a different value
    const newValue = originalValue === "60" ? "120" : "60";
    await cacheSelect.selectOption(newValue);

    // Wait a moment for the UI to react
    await page.waitForTimeout(500);

    // A reset button should now be visible
    const updatedResetBtns = page.locator("button.reset-btn:visible");
    const newCount = await updatedResetBtns.count();
    expect(newCount).toBeGreaterThan(initialCount);
  });

  test("no console errors on settings page load", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await page.goto("/settings");
    await page.locator('text="Cache Status"').waitFor({ timeout: 10_000 });

    const realErrors = errors.filter(
      (e) => !e.includes("favicon") && !e.includes("vite.svg"),
    );
    expect(realErrors).toEqual([]);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Navigation
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Navigation", () => {
  test("nav bar is present with Marine Forecast title", async ({ page }) => {
    await page.goto("/");

    const nav = page.locator('nav[aria-label="Main navigation"]');
    await expect(nav).toBeVisible();

    const title = nav.locator("h1");
    await expect(title).toContainText("Marine Forecast");
  });

  test("dashboard and settings nav links work", async ({ page }) => {
    await page.goto("/");

    // Click Settings link
    await page.click('a:has-text("Settings")');
    await expect(page).toHaveURL("/settings");

    // Click Dashboard link
    await page.click('a:has-text("Dashboard")');
    await expect(page).toHaveURL("/");
  });

  test("active nav link is highlighted", async ({ page }) => {
    await page.goto("/");

    // Dashboard link should have 'active' class (NavLink behavior)
    const dashLink = page.locator('nav a:has-text("Dashboard")');
    await expect(dashLink).toHaveClass(/active/);

    // Settings link should NOT have 'active' class
    const settingsLink = page.locator('nav a:has-text("Settings")');
    await expect(settingsLink).not.toHaveClass(/active/);

    // Navigate to settings — now Settings should be active
    await settingsLink.click();
    await expect(page).toHaveURL("/settings");
    await expect(settingsLink).toHaveClass(/active/);
    await expect(dashLink).not.toHaveClass(/active/);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Accessibility
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Accessibility", () => {
  test("skip nav link is present and becomes visible on focus", async ({ page }) => {
    await page.goto("/");

    const skipLink = page.locator("a.skip-nav");
    await expect(skipLink).toHaveAttribute("href", "#main-content");

    // Skip link text
    await expect(skipLink).toContainText("Skip to content");

    // Press Tab to focus — skip link should be the first focusable element
    await page.keyboard.press("Tab");

    // The skip link should now be visible/focused
    const focused = page.locator(":focus");
    await expect(focused).toHaveClass(/skip-nav/);
  });

  test("main content area has correct id", async ({ page }) => {
    await page.goto("/");
    const main = page.locator("main#main-content");
    await expect(main).toBeVisible();
  });

  test("nav has aria-label", async ({ page }) => {
    await page.goto("/");
    const nav = page.locator("nav");
    await expect(nav).toHaveAttribute("aria-label", "Main navigation");
  });

  test("advisory badges have appropriate aria roles", async ({ page }) => {
    await page.goto("/");
    await waitForDashboardLoaded(page);

    // All advisory badges should have role="status"
    const badges = page.locator('.badge[role="status"]');
    const count = await badges.count();
    expect(count).toBeGreaterThan(0);

    // Active advisory badges should have aria-label
    const activeBadge = page.locator('.badge-danger[aria-label="Active weather advisory"]');
    if ((await activeBadge.count()) > 0) {
      await expect(activeBadge.first()).toBeVisible();
    }
  });

  test("pin buttons have aria-pressed and aria-label", async ({ page }) => {
    await page.goto("/");
    await waitForDashboardLoaded(page);

    const pinButtons = page.locator("button.pin-btn");
    const first = pinButtons.first();
    await expect(first).toHaveAttribute("aria-pressed");
    await expect(first).toHaveAttribute("aria-label");
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Responsive Design
// ─────────────────────────────────────────────────────────────────────────────

test.describe("Responsive — Mobile Viewport (375px)", () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test("dashboard cards stack vertically on mobile", async ({ page }) => {
    await page.goto("/");
    await waitForDashboardLoaded(page);

    // Get the zone-grid container
    const grid = page.locator(".zone-grid").first();
    await expect(grid).toBeVisible();

    // On mobile, grid should use single column — all cards full width
    const cards = grid.locator(".card");
    if ((await cards.count()) >= 2) {
      const first = await cards.first().boundingBox();
      const second = await cards.nth(1).boundingBox();
      expect(first).not.toBeNull();
      expect(second).not.toBeNull();

      // Cards should be stacked (second card's top > first card's bottom)
      expect(second!.y).toBeGreaterThan(first!.y);

      // Cards should be similar width (both spanning full container)
      expect(Math.abs(first!.width - second!.width)).toBeLessThan(20);
    }
  });

  test("navigation is usable on mobile", async ({ page }) => {
    await page.goto("/");

    // Nav links should still be visible/accessible
    const dashLink = page.locator('nav a:has-text("Dashboard")');
    const settingsLink = page.locator('nav a:has-text("Settings")');

    await expect(dashLink).toBeVisible();
    await expect(settingsLink).toBeVisible();
  });

  test("settings page is usable on mobile", async ({ page }) => {
    await page.goto("/settings");
    await page.locator('text="Cache Status"').waitFor({ timeout: 10_000 });

    // All setting fields should be visible
    await expect(page.locator('text="Configuration"')).toBeVisible();

    // Dropdowns should be interactable
    const cacheSelect = page.locator("select.input").first();
    await expect(cacheSelect).toBeVisible();
  });

  test("zone detail page is readable on mobile", async ({ page }) => {
    await page.goto("/zone/PZZ135");
    await page.locator(".forecast-text-full").waitFor({ timeout: 10_000 });

    // Heading, forecast, and back link should all be visible
    await expect(page.locator("h2")).toBeVisible();
    await expect(page.locator(".forecast-text-full")).toBeVisible();
    await expect(page.locator("a.detail-back")).toBeVisible();

    // Content should not overflow viewport
    const main = page.locator("main#main-content");
    const box = await main.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeLessThanOrEqual(375 + 2); // small tolerance
  });
});
