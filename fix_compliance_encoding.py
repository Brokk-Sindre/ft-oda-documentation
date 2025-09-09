#!/usr/bin/env python3
"""Fix encoding issues in compliance/index.md file."""

import re

# Read the file as binary to handle problematic bytes
with open('docs/compliance/index.md', 'rb') as f:
    content = f.read()

# Convert to string, replacing problematic bytes
text = content.decode('utf-8', errors='replace')

# Fix the specific problematic characters
replacements = {
    '=\x10': '🔒',  # GDPR icon
    '=�': '📜',     # Licensing icon (was corrupted)
    '\x05': '✅',   # Data Quality icon
    'F�dt': 'Født',  # Danish word for "Born"
}

for old, new in replacements.items():
    text = text.replace(old, new)

# Also check for any remaining replacement characters
text = text.replace('�', 'ø')  # Default to Danish ø for any remaining

# Write the fixed content
with open('docs/compliance/index.md', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed encoding issues in compliance/index.md")