#!/usr/bin/env python3
"""Offline checks for the unlaunched B2B service-offer prototype."""
import unittest
from pathlib import Path
from html.parser import HTMLParser

HTML = (Path(__file__).resolve().parents[1] / "service-offer" / "index.html").read_text(encoding="utf-8")


class Parse(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.forms = []
        self.scripts = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        v = dict(attrs)
        if tag == "a":
            self.links.append(v)
        elif tag == "form":
            self.forms.append(v)
        elif tag == "script":
            self.scripts.append(v)
        elif tag == "h1":
            self.headings.append(v)


class OfferTests(unittest.TestCase):
    def test_accessible_landing_structure(self):
        self.assertIn('lang="ja"', HTML)
        self.assertIn('name="viewport"', HTML)
        p = Parse()
        p.feed(HTML)
        self.assertEqual(len(p.headings), 1)

    def test_offer_and_scope_defined(self):
        for item in ["小規模", "問い合わせ", "39,800円", "仮説価格", "買い切り", "正式"]:
            with self.subTest(item=item):
                self.assertIn(item, HTML)

    def test_no_fake_checkout_or_lead_capture(self):
        p = Parse()
        p.feed(HTML)
        self.assertEqual(p.forms, [])
        self.assertEqual(p.scripts, [])
        self.assertEqual([a.get("href") for a in p.links], ["./audit.html", "./demo.html"])

    def test_synthetic_demo_is_not_real_client(self):
        demo = (Path(__file__).resolve().parents[1] / "service-offer" / "demo.html").read_text(encoding="utf-8")
        self.assertIn("架空店舗", demo)
        self.assertIn('name="robots" content="noindex,nofollow"', demo)
        self.assertIn("予約や問い合わせは送信できません", demo)
        self.assertIn('id="menu"', demo)
        self.assertIn('id="contact"', demo)

    def test_browser_only_audit_prelaunch(self):
        audit = (Path(__file__).resolve().parents[1] / "service-offer" / "audit.html").read_text(encoding="utf-8")
        self.assertIn('name="robots" content="noindex,nofollow"', audit)
        self.assertIn('id="audit"', audit)
        self.assertIn('id="result"', audit)
        self.assertIn("event.preventDefault()", audit)
        self.assertIn("すべての項目に回答してください", audit)
        self.assertIn("売上改善を保証", HTML)
        self.assertNotIn("fetch(", audit)
        self.assertNotIn("XMLHttpRequest", audit)
        self.assertNotIn("localStorage", audit)
        self.assertNotIn("sendBeacon", audit)
        self.assertNotIn('type="email"', audit)
        self.assertNotIn('action="http', audit)
        self.assertIn('href="./demo.html"', audit)
        self.assertIn('href="./index.html"', audit)

    def test_no_premature_search_indexing(self):
        self.assertIn('name="robots" content="noindex,nofollow"', HTML)
        self.assertIn("販売開始前", HTML)
        self.assertIn("個人情報の取得も行いません", HTML)

    def test_no_false_performance_promises(self):
        self.assertIn("売上増加は保証できません", HTML)
        self.assertIn("納期", HTML)
        self.assertIn("個別見積", HTML)


if __name__ == "__main__":
    unittest.main()
