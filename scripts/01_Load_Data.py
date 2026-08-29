"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
01_Load_Data.py

Purpose:
Load all raw datasets and confirm that Python can read them successfully.

Author:
Sufyan Yakubu
"""
# =========================================================
# SCRIPT STATUS
# =========================================================
#
# Status  : Completed ✅
# Version : 1.0
# Last Updated : 08 July 2026
#
# Output:
#   ✓ Fuel stations loaded
#   ✓ Universities loaded
#   ✓ Markets loaded
#   ✓ Malls loaded
#   ✓ Transport terminals loaded
#   ✓ Substations loaded
#   ✓ Population raster loaded
#
# Next Script:
#   02_Data_Preparation.py
#
# =========================================================
# =========================================================
# RESEARCH CONTRIBUTION
# =========================================================
#
# This script establishes the computational foundation
# of the PhD by importing all datasets into Python.
#
# Without this script, subsequent spatial analyses
# cannot be performed.
#
# =========================================================

from pathlib import Path
import geopandas as gpd
import rasterio

# 1. Project folder
from config import PROJECT_DIR

# 2. Raw data folders
RAW_DATA = PROJECT_DIR / "Data" / "Raw"

FUEL_DIR = RAW_DATA / "Fuel_Stations"
ACTIVITY_DIR = RAW_DATA / "Activity_Centres"
POPULATION_DIR = RAW_DATA / "Population"
SUBSTATION_DIR = RAW_DATA / "Substations"

# 3. File paths
fuel_file = FUEL_DIR / "Fuel_Stations_Accra.geojson"

malls_file = ACTIVITY_DIR / "Accra_Malls.geojson"
markets_file = ACTIVITY_DIR / "Accra_Markets.geojson"
terminals_file = ACTIVITY_DIR / "Accra_Transport_Terminal.geojson"
universities_file = ACTIVITY_DIR / "Accra_Universities.geojson"

substations_file = SUBSTATION_DIR / "Accra_Substations.geojson"

population_file = POPULATION_DIR / "gha_pop_2026_CN_100m_R2025A_v1.tif"

# 4. Load vector datasets
fuel_stations = gpd.read_file(fuel_file)
malls = gpd.read_file(malls_file)
markets = gpd.read_file(markets_file)
transport_terminals = gpd.read_file(terminals_file)
universities = gpd.read_file(universities_file)
substations = gpd.read_file(substations_file)

# 5. Load population raster
population = rasterio.open(population_file)

# 6. Print summary
print("DATA LOADING SUMMARY")
print("=" * 50)

print("Fuel stations:", len(fuel_stations))
print("Malls:", len(malls))
print("Markets:", len(markets))
print("Transport terminals:", len(transport_terminals))
print("Universities:", len(universities))
print("Substations:", len(substations))

print("\nCOORDINATE REFERENCE SYSTEMS")
print("=" * 50)

print("Fuel stations CRS:", fuel_stations.crs)
print("Malls CRS:", malls.crs)
print("Markets CRS:", markets.crs)
print("Transport terminals CRS:", transport_terminals.crs)
print("Universities CRS:", universities.crs)
print("Substations CRS:", substations.crs)
print("Population raster CRS:", population.crs)

print("\nPopulation raster size:")
print("Rows:", population.height)
print("Columns:", population.width)

print("\nAll datasets loaded successfully.")
