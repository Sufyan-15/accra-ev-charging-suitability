"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
12E_Study_Area_Map.py

Research Objective:
Produce a publication-quality study-area map showing the distribution
of the 234 existing fuel stations examined in metropolitan Accra, Ghana.

Author:
Sufyan Yakubu
"""

# =====================================================
# 1. Import required libraries
# =====================================================

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx


# =====================================================
# 2. Define the project folders
# =====================================================

from config import PROJECT_DIR

PROCESSED_DATA = (
    PROJECT_DIR
    / "Data"
    / "Processed"
)

FIGURE_FOLDER = (
    PROJECT_DIR
    / "Maps"
    / "Manuscript_Figures"
)


# =====================================================
# 3. Define the input and output files
# =====================================================

fuel_file = (
    PROCESSED_DATA
    / "Fuel_Stations_Accra_Projected.geojson"
)

png_output = (
    FIGURE_FOLDER
    / "Figure_2_Fuel_Station_Spatial_Distribution.png"
)

pdf_output = (
    FIGURE_FOLDER
    / "Figure_2_Fuel_Station_Spatial_Distribution.pdf"
)


# =====================================================
# 4. Check the input file and output folder
# =====================================================

if not fuel_file.exists():

    raise FileNotFoundError(
        f"Fuel-station dataset not found:\n{fuel_file}"
    )

FIGURE_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

print(
    "Required input file found successfully."
)


# =====================================================
# 5. Load the fuel-station dataset
# =====================================================

fuel_stations = gpd.read_file(
    fuel_file
)

print(
    "\nFuel-station dataset loaded successfully."
)

print(
    "Number of fuel stations:",
    len(fuel_stations)
)

print(
    "Fuel-station CRS:",
    fuel_stations.crs
)


# =====================================================
# 6. Verify the dataset
# =====================================================

if fuel_stations.empty:

    raise ValueError(
        "The fuel-station dataset contains no records."
    )

if fuel_stations.crs is None:

    raise ValueError(
        "The fuel-station dataset has no coordinate "
        "reference system."
    )

if len(fuel_stations) != 234:

    print(
        "\nWARNING:"
        f" The dataset contains {len(fuel_stations)} "
        "stations rather than the expected 234."
    )

else:

    print(
        "\nAll 234 fuel-station records were verified."
    )
    
    # =====================================================
# 7. Transform the data for the OpenStreetMap basemap
# =====================================================

# EPSG:3857 is the Web Mercator coordinate system used
# by most online basemap services.

fuel_stations_web = fuel_stations.to_crs(
    epsg=3857
)

print(
    "\nFuel stations transformed to EPSG:3857."
)

print(
    "Map CRS:",
    fuel_stations_web.crs
)


# =====================================================
# 8. Calculate the spatial extent of the stations
# =====================================================

minimum_x, minimum_y, maximum_x, maximum_y = (
    fuel_stations_web.total_bounds
)

print(
    "\nFuel-station spatial extent calculated."
)

print(
    "Minimum x:",
    minimum_x
)

print(
    "Minimum y:",
    minimum_y
)

print(
    "Maximum x:",
    maximum_x
)

print(
    "Maximum y:",
    maximum_y
)


# =====================================================
# 9. Add map margins around the station distribution
# =====================================================

# The margins prevent stations near the edges from
# appearing too close to the map border.

horizontal_range = maximum_x - minimum_x
vertical_range = maximum_y - minimum_y

horizontal_margin = horizontal_range * 0.08
vertical_margin = vertical_range * 0.08

map_minimum_x = (
    minimum_x - horizontal_margin
)

map_maximum_x = (
    maximum_x + horizontal_margin
)

map_minimum_y = (
    minimum_y - vertical_margin
)

map_maximum_y = (
    maximum_y + vertical_margin
)

print(
    "\nMap margins calculated successfully."
)


# =====================================================
# 10. Create the study-area map canvas
# =====================================================

fig, ax = plt.subplots(
    figsize=(10, 8)
)

ax.set_xlim(
    map_minimum_x,
    map_maximum_x
)

ax.set_ylim(
    map_minimum_y,
    map_maximum_y
)


# =====================================================
# 11. Plot the 234 existing fuel stations
# =====================================================

fuel_stations_web.plot(
    ax=ax,
    color="#D73027",
    edgecolor="white",
    linewidth=0.6,
    markersize=28,
    alpha=0.90,
    label="Existing fuel stations (n = 234)",
    zorder=3
)

print(
    "\nAll fuel stations plotted successfully."
)

# =====================================================
# 12. Add the OpenStreetMap basemap
# =====================================================

try:

    ctx.add_basemap(
        ax,
        source=ctx.providers.OpenStreetMap.Mapnik,
        crs=fuel_stations_web.crs,
        attribution_size=7,
        alpha=0.85
    )

    print(
        "\nOpenStreetMap basemap added successfully."
    )

except Exception as error:

    print(
        "\nWARNING: The basemap could not be added."
    )

    print(
        "The fuel-station points will still be mapped."
    )

    print(
        "Basemap error:",
        error
    )


# =====================================================
# 13. Add the map title
# =====================================================

ax.set_title(
 "Distribution of Existing Fuel Stations in Accra and "
    "Surrounding Urban Districts",
    fontsize=16,
    fontweight="bold",
    pad=16
)


# =====================================================
# 14. Add the fuel-station legend
# =====================================================

legend = ax.legend(
    loc="lower right",
    frameon=True,
    framealpha=0.95,
    facecolor="white",
    edgecolor="#666666",
    fontsize=10
)

legend.set_title(
    "Study dataset",
    prop={
        "size": 10,
        "weight": "bold"
    }
)


# =====================================================
# 15. Add a north arrow
# =====================================================

ax.annotate(
    "N",
    xy=(0.94, 0.91),
    xytext=(0.94, 0.81),
    xycoords="axes fraction",
    ha="center",
    va="center",
    fontsize=15,
    fontweight="bold",
    arrowprops=dict(
        facecolor="black",
        edgecolor="black",
        width=4,
        headwidth=13,
        headlength=14
    ),
    zorder=5
)


# =====================================================
# 16. Add a five-kilometre scale bar
# =====================================================

# EPSG:3857 uses metres. Therefore, a line measuring
# 5,000 map units represents approximately 5 km.

scale_length = 5000

scale_start_x = (
    map_minimum_x
    + (map_maximum_x - map_minimum_x) * 0.06
)

scale_end_x = (
    scale_start_x + scale_length
)

scale_y = (
    map_minimum_y
    + (map_maximum_y - map_minimum_y) * 0.06
)

ax.plot(
    [scale_start_x, scale_end_x],
    [scale_y, scale_y],
    color="black",
    linewidth=4,
    solid_capstyle="butt",
    zorder=5
)

ax.text(
    (scale_start_x + scale_end_x) / 2,
    scale_y
    + (map_maximum_y - map_minimum_y) * 0.018,
    "5 km",
    ha="center",
    va="bottom",
    fontsize=10,
    fontweight="bold",
    color="black",
    zorder=5
)


# =====================================================
# 17. Remove Web Mercator coordinate labels
# =====================================================

# The basemap already provides recognizable roads and
# place names, so the Web Mercator axes are unnecessary.

ax.set_axis_off()

print(
    "\nMap title, legend, north arrow and scale bar "
    "added successfully."
)

# =====================================================
# 18. Adjust the figure layout
# =====================================================

fig.tight_layout(
    pad=1.5
)


# =====================================================
# 19. Save the PNG version
# =====================================================

fig.savefig(
    png_output,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.08,
    facecolor="white"
)

print(
    "\nPNG study-area map saved successfully."
)

print(
    png_output
)


# =====================================================
# 20. Save the PDF version
# =====================================================

fig.savefig(
    pdf_output,
    bbox_inches="tight",
    pad_inches=0.08,
    facecolor="white"
)

print(
    "\nPDF study-area map saved successfully."
)

print(
    pdf_output
)


# =====================================================
# 21. Display the completed map
# =====================================================

plt.show()


# =====================================================
# 22. Report completion
# =====================================================

print(
    "\nScript 12E completed successfully."
)

print(
    "\nThe study-area map contains:"
)

print(
    "1. All 234 existing fuel stations."
)

print(
    "2. OpenStreetMap geographic context."
)

print(
    "3. A north arrow and five-kilometre scale bar."
)

print(
    "4. A publication-quality legend and title."
)

print(
    "\nNo analytical datasets, suitability scores, "
    "station ranks or screening decisions were modified."
)

print(
    "\nSuggested manuscript caption:"
)

print(
    "Figure X. Location of the study area and distribution "
    "of the 234 existing fuel stations in metropolitan "
    "Accra, Ghana."
)
