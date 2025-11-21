#!/usr/bin/env python3
"""Restructure AVA layout to put chat on right side of image"""

file_path = 'src/ava/omnipresent_ava_enhanced.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove icons from button labels
print("1. Removing icons from buttons...")
content = content.replace('"📊 Portfolio"', '"Portfolio"')
content = content.replace('"🎯 Opportunities"', '"Opportunities"')
content = content.replace('"📈 Watchlist"', '"Watchlist"')
content = content.replace('"❓ Help"', '"Help"')

# 2. Change column name from actions_col to content_col
print("2. Renaming actions_col to content_col...")
content = content.replace('img_col, actions_col = st.columns([1, 3])', 'img_col, content_col = st.columns([1, 3])')
content = content.replace('with actions_col:', 'with content_col:')

# 3. Add indentation to chat section (4 spaces) to move it inside content_col
print("3. Moving chat inside content_col...")

# The chat section starts after the last quick action button
# Find the line after help button and add indentation to everything after it

lines = content.split('\n')
new_lines = []
indent_mode = False
indent_level = 0

for i, line in enumerate(lines):
    # Start indenting after the help button's st.rerun()
    if 'if st.button("Help"' in line:
        indent_mode = True
        indent_level = 0
        new_lines.append(line)
        continue

    # Once we find the rerun after help button, start indenting on next section
    if indent_mode and indent_level == 0 and 'st.rerun()' in line:
        new_lines.append(line)
        indent_level = 1  # Start indenting from next section
        continue

    # Add indentation to chat, input, and processing sections
    if indent_level == 1:
        # Don't indent the expander close or function definitions
        if line.strip() and not line.startswith('def ') and 'if __name__' not in line:
            # Check if this is a top-level section comment or code
            if line.startswith('        # SECTION') or line.startswith('        if st.session_state.ava_messages'):
                new_lines.append('    ' + line)  # Add 4 spaces
            elif line.startswith('            '):
                new_lines.append('    ' + line)  # Add 4 spaces to already indented
            elif line.startswith('        ') and 'st.' in line:
                new_lines.append('    ' + line)  # Add 4 spaces
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            if line.strip() == '' or not line.strip().startswith('#'):
                indent_level = 2  # Stop indenting
    else:
        new_lines.append(line)

content = '\n'.join(new_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Layout restructured successfully!")
print("   - Removed button icons")
print("   - Moved chat to right of image")
