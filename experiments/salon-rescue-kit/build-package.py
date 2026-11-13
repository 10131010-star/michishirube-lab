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
GUIDE = """SALON RECOVERY LAB - 7-day reservation log (staging prototype)
===============================================================
STATUS: NOT FOR SALE. No checkout, customer contact, or public launch.
Suggested price JPY 1,480 is NOT an accepted offer.

1. Keep tracker-pro.html and tracker-core.js in the SAME folder.
2. Open tracker-pro.html locally in a modern browser.
3. Start a blank seven-day tracker. Use counts only, no client names.
4. Enter reservations, previous-day confirmations, late cancellations,
   no-shows, and refilled slots. Use 0 for measured zero; blank for unknown.
5. Download the CSV yourself each day, then import it to continue.
6. Read paid-pack.md for operator guidance and message templates.
7. Results are descriptive, not evidence that interventions caused gains.

The kit does not send messages, connect to bookings, save data to servers,
or provide legal advice. Check consent and your salon's own booking terms.
The included example figures are fictional.
See manifest.json for SHA-256 checksums of every included source file.
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
