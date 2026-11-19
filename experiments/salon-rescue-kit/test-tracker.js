// Offline regression gate: node test-tracker.js. No network or npm install.
"use strict";
const assert = require("node:assert/strict");
const core = require("./tracker-core.js");
let passed=0;
function check(name, fn) {
  try { fn(); passed++; process.stdout.write("PASS "+name+"\n"); }
  catch(e) { process.stderr.write("FAIL "+name+": "+e.message+"\n"); process.exitCode=1; }
}
function rejects(fn, part) { assert.throws(fn, e => e.message.includes(part)); }
const blank=core.emptyWeek("2026-11-12");
const seven=blank.map((r,i)=>({...r,reservations:10,day_before_reminders:9,late_cancellations:2,no_shows:1,slots_refilled:1,notes:i===1?'a,"b"':''}));
check("7 consecutive days",()=>assert.equal(blank[6].date,"2026-11-18"));
check("leap day",()=>assert.equal(core.emptyWeek("2028-02-27")[2].date,"2028-02-29"));
check("invalid date blocked",()=>rejects(()=>core.emptyWeek("2026-02-30"),"存在しない"));
check("empty is unrecorded",()=>assert.equal(core.summarize(blank).days,0));
check("summary uses recorded days only",()=>{const x=core.summarize(seven);assert.equal(x.days,7);assert.equal(x.reservations,70);assert.equal(x.reminderRate,90);assert.equal(x.cancelRate,30);assert.equal(x.refillRate,33.3);assert.equal(x.unfilled,14);});
check("UTF-8 CSV roundtrip",()=>assert.deepEqual(core.parseCsv(core.toCsv(seven)),core.normalize(seven)));
check("blank CSV roundtrip",()=>assert.deepEqual(core.parseCsv(core.toCsv(blank)),core.normalize(blank)));
check("CSV formula neutralized",()=>assert.match(core.toCsv(blank.map(r=>({...r,notes:"  =SUM(A1:A4)"}))),/'  =SUM/));
check("negative CSV formula neutralized",()=>assert.match(core.toCsv(blank.map(r=>({...r,notes:"-2+3"}))),/'-2\+3/));
check("wrong header blocked",()=>rejects(()=>core.parseCsv("date,reservations\n2026-11-12,2"),"列名"));
check("oversized CSV blocked",()=>rejects(()=>core.parseCsv("X".repeat(20001)),"大きすぎ"));
check("incomplete data blocked",()=>rejects(()=>core.normalize([{...blank[0],reservations:3},...blank.slice(1)]),"5項目"));
check("non-consecutive dates blocked",()=>rejects(()=>core.normalize([{...blank[0]},{...blank[0]},...blank.slice(2)]),"連続"));
check("excess reminders blocked",()=>rejects(()=>core.normalize([{...seven[0],day_before_reminders:11},...seven.slice(1)]),"確認件数"));
check("excess cancellation blocked",()=>rejects(()=>core.normalize([{...seven[0],late_cancellations:11},...seven.slice(1)]),"キャンセル合計"));
check("excess refill blocked",()=>rejects(()=>core.normalize([{...seven[0],slots_refilled:9},...seven.slice(1)]),"埋め直し"));
check("negative count blocked",()=>rejects(()=>core.normalize([{...seven[0],reservations:-1},...seven.slice(1)]),"整数"));
check("decimal count blocked",()=>rejects(()=>core.normalize([{...seven[0],reservations:2.5},...seven.slice(1)]),"整数"));
check("invalid quote blocked",()=>rejects(()=>core.parseCsv('date,reservations,"unclosed'),"閉じて"));
check("formula in quoted multiline field roundtrip",()=>{const rows=seven.map((r,i)=>({...r,notes:i===0?"hello,\nworld":r.notes}));assert.deepEqual(core.parseCsv(core.toCsv(rows)),core.normalize(rows));});
if(process.exitCode) process.stderr.write("Tracker tests failed; do not publish.\n");
else process.stdout.write("PASS all "+passed+" offline tracker checks.\n");
