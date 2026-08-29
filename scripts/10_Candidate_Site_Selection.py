"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
10_Candidate_Site_Selection.py

Research Objective:
Extract the Very High-suitability fuel stations and prepare
a candidate-site shortlist, labelled map and interactive map
for physical feasibility assessment.

Important Interpretation:
Selection at this stage is based on spatial suitability.
It does not yet confirm adequate physical space or electrical
network capacity.

Author:
Sufyan Yakubu
"""

from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt

# =====================================================
# 1. Project folders
# =====================================================

from config import PROJECT_DIR

FINAL_DATA = PROJECT_DIR / "Data" / "Final"
RESULTS_DIR = PROJECT_DIR / "Results"
MAPS_DIR = PROJECT_DIR / "Maps"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MAPS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =====================================================
# 2. Input and output files
# =====================================================

input_file = (
    FINAL_DATA
    / "Fuel_Stations_Suitability_Classes.geojson"
)

shortlist_geojson_file = (
    FINAL_DATA
    / "Very_High_Suitability_Candidates.geojson"
)

shortlist_csv_file = (
    RESULTS_DIR
    / "Very_High_Suitability_Candidates.csv"
)

static_map_file = (
    MAPS_DIR
    / "Very_High_Candidates_Labelled_Map.png"
)

interactive_map_file = (
    MAPS_DIR
    / "Very_High_Candidates_Interactive_Map.html"
)

# =====================================================
# 3. Load the classified suitability dataset
# =====================================================

fuel_stations = gpd.read_file(input_file)

print("Classified suitability dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Dataset CRS:", fuel_stations.crs)

# =====================================================
# 4. Extract Very High-suitability stations
# =====================================================

shortlisted_stations = fuel_stations[
    fuel_stations[
        "Suitability_Class"
    ] == "Very High"
].copy()

shortlisted_stations = shortlisted_stations.sort_values(
    by="Overall_Suitability_Rank",
    ascending=True
)

print("\nVery High-suitability candidates extracted.")
print(
    "Number of shortlisted stations:",
    len(shortlisted_stations)
)

# =====================================================
# 5. Convert coordinates to latitude and longitude
# =====================================================

shortlisted_wgs84 = shortlisted_stations.to_crs(
    epsg=4326
)

shortlisted_stations["Longitude"] = (
    shortlisted_wgs84.geometry.x.values
)

shortlisted_stations["Latitude"] = (
    shortlisted_wgs84.geometry.y.values
)

print("\nCoordinates converted successfully.")
print("Coordinate system for latitude and longitude: EPSG:4326")

# =====================================================
# 6. Create Google Maps location links
# =====================================================

shortlisted_stations["Google_Maps_Link"] = (
    "https://www.google.com/maps?q="
    + shortlisted_stations["Latitude"].astype(str)
    + ","
    + shortlisted_stations["Longitude"].astype(str)
)

print("\nGoogle Maps links created successfully.")

# =====================================================
# 7. Add physical-assessment fields
# =====================================================

shortlisted_stations["Space_Category"] = ""
shortlisted_stations["Physical_Score"] = ""
shortlisted_stations["Imagery_Date"] = ""
shortlisted_stations["Assessment_Notes"] = ""

print("\nPhysical-assessment fields added successfully.")

# =====================================================
# 8. Display the complete shortlist
# =====================================================

shortlist_display_columns = [
    "Overall_Suitability_Rank",
    "Station_ID",
    "name",
    "Residential_Demand_Index",
    "Destination_Demand_Index",
    "Grid_Accessibility_Index",
    "Overall_Suitability_Index",
    "Latitude",
    "Longitude"
]

print("\nVery High-suitability candidate shortlist:")

print(
    shortlisted_stations[
        shortlist_display_columns
    ].to_string(index=False)
)

# =====================================================
# 9. Check the shortlist
# =====================================================

print("\nMissing station IDs:")
print(
    shortlisted_stations[
        "Station_ID"
    ].isnull().sum()
)

print("\nDuplicate station IDs:")
print(
    shortlisted_stations[
        "Station_ID"
    ].duplicated().sum()
)

print("\nMissing coordinates:")
print(
    shortlisted_stations[[
        "Latitude",
        "Longitude"
    ]].isnull().sum()
)

# =====================================================
# 10. Save the shortlisted GeoJSON
# =====================================================

shortlisted_stations.to_file(
    shortlist_geojson_file,
    driver="GeoJSON"
)

print("\nShortlisted GeoJSON saved successfully.")
print(shortlist_geojson_file)

# =====================================================
# 11. Save the physical-assessment CSV table
# =====================================================

csv_columns = [
    "Overall_Suitability_Rank",
    "Station_ID",
    "name",
    "Residential_Population_1km",
    "Residential_Demand_Index",
    "Destination_Demand_Index",
    "Grid_Accessibility_Index",
    "Distance_to_Substation_m",
    "Demand_Potential_Index",
    "Overall_Suitability_Index",
    "Suitability_Class",
    "Latitude",
    "Longitude",
    "Google_Maps_Link",
    "Space_Category",
    "Physical_Score",
    "Imagery_Date",
    "Assessment_Notes"
]

shortlisted_stations[
    csv_columns
].to_csv(
    shortlist_csv_file,
    index=False
)

print("\nPhysical-assessment CSV saved successfully.")
print(shortlist_csv_file)

# =====================================================
# 12. Create a labelled static map
# =====================================================

figure, axis = plt.subplots(
    figsize=(12, 10)
)

shortlisted_stations.plot(
    ax=axis,
    color="#1a9850",
    edgecolor="black",
    linewidth=0.7,
    markersize=70,
    alpha=0.90
)

for _, station in shortlisted_stations.iterrows():

    axis.annotate(
        station["Station_ID"],
        xy=(
            station.geometry.x,
            station.geometry.y
        ),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=8,
        fontweight="bold"
    )

axis.set_title(
    "Very High-Suitability Fuel Stations for\n"
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

plt.tight_layout()

figure.savefig(
    static_map_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nLabelled shortlist map saved successfully.")
print(static_map_file)

# =====================================================
# 13. Prepare data for the interactive map
# =====================================================

interactive_stations = shortlisted_stations.to_crs(
    epsg=4326
)

map_centre = [
    interactive_stations.geometry.y.mean(),
    interactive_stations.geometry.x.mean()
]

interactive_map = folium.Map(
    location=map_centre,
    zoom_start=11,
    tiles="OpenStreetMap"
)

# =====================================================
# 14. Add shortlisted stations to interactive map
# =====================================================

for _, station in interactive_stations.iterrows():

    station_name = station["name"]

    if station_name is None:
        station_name = "Unnamed station"

    popup_information = f"""
    <b>Station ID:</b> {station["Station_ID"]}<br>
    <b>Name:</b> {station_name}<br>
    <b>Overall Rank:</b> {station["Overall_Suitability_Rank"]}<br>
    <b>Overall Score:</b> {station["Overall_Suitability_Index"]:.4f}<br>
    <b>Residential Demand:</b> {station["Residential_Demand_Index"]:.4f}<br>
    <b>Destination Demand:</b> {station["Destination_Demand_Index"]:.4f}<br>
    <b>Grid Accessibility:</b> {station["Grid_Accessibility_Index"]:.4f}<br>
    <b>Latitude:</b> {station.geometry.y:.6f}<br>
    <b>Longitude:</b> {station.geometry.x:.6f}
    """

    folium.CircleMarker(
        location=[
            station.geometry.y,
            station.geometry.x
        ],
        radius=7,
        color="black",
        weight=1,
        fill=True,
        fill_color="#1a9850",
        fill_opacity=0.90,
        tooltip=(
            f'{station["Station_ID"]} | '
            f'Rank {station["Overall_Suitability_Rank"]}'
        ),
        popup=folium.Popup(
            popup_information,
            max_width=320
        )
    ).add_to(interactive_map)

# =====================================================
# 15. Save the interactive map
# =====================================================

interactive_map.save(
    interactive_map_file
)

print("\nInteractive candidate map saved successfully.")
print(interactive_map_file)

print(
    "\nNumber of shortlisted candidates processed:",
    len(shortlisted_stations)
)
