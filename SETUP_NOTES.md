# Setup Notes - Important Information

## CD.cz Website Blocking

**Important:** The České dráhy website (cd.cz) blocks automated scraping attempts with 403 Forbidden errors. This is a common anti-scraping protection.

### Solutions

There are several approaches to work around this:

### Option 1: Use Selenium (Automated Browser)

The app includes Selenium support as a fallback. This uses a real Chrome browser to fetch data.

**Requirements:**
- Google Chrome or Chromium installed
- Additional Python packages (already in requirements.txt)

**Installation:**

```bash
# Install additional dependencies
pip install selenium webdriver-manager

# On Linux, install Chrome/Chromium:
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# Or Chrome:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

The app will automatically try Selenium if regular requests fail.

### Option 2: Manual URL Update

Since CD.cz might be blocking automated requests, you can:

1. **Manually check delays** on cd.cz website
2. Update the config with today's date/URL before train departure
3. Run the app - it will work with cached/manual data

### Option 3: Use Alternative Data Sources

Other websites that might be easier to scrape:
- `kdypojedevlak.cz` - Czech train tracking
- `zugfinder.net` - International train delays
- Mobile app APIs (unofficial)

You could modify `train_fetcher.py` to use these sources instead.

### Option 4: Wait for Official API

České dráhy is working on public APIs. When available, the app can be updated to use official endpoints instead of scraping.

## Current Status

As of November 2025:
- ✅ App structure is complete and working
- ✅ Notification system works
- ✅ Monitoring logic works
- ⚠️  CD.cz blocks automated requests
- ⚠️  Selenium fallback available but requires Chrome

## Testing Without CD.cz

You can test the app's functionality without actually fetching from CD.cz:

1. **Test notifications:**
   ```bash
   python main.py --test-notifications
   ```

2. **Test with mock data:**
   Edit `train_fetcher.py` and create a mock response for testing

## Recommended Approach

For **actual use**, the best current options are:

1. **Option A - Use Selenium:**
   - Install Chrome/Chromium
   - Install selenium packages
   - App will use real browser to fetch data
   - Slower but works

2. **Option B - Monitor manually:**
   - Check CD.cz mobile app manually
   - Use this app just for notification timing
   - Update delays in config file

3. **Option C - Wait for API:**
   - Watch for official CD.cz API announcement
   - Update app when available

## Alternative: Use CD Mobile App

The official "Můj vlak" (My Train) mobile app from České dráhy already provides:
- Real-time train tracking
- Delay notifications
- Push notifications

You might want to use that instead while waiting for an official API.

## Contributing

If you find a working method to fetch CD.cz data programmatically, please contribute!

## Legal Note

Web scraping may violate CD.cz terms of service. This tool is for educational/personal use only. For production use, contact České dráhy for API access.
