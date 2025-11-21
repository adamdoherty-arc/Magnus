"""Inspect Alert Elements from Debug HTML"""

from bs4 import BeautifulSoup
import re

with open(r'C:\Users\Asus\.xtrades_cache\debug_behappy_page.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')

elements = soup.find_all(name=re.compile(r'app-.*alert.*', re.I))

print(f'Found {len(elements)} alert elements:\n')

for i, e in enumerate(elements[:5], 1):
    print(f'{i}. Tag: {e.name}')
    print(f'   Text: {e.get_text(strip=True)[:300]}')
    print(f'   HTML: {str(e)[:600]}...')
    print()
