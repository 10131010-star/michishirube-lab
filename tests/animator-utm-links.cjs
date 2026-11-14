'use strict';
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const html = fs.readFileSync(path.join(__dirname, '../vrchat-animator-check/index.html'),'utf8');
const anchors = [...html.matchAll(/<a\b[^>]*\bhref="([^"]+)"[^>]*>/g)]
  .map(match => ({tag:match[0],href:match[1].replace(/&amp;/g,'&')}))
  .filter(a => a.href.startsWith('https://nokino-tools.booth.pm/items/9133855?'));
assert.equal(anchors.length,3,'free check must have exactly three tracked BOOTH CTAs');
const contents = [];
const events = new Set();
for(const a of anchors) {
  const url = new URL(a.href);
  assert.equal(url.origin,'https://nokino-tools.booth.pm');
  assert.equal(url.pathname,'/items/9133855');
  assert.equal(url.searchParams.get('utm_source'),'michishirube_freecheck');
  assert.equal(url.searchParams.get('utm_medium'),'referral');
  assert.equal(url.searchParams.get('utm_campaign'),'animator_pro_launch');
  const content=url.searchParams.get('utm_content');
  assert.ok(content,'each CTA must identify its unique position');
  contents.push(content);
  const event = a.tag.match(/data-goatcounter-click="([^"]+)"/);
  assert.ok(event,'existing privacy-safe outbound click event must remain');
  events.add(event[1]);
  assert.equal(url.searchParams.get('email'),null,'no personal detail in URLs');
}
assert.deepEqual(contents.sort(),['check_section','footer','verified_demo']);
assert.equal(events.size,3,'click events must remain distinct');
assert.match(html,/data-goatcounter="https:\/\/michishirube-ai\.goatcounter\.com\/count"/);
assert.match(html,/回答・結果は外部送信しません/);
assert.doesNotMatch(html,/utm_campaign=animator_doctor/);
// The fourth troubleshooting scenario must be navigable, source-backed, and scoped.
assert.match(html, /href="#case-transition"/);
assert.match(html, /<h3 id="case-transition">Q3\./);
assert.match(html, /<h2 id="troubletitle">よくある4つのつまずきと確認順<\/h2>/);
assert.match(html, /https:\/\/docs\.unity3d\.com\/ja\/2022\.3\/Manual\/class-Transition\.html/);
assert.match(html, /Exit TimeやVRChat内の復帰動作を自動で検証する機能はありません/);
assert.match(html, /href="#verified-demo">検証用Controllerの実例と機能差を確認/);
console.log(JSON.stringify({status:'passed',cases:18,ctaCount:3,positions:contents,scope:'static HTML/URL regression only; GA4 reception, live-site browsers and Unity not tested'},null,2));
