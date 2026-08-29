"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
07_Grid_Suitability_Analysis.py

Research Objective:
Construct a planning-level Grid Accessibility Index using
the normalized distance from each candidate fuel station
to its nearest electrical substation.

Important Interpretation:
The index represents relative proximity to major grid
infrastructure. It does not confirm available grid capacity,
feeder capacity, transformer loading or connection approval.

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
    / "Fuel_Stations_Destination_Demand.geojson"
)

# =====================================================
# 3. Load the Destination Demand dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Destination Demand dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Identify grid-accessibility variables
# =====================================================

grid_variables = [
    "Distance_to_Substation_m",
    "Norm_Substation_Proximity"
]

print("\nGrid-accessibility variables:")

for variable in grid_variables:
    print(variable)

print("\nMissing values in grid variables:")
print(
    fuel_stations[
        grid_variables
    ].isnull().sum()
)

# =====================================================
# 5. Create the Grid Accessibility Index
# =====================================================

fuel_stations["Grid_Accessibility_Index"] = (
    fuel_stations[
        "Norm_Substation_Proximity"
    ]
)

print("\nGrid Accessibility Index created successfully.")

# =====================================================
# 6. Check the Grid Accessibility Index
# =====================================================

print("\nGrid Accessibility Index summary:")

print(
    fuel_stations[
        "Grid_Accessibility_Index"
    ].describe()
)

print("\nGrid Accessibility Index range:")

print(
    "Minimum:",
    fuel_stations[
        "Grid_Accessibility_Index"
    ].min()
)

print(
    "Maximum:",
    fuel_stations[
        "Grid_Accessibility_Index"
    ].max()
)

# =====================================================
# 7. Rank stations by grid accessibility
# =====================================================

fuel_stations["Grid_Accessibility_Rank"] = (
    fuel_stations[
        "Grid_Accessibility_Index"
    ]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

print("\nFuel stations ranked by grid accessibility.")

# =====================================================
# 8. Display top 10 grid-accessible stations
# =====================================================

top_10_grid = fuel_stations.sort_values(
    by="Grid_Accessibility_Index",
    ascending=False
)

print("\nTop 10 stations by Grid Accessibility Index:")

print(
    top_10_grid[[
        "Grid_Accessibility_Rank",
        "Station_ID",
        "name",
        "Distance_to_Substation_m",
        "Grid_Accessibility_Index"
    ]].head(10)
)

# =====================================================
# 9. Final quality checks
# =====================================================

print("\nMissing Grid Accessibility Index values:")

print(
    fuel_stations[
        "Grid_Accessibility_Index"
    ].isnull().sum()
)

print("\nNumber of stations ranked:")

print(
    fuel_stations[
        "Grid_Accessibility_Rank"
    ].count()
)

# =====================================================
# 10. Save the Grid Accessibility dataset
# =====================================================

output_file = (
    FINAL_DATA
    / "Fuel_Stations_Grid_Accessibility.geojson"
)

fuel_stations.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nGrid Accessibility dataset saved successfully.")
print(output_file)

print("\nNumber of fuel stations saved:", len(fuel_stations))

