import { test, expect, Page } from '@playwright/test';

// Test real-time sync functionality
test.describe('Real-time Sync Functionality', () => {
  let page1: Page;
  let page2: Page;

  test.beforeAll(async ({ browser }) => {
    // Open two browser contexts to simulate two users
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    page1 = await context1.newPage();
    page2 = await context2.newPage();
    
    // Navigate to the dashboard in both pages
    await page1.goto('/dashboard');
    await page2.goto('/dashboard');
    
    // Wait for both pages to load
    await page1.waitForSelector('[data-testid="task-list"]');
    await page2.waitForSelector('[data-testid="task-list"]');
  });

  test.afterAll(async () => {
    await page1.close();
    await page2.close();
  });

  test('should sync tasks in real-time between different tabs', async () => {
    // Create a task in the first tab
    await page1.fill('[data-testid="task-title-input"]', 'Real-time sync test task');
    await page1.fill('[data-testid="task-description-input"]', 'This task should appear in the other tab');
    await page1.click('[data-testid="add-task-button"]');
    
    // Wait for the task to be created
    await page1.waitForSelector('[data-testid="task-item"]:has-text("Real-time sync test task")');
    
    // Check that the task appears in the second tab within a reasonable time
    await expect(page2.locator('[data-testid="task-item"]:has-text("Real-time sync test task")')).toBeVisible({ timeout: 10000 });
    
    // Verify the description is also synced
    await expect(page2.locator('[data-testid="task-item"]:has-text("This task should appear in the other tab")')).toBeVisible();
  });

  test('should sync task updates in real-time', async () => {
    // Update the task in the first tab
    await page1.click('[data-testid="toggle-completion-btn"]');
    
    // Wait for the completion status to update in the first tab
    await page1.waitForSelector('[data-testid="task-item"].completed:has-text("Real-time sync test task")');
    
    // Check that the completion status is updated in the second tab
    await expect(page2.locator('[data-testid="task-item"].completed:has-text("Real-time sync test task")')).toBeVisible({ timeout: 10000 });
  });

  test('should sync task deletions in real-time', async () => {
    // Delete the task in the first tab
    await page1.click('[data-testid="delete-task-btn"]');
    
    // Confirm deletion
    page1.on('dialog', dialog => dialog.accept());
    
    // Wait for the task to be removed from the first tab
    await expect(page1.locator('[data-testid="task-item"]:has-text("Real-time sync test task")')).not.toBeVisible();
    
    // Check that the task is also removed from the second tab
    await expect(page2.locator('[data-testid="task-item"]:has-text("Real-time sync test task")')).not.toBeVisible({ timeout: 10000 });
  });
});