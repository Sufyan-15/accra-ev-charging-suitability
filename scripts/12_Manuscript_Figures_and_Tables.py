"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
12_Manuscript_Figures_and_Tables.py

Research Objective:
Create publication-quality figures and tables summarizing the
EV-charging suitability, sensitivity and physical-screening results.

Important:
This script does not recalculate or change the research results.
It only presents results created by the preceding analysis scripts.

Author:
Sufyan Yakubu
"""

# =====================================================
# 1. Import Python libraries
# =====================================================

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter


# =====================================================
# 2. Define the project folders
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

MAPS_DIR = (
    PROJECT_DIR
    / "Maps"
)

MANUSCRIPT_TABLES = (
    RESULTS_DIR
    / "Manuscript_Tables"
)

MANUSCRIPT_FIGURES = (
    MAPS_DIR
    / "Manuscript_Figures"
)

MANUSCRIPT_TABLES.mkdir(
    parents=True,
    exist_ok=True
)

MANUSCRIPT_FIGURES.mkdir(
    parents=True,
    exist_ok=True
)

print("Manuscript output folders prepared successfully.")


# =====================================================
# 3. Define the required input files
# =====================================================

suitability_file = (
    FINAL_DATA
    / "Fuel_Stations_Suitability_Classes.geojson"
)

screened_candidates_file = (
    FINAL_DATA
    / "Physically_Screened_EVCS_Candidates.geojson"
)

buffer_sensitivity_file = (
    RESULTS_DIR
    / "Population_Buffer_Sensitivity_Summary.csv"
)


# =====================================================
# 4. Check that the input files exist
# =====================================================

required_files = [
    suitability_file,
    screened_candidates_file,
    buffer_sensitivity_file
]

for required_file in required_files:

    if not required_file.exists():

        raise FileNotFoundError(
            "\nRequired input file was not found:\n"
            f"{required_file}"
        )

print("\nAll required input files were found successfully.")


# =====================================================
# 5. Load the research datasets
# =====================================================

all_stations = gpd.read_file(
    suitability_file
)

screened_candidates = gpd.read_file(
    screened_candidates_file
)

buffer_sensitivity = pd.read_csv(
    buffer_sensitivity_file
)

print("\nResearch datasets loaded successfully.")

print(
    "Number of fuel stations:",
    len(all_stations)
)

print(
    "Number of physically assessed candidates:",
    len(screened_candidates)
)

print(
    "Number of population-buffer scenarios:",
    len(buffer_sensitivity)
)

print(
    "Fuel-station dataset CRS:",
    all_stations.crs
)

print(
    "Screened-candidate dataset CRS:",
    screened_candidates.crs
)


# =====================================================
# 6. Check the spatial datasets
# =====================================================

if all_stations.crs is None:

    raise ValueError(
        "\nThe complete fuel-station dataset has no CRS."
    )

if screened_candidates.crs is None:

    raise ValueError(
        "\nThe screened-candidate dataset has no CRS."
    )

if all_stations.empty:

    raise ValueError(
        "\nThe complete fuel-station dataset is empty."
    )

if screened_candidates.empty:

    raise ValueError(
        "\nThe screened-candidate dataset is empty."
    )


# =====================================================
# 7. Check the required suitability columns
# =====================================================

required_suitability_columns = [
    "Station_ID",
    "name",
    "Residential_Demand_Index",
    "Destination_Demand_Index",
    "Grid_Accessibility_Index",
    "Overall_Suitability_Index",
    "Overall_Suitability_Rank",
    "Suitability_Class",
    "geometry"
]

missing_suitability_columns = [
    column
    for column in required_suitability_columns
    if column not in all_stations.columns
]

if missing_suitability_columns:

    raise KeyError(
        "\nRequired suitability columns are missing:\n"
        + "\n".join(
            missing_suitability_columns
        )
    )

print("\nAll required suitability columns were found.")


# =====================================================
# 8. Check the physical-screening columns
# =====================================================

required_screening_columns = [
    "Station_ID",
    "Original_Station_Name",
    "Verified_Station_Name",
    "Overall_Suitability_Index",
    "Overall_Suitability_Rank",
    "Physical_Category",
    "Candidate_Eligibility",
    "Physical_Screening_Decision",
    "geometry"
]

missing_screening_columns = [
    column
    for column in required_screening_columns
    if column not in screened_candidates.columns
]

if missing_screening_columns:

    raise KeyError(
        "\nRequired physical-screening columns are missing:\n"
        + "\n".join(
            missing_screening_columns
        )
    )

print(
    "\nAll required physical-screening columns were found."
)


# =====================================================
# 9. Check the population-sensitivity columns
# =====================================================

required_sensitivity_columns = [
    "Population_Buffer",
    "Spearman_Rank_Correlation",
    "Top_10_Overlap",
    "Top_22_Overlap",
    "Mean_Absolute_Rank_Change",
    "Maximum_Absolute_Rank_Change"
]

missing_sensitivity_columns = [
    column
    for column in required_sensitivity_columns
    if column not in buffer_sensitivity.columns
]

if missing_sensitivity_columns:

    raise KeyError(
        "\nRequired population-sensitivity columns are missing:\n"
        + "\n".join(
            missing_sensitivity_columns
        )
    )

print(
    "\nAll required population-sensitivity columns were found."
)


# =====================================================
# 10. Final input-data check
# =====================================================

print("\nInput-data verification completed successfully.")

print(
    "\nSuitability-class counts:"
)

print(
    all_stations[
        "Suitability_Class"
    ].value_counts()
)

print(
    "\nPhysical-screening decision counts:"
)

print(
    screened_candidates[
        "Physical_Screening_Decision"
    ].value_counts()
)


# =====================================================
# 11. Create Table 1:
#     Descriptive statistics for suitability indices
# =====================================================

index_information = {
    "Residential_Demand_Index":
        "Residential Demand Index",
    "Destination_Demand_Index":
        "Destination Demand Index",
    "Grid_Accessibility_Index":
        "Grid Accessibility Index",
    "Overall_Suitability_Index":
        "Overall Suitability Index"
}

descriptive_rows = []

for column_name, display_name in (
    index_information.items()
):

    descriptive_rows.append(
        {
            "Indicator": display_name,
            "Number_of_Stations":
                all_stations[column_name].count(),
            "Minimum":
                all_stations[column_name].min(),
            "Mean":
                all_stations[column_name].mean(),
            "Standard_Deviation":
                all_stations[column_name].std(),
            "Median":
                all_stations[column_name].median(),
            "Maximum":
                all_stations[column_name].max()
        }
    )

descriptive_statistics = pd.DataFrame(
    descriptive_rows
)

numeric_columns_table_1 = [
    "Minimum",
    "Mean",
    "Standard_Deviation",
    "Median",
    "Maximum"
]

descriptive_statistics[
    numeric_columns_table_1
] = descriptive_statistics[
    numeric_columns_table_1
].round(4)

table_1_file = (
    MANUSCRIPT_TABLES
    / "Table_1_Suitability_Descriptive_Statistics.csv"
)

descriptive_statistics.to_csv(
    table_1_file,
    index=False
)

print(
    "\nTable 1 created successfully:"
)

print(
    descriptive_statistics.to_string(
        index=False
    )
)

print(table_1_file)


# =====================================================
# 12. Create Table 2:
#     Distribution of suitability classes
# =====================================================

class_order = [
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High"
]

class_distribution = (
    all_stations[
        "Suitability_Class"
    ]
    .value_counts()
    .reindex(
        class_order,
        fill_value=0
    )
    .rename_axis(
        "Suitability_Class"
    )
    .reset_index(
        name="Number_of_Stations"
    )
)

class_distribution[
    "Percentage_of_Stations"
] = (
    class_distribution[
        "Number_of_Stations"
    ]
    / len(all_stations)
    * 100
).round(2)

table_2_file = (
    MANUSCRIPT_TABLES
    / "Table_2_Suitability_Class_Distribution.csv"
)

class_distribution.to_csv(
    table_2_file,
    index=False
)

print(
    "\nTable 2 created successfully:"
)

print(
    class_distribution.to_string(
        index=False
    )
)

print(table_2_file)


# =====================================================
# 13. Prepare the physical-screening table columns
# =====================================================

candidate_table_columns = [
    "Overall_Suitability_Rank",
    "Station_ID",
    "Original_Station_Name",
    "Verified_Station_Name",
    "Overall_Suitability_Index",
    "Physical_Category",
    "Candidate_Eligibility",
    "Physical_Screening_Decision"
]

optional_candidate_columns = [
    "Bay_Space_Assessment",
    "Circulation_Assessment",
    "Operational_Interference",
    "Expansion_Assessment",
    "Imagery_Date",
    "Evidence_File",
    "Assessment_Notes"
]

for optional_column in optional_candidate_columns:

    if optional_column in screened_candidates.columns:

        candidate_table_columns.append(
            optional_column
        )


# =====================================================
# 14. Create Table 3:
#     Physically screened candidate stations
# =====================================================

physical_screening_table = (
    screened_candidates[
        candidate_table_columns
    ]
    .copy()
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

physical_screening_table[
    "Overall_Suitability_Index"
] = physical_screening_table[
    "Overall_Suitability_Index"
].round(4)

table_3_file = (
    MANUSCRIPT_TABLES
    / "Table_3_Physically_Screened_Candidates.csv"
)

physical_screening_table.to_csv(
    table_3_file,
    index=False
)

print(
    "\nTable 3 created successfully."
)

print(
    "\nFirst ten rows of the physical-screening table:"
)

print(
    physical_screening_table.head(
        10
    ).to_string(
        index=False
    )
)

print(table_3_file)


# =====================================================
# 15. Confirm the manuscript tables
# =====================================================

print(
    "\nAll three manuscript tables were "
    "created successfully."
)

print(
    "\nManuscript tables folder:"
)

print(
    MANUSCRIPT_TABLES
)


# =====================================================
# 16. Define consistent suitability colours
# =====================================================

suitability_colours = {
    "Very Low": "#d73027",
    "Low": "#fc8d59",
    "Moderate": "#fee08b",
    "High": "#91cf60",
    "Very High": "#1a9850"
}


# =====================================================
# 17. Create Figure 1:
#     Suitability-score and class distributions
# =====================================================

figure_1, axes_1 = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(13, 5.5),
    constrained_layout=True
)

# -----------------------------------------------------
# Figure 1A: Overall Suitability Index distribution
# -----------------------------------------------------

suitability_scores = all_stations[
    "Overall_Suitability_Index"
]

histogram_weights = (
    np.ones_like(
        suitability_scores,
        dtype=float
    )
    / len(suitability_scores)
    * 100
)

axes_1[0].hist(
    suitability_scores,
    bins=12,
    weights=histogram_weights,
    color="#3182bd",
    edgecolor="black",
    linewidth=0.7
)

axes_1[0].axvline(
    suitability_scores.mean(),
    color="#b2182b",
    linestyle="--",
    linewidth=1.8,
    label=(
        f"Mean = "
        f"{suitability_scores.mean():.3f}"
    )
)

axes_1[0].set_xlabel(
    "Overall Suitability Index",
    fontsize=11
)

axes_1[0].set_ylabel(
    "Percentage of fuel stations",
    fontsize=11
)

axes_1[0].set_title(
    "(a) Distribution of suitability scores",
    fontsize=12,
    fontweight="bold"
)

axes_1[0].yaxis.set_major_formatter(
    PercentFormatter(
        xmax=100
    )
)

axes_1[0].legend(
    frameon=False
)

axes_1[0].grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)


# -----------------------------------------------------
# Figure 1B: Suitability-class distribution
# -----------------------------------------------------

class_colours = [
    suitability_colours[
        suitability_class
    ]
    for suitability_class in class_order
]

class_bars = axes_1[1].bar(
    class_distribution[
        "Suitability_Class"
    ],
    class_distribution[
        "Number_of_Stations"
    ],
    color=class_colours,
    edgecolor="black",
    linewidth=0.7
)

axes_1[1].set_xlabel(
    "Suitability class",
    fontsize=11
)

axes_1[1].set_ylabel(
    "Number of fuel stations",
    fontsize=11
)

axes_1[1].set_title(
    "(b) Distribution of suitability classes",
    fontsize=12,
    fontweight="bold"
)

axes_1[1].tick_params(
    axis="x",
    rotation=25
)

axes_1[1].grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

for bar, station_count in zip(
    class_bars,
    class_distribution[
        "Number_of_Stations"
    ]
):

    axes_1[1].text(
        bar.get_x()
        + bar.get_width() / 2,
        bar.get_height() + 1,
        str(station_count),
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )

figure_1.suptitle(
    "Distribution of EV-Charging Suitability "
    "Across Existing Fuel Stations",
    fontsize=14,
    fontweight="bold"
)

figure_1_png = (
    MANUSCRIPT_FIGURES
    / "Figure_3_Suitability_Distribution.png"
)

figure_1_pdf = (
    MANUSCRIPT_FIGURES
    / "Figure_3_Suitability_Distribution.pdf"
)

figure_1.savefig(
    figure_1_png,
    dpi=600,
    bbox_inches="tight"
)

figure_1.savefig(
    figure_1_pdf,
    bbox_inches="tight"
)

plt.close(
    figure_1
)

print(
    "\nFigure 1 created successfully."
)

print(figure_1_png)
print(figure_1_pdf)


# =====================================================
# 18. Arrange the buffer-sensitivity scenarios
# =====================================================

buffer_order = [
    "500m",
    "1km",
    "2km"
]

buffer_sensitivity[
    "Population_Buffer"
] = pd.Categorical(
    buffer_sensitivity[
        "Population_Buffer"
    ],
    categories=buffer_order,
    ordered=True
)

buffer_sensitivity = (
    buffer_sensitivity
    .sort_values(
        "Population_Buffer"
    )
    .reset_index(
        drop=True
    )
)

buffer_sensitivity[
    "Top_10_Overlap_Percentage"
] = (
    buffer_sensitivity[
        "Top_10_Overlap"
    ]
    / 10
    * 100
)

buffer_sensitivity[
    "Top_22_Overlap_Percentage"
] = (
    buffer_sensitivity[
        "Top_22_Overlap"
    ]
    / 22
    * 100
)


# =====================================================
# 19. Create Figure 2:
#     Population-buffer sensitivity
# =====================================================

figure_2, axes_2 = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(13, 5.5),
    constrained_layout=True
)

x_positions = np.arange(
    len(buffer_sensitivity)
)

buffer_labels = (
    buffer_sensitivity[
        "Population_Buffer"
    ]
    .astype(str)
)


# -----------------------------------------------------
# Figure 2A: Spearman rank correlation
# -----------------------------------------------------

correlation_bars = axes_2[0].bar(
    x_positions,
    buffer_sensitivity[
        "Spearman_Rank_Correlation"
    ],
    color=[
        "#9ecae1",
        "#3182bd",
        "#6baed6"
    ],
    edgecolor="black",
    linewidth=0.7
)

axes_2[0].set_xticks(
    x_positions
)

axes_2[0].set_xticklabels(
    buffer_labels
)

axes_2[0].set_ylim(
    0.90,
    1.01
)

axes_2[0].set_xlabel(
    "Population-buffer distance",
    fontsize=11
)

axes_2[0].set_ylabel(
    "Spearman rank correlation",
    fontsize=11
)

axes_2[0].set_title(
    "(a) Correlation with the 1 km baseline",
    fontsize=12,
    fontweight="bold"
)

axes_2[0].grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

for bar, correlation_value in zip(
    correlation_bars,
    buffer_sensitivity[
        "Spearman_Rank_Correlation"
    ]
):

    axes_2[0].text(
        bar.get_x()
        + bar.get_width() / 2,
        correlation_value + 0.002,
        f"{correlation_value:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold"
    )


# -----------------------------------------------------
# Figure 2B: Top-ranked station overlap
# -----------------------------------------------------

bar_width = 0.35

top_10_bars = axes_2[1].bar(
    x_positions - bar_width / 2,
    buffer_sensitivity[
        "Top_10_Overlap_Percentage"
    ],
    width=bar_width,
    color="#756bb1",
    edgecolor="black",
    linewidth=0.7,
    label="Top 10 overlap"
)

top_22_bars = axes_2[1].bar(
    x_positions + bar_width / 2,
    buffer_sensitivity[
        "Top_22_Overlap_Percentage"
    ],
    width=bar_width,
    color="#31a354",
    edgecolor="black",
    linewidth=0.7,
    label="Top 22 overlap"
)

axes_2[1].set_xticks(
    x_positions
)

axes_2[1].set_xticklabels(
    buffer_labels
)

axes_2[1].set_ylim(
    0,
    110
)

axes_2[1].set_xlabel(
    "Population-buffer distance",
    fontsize=11
)

axes_2[1].set_ylabel(
    "Stations retained from baseline (%)",
    fontsize=11
)

axes_2[1].set_title(
    "(b) Overlap with baseline priority groups",
    fontsize=12,
    fontweight="bold"
)

axes_2[1].yaxis.set_major_formatter(
    PercentFormatter(
        xmax=100
    )
)

axes_2[1].legend(
    frameon=False,
    loc="lower center"
)

axes_2[1].grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

for bars in [
    top_10_bars,
    top_22_bars
]:

    for bar in bars:

        axes_2[1].text(
            bar.get_x()
            + bar.get_width() / 2,
            bar.get_height() + 2,
            f"{bar.get_height():.0f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

figure_2.suptitle(
    "Sensitivity of Fuel-Station Rankings to "
    "Population-Buffer Distance",
    fontsize=14,
    fontweight="bold"
)

figure_2_png = (
    MANUSCRIPT_FIGURES
    / "Figure_5_Population_Buffer_Sensitivity.png"
)

figure_2_pdf = (
    MANUSCRIPT_FIGURES
    / "Figure_5_Population_Buffer_Sensitivity.pdf"
)

figure_2.savefig(
    figure_2_png,
    dpi=600,
    bbox_inches="tight"
)

figure_2.savefig(
    figure_2_pdf,
    bbox_inches="tight"
)

plt.close(
    figure_2
)

print(
    "\nFigure 2 created successfully."
)

print(figure_2_png)
print(figure_2_pdf)


# =====================================================
# 20. Prepare the physically screened candidates map
# =====================================================

# Convert both spatial datasets to the same projected CRS.
map_crs = all_stations.crs

screened_candidates_map = (
    screened_candidates.to_crs(
        map_crs
    )
)

all_stations_map = (
    all_stations.to_crs(
        map_crs
    )
)


# =====================================================
# 21. Define physical-screening colours and symbols
# =====================================================

screening_styles = {
    "Retain": {
        "colour": "#1a9850",
        "marker": "o",
        "label": "Retain"
    },
    "Retain conditionally": {
        "colour": "#fdae61",
        "marker": "^",
        "label": "Retain conditionally"
    },
    "Field verification required": {
        "colour": "#8073ac",
        "marker": "D",
        "label": "Field verification required"
    },
    "Exclude from immediate shortlist": {
        "colour": "#d73027",
        "marker": "X",
        "label": "Exclude from immediate shortlist"
    },
    "Ineligible - exclude": {
        "colour": "#252525",
        "marker": "P",
        "label": "Ineligible candidate"
    }
}


# =====================================================
# 22. Create Figure 3:
#     Physically screened candidate map
# =====================================================

figure_3 = plt.figure(
    figsize=(16, 10)
)

figure_3_grid = figure_3.add_gridspec(
    nrows=1,
    ncols=2,
    width_ratios=[
        3.2,
        1.3
    ],
    wspace=0.04
)

map_axis = figure_3.add_subplot(
    figure_3_grid[0]
)

station_key_axis = figure_3.add_subplot(
    figure_3_grid[1]
)


# -----------------------------------------------------
# Plot all 234 fuel stations as geographic context
# -----------------------------------------------------

all_stations_map.plot(
    ax=map_axis,
    color="#d9d9d9",
    edgecolor="#737373",
    linewidth=0.3,
    markersize=18,
    alpha=0.65,
    zorder=1
)


# -----------------------------------------------------
# Plot candidates according to screening decision
# -----------------------------------------------------

legend_handles = [
    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="None",
        markerfacecolor="#d9d9d9",
        markeredgecolor="#737373",
        markersize=7,
        label="Other assessed fuel stations"
    )
]

for decision, style_information in (
    screening_styles.items()
):

    decision_candidates = (
        screened_candidates_map.loc[
            screened_candidates_map[
                "Physical_Screening_Decision"
            ] == decision
        ]
    )

    if decision_candidates.empty:

        continue

    decision_candidates.plot(
        ax=map_axis,
        color=style_information[
            "colour"
        ],
        edgecolor="black",
        linewidth=0.8,
        marker=style_information[
            "marker"
        ],
        markersize=90,
        zorder=3
    )

    legend_handles.append(
        Line2D(
            [0],
            [0],
            marker=style_information[
                "marker"
            ],
            linestyle="None",
            markerfacecolor=style_information[
                "colour"
            ],
            markeredgecolor="black",
            markersize=9,
            label=style_information[
                "label"
            ]
        )
    )


# =====================================================
# 23. Add station-ID labels
# =====================================================

labelled_decisions = [
    "Retain",
    "Retain conditionally",
    "Field verification required"
]

labelled_candidates = (
    screened_candidates_map.loc[
        screened_candidates_map[
            "Physical_Screening_Decision"
        ].isin(
            labelled_decisions
        )
    ]
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

label_offsets = [
    (6, 7),
    (6, -12),
    (-35, 7),
    (-35, -12),
    (10, 14),
    (10, -18)
]

for label_number, (
    row_index,
    candidate
) in enumerate(
    labelled_candidates.iterrows()
):

    x_coordinate = (
        candidate.geometry.x
    )

    y_coordinate = (
        candidate.geometry.y
    )

    x_offset, y_offset = label_offsets[
        label_number
        % len(label_offsets)
    ]

    map_axis.annotate(
        candidate["Station_ID"],
        xy=(
            x_coordinate,
            y_coordinate
        ),
        xytext=(
            x_offset,
            y_offset
        ),
        textcoords="offset points",
        fontsize=8.5,
        fontweight="bold",
        color="#252525",
        bbox={
            "boxstyle": "round,pad=0.18",
            "facecolor": "white",
            "edgecolor": "#636363",
            "linewidth": 0.4,
            "alpha": 0.85
        },
        arrowprops={
            "arrowstyle": "-",
            "color": "#636363",
            "linewidth": 0.5
        },
        zorder=4
    )


# =====================================================
# 24. Format the candidate map
# =====================================================

map_axis.set_title(
    "(a) Spatial distribution and "
    "physical-screening decisions",
    fontsize=13,
    fontweight="bold",
    pad=12
)

map_axis.set_xlabel(
    "Easting (metres)",
    fontsize=11
)

map_axis.set_ylabel(
    "Northing (metres)",
    fontsize=11
)

map_axis.grid(
    linestyle="--",
    linewidth=0.5,
    alpha=0.35
)

map_axis.set_aspect(
    "equal"
)

map_axis.legend(
    handles=legend_handles,
    title="Physical-screening decision",
    loc="lower right",
    fontsize=8.5,
    title_fontsize=9,
    frameon=True,
    framealpha=0.95
)


# -----------------------------------------------------
# Add a north arrow
# -----------------------------------------------------

map_axis.annotate(
    "N",
    xy=(
        0.95,
        0.91
    ),
    xytext=(
        0.95,
        0.80
    ),
    xycoords="axes fraction",
    ha="center",
    va="center",
    fontsize=16,
    fontweight="bold",
    arrowprops={
        "facecolor": "black",
        "edgecolor": "black",
        "width": 4,
        "headwidth": 13,
        "headlength": 14
    }
)


# =====================================================
# 25. Create the station-name key
# =====================================================

station_key_axis.axis(
    "off"
)

station_key_axis.set_title(
    "(b) Candidate station key",
    fontsize=13,
    fontweight="bold",
    pad=12
)

station_key_axis.text(
    0.0,
    0.97,
    "Map labels identify retained, conditionally\n"
    "retained and field-verification candidates.",
    transform=station_key_axis.transAxes,
    fontsize=9.5,
    va="top",
    color="#525252"
)

station_key_candidates = (
    screened_candidates
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

vertical_position = 0.89

for row_index, candidate in (
    station_key_candidates.iterrows()
):

    decision = candidate[
        "Physical_Screening_Decision"
    ]

    style_information = (
        screening_styles.get(
            decision,
            {
                "colour": "#737373",
                "marker": "o"
            }
        )
    )

    station_name = candidate[
        "Verified_Station_Name"
    ]

    if pd.isna(station_name):

        station_name = candidate[
            "Original_Station_Name"
        ]

    if pd.isna(station_name):

        station_name = "Unnamed station"

    station_key_axis.scatter(
        0.03,
        vertical_position,
        s=55,
        color=style_information[
            "colour"
        ],
        edgecolor="black",
        linewidth=0.6,
        marker=style_information[
            "marker"
        ],
        transform=station_key_axis.transAxes
    )

    station_key_axis.text(
        0.08,
        vertical_position,
        (
            f"{candidate['Station_ID']} — "
            f"{station_name}"
        ),
        transform=station_key_axis.transAxes,
        fontsize=8.2,
        va="center"
    )

    vertical_position -= 0.037


# =====================================================
# 26. Add the overall figure title and note
# =====================================================

figure_3.suptitle(
    "Physical Screening of Spatially "
    "Very High-Suitability Fuel Stations",
    fontsize=16,
    fontweight="bold",
    y=0.97
)

figure_3.text(
    0.5,
    0.025,
    (
        "Note: GIS suitability ranks were preserved. "
        "Physical assessment was applied as a screening "
        "filter rather than as an additional weighted score."
    ),
    ha="center",
    fontsize=9.5,
    style="italic"
)


# =====================================================
# 27. Save Figure 3
# =====================================================

figure_3_png = (
    MANUSCRIPT_FIGURES
    / "Diagnostic_Physically_Screened_Candidates_Map.png"
)

figure_3_pdf = (
    MANUSCRIPT_FIGURES
    / "Diagnostic_Physically_Screened_Candidates_Map.pdf"
)

figure_3.savefig(
    figure_3_png,
    dpi=600,
    bbox_inches="tight"
)

figure_3.savefig(
    figure_3_pdf,
    bbox_inches="tight"
)

plt.close(
    figure_3
)

print(
    "\nFigure 3 created successfully."
)

print(figure_3_png)
print(figure_3_pdf)


# =====================================================
# 28. Final output summary
# =====================================================

print(
    "\nManuscript figures and tables "
    "created successfully."
)

print(
    "\nNumber of manuscript tables created: 3"
)

print(
    "Number of manuscript figures created: 3"
)

print(
    "\nTables saved in:"
)

print(
    MANUSCRIPT_TABLES
)

print(
    "\nFigures saved in:"
)

print(
    MANUSCRIPT_FIGURES
)

print(
    "\nScript 12 completed successfully."
)




