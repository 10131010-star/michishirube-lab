#!/usr/bin/env python3
"""Build a reproducible, *staging-only* offline kit ZIP. No publishing or uploads."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

BASE = Path(__file__).resolve().parent
PACKAGE_DIR = "salon-rescue-kit-v0.3/"
PRODUCT_FILES = (
    "tracker-pro.html",
    "tracker-core.js",
    "7-day-tracker.csv",
    "paid-pack.md",
)
FIXED_ZIP_TIME = (2026, 11, 14, 0, 0, 0)
MAX_FILE_BYTES = 2_000_000
GUIDE = """サロン予約ロス対策キット｜7日間の記録ツール（試作品）
===================================================
NOT FOR SALE / 未販売・決済不可・お客様への配布前の検証版
仮価格1,480円は未承認です。サポート窓口・返品返金・利用許諾・対応環境は未確定です。

【このZIPだけでできること】
予約件数・前日確認件数・直前キャンセル件数・無断キャンセル件数・
空き枠の埋め直し件数を7日分手入力し、集計してCSV保存・再読込できます。
予約システムへの接続、LINE自動送信、顧客情報の収集はできません。
無料の損失概算ミニツール（index.html）は、このZIPには含まれません。

【はじめかた（パソコンを想定・スマホ動作は未保証）】
1. ZIPを展開し、tracker-pro.html と tracker-core.js を同じフォルダーに置きます。
2. Chrome/Edge等で tracker-pro.html を開き、開始日と「空欄の7日間」を設定します。
3. 予約・前日確認・直前キャンセル・無断・埋め直しの件数を日ごとに入力します。
4. 実際に計測した0件は「0」、未確認・未入力は空欄とし、推測で埋めません。
5. 「CSVを保存」を押して端末に保管し、再開するときはCSVを読み込みます。
6. 7日後の集計結果を確認します。増収やキャンセル減少の因果効果は証明しません。
7. 同梱のpaid-pack.mdで、連絡文案・安全上の注意を確認してください。

【情報・トラブル防止】
予約者の氏名・連絡先・予約名簿は入力しないでください。端末外への自動保存はありません。
予約者への連絡は店舗の既存の同意済み手段を使い、送信前に確認してください。
CSVは利用者が適切に保管・バックアップしてください。効果・端末互換性は未保証です。
このZIPは販売用最終版ではありません。現段階で購入・配布・サポート受付はありません。
manifest.jsonに同梱元ファイルのSHA-256を記録しています。
"""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def entry(name: str, data: bytes) -> tuple[ZipInfo, bytes]:
    info = ZipInfo(PACKAGE_DIR + name, FIXED_ZIP_TIME)
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    info.create_system = 3
    return info, data

def build(output: Path) -> tuple[Path, str]:
    items: list[tuple[str, bytes]] = []
    for name in PRODUCT_FILES:
        source = BASE / name
        if source.is_symlink() or not source.is_file() or source.resolve().parent != BASE:
            raise ValueError("Missing or unsafe product source: " + name)
        data = source.read_bytes()
        if not data or len(data) > MAX_FILE_BYTES:
            raise ValueError("Invalid product source size: " + name)
        items.append((name, data))
    tracker = dict(items)["tracker-pro.html"].decode("utf-8")
    if './tracker-core.js' not in tracker:
        raise ValueError("The offline tracker must reference its bundled core JS")
    guide = GUIDE.encode("utf-8")
    items.append(("README-FIRST.txt", guide))
    manifest = {
        "version": "0.3",
        "status": "staging-only; not for sale; not a live checkout",
        "privacy": "no personal customer data required; local CSV download",
        "files": [{"path": name, "bytes": len(data), "sha256": digest(data)}
                  for name, data in items],
    }
    items.append(("manifest.json", (json.dumps(manifest, indent=2, ensure_ascii=False)
                                    + "\n").encode("utf-8")))
    if output.is_symlink():
        raise ValueError("Refusing a symlink output")
    output.parent.mkdir(parents=True, exist_ok=True)
    # All paths and timestamps are fixed. The ZIP is a distributable candidate,
    # not proof of payment integration, browser compatibility, or public release.
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in items:
            info, raw = entry(name, data)
            archive.writestr(info, raw, compress_type=ZIP_DEFLATED, compresslevel=9)
    package_sha = digest(output.read_bytes())
    output.with_suffix(output.suffix + ".sha256").write_text(
        package_sha + "  " + output.name + "\n", encoding="utf-8"
    )
    return output, package_sha

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=BASE / "dist" / "salon-rescue-kit-v0.3-staging.zip")
    args = parser.parse_args()
    output, sha = build(args.output.resolve())
    print("STAGING ZIP:", output)
    print("SHA256:", sha)
    print("NO SALE OR PUBLIC RELEASE PERFORMED")

if __name__ == "__main__":
    main()
