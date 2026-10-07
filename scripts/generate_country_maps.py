#!/usr/bin/env python3
"""Generate region locator + territory maps for each country post."""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from shapely.geometry import box
from shapely.ops import unary_union

warnings.filterwarnings("ignore", category=UserWarning)

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "naturalearth"
ASSETS = ROOT / "assets"
REGIONS_JSON = Path(__file__).resolve().parent / "country_regions.json"

MAP_UNITS = CACHE / "ne_50m_admin_0_map_units.gpkg"
COUNTRIES = CACHE / "ne_50m_admin_0_countries.gpkg"

HIGHLIGHT = "#C62828"
OTHER = "#E0E0E0"
EDGE = "#424242"
OCEAN = "#E3F2FD"
FIGSIZE = (10.24, 10.24)
DPI = 100


def load_world() -> gpd.GeoDataFrame:
    frames = []
    for path in (MAP_UNITS, COUNTRIES, CACHE / "gibraltar.gpkg"):
        if path.exists():
            frames.append(gpd.read_file(path))
    if not frames:
        raise FileNotFoundError("Natural Earth cache missing. Download ne_50m datasets first.")
    gdf = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=frames[0].crs)
    # Prefer map_units rows first; drop duplicate GEOUNIT/NAME later when matching
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    return gdf.to_crs(4326)


def match_geometry(world: gpd.GeoDataFrame, ne_names: list[str]):
    cols = [c for c in ("NAME", "ADMIN", "NAME_LONG", "GEOUNIT", "BRK_NAME") if c in world.columns]
    for name in ne_names:
        for col in cols:
            hits = world[world[col].astype(str) == name]
            if len(hits):
                return unary_union(hits.geometry.values), name
        # case-insensitive contains fallback
        for col in cols:
            hits = world[world[col].astype(str).str.lower() == name.lower()]
            if len(hits):
                return unary_union(hits.geometry.values), str(hits.iloc[0][col])
    return None, None


def padded_bounds(geom, pad_ratio: float = 0.12, min_pad: float = 0.35, square: bool = False):
    minx, miny, maxx, maxy = geom.bounds
    w = max(maxx - minx, 0.05)
    h = max(maxy - miny, 0.05)
    pad_x = max(w * pad_ratio, min_pad)
    pad_y = max(h * pad_ratio, min_pad)
    minx, maxx = minx - pad_x, maxx + pad_x
    miny, maxy = miny - pad_y, maxy + pad_y
    if square:
        side = max(maxx - minx, maxy - miny)
        cx = (minx + maxx) / 2
        cy = (miny + maxy) / 2
        return cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2
    return minx, miny, maxx, maxy


def draw_map(
    world: gpd.GeoDataFrame,
    focus_geom,
    extent,
    title: str,
    out_path: Path,
    highlight_geom=None,
):
    minx, miny, maxx, maxy = extent
    clip = box(minx, miny, maxx, maxy)
    visible = world[world.intersects(clip)].copy()

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_facecolor(OCEAN)
    fig.patch.set_facecolor("white")

    if len(visible):
        visible.plot(ax=ax, color=OTHER, edgecolor=EDGE, linewidth=0.4)

    hg = highlight_geom if highlight_geom is not None else focus_geom
    gpd.GeoSeries([hg], crs=4326).plot(ax=ax, color=HIGHLIGHT, edgecolor="#7F0000", linewidth=0.9)

    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(title, fontsize=16, pad=12, color="#212121")
    ax.legend(
        handles=[Patch(facecolor=HIGHLIGHT, edgecolor="#7F0000", label="Focus")],
        loc="lower left",
        frameon=True,
        fontsize=10,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", pad_inches=0.15, dpi=DPI)
    plt.close(fig)


def generate_for_country(world: gpd.GeoDataFrame, entry: dict, region_members: list[dict], force: bool = False):
    country = entry["country"]
    region = entry["region"]
    region_path = ASSETS / f"{country}_Region_Map.png"
    territory_path = ASSETS / f"{country}_Territory_Map.png"

    focus_geom, matched = match_geometry(world, entry["ne_names"])
    if focus_geom is None:
        return {"country": country, "status": "no_geometry", "matched": None}

    # Region geometry = union of member countries that resolve
    member_geoms = []
    for m in region_members:
        g, _ = match_geometry(world, m["ne_names"])
        if g is not None:
            member_geoms.append(g)
    if not member_geoms:
        member_geoms = [focus_geom]
    region_union = unary_union(member_geoms)

    results = []
    if force or not region_path.exists():
        extent = padded_bounds(region_union, pad_ratio=0.10, min_pad=0.4, square=False)
        draw_map(
            world,
            focus_geom,
            extent,
            f"{''.join(region.split())} · {country}",
            region_path,
            highlight_geom=focus_geom,
        )
        results.append("region")
    if force or not territory_path.exists():
        extent = padded_bounds(focus_geom, pad_ratio=0.25, min_pad=0.4, square=True)
        draw_map(
            world,
            focus_geom,
            extent,
            country,
            territory_path,
            highlight_geom=focus_geom,
        )
        results.append("territory")
    return {"country": country, "status": "ok", "matched": matched, "wrote": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", action="append", help="Country key, e.g. Germany. Repeatable.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if not REGIONS_JSON.exists():
        raise SystemExit("Run scripts/build_country_regions.py first")

    entries = json.loads(REGIONS_JSON.read_text(encoding="utf-8"))
    by_region: dict[str, list[dict]] = {}
    for e in entries:
        by_region.setdefault(e["region"], []).append(e)

    if args.country:
        wanted = set(args.country)
        entries = [e for e in entries if e["country"] in wanted]
    if args.limit:
        entries = entries[: args.limit]

    print("Loading Natural Earth…")
    world = load_world()
    print(f"Features: {len(world)}")

    ok = fail = skip = 0
    failures = []
    for i, entry in enumerate(entries, 1):
        res = generate_for_country(world, entry, by_region[entry["region"]], force=args.force)
        if res["status"] == "ok":
            if res.get("wrote"):
                ok += 1
                print(f"[{i}/{len(entries)}] {entry['country']}: wrote {', '.join(res['wrote'])} ({res['matched']})")
            else:
                skip += 1
                print(f"[{i}/{len(entries)}] {entry['country']}: exists")
        else:
            fail += 1
            failures.append(entry["country"])
            print(f"[{i}/{len(entries)}] {entry['country']}: NO GEOMETRY for {entry['ne_names']}")

    print(f"\nDone. wrote={ok} skipped={skip} failed={fail}")
    if failures:
        print("Failures:", ", ".join(failures))
        (Path(__file__).parent / "map_failures.txt").write_text("\n".join(failures) + "\n")


if __name__ == "__main__":
    main()
