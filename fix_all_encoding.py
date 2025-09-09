#!/usr/bin/env python3
"""Fix encoding issues in all documentation files."""

import os
import glob

def fix_file(filepath):
    """Fix encoding issues in a single file."""
    try:
        # Read the file as binary
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Convert to string, replacing problematic bytes
        text = content.decode('utf-8', errors='replace')
        
        # Fix known problematic patterns
        replacements = {
            '=\x10': '🔒',     # Lock icon
            '=�': '📜',        # Scroll icon
            '\x05': '✅',      # Check icon
            '=\x17': '🔗',     # Link icon
            '<�\x0f': '📋',    # Clipboard icon
            '=e': '📁',        # Folder icon
            '=\'': '🔧',       # Wrench icon
            '�': 'ø',          # Danish ø
            'F�dt': 'Født',    # Danish "Born"
            'Akt�r': 'Aktør',  # Danish "Actor"
            'M�de': 'Møde',    # Danish "Meeting"
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Write the fixed content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"Fixed: {filepath}")
        return True
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

# Fix all markdown files
md_files = glob.glob('docs/**/*.md', recursive=True)
fixed_count = 0
for filepath in md_files:
    if fix_file(filepath):
        fixed_count += 1

print(f"\nFixed {fixed_count} files total")