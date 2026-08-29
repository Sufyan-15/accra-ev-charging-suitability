"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
05_Normalization.py

Research Objective:
Standardize the residential population and proximity variables
to a common scale ranging from 0 to 1.

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
    / "Fuel_Stations_Population_Analysis.geojson"
)

# =====================================================
# 3. Load the analytical dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Population analysis dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Identify variables for normalization
# =====================================================

normalization_variables = [
    "Residential_Population_1km",
    "Distance_to_University_m",
    "Distance_to_Market_m",
    "Distance_to_Mall_m",
    "Distance_to_Transport_Terminal_m",
    "Distance_to_Substation_m"
]

print("\nVariables selected for normalization:")

for variable in normalization_variables:
    print(variable)

# =====================================================
# 5. Check missing values
# =====================================================

print("\nMissing values before normalization:")
print(
    fuel_stations[
        normalization_variables
    ].isnull().sum()
)

# =====================================================
# 6. Display original value ranges
# =====================================================

print("\nOriginal minimum and maximum values:")

for variable in normalization_variables:

    minimum_value = fuel_stations[variable].min()
    maximum_value = fuel_stations[variable].max()

    print(
        variable,
        "| Minimum:",
        minimum_value,
        "| Maximum:",
        maximum_value
    )
    
    # =====================================================
# 7. Normalize residential population
#    Benefit criterion: higher population is better
# =====================================================

population_column = "Residential_Population_1km"

population_minimum = fuel_stations[
    population_column
].min()

population_maximum = fuel_stations[
    population_column
].max()

fuel_stations["Norm_Residential_Population"] = (
    fuel_stations[population_column]
    - population_minimum
) / (
    population_maximum
    - population_minimum
)

print("\nResidential population normalized successfully.")

print("\nFirst five normalized population results:")
print(
    fuel_stations[[
        "name",
        "Residential_Population_1km",
        "Norm_Residential_Population"
    ]].head()
)

print("\nNormalized population range:")
print(
    "Minimum:",
    fuel_stations[
        "Norm_Residential_Population"
    ].min()
)

print(
    "Maximum:",
    fuel_stations[
        "Norm_Residential_Population"
    ].max()
)

# =====================================================
# 8. Define distance variables and output columns
# =====================================================

distance_variables = {
    "Distance_to_University_m": "Norm_University_Proximity",
    "Distance_to_Market_m": "Norm_Market_Proximity",
    "Distance_to_Mall_m": "Norm_Mall_Proximity",
    "Distance_to_Transport_Terminal_m": "Norm_Transport_Terminal_Proximity",
    "Distance_to_Substation_m": "Norm_Substation_Proximity"
}

# =====================================================
# 9. Normalize distance variables
#    Cost criteria: shorter distance is better
# =====================================================

for original_column, normalized_column in distance_variables.items():

    distance_minimum = fuel_stations[
        original_column
    ].min()

    distance_maximum = fuel_stations[
        original_column
    ].max()

    fuel_stations[normalized_column] = (
        distance_maximum
        - fuel_stations[original_column]
    ) / (
        distance_maximum
        - distance_minimum
    )

    print(
        "\nNormalized:",
        original_column,
        "as",
        normalized_column
    )

# =====================================================
# 10. Display the first five normalized results
# =====================================================

normalized_columns = [
    "Norm_Residential_Population",
    "Norm_University_Proximity",
    "Norm_Market_Proximity",
    "Norm_Mall_Proximity",
    "Norm_Transport_Terminal_Proximity",
    "Norm_Substation_Proximity"
]

print("\nFirst five normalized results:")

print(
    fuel_stations[
        ["name"] + normalized_columns
    ].head()
)

# =====================================================
# 11. Check normalized value ranges
# =====================================================

print("\nNormalized value ranges:")

for column in normalized_columns:

    print(
        column,
        "| Minimum:",
        fuel_stations[column].min(),
        "| Maximum:",
        fuel_stations[column].max()
    )
    
    # =====================================================
# 12. Check missing normalized values
# =====================================================

print("\nMissing values after normalization:")

print(
    fuel_stations[
        normalized_columns
    ].isnull().sum()
)

# =====================================================
# 13. Save the normalized dataset
# =====================================================

output_file = (
    FINAL_DATA
    / "Fuel_Stations_Normalized.geojson"
)

fuel_stations.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nNormalized dataset saved successfully.")
print(output_file)

print("\nNumber of fuel stations saved:", len(fuel_stations))
