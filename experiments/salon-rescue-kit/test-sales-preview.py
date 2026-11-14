#!/usr/bin/env python3
"""No-dependency, offline safety contract for the staging salon sales preview."""
from html.parser import HTMLParser
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
PAGE = HERE / 'sales-preview.html'

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.scripts = []
        self.meta = []
        self.buttons = []
        self.titles = []
        self.inside_title = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'a': self.links.append(d)
        if tag == 'script': self.scripts.append(d)
        if tag == 'meta': self.meta.append(d)
        if tag == 'button': self.buttons.append(d)
        if tag == 'title': self.inside_title = True
    def handle_endtag(self, tag):
        if tag == 'title': self.inside_title = False
    def handle_data(self, data):
        if self.inside_title: self.titles.append(data)

def main():
    page = PAGE.read_text(encoding='utf-8')
    parser = Inspect()
    parser.feed(page)
    checks = {
        'Japanese locale and viewport': 'lang="ja"' in page and any(m.get('name') == 'viewport' for m in parser.meta),
        'not indexed before approval': any(m.get('name') == 'robots' and m.get('content') == 'noindex,nofollow' for m in parser.meta),
        'draft-only, no checkout': all(x in page for x in ('販売準備中','購入ボタン・決済・注文受付はありません','仮価格')),
        'two free-tool destinations only': {a.get('href') for a in parser.links} == {'./checklist.html','./index.html'},
        'all links are explicitly campaign-propagatable': all('data-utm-pass' in a for a in parser.links),
        'no external scripts or forms': all('src' not in s for s in parser.scripts) and '<form' not in page.lower(),
        'no network/tracking scripts': not re.search(r'\b(fetch\s*\(|XMLHttpRequest|sendBeacon\s*\(|gtag\s*\(|localStorage|document\.cookie)\b', page),
        'five allowlisted UTM labels': all("'"+key+"'" in page for key in ('utm_source','utm_medium','utm_campaign','utm_content','utm_term')),
        'UTM value validation and safe relative link targets': "{1,60}" in page and 'index|checklist' in page,
        'responsive and reduced motion': '@media(max-width:760px)' in page and 'prefers-reduced-motion' in page,
        'privacy/limitations FAQ': all(s in page for s in ('個人を特定','自動連携・自動メッセージ配信','売上増加は保証しません','法的判断')),
        'no active external sales links': not any((a.get('href') or '').startswith(('https:','http:','mailto:','tel:')) for a in parser.links),
    }
    for name, okay in checks.items(): print(('PASS' if okay else 'FAIL') + ': ' + name)
    if not all(checks.values()): raise SystemExit('Preview staging QA failed')
    print(f'PASS: {len(checks)} staging checks; no publishing, checkout, or analytics connection')

if __name__ == '__main__': main()
