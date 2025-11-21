#!/usr/bin/env python3
"""Add fixed-width constraint to AVA expander"""

file_path = 'src/ava/omnipresent_ava_enhanced.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the end of the scrollbar styling and add width constraints before </style>
old_css_end = """        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #6b7280;
        }
        </style>"""

new_css_end = """        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #6b7280;
        }

        /* Constrain expander width for wide screens */
        [data-testid="stExpander"] {
            max-width: 1400px;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        .streamlit-expanderHeader {
            max-width: 1400px;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        /* Constrain expander content */
        [data-testid="stExpander"] > div {
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }
        </style>"""

content = content.replace(old_css_end, new_css_end)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added fixed-width constraint (max-width: 1400px)")
print("   - Expander will now stay centered and not stretch across wide screens")
print("   - Everything will be compact and easily accessible")
