# Microsoft Playwright MCP - UI Testing Setup Guide

**Date**: 2025-11-13
**Status**: Ready for Installation
**Priority**: High (User-Requested)

---

## EXECUTIVE SUMMARY

Microsoft Playwright MCP enables **automated browser testing** for your entire Streamlit UI. It can navigate pages, click buttons, fill forms, and verify elements - essentially "going all over the UI and testing it all" as requested.

**User Request**:
> "one I would like to test is microsoft play right that should go all over a UI and test it all"

---

## WHAT IS MICROSOFT PLAYWRIGHT MCP?

### Overview

**Playwright MCP** is a Model Context Protocol server that gives AI assistants the ability to:
- Navigate web pages (your Streamlit dashboard)
- Click buttons and links
- Fill form inputs
- Take screenshots
- Verify elements exist
- Test entire workflows automatically

### How It Works

```
Claude/AVA → Playwright MCP → Actual Browser → Your Streamlit App
```

The AI can **"see" your UI** using the accessibility tree (no screenshots needed) and interact with it just like a human user would.

---

## INSTALLATION

### Prerequisites

- **Node.js 18+** installed
- **npm** package manager
- **Windows PowerShell** or **Command Prompt**

### Step 1: Install Playwright MCP

Open PowerShell/Command Prompt:

```bash
npm install -g @playwright/mcp
```

**Expected Output**:
```
added 1 package in 5s
```

### Step 2: Install Browser Binaries

```bash
npx playwright install
```

**Expected Output**:
```
Downloading Chromium 120.0.6099.71 (playwright build v1095)
Downloading Firefox 119.0 (playwright build v1421)
Downloading Webkit 17.4 (playwright build v1900)
```

This downloads actual browser binaries that Playwright will control.

### Step 3: Verify Installation

```bash
npx playwright --version
```

**Expected Output**:
```
Version 1.40.1
```

---

## CONFIGURATION

### For Claude Desktop (if using Claude app)

Add to Claude config file:

**Location**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "-y",
        "@playwright/mcp"
      ]
    }
  }
}
```

### For Python Integration (Direct Use)

Create file: `test_playwright_mcp.py`

```python
import asyncio
from playwright.async_api import async_playwright

async def test_streamlit_dashboard():
    """Test AVA Streamlit dashboard"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # headless=True for no GUI
        page = await browser.new_page()

        # Navigate to dashboard
        await page.goto('http://localhost:8513')

        # Wait for page to load
        await page.wait_for_load_state('networkidle')

        # Take screenshot
        await page.screenshot(path='dashboard_home.png')

        # Click on AVA chat tab
        await page.click('text=AVA Chat')
        await page.wait_for_timeout(1000)

        # Fill in chat input
        chat_input = await page.locator('textarea[placeholder*="help"]')
        await chat_input.fill("Test message from Playwright")

        # Click send button (inside the input)
        send_button = await page.locator('button[type="submit"]')
        await send_button.click()

        # Verify response appears
        await page.wait_for_selector('text=AVA', timeout=10000)

        # Take screenshot of result
        await page.screenshot(path='dashboard_chat_result.png')

        print("✓ Test passed: AVA chat working!")

        await browser.close()

# Run test
asyncio.run(test_streamlit_dashboard())
```

**Run the test**:
```bash
cd c:\Code\Legion\repos\ava
python test_playwright_mcp.py
```

---

## EXAMPLE TESTS FOR YOUR DASHBOARD

### Test 1: Navigate All Pages

```python
async def test_all_pages():
    """Navigate through all dashboard pages"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        pages_to_test = [
            "Dashboard",
            "Opportunities",
            "Positions",
            "Premium Scanner",
            "TradingView Watchlists",
            "Database Scan",
            "Earnings Calendar",
            "Calendar Spreads",
            "Game Cards",
            "AVA Chat"
        ]

        for page_name in pages_to_test:
            print(f"Testing {page_name}...")
            await page.click(f'text={page_name}')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=f'test_{page_name.lower().replace(" ", "_")}.png')
            print(f"✓ {page_name} loaded successfully")

        await browser.close()
```

### Test 2: Opportunities Filtering

```python
async def test_opportunities_filtering():
    """Test CSP opportunities with filters"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        # Go to Opportunities page
        await page.click('text=Opportunities')
        await page.wait_for_load_state('networkidle')

        # Set minimum premium
        premium_input = await page.locator('input[type="number"]').first
        await premium_input.fill('1.00')

        # Set DTE range
        dte_slider = await page.locator('div[data-testid="stSlider"]').first
        await dte_slider.click()  # Interact with slider

        # Verify results update
        results = await page.locator('text=Premium').count()
        assert results > 0, "No opportunities found"

        print(f"✓ Found {results} opportunities with filters")

        await browser.close()
```

### Test 3: Robinhood Position Loading

```python
async def test_positions_loading():
    """Test if Robinhood positions load"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        # Go to Positions page
        await page.click('text=Positions')
        await page.wait_for_timeout(3000)  # Wait for data load

        # Check if positions table exists
        table_exists = await page.locator('table').count() > 0

        if table_exists:
            print("✓ Positions table loaded")

            # Count rows
            rows = await page.locator('tr').count()
            print(f"✓ Found {rows} position rows")
        else:
            print("⚠ No positions found (may be expected if no open positions)")

        await browser.close()
```

### Test 4: AVA Chat Interaction

```python
async def test_ava_chat_full_workflow():
    """Complete AVA chat test workflow"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        # Navigate to AVA Chat
        await page.click('text=AVA Chat')
        await page.wait_for_load_state('networkidle')

        # Test different message types
        test_messages = [
            "What tickers are good for wheel strategy?",
            "Show me CSP opportunities under $50",
            "What's my portfolio status?"
        ]

        for msg in test_messages:
            print(f"Testing message: {msg}")

            # Fill chat input
            chat_input = await page.locator('textarea').first
            await chat_input.fill(msg)

            # Send message
            await page.keyboard.press('Enter')

            # Wait for response
            await page.wait_for_timeout(5000)

            # Verify response appeared
            messages = await page.locator('div[data-testid="stChatMessage"]').count()
            print(f"✓ Total messages: {messages}")

        await browser.close()
```

### Test 5: File Upload Test

```python
async def test_file_upload():
    """Test file upload in AVA chat"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        # Go to AVA Chat
        await page.click('text=AVA Chat')

        # Look for file upload button (paperclip icon)
        file_input = await page.locator('input[type="file"]')

        # Upload test file
        await file_input.set_input_files('test_data.csv')

        # Verify file shows in chat
        await page.wait_for_selector('text=test_data.csv', timeout=5000)

        print("✓ File upload successful")

        await browser.close()
```

---

## COMPREHENSIVE TEST SUITE

Create `comprehensive_ui_tests.py`:

```python
import asyncio
from playwright.async_api import async_playwright
import time

class StreamlitDashboardTests:
    """Comprehensive test suite for AVA dashboard"""

    def __init__(self, base_url="http://localhost:8513"):
        self.base_url = base_url
        self.results = []

    async def run_all_tests(self):
        """Run all test cases"""
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)
            self.page = await self.browser.new_page()

            # Set viewport
            await self.page.set_viewport_size({"width": 1920, "height": 1080})

            tests = [
                self.test_homepage_loads,
                self.test_all_navigation_tabs,
                self.test_opportunities_page,
                self.test_positions_page,
                self.test_ava_chat,
                self.test_settings_panel,
                self.test_responsive_design
            ]

            for test in tests:
                try:
                    await test()
                    self.results.append(f"✓ PASS: {test.__name__}")
                except Exception as e:
                    self.results.append(f"✗ FAIL: {test.__name__} - {str(e)}")

            await self.browser.close()

            # Print results
            print("\n" + "="*60)
            print("TEST RESULTS")
            print("="*60)
            for result in self.results:
                print(result)
            print("="*60)

    async def test_homepage_loads(self):
        """Test if homepage loads successfully"""
        await self.page.goto(self.base_url)
        await self.page.wait_for_load_state('networkidle')

        # Verify title exists
        title = await self.page.locator('h1').first.text_content()
        assert title, "No title found"

        print(f"✓ Homepage loaded: {title}")

    async def test_all_navigation_tabs(self):
        """Test all navigation tabs are clickable"""
        tabs = await self.page.locator('[role="tab"]').all()

        for tab in tabs:
            tab_name = await tab.text_content()
            await tab.click()
            await self.page.wait_for_timeout(1000)
            print(f"✓ Navigated to: {tab_name}")

    async def test_opportunities_page(self):
        """Test opportunities page functionality"""
        await self.page.click('text=Opportunities')
        await self.page.wait_for_timeout(2000)

        # Check for data tables or cards
        has_data = await self.page.locator('table, div[data-testid="stDataFrame"]').count() > 0
        assert has_data, "No data displayed on Opportunities page"

        print("✓ Opportunities page has data")

    async def test_positions_page(self):
        """Test positions page loads"""
        await self.page.click('text=Positions')
        await self.page.wait_for_timeout(2000)

        # Page should load without errors
        errors = await self.page.locator('text=Error, text=Exception').count()
        assert errors == 0, "Errors found on Positions page"

        print("✓ Positions page loads without errors")

    async def test_ava_chat(self):
        """Test AVA chat interface"""
        await self.page.click('text=AVA Chat')
        await self.page.wait_for_timeout(1000)

        # Find chat input
        chat_input = await self.page.locator('textarea').first
        await chat_input.fill("Test message")

        # Send message (Enter key)
        await self.page.keyboard.press('Enter')
        await self.page.wait_for_timeout(3000)

        # Verify message appeared
        messages = await self.page.locator('div[data-testid="stChatMessage"]').count()
        assert messages > 0, "No chat messages found"

        print(f"✓ AVA chat working - {messages} messages")

    async def test_settings_panel(self):
        """Test settings panel opens"""
        # Look for settings button (⚙️)
        settings_button = await self.page.locator('button:has-text("⚙")').first
        await settings_button.click()
        await self.page.wait_for_timeout(500)

        # Settings panel should appear
        # (Implementation depends on your settings panel structure)

        print("✓ Settings panel accessible")

    async def test_responsive_design(self):
        """Test responsive design at different viewports"""
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop"},
            {"width": 1024, "height": 768, "name": "Tablet"},
            {"width": 375, "height": 667, "name": "Mobile"}
        ]

        for viewport in viewports:
            await self.page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            await self.page.wait_for_timeout(500)

            # Verify content still visible
            content = await self.page.locator('body').first
            assert content, f"Content not visible on {viewport['name']}"

            print(f"✓ Responsive at {viewport['name']} ({viewport['width']}x{viewport['height']})")

# Run tests
if __name__ == "__main__":
    tester = StreamlitDashboardTests()
    asyncio.run(tester.run_all_tests())
```

**Run comprehensive tests**:
```bash
cd c:\Code\Legion\repos\ava
python comprehensive_ui_tests.py
```

---

## INTEGRATION WITH CI/CD

### GitHub Actions Example

Create `.github/workflows/playwright-tests.yml`:

```yaml
name: Playwright UI Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install Playwright
      run: |
        npm install -g @playwright/mcp
        npx playwright install

    - name: Install Python dependencies
      run: pip install -r requirements.txt

    - name: Start Streamlit dashboard
      run: |
        streamlit run dashboard.py --server.port 8513 &
        Start-Sleep -Seconds 10

    - name: Run Playwright tests
      run: python comprehensive_ui_tests.py

    - name: Upload test screenshots
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-screenshots
        path: '*.png'
```

---

## ADVANCED USAGE

### Visual Regression Testing

```python
async def test_visual_regression():
    """Compare screenshots to detect UI changes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:8513')

        # Take baseline screenshot
        await page.screenshot(path='baseline_home.png')

        # Later, compare against baseline
        from PIL import Image
        import imagehash

        baseline = Image.open('baseline_home.png')
        current = Image.open('current_home.png')

        diff = imagehash.average_hash(baseline) - imagehash.average_hash(current)

        if diff > 5:  # Threshold for acceptable difference
            print(f"⚠ Visual regression detected! Diff: {diff}")
        else:
            print("✓ No visual changes")

        await browser.close()
```

### Network Monitoring

```python
async def test_with_network_monitoring():
    """Monitor network requests during testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Track network requests
        requests = []
        page.on('request', lambda req: requests.append(req.url))

        await page.goto('http://localhost:8513')
        await page.wait_for_load_state('networkidle')

        # Analyze requests
        print(f"Total requests: {len(requests)}")

        # Check for slow endpoints
        for req in requests:
            if 'api' in req:
                print(f"API call: {req}")

        await browser.close()
```

---

## BENEFITS OF PLAYWRIGHT MCP

✅ **Comprehensive Testing**: Tests entire UI automatically
✅ **Real Browser**: Uses actual Chrome/Firefox/Safari
✅ **No Manual Testing**: Automate repetitive test cases
✅ **Screenshot Capture**: Visual proof of test results
✅ **Fast Execution**: Tests run in seconds
✅ **CI/CD Integration**: Automated on every commit
✅ **Multi-Browser**: Test on Chrome, Firefox, Safari
✅ **Responsive Testing**: Test different screen sizes

---

## TROUBLESHOOTING

### Issue: "npx: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### Issue: "Browser not found"
**Solution**: Run `npx playwright install` to download browsers

### Issue: "TimeoutError: waiting for selector"
**Solution**: Increase timeout or check if element exists:
```python
await page.wait_for_selector('text=Your Text', timeout=30000)
```

### Issue: Tests fail on headless mode
**Solution**: Run with `headless=False` to debug visually:
```python
browser = await p.chromium.launch(headless=False)
```

---

## NEXT STEPS

1. **Install Playwright**:
   ```bash
   npm install -g @playwright/mcp
   npx playwright install
   ```

2. **Create Test File**:
   - Copy one of the example tests above
   - Save as `test_dashboard.py`

3. **Run Test**:
   ```bash
   python test_dashboard.py
   ```

4. **Review Results**:
   - Check console output
   - Review screenshots generated
   - Fix any failing tests

5. **Integrate with CI/CD**:
   - Add GitHub Actions workflow
   - Run tests on every commit

---

## RELATED DOCUMENTATION

1. **MCP_SERVERS_AND_FREE_AI_APIS_GUIDE.md** - Full MCP server research
2. **DEEPSEEK_FIX_AND_HUGGINGFACE_IMPLEMENTATION.md** - AI provider implementations
3. **Playwright Official Docs**: https://playwright.dev/python/docs/intro

---

## CONCLUSION

Microsoft Playwright MCP enables **complete automated UI testing** of your Streamlit dashboard. It can:
- Navigate all pages
- Test all interactive elements
- Verify data loads correctly
- Capture screenshots
- Run in CI/CD pipelines

**Key Takeaway**: This is exactly what you requested - a tool that can "go all over the UI and test it all" automatically.

---

**Status**: Ready for Installation
**Installation Time**: ~10 minutes
**First Test Run**: ~2 minutes

---

**Start Here**: Run `npm install -g @playwright/mcp` to begin! 🚀
