#!/usr/bin/env python3
"""Check for delay information in the HTML"""

from bs4 import BeautifulSoup
import re

print("Looking for delay information in selenium_debug.html...\n")

with open('selenium_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

print("="*60)
print("SEARCHING FOR DELAY KEYWORDS")
print("="*60)

# Look for delay-related text
delay_keywords = ['zpoždění', 'zpožděn', 'delay', 'Připočítat zpoždění', 'potvrzené zpoždění']

for keyword in delay_keywords:
    if keyword in html:
        print(f"\n✅ Found: '{keyword}'")

        # Find context around this keyword
        idx = html.find(keyword)
        start = max(0, idx - 150)
        end = min(len(html), idx + 150)
        snippet = html[start:end]

        # Show cleaned up version
        snippet_soup = BeautifulSoup(snippet, 'lxml')
        text = snippet_soup.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"  Context: {' / '.join(lines[:5])}")

print("\n" + "="*60)
print("ANALYZING STATION ELEMENTS FOR DELAY INFO")
print("="*60)

# Find the train schedule
schedule = soup.find('ul', class_='train-schedule')
if schedule:
    stations = schedule.find_all('li', class_='train-schedule__item')

    print(f"\nChecking all {len(stations)} stations for delay information:\n")

    for i, station in enumerate(stations, 1):
        name_elem = station.find('h3', class_='train-schedule__station-title')
        name = name_elem.get_text(strip=True) if name_elem else "Unknown"

        full_text = station.get_text()

        # Look for any delay patterns
        delay_patterns = [
            r'zpoždění[:\s]*(\+)?(\d+)\s*min',
            r'zpožděn[ío][:\s]*(\+)?(\d+)\s*min',
            r'(\+|\-)(\d+)\s*min',
            r'potvrzené zpoždění[:\s]*(\d+)',
        ]

        found_delay = False
        for pattern in delay_patterns:
            match = re.search(pattern, full_text, re.I)
            if match:
                print(f"{i}. {name}")
                print(f"   Pattern: {pattern}")
                print(f"   Match: {match.group(0)}")
                found_delay = True
                break

        # Also check HTML for data attributes that might contain delay
        if station.get('data-delay'):
            print(f"{i}. {name} - data-delay: {station.get('data-delay')}")
            found_delay = True

        # Check for delay CSS classes
        classes = ' '.join(station.get('class', []))
        if 'delay' in classes.lower():
            print(f"{i}. {name} - delay class: {classes}")
            found_delay = True

print("\n" + "="*60)
print("LOOKING FOR 'Připočítat zpoždění' BUTTON")
print("="*60)

# Find the button
button = soup.find(string=re.compile(r'Připočítat zpoždění', re.I))
if button:
    print("\n✅ Found 'Připočítat zpoždění' button!")
    parent = button.parent
    for _ in range(3):  # Go up a few levels
        print(f"\n  Parent: <{parent.name} class='{' '.join(parent.get('class', []))}'>")
        if parent.get('onclick'):
            print(f"  onclick: {parent.get('onclick')}")
        if parent.get('data-bind'):
            print(f"  data-bind: {parent.get('data-bind')}")
        parent = parent.parent
        if parent is None:
            break
else:
    print("\n❌ Button not found")

print("\n" + "="*60)
print("CHECKING FOR JAVASCRIPT/AJAX DELAY DATA")
print("="*60)

# Look for JavaScript variables or AJAX endpoints
js_patterns = [
    r'delay["\']?\s*:\s*\d+',
    r'zpozdeni["\']?\s*:\s*\d+',
    r'\/api\/.*delay',
]

for pattern in js_patterns:
    matches = re.findall(pattern, html, re.I)
    if matches:
        print(f"\n✅ Pattern '{pattern}':")
        for match in matches[:5]:
            print(f"  {match}")
