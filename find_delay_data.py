#!/usr/bin/env python3
"""Find the exact location of delay data"""

from bs4 import BeautifulSoup
import re
import json

print("Finding delay data in selenium_debug.html...\n")

with open('selenium_debug.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')

print("="*60)
print("SEARCHING FOR 'delay\":12' PATTERN")
print("="*60)

# Find all occurrences of delay":NUMBER
delay_matches = re.finditer(r'"delay"\s*:\s*(\d+)', html)

positions = []
for match in delay_matches:
    delay_value = match.group(1)
    position = match.start()
    positions.append((position, delay_value))

print(f"\nFound {len(positions)} delay values:")
for pos, val in positions:
    print(f"  Position {pos}: delay = {val} minutes")

if positions:
    # Show context around the first delay
    pos, val = positions[0]
    start = max(0, pos - 500)
    end = min(len(html), pos + 500)
    context = html[start:end]

    print("\n" + "="*60)
    print(f"CONTEXT AROUND FIRST DELAY (delay={val})")
    print("="*60)
    print(context)

    # Try to extract the complete JSON object containing this delay
    print("\n" + "="*60)
    print("EXTRACTING COMPLETE OBJECT")
    print("="*60)

    # Find the start of the object (look backwards for {)
    obj_start = pos
    brace_count = 0
    while obj_start > 0:
        if html[obj_start] == '}':
            brace_count += 1
        elif html[obj_start] == '{':
            if brace_count == 0:
                break
            brace_count -= 1
        obj_start -= 1

    # Find the end of the object (look forwards for })
    obj_end = pos
    brace_count = 0
    while obj_end < len(html):
        if html[obj_end] == '{':
            brace_count += 1
        elif html[obj_end] == '}':
            if brace_count == 0:
                obj_end += 1
                break
            brace_count -= 1
        obj_end += 1

    json_obj = html[obj_start:obj_end]
    print(f"\nExtracted object:")
    print(json_obj[:1000])

    # Try to parse it as JSON
    try:
        # Clean up JavaScript to make it valid JSON
        cleaned = json_obj
        # Remove trailing commas
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        # Remove comments
        cleaned = re.sub(r'//.*', '', cleaned)

        parsed = json.loads(cleaned)
        print("\n✅ Successfully parsed as JSON!")
        print("\nParsed object:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ Could not parse as JSON: {e}")

print("\n" + "="*60)
print("LOOKING FOR ARRAY OF STATION OBJECTS WITH DELAYS")
print("="*60)

# Look for patterns like: [{..., "delay": 12, ...}, {...}, ...]
# or: stations = [...]
array_patterns = [
    r'(\[\s*\{[^]]{200,}"delay"\s*:\s*\d+[^]]{200,}\])',
    r'stations?\s*[:=]\s*(\[\s*\{[^]]*"delay"[^]]*\}[^]]*\])',
]

for pattern in array_patterns:
    matches = re.findall(pattern, html, re.DOTALL)
    if matches:
        print(f"\n✅ Found array with delay data!")
        print(f"Pattern: {pattern[:50]}...")
        for i, match in enumerate(matches[:2], 1):
            print(f"\nMatch {i} (first 800 chars):")
            print(match[:800])

# Also look in <script> tags specifically
print("\n" + "="*60)
print("CHECKING SCRIPT TAGS FOR DELAY DATA")
print("="*60)

scripts = soup.find_all('script')
for i, script in enumerate(scripts):
    if script.string and 'delay":12' in script.string:
        print(f"\n✅ Found in script tag {i+1}")
        print(f"Script content (first 1000 chars):")
        print(script.string[:1000])

        # Try to extract a clean JSON array/object
        script_text = script.string

        # Look for variable assignment
        var_match = re.search(r'(var|let|const)\s+(\w+)\s*=\s*(\[[\s\S]*?\]);', script_text)
        if var_match:
            var_name = var_match.group(2)
            var_value = var_match.group(3)
            print(f"\n✅ Found variable: {var_name}")
            print(f"Value (first 500 chars): {var_value[:500]}")
