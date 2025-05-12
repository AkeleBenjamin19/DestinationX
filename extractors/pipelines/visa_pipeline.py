import os
import re
from typing import Dict, List
from dotenv import load_dotenv
from restcountries_client import RestCountriesClient
from store import save_all
import aiohttp
from functools import lru_cache
import trafilatura
import pycountry
import json

# Global dictionary to accumulate results
visa_dict = {}

async def main():
    load_dotenv()
    os.makedirs('data', exist_ok=True)

    #---------VISA DATA EXTRACTION---------
    client    = RestCountriesClient()
    countries = client.get_countries()
    print(f"[Orchestrator] Starting sequential processing for {len(countries)} countries...")

    # Sequentially process each country
    for entry in countries:
        await worker(entry)

    #Finally, save the full dict
    save_all()
    print("[Orchestrator] All done.")
    #---------VISA DATA EXTRACTION---------

async def worker(entry):
    name    = entry['name']
    demonym = entry['demonym']
    print(f"[Orchestrator] Starting pipeline for {name} ({demonym})")

    # Fetch
    try:
        raw = await fetch_html(demonym)
    except Exception as e:
        print(f"[Orchestrator] ❌ Fetch failed for {name}: {e}")
        return  # skip to next country
    print(f"[Orchestrator] ✅ Fetched HTML for {name}")

    # Preprocess
    main_html = extract_main_html(raw)

    #Extractor
    extracted=extract_visa_info(main_html)
    print(f"[Orchestrator] ✅ Extracted data for {name}")


@lru_cache(maxsize=1000)
async def fetch_html(slug: str) -> str:
    """
    Async fetch and return raw HTML for a passport page slug.
    Slugs with ', ' get '-and-' instead of a comma, then spaces → dashes.
    """
    # Normalize slug: replace comma-space with '-and-' if present
    slug_norm = slug
    if ", " in slug_norm:
        slug_norm = slug_norm.replace(", ", "-and-")
    # Replace remaining spaces with dashes and lowercase
    slug_norm = slug_norm.replace(" ", "").lower()

    url = f"https://visaguide.world/visa-free-countries/{slug_norm}-passport/"
    print(f"[Fetcher] Downloading {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=10) as resp:
            resp.raise_for_status()
            html = await resp.text()
            print(f"[Fetcher] Completed download for {slug_norm}")
            return html

def extract_main_html(html: str) -> str:
    """
    Strip boilerplate, return main content HTML and save it to a file.
    """
    print("[Preprocessor] Extracting main HTML content...")
    summary = trafilatura.extract(html, include_comments=False, include_tables=False)
    print("[Preprocessor] Main HTML extraction complete")

    return summary

def extract_visa_info(html: str) -> Dict[str, List[str]]:
    """
    Parse the raw HTML as plain text: find each section by its heading regex,
    then collect all lines immediately below that start with "- ".
    Finally merge 'without_passport' into 'visa_free'.
    """
    # Define heading patterns (regex) for each category
    section_patterns = {
        "visa_free":        re.compile(r"Where Can .* Travel Without a Visa\?", re.I),
        "without_passport": re.compile(r"Where Can .* Go Without a Passport\?", re.I),
        "e_visa":           re.compile(r"What Countries Issue eVisa to .*", re.I),
        "visa_on_arrival":  re.compile(r"What Countries Issue Visa on Arrival to .*", re.I),
        "visa_required":    re.compile(r"Countries With Visa Requirements for .*", re.I),
    }

    # Prepare result dict
    data: Dict[str, List[str]] = {key: [] for key in section_patterns}

    current_key: str = None

    # Process line by line
    for raw_line in html.splitlines():
        line = raw_line.strip()

        # Check if this line matches any section heading
        for key, pattern in section_patterns.items():
            if pattern.search(line):
                current_key = key
                break
        else:
            # If not a heading, and we're inside a section, collect dash-list items
            if current_key and line.startswith("- "):
                country = line[2:].strip()
                data[current_key].append(country)

    # Merge "without_passport" entries into "visa_free"
    if data["without_passport"]:
        data["visa_free"].extend(data["without_passport"])

    return data

def append_visa_info(country: str, filepath: str = 'visa_dict.txt'):
    """
    Append a single country's visa info to the text file immediately after extraction.
    """
    if country not in visa_dict:
        print(f"[Store] ⚠ No data for {country}, skipping append.")
        return
    entry = visa_dict[country]
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f"\nvisa_dict['{country}'] = {json.dumps(entry, ensure_ascii=False)}\n")
    print(f"[Store] Appended {country} to {filepath}")

def store_visa_info(country: str, data: dict):
    print(f"[Store] Normalizing and storing data for {country}")
    visa_dict[country] = {
        'visa required':        normalize_countries(data.get('visa_required', [])),
        'e-visa':               normalize_countries(data.get('e_visa', [])),
        'visa on Arrival(eta)': normalize_countries(data.get('visa_on_arrival', [])),
        'visa free':            normalize_countries(data.get('visa_free', [])),
        'without a passport':   normalize_countries(data.get('without_passport', []))
    }

def normalize_countries(names: list[str]) -> list[str]:
    normalized = []
    for name in names:
        try:
            country = pycountry.countries.lookup(name)
            normalized.append(country.name)
        except LookupError:
            normalized.append(name)
    return sorted(set(normalized))

def save_all(filepath: str = 'visa_dict.txt'):
    print(f"[Store] Saving all data to {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('visa_dict = ' + json.dumps(visa_dict, ensure_ascii=False, indent=2))