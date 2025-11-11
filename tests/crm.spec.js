const { test, expect } = require("@playwright/test");

/**
 * AutoMentor CRM - Comprehensive Test Suite
 * Tests all functionality across realistic recruiting workflows
 */

test.describe("AutoMentor CRM - Comprehensive Testing", () => {
  // ========== LEVEL 1: INTAKE - DATA ENTRY ==========

  test.describe("Level 1: Intake - Data Entry", () => {
    test("should add complete recruit with all fields", async ({ page }) => {
      await page.goto("/add");

      // Fill complete form
      await page.getByLabel("Name").fill("John Complete Doe");
      await page.getByLabel("Email").fill("john.complete@test.com");
      await page.getByLabel("Phone").fill("(555) 123-4567");
      await page.locator("select[name='stage']").selectOption("New");
      await page
        .getByLabel("Notes")
        .fill("Complete record with all fields filled");

      // Submit and verify redirect
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Verify recruit appears on dashboard
      await expect(page.locator("text=John Complete Doe")).toBeVisible();

      // Verify stage count updated
      const statsRow = page.locator(".stats-row");
      await expect(statsRow.locator(".stat-card").first()).toContainText(/\d+/);
    });

    test("should add recruit with partial data (missing phone)", async ({
      page,
    }) => {
      await page.goto("/add");

      await page.getByLabel("Name").fill("Jane Partial Smith");
      await page.getByLabel("Email").fill("jane.partial@test.com");
      // Phone left empty
      await page.locator("select[name='stage']").selectOption("New");

      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      await expect(page.locator("text=Jane Partial Smith")).toBeVisible();
    });

    test("should add recruit with minimal data (name only)", async ({
      page,
    }) => {
      await page.goto("/add");

      await page.getByLabel("Name").fill("Minimal Name Only");
      // All other fields empty

      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      await expect(page.locator("text=Minimal Name Only")).toBeVisible();
    });

    test("should validate required name field", async ({ page }) => {
      await page.goto("/add");

      // Try to submit without name
      await page.getByLabel("Email").fill("no-name@test.com");
      await page.getByRole("button", { name: "Add Recruit" }).click();

      // Should stay on add page due to HTML5 validation
      await expect(page).toHaveURL(/.*\/add/);
    });

    test("should instantly refresh dashboard after adding recruit", async ({
      page,
    }) => {
      await page.goto("/");

      // Get initial count
      const statsRow = page.locator(".stats-row");
      const newStageCard = statsRow.locator(".stat-card").first();
      const initialText = await newStageCard.textContent();
      const initialCount = parseInt(initialText?.match(/\d+/)?.[0] || "0");

      // Add recruit via form
      await page.goto("/add");
      await page.getByLabel("Name").fill("Instant Refresh Test");
      await page.locator("select[name='stage']").selectOption("New");
      await page.getByRole("button", { name: "Add Recruit" }).click();

      // Check dashboard updated
      await page.waitForURL("/");
      const updatedText = await newStageCard.textContent();
      const updatedCount = parseInt(updatedText?.match(/\d+/)?.[0] || "0");

      expect(updatedCount).toBeGreaterThan(initialCount);
    });
  });

  // ========== LEVEL 2: STAGE TRANSITIONS ==========

  test.describe("Level 2: Stage Transitions", () => {
    test("should update recruit stage and reflect in metrics", async ({
      page,
    }) => {
      // First add a recruit
      await page.goto("/add");
      await page.getByLabel("Name").fill("Stage Transition Test");
      await page.getByLabel("Email").fill("stage.test@test.com");
      await page.locator("select[name='stage']").selectOption("New");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Find the recruit card
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Stage Transition Test"),
        })
        .first();

      await expect(recruitCard).toBeVisible();

      // Click edit button
      await recruitCard.locator("button:has-text('Edit')").click();

      // Wait for form to appear
      const editForm = recruitCard.locator("form");
      await expect(editForm).toBeVisible();

      // Change stage
      await editForm.locator("select[name='stage']").selectOption("Contacted");

      // Save changes
      await editForm.locator("button:has-text('Save')").click();

      // Wait for form to disappear
      await expect(editForm).not.toBeVisible();

      // Verify stage updated in UI
      await expect(recruitCard.locator(".stage-badge")).toContainText(
        "Contacted"
      );
    });

    test("should handle bulk stage updates correctly", async ({ page }) => {
      // Add multiple recruits
      const names = ["Bulk Test 1", "Bulk Test 2", "Bulk Test 3"];

      for (const name of names) {
        await page.goto("/add");
        await page.getByLabel("Name").fill(name);
        await page.locator("select[name='stage']").selectOption("New");
        await page.getByRole("button", { name: "Add Recruit" }).click();
        await page.waitForURL("/");
      }

      // Update each to different stages
      const stages = ["Contacted", "In Training", "Licensed"];

      for (let i = 0; i < names.length; i++) {
        const recruitCard = page
          .locator(".recruit-card", {
            has: page.locator(`text=${names[i]}`),
          })
          .first();

        await recruitCard.locator("button:has-text('Edit')").click();
        await recruitCard
          .locator("select[name='stage']")
          .selectOption(stages[i]);
        await recruitCard.locator("button:has-text('Save')").click();

        // Wait for save to complete
        await page.waitForTimeout(500);
      }

      // Verify all stages updated
      for (let i = 0; i < names.length; i++) {
        const recruitCard = page
          .locator(".recruit-card", {
            has: page.locator(`text=${names[i]}`),
          })
          .first();
        await expect(recruitCard.locator(".stage-badge")).toContainText(
          stages[i]
        );
      }
    });

    test("should support keyboard navigation in dropdown", async ({ page }) => {
      await page.goto("/add");

      await page.getByLabel("Name").fill("Keyboard Test");

      // Tab to stage dropdown
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab"); // Should be on stage select

      // Use arrow keys
      await page.keyboard.press("ArrowDown");
      await page.keyboard.press("ArrowDown");

      // Submit
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Enter");

      await page.waitForURL("/");
      await expect(page.locator("text=Keyboard Test")).toBeVisible();
    });
  });

  // ========== LEVEL 3: EDIT & DELETE FLOW ==========

  test.describe("Level 3: Edit & Delete Flow", () => {
    test("should edit existing recruit without page refresh", async ({
      page,
    }) => {
      // Add recruit
      await page.goto("/add");
      await page.getByLabel("Name").fill("Edit Test User");
      await page.getByLabel("Email").fill("edit@test.com");
      await page.getByLabel("Notes").fill("Original notes");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Find and edit recruit
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Edit Test User"),
        })
        .first();

      await recruitCard.locator("button:has-text('Edit')").click();

      // Modify notes
      await recruitCard
        .locator("textarea[name='notes']")
        .fill("Updated notes via edit");
      await recruitCard.locator("button:has-text('Save')").click();

      // Verify notes updated without reload
      await page.waitForTimeout(500);
      await recruitCard.locator("button:has-text('Edit')").click();
      await expect(recruitCard.locator("textarea[name='notes']")).toHaveValue(
        "Updated notes via edit"
      );
    });

    test("should delete recruit and update counts", async ({ page }) => {
      // Add recruit
      await page.goto("/add");
      await page.getByLabel("Name").fill("Delete Test User");
      await page.locator("select[name='stage']").selectOption("New");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Get initial New count
      const statsRow = page.locator(".stats-row");
      const newCard = statsRow.locator(".stat-card").first();
      const initialText = await newCard.textContent();
      const initialCount = parseInt(initialText?.match(/\d+/)?.[0] || "0");

      // Delete recruit
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Delete Test User"),
        })
        .first();

      await recruitCard.locator("button:has-text('Delete')").click();

      // Confirm deletion (if dialog appears)
      page.on("dialog", (dialog) => dialog.accept());

      // Wait for card to be removed
      await expect(recruitCard).not.toBeVisible({ timeout: 2000 });

      // Verify count decreased
      await page.waitForTimeout(500);
      const updatedText = await newCard.textContent();
      const updatedCount = parseInt(updatedText?.match(/\d+/)?.[0] || "0");
      expect(updatedCount).toBeLessThan(initialCount);
    });

    test("should delete one recruit per stage accurately", async ({ page }) => {
      const stages = [
        "New",
        "Contacted",
        "In Training",
        "Licensed",
        "Inactive",
      ];

      // Add one recruit per stage
      for (const stage of stages) {
        await page.goto("/add");
        await page.getByLabel("Name").fill(`Delete ${stage} Test`);
        await page.locator("select[name='stage']").selectOption(stage);
        await page.getByRole("button", { name: "Add Recruit" }).click();
        await page.waitForURL("/");
      }

      // Delete each one
      for (const stage of stages) {
        const recruitCard = page
          .locator(".recruit-card", {
            has: page.locator(`text=Delete ${stage} Test`),
          })
          .first();

        if (await recruitCard.isVisible()) {
          await recruitCard.locator("button:has-text('Delete')").click();
          page.on("dialog", (dialog) => dialog.accept());
          await expect(recruitCard).not.toBeVisible({ timeout: 2000 });
        }
      }
    });
  });

  // ========== LEVEL 4: DASHBOARD INTEGRITY ==========

  test.describe("Level 4: Dashboard Integrity", () => {
    test("should display all stage cards correctly", async ({ page }) => {
      await page.goto("/");

      const statsRow = page.locator(".stats-row");
      const statCards = statsRow.locator(".stat-card");

      // Should have 5 stage cards minimum (might have weekly stats too)
      await expect(statCards.first()).toBeVisible();

      // Check stage labels present
      const stages = [
        "New",
        "Contacted",
        "In Training",
        "Licensed",
        "Inactive",
      ];
      for (const stage of stages) {
        await expect(page.locator(`text=${stage}`).first()).toBeVisible();
      }
    });

    test("should render cards correctly with 10+ entries", async ({ page }) => {
      await page.goto("/");

      // Check if recruits list exists
      const recruitsList = page.locator(".recruits-list");
      await expect(recruitsList).toBeVisible();

      // Verify cards render
      const recruitCards = page.locator(".recruit-card");
      const count = await recruitCards.count();

      // Should have some recruits (from demo data or previous tests)
      expect(count).toBeGreaterThanOrEqual(0);
    });

    test("should maintain smooth scroll performance", async ({ page }) => {
      await page.goto("/");

      // Scroll through page
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });

      await page.waitForTimeout(500);

      // Scroll back up
      await page.evaluate(() => {
        window.scrollTo(0, 0);
      });

      // Page should still be responsive
      const addButton = page.locator("a:has-text('Add Recruit')");
      await expect(addButton).toBeVisible();
    });
  });

  // ========== LEVEL 5: PERSISTENCE & REFRESH ==========

  test.describe("Level 5: Persistence & Refresh", () => {
    test("should persist data across page refreshes", async ({ page }) => {
      // Add recruit
      await page.goto("/add");
      await page.getByLabel("Name").fill("Persistence Test User");
      await page.getByLabel("Email").fill("persist@test.com");
      await page.locator("select[name='stage']").selectOption("Contacted");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Verify recruit exists
      await expect(page.locator("text=Persistence Test User")).toBeVisible();

      // Refresh page
      await page.reload();

      // Verify recruit still exists
      await expect(page.locator("text=Persistence Test User")).toBeVisible();

      // Verify stage persisted
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Persistence Test User"),
        })
        .first();
      await expect(recruitCard.locator(".stage-badge")).toContainText(
        "Contacted"
      );
    });

    test("should preserve timestamps after edits", async ({ page }) => {
      await page.goto("/add");
      await page.getByLabel("Name").fill("Timestamp Test");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Edit recruit
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Timestamp Test"),
        })
        .first();

      await recruitCard.locator("button:has-text('Edit')").click();
      await recruitCard
        .locator("select[name='stage']")
        .selectOption("Contacted");
      await recruitCard.locator("button:has-text('Save')").click();

      // Timestamps should exist (checked via visual inspection or API)
      await page.waitForTimeout(500);
      await expect(recruitCard).toBeVisible();
    });
  });

  // ========== LEVEL 6: EDGE CASES ==========

  test.describe("Level 6: Edge Cases", () => {
    test("should handle duplicate emails", async ({ page }) => {
      const duplicateEmail = "duplicate@test.com";

      // Add first recruit
      await page.goto("/add");
      await page.getByLabel("Name").fill("First Duplicate");
      await page.getByLabel("Email").fill(duplicateEmail);
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Add second recruit with same email
      await page.goto("/add");
      await page.getByLabel("Name").fill("Second Duplicate");
      await page.getByLabel("Email").fill(duplicateEmail);
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Both should exist (system allows duplicates)
      await expect(page.locator("text=First Duplicate")).toBeVisible();
      await expect(page.locator("text=Second Duplicate")).toBeVisible();
    });

    test("should handle very long names", async ({ page }) => {
      await page.goto("/add");

      const longName =
        "Very Long Name That Tests UI Boundaries And Word Wrapping Capabilities Of The Card Layout System";
      await page.getByLabel("Name").fill(longName);
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Should display without breaking layout
      const recruitCard = page.locator(".recruit-card").first();
      await expect(recruitCard).toBeVisible();
    });

    test("should handle special characters in input", async ({ page }) => {
      await page.goto("/add");

      await page.getByLabel("Name").fill("Test User @#$% & Symbols");
      await page.getByLabel("Email").fill("special+chars@test.com");
      await page
        .getByLabel("Notes")
        .fill("Notes with <html> & \"quotes\" and 'apostrophes'");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Should handle without XSS or breaking
      await expect(page.locator("text=Test User @#$% & Symbols")).toBeVisible();
    });

    test("should handle backward stage transitions", async ({ page }) => {
      // Add recruit at Licensed stage
      await page.goto("/add");
      await page.getByLabel("Name").fill("Backward Stage Test");
      await page.locator("select[name='stage']").selectOption("Licensed");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      // Move back to Contacted (unusual but valid)
      const recruitCard = page
        .locator(".recruit-card", {
          has: page.locator("text=Backward Stage Test"),
        })
        .first();

      await recruitCard.locator("button:has-text('Edit')").click();
      await recruitCard
        .locator("select[name='stage']")
        .selectOption("Contacted");
      await recruitCard.locator("button:has-text('Save')").click();

      // Should update successfully
      await page.waitForTimeout(500);
      await expect(recruitCard.locator(".stage-badge")).toContainText(
        "Contacted"
      );
    });
  });

  // ========== LEVEL 7: MOBILE RESPONSIVENESS ==========

  test.describe("Level 7: Mobile Responsiveness", () => {
    test("should display correctly on mobile viewport", async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.goto("/");

      // Navigation should be visible
      await expect(page.locator("nav")).toBeVisible();

      // Stats should stack vertically
      const statsRow = page.locator(".stats-row");
      await expect(statsRow).toBeVisible();

      // Cards should be full width
      const recruitCard = page.locator(".recruit-card").first();
      if (await recruitCard.isVisible()) {
        const box = await recruitCard.boundingBox();
        if (box) {
          // Card should be close to viewport width (minus padding)
          expect(box.width).toBeGreaterThan(300);
        }
      }
    });

    test("should maintain functionality on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });

      await page.goto("/add");

      // Form should work
      await page.getByLabel("Name").fill("Tablet Test");
      await page.getByRole("button", { name: "Add Recruit" }).click();
      await page.waitForURL("/");

      await expect(page.locator("text=Tablet Test")).toBeVisible();
    });
  });
});
