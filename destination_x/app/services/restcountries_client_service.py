""" RestCountriesClient Service
This module contains the RestCountriesClient class which is responsible for
fetching country data from the RestCountries API."""

__author__ = "Akele Benjamin(620130803)"
import requests
from requests.exceptions import RequestException
from typing import List, Dict

class RestCountriesClient:
    BASE_URL = "https://restcountries.com/v3.1/all"
    continent_code_map = {
        "Africa":         "AF",
        "Antarctica":     "AN",
        "Asia":           "AS",
        "Europe":         "EU",
        "North America":  "NA",
        "Oceania":        "OC",
        "South America":  "SA",
    }

    def get_countries(self) -> List[Dict[str, str]]:
        resp = requests.get(self.BASE_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        countries = []
        for entry in data:
            name = entry.get("name", {}).get("common")
            demonyms = entry.get("demonyms", {}).get("eng", {})
            demonym = demonyms.get("m") or demonyms.get("f")
            country_code = entry.get("cca2")

            # get the continent name and now its 2-letter code
            cont_list = entry.get("continents", [])
            continent = cont_list[0] if cont_list else None
            continent_code = self.continent_code_map.get(continent)

            if all([name, demonym, country_code, continent_code]):
                countries.append({
                    "name":           name,
                    "demonym":        demonym,
                    "country_code":   country_code,
                    "continent":      continent,
                    "continent_code": continent_code,
                })

        return sorted(countries, key=lambda x: x["name"])
