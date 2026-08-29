"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
06_Destination_Demand_Index.py

Research Objective:
Construct a Destination Demand Index using normalized proximity
to universities, markets, malls and transport terminals.

Author:
Sufyan Yakubu
"""

from pathlib import Path
import geopandas as gpd

# =====================================================
# 1. Project folders
# =====================================================

from config import PROJECT_DIR

FINAL_DATA = PROJECT_DIR / "Data" / "Final"

# =====================================================
# 2. Input file
# =====================================================

input_file = (
    FINAL_DATA
    / "Fuel_Stations_Normalized.geojson"
)

# =====================================================
# 3. Load the normalized dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Normalized dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Create unique fuel-station IDs
# =====================================================

station_ids = [
    f"FS{number:03d}"
    for number in range(1, len(fuel_stations) + 1)
]

fuel_stations.insert(
    0,
    "Station_ID",
    station_ids
)

print("\nUnique station IDs created successfully.")

print("\nFirst five station IDs:")
print(
    fuel_stations[[
        "Station_ID",
        "name"
    ]].head()
)

print("\nNumber of unique station IDs:")
print(
    fuel_stations[
        "Station_ID"
    ].nunique()
)

# =====================================================
# 5. Identify DDI variables
# =====================================================

ddi_variables = [
    "Norm_University_Proximity",
    "Norm_Market_Proximity",
    "Norm_Mall_Proximity",
    "Norm_Transport_Terminal_Proximity"
]

print("\nDestination Demand Index variables:")

for variable in ddi_variables:
    print(variable)

print("\nMissing values in DDI variables:")
print(
    fuel_stations[
        ddi_variables
    ].isnull().sum()
)

# =====================================================
# 6. Assign equal destination weights
# =====================================================

destination_weights = {
    "Norm_University_Proximity": 0.25,
    "Norm_Market_Proximity": 0.25,
    "Norm_Mall_Proximity": 0.25,
    "Norm_Transport_Terminal_Proximity": 0.25
}

total_weight = sum(
    destination_weights.values()
)

print("\nDestination weights:")

for variable, weight in destination_weights.items():
    print(variable, "=", weight)

print("\nTotal destination weight:", total_weight)

# =====================================================
# 7. Calculate the Destination Demand Index
# =====================================================

fuel_stations["Destination_Demand_Index"] = 0.0

for variable, weight in destination_weights.items():

    fuel_stations["Destination_Demand_Index"] += (
        fuel_stations[variable] * weight
    )

print("\nDestination Demand Index calculated successfully.")

# =====================================================
# 8. Display the first five DDI results
# =====================================================

print("\nFirst five Destination Demand Index results:")

print(
    fuel_stations[[
        "Station_ID",
        "name",
        "Destination_Demand_Index"
    ]].head()
)

# =====================================================
# 9. Check the DDI range and distribution
# =====================================================

print("\nDestination Demand Index summary:")

print(
    fuel_stations[
        "Destination_Demand_Index"
    ].describe()
)

print("\nDDI minimum:")
print(
    fuel_stations[
        "Destination_Demand_Index"
    ].min()
)

print("\nDDI maximum:")
print(
    fuel_stations[
        "Destination_Demand_Index"
    ].max()
)

# =====================================================
# 10. Rank stations by Destination Demand Index
# =====================================================

fuel_stations["DDI_Rank"] = (
    fuel_stations[
        "Destination_Demand_Index"
    ]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

print("\nFuel stations ranked by destination demand.")

print("\nTop 10 stations by Destination Demand Index:")

top_10_ddi = fuel_stations.sort_values(
    by="Destination_Demand_Index",
    ascending=False
)

print(
    top_10_ddi[[
        "DDI_Rank",
        "Station_ID",
        "name",
        "Destination_Demand_Index"
    ]].head(10)
)

# =====================================================
# 11. Check the final DDI results
# =====================================================

print("\nMissing Destination Demand Index values:")
print(
    fuel_stations[
        "Destination_Demand_Index"
    ].isnull().sum()
)

print("\nNumber of stations ranked:")
print(
    fuel_stations[
        "DDI_Rank"
    ].count()
)

# =====================================================
# 12. Save the DDI dataset
# =====================================================

output_file = (
    FINAL_DATA
    / "Fuel_Stations_Destination_Demand.geojson"
)

fuel_stations.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nDestination Demand dataset saved successfully.")
print(output_file)

print("\nNumber of fuel stations saved:", len(fuel_stations))

