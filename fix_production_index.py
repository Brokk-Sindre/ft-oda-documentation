#!/usr/bin/env python3
"""Fix remaining encoding issues in production/index.md."""

# Read the file
with open('docs/production/index.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic lines
content = content.replace('### = [Security]', '### 🔒 [Security]')
content = content.replace('### ø [Performance]', '### ⚡ [Performance]')

# Write back
with open('docs/production/index.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed production/index.md")