#!/usr/bin/env python3
"""Add a Table of Contents page to each recipe section HTML file."""

import re
import os
import html

RECIPE_DIR = os.path.dirname(os.path.abspath(__file__))

TOC_CSS = """
        /* Table of Contents styles */
        .toc {
            page-break-after: always;
            padding: 0.5in 0;
        }
        .toc h2 {
            font-family: 'Playfair Display', Georgia, serif;
            text-align: center;
            font-size: 22px;
            color: #8B0000;
            border-bottom: 2px solid #8B0000;
            padding-bottom: 8px;
            margin: 24px 0 16px 0;
        }
        .toc ol {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .toc li {
            font-family: 'Lato', Georgia, serif;
            font-size: 16px;
            line-height: 2.2;
            border-bottom: 1px dotted #ccc;
        }
        .toc li a {
            color: #333;
            text-decoration: none;
            display: block;
            padding: 2px 0;
        }
        .toc li a:hover {
            color: #8B0000;
        }
        .toc li .toc-number {
            color: #8B0000;
            font-weight: bold;
            margin-right: 10px;
        }
"""

def slugify(text):
    """Convert recipe title to a URL-friendly anchor ID."""
    # Decode HTML entities first
    text = html.unescape(text)
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text.strip('-')

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if TOC already added
    if 'class="toc"' in content:
        print(f"  SKIP (TOC already exists): {os.path.basename(filepath)}")
        return

    # Extract recipe titles in order
    title_pattern = re.compile(r'<p class="recipe-title">(.*?)</p>')
    titles = title_pattern.findall(content)

    if not titles:
        print(f"  SKIP (no recipes found): {os.path.basename(filepath)}")
        return

    # Generate slugs
    slugs = [slugify(t) for t in titles]

    # 1. Inject TOC CSS before </style>
    content = content.replace('</style>', TOC_CSS + '    </style>', 1)

    # 2. Add id attributes to each <div class="recipe"> in order
    recipe_div_pattern = re.compile(r'<div class="recipe">')
    matches = list(recipe_div_pattern.finditer(content))

    # Work backwards to preserve positions
    for i in reversed(range(len(matches))):
        if i < len(slugs):
            m = matches[i]
            replacement = f'<div class="recipe" id="{slugs[i]}">'
            content = content[:m.start()] + replacement + content[m.end():]

    # 3. Build TOC HTML
    toc_lines = ['', '<div class="toc">', '    <h2>Table of Contents</h2>', '    <ol>']
    for i, title in enumerate(titles):
        toc_lines.append(f'        <li><a href="#{slugs[i]}"><span class="toc-number">{i+1}.</span> {title}</a></li>')
    toc_lines.append('    </ol>')
    toc_lines.append('</div>')
    toc_html = '\n'.join(toc_lines)

    # 4. Insert TOC after <h1 class="section-title">...</h1>
    section_title_pattern = re.compile(r'(<h1 class="section-title">.*?</h1>)')
    content = section_title_pattern.sub(r'\1\n' + toc_html, content, count=1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  DONE ({len(titles)} recipes): {os.path.basename(filepath)}")

def main():
    print("Adding Table of Contents to recipe section files...\n")
    for dirpath, dirnames, filenames in os.walk(RECIPE_DIR):
        for fname in sorted(filenames):
            if fname.endswith('.html'):
                filepath = os.path.join(dirpath, fname)
                section = os.path.basename(dirpath)
                print(f"[{section}]")
                process_file(filepath)
    print("\nDone!")

if __name__ == '__main__':
    main()
