#!/usr/bin/env python3
"""Convert markdown chapter files to book-content.js for the website."""

import re
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAPTERS_DIR = os.path.join(SCRIPT_DIR, '..', 'chapters')
OUTPUT_FILE = os.path.join(SCRIPT_DIR, '..', 'website', 'book-content.js')

PART_FILES = ['part0.md', 'part1.md', 'part2.md', 'part3.md', 'part4.md']

PART_NAMES = {
    'part0.md': 'Part 0：在開始之前',
    'part1.md': 'Part 1：知識地圖',
    'part2.md': 'Part 2：方法論',
    'part3.md': 'Part 3：實戰流程',
    'part4.md': 'Part 4：心智模型',
}


def split_chapters(content):
    """Split markdown content by H1 headers."""
    chapters = []
    parts = re.split(r'^(# .+)$', content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        title = parts[i].lstrip('# ').strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''

        ch_match = re.search(r'第 (\d+) 章', title)
        app_match = re.search(r'附錄 ([A-C])', title)
        if ch_match:
            ch_id = f"ch{ch_match.group(1)}"
        elif app_match:
            ch_id = f"appendix-{app_match.group(1).lower()}"
        else:
            ch_id = re.sub(r'[^\w]', '-', title)[:20]

        chapters.append({
            'id': ch_id,
            'title': title,
            'content': body,
        })

    return chapters


def main():
    all_chapters = []

    preface_path = os.path.join(CHAPTERS_DIR, 'preface.md')
    if os.path.exists(preface_path):
        with open(preface_path, 'r') as f:
            preface_content = f.read()
        preface_body = re.sub(r'^# .+$', '', preface_content, count=1, flags=re.MULTILINE).strip()
        all_chapters.append({
            'id': 'preface',
            'title': '前言',
            'part': '',
            'content': preface_body,
        })

    for part_file in PART_FILES:
        path = os.path.join(CHAPTERS_DIR, part_file)
        if not os.path.exists(path):
            print(f"Warning: {path} not found")
            continue

        with open(path, 'r') as f:
            content = f.read()

        part_name = PART_NAMES.get(part_file, '')
        chapters = split_chapters(content)

        for ch in chapters:
            ch['part'] = part_name
            all_chapters.append(ch)

    js_content = f"const BOOK_CHAPTERS = {json.dumps(all_chapters, ensure_ascii=False, indent=2)};\n"

    with open(OUTPUT_FILE, 'w') as f:
        f.write(js_content)

    print(f"Generated {OUTPUT_FILE} with {len(all_chapters)} chapters")
    for ch in all_chapters:
        print(f"  {ch['id']}: {ch['title']} ({len(ch['content'])} chars)")


if __name__ == '__main__':
    main()
