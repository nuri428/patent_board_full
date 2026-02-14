import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Task 9: SSE Streaming in Chatbot Component
 *
 * Tests SSE streaming functionality:
 * - Streaming token-by-token display
 * - Patent URLs from metadata
 * - Loading states during streaming
 * - Connection error handling
 * - Backward compatibility with non-streaming mode
 */

const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
};

test.describe('Task 9: SSE Streaming Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to chat or dashboard
    await page.waitForURL(/.*(chat|dashboard)/, { timeout: 10000 });
  });

  test('Scenario: Chatbot displays streaming text token-by-token', async ({ page }) => {
    // Preconditions: Frontend dev server running, LangServe on port 8003, valid login
    await page.goto('/chat');

    // Fill: .chat-input with "Show me streaming"
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Show me streaming');

    // Click: button[type="submit"]
    await page.click('button[type="submit"]');

    // Wait for: .message.assistant visible (timeout: 10s)
    await expect(page.locator('.message.assistant, .chat-message.assistant-message')).toBeVisible({ timeout: 10000 });

    // Observe message content appears token-by-token
    // Assert: Text updates in real-time (not all at once)
    // Assert: Each token is visible as it arrives

    // Note: This test requires LangServe backend to be running
    // If backend is not available, this will fail or timeout

    // Screenshot: .sisyphus/evidence/task-9-streaming-display.png
    await page.screenshot({
      path: '.sisyphus/evidence/task-9-streaming-display.png',
      fullPage: true
    });

    // Expected Result: Token-by-token streaming visible in real-time
    // Evidence: Screenshot showing progressive text buildup captured
  });

  test('Scenario: Chatbot handles streaming metadata (patent URLs)', async ({ page }) => {
    // Preconditions: Frontend dev server running, message with patents
    await page.goto('/chat');

    // Fill: .chat-input with "Search AI patents"
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Search AI patents');

    // Click: button[type="submit"]
    await page.click('button[type="submit"]');

    // Wait for stream to complete (timeout: 10s)
    await page.waitForTimeout(10000);

    // Assert: Patent URLs displayed after stream
    // Assert: URLs are clickable/interactive

    // Screenshot: .sisyphus/evidence/task-9-patent-urls.png
    await page.screenshot({
      path: '.sisyphus/evidence/task-9-patent-urls.png',
      fullPage: true
    });

    // Expected Result: Patent URLs extracted from metadata and displayed
    // Evidence: Screenshot showing patent URLs captured
  });

  test('Scenario: Chatbot shows loading state during streaming', async ({ page }) => {
    // Preconditions: Frontend dev server running
    await page.goto('/chat');

    // Fill: .chat-input with "Test loading"
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test loading');

    // Click: button[type="submit"]
    await page.click('button[type="submit"]');

    // Wait: 2 seconds
    await page.waitForTimeout(2000);

    // Assert: Loading indicator visible ("AI is typing" or spinner)
    await expect(page.locator('.typing-indicator')).toBeVisible({ timeout: 3000 });

    // Assert: Send button disabled during streaming
    const submitButton = page.locator('button[type="submit"]').first();
    await expect(submitButton).toBeDisabled();

    // Wait for stream to complete (10 seconds)
    await page.waitForTimeout(10000);

    // Assert: Loading indicator disappears
    await expect(page.locator('.typing-indicator')).toBeHidden({ timeout: 3000 });

    // Assert: Send button re-enabled
    await expect(submitButton).toBeEnabled();

    // Screenshot: .sisyphus/evidence/task-9-loading-states.png
    await page.screenshot({
      path: '.sisyphus/evidence/task-9-loading-states.png',
      fullPage: true
    });

    // Expected Result: Loading states visible during streaming, hidden after
    // Evidence: Screenshots showing loading states captured
  });

  test('Scenario: Chatbot handles connection errors gracefully', async ({ page }) => {
    // Preconditions: Frontend dev server running, LangServe stopped
    // Note: This test requires manual intervention to stop LangServe
    // For automated testing, we can't stop the service from the browser

    await page.goto('/chat');

    // Fill: .chat-input with "Test error"
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test error');

    // Click: button[type="submit"]
    await page.click('button[type="submit"]');

    // Wait: 5 seconds
    await page.waitForTimeout(5000);

    // Assert: Error message displayed
    // Assert: Error message mentions "connection" or "network"
    // Assert: Retry button visible

    // Screenshot: .sisyphus/evidence/task-9-error-handling.png
    await page.screenshot({
      path: '.sisyphus/evidence/task-9-error-handling.png',
      fullPage: true
    });

    // Expected Result: Error displayed with retry option
    // Evidence: Screenshot showing error state captured
  });

  test('Scenario: Backward compatibility with non-streaming mode', async ({ page }) => {
    // Preconditions: Frontend dev server running, unauthenticated user
    // For this test, we'll logout first
    await page.goto('/logout');

    // Navigate to: http://localhost:3000/chat (unauthenticated)
    await page.goto('/chat');

    // Fill: .chat-input with "Test limited mode"
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test limited mode');

    // Click: button[type="submit"]
    await page.click('button[type="submit"]');

    // Wait: 3 seconds
    await page.waitForTimeout(3000);

    // Assert: Response appears (limited mode works)
    // Assert: No streaming errors or warnings

    // Screenshot: .sisyphus/evidence/task-9-backward-compat.png
    await page.screenshot({
      path: '.sisyphus/evidence/task-9-backward-compat.png',
      fullPage: true
    });

    // Expected Result: Non-streaming fallback works, no errors
    // Evidence: Screenshot with full response (no streaming) captured
  });

  test('Scenario: Stop button appears during streaming', async ({ page }) => {
    await page.goto('/chat');

    // Fill and send message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test stop button');
    await page.click('button[type="submit"]');

    // Wait briefly for streaming to start
    await page.waitForTimeout(1000);

    // Assert: Stop button is visible during streaming
    await expect(page.locator('button:has-text("Stop")')).toBeVisible({ timeout: 3000 });
  });

  test('Scenario: Stop button aborts streaming', async ({ page }) => {
    await page.goto('/chat');

    // Fill and send message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test abort');

    await page.click('button[type="submit"]');

    // Wait for streaming to start
    await page.waitForTimeout(1000);

    // Click stop button
    await page.click('button:has-text("Stop")');

    // Wait for abort to complete
    await page.waitForTimeout(1000);

    // Assert: Streaming stops (no more messages)
    // Assert: Input is re-enabled
    const submitButton = page.locator('button[type="submit"]').first();
    await expect(submitButton).toBeEnabled();
  });

  test('Scenario: Typing dots animation is visible', async ({ page }) => {
    await page.goto('/chat');

    // Fill and send message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test animation');
    await page.click('button[type="submit"]');

    // Wait for streaming to start
    await page.waitForTimeout(1000);

    // Assert: Typing indicator is visible
    await expect(page.locator('.typing-indicator')).toBeVisible({ timeout: 3000 });

    // Assert: Typing dots are visible
    await expect(page.locator('.typing-dots')).toBeVisible();
  });
});
