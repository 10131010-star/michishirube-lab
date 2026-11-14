#!/usr/bin/env python3
"""Offline regression for the actual free Animator check -> BOOTH funnel.

This checks wiring, not live sessions/clicks/purchases. No HTTP, API keys or
analytics accounts needed. A true purchase requires a separate BOOTH report.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "vrchat-animator-check" / "index.html"
PRODUCT_HOST = "nokino-tools.booth.pm"
PRODUCT_PATH = "/items/9133855"
CAMPAIGN = "animator_pro_launch"


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "a":
            self.links.append(data)
        elif tag == "script":
            self.scripts.append(data)


class AnimatorFunnelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.doc = Links()
        cls.doc.feed(cls.html)

    def test_free_to_booth_has_three_distinct_ctas(self):
        links = [a for a in self.doc.links if urlparse(a.get("href", "")).hostname == PRODUCT_HOST]
        self.assertEqual(len(links), 3, "Three page locations should link to the existing BOOTH product")
        ids = set()
        for link in links:
            url = urlparse(link["href"])
            self.assertEqual(url.scheme, "https")
            self.assertEqual(url.path, PRODUCT_PATH)
            self.assertEqual(url.fragment, "")
            params = parse_qs(url.query, keep_blank_values=True)
            self.assertEqual(params.get("utm_source"), ["michishirube_freecheck"])
            self.assertEqual(params.get("utm_medium"), ["referral"])
            self.assertEqual(params.get("utm_campaign"), [CAMPAIGN])
            self.assertEqual(len(params.get("utm_content", [])), 1)
            self.assertTrue(params["utm_content"][0])
            ids.add(params["utm_content"][0])
            self.assertEqual(link.get("target"), "_blank")
            self.assertIn("noopener", link.get("rel", "").split())
            self.assertIn("noreferrer", link.get("rel", "").split())
            self.assertTrue(link.get("data-goatcounter-click", "").startswith("vrchat-freecheck-"))
        self.assertEqual(ids, {"check_section", "verified_demo", "footer"})

    def test_click_ids_unique_and_no_pii_in_urls(self):
        event_ids = [a.get("data-goatcounter-click") for a in self.doc.links
                     if "data-goatcounter-click" in a]
        self.assertEqual(len(event_ids), len(set(event_ids)), "Event IDs must be unique per action")
        for a in self.doc.links:
            url = urlparse(a.get("href", ""))
            if url.hostname == PRODUCT_HOST:
                self.assertNotIn("email", url.query.lower())
                self.assertNotIn("user_id", url.query.lower())
                self.assertNotIn("purchase", url.query.lower())

    def test_page_counter_and_aggregate_completion_event(self):
        self.assertTrue(any(s.get("data-goatcounter") == "https://michishirube-ai.goatcounter.com/count"
                            for s in self.doc.scripts))
        self.assertIn("vrchat-freecheck-report-generated", self.html)
        self.assertIn("reportEventSent", self.html)
        self.assertIn("event:true", self.html)

    def test_organic_share_is_draft_only_and_source_marked(self):
        shares = [a for a in self.doc.links if "bsky.app/intent/compose" in a.get("href", "")]
        self.assertGreaterEqual(len(shares), 1)
        for a in shares:
            self.assertIn("utm_source%3Dbluesky", a["href"])
            self.assertIn("utm_medium%3Dorganic", a["href"])
        self.assertIn("自動投稿されません", self.html)

    def test_disclosures_and_real_measurement_boundary(self):
        self.assertIn("自動修復は行わず", self.html)
        self.assertIn("購入", self.html)
        self.assertIn("UTMは識別用", self.html)
        self.assertIn("実測値ではありません", self.html)


if __name__ == "__main__":
    unittest.main()
