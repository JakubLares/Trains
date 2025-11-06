"""
Train Data Fetcher
Fetches train schedule and delay information from České dráhy (CD.cz)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
import logging
import time

# Selenium imports (optional, for fallback)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available, will only use requests")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainFetcher:
    """Fetches and parses train information from CD.cz"""

    def __init__(self, use_selenium=True):
        """
        Initialize train fetcher

        Args:
            use_selenium: True/False to force selenium on/off, None for auto (fallback)
                         Default: True (CD.cz blocks simple requests)
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        # Set headers to mimic a real browser to avoid 403 errors
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'cs,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.cd.cz/',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        })
        self.driver = None

    def fetch_train_data(self, url: str) -> Optional[Dict]:
        """
        Fetch train data from CD.cz URL

        Args:
            url: CD.cz train URL (e.g., https://www.cd.cz/vlak/140/6.11.2025/...)

        Returns:
            Dictionary with train information including delays
        """
        # Determine method
        use_selenium_now = self.use_selenium

        if use_selenium_now is None:
            # Auto mode: try requests first, fallback to selenium
            html_content = self._fetch_with_requests(url)
            if html_content is None and SELENIUM_AVAILABLE:
                logger.info("Requests failed, trying with Selenium...")
                html_content = self._fetch_with_selenium(url)
        elif use_selenium_now and SELENIUM_AVAILABLE:
            # Force selenium
            html_content = self._fetch_with_selenium(url)
        else:
            # Force requests
            html_content = self._fetch_with_requests(url)

        if html_content is None:
            logger.error("Failed to fetch train data with all methods")
            return None

        try:
            soup = BeautifulSoup(html_content, 'lxml')
            train_data = self._parse_train_page(soup, url)
            return train_data
        except Exception as e:
            logger.error(f"Error parsing train data: {e}")
            return None

    def _fetch_with_requests(self, url: str) -> Optional[str]:
        """Fetch page using requests library"""
        try:
            logger.info(f"Fetching with requests: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Requests method failed: {e}")
            return None

    def _fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch page using Selenium (real browser)"""
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available")
            return None

        try:
            logger.info(f"Fetching with Selenium: {url}")

            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Create driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            try:
                # Load page
                driver.get(url)

                # Wait for page to load (wait for any content with times)
                time.sleep(3)  # Give page time to load

                # Get page source
                html_content = driver.page_source

                logger.info("Successfully fetched page with Selenium")
                return html_content

            finally:
                driver.quit()

        except Exception as e:
            logger.error(f"Selenium method failed: {e}")
            return None

    def _parse_train_page(self, soup: BeautifulSoup, url: str) -> Dict:
        """Parse the train page HTML to extract relevant information"""

        # Extract train number from URL
        train_number = self._extract_train_number(url)

        # Find all stations and times
        stations = []

        # CD.cz uses <ul class='train-schedule'> with <li class='train-schedule__item'>
        schedule_list = soup.find('ul', class_='train-schedule')

        if schedule_list:
            logger.info("Found train-schedule list")
            station_elements = schedule_list.find_all('li', class_='train-schedule__item')
            logger.info(f"Found {len(station_elements)} station elements")

            for elem in station_elements:
                station_info = self._parse_cd_station_element(elem)
                if station_info:
                    stations.append(station_info)
        else:
            logger.warning("Could not find train-schedule list, trying fallback")
            # Fallback to old method
            station_elements = self._find_time_elements(soup)
            for elem in station_elements:
                station_info = self._parse_station_element(elem)
                if station_info:
                    stations.append(station_info)

        # Extract train name/title
        train_name = self._extract_train_name(soup)

        train_data = {
            'train_number': train_number,
            'train_name': train_name,
            'url': url,
            'stations': stations,
            'fetched_at': datetime.now().isoformat(),
        }

        logger.info(f"Parsed {len(stations)} stations for train {train_number}")
        return train_data

    def _extract_train_number(self, url: str) -> str:
        """Extract train number from URL"""
        # URL format: https://www.cd.cz/vlak/140/...
        match = re.search(r'/vlak/(\d+)/', url)
        return match.group(1) if match else 'unknown'

    def _extract_train_name(self, soup: BeautifulSoup) -> str:
        """Extract train name from page"""
        # Look for common patterns for train name
        title = soup.find('h1')
        if title:
            return title.get_text(strip=True)

        # Try meta tags
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '')

        return ''

    def _find_time_elements(self, soup: BeautifulSoup) -> List:
        """Fallback method to find elements containing time information"""
        # Look for patterns like HH:MM
        time_pattern = re.compile(r'\d{1,2}[:.]\d{2}')
        elements = []

        for elem in soup.find_all(['div', 'tr', 'td', 'span']):
            text = elem.get_text()
            if time_pattern.search(text):
                elements.append(elem)

        return elements[:50]  # Limit to avoid too many elements

    def _parse_cd_station_element(self, elem) -> Optional[Dict]:
        """Parse a CD.cz train-schedule__item element"""
        try:
            # Extract station name from h3.train-schedule__station-title
            name_elem = elem.find('h3', class_='train-schedule__station-title')
            if not name_elem:
                return None

            station_name = name_elem.get_text(strip=True)

            # Get full text to extract times
            full_text = elem.get_text(strip=True)

            # Extract arrival time (PŘÍJEZD followed by time)
            arrival_time = None
            arrival_match = re.search(r'PŘÍJEZD\s*(\d{1,2}):(\d{2})', full_text)
            if arrival_match:
                arrival_time = f"{arrival_match.group(1).zfill(2)}:{arrival_match.group(2)}"

            # Extract departure time (ODJEZD followed by time)
            departure_time = None
            departure_match = re.search(r'ODJEZD\s*(\d{1,2}):(\d{2})', full_text)
            if departure_match:
                departure_time = f"{departure_match.group(1).zfill(2)}:{departure_match.group(2)}"

            # Look for delay information (zpoždění +X min)
            delay_minutes = 0
            delay_match = re.search(r'zpoždění\s*(\+|\-)?(\d+)\s*min', full_text, re.I)
            if delay_match:
                sign = -1 if delay_match.group(1) == '-' else 1
                delay_minutes = sign * int(delay_match.group(2))

            # Also check for standalone delay pattern
            if delay_minutes == 0:
                delay_match = re.search(r'(\+|\-)(\d+)\s*min', full_text)
                if delay_match:
                    sign = -1 if delay_match.group(1) == '-' else 1
                    delay_minutes = sign * int(delay_match.group(2))

            return {
                'name': station_name,
                'arrival': arrival_time,
                'departure': departure_time,
                'delay_minutes': delay_minutes,
                'raw_text': full_text[:200]  # Keep some raw text for debugging
            }

        except Exception as e:
            logger.debug(f"Could not parse CD.cz station element: {e}")
            return None

    def _parse_station_element(self, elem) -> Optional[Dict]:
        """Parse a single station element to extract station info (fallback method)"""
        try:
            text = elem.get_text(strip=True)

            # Extract station name (usually the longest non-time text)
            # Extract times (format: HH:MM or HH.MM)
            time_pattern = re.compile(r'(\d{1,2})[:.:](\d{2})')
            times = time_pattern.findall(text)

            # Extract station name (remove times and common keywords)
            station_name = re.sub(r'\d{1,2}[:.]\d{2}', '', text)
            station_name = re.sub(r'(příjezd|odjezd|arrival|departure|delay|zpoždění)', '', station_name, flags=re.I)
            station_name = station_name.strip()

            # Look for delay information
            delay_match = re.search(r'(\+|\-)?(\d+)\s*(min|minut)', text, re.I)
            delay_minutes = 0
            if delay_match:
                sign = -1 if delay_match.group(1) == '-' else 1
                delay_minutes = sign * int(delay_match.group(2))

            if not station_name or not times:
                return None

            # Determine arrival and departure times
            arrival_time = None
            departure_time = None

            if len(times) >= 2:
                arrival_time = f"{times[0][0].zfill(2)}:{times[0][1]}"
                departure_time = f"{times[1][0].zfill(2)}:{times[1][1]}"
            elif len(times) == 1:
                # If only one time, it could be either arrival or departure
                time_str = f"{times[0][0].zfill(2)}:{times[0][1]}"
                if 'příjezd' in text.lower() or 'arrival' in text.lower():
                    arrival_time = time_str
                else:
                    departure_time = time_str

            return {
                'name': station_name,
                'arrival': arrival_time,
                'departure': departure_time,
                'delay_minutes': delay_minutes,
                'raw_text': text[:200]  # Keep some raw text for debugging
            }

        except Exception as e:
            logger.debug(f"Could not parse station element: {e}")
            return None

    def get_arrival_time_at_station(self, train_data: Dict, station_name: str) -> Optional[Dict]:
        """
        Get the arrival time at a specific station including delays

        Args:
            train_data: Train data dictionary from fetch_train_data
            station_name: Name of the destination station (partial match ok)

        Returns:
            Dictionary with scheduled and actual arrival time
        """
        if not train_data or 'stations' not in train_data:
            return None

        station_name_lower = station_name.lower()

        for station in train_data['stations']:
            if station_name_lower in station['name'].lower():
                if not station.get('arrival'):
                    continue

                # Parse scheduled arrival time
                try:
                    arrival_str = station['arrival']
                    hours, minutes = map(int, arrival_str.split(':'))

                    # Get today's date (or use date from URL if available)
                    today = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)

                    # Calculate actual arrival with delay
                    delay = station.get('delay_minutes', 0)
                    actual_arrival = today + timedelta(minutes=delay)

                    return {
                        'station': station['name'],
                        'scheduled_arrival': today,
                        'delay_minutes': delay,
                        'actual_arrival': actual_arrival,
                    }
                except Exception as e:
                    logger.error(f"Error parsing arrival time: {e}")
                    return None

        logger.warning(f"Station '{station_name}' not found in train data")
        return None


def main():
    """Test the fetcher"""
    fetcher = TrainFetcher()

    # Test URL
    test_url = "https://www.cd.cz/vlak/140/6.11.2025/5617915/14.34/5457076/19.36/"

    print(f"Fetching train data from: {test_url}")
    train_data = fetcher.fetch_train_data(test_url)

    if train_data:
        print(f"\nTrain: {train_data.get('train_name', 'N/A')}")
        print(f"Number: {train_data.get('train_number', 'N/A')}")
        print(f"Stations found: {len(train_data.get('stations', []))}")

        print("\nStations:")
        for station in train_data.get('stations', [])[:10]:  # Show first 10
            print(f"  {station['name']}")
            if station['arrival']:
                print(f"    Arrival: {station['arrival']}", end='')
                if station['delay_minutes']:
                    print(f" (delay: {station['delay_minutes']:+d} min)", end='')
                print()
            if station['departure']:
                print(f"    Departure: {station['departure']}")

        # Test getting arrival at Praha
        print("\n" + "="*50)
        arrival_info = fetcher.get_arrival_time_at_station(train_data, "Praha")
        if arrival_info:
            print(f"\nArrival at {arrival_info['station']}:")
            print(f"  Scheduled: {arrival_info['scheduled_arrival'].strftime('%H:%M')}")
            print(f"  Delay: {arrival_info['delay_minutes']:+d} minutes")
            print(f"  Actual arrival: {arrival_info['actual_arrival'].strftime('%H:%M')}")
    else:
        print("Failed to fetch train data")


if __name__ == '__main__':
    main()
