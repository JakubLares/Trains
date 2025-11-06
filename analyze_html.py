#!/usr/bin/env python3
"""Analyze the HTML structure from selenium_debug.html"""

from bs4 import BeautifulSoup
import re

print("Analyzing selenium_debug.html...\n")

# Load the saved HTML
try:
    with open('selenium_debug.html', 'r', encoding='utf-8') as f:
        html = f.read()
except FileNotFoundError:
    print("❌ selenium_debug.html not found!")
    print("Run 'python test_selenium.py' first to generate it.")
    exit(1)

soup = BeautifulSoup(html, 'lxml')

# Find elements with times
times = re.findall(r'\b\d{1,2}:\d{2}\b', html)
print(f"✅ Found {len(times)} times total\n")

print("="*60)
print("HTML STRUCTURE")
print("="*60)
print(f"Tables: {len(soup.find_all('table'))}")
print(f"List items (li): {len(soup.find_all('li'))}")
print(f"Rows (tr): {len(soup.find_all('tr'))}")
print(f"Divs: {len(soup.find_all('div'))}")

print("\n" + "="*60)
print("SAMPLE ELEMENTS WITH TIMES")
print("="*60)

# Find all elements with times
elements_with_time = []
for elem in soup.find_all(['div', 'tr', 'li', 'td', 'span', 'p']):
    text = elem.get_text(strip=True)
    if re.search(r'\b\d{1,2}:\d{2}\b', text) and len(text) < 200:
        classes = ' '.join(elem.get('class', []))
        elements_with_time.append((elem.name, classes, text[:150]))

# Show first 15 unique patterns
seen = set()
count = 0
for tag, classes, text in elements_with_time[:100]:
    pattern = f"{tag}.{classes}"
    if pattern not in seen and count < 15:
        seen.add(pattern)
        print(f"\n{count+1}. <{tag} class='{classes}'>")
        print(f"   {text}")
        count += 1

print("\n" + "="*60)
print("STATION NAMES FOUND")
print("="*60)

stations = ['Ostrava', 'Praha', 'Brno', 'Olomouc', 'Pardubice', 'Přerov', 'Bohumín']
for station in stations:
    if station in html:
        print(f"✅ {station}")
        # Find the first occurrence and show surrounding HTML
        idx = html.find(station)
        start = max(0, idx - 200)
        end = min(len(html), idx + 200)
        snippet = html[start:end]

        # Parse this snippet
        snippet_soup = BeautifulSoup(snippet, 'lxml')
        # Find the element containing the station
        for elem in snippet_soup.find_all(string=re.compile(station)):
            parent = elem.parent
            print(f"   In: <{parent.name} class='{' '.join(parent.get('class', []))}'>")
            break
    else:
        print(f"❌ {station} not found")

print("\n" + "="*60)
print("LOOKING FOR SCHEDULE TABLE/LIST")
print("="*60)

# Try to find the main schedule container
# Look for elements with multiple time entries
containers = []
for elem in soup.find_all(['table', 'ul', 'ol', 'div']):
    text = elem.get_text()
    time_count = len(re.findall(r'\b\d{1,2}:\d{2}\b', text))
    if time_count >= 5:  # Has at least 5 times
        classes = ' '.join(elem.get('class', []))
        elem_id = elem.get('id', '')
        containers.append((elem.name, classes, elem_id, time_count))

containers.sort(key=lambda x: x[3], reverse=True)
print(f"\nFound {len(containers)} containers with 5+ times:\n")
for i, (tag, classes, elem_id, count) in enumerate(containers[:5], 1):
    print(f"{i}. <{tag} class='{classes}' id='{elem_id}'> - {count} times")

print("\n✅ Analysis complete!")
print("\nNext: Look at the output above and identify the pattern for station/time data")
