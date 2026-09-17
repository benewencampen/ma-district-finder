#!/usr/bin/env python3
"""Inline the district bundle into the page template."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')  # GitHub Pages serves this at the site root

data = open('ma_legislative_data.json').read()
hazards = [c for c in ('<', '>', '&', '\u2028', '\u2029') if c in data]
print('raw hazards in JSON:', hazards or 'none')

# The bundle sits inside a <script> block, so any '<' must not be able to close
# it. JSON's \u escapes survive JSON.parse unchanged.
data = (data.replace('<', '\\u003c').replace('>', '\\u003e')
            .replace('\u2028', '\\u2028').replace('\u2029', '\\u2029'))

html = open('template.html').read().replace('__DATA__', data)
assert '__DATA__' not in html
open(OUT, 'w').write(html)
print('wrote', OUT, round(len(html) / 1e6, 2), 'MB')
