"""
Configuration file for steel tariff analysis project.
"""
from pathlib import Path
import os

# Project directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"

# Data collection parameters
START_YEAR = 2000
END_YEAR = 2025
SECTION_232_START = "2018-03"  # Section 232 steel tariffs enacted March 2018

# HS6 codes for steel products (Section 232-affected)
# These are the primary steel HS codes subject to Section 232 tariffs
STEEL_HS6_CODES = [
    # Flat-rolled products of iron or non-alloy steel
    "720810", "720825", "720826", "720827", "720836", "720837", "720838", "720839",
    "720840", "720851", "720852", "720853", "720854", "720890",
    "720915", "720916", "720917", "720918", "720925", "720926", "720927", "720990",
    "721011", "721012", "721020", "721030", "721041", "721049", "721050", "721061",
    "721069", "721070", "721090",
    "721113", "721114", "721119", "721123", "721129", "721190",
    "721210", "721220", "721230", "721240", "721250", "721260",
    "721310", "721320", "721391", "721399",
    "721410", "721420", "721430", "721491", "721499",
    # Bars and rods
    "721510", "721550", "721590",
    "721610", "721621", "721622", "721631", "721632", "721633", "721640", "721650",
    # Wire
    "721710", "721720", "721730", "721790",
    # Stainless steel
    "722011", "722012", "722020", "722090",
    "722100",
    "722211", "722219", "722220", "722230", "722240",
    # Tubes and pipes
    "730410", "730423", "730424", "730429", "730431", "730439", "730441", "730449",
    "730451", "730459", "730490",
]

# Control HS6 codes (non-steel products for comparison)
CONTROL_HS6_CODES = [
    # Aluminum products (also subject to Section 232 but useful for comparison)
    "760110", "760120", "760200",
    "760611", "760612", "760691", "760692",
    # Copper products (not subject to Section 232)
    "740311", "740312", "740313", "740319", "740321", "740322", "740329",
]

# API Keys (set via environment variables)
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

# USITC DataWeb (requires manual download)
USITC_BASE_URL = "https://dataweb.usitc.gov/"

# BLS API
BLS_API_KEY = os.getenv("BLS_API_KEY", "")
BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Import Price Index Series IDs (examples - adjust based on actual series)
BLS_IMPORT_PRICE_SERIES = {
    "steel_imports": "IR33112",  # Import price index - Steel mill products
}

# Producer Price Index Series IDs
BLS_PPI_SERIES = {
    "steel_domestic": "PCU33110033110",  # PPI - Steel mill products
}

# FRED series for macro controls
FRED_SERIES = {
    "oil_price": "DCOILWTICO",  # WTI Crude Oil Price
    "global_pmi": "USALOLITONOSTSAM",  # US Manufacturing PMI (proxy for global)
}

# Tariff rates
SECTION_232_TARIFF_RATE = 0.25  # 25% ad valorem tariff

# Country groupings
MAJOR_STEEL_EXPORTERS = [
    "China", "Japan", "South Korea", "Germany", "Taiwan", "Mexico", "Canada",
    "Brazil", "Turkey", "India"
]
