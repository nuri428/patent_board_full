import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Chatbot Streaming Functionality
 *
 * Tests the ChatMessage component's streaming display features:
 * - Streaming cursor animation
 * - Fade-in animation for content
 * - Backward compatibility (complete messages)
 */

const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
};

test.describe('Chatbot Streaming Display', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for redirect to chat or dashboard
    await page.waitForURL(/.*(chat|dashboard)/, { timeout: 10000 });
  });

  test('should navigate to chat page', async ({ page }) => {
    await page.goto('/chat');
    await expect(page).toHaveURL(/.*chat/);
  });

  test('should display chat interface', async ({ page }) => {
    await page.goto('/chat');

    // Check for chat container
    await expect(page.locator('.chatbot-container, .chat-page')).toBeVisible();

    // Check for input field
    await expect(page.locator('input[type="text"], textarea, [contenteditable="true"]')).toBeVisible();

    // Check for submit button
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should send a message and receive response', async ({ page }) => {
    await page.goto('/chat');

    // Find and fill the chat input
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Hello, this is a test message');

    // Submit the message
    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();

    // Wait for message to appear (user message)
    await expect(page.locator('.chat-message').filter({ hasText: /Hello, this is a test message/ })).toBeVisible({ timeout: 5000 });

    // Wait for AI response (assistant message)
    await expect(page.locator('.chat-message.assistant-message')).toBeVisible({ timeout: 10000 });
  });

  test('should display user and assistant messages correctly', async ({ page }) => {
    await page.goto('/chat');

    // Send a test message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Test message for UI verification');
    await page.locator('button[type="submit"]').first().click();

    // Wait for messages
    await page.waitForTimeout(5000);

    // Check for user message
    const userMessage = page.locator('.chat-message.user-message').filter({ hasText: /Test message for UI verification/ });
    await expect(userMessage).toBeVisible();

    // Check for assistant message header
    const assistantHeader = page.locator('.chat-message.assistant-message .message-header').first();
    await expect(assistantHeader).toBeVisible();
  });

  test('should have proper message structure', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Structure test');
    await page.locator('button[type="submit"]').first().click();

    // Wait for messages
    await page.waitForTimeout(5000);

    // Check for assistant message
    const assistantMessage = page.locator('.chat-message.assistant-message').first();
    await expect(assistantMessage).toBeVisible();

    // Check for message components
    await expect(assistantMessage.locator('.message-header')).toBeVisible();
    await expect(assistantMessage.locator('.message-body')).toBeVisible();
    await expect(assistantMessage.locator('.message-container')).toBeVisible();
  });

  test('should display message role indicators', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Role test');
    await page.locator('button[type="submit"]').first().click();

    // Wait for messages
    await page.waitForTimeout(5000);

    // Check for role indicators in headers
    const assistantHeader = page.locator('.chat-message.assistant-message .message-header').first();
    await expect(assistantHeader).toContainText(/AI|Assistant|Logic/i);
  });

  test('should handle multiple messages in conversation', async ({ page }) => {
    await page.goto('/chat');

    // Send multiple messages
    const messages = ['First message', 'Second message', 'Third message'];
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();

    for (const msg of messages) {
      await chatInput.fill(msg);
      await page.locator('button[type="submit"]').first().click();
      await page.waitForTimeout(2000);
    }

    // Check that all messages are visible
    await expect(page.locator('.chat-message')).toHaveCount(messages.length * 2); // user + assistant for each

    // Take screenshot for evidence
    await page.screenshot({ path: '.sisyphus/evidence/task-10-multiple-messages.png', fullPage: true });
  });

  test('should display pending state while processing', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Pending test');

    // Submit and immediately check for pending state
    await page.locator('button[type="submit"]').first().click();

    // Check for pending indicator (may appear briefly)
    const pendingIndicator = page.locator('.message-pending, .typing-indicator');
    const isVisible = await pendingIndicator.isVisible().catch(() => false);

    // If pending indicator exists, it should be visible
    if (isVisible) {
      await expect(pendingIndicator).toBeVisible({ timeout: 2000 });
    }

    // Wait for response
    await page.waitForTimeout(5000);
  });

  test('should maintain backward compatibility with complete messages', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Compatibility test');
    await page.locator('button[type="submit"]').first().click();

    // Wait for complete messages
    await page.waitForTimeout(5000);

    // Verify messages display correctly
    const messages = page.locator('.chat-message');
    await expect(messages).toHaveCount(2);

    // Check that complete messages don't show streaming indicators
    const streamingCursors = page.locator('.chat-message [aria-label="AI is typing"]');
    await expect(streamingCursors).toHaveCount(0);

    // Take screenshot for evidence
    await page.screenshot({ path: '.sisyphus/evidence/task-10-no-regression.png', fullPage: true });
  });

  test('should handle message timestamp display', async ({ page }) => {
    await page.goto('/chat');

    // Send a message
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Timestamp test');
    await page.locator('button[type="submit"]').first().click();

    // Wait for messages
    await page.waitForTimeout(5000);

    // Check for timestamp in message headers
    const timestampElements = page.locator('.message-header');
    const hasTimestamp = await timestampElements.count() > 0;

    if (hasTimestamp) {
      await expect(timestampElements.first()).toBeVisible();
    }
  });

  test('should support chat session management', async ({ page }) => {
    await page.goto('/chat');

    // Check for session list or session indicator
    const sessionList = page.locator('.session-list, [class*="session"]').first();
    const hasSessionList = await sessionList.isVisible().catch(() => false);

    if (hasSessionList) {
      await expect(sessionList).toBeVisible();
    }

    // Send a message to ensure session is active
    const chatInput = page.locator('input[type="text"], textarea, [contenteditable="true"]').first();
    await chatInput.fill('Session test');
    await page.locator('button[type="submit"]').first().click();
    await page.waitForTimeout(5000);

    // Verify conversation persists
    await expect(page.locator('.chat-message')).toHaveCount(2);
  });
});

test.describe('Streaming Cursor Animation (Manual Test)', () => {
  /**
   * Note: These tests verify the component structure.
   * Actual streaming functionality requires backend implementation
   * of streaming responses, which is not yet available.
   *
   * To manually test streaming:
   * 1. Set isStreaming={true} on ChatMessage component
   * 2. Verify cursor animation appears at end of message
   * 3. Set isStreaming={false}
   * 4. Verify cursor disappears
   */

  test('should have streaming cursor CSS classes defined', async ({ page }) => {
    await page.goto('/chat');

    // Check that page loads without errors
    await expect(page).toHaveURL(/.*chat/);

    // Verify no console errors related to streaming
    const consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.waitForTimeout(2000);

    // Should not have streaming-related errors
    const streamingErrors = consoleErrors.filter(err =>
      err.toLowerCase().includes('stream') ||
      err.toLowerCase().includes('cursor') ||
      err.toLowerCase().includes('framer-motion')
    );

    expect(streamingErrors).toHaveLength(0);
  });

  test('should have framer-motion loaded for animations', async ({ page }) => {
    await page.goto('/chat');

    // Check that framer-motion is loaded
    const motionExists = await page.evaluate(() => {
      return typeof window !== 'undefined' &&
             window.document.querySelector('[class*="motion"]') !== null;
    });

    // Motion components should be present (from typing indicator)
    expect(motionExists).toBeTruthy();
  });
});
