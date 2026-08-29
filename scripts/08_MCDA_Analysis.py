"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
08_MCDA_Analysis.py

Research Objective:
Calculate a baseline Overall Suitability Index for candidate
fuel stations using equal weights for residential demand,
destination demand and grid accessibility.

MCDA Method:
Equal-weight Weighted Linear Combination

Important Interpretation:
The result represents preliminary spatial suitability.
It does not confirm physical site feasibility or available
electrical network capacity.

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
    / "Fuel_Stations_Grid_Accessibility.geojson"
)

# =====================================================
# 3. Load the Grid Accessibility dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Grid Accessibility dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Create the Residential Demand Index
# =====================================================

fuel_stations["Residential_Demand_Index"] = (
    fuel_stations[
        "Norm_Residential_Population"
    ]
)

print("\nResidential Demand Index created successfully.")

# =====================================================
# 5. Create the Demand Potential Index
# =====================================================

fuel_stations["Demand_Potential_Index"] = (
    0.50
    * fuel_stations[
        "Residential_Demand_Index"
    ]
    +
    0.50
    * fuel_stations[
        "Destination_Demand_Index"
    ]
)

print("\nDemand Potential Index created successfully.")

# =====================================================
# 6. Define the baseline MCDA criteria
# =====================================================

mcda_weights = {
    "Residential_Demand_Index": 1 / 3,
    "Destination_Demand_Index": 1 / 3,
    "Grid_Accessibility_Index": 1 / 3
}

print("\nBaseline MCDA weights:")

for criterion, weight in mcda_weights.items():
    print(
        criterion,
        "=",
        round(weight, 4)
    )

total_weight = sum(
    mcda_weights.values()
)

print("\nTotal MCDA weight:", total_weight)

# =====================================================
# 7. Calculate the Overall Suitability Index
# =====================================================

fuel_stations["Overall_Suitability_Index"] = 0.0

for criterion, weight in mcda_weights.items():

    fuel_stations[
        "Overall_Suitability_Index"
    ] += (
        fuel_stations[criterion]
        * weight
    )

print("\nOverall Suitability Index calculated successfully.")

# =====================================================
# 8. Check the suitability-score distribution
# =====================================================

print("\nOverall Suitability Index summary:")

print(
    fuel_stations[
        "Overall_Suitability_Index"
    ].describe()
)

print("\nOverall Suitability Index range:")

print(
    "Minimum:",
    fuel_stations[
        "Overall_Suitability_Index"
    ].min()
)

print(
    "Maximum:",
    fuel_stations[
        "Overall_Suitability_Index"
    ].max()
)

# =====================================================
# 9. Rank stations by overall suitability
# =====================================================

fuel_stations["Overall_Suitability_Rank"] = (
    fuel_stations[
        "Overall_Suitability_Index"
    ]
    .rank(
        ascending=False,
        method="min"
    )
    .astype(int)
)

print("\nFuel stations ranked by overall suitability.")

# =====================================================
# 10. Display the top 10 candidate stations
# =====================================================

top_10_candidates = fuel_stations.sort_values(
    by="Overall_Suitability_Index",
    ascending=False
)

print("\nTop 10 stations in the baseline MCDA model:")

print(
    top_10_candidates[[
        "Overall_Suitability_Rank",
        "Station_ID",
        "name",
        "Residential_Demand_Index",
        "Destination_Demand_Index",
        "Grid_Accessibility_Index",
        "Overall_Suitability_Index"
    ]].head(10)
)

# =====================================================
# 11. Quality checks
# =====================================================

mcda_output_columns = [
    "Residential_Demand_Index",
    "Destination_Demand_Index",
    "Grid_Accessibility_Index",
    "Demand_Potential_Index",
    "Overall_Suitability_Index",
    "Overall_Suitability_Rank"
]

print("\nMissing MCDA output values:")

print(
    fuel_stations[
        mcda_output_columns
    ].isnull().sum()
)

print("\nNumber of stations ranked:")

print(
    fuel_stations[
        "Overall_Suitability_Rank"
    ].count()
)

# =====================================================
# 12. Save the baseline MCDA dataset
# =====================================================

output_file = (
    FINAL_DATA
    / "Fuel_Stations_MCDA_Baseline.geojson"
)

fuel_stations.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nBaseline MCDA dataset saved successfully.")
print(output_file)

print("\nNumber of fuel stations saved:", len(fuel_stations))

