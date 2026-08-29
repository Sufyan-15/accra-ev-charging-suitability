"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
11_Sensitivity_Analysis.py

Research Objective:
Test the stability of fuel-station suitability rankings under
alternative MCDA weighting scenarios.

Important Methodological Note:
Substation proximity is treated as a grid-accessibility proxy.
It does not directly measure transformer capacity, feeder loading,
connection cost or the technical ability to supply EV chargers.

Author:
Sufyan Yakubu
"""

# =====================================================
# 1. Import Python libraries
# =====================================================

from pathlib import Path

import pandas as pd
import geopandas as gpd


# =====================================================
# 2. Define project folders
# =====================================================

from config import PROJECT_DIR

FINAL_DATA = (
    PROJECT_DIR
    / "Data"
    / "Final"
)

RESULTS_DIR = (
    PROJECT_DIR
    / "Results"
)


# =====================================================
# 3. Define input file
# =====================================================

input_file = (
    FINAL_DATA
    / "Fuel_Stations_MCDA_Baseline.geojson"
)


# =====================================================
# 4. Define output files
# =====================================================

spatial_output_file = (
    FINAL_DATA
    / "Fuel_Stations_Sensitivity_Analysis.geojson"
)

station_results_file = (
    RESULTS_DIR
    / "Sensitivity_Analysis_Station_Results.csv"
)

scenario_summary_file = (
    RESULTS_DIR
    / "Sensitivity_Analysis_Scenario_Summary.csv"
)

robust_candidates_file = (
    RESULTS_DIR
    / "Sensitivity_Analysis_Robust_Top22.csv"
)


# =====================================================
# 5. Check that the input file exists
# =====================================================

if not input_file.exists():

    raise FileNotFoundError(
        f"MCDA baseline dataset not found:\n"
        f"{input_file}"
    )


print("MCDA baseline input file found successfully.")


# =====================================================
# 6. Load the MCDA baseline dataset
# =====================================================

stations = gpd.read_file(input_file)


print("\nMCDA baseline dataset loaded successfully.")
print("Number of fuel stations:", len(stations))
print("Dataset CRS:", stations.crs)


# =====================================================
# 7. Define the MCDA variables
# =====================================================

residential_variable = (
    "Residential_Demand_Index"
)

destination_variable = (
    "Destination_Demand_Index"
)

grid_variable = (
    "Grid_Accessibility_Index"
)


required_variables = [
    residential_variable,
    destination_variable,
    grid_variable
]


print("\nVariables used in sensitivity analysis:")

for variable in required_variables:

    print(variable)


# =====================================================
# 8. Check that the required variables exist
# =====================================================

missing_columns = [
    variable
    for variable in required_variables
    if variable not in stations.columns
]


if len(missing_columns) > 0:

    raise KeyError(
        "\nThe following required variables are missing:\n"
        f"{missing_columns}"
    )


print("\nAll required MCDA variables were found.")


# =====================================================
# 9. Check for missing values
# =====================================================

print("\nMissing values in MCDA variables:")

print(
    stations[
        required_variables
    ].isnull().sum()
)


total_missing_values = (
    stations[
        required_variables
    ].isnull().sum().sum()
)


if total_missing_values > 0:

    raise ValueError(
        "Missing values were found in the MCDA variables."
    )


print("\nNo missing MCDA values were found.")


# =====================================================
# 10. Check the ranges of the normalized indices
# =====================================================

print("\nMCDA variable ranges:")

for variable in required_variables:

    minimum_value = stations[variable].min()
    maximum_value = stations[variable].max()

    print(
        f"{variable} | "
        f"Minimum: {minimum_value:.6f} | "
        f"Maximum: {maximum_value:.6f}"
    )


# =====================================================
# 11. Define the sensitivity scenarios
# =====================================================

sensitivity_scenarios = {

    "Baseline": {
        "Residential": 1 / 3,
        "Destination": 1 / 3,
        "Grid": 1 / 3
    },

    "Residential_Priority": {
        "Residential": 0.50,
        "Destination": 0.30,
        "Grid": 0.20
    },

    "Destination_Priority": {
        "Residential": 0.30,
        "Destination": 0.50,
        "Grid": 0.20
    },

    "Grid_Priority": {
        "Residential": 0.30,
        "Destination": 0.30,
        "Grid": 0.40
    },

    "Demand_Priority": {
        "Residential": 0.40,
        "Destination": 0.40,
        "Grid": 0.20
    }
}


print("\nSensitivity-analysis scenarios:")

for scenario_name, weights in (
    sensitivity_scenarios.items()
):

    total_weight = sum(weights.values())

    print(f"\n{scenario_name}")

    print(
        "Residential weight:",
        weights["Residential"]
    )

    print(
        "Destination weight:",
        weights["Destination"]
    )

    print(
        "Grid weight:",
        weights["Grid"]
    )

    print(
        "Total weight:",
        round(total_weight, 6)
    )


# =====================================================
# 12. Validate scenario weights
# =====================================================

for scenario_name, weights in (
    sensitivity_scenarios.items()
):

    total_weight = sum(weights.values())

    if abs(total_weight - 1.0) > 0.000001:

        raise ValueError(
            f"Weights for {scenario_name} "
            f"do not sum to 1.0."
        )


print("\nAll scenario weights sum to 1.0.")


# =====================================================
# 13. Calculate suitability scores and ranks
# =====================================================

score_columns = []
rank_columns = []


for scenario_name, weights in (
    sensitivity_scenarios.items()
):

    score_column = (
        f"Sensitivity_Score_{scenario_name}"
    )

    rank_column = (
        f"Sensitivity_Rank_{scenario_name}"
    )

    stations[score_column] = (

        weights["Residential"]
        * stations[residential_variable]

        + weights["Destination"]
        * stations[destination_variable]

        + weights["Grid"]
        * stations[grid_variable]
    )

    stations[rank_column] = (

        stations[score_column]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    score_columns.append(score_column)
    rank_columns.append(rank_column)

    print(
        f"\n{scenario_name} scores and "
        f"ranks calculated successfully."
    )


# =====================================================
# 14. Compare recalculated baseline with Script 08
# =====================================================

if "Overall_Suitability_Index" in stations.columns:

    stations["Baseline_Score_Difference"] = (

        stations["Sensitivity_Score_Baseline"]

        - stations["Overall_Suitability_Index"]
    ).abs()

    maximum_baseline_difference = (
        stations["Baseline_Score_Difference"].max()
    )

    print(
        "\nMaximum difference between the "
        "recalculated baseline score and "
        "the Script 08 baseline score:"
    )

    print(maximum_baseline_difference)


if "Overall_Suitability_Rank" in stations.columns:

    stations["Baseline_Rank_Difference"] = (

        stations["Sensitivity_Rank_Baseline"]

        - stations["Overall_Suitability_Rank"]
    )

    maximum_baseline_rank_difference = (

        stations["Baseline_Rank_Difference"]
        .abs()
        .max()
    )

    print(
        "\nMaximum baseline rank difference:"
    )

    print(maximum_baseline_rank_difference)


# =====================================================
# 15. Calculate rank changes from the baseline
# =====================================================

baseline_rank_column = (
    "Sensitivity_Rank_Baseline"
)


for scenario_name in sensitivity_scenarios:

    if scenario_name == "Baseline":

        continue

    rank_column = (
        f"Sensitivity_Rank_{scenario_name}"
    )

    rank_change_column = (
        f"Rank_Change_{scenario_name}"
    )

    absolute_change_column = (
        f"Absolute_Rank_Change_{scenario_name}"
    )

    stations[rank_change_column] = (

        stations[rank_column]

        - stations[baseline_rank_column]
    )

    stations[absolute_change_column] = (

        stations[rank_change_column].abs()
    )


print(
    "\nRank changes from the baseline "
    "calculated successfully."
)


# =====================================================
# 16. Calculate average rank and rank variability
# =====================================================

stations["Sensitivity_Mean_Rank"] = (

    stations[rank_columns].mean(axis=1)
)


stations["Sensitivity_Rank_Std"] = (

    stations[rank_columns].std(
        axis=1,
        ddof=0
    )
)


stations["Sensitivity_Best_Rank"] = (

    stations[rank_columns].min(axis=1)
)


stations["Sensitivity_Worst_Rank"] = (

    stations[rank_columns].max(axis=1)
)


stations["Sensitivity_Rank_Range"] = (

    stations["Sensitivity_Worst_Rank"]

    - stations["Sensitivity_Best_Rank"]
)


print(
    "\nMean rank and rank variability "
    "calculated successfully."
)


# =====================================================
# 17. Count top-10 and top-22 appearances
# =====================================================

top_10_columns = []
top_22_columns = []


for scenario_name in sensitivity_scenarios:

    rank_column = (
        f"Sensitivity_Rank_{scenario_name}"
    )

    top_10_column = (
        f"Top10_{scenario_name}"
    )

    top_22_column = (
        f"Top22_{scenario_name}"
    )

    stations[top_10_column] = (
        stations[rank_column] <= 10
    )

    stations[top_22_column] = (
        stations[rank_column] <= 22
    )

    top_10_columns.append(top_10_column)
    top_22_columns.append(top_22_column)


stations["Top10_Appearance_Count"] = (

    stations[top_10_columns]
    .sum(axis=1)
    .astype(int)
)


stations["Top22_Appearance_Count"] = (

    stations[top_22_columns]
    .sum(axis=1)
    .astype(int)
)


print(
    "\nTop-10 and top-22 appearance counts "
    "calculated successfully."
)


# =====================================================
# 18. Assign ranking-robustness categories
# =====================================================

def assign_robustness_category(
    top_22_count
):

    if top_22_count == 5:

        return "Very robust"

    elif top_22_count == 4:

        return "Robust"

    elif top_22_count in [2, 3]:

        return "Moderately robust"

    elif top_22_count == 1:

        return "Scenario-sensitive"

    else:

        return "Not selected in top 22"


stations["Ranking_Robustness"] = (

    stations["Top22_Appearance_Count"]
    .apply(assign_robustness_category)
)


print(
    "\nRanking-robustness categories "
    "assigned successfully."
)


# =====================================================
# 19. Calculate Spearman rank correlations
# =====================================================

scenario_summary_records = []


baseline_top_10 = set(

    stations.loc[
        stations[baseline_rank_column] <= 10,
        "Station_ID"
    ]
)


baseline_top_22 = set(

    stations.loc[
        stations[baseline_rank_column] <= 22,
        "Station_ID"
    ]
)


for scenario_name, weights in (
    sensitivity_scenarios.items()
):

    rank_column = (
        f"Sensitivity_Rank_{scenario_name}"
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

    spearman_correlation = (

        stations[baseline_rank_column]
        .corr(
            stations[rank_column],
            method="spearman"
        )
    )

    mean_absolute_rank_change = (

        (
            stations[rank_column]
            - stations[baseline_rank_column]
        )
        .abs()
        .mean()
    )

    maximum_absolute_rank_change = (

        (
            stations[rank_column]
            - stations[baseline_rank_column]
        )
        .abs()
        .max()
    )

    scenario_summary_records.append({

        "Scenario": scenario_name,

        "Residential_Weight":
            weights["Residential"],

        "Destination_Weight":
            weights["Destination"],

        "Grid_Weight":
            weights["Grid"],

        "Spearman_Correlation_With_Baseline":
            spearman_correlation,

        "Top10_Overlap_Count":
            top_10_overlap,

        "Top10_Overlap_Percent":
            top_10_overlap / 10 * 100,

        "Top22_Overlap_Count":
            top_22_overlap,

        "Top22_Overlap_Percent":
            top_22_overlap / 22 * 100,

        "Mean_Absolute_Rank_Change":
            mean_absolute_rank_change,

        "Maximum_Absolute_Rank_Change":
            maximum_absolute_rank_change
    })


scenario_summary = pd.DataFrame(
    scenario_summary_records
)


print(
    "\nScenario-comparison statistics "
    "calculated successfully."
)


# =====================================================
# 20. Print the scenario summary
# =====================================================

print("\nSensitivity-analysis scenario summary:")

print(
    scenario_summary.to_string(
        index=False
    )
)


# =====================================================
# 21. Prepare robust top-22 candidate table
# =====================================================

robust_top_22 = stations[

    stations["Top22_Appearance_Count"] > 0

].copy()


robust_top_22 = robust_top_22.sort_values(

    by=[
        "Top22_Appearance_Count",
        "Sensitivity_Mean_Rank"
    ],

    ascending=[
        False,
        True
    ]
)


robust_display_columns = [
    "Station_ID",
    "name",
    "Overall_Suitability_Rank",
    "Overall_Suitability_Index",
    "Top10_Appearance_Count",
    "Top22_Appearance_Count",
    "Sensitivity_Mean_Rank",
    "Sensitivity_Best_Rank",
    "Sensitivity_Worst_Rank",
    "Sensitivity_Rank_Range",
    "Ranking_Robustness"
]


robust_display_columns = [

    column
    for column in robust_display_columns
    if column in robust_top_22.columns
]


print(
    "\nStations appearing in the top 22 "
    "under at least one scenario:"
)

print(
    robust_top_22[
        robust_display_columns
    ].to_string(index=False)
)


# =====================================================
# 22. Print top 10 under each scenario
# =====================================================

for scenario_name in sensitivity_scenarios:

    rank_column = (
        f"Sensitivity_Rank_{scenario_name}"
    )

    score_column = (
        f"Sensitivity_Score_{scenario_name}"
    )

    scenario_top_10 = (

        stations
        .sort_values(rank_column)
        .head(10)
    )

    top_10_display_columns = [
        rank_column,
        "Station_ID",
        "name",
        score_column
    ]

    print(
        f"\nTop 10 stations under "
        f"{scenario_name}:"
    )

    print(
        scenario_top_10[
            top_10_display_columns
        ].to_string(index=False)
    )


# =====================================================
# 23. Save the station-level sensitivity results
# =====================================================

station_results = pd.DataFrame(
    stations.drop(
        columns="geometry"
    )
)


station_results.to_csv(
    station_results_file,
    index=False
)


print(
    "\nStation-level sensitivity results "
    "saved successfully."
)

print(station_results_file)


# =====================================================
# 24. Save the scenario-summary table
# =====================================================

scenario_summary.to_csv(
    scenario_summary_file,
    index=False
)


print(
    "\nScenario summary saved successfully."
)

print(scenario_summary_file)


# =====================================================
# 25. Save the robust top-22 table
# =====================================================

pd.DataFrame(
    robust_top_22.drop(
        columns="geometry"
    )
).to_csv(
    robust_candidates_file,
    index=False
)


print(
    "\nRobust top-22 candidate table "
    "saved successfully."
)

print(robust_candidates_file)


# =====================================================
# 26. Save the spatial sensitivity dataset
# =====================================================

stations.to_file(
    spatial_output_file,
    driver="GeoJSON"
)


print(
    "\nSpatial sensitivity-analysis dataset "
    "saved successfully."
)

print(spatial_output_file)


# =====================================================
# 27. Final completion message
# =====================================================

print(
    "\nMCDA weight sensitivity analysis "
    "completed successfully."
)

print(
    "\nNumber of fuel stations analysed:",
    len(stations)
)

print(
    "\nThe analysis tested ranking stability "
    "under five MCDA weighting scenarios."
)
