"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
02_Data_Preparation.py

Research Objective:
Check the quality of the spatial datasets and prepare them for
distance-based spatial analysis.

Author:
Sufyan Yakubu
"""
from pathlib import Path
import geopandas as gpd
import rasterio
# Project folder
from config import PROJECT_DIR

RAW_DATA = PROJECT_DIR / "Data" / "Raw"
PROCESSED_DATA = PROJECT_DIR / "Data" / "Processed"

FUEL_DIR = RAW_DATA / "Fuel_Stations"
ACTIVITY_DIR = RAW_DATA / "Activity_Centres"
POPULATION_DIR = RAW_DATA / "Population"
SUBSTATION_DIR = RAW_DATA / "Substations"
fuel_file = FUEL_DIR / "Fuel_Stations_Accra.geojson"

fuel_stations = gpd.read_file(fuel_file)

universities = gpd.read_file(ACTIVITY_DIR / "Accra_Universities.geojson")
markets = gpd.read_file(ACTIVITY_DIR / "Accra_Markets.geojson")
malls = gpd.read_file(ACTIVITY_DIR / "Accra_Malls.geojson")
transport_terminals = gpd.read_file(ACTIVITY_DIR / "Accra_Transport_Terminal.geojson")
substations = gpd.read_file(SUBSTATION_DIR / "Accra_Substations.geojson")

print(fuel_stations.columns)
# =====================================================
# Check for missing geometries
# =====================================================

missing_geometry = fuel_stations.geometry.isnull().sum()

print("\nMissing geometries:", missing_geometry)
# =====================================================
# Check for duplicate fuel stations
# =====================================================

duplicate_stations = fuel_stations.duplicated().sum()

print("Duplicate records:", duplicate_stations)
# =====================================================
# Reproject fuel stations to a projected CRS in metres
# =====================================================

PROJECTED_CRS = "EPSG:32630"

fuel_stations_projected = fuel_stations.to_crs(PROJECTED_CRS)

print("\nOriginal CRS:", fuel_stations.crs)
print("Projected CRS:", fuel_stations_projected.crs)

print("\nFirst 5 projected geometries:")
print(fuel_stations_projected.geometry.head())
# =====================================================
# Project and save all vector datasets
# =====================================================

datasets = {
    "Fuel_Stations_Accra": fuel_stations,
    "Universities": universities,
    "Markets": markets,
    "Malls": malls,
    "Transport_Terminals": transport_terminals,
    "Substations": substations
}

for name, dataset in datasets.items():

    print("\nProcessing:", name)

    projected_dataset = dataset.to_crs(PROJECTED_CRS)

    output_file = PROCESSED_DATA / f"{name}_Projected.geojson"

    projected_dataset.to_file(output_file, driver="GeoJSON")

    print("Saved:", output_file)
    
    
    

    
