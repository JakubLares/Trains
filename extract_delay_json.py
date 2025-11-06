#!/usr/bin/env python3
"""Extract JSON delay data from the HTML"""

from bs4 import BeautifulSoup
import re
import json

print("Extracting JSON delay data from selenium_debug.html...\n")

with open('selenium_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("="*60)
print("LOOKING FOR JSON DATA WITH DELAY INFO")
print("="*60)

# Look for JavaScript objects/arrays that contain delay and station info
# Common patterns in CD.cz:
# - var trainData = {...}
# - ko.applyBindings({...})
# - JSON embedded in <script> tags

soup = BeautifulSoup(html, 'lxml')

# Find all script tags
scripts = soup.find_all('script')
print(f"\nFound {len(scripts)} script tags\n")

for i, script in enumerate(scripts):
    script_text = script.string
    if script_text and 'delay' in script_text.lower():
        print(f"\nScript {i+1} contains 'delay':")
        print("-" * 60)

        # Look for JSON-like structures
        # Try to find objects with delay property
        json_patterns = [
            r'\{[^{}]*"delay"\s*:\s*\d+[^{}]*\}',
            r'\{[^{}]*delay\s*:\s*\d+[^{}]*\}',
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, script_text)
            if matches:
                print(f"\nFound {len(matches)} JSON objects with delay:")
                for j, match in enumerate(matches[:5], 1):
                    print(f"\n{j}. {match[:200]}")

        # Also look for arrays of station objects
        # Pattern: [{...}, {...}, ...]
        array_match = re.search(r'(\[\s*\{[^\]]{100,}\}\s*\])', script_text)
        if array_match:
            print("\n" + "="*60)
            print("FOUND ARRAY OF OBJECTS - This might be station data!")
            print("="*60)
            array_text = array_match.group(1)

            # Try to clean and parse it
            # Remove comments and trailing commas
            cleaned = re.sub(r'//.*', '', array_text)
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

            # Show a sample
            print(f"\nSample (first 500 chars):")
            print(array_text[:500])

            # Try to extract just the first object to see structure
            first_obj_match = re.search(r'\{[^{}]*?\}', array_text)
            if first_obj_match:
                print(f"\nFirst object structure:")
                print(first_obj_match.group(0))

print("\n" + "="*60)
print("SEARCHING FOR KNOCKOUT.JS DATA BINDING")
print("="*60)

# CD.cz uses Knockout.js, look for the data model
# Pattern: ko.applyBindings(dataModel, element)
ko_match = re.search(r'ko\.applyBindings\s*\(\s*(\{[\s\S]*?\})\s*(?:,|\))', html)
if ko_match:
    print("\n✅ Found ko.applyBindings with data model")
    model_text = ko_match.group(1)
    print(f"\nData model (first 500 chars):")
    print(model_text[:500])
else:
    print("\n❌ No ko.applyBindings found")

# Alternative: look for variable assignments that might contain train data
var_patterns = [
    r'var\s+trainData\s*=\s*(\{[\s\S]*?\});',
    r'var\s+stations\s*=\s*(\[[\s\S]*?\]);',
    r'const\s+trainData\s*=\s*(\{[\s\S]*?\});',
]

for pattern in var_patterns:
    match = re.search(pattern, html)
    if match:
        print(f"\n✅ Found pattern: {pattern}")
        data_text = match.group(1)
        print(f"Data (first 300 chars):")
        print(data_text[:300])

print("\n" + "="*60)
print("LOOKING FOR INLINE DATA ATTRIBUTES")
print("="*60)

# Sometimes data is in data-* attributes
schedule = soup.find('ul', class_='train-schedule')
if schedule:
    # Check if parent has data attributes
    parent = schedule.parent
    for _ in range(3):
        if parent:
            data_attrs = {k: v for k, v in parent.attrs.items() if k.startswith('data-')}
            if data_attrs:
                print(f"\n<{parent.name}> has data attributes:")
                for k, v in data_attrs.items():
                    print(f"  {k}: {v[:100]}")
            parent = parent.parent
