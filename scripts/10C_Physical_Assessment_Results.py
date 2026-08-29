"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
10C_Physical_Assessment_Results.py

Research Objective:
Analyse the completed physical assessments of the 22 shortlisted
fuel stations and create a physically screened EV charging
candidate dataset.

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

FINAL_DATA = PROJECT_DIR / "Data" / "Final"
RESULTS_DIR = PROJECT_DIR / "Results"


# =====================================================
# 3. Define input files
# =====================================================

assessment_file = (
    RESULTS_DIR
    / "Physical_Assessment_Progress.csv"
)

candidate_geojson_file = (
    FINAL_DATA
    / "Very_High_Suitability_Candidates.geojson"
)


# =====================================================
# 4. Define output files
# =====================================================

summary_output_file = (
    RESULTS_DIR
    / "Physical_Assessment_Summary.csv"
)

screened_geojson_file = (
    FINAL_DATA
    / "Physically_Screened_EVCS_Candidates.geojson"
)


# =====================================================
# 5. Check that the input files exist
# =====================================================

if not assessment_file.exists():

    raise FileNotFoundError(
        f"Physical-assessment file not found:\n"
        f"{assessment_file}"
    )

if not candidate_geojson_file.exists():

    raise FileNotFoundError(
        f"Candidate GeoJSON file not found:\n"
        f"{candidate_geojson_file}"
    )

print("Required input files found successfully.")


# =====================================================
# 6. Load the completed physical assessments
# =====================================================

assessments = pd.read_csv(assessment_file)

print("\nPhysical-assessment dataset loaded successfully.")
print("Number of assessment records:", len(assessments))

print("\nColumns found in the assessment dataset:")

for column in assessments.columns:

    print(column)


# =====================================================
# 7. Find the physical-category column
# =====================================================

possible_category_columns = [
    "Space_Category",
    "Physical_Suitability_Category",
    "Overall_Physical_Category",
    "Physical_Category",
    "Overall physical category"
]

physical_category_column = None

for column in possible_category_columns:

    if column in assessments.columns:

        physical_category_column = column

        break


# Try a keyword search if the exact name was not found

if physical_category_column is None:

    for column in assessments.columns:

        simplified_name = column.lower().replace("_", " ")

        if (
            "physical" in simplified_name
            and "category" in simplified_name
        ):

            physical_category_column = column

            break


if physical_category_column is None:

    raise KeyError(
        "\nThe physical-category column could not be found.\n"
        "Please inspect the column names printed above."
    )


print(
    "\nPhysical-category column identified as:",
    physical_category_column
)

# =====================================================
# 8. Rename the category column consistently
# =====================================================

if physical_category_column != "Physical_Category":

    assessments = assessments.rename(
        columns={
            physical_category_column: "Physical_Category"
        }
    )


# =====================================================
# 9. Check the Station_ID column
# =====================================================

if "Station_ID" not in assessments.columns:

    raise KeyError(
        "The Station_ID column is missing from the "
        "physical-assessment dataset."
    )


# Remove accidental spaces from station IDs

assessments["Station_ID"] = (
    assessments["Station_ID"]
    .astype(str)
    .str.strip()
)


# =====================================================
# 10. Confirm the number of assessed stations
# =====================================================

number_of_records = len(assessments)

number_of_unique_ids = (
    assessments["Station_ID"].nunique()
)

print("\nAssessment-record check:")
print("Number of records:", number_of_records)
print("Number of unique station IDs:", number_of_unique_ids)


if number_of_records != 22:

    print(
        "\nCAUTION:"
        "\nThe assessment file does not contain exactly "
        "22 records."
    )


if number_of_unique_ids != number_of_records:

    raise ValueError(
        "Duplicate Station_ID values were found in the "
        "assessment dataset."
    )


# =====================================================
# 11. Clean the physical-category values
# =====================================================

assessments["Physical_Category"] = (
    assessments["Physical_Category"]
    .astype(str)
    .str.strip()
    .str.title()
)


valid_categories = [
    "High",
    "Medium",
    "Low",
    "Uncertain"
]


invalid_categories = assessments[
    ~assessments["Physical_Category"].isin(
        valid_categories
    )
]


if len(invalid_categories) > 0:

    print("\nInvalid or incomplete physical categories:")

    print(
        invalid_categories[
            ["Station_ID", "Physical_Category"]
        ]
    )

    raise ValueError(
        "\nSome assessments are incomplete."
        "\nEvery station must have High, Medium, Low "
        "or Uncertain as its physical category."
    )


print(
    "\nAll physical-category values are valid."
)


# =====================================================
# 12. Preserve the original station names
# =====================================================

if "name" in assessments.columns:

    assessments["Original_Station_Name"] = (
        assessments["name"]
    )

elif "Original_Station_Name" not in assessments.columns:

    assessments["Original_Station_Name"] = (
        "Unnamed station"
    )


# Replace missing original names with a clear label

assessments["Original_Station_Name"] = (
    assessments["Original_Station_Name"]
    .fillna("Unnamed station")
    .replace(
        {
            "None": "Unnamed station",
            "nan": "Unnamed station",
            "": "Unnamed station"
        }
    )
)


# =====================================================
# 13. Record station names verified from imagery
# =====================================================

verified_name_corrections = {
    "FS051": "Goil Fuel Station, Lartebiokorshie",
    "FS091": "Nick Petroleum, Kotobabi",
    "FS095": "Zen Filling Station, New Town",
    "FS212": "Radiance Petroleum, Dansoman",
    "FS213": "Star Oil Fuel Station, Laterbiokorshie–Flamingo Libero",
    "FS222": "Star Oil Fuel Station, New Russia",
    "FS223": "Amser Fuel Station, Russia"
}


# Begin by copying the original station name

assessments["Verified_Station_Name"] = (
    assessments["Original_Station_Name"]
)


# Apply only the corrections confirmed during assessment

for station_id, verified_name in (
    verified_name_corrections.items()
):

    station_mask = (
        assessments["Station_ID"] == station_id
    )

    assessments.loc[
        station_mask,
        "Verified_Station_Name"
    ] = verified_name


# =====================================================
# 14. Create name-verification status
# =====================================================

assessments["Name_Verification_Status"] = (
    "Original name retained"
)


for station_id in verified_name_corrections:

    station_mask = (
        assessments["Station_ID"] == station_id
    )

    assessments.loc[
        station_mask,
        "Name_Verification_Status"
    ] = "Corrected using visual evidence"


# FS028 could not be verified from imagery

assessments.loc[
    assessments["Station_ID"] == "FS028",
    "Name_Verification_Status"
] = "Station identity requires field verification"


# =====================================================
# 15. Create candidate-eligibility status
# =====================================================

assessments["Candidate_Eligibility"] = (
    "Eligible conventional fuel station"
)


# FS190 is an LPG/gas facility rather than the
# intended conventional retail fuel-station candidate

assessments.loc[
    assessments["Station_ID"] == "FS190",
    "Candidate_Eligibility"
] = "Ineligible candidate-type mismatch"


# =====================================================
# 16. Apply the physical-screening rules
# =====================================================

screening_rules = {

    "High": "Retain",

    "Medium": "Retain conditionally",

    "Low": "Exclude from immediate shortlist",

    "Uncertain": "Field verification required"
}


assessments["Physical_Screening_Decision"] = (
    assessments["Physical_Category"]
    .map(screening_rules)
)


# Override the decision for FS190

assessments.loc[
    assessments["Station_ID"] == "FS190",
    "Physical_Screening_Decision"
] = "Ineligible - exclude"


print(
    "\nPhysical-screening decisions created successfully."
)


# =====================================================
# 17. Create a simple decision-order column
# =====================================================

decision_order = {

    "Retain": 1,

    "Retain conditionally": 2,

    "Field verification required": 3,

    "Exclude from immediate shortlist": 4,

    "Ineligible - exclude": 5
}


assessments["Decision_Order"] = (
    assessments["Physical_Screening_Decision"]
    .map(decision_order)
)


# =====================================================
# 18. Sort the physical-assessment results
# =====================================================

sorting_columns = ["Decision_Order"]

if "Overall_Suitability_Rank" in assessments.columns:

    sorting_columns.append(
        "Overall_Suitability_Rank"
    )


assessments = assessments.sort_values(
    by=sorting_columns
).reset_index(drop=True)


# =====================================================
# 19. Print the physical-category summary
# =====================================================

print("\nPhysical-category summary:")

physical_category_summary = (
    assessments["Physical_Category"]
    .value_counts()
    .reindex(valid_categories, fill_value=0)
)

print(physical_category_summary)


# =====================================================
# 20. Print the screening-decision summary
# =====================================================

print("\nPhysical-screening decision summary:")

decision_summary = (
    assessments["Physical_Screening_Decision"]
    .value_counts()
)

print(decision_summary)


# =====================================================
# 21. Print the screened candidate table
# =====================================================

display_columns = [
    "Station_ID",
    "Original_Station_Name",
    "Verified_Station_Name",
    "Physical_Category",
    "Candidate_Eligibility",
    "Physical_Screening_Decision"
]


if "Overall_Suitability_Rank" in assessments.columns:

    display_columns.insert(
        3,
        "Overall_Suitability_Rank"
    )


if "Overall_Suitability_Index" in assessments.columns:

    position = display_columns.index(
        "Physical_Category"
    )

    display_columns.insert(
        position,
        "Overall_Suitability_Index"
    )


print("\nPhysically screened candidate results:")

print(
    assessments[
        display_columns
    ].to_string(index=False)
)


# =====================================================
# 22. Save the assessment-summary CSV
# =====================================================

assessments.to_csv(
    summary_output_file,
    index=False
)


print(
    "\nPhysical-assessment summary saved successfully."
)

print(summary_output_file)


# =====================================================
# 23. Load the candidate spatial dataset
# =====================================================

candidate_sites = gpd.read_file(
    candidate_geojson_file
)


print(
    "\nCandidate spatial dataset loaded successfully."
)

print(
    "Number of spatial candidate records:",
    len(candidate_sites)
)

print(
    "Spatial dataset CRS:",
    candidate_sites.crs
)


# =====================================================
# 24. Prepare the assessment fields for spatial joining
# =====================================================

fields_to_join = [

    "Station_ID",

    "Original_Station_Name",

    "Verified_Station_Name",

    "Name_Verification_Status",

    "Physical_Category",

    "Candidate_Eligibility",

    "Physical_Screening_Decision",

    "Decision_Order"
]


# Include all physical-assessment fields where available

optional_keywords = [
    "charging",
    "access",
    "circulation",
    "interference",
    "expansion",
    "imagery",
    "evidence",
    "assessment",
    "note"
]


for column in assessments.columns:

    simplified_column = column.lower()

    if any(
        keyword in simplified_column
        for keyword in optional_keywords
    ):

        if column not in fields_to_join:

            fields_to_join.append(column)


# Keep only fields that exist

fields_to_join = [
    column
    for column in fields_to_join
    if column in assessments.columns
]


assessment_fields = assessments[
    fields_to_join
].copy()


# =====================================================
# 25. Remove old duplicate assessment fields
# =====================================================

fields_to_remove = [
    column
    for column in fields_to_join
    if (
        column != "Station_ID"
        and column in candidate_sites.columns
    )
]


if len(fields_to_remove) > 0:

    candidate_sites = candidate_sites.drop(
        columns=fields_to_remove
    )


# =====================================================
# 26. Join assessments to the spatial candidates
# =====================================================

screened_candidates = candidate_sites.merge(
    assessment_fields,
    on="Station_ID",
    how="left"
)


print(
    "\nPhysical assessments joined to spatial "
    "candidate data successfully."
)

print(
    "Number of joined candidate records:",
    len(screened_candidates)
)


# =====================================================
# 27. Check the spatial join
# =====================================================

missing_physical_results = (
    screened_candidates[
        "Physical_Screening_Decision"
    ]
    .isna()
    .sum()
)


print(
    "\nMissing physical-screening decisions "
    "after the spatial join:"
)

print(missing_physical_results)


if missing_physical_results > 0:

    raise ValueError(
        "Some candidate stations did not receive "
        "physical-screening results."
    )


# =====================================================
# 28. Save the physically screened GeoJSON
# =====================================================

screened_candidates.to_file(
    screened_geojson_file,
    driver="GeoJSON"
)


print(
    "\nPhysically screened spatial dataset "
    "saved successfully."
)

print(screened_geojson_file)


# =====================================================
# 29. Final completion message
# =====================================================

print(
    "\nPhysical-assessment analysis completed successfully."
)

print(
    "\nNumber of candidate stations processed:",
    len(assessments)
)

print(
    "\nThe original GIS suitability scores and ranks "
    "have been retained."
)

print(
    "\nPhysical suitability was applied as a screening "
    "filter rather than as another weighted MCDA score."
)

