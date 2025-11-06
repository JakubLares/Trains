#!/usr/bin/env python3
"""
Test Selenium fetching for CD.cz
"""

import sys

print("Testing Selenium setup...\n")

# Check if selenium is available
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    print("✅ Selenium is installed")
except ImportError as e:
    print(f"❌ Selenium not installed: {e}")
    print("\nInstall with: pip install selenium webdriver-manager")
    sys.exit(1)

# Try to fetch the page
print("\nAttempting to fetch train page with Selenium...")
print("This will download ChromeDriver if needed (one-time only)...")

try:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("\nStarting Chrome browser...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://www.cd.cz/vlak/140/6.11.2025/5617915/14.34/5457076/19.36/"
    print(f"Loading: {url}")

    driver.get(url)

    import time
    time.sleep(3)  # Wait for page to load

    html = driver.page_source
    driver.quit()

    print(f"\n✅ Successfully fetched page ({len(html)} bytes)")

    # Check if we got real content
    if "Access denied" in html:
        print("❌ Still getting 'Access denied' - website may have additional blocking")
    elif len(html) < 1000:
        print("⚠️  Page seems too short, might not have loaded properly")
    else:
        print("✅ Page looks good!")

        # Quick check for station data
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'lxml')

        # Look for time patterns (HH:MM)
        import re
        times = re.findall(r'\b\d{1,2}:\d{2}\b', html)
        print(f"\nFound {len(times)} time entries: {times[:10]}")

        # Save for inspection
        with open('selenium_debug.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("\n📄 Full HTML saved to selenium_debug.html for inspection")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure Chrome or Chromium is installed:")
    print("  brew install --cask google-chrome")
    print("  or")
    print("  brew install --cask chromium")
    sys.exit(1)

print("\n" + "="*60)
print("✅ Selenium setup is working!")
print("="*60)
