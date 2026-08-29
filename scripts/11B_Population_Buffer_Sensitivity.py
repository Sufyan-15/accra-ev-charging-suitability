"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
11B_Population_Buffer_Sensitivity.py

Research Objective:
Test whether changing the residential population catchment from
1 km to 500 m or 2 km materially changes EV-charging suitability
scores and station rankings.

Author:
Sufyan Yakubu
"""

# =====================================================
# 1. Import Python libraries
# =====================================================

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio

from rasterio.mask import mask
from scipy.stats import spearmanr


# =====================================================
# 2. Define the project folders
# =====================================================

from config import PROJECT_DIR

RAW_DATA = PROJECT_DIR / "Data" / "Raw"
FINAL_DATA = PROJECT_DIR / "Data" / "Final"
RESULTS_DIR = PROJECT_DIR / "Results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# 3. Define the input files
# =====================================================

population_file = (
    RAW_DATA
    / "Population"
    / "gha_pop_2026_CN_100m_R2025A_v1.tif"
)

baseline_file = (
    FINAL_DATA
    / "Fuel_Stations_MCDA_Baseline.geojson"
)


# =====================================================
# 4. Check that the input files exist
# =====================================================

required_files = [
    population_file,
    baseline_file
]

for required_file in required_files:

    if not required_file.exists():

        raise FileNotFoundError(
            f"\nRequired input file was not found:\n{required_file}"
        )

print("Required input files found successfully.")


# =====================================================
# 5. Load the baseline MCDA dataset
# =====================================================

stations = gpd.read_file(baseline_file)

print("\nBaseline MCDA dataset loaded successfully.")
print("Number of fuel stations:", len(stations))
print("Dataset CRS:", stations.crs)


# =====================================================
# 6. Identify the required variables
# =====================================================

required_columns = [
    "Station_ID",
    "Residential_Population_1km",
    "Destination_Demand_Index",
    "Grid_Accessibility_Index",
    "Overall_Suitability_Index",
    "Overall_Suitability_Rank"
]

missing_columns = [
    column
    for column in required_columns
    if column not in stations.columns
]

if missing_columns:

    raise KeyError(
        "\nThe following required columns are missing:\n"
        + "\n".join(missing_columns)
    )

print("\nAll required analysis variables were found.")


# =====================================================
# 7. Check the station records
# =====================================================

if stations.crs is None:

    raise ValueError(
        "\nThe fuel-station dataset has no coordinate reference system."
    )

if not stations.crs.is_projected:

    raise ValueError(
        "\nThe fuel-station dataset must use a projected CRS "
        "before metre-based buffers can be created."
    )

if stations["Station_ID"].isnull().any():

    raise ValueError(
        "\nMissing Station_ID values were found."
    )

if stations["Station_ID"].duplicated().any():

    raise ValueError(
        "\nDuplicate Station_ID values were found."
    )

print("\nStation-record checks completed successfully.")
print("Number of unique station IDs:",
      stations["Station_ID"].nunique())


# =====================================================
# 8. Define the population normalization function
# =====================================================

def min_max_normalize(values):
    """
    Convert population values to a scale between 0 and 1.

    A station with the lowest population receives 0.
    A station with the highest population receives 1.
    """

    minimum_value = values.min()
    maximum_value = values.max()

    if maximum_value == minimum_value:

        raise ValueError(
            "\nNormalization cannot be completed because "
            "all population values are identical."
        )

    normalized_values = (
        (values - minimum_value)
        / (maximum_value - minimum_value)
    )

    return normalized_values

# =====================================================
# 9. Define the population calculation function
# =====================================================

def calculate_population(population_raster, buffer_geometry):
    """
    Calculate the total population contained within one buffer.

    Parameters
    ----------
    population_raster:
        The population raster opened with Rasterio.

    buffer_geometry:
        One fuel-station buffer transformed to the raster CRS.

    Returns
    -------
    int:
        Estimated population inside the buffer.
    """

    clipped_population, clipped_transform = mask(
        population_raster,
        [buffer_geometry],
        crop=True,
        filled=False,
        all_touched=False
    )

    population_values = clipped_population[0]

    valid_values = population_values.compressed()

    valid_values = valid_values[
        np.isfinite(valid_values)
    ]

    valid_values = valid_values[
        valid_values >= 0
    ]

    total_population = valid_values.sum()

    return int(round(total_population))


# =====================================================
# 10. Define the three buffer distances
# =====================================================

buffer_distances = {
    "500m": 500,
    "1km": 1000,
    "2km": 2000
}

print("\nPopulation buffer distances selected:")

for buffer_name, buffer_distance in buffer_distances.items():

    print(
        f"{buffer_name}: {buffer_distance} metres"
    )


# =====================================================
# 11. Open and inspect the population raster
# =====================================================

with rasterio.open(population_file) as population_raster:

    print("\nPopulation raster loaded successfully.")
    print("Population raster CRS:", population_raster.crs)
    print("Raster NoData value:", population_raster.nodata)

    if population_raster.crs is None:

        raise ValueError(
            "\nThe population raster has no coordinate "
            "reference system."
        )


    # =================================================
    # 12. Calculate population for each buffer distance
    # =================================================

    for buffer_name, buffer_distance in buffer_distances.items():

        print(
            f"\nCalculating population within "
            f"{buffer_name} buffers..."
        )

        # Create buffers in the projected station CRS.
        station_buffers = stations[
            ["Station_ID", "geometry"]
        ].copy()

        station_buffers["geometry"] = (
            station_buffers.geometry.buffer(
                buffer_distance
            )
        )

        # Transform the buffers to the raster CRS.
        raster_buffers = station_buffers.to_crs(
            population_raster.crs
        )

        population_results = []

        # Calculate population for every fuel station.
        for station_number, buffer_geometry in enumerate(
            raster_buffers.geometry,
            start=1
        ):

            population_total = calculate_population(
                population_raster,
                buffer_geometry
            )

            population_results.append(
                population_total
            )

            if (
                station_number % 25 == 0
                or station_number == len(raster_buffers)
            ):

                print(
                    f"{station_number} of "
                    f"{len(raster_buffers)} stations completed."
                )

        population_column = (
            f"Residential_Population_{buffer_name}"
        )

        stations[population_column] = (
            population_results
        )

        print(
            f"Population within {buffer_name} "
            "calculated successfully."
        )


# =====================================================
# 13. Display population results
# =====================================================

population_columns = [
    "Residential_Population_500m",
    "Residential_Population_1km",
    "Residential_Population_2km"
]

print("\nFirst five population-buffer results:")

print(
    stations[
        [
            "Station_ID",
            "name",
            *population_columns
        ]
    ].head()
)

print("\nPopulation summaries:")

print(
    stations[population_columns].describe()
)

# =====================================================
# 14. Check the calculated population values
# =====================================================

print("\nMissing population values:")

print(
    stations[population_columns].isnull().sum()
)

print("\nZero population values:")

for population_column in population_columns:

    zero_count = (
        stations[population_column] == 0
    ).sum()

    print(
        f"{population_column}: {zero_count}"
    )


# =====================================================
# 15. Normalize each population-buffer result
# =====================================================

population_scenarios = {
    "500m": "Residential_Population_500m",
    "1km": "Residential_Population_1km",
    "2km": "Residential_Population_2km"
}

for scenario_name, population_column in (
    population_scenarios.items()
):

    normalized_column = (
        f"Norm_Residential_Population_{scenario_name}"
    )

    stations[normalized_column] = (
        min_max_normalize(
            stations[population_column]
        )
    )

    print(
        f"\n{scenario_name} residential population "
        "normalized successfully."
    )

    print(
        "Minimum:",
        stations[normalized_column].min()
    )

    print(
        "Maximum:",
        stations[normalized_column].max()
    )


# =====================================================
# 16. Define the baseline MCDA weights
# =====================================================

residential_weight = 1 / 3
destination_weight = 1 / 3
grid_weight = 1 / 3

print("\nBaseline MCDA weights:")

print(
    "Residential Demand Index:",
    residential_weight
)

print(
    "Destination Demand Index:",
    destination_weight
)

print(
    "Grid Accessibility Index:",
    grid_weight
)

print(
    "Total weight:",
    residential_weight
    + destination_weight
    + grid_weight
)


# =====================================================
# 17. Recalculate suitability for each buffer
# =====================================================

for scenario_name in population_scenarios:

    normalized_population_column = (
        f"Norm_Residential_Population_{scenario_name}"
    )

    score_column = (
        f"Suitability_Score_{scenario_name}"
    )

    rank_column = (
        f"Suitability_Rank_{scenario_name}"
    )

    stations[score_column] = (
        residential_weight
        * stations[normalized_population_column]
        + destination_weight
        * stations["Destination_Demand_Index"]
        + grid_weight
        * stations["Grid_Accessibility_Index"]
    )

    stations[rank_column] = (
        stations[score_column]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    print(
        f"\nSuitability scores and ranks for "
        f"the {scenario_name} buffer calculated successfully."
    )


# =====================================================
# 18. Check the recalculated one-kilometre model
# =====================================================

stations["One_km_Score_Difference"] = abs(
    stations["Suitability_Score_1km"]
    - stations["Overall_Suitability_Index"]
)

stations["One_km_Rank_Difference"] = abs(
    stations["Suitability_Rank_1km"]
    - stations["Overall_Suitability_Rank"]
)

maximum_score_difference = (
    stations["One_km_Score_Difference"].max()
)

maximum_rank_difference = (
    stations["One_km_Rank_Difference"].max()
)

print("\nOne-kilometre baseline verification:")

print(
    "Maximum suitability-score difference:",
    maximum_score_difference
)

print(
    "Maximum rank difference:",
    maximum_rank_difference
)

if (
    maximum_score_difference <= 0.000001
    and maximum_rank_difference == 0
):

    print(
        "The recalculated 1 km model reproduces "
        "the original baseline model."
    )

else:

    print(
        "NOTICE: Small differences may result from "
        "recalculating the raster population values. "
        "The original Script 08 results remain the "
        "official baseline."
    )


# =====================================================
# 19. Display the top stations under each buffer
# =====================================================

for scenario_name in population_scenarios:

    score_column = (
        f"Suitability_Score_{scenario_name}"
    )

    rank_column = (
        f"Suitability_Rank_{scenario_name}"
    )

    top_stations = (
        stations[
            [
                "Station_ID",
                "name",
                score_column,
                rank_column
            ]
        ]
        .sort_values(rank_column)
        .head(10)
    )

    print(
        f"\nTop 10 stations using the "
        f"{scenario_name} population buffer:"
    )

    print(
        top_stations.to_string(index=False)
    )
    
  # =====================================================
# 20. Define the baseline ranking groups
# =====================================================

baseline_top_10 = set(
    stations.loc[
        stations["Overall_Suitability_Rank"] <= 10,
        "Station_ID"
    ]
)

baseline_top_22 = set(
    stations.loc[
        stations["Overall_Suitability_Rank"] <= 22,
        "Station_ID"
    ]
)


# =====================================================
# 21. Compare each buffer with the official baseline
# =====================================================

sensitivity_summary = []

for scenario_name in population_scenarios:

    rank_column = (
        f"Suitability_Rank_{scenario_name}"
    )

    scenario_top_10 = set(
        stations.loc[
            stations[rank_column] <= 10,
            "Station_ID"
        ]
    )

    scenario_top_22 = set(
        stations.loc[
            stations[rank_column] <= 22,
            "Station_ID"
        ]
    )

    rank_correlation, p_value = spearmanr(
        stations["Overall_Suitability_Rank"],
        stations[rank_column]
    )

    absolute_rank_change = abs(
        stations[rank_column]
        - stations["Overall_Suitability_Rank"]
    )

    top_10_overlap = len(
        baseline_top_10.intersection(
            scenario_top_10
        )
    )

    top_22_overlap = len(
        baseline_top_22.intersection(
            scenario_top_22
        )
    )

    sensitivity_summary.append(
        {
            "Population_Buffer": scenario_name,
            "Spearman_Rank_Correlation": rank_correlation,
            "Spearman_P_Value": p_value,
            "Top_10_Overlap": top_10_overlap,
            "Top_22_Overlap": top_22_overlap,
            "Mean_Absolute_Rank_Change":
                absolute_rank_change.mean(),
            "Maximum_Absolute_Rank_Change":
                absolute_rank_change.max()
        }
    )

sensitivity_summary = pd.DataFrame(
    sensitivity_summary
)


# =====================================================
# 22. Display the sensitivity summary
# =====================================================

print("\nPopulation-buffer sensitivity summary:")

print(
    sensitivity_summary.to_string(
        index=False
    )
)


# =====================================================
# 23. Calculate station-level rank changes
# =====================================================

stations["Rank_Change_500m"] = (
    stations["Suitability_Rank_500m"]
    - stations["Overall_Suitability_Rank"]
)

stations["Rank_Change_1km"] = (
    stations["Suitability_Rank_1km"]
    - stations["Overall_Suitability_Rank"]
)

stations["Rank_Change_2km"] = (
    stations["Suitability_Rank_2km"]
    - stations["Overall_Suitability_Rank"]
)

stations["Absolute_Rank_Change_500m"] = abs(
    stations["Rank_Change_500m"]
)

stations["Absolute_Rank_Change_1km"] = abs(
    stations["Rank_Change_1km"]
)

stations["Absolute_Rank_Change_2km"] = abs(
    stations["Rank_Change_2km"]
)


# =====================================================
# 24. Identify consistently high-ranked stations
# =====================================================

stations["Top22_Baseline"] = (
    stations["Overall_Suitability_Rank"] <= 22
)

stations["Top22_500m"] = (
    stations["Suitability_Rank_500m"] <= 22
)

stations["Top22_1km"] = (
    stations["Suitability_Rank_1km"] <= 22
)

stations["Top22_2km"] = (
    stations["Suitability_Rank_2km"] <= 22
)

top_22_columns = [
    "Top22_Baseline",
    "Top22_500m",
    "Top22_1km",
    "Top22_2km"
]

stations["Number_of_Top22_Appearances"] = (
    stations[top_22_columns]
    .astype(int)
    .sum(axis=1)
)

stations["Buffer_Robustness_Category"] = np.select(
    [
        stations["Number_of_Top22_Appearances"] == 4,
        stations["Number_of_Top22_Appearances"] == 3,
        stations["Number_of_Top22_Appearances"] == 2,
        stations["Number_of_Top22_Appearances"] == 1
    ],
    [
        "Consistently Top 22",
        "Top 22 in three models",
        "Top 22 in two models",
        "Top 22 in one model"
    ],
    default="Never Top 22"
)

print("\nBuffer-robustness category summary:")

print(
    stations[
        "Buffer_Robustness_Category"
    ].value_counts()
)


# =====================================================
# 25. Display consistently high-ranked stations
# =====================================================

robust_top_22 = (
    stations.loc[
        stations[
            "Buffer_Robustness_Category"
        ] == "Consistently Top 22",
        [
            "Station_ID",
            "name",
            "Overall_Suitability_Rank",
            "Suitability_Rank_500m",
            "Suitability_Rank_1km",
            "Suitability_Rank_2km",
            "Number_of_Top22_Appearances"
        ]
    ]
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

print(
    "\nStations that remain in the Top 22 "
    "under every population-buffer model:"
)

print(
    robust_top_22.to_string(
        index=False
    )
)


# =====================================================
# 26. Prepare the station-level results table
# =====================================================

station_result_columns = [
    "Station_ID",
    "name",
    "Residential_Population_500m",
    "Residential_Population_1km",
    "Residential_Population_2km",
    "Norm_Residential_Population_500m",
    "Norm_Residential_Population_1km",
    "Norm_Residential_Population_2km",
    "Overall_Suitability_Index",
    "Overall_Suitability_Rank",
    "Suitability_Score_500m",
    "Suitability_Rank_500m",
    "Suitability_Score_1km",
    "Suitability_Rank_1km",
    "Suitability_Score_2km",
    "Suitability_Rank_2km",
    "Rank_Change_500m",
    "Rank_Change_1km",
    "Rank_Change_2km",
    "Number_of_Top22_Appearances",
    "Buffer_Robustness_Category"
]

station_results = stations[
    station_result_columns
].copy()


# =====================================================
# 27. Define the output files
# =====================================================

station_results_file = (
    RESULTS_DIR
    / "Population_Buffer_Sensitivity_Station_Results.csv"
)

summary_file = (
    RESULTS_DIR
    / "Population_Buffer_Sensitivity_Summary.csv"
)

robust_top_22_file = (
    RESULTS_DIR
    / "Population_Buffer_Sensitivity_Robust_Top22.csv"
)

spatial_output_file = (
    FINAL_DATA
    / "Fuel_Stations_Population_Buffer_Sensitivity.geojson"
)


# =====================================================
# 28. Save the CSV results
# =====================================================

station_results.to_csv(
    station_results_file,
    index=False
)

sensitivity_summary.to_csv(
    summary_file,
    index=False
)

robust_top_22.to_csv(
    robust_top_22_file,
    index=False
)

print("\nStation-level sensitivity results saved successfully.")
print(station_results_file)

print("\nSensitivity summary saved successfully.")
print(summary_file)

print("\nRobust Top 22 results saved successfully.")
print(robust_top_22_file)


# =====================================================
# 29. Save the spatial sensitivity dataset
# =====================================================

stations.to_file(
    spatial_output_file,
    driver="GeoJSON"
)

print("\nSpatial sensitivity dataset saved successfully.")
print(spatial_output_file)


# =====================================================
# 30. Final completion message
# =====================================================

print(
    "\nPopulation-buffer sensitivity analysis "
    "completed successfully."
)

print(
    "\nThe 1 km population buffer remains the "
    "main methodological choice."
)

print(
    "The 500 m and 2 km buffers were used only "
    "to test the robustness of the results."
)

print(
    "\nNumber of fuel stations analysed:",
    len(stations)
)  
