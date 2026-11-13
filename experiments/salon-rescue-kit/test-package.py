#!/usr/bin/env python3
"""Offline acceptance tests for the proposed salon kit package. No uploads."""
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("salon_packager", HERE / "build-package.py")
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def main():
    with tempfile.TemporaryDirectory(prefix="salon-kit-qa-") as tmp:
        temp = Path(tmp)
        first = temp / "first.zip"
        second = temp / "second.zip"
        path, sha = packager.build(first)
        check(path == first, "must write to explicit temporary destination")
        check(sha == hashlib.sha256(first.read_bytes()).hexdigest(), "ZIP SHA mismatch")
        check(first.with_suffix(".zip.sha256").is_file(), "SHA sidecar missing")
        expected = set(packager.PRODUCT_FILES) | {"README-FIRST.txt", "manifest.json"}
        with ZipFile(first) as z:
            names = z.namelist()
            check(len(names) == len(set(names)), "duplicate entry")
            check(set(names) == {packager.PACKAGE_DIR + name for name in expected},
                  "required file missing or unexpected file packaged")
            check(all(".." not in Path(name).parts and not name.startswith("/")
                      for name in names), "unsafe ZIP entry")
            manifest = json.loads(z.read(packager.PACKAGE_DIR + "manifest.json"))
            check("not for sale" in manifest["status"], "staging disclaimer missing")
            check(len(manifest["files"]) == len(expected) - 1, "manifest entry count")
            for record in manifest["files"]:
                name = record["path"]
                content = z.read(packager.PACKAGE_DIR + name)
                check(hashlib.sha256(content).hexdigest() == record["sha256"],
                      "ZIP manifest checksum mismatch: " + name)
                check(len(content) == record["bytes"], "manifest byte count: " + name)
                if name in packager.PRODUCT_FILES:
                    check(content == (HERE / name).read_bytes(),
                          "packaged source differs from repository source: " + name)
            check(b"NOT FOR SALE" in z.read(packager.PACKAGE_DIR + "README-FIRST.txt"),
                  "customer-facing staging warning missing")
        _, sha2 = packager.build(second)
        check(sha == sha2, "repeated build was not reproducible")
        # A missing dependency must stop packaging; do not silently ship broken tools.
        actual_root = packager.BASE
        try:
            packager.BASE = temp
            for name in packager.PRODUCT_FILES[1:]:
                (temp / name).write_bytes((HERE / name).read_bytes())
            try:
                packager.build(temp / "incomplete.zip")
            except ValueError as e:
                check("Missing or unsafe" in str(e), "unexpected missing file error")
            else:
                raise AssertionError("missing tracker-pro.html was not rejected")
        finally:
            packager.BASE = actual_root
    print("PASS: salon kit archive entries, SHA256 manifest, exact sources,")
    print("      staging disclaimer, repeatability, missing-file rejection")
    print("NOTE: no browser QA, no payment integration, no public release")

if __name__ == "__main__":
    main()
