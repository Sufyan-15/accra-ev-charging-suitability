# Accra EV-Charging Suitability

Python-based GIS and multi-criteria decision analysis (MCDA) workflow for prioritising existing fuel stations for electric vehicle charging infrastructure in metropolitan Accra, Ghana.

## Study overview

The workflow evaluates 234 existing fuel stations using three spatial dimensions:

- residential demand, represented by population within a 1 km baseline catchment;
- destination demand, represented by proximity to universities, markets, shopping malls and transport terminals; and
- grid accessibility, represented by proximity to electrical substations.

The three component indices are combined using an equal-weight MCDA model. Candidate stations are ranked, classified using Jenks Natural Breaks, tested under alternative criterion weights and population-buffer distances, and subjected to non-compensatory physical-site screening.

## Repository structure

```text
accra-ev-charging-suitability/
├── README.md
├── requirements.txt
├── .gitignore
├── scripts/
├── Data/
├── Results/
└── Maps/
```

The repository contains the analytical scripts and documentation. Large source datasets, intermediate outputs and physical-assessment images are not included.

## Software requirements

Python 3.11 or later is recommended. Install the required packages from the project root:

```bash
python -m pip install -r requirements.txt
```

`tkinter`, used by the physical-assessment interface, is distributed with most standard Python installations and is not installed through `pip`.

## Data preparation

Download or extract the source datasets described in [Data/README.md](Data/README.md), and retain the filenames and folder structure shown there. The WorldPop raster and OpenStreetMap-derived GeoJSON files are deliberately excluded from this repository.

All scripts obtain the project root from `scripts/config.py`. No user-specific computer path is required. Advanced users may override the detected root by setting the `EV_CHARGING_PROJECT_DIR` environment variable.

## Recommended execution order

Run the scripts from the project root in the following order:

1. `01_Load_Data.py` — inspect the required source datasets.
2. `02_Data_Preparation.py` — clean and project vector datasets.
3. `03_Distance_Analysis.py` — calculate nearest-feature distances.
4. `04_Population_Analysis.py` — estimate population within the 1 km baseline buffer.
5. `05_Normalization.py` — normalise the population and proximity variables.
6. `06_Destination_Demand_Index.py` — construct the Destination Demand Index.
7. `07_Grid_Suitability_Analysis.py` — construct the Grid Accessibility Index.
8. `08_MCDA_Analysis.py` — calculate the baseline Overall Suitability Index.
9. `09_Suitability_Mapping.py` — classify and map the suitability results.
10. `10_Candidate_Site_Selection.py` — identify the Very High-suitability shortlist.
11. `10B_Physical_Assessment_Tool.py` — record desktop physical-site assessments.
12. `10C_Physical_Assessment_Results.py` — process the physical-screening decisions.
13. `11_Sensitivity_Analysis.py` — test alternative MCDA criterion weights.
14. `11B_Population_Buffer_Sensitivity.py` — test 500 m, 1 km and 2 km population buffers.
15. `12_Manuscript_Figures_and_Tables.py` — generate descriptive tables and principal analytical figures.
16. `12C_Final_Publication_Map.py` — generate the final physical-screening map.
17. `12D_Analytical_Workflow_Figure.py` — generate the analytical-framework figure.
18. `12E_Study_Area_Map.py` — generate the study-area map.

Example:

```bash
python scripts/01_Load_Data.py
```

## Main manuscript figures

| Figure | Output | Generating script |
|---|---|---|
| Figure 1 | Analytical framework | `12D_Analytical_Workflow_Figure.py` |
| Figure 2 | Fuel-station spatial distribution | `12E_Study_Area_Map.py` |
| Figure 3 | Suitability-score and class distributions | `12_Manuscript_Figures_and_Tables.py` |
| Figure 4 | Overall Suitability Index classes | `09_Suitability_Mapping.py` |
| Figure 5 | Population-buffer sensitivity | `12_Manuscript_Figures_and_Tables.py` |
| Figure 6 | Physical-screening outcomes | `12C_Final_Publication_Map.py` |

## Important methodological limitation

The Grid Accessibility Index is a spatial proximity proxy. It does not measure feeder capacity, transformer loading, voltage compatibility, connection cost or the need for network reinforcement. Detailed utility-led electrical studies remain necessary before implementation.

## Data and code availability

The source datasets are available from their official providers, as documented in [Data/README.md](Data/README.md). The scripts in this repository reproduce the processing, spatial analysis, MCDA, sensitivity analysis and figure-generation workflow when the required source data are supplied.

## Author

Sufyan Yakubu

## Citation

The formal citation for the associated manuscript and a permanent repository DOI will be added when they become available.
