#!/usr/bin/env python3
"""Analyze the list items to see station data structure"""

from bs4 import BeautifulSoup
import re

print("Analyzing list items in selenium_debug.html...\n")

with open('selenium_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

# Find all list items
all_lis = soup.find_all('li')
print(f"Total <li> elements: {len(all_lis)}\n")

print("="*60)
print("LIST ITEMS WITH TIME PATTERNS")
print("="*60)

count = 0
for i, li in enumerate(all_lis):
    text = li.get_text(strip=True)

    # Check if this li contains a time
    if re.search(r'\b\d{1,2}:\d{2}\b', text):
        count += 1
        if count <= 20:  # Show first 20
            classes = ' '.join(li.get('class', []))

            print(f"\n{count}. <li class='{classes}'>")

            # Show child structure
            children = list(li.children)
            print(f"   Children: {len(children)}")

            # Show text content (truncated)
            if len(text) < 200:
                print(f"   Text: {text}")
            else:
                print(f"   Text: {text[:200]}...")

            # Show HTML structure
            inner_html = str(li)[:500]
            print(f"   HTML: {inner_html}...")

print(f"\n\nTotal list items with times: {count}")

print("\n" + "="*60)
print("LOOKING FOR STATION LIST CONTAINER")
print("="*60)

# Find parent of these list items
for ul in soup.find_all(['ul', 'ol']):
    lis_with_times = [li for li in ul.find_all('li') if re.search(r'\b\d{1,2}:\d{2}\b', li.get_text())]

    if len(lis_with_times) >= 5:
        classes = ' '.join(ul.get('class', []))
        elem_id = ul.get('id', '')
        print(f"\n<{ul.name} class='{classes}' id='{elem_id}'>")
        print(f"  Contains {len(lis_with_times)} list items with times")

        # Show structure of first item
        if lis_with_times:
            first_li = lis_with_times[0]
            print(f"\n  Sample item:")
            print(f"  {str(first_li)[:400]}")
