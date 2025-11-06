#!/usr/bin/env python3
"""Show the full structure of station list items"""

from bs4 import BeautifulSoup

print("Analyzing train-schedule structure...\n")

with open('selenium_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Find the train schedule
schedule = soup.find('ul', class_='train-schedule')

if schedule:
    stations = schedule.find_all('li', class_='train-schedule__item')
    print(f"✅ Found {len(stations)} stations\n")
    print("="*60)

    # Show first 3 stations in detail
    for i, station in enumerate(stations[:3], 1):
        print(f"\nSTATION {i}:")
        print("="*60)

        # Get station name
        name_elem = station.find('h3', class_='train-schedule__station-title')
        if name_elem:
            print(f"Name: {name_elem.get_text(strip=True)}")

        # Get all text
        full_text = station.get_text(strip=True)
        print(f"\nFull text:\n{full_text[:300]}")

        # Show HTML structure (more complete)
        html_str = str(station)
        print(f"\nHTML structure:\n{html_str[:800]}")
        print("...")

    print("\n" + "="*60)
    print("Last 3 stations:")
    print("="*60)

    # Show last 3 stations (including Praha hopefully)
    for i, station in enumerate(stations[-3:], len(stations)-2):
        print(f"\nSTATION {i}:")
        name_elem = station.find('h3', class_='train-schedule__station-title')
        if name_elem:
            print(f"Name: {name_elem.get_text(strip=True)}")
        full_text = station.get_text(strip=True)
        print(f"Text: {full_text[:200]}")

else:
    print("❌ Could not find <ul class='train-schedule'>")
