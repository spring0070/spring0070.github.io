#!/usr/bin/env python3
"""Parse World.md into scripts/country_regions.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "World.md"
OUT = Path(__file__).resolve().parent / "country_regions.json"

# Country key (from post slug) -> Natural Earth NAME / ADMIN / GEOUNIT candidates
NE_ALIASES: dict[str, list[str]] = {
    "Germany": ["Germany"],
    "Poland": ["Poland"],
    "CzechRepublic": ["Czechia", "Czech Republic"],
    "Hungary": ["Hungary"],
    "Austria": ["Austria"],
    "Switzerland": ["Switzerland"],
    "Slovakia": ["Slovakia"],
    "Slovenia": ["Slovenia"],
    "Liechtenstein": ["Liechtenstein"],
    "Sweden": ["Sweden"],
    "Denmark": ["Denmark"],
    "Norway": ["Norway"],
    "Finland": ["Finland"],
    "Iceland": ["Iceland"],
    "FaroeIslands": ["Faroe Islands"],
    "AlandIslands": ["Åland", "Aland", "Åland Islands"],
    "SvalbardandJanMayen": ["Svalbard", "Svalbard Islands", "Jan Mayen"],
    "Lithuania": ["Lithuania"],
    "Latvia": ["Latvia"],
    "Estonia": ["Estonia"],
    "UnitedKingdom": ["United Kingdom"],
    "Ireland": ["Ireland"],
    "Netherlands": ["Netherlands"],
    "Belgium": ["Belgium"],
    "Luxembourg": ["Luxembourg"],
    "Jersey": ["Jersey"],
    "IsleofMan": ["Isle of Man"],
    "Guernsey": ["Guernsey"],
    "France": ["France"],
    "Italy": ["Italy"],
    "Spain": ["Spain"],
    "Portugal": ["Portugal"],
    "Greece": ["Greece"],
    "Malta": ["Malta"],
    "Cyprus": ["Cyprus"],
    "NorthernCyprus": ["N. Cyprus", "Northern Cyprus"],
    "VaticanCity": ["Vatican"],
    "SanMarino": ["San Marino"],
    "Monaco": ["Monaco"],
    "Andorra": ["Andorra"],
    "Gibraltar": ["Gibraltar"],
    "MaltaOrder": ["Malta"],  # no NE geometry; fallback handled in generator
    "Croatia": ["Croatia"],
    "BosniaandHerzegovina": ["Bosnia and Herz.", "Bosnia and Herzegovina"],
    "Serbia": ["Serbia"],
    "Montenegro": ["Montenegro"],
    "NorthMacedonia": ["North Macedonia", "Macedonia"],
    "Albania": ["Albania"],
    "Kosovo": ["Kosovo"],
    "Bulgaria": ["Bulgaria"],
    "Romania": ["Romania"],
    "Moldova": ["Moldova"],
    "Ukraine": ["Ukraine"],
    "Belarus": ["Belarus"],
    "Russia": ["Russia", "Russian Federation"],
    "Georgia": ["Georgia"],
    "Armenia": ["Armenia"],
    "Azerbaijan": ["Azerbaijan"],
    "Abkhazia": ["Georgia"],  # disputed; approximate with Georgia highlight fallback
    "SouthOssetia": ["Georgia"],
    "UnitedStates": ["United States of America", "United States"],
    "Canada": ["Canada"],
    "Mexico": ["Mexico"],
    "Guatemala": ["Guatemala"],
    "Belize": ["Belize"],
    "Honduras": ["Honduras"],
    "ElSalvador": ["El Salvador"],
    "Nicaragua": ["Nicaragua"],
    "CostaRica": ["Costa Rica"],
    "Panama": ["Panama"],
    "Cuba": ["Cuba"],
    "Jamaica": ["Jamaica"],
    "Haiti": ["Haiti"],
    "DominicanRepublic": ["Dominican Rep.", "Dominican Republic"],
    "TheBahamas": ["Bahamas", "The Bahamas"],
    "TrinidadAndTobago": ["Trinidad and Tobago"],
    "Barbados": ["Barbados"],
    "SaintLucia": ["Saint Lucia"],
    "SaintVincentAndTheGrenadines": ["Saint Vincent and the Grenadines"],
    "Grenada": ["Grenada"],
    "AntiguaAndBarbuda": ["Antigua and Barbuda", "Antigua"],
    "SaintKittsAndNevis": ["Saint Kitts and Nevis"],
    "Dominica": ["Dominica"],
    "SaintMartin": ["St-Martin", "Saint Martin"],
    "SintMaarten": ["Sint Maarten"],
    "SaintBarthelemy": ["Saint Barthelemy"],
    "Anguilla": ["Anguilla"],
    "Montserrat": ["Montserrat"],
    "BritishVirginIslands": ["British Virgin Is.", "British Virgin Islands"],
    "U.S.VirginIslands": ["U.S. Virgin Is.", "United States Virgin Islands"],
    "CaymanIslands": ["Cayman Is.", "Cayman Islands"],
    "TurksAndCaicosIslands": ["Turks and Caicos Is.", "Turks and Caicos Islands"],
    "Bermuda": ["Bermuda"],
    "Aruba": ["Aruba"],
    "Curacao": ["Curaçao"],
    "PuertoRico": ["Puerto Rico"],
    "Greenland": ["Greenland"],
    "Brazil": ["Brazil"],
    "Argentina": ["Argentina"],
    "Chile": ["Chile"],
    "Peru": ["Peru"],
    "Colombia": ["Colombia"],
    "Venezuela": ["Venezuela"],
    "Ecuador": ["Ecuador"],
    "Bolivia": ["Bolivia"],
    "Paraguay": ["Paraguay"],
    "Uruguay": ["Uruguay"],
    "Guyana": ["Guyana"],
    "Suriname": ["Suriname"],
    "FrenchGuiana": ["France"],  # often part of France in NE
    "FalklandIslands": ["Falkland Is.", "Falkland Islands", "Falkland Islands / Malvinas"],
    "Australia": ["Australia"],
    "NewZealand": ["New Zealand"],
    "PapuaNewGuinea": ["Papua New Guinea"],
    "Fiji": ["Fiji"],
    "SolomonIslands": ["Solomon Is.", "Solomon Islands"],
    "Vanuatu": ["Vanuatu"],
    "NewCaledonia": ["New Caledonia"],
    "FrenchPolynesia": ["French Polynesia"],
    "Samoa": ["Samoa"],
    "Tonga": ["Tonga"],
    "Kiribati": ["Kiribati"],
    "Micronesia": ["Federated States of Micronesia", "Micronesia"],
    "FederatedStatesofMicronesia": ["Federated States of Micronesia", "Micronesia"],
    "MarshallIslands": ["Marshall Is.", "Marshall Islands"],
    "Palau": ["Palau"],
    "Nauru": ["Nauru"],
    "Tuvalu": ["Tuvalu"],
    "CookIslands": ["Cook Is.", "Cook Islands"],
    "Niue": ["Niue"],
    "Tokelau": ["Tokelau"],
    "AmericanSamoa": ["American Samoa"],
    "Guam": ["Guam"],
    "NorthernMarianaIslands": ["Northern Mariana Islands"],
    "NorfolkIsland": ["Norfolk Island"],
    "PitcairnIslands": ["Pitcairn Is.", "Pitcairn Islands"],
    "WallisAndFutuna": ["Wallis and Futuna", "Wallis and Futuna Islands", "Wallis and Futuna Is."],
    "ChristmasIsland": ["Christmas I.", "Christmas Island"],
    "Cocos(Keeling)Islands": ["Cocos (Keeling) Islands", "Cocos Is.", "Cocos Islands"],
    "Japan-hokkaido": ["Japan"],
    "Japan-fuji": ["Japan"],
    "EastTimor": ["East Timor", "Timor-Leste"],
    "Indonesia": ["Indonesia"],
    "Malaysia": ["Malaysia"],
    "Singapore": ["Singapore"],
    "Brunei": ["Brunei", "Brunei Darussalam"],
    "Philippines": ["Philippines"],
    "Thailand": ["Thailand"],
    "Vietnam": ["Vietnam"],
    "Cambodia": ["Cambodia"],
    "Laos": ["Laos"],
    "Myanmar": ["Myanmar"],
    "China": ["China"],
    "Taiwan": ["Taiwan"],
    "HongKong": ["Hong Kong", "Hong Kong S.A.R."],
    "Macau": ["Macao", "Macao S.A.R"],
    "Mongolia": ["Mongolia"],
    "NorthKorea": ["North Korea", "Dem. Rep. Korea"],
    "SouthKorea": ["South Korea", "Republic of Korea"],
    "Japan": ["Japan"],
    "India": ["India"],
    "Pakistan": ["Pakistan"],
    "Bangladesh": ["Bangladesh"],
    "SriLanka": ["Sri Lanka"],
    "Nepal": ["Nepal"],
    "Bhutan": ["Bhutan"],
    "Maldives": ["Maldives"],
    "Afghanistan": ["Afghanistan"],
    "Iran": ["Iran"],
    "Iraq": ["Iraq"],
    "SaudiArabia": ["Saudi Arabia"],
    "Yemen": ["Yemen"],
    "Oman": ["Oman"],
    "UnitedArabEmirates": ["United Arab Emirates"],
    "Qatar": ["Qatar"],
    "Kuwait": ["Kuwait"],
    "Bahrain": ["Bahrain"],
    "Jordan": ["Jordan"],
    "Lebanon": ["Lebanon"],
    "Syria": ["Syria"],
    "Israel": ["Israel"],
    "PalestinianAuthority": ["Palestine"],
    "Turkey": ["Turkey"],
    "Georgia": ["Georgia"],
    "Armenia": ["Armenia"],
    "Azerbaijan": ["Azerbaijan"],
    "Kazakhstan": ["Kazakhstan"],
    "Uzbekistan": ["Uzbekistan"],
    "Turkmenistan": ["Turkmenistan"],
    "Kyrgyzstan": ["Kyrgyzstan"],
    "Tajikistan": ["Tajikistan"],
    "Egypt": ["Egypt"],
    "Libya": ["Libya"],
    "Tunisia": ["Tunisia"],
    "Algeria": ["Algeria"],
    "Morocco": ["Morocco"],
    "WesternSahara": ["Western Sahara"],
    "Sudan": ["Sudan"],
    "SouthSudan": ["S. Sudan", "South Sudan"],
    "Ethiopia": ["Ethiopia"],
    "Eritrea": ["Eritrea"],
    "Djibouti": ["Djibouti"],
    "Somalia": ["Somalia"],
    "Somaliland": ["Somaliland"],
    "Kenya": ["Kenya"],
    "Uganda": ["Uganda"],
    "Tanzania": ["Tanzania", "United Republic of Tanzania"],
    "Rwanda": ["Rwanda"],
    "Burundi": ["Burundi"],
    "Madagascar": ["Madagascar"],
    "Mauritius": ["Mauritius"],
    "Seychelles": ["Seychelles"],
    "Comoros": ["Comoros"],
    "Mozambique": ["Mozambique"],
    "Malawi": ["Malawi"],
    "Zambia": ["Zambia"],
    "Zimbabwe": ["Zimbabwe"],
    "Botswana": ["Botswana"],
    "Namibia": ["Namibia"],
    "SouthAfrica": ["South Africa"],
    "Lesotho": ["Lesotho"],
    "Eswatini": ["eSwatini", "Kingdom of eSwatini"],
    "Angola": ["Angola"],
    "Congo": ["Republic of the Congo", "Congo"],
    "RepublicOfTheCongo": ["Republic of the Congo", "Congo"],
    "DemocraticRepublicOfTheCongo": ["Democratic Republic of the Congo", "Dem. Rep. Congo"],
    "Gabon": ["Gabon"],
    "EquatorialGuinea": ["Eq. Guinea", "Equatorial Guinea"],
    "Cameroon": ["Cameroon"],
    "CentralAfricanRepublic": ["Central African Rep.", "Central African Republic"],
    "Chad": ["Chad"],
    "Nigeria": ["Nigeria"],
    "Niger": ["Niger"],
    "Mali": ["Mali"],
    "BurkinaFaso": ["Burkina Faso"],
    "Benin": ["Benin"],
    "Togo": ["Togo"],
    "Ghana": ["Ghana"],
    "IvoryCoast": ["Ivory Coast", "Côte d'Ivoire"],
    "Liberia": ["Liberia"],
    "SierraLeone": ["Sierra Leone"],
    "Guinea": ["Guinea"],
    "Guinea-Bissau": ["Guinea-Bissau"],
    "Senegal": ["Senegal"],
    "Gambia": ["Gambia", "The Gambia"],
    "Mauritania": ["Mauritania"],
    "CapeVerde": ["Cape Verde", "Cabo Verde"],
    "SaoTomeAndPrincipe": ["São Tomé and Principe", "Sao Tome and Principe"],
}


def country_key_from_slug(slug: str) -> str:
    parts = slug.split("-")
    return "-".join(parts[3:]) if len(parts) > 3 else parts[-1]


def parse_world_md() -> list[dict]:
    text = WORLD.read_text(encoding="utf-8")
    continent = None
    region = None
    rows: list[dict] = []
    for line in text.splitlines():
        if line.startswith("# "):
            continent = line[2:].strip()
        elif line.startswith("## "):
            region = line[3:].strip()
        m = re.search(r"post_url\s+([^ %\}]+)", line)
        if m and region:
            slug = m.group(1).strip()
            country = country_key_from_slug(slug)
            rows.append(
                {
                    "slug": slug,
                    "country": country,
                    "continent": continent,
                    "region": region,
                    "ne_names": NE_ALIASES.get(country, [re.sub(r"(?<!^)(?=[A-Z])", " ", country)]),
                }
            )
    return rows


def main() -> None:
    rows = parse_world_md()
    # fill missing aliases with spaced CamelCase guess
    for r in rows:
        if r["country"] not in NE_ALIASES:
            guess = re.sub(r"(?<!^)(?=[A-Z])", " ", r["country"]).replace("(", " (").strip()
            r["ne_names"] = [guess, r["country"]]
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    missing_alias = [r["country"] for r in rows if r["country"] not in NE_ALIASES]
    print(f"Wrote {len(rows)} countries -> {OUT}")
    print(f"Without explicit alias: {len(missing_alias)}")
    if missing_alias:
        print(", ".join(missing_alias[:40]))


if __name__ == "__main__":
    main()
