#!/usr/bin/env python3
"""Insert territory map includes into country markdown posts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
REGIONS_JSON = Path(__file__).resolve().parent / "country_regions.json"
ASSETS = ROOT / "assets"


def territory_include(country: str) -> str:
    return (
        f'{{% include custom-nav-links.html src="{country}_Territory_Map.png" '
        f'data="photo" title="國土地圖" %}}\n'
    )


def split_front_matter(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[: end + 5], text[end + 5 :]
    return "", text


def insert_maps(text: str, country: str, region: str) -> tuple[str, list[str]]:
    del region  # region locator maps are not inserted into posts
    changes: list[str] = []
    territory_src = f"{country}_Territory_Map.png"
    fm, body = split_front_matter(text)

    if territory_src in (fm + body):
        return fm + body, changes

    area = re.search(r"^- \*\*國土面積\*\*.+$", body, flags=re.M)
    if area:
        body = body[: area.end()] + "\n" + territory_include(country) + body[area.end() :]
        changes.append("territory")
        return fm + body, changes

    m = re.search(
        r"(## [^\n]*基本資料[^\n]*\n)([\s\S]*?)(?=\n## |\n---|\Z)",
        body,
    )
    if m:
        body_block = m.group(2).rstrip() + "\n" + territory_include(country) + "\n"
        body = body[: m.start(2)] + body_block + body[m.end(2) :]
        changes.append("territory-fallback-basic")
        return fm + body, changes

    hm = re.search(r"^#{1,6} .+$", body, flags=re.M)
    if hm:
        line_end = body.find("\n", hm.end())
        if line_end == -1:
            line_end = len(body)
        body = body[:line_end] + "\n" + territory_include(country) + body[line_end:]
        changes.append("territory-after-heading")

    return fm + body, changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", action="append")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    entries = json.loads(REGIONS_JSON.read_text(encoding="utf-8"))
    if args.country:
        wanted = set(args.country)
        entries = [e for e in entries if e["country"] in wanted]

    updated = skipped = missing_assets = 0
    for entry in entries:
        country = entry["country"]
        region = entry["region"]
        slug = entry["slug"]
        post = POSTS / f"{slug}.md"
        if not post.exists():
            print(f"MISSING POST {slug}")
            continue
        territory_asset = ASSETS / f"{country}_Territory_Map.png"
        if not territory_asset.exists():
            missing_assets += 1
            print(f"SKIP {country}: territory map missing")
            continue
        text = post.read_text(encoding="utf-8")
        new_text, changes = insert_maps(text, country, region)
        if not changes:
            skipped += 1
            continue
        if args.dry_run:
            print(f"DRY {country}: {changes}")
        else:
            post.write_text(new_text, encoding="utf-8")
            print(f"UPDATED {country}: {changes}")
        updated += 1
    print(f"\nupdated={updated} skipped={skipped} missing_assets={missing_assets}")


if __name__ == "__main__":
    main()
