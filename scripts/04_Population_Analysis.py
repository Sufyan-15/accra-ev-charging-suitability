"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
04_Population_Analysis.py

Research Objective:
Estimate the residential population within 1 km of each existing
fuel station considered as a candidate EV charging location.

Author:
Sufyan Yakubu
"""

from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.mask import mask

# =====================================================
# 1. Project folders
# =====================================================

from config import PROJECT_DIR

RAW_DATA = PROJECT_DIR / "Data" / "Raw"
FINAL_DATA = PROJECT_DIR / "Data" / "Final"

# =====================================================
# 2. Input files
# =====================================================

fuel_file = FINAL_DATA / "Fuel_Stations_Distance_Analysis.geojson"

population_file = (
    RAW_DATA
    / "Population"
    / "gha_pop_2026_CN_100m_R2025A_v1.tif"
)

# =====================================================
# 3. Load fuel stations
# =====================================================

fuel_stations = gpd.read_file(fuel_file)

# =====================================================
# 4. Inspect the population raster
# =====================================================

with rasterio.open(population_file) as population_raster:

    raster_crs = population_raster.crs

    print("Population raster loaded successfully.")
    print("Raster CRS:", population_raster.crs)
    print("Raster width:", population_raster.width)
    print("Raster height:", population_raster.height)
    print("Raster bands:", population_raster.count)
    print("Raster NoData value:", population_raster.nodata)

# =====================================================
# 5. Inspect the fuel-station dataset
# =====================================================

print("\nFuel-station dataset loaded successfully.")
print("Number of fuel stations:", len(fuel_stations))
print("Fuel-station CRS:", fuel_stations.crs)

print("\nFirst five station names:")
print(fuel_stations["name"].head())

# =====================================================
# 6. Create 1 km buffers around fuel stations
# =====================================================

BUFFER_DISTANCE_M = 1000

fuel_station_buffers = fuel_stations.copy()

fuel_station_buffers["geometry"] = fuel_station_buffers.geometry.buffer(
    BUFFER_DISTANCE_M
)

print("\nOne-kilometre buffers created successfully.")
print("Number of buffers:", len(fuel_station_buffers))
print("Buffer CRS:", fuel_station_buffers.crs)

# =====================================================
# 7. Transform buffers to the population raster CRS
# =====================================================

buffers_raster_crs = fuel_station_buffers.to_crs(raster_crs)

print("\nBuffers transformed to the population raster CRS.")
print("Transformed buffer CRS:", buffers_raster_crs.crs)
# =====================================================
# 8. Calculate population within each 1 km buffer
# =====================================================

residential_population = []

with rasterio.open(population_file) as population_raster:

    for buffer_geometry in buffers_raster_crs.geometry:

        clipped_population, clipped_transform = mask(
            population_raster,
            [buffer_geometry],
            crop=True,
            filled=False,
            indexes=1
        )

        valid_population = clipped_population.compressed()

        valid_population = valid_population[
            valid_population >= 0
        ]

        total_population = valid_population.sum()

        residential_population.append(
            round(float(total_population))
        )

print("\nPopulation calculation completed successfully.")
print("Number of population results:", len(residential_population))

# =====================================================
# 9. Add population results to fuel stations
# =====================================================

fuel_stations["Residential_Population_1km"] = (
    residential_population
)

print("\nFirst five population results:")
print(fuel_stations[[
    "name",
    "Residential_Population_1km"
]].head())
# =====================================================
# 10. Check the population results
# =====================================================

print("\nPopulation result summary:")
print(
    fuel_stations[
        "Residential_Population_1km"
    ].describe()
)

print("\nMissing population values:")
print(
    fuel_stations[
        "Residential_Population_1km"
    ].isnull().sum()
)

print("\nZero population values:")
print(
    (
        fuel_stations[
            "Residential_Population_1km"
        ] == 0
    ).sum()
)

# =====================================================
# 11. Save the population analysis dataset
# =====================================================

output_file = (
    FINAL_DATA
    / "Fuel_Stations_Population_Analysis.geojson"
)

fuel_stations.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nPopulation analysis dataset saved successfully.")
print(output_file)
