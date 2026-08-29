"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
03_Distance_Analysis.py

Research Objective:
Calculate proximity variables between existing fuel stations and
key activity centres/substations for EV charging site suitability analysis.

Author:
Sufyan Yakubu
"""

from pathlib import Path
import geopandas as gpd
# =====================================================
# Project folders
# =====================================================

from config import PROJECT_DIR

PROCESSED_DATA = PROJECT_DIR / "Data" / "Processed"
FINAL_DATA = PROJECT_DIR / "Data" / "Final"

# =====================================================
# Load processed datasets
# =====================================================

fuel_stations = gpd.read_file(PROCESSED_DATA / "Fuel_Stations_Accra_Projected.geojson")

universities = gpd.read_file(PROCESSED_DATA / "Universities_Projected.geojson")

markets = gpd.read_file(PROCESSED_DATA / "Markets_Projected.geojson")

malls = gpd.read_file(PROCESSED_DATA / "Malls_Projected.geojson")

transport_terminals = gpd.read_file(PROCESSED_DATA / "Transport_Terminals_Projected.geojson")

substations = gpd.read_file(PROCESSED_DATA / "Substations_Projected.geojson")
print("Fuel Stations:", len(fuel_stations))
print("Universities:", len(universities))
print("Markets:", len(markets))
print("Malls:", len(malls))
print("Transport Terminals:", len(transport_terminals))
print("Substations:", len(substations))

# =====================================================
# Calculate nearest distances
# =====================================================

analysis_layers = {
    "University": universities,
    "Market": markets,
    "Mall": malls,
    "Transport_Terminal": transport_terminals,
    "Substation": substations
}

results = fuel_stations.copy()

for layer_name, layer in analysis_layers.items():

    print(f"\nCalculating nearest {layer_name}...")

    joined = gpd.sjoin_nearest(
        results,
        layer,
        how="left",
        distance_col=f"Distance_to_{layer_name}_m"
    )

    results[f"Distance_to_{layer_name}_m"] = joined[
        f"Distance_to_{layer_name}_m"
    ]

print("\nDistance analysis completed successfully.")
print(results[[
    "name",
    "Distance_to_University_m",
    "Distance_to_Market_m",
    "Distance_to_Mall_m",
    "Distance_to_Transport_Terminal_m",
    "Distance_to_Substation_m"
]].head())
print("\nNumber of fuel stations analysed:", len(results))

print("\nMissing values in distance columns:")
print(results[[
    "Distance_to_University_m",
    "Distance_to_Market_m",
    "Distance_to_Mall_m",
    "Distance_to_Transport_Terminal_m",
    "Distance_to_Substation_m"
]].isnull().sum())
# =====================================================
# Save final distance analysis dataset
# =====================================================

output_file = FINAL_DATA / "Fuel_Stations_Distance_Analysis.geojson"

results.to_file(output_file, driver="GeoJSON")

print("\nDistance analysis dataset saved successfully.")

print(output_file)


