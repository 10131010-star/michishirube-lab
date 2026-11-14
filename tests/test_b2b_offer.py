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
        hrefs = [a.get("href") for a in p.links]
        self.assertEqual(hrefs[:4], ["./audit.html", "./demo.html", "./audit.html", "./demo.html"])
        self.assertEqual(len(hrefs), 5)
        # This mailto only opens the visitor's mail app; it never sends automatically.
        self.assertTrue(hrefs[4].startswith("mailto:michishirube.office@gmail.com?subject="))
        self.assertIn("所有・受信試験", HTML)
        self.assertIn("一般公開・営業送信しません", HTML)
        self.assertIn('class="header-ctas"', HTML)
        self.assertIn("無料5項目チェックを試す", HTML)
        self.assertIn("予約・問い合わせ・注文は受け付けません", HTML)

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
        self.assertIn("getElementById('audit-run').addEventListener('click'", audit)
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
        # Prioritized next-step links contain only static fragments, not audit answers.
        self.assertIn('id="audit-next" hidden', audit)
        self.assertIn('id="audit-demo-link"', audit)
        self.assertIn("demoLink.href='./demo.html#'+(demoAnchors[key]||'journey')", audit)
        self.assertIn('href="./index.html#offer-price"', audit)
        self.assertIn('id="offer-price"', HTML)

    def test_no_premature_search_indexing(self):
        self.assertIn('name="robots" content="noindex,nofollow"', HTML)
        self.assertIn("販売開始前", HTML)
        self.assertIn("個人情報の取得も行いません", HTML)

    def test_no_false_performance_promises(self):
        self.assertIn("売上増加は保証できません", HTML)
        self.assertIn("納期", HTML)
        self.assertIn("個別見積", HTML)


    def test_interactive_synthetic_demo_has_a_safe_click_path(self):
        demo = (Path(__file__).resolve().parents[1] / "service-offer" / "demo.html").read_text(encoding="utf-8")
        for required in [
            'id="menu"', 'id="hours"', 'id="contact"',
            'href="#menu"', 'href="#hours"', 'href="#contact"',
            'id="show-before"', 'id="show-after"', 'aria-pressed="true"',
            'id="contact-dialog"', 'id="try-contact"', 'dialog.showModal()',
            '予約や問い合わせは送信できません', '架空店舗',
        ]:
            with self.subTest(required=required):
                self.assertIn(required, demo)
        # No fake booking, analytics, customer data collection, or external links.
        parser = Parse()
        parser.feed(demo)
        self.assertEqual(parser.forms, [])
        self.assertFalse(any((link.get("href") or "").startswith(("http:", "https:", "mailto:", "tel:")) for link in parser.links))
        for unsafe in ["fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "sessionStorage", "<iframe", "type=\"email\""]:
            self.assertNotIn(unsafe, demo)
        self.assertIn('name="robots" content="noindex,nofollow"', demo)
        self.assertIn('<a class="btn" href="#hours">次に営業時間・定休日を確認する</a>', demo)
        self.assertIn('<a class="btn" href="#contact">営業時間を確認したら、予約・問い合わせ案内へ</a>', demo)

    def test_costs_and_official_alternatives_are_disclosed(self):
        self.assertIn("継続利用料", HTML)
        self.assertIn("支払い担当", HTML)
        note = (Path(__file__).resolve().parents[1] / "service-offer" / "COMPETITOR-AND-SCOPE.md").read_text(encoding="utf-8")
        for item in ["studio.design/ja/pricing", "peraichi.com/news/press_2025_0818", "未承認", "外部通信なし", "受注", "粗利益"]:
            self.assertIn(item, note)


    def test_audit_provides_actionable_local_copy_and_fresh_result(self):
        audit = (Path(__file__).resolve().parents[1] / "service-offer" / "audit.html").read_text(encoding="utf-8")
        for marker in ['id="copy-result" hidden', "navigator.clipboard.writeText(latestResult)",
                       "addEventListener('change',reset)", "今週試す1手",
                       "優先順は仮の案", "latestResult=''",
                       "外部への送信はしません"]:
            with self.subTest(marker=marker):
                self.assertIn(marker, audit)
        for banned in ["fetch(", "XMLHttpRequest", "sendBeacon", "localStorage", "<form", 'type="email"']:
            self.assertNotIn(banned, audit)


    def test_audit_cannot_submit_answers_if_javascript_is_disabled(self):
        # Without JavaScript, an ordinary form+submit button silently sends
        # answers as query parameters despite the browser-only privacy claim.
        audit = (Path(__file__).resolve().parents[1] / "service-offer" / "audit.html").read_text(encoding="utf-8")
        parser = Parse()
        parser.feed(audit)
        self.assertEqual(parser.forms, [], "Never allow an implicit GET form submission")
        self.assertIn('type="button" id="audit-run"', audit)
        self.assertIn("getElementById('audit-run').addEventListener('click'", audit)
        self.assertIn("<noscript>", audit)


if __name__ == "__main__":
    unittest.main()
