import { test, expect, Page } from '@playwright/test';

test.describe('AI Chatbot Task Management E2E', () => {
  let page: Page;

  test.beforeEach(async ({ browser }) => {
    page = await browser.newPage();
    // Navigate to the dashboard where the chat interface is available
    await page.goto('http://localhost:3000/dashboard');
    
    // For this test, we'll assume the user is already logged in
    // In a real scenario, you would implement login here
  });

  test.afterEach(async () => {
    await page.close();
  });

  test('should allow user to create a task via chatbot', async () => {
    // Wait for the chat interface to load
    await page.waitForSelector('[data-testid="chat-interface"]');
    
    // Type a message to create a task
    await page.fill('input[placeholder="Type your message..."]', 'Add a task to buy groceries');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Verify the AI responded appropriately
    const aiResponse = await page.textContent('.message-assistant');
    expect(aiResponse).not.toBeNull();
    expect(aiResponse).toContain('buy groceries');
    expect(aiResponse).toContain('added');
    
    // Verify the task appears in the task list
    await page.waitForTimeout(1000); // Allow time for UI update
    const taskListItems = await page.$$('.task-item');
    let foundTask = false;
    for (const item of taskListItems) {
      const text = await item.textContent();
      if (text && text.includes('buy groceries')) {
        foundTask = true;
        break;
      }
    }
    expect(foundTask).toBeTruthy();
  });

  test('should allow user to update a task via chatbot', async () => {
    // First, create a task to update
    await page.fill('input[placeholder="Type your message..."]', 'Add a task to walk the dog');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Now update the task
    await page.fill('input[placeholder="Type your message..."]', 'Change the walk the dog task to include morning walk');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Verify the AI responded appropriately
    const aiResponse = await page.textContent('.message-assistant');
    expect(aiResponse).not.toBeNull();
    expect(aiResponse).toContain('updated');
    expect(aiResponse).toContain('morning walk');
  });

  test('should allow user to mark a task as complete via chatbot', async () => {
    // First, create a task to complete
    await page.fill('input[placeholder="Type your message..."]', 'Add a task to finish homework');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Now mark the task as complete
    await page.fill('input[placeholder="Type your message..."]', 'Mark the finish homework task as complete');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Verify the AI responded appropriately
    const aiResponse = await page.textContent('.message-assistant');
    expect(aiResponse).not.toBeNull();
    expect(aiResponse).toContain('complete');
    expect(aiResponse).toContain('finished');
    
    // Verify the task is marked as completed in the UI
    await page.waitForTimeout(1000); // Allow time for UI update
    const completedTask = await page.$('.task-item.completed[data-task-title*="finish homework"]');
    expect(completedTask).toBeTruthy();
  });

  test('should allow user to view tasks via chatbot', async () => {
    // Create a few tasks first
    await page.fill('input[placeholder="Type your message..."]', 'Add a task to clean the house');
    await page.click('button[type="submit"]');
    await page.waitForSelector('.message-assistant');
    
    await page.fill('input[placeholder="Type your message..."]', 'Add a task to call mom');
    await page.click('button[type="submit"]');
    await page.waitForSelector('.message-assistant');
    
    // Now ask to see tasks
    await page.fill('input[placeholder="Type your message..."]', 'Show me my tasks');
    await page.click('button[type="submit"]');
    
    // Wait for the response
    await page.waitForSelector('.message-assistant');
    
    // Verify the AI responded with the tasks
    const aiResponse = await page.textContent('.message-assistant');
    expect(aiResponse).not.toBeNull();
    expect(aiResponse).toContain('clean the house');
    expect(aiResponse).toContain('call mom');
  });
});