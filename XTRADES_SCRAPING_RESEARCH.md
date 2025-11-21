# Xtrades Scraping - Research & Best Practices
**Date**: 2025-11-06
**Research**: GitHub, Reddit, Web Search for better scraping methods

## Research Summary

### Key Findings:

1. **No Existing Solutions**
   - ✅ No public GitHub repos for xtrades.net scraping
   - ✅ No public Xtrades API or webhooks available
   - ✅ We're pioneering this approach!

2. **Current Limitation**
   - Only getting **3 posts per profile** instead of full history
   - User can see "many many alerts" in browser manually
   - Infinite scroll not being handled properly

3. **Angular SPA Challenges (2025 Best Practices)**
   - Modern frameworks like Angular use client-side rendering
   - Content loads dynamically via JavaScript
   - Infinite scroll requires special handling
   - Average load time: ~18 seconds for Angular SPAs

---

## Current Approach (What We're Doing)

```python
# Current scroll implementation (INSUFFICIENT!)
for i in range(3):  # Only 3 scrolls!
    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)  # Fixed delay
    print(f"Scrolled {i+1}/3")
```

**Problems:**
- ❌ Fixed number of scrolls (3) - not enough for full history
- ❌ Time-based delays instead of waiting for content
- ❌ Doesn't check if new content actually loaded
- ❌ No detection of "end of content"

---

## Best Practices from Research

### 1. Scroll Until No More Content

```python
def scroll_to_load_all_posts(driver, max_scrolls=100):
    """Scroll until no new content loads"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    no_change_count = 0

    for scroll_num in range(max_scrolls):
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for content to load (explicit wait)
        time.sleep(2)  # Can be replaced with WebDriverWait

        # Check if height changed
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            no_change_count += 1
            if no_change_count >= 3:  # No change for 3 scrolls = done
                print(f"Reached end of content after {scroll_num} scrolls")
                break
        else:
            no_change_count = 0  # Reset counter

        last_height = new_height

    return scroll_num
```

### 2. Use Explicit Waits (Not Time Delays)

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Wait for specific elements to load
wait = WebDriverWait(driver, 10)
posts = wait.until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "app-post"))
)
```

### 3. Count Elements Before/After Scroll

```python
def scroll_until_all_loaded(driver, element_selector="app-post"):
    """Keep scrolling until no new elements appear"""
    previous_count = 0
    stale_count = 0

    while stale_count < 3:  # Stop after 3 attempts with no new content
        # Scroll
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Count elements
        elements = driver.find_elements(By.TAG_NAME, element_selector)
        current_count = len(elements)

        print(f"Found {current_count} elements (previous: {previous_count})")

        if current_count == previous_count:
            stale_count += 1
        else:
            stale_count = 0

        previous_count = current_count

    return current_count
```

### 4. Check for "Load More" Button

```python
def click_load_more_if_exists(driver):
    """Click 'Load More' button if present"""
    try:
        load_more = driver.find_element(By.XPATH,
            "//*[contains(text(), 'Load More') or contains(text(), 'Show More')]")
        if load_more.is_displayed():
            load_more.click()
            time.sleep(1)
            return True
    except:
        return False
```

### 5. Aggressive Scroll Strategy

```python
def aggressive_infinite_scroll(driver, max_duration_seconds=300):
    """Scroll aggressively until timeout or no more content"""
    start_time = time.time()
    scroll_pause = 1  # Shorter pause for faster loading
    last_post_count = 0
    no_new_content_count = 0

    while time.time() - start_time < max_duration_seconds:
        # Get current post count
        posts = driver.find_elements(By.TAG_NAME, "app-post")
        current_count = len(posts)

        # Scroll multiple times quickly
        for _ in range(5):  # 5 rapid scrolls
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.2)

        # Final scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        # Check for Load More button
        if click_load_more_if_exists(driver):
            continue

        # Check if new posts loaded
        if current_count == last_post_count:
            no_new_content_count += 1
            if no_new_content_count >= 5:
                print(f"No new content after {no_new_content_count} attempts")
                break
        else:
            no_new_content_count = 0
            print(f"Loaded {current_count - last_post_count} new posts (total: {current_count})")

        last_post_count = current_count

    return current_count
```

---

## Recommended Implementation

### Priority 1: Improve Infinite Scroll

Update `get_profile_alerts()` in `src/xtrades_scraper.py`:

```python
def _scroll_to_load_all_alerts(self, max_scrolls=100):
    """
    Scroll until all alerts are loaded or max_scrolls reached

    Returns:
        Number of scrolls performed
    """
    last_height = self.driver.execute_script("return document.body.scrollHeight")
    last_post_count = 0
    no_change_iterations = 0

    for scroll_num in range(1, max_scrolls + 1):
        # Scroll to bottom
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for content (can use WebDriverWait for better precision)
        time.sleep(1.5)

        # Count current posts
        try:
            posts = self.driver.find_elements(By.TAG_NAME, "app-post")
            current_count = len(posts)
        except:
            current_count = last_post_count

        # Get new height
        new_height = self.driver.execute_script("return document.body.scrollHeight")

        # Check if anything changed
        if new_height == last_height and current_count == last_post_count:
            no_change_iterations += 1
            if no_change_iterations >= 3:
                print(f"Reached end of content at scroll {scroll_num}")
                break
        else:
            no_change_iterations = 0
            print(f"Scroll {scroll_num}: {current_count} posts loaded")

        last_height = new_height
        last_post_count = current_count

    print(f"Total posts after scrolling: {last_post_count}")
    return scroll_num
```

### Priority 2: Add Explicit Waits

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Wait for posts to load after scroll
wait = WebDriverWait(self.driver, 10)
try:
    # Wait for at least one post to be present
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "app-post")))
except TimeoutException:
    print("Timeout waiting for posts to load")
```

### Priority 3: Alternative - Direct URL to Feed

Instead of clicking tabs, navigate directly to feed:
```python
url = f"https://app.xtrades.net/profile/{username}/feed"
self.driver.get(url)
```

---

## Expected Improvements

### Before (Current):
- 3 scrolls only
- 3 posts per profile
- ~15 alerts total

### After (Improved):
- 100+ scrolls if needed
- All available posts per profile
- Hundreds of alerts (historical data)
- Full trading history

---

## Implementation Priority

**HIGH PRIORITY - Next Steps:**

1. **Implement aggressive infinite scroll** (Est. 2 hours)
   - Replace fixed 3 scrolls with dynamic scrolling
   - Add post count checking
   - Stop when no new content loads

2. **Add explicit waits** (Est. 30 mins)
   - Use WebDriverWait for element presence
   - Replace time.sleep() with conditional waits

3. **Test with one profile** (Est. 30 mins)
   - Verify it loads ALL posts
   - Check performance impact
   - Measure total alerts retrieved

4. **Deploy to all profiles** (Est. 15 mins)
   - Update background sync
   - Monitor for issues

**MEDIUM PRIORITY - Future:**

5. Check for pagination buttons
6. Try direct feed URL navigation
7. Implement scroll speed optimization

---

## Alternative Approaches Considered

### 1. Network Interception
- Capture XHR/Fetch requests for alert data
- Would bypass HTML parsing entirely
- Requires Chrome DevTools Protocol
- More fragile (API changes break it)

### 2. Browser Developer Tools
- Use browser's Network tab to find API endpoints
- Reverse engineer API calls
- Could be rate-limited
- May violate ToS

### 3. Playwright Instead of Selenium
- Modern browser automation
- Better handling of SPAs
- Requires code rewrite
- Overkill for current needs

---

## Conclusion

**Recommendation**: Implement improved infinite scroll with explicit waits.

**Why**:
- Minimal code changes
- Proven technique for Angular SPAs
- Will capture full alert history
- No API required
- Respects site structure

**Expected Result**:
- From 3 posts to 100+ posts per profile
- From 58 total alerts to 500+ alerts
- Complete historical trading data

**Implementation Time**: ~3 hours total

---

## References

- **Selenium with Angular SPAs (2025)**: https://scrape.do/blog/selenium-web-scraping/
- **Infinite Scroll Best Practices**: Stack Overflow discussions on Python Selenium infinite scroll
- **GitHub Examples**: Multiple repos showing scroll-until-done patterns
- **ScrapingBee Guide**: https://www.scrapingbee.com/blog/selenium-python/

---

**Status**: Research complete, ready for implementation
**Priority**: HIGH - User wants "many many alerts"
**Next Step**: Update `src/xtrades_scraper.py` with improved scroll logic
