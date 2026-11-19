/* Offline-only 7-day salon tracker. No external code or personal-data handling. */
(function (root, make) {
  "use strict";
  var api = make();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SalonTracker = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  var HEADER = ["date","reservations","day_before_reminders","late_cancellations","no_shows","slots_refilled","notes"];
  var KEYS = HEADER.slice(1,6);
  function dayString(input) {
    var s = String(input || "");
    if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) throw Error("日付は YYYY-MM-DD 形式で入力してください");
    var d = new Date(s + "T00:00:00Z");
    if (!Number.isFinite(d.getTime()) || d.toISOString().slice(0,10) !== s) throw Error("存在しない日付です");
    return s;
  }
  function nextDay(s, n) {
    var d = new Date(dayString(s) + "T00:00:00Z");
    d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0,10);
  }
  function emptyWeek(start) {
    return Array.from({length:7}, function(_,i) {
      var r = {date:nextDay(start,i),notes:""};
      KEYS.forEach(function(k){r[k] = "";});
      return r;
    });
  }
  function normalize(input) {
    if (!Array.isArray(input) || input.length !== 7) throw Error("7日分の行が必要です");
    var start = dayString(input[0].date);
    return input.map(function(r,i) {
      if (!r || dayString(r.date) !== nextDay(start,i)) throw Error((i+1)+"日目の日付が連続していません");
      var out={date:r.date,notes:String(r.notes == null?"":r.notes)};
      if (out.notes.length > 120) throw Error((i+1)+"日目：メモは120文字以内です");
      var blanks=0;
      KEYS.forEach(function(k) {
        var v = String(r[k] == null?"":r[k]).trim();
        if (v === "") { out[k]=""; blanks++; }
        else if (!/^\d+$/.test(v) || !Number.isSafeInteger(Number(v)) || Number(v)>100000) {
          throw Error((i+1)+"日目："+k+"は0〜100000の整数で入力してください");
        } else out[k]=Number(v);
      });
      if (blanks !== 0 && blanks !== KEYS.length) throw Error((i+1)+"日目：数値は5項目すべて入力するか、すべて空欄にしてください");
      if (!blanks) {
        if (out.day_before_reminders>out.reservations) throw Error((i+1)+"日目：確認件数が予約数を超えています");
        if (out.late_cancellations+out.no_shows>out.reservations) throw Error((i+1)+"日目：キャンセル合計が予約数を超えています");
        if (out.slots_refilled>out.late_cancellations+out.no_shows) throw Error((i+1)+"日目：埋め直し件数がキャンセル合計を超えています");
      }
      return out;
    });
  }
  function summarize(rows) {
    var normalized = normalize(rows);
    var totals={days:0,reservations:0,day_before_reminders:0,late_cancellations:0,no_shows:0,slots_refilled:0,unfilled:0};
    normalized.forEach(function(r) {
      if (r.reservations === "") return;
      totals.days++;
      KEYS.forEach(function(k){totals[k]+=r[k];});
      totals.unfilled+=r.late_cancellations+r.no_shows-r.slots_refilled;
    });
    function rate(n,d){return d>0 ? Math.round((n/d)*1000)/10 : null;}
    totals.reminderRate=rate(totals.day_before_reminders,totals.reservations);
    totals.cancelRate=rate(totals.late_cancellations+totals.no_shows,totals.reservations);
    totals.refillRate=rate(totals.slots_refilled,totals.late_cancellations+totals.no_shows);
    return totals;
  }
  function escapeCell(s) {
    s=String(s == null?"":s);
    // Spreadsheet formula injection (including leading whitespace/control chars).
    if (/^[\s\u0000-\u001f]*[=+\-@]/.test(s)) s="'"+s;
    return /[",\r\n]/.test(s) ? '"'+s.replace(/"/g,'""')+'"' : s;
  }
  function toCsv(rows) {
    var checked=normalize(rows);
    var body=checked.map(function(r){return HEADER.map(function(k){return escapeCell(r[k]);}).join(",");});
    return "\uFEFF"+HEADER.join(",")+"\r\n"+body.join("\r\n")+"\r\n";
  }
  function parseCsv(src) {
    src=String(src || "").replace(/^\uFEFF/,"");
    if (src.length>20000) throw Error("CSVが大きすぎます（20KB上限）");
    var all=[],row=[],field="",quoted=false,afterQuote=false;
    for(var i=0;i<src.length;i++){
      var c=src[i];
      if (quoted) {
        if(c==='"') {if(src[i+1]==='"'){field+='"';i++;}else {quoted=false;afterQuote=true;}}
        else field+=c;
      } else if (afterQuote) {
        if (c===','){row.push(field);field="";afterQuote=false;}
        else if(c==='\r'||c==='\n'){row.push(field);all.push(row);row=[];field="";afterQuote=false;if(c==='\r'&&src[i+1]==='\n')i++;}
        else throw Error("CSVの引用符が不正です");
      } else if (c==='"') {
        if(field!=="") throw Error("CSVの引用符が不正です");
        quoted=true;
      } else if(c===','){row.push(field);field="";}
      else if(c==='\r'||c==='\n'){row.push(field);all.push(row);row=[];field="";if(c==='\r'&&src[i+1]==='\n')i++;}
      else field+=c;
    }
    if(quoted)throw Error("CSVの引用符が閉じていません");
    if(field!==""||row.length){row.push(field);all.push(row);}
    if(!all.length || all[0].join(",")!==HEADER.join(","))throw Error("CSVの列名が違います。専用の7日記録CSVをご利用ください");
    var data=all.slice(1);
    if(data.length!==7)throw Error("CSVは7日分の行にしてください");
    if(data.some(function(r){return r.length!==HEADER.length;}))throw Error("CSVの列数が合いません");
    return normalize(data.map(function(row){var r={};HEADER.forEach(function(k,i){r[k]=row[i];});return r;}));
  }
  return Object.freeze({HEADER:HEADER.slice(),emptyWeek:emptyWeek,normalize:normalize,summarize:summarize,toCsv:toCsv,parseCsv:parseCsv});
});
