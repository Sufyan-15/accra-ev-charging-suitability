"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
09_Suitability_Mapping.py

Research Objective:
Classify candidate fuel stations into five suitability categories
using Jenks Natural Breaks and generate a static spatial
suitability map for EV charging infrastructure planning.

Author:
Sufyan Yakubu
"""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import mapclassify

from matplotlib.lines import Line2D

# =====================================================
# 1. Project folders
# =====================================================

from config import PROJECT_DIR

FINAL_DATA = PROJECT_DIR / "Data" / "Final"
MAPS_DIR = PROJECT_DIR / "Maps"

MAPS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# 2. Input and output files
# =====================================================

input_file = (
    FINAL_DATA
    / "Fuel_Stations_MCDA_Baseline.geojson"
)

classified_output_file = (
    FINAL_DATA
    / "Fuel_Stations_Suitability_Classes.geojson"
)

map_png_output_file = (
    MAPS_DIR
    / "Figure_4_Overall_Suitability_Classes_Map.png"
)

map_pdf_output_file = (
    MAPS_DIR
    / "Figure_4_Overall_Suitability_Classes_Map.pdf"
)

# =====================================================
# 3. Load the baseline MCDA dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Baseline MCDA dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Check the suitability variable
# =====================================================

suitability_column = "Overall_Suitability_Index"

print("\nMissing Overall Suitability Index values:")

print(
    fuel_stations[
        suitability_column
    ].isnull().sum()
)

print("\nOverall Suitability Index range:")

print(
    "Minimum:",
    fuel_stations[
        suitability_column
    ].min()
)

print(
    "Maximum:",
    fuel_stations[
        suitability_column
    ].max()
)

# =====================================================
# 5. Apply five-class Jenks Natural Breaks
# =====================================================

number_of_classes = 5

jenks_classifier = mapclassify.NaturalBreaks(
    fuel_stations[
        suitability_column
    ],
    k=number_of_classes
)

fuel_stations["Suitability_Class_Code"] = (
    jenks_classifier.yb + 1
)

print("\nJenks Natural Breaks classification completed.")

print("\nJenks upper class boundaries:")

for class_number, boundary in enumerate(
    jenks_classifier.bins,
    start=1
):

    print(
        "Class",
        class_number,
        "upper boundary:",
        round(boundary, 6)
    )

# =====================================================
# 6. Assign suitability-class labels
# =====================================================

class_labels = {
    1: "Very Low",
    2: "Low",
    3: "Moderate",
    4: "High",
    5: "Very High"
}

fuel_stations["Suitability_Class"] = (
    fuel_stations[
        "Suitability_Class_Code"
    ].map(class_labels)
)

print("\nSuitability labels assigned successfully.")

# =====================================================
# 7. Count stations in each class
# =====================================================

class_order = [
    "Very Low",
    "Low",
    "Moderate",
    "High",
    "Very High"
]

class_counts = (
    fuel_stations[
        "Suitability_Class"
    ]
    .value_counts()
    .reindex(class_order)
)

print("\nNumber of fuel stations in each class:")

print(class_counts)

print(
    "\nTotal classified stations:",
    class_counts.sum()
)

# =====================================================
# 8. Define map colours
# =====================================================

class_colours = {
    "Very Low": "#d73027",
    "Low": "#fc8d59",
    "Moderate": "#fee08b",
    "High": "#91cf60",
    "Very High": "#1a9850"
}

fuel_stations["Map_Colour"] = (
    fuel_stations[
        "Suitability_Class"
    ].map(class_colours)
)

# =====================================================
# 9. Create the suitability map
# =====================================================

figure, axis = plt.subplots(
    figsize=(11, 10)
)

fuel_stations.plot(
    ax=axis,
    color=fuel_stations["Map_Colour"],
    edgecolor="black",
    linewidth=0.4,
    markersize=45,
    alpha=0.90
)

axis.set_title(
    "Spatial Suitability of Existing Fuel Stations for\n"
    "EV Charging Infrastructure in Accra, Ghana",
    fontsize=15,
    fontweight="bold",
    pad=15
)

axis.set_xlabel(
    "Easting (metres)",
    fontsize=11
)

axis.set_ylabel(
    "Northing (metres)",
    fontsize=11
)

axis.grid(
    visible=True,
    linestyle="--",
    linewidth=0.4,
    alpha=0.5
)

# =====================================================
# 10. Create the map legend
# =====================================================

legend_items = []

for class_name in class_order:

    legend_item = Line2D(
        [0],
        [0],
        marker="o",
        color="white",
        markerfacecolor=class_colours[class_name],
        markeredgecolor="black",
        markersize=9,
        label=class_name
    )

    legend_items.append(legend_item)

axis.legend(
    handles=legend_items,
    title="Suitability Class",
    loc="lower right",
    frameon=True
)

# =====================================================
# 11. Add a north arrow
# =====================================================

axis.annotate(
    "N",
    xy=(0.95, 0.95),
    xytext=(0.95, 0.84),
    xycoords="axes fraction",
    ha="center",
    va="center",
    fontsize=14,
    fontweight="bold",
    arrowprops=dict(
        facecolor="black",
        width=4,
        headwidth=12
    )
)

# =====================================================
# 12. Save and display the map
# =====================================================

plt.tight_layout()

figure.savefig(
    map_png_output_file,
    dpi=600,
    bbox_inches="tight"
)

figure.savefig(
    map_pdf_output_file,
    bbox_inches="tight"
)

plt.show()

print("\nSuitability map saved successfully.")
print(map_png_output_file)
print(map_pdf_output_file)

# =====================================================
# 13. Save the classified spatial dataset
# =====================================================

fuel_stations.to_file(
    classified_output_file,
    driver="GeoJSON"
)

print("\nClassified suitability dataset saved successfully.")
print(classified_output_file)

print(
    "\nNumber of classified stations saved:",
    len(fuel_stations)
)

