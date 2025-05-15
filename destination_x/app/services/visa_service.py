""" Visa Service Module
This module contains functions to fetch, process, and store visa information
for various countries. It includes functions to fetch HTML content from
visaguide.world, extract visa information, and save it to a database."""


__author__ = "Akele Benjamin(620130803)"
import os
import re
import aiohttp
import trafilatura
import pycountry
import json
from typing import Dict, List
from dotenv import load_dotenv
from app.models.country import Country
from app.models.visa_policy import VisaPolicy
from app.services.restcountries_client_service import RestCountriesClient
from .. import db


from functools import lru_cache


# Global dictionary to accumulate results
visa_dict = {}


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

def save_visa_policies(origin_country_name: str,
                       visa_data: Dict[str, List[str]]) -> None:
    """
    Given an origin country (by name) and a dict mapping:
      {
        "visa_free": [...],
        "e_visa": [...],
        "visa_on_arrival": [...],
        "visa_required": [...]
      }
    this will:
      1. Look up the origin Country record.
      2. Delete any existing VisaPolicy rows for that origin.
      3. For each destination, create a new VisaPolicy with the correct flags.
      4. Commit all changes in one transaction.
    """
    # 1) fetch origin country
    origin = Country.query.filter_by(name=origin_country_name).first()
    if not origin:
        raise ValueError(f"Origin country '{origin_country_name}' not found")

    # 2) delete old policies for this origin
    VisaPolicy.query.filter_by(origin_id=origin.id).delete()

    # 3) build a map of country name → id
    countries = Country.query.all()
    name_to_id = {c.name: c.id for c in countries}

    # 4) gather every destination mentioned
    all_destinations = set()
    for lst in visa_data.values():
        all_destinations.update(lst)

    # 5) insert new policies
    for dest_name in all_destinations:
        dest_id = name_to_id.get(dest_name)
        if not dest_id:
            print(f"[Store] ❌ Destination '{dest_name}' not found, skipping.")
            continue

        policy = VisaPolicy(
            origin_id       = origin.id,
            destination_id  = dest_id,
            visa_free       = dest_name in visa_data.get("visa_free", []),
            e_visa          = dest_name in visa_data.get("e_visa", []),
            visa_on_arrival = dest_name in visa_data.get("visa_on_arrival", []),
            visa_required   = dest_name in visa_data.get("visa_required", [])
        )
        db.session.add(policy)

    # 6) commit once at the end
    db.session.commit()

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