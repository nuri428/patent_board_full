# E2E Integration Tests

This directory contains Playwright-based end-to-end tests for the Patent Board application.

## Test Coverage

### Authentication Flow
- Login form validation
- Protected route redirects
- Error handling for invalid credentials

### Report Generation Flow
- Navigate to reports page
- Open generate report modal
- Submit report generation form
- Display report status updates

### WebSocket Notification Flow
- Establish WebSocket connection
- Display toast notifications
- Real-time status updates

### End-to-End User Flow
Complete flow: Login → Generate report → View status → Receive notification

### Health Check Integration
- API health endpoint verification
- Detailed health check with service dependencies

## Running Tests

### Prerequisites
1. Install dependencies:
   ```bash
   npm install
   npx playwright install
   ```

2. Ensure backend services are running:
   ```bash
   # Backend API (port 8005)
   cd ../back_end && uv run uvicorn app.main:app --reload
   
   # Frontend (port 3301)
   npm run dev
   ```

### Run Tests

```bash
# Run all tests
npm run test:e2e

# Run tests with UI mode
npm run test:e2e:ui

# Run tests in debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test e2e/tests/patent-board.spec.js

# Run tests in headed mode (see browser)
npx playwright test --headed
```

## Test Configuration

Tests are configured in `playwright.config.js`:
- **Base URL**: http://localhost:3301
- **Browsers**: Chromium, Firefox
- **Screenshot**: On failure
- **Trace**: On first retry

## Test Data

Test user credentials (should match test database):
- Email: `test@example.com`
- Password: `testpassword123`

## CI/CD Integration

Tests can be run in CI with:
```bash
CI=true npm run test:e2e
```

This will:
- Run tests in headless mode
- Retry failed tests 2 times
- Use 1 worker for deterministic results

## Writing New Tests

See [Playwright documentation](https://playwright.dev/docs/writing-tests) for best practices.

Example test structure:
```javascript
test('should do something', async ({ page }) => {
  await page.goto('/some-route');
  await expect(page.locator('selector')).toBeVisible();
});
```
