"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
12C_Final_Publication_Map.py

Research Objective:
Create the final publication-quality map of physically screened
EV-charging candidate fuel stations in Accra.

Cartographic improvements:
1. Remove Web Mercator coordinate labels.
2. Show the detailed-map extent on the overview.
3. Move the decision legend outside the maps.
4. Reposition the north arrow.
5. Improve crowded station labels.

Important:
This script does not modify suitability scores, ranks,
station names or physical-screening decisions.

Author:
Sufyan Yakubu
"""

# =====================================================
# 1. Import Python libraries
# =====================================================

from pathlib import Path

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


# =====================================================
# 2. Define project folders
# =====================================================

from config import PROJECT_DIR

FINAL_DATA = (
    PROJECT_DIR
    / "Data"
    / "Final"
)

MANUSCRIPT_FIGURES = (
    PROJECT_DIR
    / "Maps"
    / "Manuscript_Figures"
)

MANUSCRIPT_FIGURES.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================================
# 3. Define the input files
# =====================================================

all_stations_file = (
    FINAL_DATA
    / "Fuel_Stations_Suitability_Classes.geojson"
)

screened_candidates_file = (
    FINAL_DATA
    / "Physically_Screened_EVCS_Candidates.geojson"
)


# =====================================================
# 4. Check the input files
# =====================================================

required_files = [
    all_stations_file,
    screened_candidates_file
]

for required_file in required_files:

    if not required_file.exists():

        raise FileNotFoundError(
            "\nRequired input file was not found:\n"
            f"{required_file}"
        )

print("Required input files found successfully.")


# =====================================================
# 5. Load the spatial datasets
# =====================================================

all_stations = gpd.read_file(
    all_stations_file
)

screened_candidates = gpd.read_file(
    screened_candidates_file
)

print("\nSpatial datasets loaded successfully.")

print(
    "Number of fuel stations:",
    len(all_stations)
)

print(
    "Number of screened candidates:",
    len(screened_candidates)
)


# =====================================================
# 6. Check the required candidate columns
# =====================================================

required_candidate_columns = [
    "Station_ID",
    "Verified_Station_Name",
    "Overall_Suitability_Rank",
    "Physical_Screening_Decision",
    "geometry"
]

missing_candidate_columns = [
    column
    for column in required_candidate_columns
    if column not in screened_candidates.columns
]

if missing_candidate_columns:

    raise KeyError(
        "\nRequired candidate columns are missing:\n"
        + "\n".join(
            missing_candidate_columns
        )
    )

if all_stations.crs is None:

    raise ValueError(
        "\nThe fuel-station dataset has no CRS."
    )

if screened_candidates.crs is None:

    raise ValueError(
        "\nThe candidate dataset has no CRS."
    )

print(
    "\nRequired map variables verified successfully."
)


# =====================================================
# 7. Transform datasets for the online basemap
# =====================================================

web_map_crs = "EPSG:3857"

all_stations_web = all_stations.to_crs(
    web_map_crs
)

screened_candidates_web = (
    screened_candidates.to_crs(
        web_map_crs
    )
)

print(
    "\nDatasets transformed to EPSG:3857."
)


# =====================================================
# 8. Define physical-screening styles
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
# 9. Select the candidates that receive labels
# =====================================================

labelled_decisions = [
    "Retain",
    "Retain conditionally",
    "Field verification required"
]

labelled_candidates = (
    screened_candidates_web.loc[
        screened_candidates_web[
            "Physical_Screening_Decision"
        ].isin(
            labelled_decisions
        )
    ]
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

print(
    "\nNumber of labelled candidates:",
    len(labelled_candidates)
)


# =====================================================
# 10. Calculate the overview and detail extents
# =====================================================

all_minimum_x, all_minimum_y, (
    all_maximum_x
), all_maximum_y = (
    all_stations_web.total_bounds
)

candidate_minimum_x, candidate_minimum_y, (
    candidate_maximum_x
), candidate_maximum_y = (
    screened_candidates_web.total_bounds
)

all_x_padding = (
    all_maximum_x
    - all_minimum_x
) * 0.05

all_y_padding = (
    all_maximum_y
    - all_minimum_y
) * 0.05

candidate_x_padding = (
    candidate_maximum_x
    - candidate_minimum_x
) * 0.18

candidate_y_padding = (
    candidate_maximum_y
    - candidate_minimum_y
) * 0.18

detail_minimum_x = (
    candidate_minimum_x
    - candidate_x_padding
)

detail_maximum_x = (
    candidate_maximum_x
    + candidate_x_padding
)

detail_minimum_y = (
    candidate_minimum_y
    - candidate_y_padding
)

detail_maximum_y = (
    candidate_maximum_y
    + candidate_y_padding
)

# =====================================================
# 11. Create the final map figure and panels
# =====================================================

figure = plt.figure(
    figsize=(18, 10)
)

figure_grid = figure.add_gridspec(
    nrows=1,
    ncols=3,
    width_ratios=[
        1.25,
        1.65,
        0.95
    ],
    wspace=0.05
)

overview_axis = figure.add_subplot(
    figure_grid[0]
)

detail_axis = figure.add_subplot(
    figure_grid[1]
)

key_axis = figure.add_subplot(
    figure_grid[2]
)


# =====================================================
# 12. Set the Accra-wide overview extent
# =====================================================

overview_axis.set_xlim(
    all_minimum_x - all_x_padding,
    all_maximum_x + all_x_padding
)

overview_axis.set_ylim(
    all_minimum_y - all_y_padding,
    all_maximum_y + all_y_padding
)


# =====================================================
# 13. Plot all fuel stations in the overview
# =====================================================

all_stations_web.plot(
    ax=overview_axis,
    color="#bdbdbd",
    edgecolor="#525252",
    linewidth=0.25,
    markersize=17,
    alpha=0.72,
    zorder=2
)


# =====================================================
# 14. Plot screened candidates in the overview
# =====================================================

for decision, style_information in (
    screening_styles.items()
):

    decision_candidates = (
        screened_candidates_web.loc[
            screened_candidates_web[
                "Physical_Screening_Decision"
            ] == decision
        ]
    )

    if decision_candidates.empty:

        continue

    decision_candidates.plot(
        ax=overview_axis,
        color=style_information[
            "colour"
        ],
        edgecolor="black",
        linewidth=0.8,
        marker=style_information[
            "marker"
        ],
        markersize=72,
        zorder=4
    )


# =====================================================
# 15. Add the overview basemap
# =====================================================

try:

    ctx.add_basemap(
        overview_axis,
        source=ctx.providers.CartoDB.Positron,
        crs=web_map_crs,
        attribution_size=5,
        reset_extent=True
    )

    print(
        "\nOverview basemap added successfully."
    )

except Exception as basemap_error:

    print(
        "\nWARNING: Overview basemap unavailable."
    )

    print(
        "Basemap error:",
        basemap_error
    )


# =====================================================
# 16. Show the detailed-map area on the overview
# =====================================================

detail_extent_rectangle = Rectangle(
    (
        detail_minimum_x,
        detail_minimum_y
    ),
    detail_maximum_x
    - detail_minimum_x,
    detail_maximum_y
    - detail_minimum_y,
    fill=False,
    edgecolor="#2166ac",
    linewidth=2.0,
    linestyle="--",
    zorder=6
)

overview_axis.add_patch(
    detail_extent_rectangle
)

overview_axis.text(
    detail_minimum_x,
    detail_maximum_y
    + (
        all_maximum_y
        - all_minimum_y
    ) * 0.015,
    "Area enlarged in panel (b)",
    fontsize=8,
    fontweight="bold",
    color="#2166ac",
    ha="left",
    va="bottom",
    bbox={
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.80
    },
    zorder=7
)


# =====================================================
# 17. Format the overview panel
# =====================================================

overview_axis.set_title(
    "(a) Accra-wide overview",
    fontsize=13,
    fontweight="bold",
    pad=12
)

overview_axis.set_aspect(
    "equal"
)

# The basemap supplies the geographical context.
# Web Mercator coordinate numbers are therefore hidden.
overview_axis.set_axis_off()


# =====================================================
# 18. Add the overview north arrow
# =====================================================

overview_axis.annotate(
    "N",
    xy=(
        0.93,
        0.91
    ),
    xytext=(
        0.93,
        0.80
    ),
    xycoords="axes fraction",
    ha="center",
    va="center",
    fontsize=13,
    fontweight="bold",
    arrowprops={
        "facecolor": "black",
        "edgecolor": "black",
        "width": 3,
        "headwidth": 10,
        "headlength": 11
    },
    zorder=8
)

# =====================================================
# 19. Set the detailed candidate-map extent
# =====================================================

detail_axis.set_xlim(
    detail_minimum_x,
    detail_maximum_x
)

detail_axis.set_ylim(
    detail_minimum_y,
    detail_maximum_y
)


# =====================================================
# 20. Plot contextual fuel stations
# =====================================================

stations_in_detail_area = (
    all_stations_web.cx[
        detail_minimum_x:detail_maximum_x,
        detail_minimum_y:detail_maximum_y
    ]
)

stations_in_detail_area.plot(
    ax=detail_axis,
    color="#bdbdbd",
    edgecolor="#525252",
    linewidth=0.25,
    markersize=16,
    alpha=0.58,
    zorder=2
)


# =====================================================
# 21. Plot the physically screened candidates
# =====================================================

for decision, style_information in (
    screening_styles.items()
):

    decision_candidates = (
        screened_candidates_web.loc[
            screened_candidates_web[
                "Physical_Screening_Decision"
            ] == decision
        ]
    )

    if decision_candidates.empty:

        continue

    decision_candidates.plot(
        ax=detail_axis,
        color=style_information[
            "colour"
        ],
        edgecolor="black",
        linewidth=0.9,
        marker=style_information[
            "marker"
        ],
        markersize=105,
        zorder=4
    )


# =====================================================
# 22. Add the detailed-panel basemap
# =====================================================

try:

    ctx.add_basemap(
        detail_axis,
        source=ctx.providers.CartoDB.Positron,
        crs=web_map_crs,
        attribution_size=5,
        reset_extent=True
    )

    print(
        "\nDetailed basemap added successfully."
    )

except Exception as basemap_error:

    print(
        "\nWARNING: Detailed basemap unavailable."
    )

    print(
        "Basemap error:",
        basemap_error
    )


# =====================================================
# 23. Define refined station-label positions
# =====================================================

label_offsets = {
    "FS167": (14, 12),
    "FS217": (14, -20),
    "FS018": (-50, -18),
    "FS134": (-62, 5),
    "FS180": (-58, 25),
    "FS051": (-58, -20),
    "FS213": (15, 25),
    "FS029": (-52, 22),
    "FS061": (14, 12),
    "FS223": (-62, -16),
    "FS214": (-52, -10),
    "FS095": (-52, -20),
    "FS179": (14, 14),
    "FS054": (14, -20),
    "FS028": (15, -12)
}


# =====================================================
# 24. Add labels to retained and conditional candidates
# =====================================================

for row_index, candidate in (
    labelled_candidates.iterrows()
):

    station_id = candidate[
        "Station_ID"
    ]

    x_coordinate = (
        candidate.geometry.x
    )

    y_coordinate = (
        candidate.geometry.y
    )

    x_offset, y_offset = (
        label_offsets.get(
            station_id,
            (10, 10)
        )
    )

    detail_axis.annotate(
        station_id,
        xy=(
            x_coordinate,
            y_coordinate
        ),
        xytext=(
            x_offset,
            y_offset
        ),
        textcoords="offset points",
        fontsize=8,
        fontweight="bold",
        color="#252525",
        bbox={
            "boxstyle": "round,pad=0.20",
            "facecolor": "white",
            "edgecolor": "#525252",
            "linewidth": 0.5,
            "alpha": 0.94
        },
        arrowprops={
            "arrowstyle": "-",
            "color": "#525252",
            "linewidth": 0.65
        },
        zorder=7
    )


# =====================================================
# 25. Format the detailed panel
# =====================================================

detail_axis.set_title(
    "(b) Detailed candidate area",
    fontsize=13,
    fontweight="bold",
    pad=12
)

detail_axis.set_aspect(
    "equal"
)

# Hide Web Mercator coordinates because the road
# basemap provides more meaningful geographic context.
detail_axis.set_axis_off()


# =====================================================
# 26. Add the relocated north arrow
# =====================================================

detail_axis.annotate(
    "N",
    xy=(
        0.08,
        0.91
    ),
    xytext=(
        0.08,
        0.80
    ),
    xycoords="axes fraction",
    ha="center",
    va="center",
    fontsize=13,
    fontweight="bold",
    arrowprops={
        "facecolor": "black",
        "edgecolor": "black",
        "width": 3,
        "headwidth": 10,
        "headlength": 11
    },
    zorder=8
)


# =====================================================
# 27. Add an approximate two-kilometre scale bar
# =====================================================

scale_bar_length = 2000

scale_bar_start_x = (
    detail_minimum_x
    + (
        detail_maximum_x
        - detail_minimum_x
    ) * 0.08
)

scale_bar_y = (
    detail_minimum_y
    + (
        detail_maximum_y
        - detail_minimum_y
    ) * 0.06
)

detail_axis.plot(
    [
        scale_bar_start_x,
        scale_bar_start_x
        + scale_bar_length
    ],
    [
        scale_bar_y,
        scale_bar_y
    ],
    color="black",
    linewidth=4,
    solid_capstyle="butt",
    zorder=8
)

detail_axis.text(
    scale_bar_start_x
    + scale_bar_length / 2,
    scale_bar_y
    + (
        detail_maximum_y
        - detail_minimum_y
    ) * 0.018,
    "2 km",
    ha="center",
    va="bottom",
    fontsize=9,
    fontweight="bold",
    bbox={
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.78
    },
    zorder=8
)

# =====================================================
# 28. Prepare the combined legend and station-key panel
# =====================================================

key_axis.axis(
    "off"
)

key_axis.set_title(
    "(c) Map and candidate key",
    fontsize=13,
    fontweight="bold",
    pad=12
)


# =====================================================
# 29. Create the physical-screening legend
# =====================================================

legend_handles = [
    Line2D(
        [0],
        [0],
        marker="o",
        linestyle="None",
        markerfacecolor="#bdbdbd",
        markeredgecolor="#525252",
        markersize=6,
        label="Other fuel stations"
    )
]

for decision, style_information in (
    screening_styles.items()
):

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
            markersize=8,
            label=style_information[
                "label"
            ]
        )
    )

decision_legend = key_axis.legend(
    handles=legend_handles,
    title="Physical-screening decision",
    loc="upper left",
    bbox_to_anchor=(
        0.0,
        0.98
    ),
    fontsize=7.2,
    title_fontsize=8.2,
    frameon=True,
    framealpha=0.95,
    borderpad=0.7,
    labelspacing=0.55
)

key_axis.add_artist(
    decision_legend
)


# =====================================================
# 30. Add the candidate-station heading
# =====================================================

key_axis.text(
    0.0,
    0.68,
    "Candidate stations",
    transform=key_axis.transAxes,
    fontsize=9.5,
    fontweight="bold",
    va="top"
)

key_axis.text(
    0.0,
    0.645,
    (
        "IDs correspond to labels in panel (b)."
    ),
    transform=key_axis.transAxes,
    fontsize=7.2,
    color="#525252",
    va="top"
)


# =====================================================
# 31. Prepare the candidate station list
# =====================================================

station_key_candidates = (
    screened_candidates
    .sort_values(
        "Overall_Suitability_Rank"
    )
)

vertical_position = 0.605


# =====================================================
# 32. Add all candidates to the station key
# =====================================================

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

        station_name = (
            "Unnamed fuel station"
        )

    key_axis.scatter(
        0.025,
        vertical_position,
        s=42,
        color=style_information[
            "colour"
        ],
        edgecolor="black",
        linewidth=0.5,
        marker=style_information[
            "marker"
        ],
        transform=key_axis.transAxes
    )

    key_axis.text(
        0.07,
        vertical_position,
        (
            f"{candidate['Station_ID']} — "
            f"{station_name}"
        ),
        transform=key_axis.transAxes,
        fontsize=6.5,
        va="center"
    )

    vertical_position -= 0.027


# =====================================================
# 33. Add the final figure title
# =====================================================

figure.suptitle(
    "Physical Screening of Spatially "
    "Very High-Suitability Fuel Stations "
    "in Accra, Ghana",
    fontsize=16,
    fontweight="bold",
    y=0.97
)


# =====================================================
# 34. Add the methodological note
# =====================================================

figure.text(
    0.5,
    0.025,
    (
        "Note: GIS suitability scores and ranks were "
        "preserved. Physical assessment was applied as "
        "a non-compensatory screening filter rather than "
        "as an additional weighted MCDA criterion."
    ),
    ha="center",
    fontsize=9.5,
    style="italic"
)


# =====================================================
# 35. Define the final output files
# =====================================================

final_map_png = (
    MANUSCRIPT_FIGURES
    / "Figure_6_Physical_Screening_Outcomes.png"
)

final_map_pdf = (
    MANUSCRIPT_FIGURES
    / "Figure_6_Physical_Screening_Outcomes.pdf"
)


# =====================================================
# 36. Save the final publication map
# =====================================================

figure.savefig(
    final_map_png,
    dpi=600,
    bbox_inches="tight"
)

figure.savefig(
    final_map_pdf,
    bbox_inches="tight"
)

plt.close(
    figure
)

print(
    "\nFinal physical-screening map "
    "saved successfully."
)

print(final_map_png)
print(final_map_pdf)


# =====================================================
# 37. Final completion message
# =====================================================

print(
    "\nScript 12C completed successfully."
)

print(
    "\nFinal cartographic improvements:"
)

print(
    "1. Web Mercator coordinates removed."
)

print(
    "2. Detailed-map extent added to the overview."
)

print(
    "3. Decision legend moved outside the maps."
)

print(
    "4. North arrow relocated."
)

print(
    "5. Candidate labels repositioned."
)

print(
    "\nNo analytical results were modified."
)
