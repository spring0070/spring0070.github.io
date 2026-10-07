# Country map scripts

Generate geographically accurate region locator maps and territory maps for every country post.

## Prerequisites

```bash
pip3 install geopandas shapely pyogrio matplotlib pandas
```

Natural Earth data is cached under `.cache/naturalearth/` (gitignored via `.cache`).

## Rebuild country → region mapping

```bash
python3 scripts/build_country_regions.py
```

Reads `World.md` and writes `scripts/country_regions.json`.

## Generate map PNGs

```bash
# one country
python3 scripts/generate_country_maps.py --country Germany --force

# all countries (~480 PNGs into assets/)
python3 scripts/generate_country_maps.py --force
```

Outputs:

- `assets/{Country}_Region_Map.png` — country highlighted inside its World.md region
- `assets/{Country}_Territory_Map.png` — country outline / territory view

## Insert includes into posts

```bash
python3 scripts/insert_country_maps.py --country Germany
python3 scripts/insert_country_maps.py
```

Idempotent: skips posts that already contain the includes.

## Placement

Only the **territory map** is inserted into posts (after `國土面積`, or after `基本資料` / first heading on stub posts).

Region locator PNGs may still be generated into `assets/` for reuse, but they are **not** shown on country pages.
