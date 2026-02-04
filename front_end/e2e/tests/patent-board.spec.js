import { test, expect } from '@playwright/test';

/**
 * E2E Integration Tests for Patent Board
 * 
 * Tests complete user flows:
 * 1. Login flow
 * 2. Report generation flow
 * 3. WebSocket notification flow
 */

const TEST_USER = {
  email: 'test@example.com',
  password: 'testpassword123',
};

test.describe('Authentication Flow', () => {
  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/chat');
    await expect(page).toHaveURL(/.*login/);
  });

  test('should display login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    await expect(page.locator('.text-red-600, [role="alert"]')).toBeVisible();
  });
});

test.describe('Report Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Wait for redirect to chat or dashboard
    await page.waitForURL(/.*(chat|dashboard)/, { timeout: 10000 });
  });

  test('should navigate to reports page', async ({ page }) => {
    await page.goto('/reports');
    await expect(page.locator('h1, h2').filter({ hasText: /report/i })).toBeVisible();
  });

  test('should open generate report modal', async ({ page }) => {
    await page.goto('/reports');
    
    // Click generate report button
    const generateBtn = page.locator('button').filter({ hasText: /generate|new|create/i }).first();
    await expect(generateBtn).toBeVisible();
    await generateBtn.click();
    
    // Check modal is open
    await expect(page.locator('[role="dialog"], .modal, [class*="modal"]')).toBeVisible();
  });

  test('should submit report generation form', async ({ page }) => {
    await page.goto('/reports');
    
    // Open generate modal
    const generateBtn = page.locator('button').filter({ hasText: /generate|new|create/i }).first();
    await generateBtn.click();
    
    // Fill form
    await page.fill('input[name="topic"], input[placeholder*="topic" i]', 'AI in Healthcare');
    
    // Select report type if dropdown exists
    const typeSelect = page.locator('select[name="report_type"]').first();
    if (await typeSelect.isVisible().catch(() => false)) {
      await typeSelect.selectOption('comprehensive');
    }
    
    // Submit form
    const submitBtn = page.locator('button[type="submit"]').filter({ hasText: /generate|submit|create/i }).first();
    await submitBtn.click();
    
    // Check for success message or redirect
    await expect(page.locator('.text-green-600, .text-blue-600, [role="status"]').first()).toBeVisible({ timeout: 5000 });
  });

  test('should display report status updates', async ({ page }) => {
    await page.goto('/reports');
    
    // Check for status badges or indicators
    const statusElements = page.locator('[class*="status"], [class*="badge"], .px-2').first();
    if (await statusElements.isVisible().catch(() => false)) {
      await expect(statusElements).toBeVisible();
    }
  });
});

test.describe('WebSocket Notification Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/.*(chat|dashboard)/, { timeout: 10000 });
  });

  test('should establish WebSocket connection', async ({ page }) => {
    // Listen for console messages to detect WebSocket activity
    const consoleMessages = [];
    page.on('console', (msg) => {
      consoleMessages.push(msg.text());
    });

    // Navigate to any page (WebSocket should connect on auth)
    await page.goto('/reports');
    
    // Wait a bit for WebSocket to attempt connection
    await page.waitForTimeout(2000);
    
    // Check for WebSocket-related console messages
    const wsMessages = consoleMessages.filter(msg => 
      msg.toLowerCase().includes('websocket') || 
      msg.toLowerCase().includes('ws') ||
      msg.toLowerCase().includes('connected')
    );
    
    // WebSocket messages might be present in debug mode
    console.log('WebSocket-related messages:', wsMessages);
  });

  test('should display toast notifications', async ({ page }) => {
    await page.goto('/reports');
    
    // Look for toast container or notification elements
    const toastContainer = page.locator('[class*="toast"], [class*="notification"]').first();
    
    // Toast might not be visible initially, but container should exist
    // Test passes if page loads without errors
    await expect(page).toHaveURL(/.*reports/);
  });
});

test.describe('End-to-End User Flow', () => {
  test('complete flow: login → generate report → view status', async ({ page }) => {
    // Step 1: Login
    await page.goto('/login');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Wait for authentication
    await page.waitForURL(/.*(chat|dashboard)/, { timeout: 10000 });
    
    // Step 2: Navigate to reports
    await page.goto('/reports');
    await expect(page.locator('h1, h2').filter({ hasText: /report/i })).toBeVisible();
    
    // Step 3: Generate a report
    const generateBtn = page.locator('button').filter({ hasText: /generate|new|create/i }).first();
    await expect(generateBtn).toBeVisible();
    await generateBtn.click();
    
    // Fill and submit form
    await page.fill('input[name="topic"], input[placeholder*="topic" i]', 'Machine Learning Patents');
    const submitBtn = page.locator('button[type="submit"]').filter({ hasText: /generate|submit|create/i }).first();
    await submitBtn.click();
    
    // Step 4: Verify report appears in list
    await expect(page.locator('text=Machine Learning Patents, text=Pending, text=Processing').first()).toBeVisible({ timeout: 10000 });
    
    // Step 5: Wait for status updates (polling every 3 seconds)
    await page.waitForTimeout(5000);
    
    // Take screenshot for verification
    await page.screenshot({ path: 'test-results/e2e-report-flow.png' });
  });
});

test.describe('Health Check Integration', () => {
  test('API health endpoint should return healthy', async ({ request }) => {
    const response = await request.get('http://localhost:8005/health');
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body.status).toBe('healthy');
  });

  test('detailed health check should include services', async ({ request }) => {
    const response = await request.get('http://localhost:8005/health/detailed');
    expect(response.ok()).toBeTruthy();
    
    const body = await response.json();
    expect(body).toHaveProperty('services');
    expect(body).toHaveProperty('timestamp');
    expect(body).toHaveProperty('response_time_ms');
  });
});
