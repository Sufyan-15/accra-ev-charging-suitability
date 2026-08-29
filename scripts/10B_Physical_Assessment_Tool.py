"""
Project:
Spatial Decision Support Framework for EV Charging Infrastructure Planning

Script:
10B_Physical_Assessment_Tool.py

Research Objective:
Provide a structured Python-assisted interface for visually
assessing the physical suitability of shortlisted fuel stations
using Google Maps and Google Earth.

Important Interpretation:
The tool records structured visual observations. It does not
confirm engineering, electrical, ownership, safety or regulatory
feasibility.

Author:
Sufyan Yakubu
"""

from pathlib import Path
import webbrowser

import pandas as pd
import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

# =====================================================
# 1. Project folders
# =====================================================

from config import PROJECT_DIR

RESULTS_DIR = PROJECT_DIR / "Results"

# =====================================================
# 2. Input and progress files
# =====================================================

input_file = (
    RESULTS_DIR
    / "Very_High_Suitability_Candidates.csv"
)

progress_file = (
    RESULTS_DIR
    / "Physical_Assessment_Progress.csv"
)

# =====================================================
# 3. Load existing progress or start a new assessment
# =====================================================

if progress_file.exists():

    assessment_data = pd.read_csv(
        progress_file
    )

    print("Existing assessment progress loaded.")

else:

    assessment_data = pd.read_csv(
        input_file
    )

    print("New physical assessment started.")

print(
    "Number of shortlisted stations:",
    len(assessment_data)
)

# =====================================================
# 4. Add structured assessment columns
# =====================================================

assessment_columns = [
    "Bay_Space_Assessment",
    "Circulation_Assessment",
    "Operational_Interference",
    "Expansion_Assessment",
    "Evidence_File"
]

for column in assessment_columns:

    if column not in assessment_data.columns:
        assessment_data[column] = ""

required_existing_columns = [
    "Space_Category",
    "Physical_Score",
    "Imagery_Date",
    "Assessment_Notes"
]

for column in required_existing_columns:

    if column not in assessment_data.columns:
        assessment_data[column] = ""

# =====================================================
# 5. Helper functions
# =====================================================

def clean_text(value):
    """
    Convert missing values into blank text.
    """

    if pd.isna(value):
        return ""

    return str(value)


def existing_or_default(value, valid_choices):
    """
    Return an existing valid response or the default Select.
    """

    cleaned_value = clean_text(value)

    if cleaned_value in valid_choices:
        return cleaned_value

    return "Select"


def calculate_completed_assessments():
    """
    Count stations with an assigned overall category.
    """

    category_values = assessment_data[
        "Space_Category"
    ]

    completed = (
        category_values.notna()
        & category_values.astype(str).str.strip().ne("")
    ).sum()

    return int(completed)


# =====================================================
# 6. Assessment choices
# =====================================================

bay_space_choices = [
    "Select",
    "Adequate",
    "Limited",
    "None visible",
    "Uncertain"
]

circulation_choices = [
    "Select",
    "Good",
    "Manageable",
    "Poor",
    "Uncertain"
]

interference_choices = [
    "Select",
    "Low",
    "Manageable",
    "High",
    "Uncertain"
]

expansion_choices = [
    "Select",
    "Good",
    "Limited",
    "None visible",
    "Uncertain"
]

category_choices = [
    "Select",
    "High",
    "Medium",
    "Low",
    "Uncertain"
]

category_scores = {
    "High": 1.00,
    "Medium": 0.50,
    "Low": 0.00,
    "Uncertain": pd.NA
}

# =====================================================
# 7. Create the application window
# =====================================================

application = tk.Tk()

application.title(
    "EV Charging Candidate Physical Assessment"
)

application.geometry("940x820")

application.minsize(
    900,
    760
)

current_position = 0

# =====================================================
# 8. Create display variables
# =====================================================

station_heading = tk.StringVar()
station_information = tk.StringVar()
progress_information = tk.StringVar()

bay_space_variable = tk.StringVar(
    value="Select"
)

circulation_variable = tk.StringVar(
    value="Select"
)

interference_variable = tk.StringVar(
    value="Select"
)

expansion_variable = tk.StringVar(
    value="Select"
)

category_variable = tk.StringVar(
    value="Select"
)

imagery_date_variable = tk.StringVar()
evidence_file_variable = tk.StringVar()

# =====================================================
# 9. Main interface heading
# =====================================================

heading_label = ttk.Label(
    application,
    text="Physical Suitability Assessment of Shortlisted Fuel Stations",
    font=("Arial", 16, "bold")
)

heading_label.pack(
    pady=(15, 5)
)

progress_label = ttk.Label(
    application,
    textvariable=progress_information,
    font=("Arial", 10)
)

progress_label.pack(
    pady=(0, 10)
)

# =====================================================
# 10. Station information panel
# =====================================================

station_frame = ttk.LabelFrame(
    application,
    text="Candidate Station"
)

station_frame.pack(
    fill="x",
    padx=20,
    pady=5
)

station_title_label = ttk.Label(
    station_frame,
    textvariable=station_heading,
    font=("Arial", 14, "bold")
)

station_title_label.pack(
    anchor="w",
    padx=12,
    pady=(10, 4)
)

station_details_label = ttk.Label(
    station_frame,
    textvariable=station_information,
    justify="left",
    font=("Arial", 10)
)

station_details_label.pack(
    anchor="w",
    padx=12,
    pady=(0, 10)
)

# =====================================================
# 11. Map buttons
# =====================================================

map_button_frame = ttk.Frame(
    application
)

map_button_frame.pack(
    pady=8
)

google_maps_button = ttk.Button(
    map_button_frame,
    text="Open Google Maps"
)

google_maps_button.grid(
    row=0,
    column=0,
    padx=8
)

google_earth_button = ttk.Button(
    map_button_frame,
    text="Open Google Earth"
)

google_earth_button.grid(
    row=0,
    column=1,
    padx=8
)

# =====================================================
# 12. Assessment criteria panel
# =====================================================

criteria_frame = ttk.LabelFrame(
    application,
    text="Structured Visual Assessment"
)

criteria_frame.pack(
    fill="x",
    padx=20,
    pady=5
)

criteria_instructions = ttk.Label(
    criteria_frame,
    text=(
        "Assess only what is reasonably visible. "
        "Choose Uncertain when imagery is unclear."
    ),
    font=("Arial", 9, "italic")
)

criteria_instructions.grid(
    row=0,
    column=0,
    columnspan=2,
    sticky="w",
    padx=12,
    pady=(8, 10)
)

# Charging-bay space

ttk.Label(
    criteria_frame,
    text="1. Visible charging-bay space:"
).grid(
    row=1,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

bay_space_box = ttk.Combobox(
    criteria_frame,
    textvariable=bay_space_variable,
    values=bay_space_choices,
    state="readonly",
    width=24
)

bay_space_box.grid(
    row=1,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Vehicle circulation

ttk.Label(
    criteria_frame,
    text="2. Vehicle access and circulation:"
).grid(
    row=2,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

circulation_box = ttk.Combobox(
    criteria_frame,
    textvariable=circulation_variable,
    values=circulation_choices,
    state="readonly",
    width=24
)

circulation_box.grid(
    row=2,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Operational interference

ttk.Label(
    criteria_frame,
    text="3. Interference with fuel-station operations:"
).grid(
    row=3,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

interference_box = ttk.Combobox(
    criteria_frame,
    textvariable=interference_variable,
    values=interference_choices,
    state="readonly",
    width=24
)

interference_box.grid(
    row=3,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Expansion potential

ttk.Label(
    criteria_frame,
    text="4. Future expansion potential:"
).grid(
    row=4,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

expansion_box = ttk.Combobox(
    criteria_frame,
    textvariable=expansion_variable,
    values=expansion_choices,
    state="readonly",
    width=24
)

expansion_box.grid(
    row=4,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Overall category

ttk.Label(
    criteria_frame,
    text="Overall physical category:"
).grid(
    row=5,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

category_box = ttk.Combobox(
    criteria_frame,
    textvariable=category_variable,
    values=category_choices,
    state="readonly",
    width=24
)

category_box.grid(
    row=5,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Imagery date

ttk.Label(
    criteria_frame,
    text="Imagery date or Unknown:"
).grid(
    row=6,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

imagery_date_entry = ttk.Entry(
    criteria_frame,
    textvariable=imagery_date_variable,
    width=27
)

imagery_date_entry.grid(
    row=6,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Evidence file

ttk.Label(
    criteria_frame,
    text="Screenshot/evidence filename:"
).grid(
    row=7,
    column=0,
    sticky="w",
    padx=12,
    pady=6
)

evidence_file_entry = ttk.Entry(
    criteria_frame,
    textvariable=evidence_file_variable,
    width=45
)

evidence_file_entry.grid(
    row=7,
    column=1,
    sticky="w",
    padx=12,
    pady=6
)

# Assessment notes

ttk.Label(
    criteria_frame,
    text="Assessment notes:"
).grid(
    row=8,
    column=0,
    sticky="nw",
    padx=12,
    pady=6
)

notes_text = tk.Text(
    criteria_frame,
    width=60,
    height=5,
    wrap="word"
)

notes_text.grid(
    row=8,
    column=1,
    sticky="w",
    padx=12,
    pady=(6, 12)
)

# =====================================================
# 13. Load one station into the interface
# =====================================================

def load_station():
    """
    Display the current station and its existing assessment.
    """

    row = assessment_data.iloc[current_position]

    station_id = clean_text(
        row["Station_ID"]
    )

    station_name = clean_text(
        row["name"]
    )

    if station_name == "":
        station_name = "Unnamed station"

    station_heading.set(
        f'{station_id} — {station_name}'
    )

    station_information.set(
        f'Overall rank: {int(row["Overall_Suitability_Rank"])}\n'
        f'Overall suitability score: '
        f'{float(row["Overall_Suitability_Index"]):.4f}\n'
        f'Residential Demand Index: '
        f'{float(row["Residential_Demand_Index"]):.4f}\n'
        f'Destination Demand Index: '
        f'{float(row["Destination_Demand_Index"]):.4f}\n'
        f'Grid Accessibility Index: '
        f'{float(row["Grid_Accessibility_Index"]):.4f}\n'
        f'Latitude: {float(row["Latitude"]):.6f}\n'
        f'Longitude: {float(row["Longitude"]):.6f}'
    )

    completed = calculate_completed_assessments()

    progress_information.set(
        f'Station {current_position + 1} of '
        f'{len(assessment_data)} | '
        f'Completed assessments: {completed}'
    )

    bay_space_variable.set(
        existing_or_default(
            row["Bay_Space_Assessment"],
            bay_space_choices
        )
    )

    circulation_variable.set(
        existing_or_default(
            row["Circulation_Assessment"],
            circulation_choices
        )
    )

    interference_variable.set(
        existing_or_default(
            row["Operational_Interference"],
            interference_choices
        )
    )

    expansion_variable.set(
        existing_or_default(
            row["Expansion_Assessment"],
            expansion_choices
        )
    )

    category_variable.set(
        existing_or_default(
            row["Space_Category"],
            category_choices
        )
    )

    imagery_date_variable.set(
        clean_text(
            row["Imagery_Date"]
        )
    )

    evidence_file_variable.set(
        clean_text(
            row["Evidence_File"]
        )
    )

    notes_text.delete(
        "1.0",
        tk.END
    )

    notes_text.insert(
        "1.0",
        clean_text(
            row["Assessment_Notes"]
        )
    )


# =====================================================
# 14. Open the current station in Google Maps
# =====================================================

def open_google_maps():
    """
    Open the current candidate in Google Maps.
    """

    row = assessment_data.iloc[current_position]

    latitude = row["Latitude"]
    longitude = row["Longitude"]

    maps_url = (
        f"https://www.google.com/maps?q="
        f"{latitude},{longitude}"
    )

    webbrowser.open(
        maps_url
    )


# =====================================================
# 15. Open the current station in Google Earth
# =====================================================

def open_google_earth():
    """
    Open the current candidate in Google Earth Web.
    """

    row = assessment_data.iloc[current_position]

    latitude = row["Latitude"]
    longitude = row["Longitude"]

    earth_url = (
        f"https://earth.google.com/web/search/"
        f"{latitude},{longitude}"
    )

    webbrowser.open(
        earth_url
    )


google_maps_button.configure(
    command=open_google_maps
)

google_earth_button.configure(
    command=open_google_earth
)

# =====================================================
# 16. Validate and save the current assessment
# =====================================================

def save_current_assessment():
    """
    Validate entries and save the current station.
    """

    structured_responses = [
        bay_space_variable.get(),
        circulation_variable.get(),
        interference_variable.get(),
        expansion_variable.get()
    ]

    if "Select" in structured_responses:

        messagebox.showwarning(
            "Incomplete assessment",
            "Please complete all four structured criteria."
        )

        return False

    selected_category = category_variable.get()

    if selected_category == "Select":

        messagebox.showwarning(
            "Missing category",
            "Please choose an overall physical category."
        )

        return False

    imagery_date = (
        imagery_date_variable.get().strip()
    )

    if imagery_date == "":

        messagebox.showwarning(
            "Missing imagery date",
            "Enter the imagery date or type Unknown."
        )

        return False

    assessment_notes = (
        notes_text.get(
            "1.0",
            tk.END
        ).strip()
    )

    if assessment_notes == "":

        messagebox.showwarning(
            "Missing notes",
            "Please record the reason for the assessment."
        )

        return False

    row_index = assessment_data.index[
        current_position
    ]

    assessment_data.at[
        row_index,
        "Bay_Space_Assessment"
    ] = bay_space_variable.get()

    assessment_data.at[
        row_index,
        "Circulation_Assessment"
    ] = circulation_variable.get()

    assessment_data.at[
        row_index,
        "Operational_Interference"
    ] = interference_variable.get()

    assessment_data.at[
        row_index,
        "Expansion_Assessment"
    ] = expansion_variable.get()

    assessment_data.at[
        row_index,
        "Space_Category"
    ] = selected_category

    assessment_data.at[
        row_index,
        "Physical_Score"
    ] = category_scores[selected_category]

    assessment_data.at[
        row_index,
        "Imagery_Date"
    ] = imagery_date

    assessment_data.at[
        row_index,
        "Evidence_File"
    ] = evidence_file_variable.get().strip()

    assessment_data.at[
        row_index,
        "Assessment_Notes"
    ] = assessment_notes

    assessment_data.to_csv(
        progress_file,
        index=False
    )

    progress_information.set(
        f'Station {current_position + 1} of '
        f'{len(assessment_data)} | '
        f'Completed assessments: '
        f'{calculate_completed_assessments()}'
    )

    messagebox.showinfo(
        "Assessment saved",
        (
            f'Assessment for '
            f'{assessment_data.at[row_index, "Station_ID"]} '
            f'was saved successfully.'
        )
    )

    return True


# =====================================================
# 17. Navigation functions
# =====================================================

def show_previous_station():
    """
    Move to the previous candidate.
    """

    global current_position

    if current_position > 0:

        current_position -= 1
        load_station()

    else:

        messagebox.showinfo(
            "First station",
            "You are already at the first station."
        )


def show_next_station():
    """
    Move to the next candidate without saving.
    """

    global current_position

    if current_position < len(assessment_data) - 1:

        current_position += 1
        load_station()

    else:

        messagebox.showinfo(
            "Last station",
            "You are already at the last station."
        )


def save_and_show_next():
    """
    Save the assessment and move to the next station.
    """

    global current_position

    saved = save_current_assessment()

    if not saved:
        return

    if current_position < len(assessment_data) - 1:

        current_position += 1
        load_station()

    else:

        messagebox.showinfo(
            "Assessment complete",
            "The final station has been saved."
        )


# =====================================================
# 18. Navigation and save buttons
# =====================================================

navigation_frame = ttk.Frame(
    application
)

navigation_frame.pack(
    pady=15
)

previous_button = ttk.Button(
    navigation_frame,
    text="Previous Station",
    command=show_previous_station
)

previous_button.grid(
    row=0,
    column=0,
    padx=6
)

save_button = ttk.Button(
    navigation_frame,
    text="Save Current Assessment",
    command=save_current_assessment
)

save_button.grid(
    row=0,
    column=1,
    padx=6
)

save_next_button = ttk.Button(
    navigation_frame,
    text="Save and Next",
    command=save_and_show_next
)

save_next_button.grid(
    row=0,
    column=2,
    padx=6
)

next_button = ttk.Button(
    navigation_frame,
    text="Next Without Saving",
    command=show_next_station
)

next_button.grid(
    row=0,
    column=3,
    padx=6
)

# =====================================================
# 19. Start at first incomplete station
# =====================================================

completed_mask = (
    assessment_data[
        "Space_Category"
    ].notna()
    & assessment_data[
        "Space_Category"
    ].astype(str).str.strip().ne("")
)

incomplete_positions = [
    position
    for position, completed in enumerate(
        completed_mask
    )
    if not completed
]

if incomplete_positions:
    current_position = incomplete_positions[0]

else:
    current_position = 0

load_station()

# =====================================================
# 20. Start the assessment application
# =====================================================

application.mainloop()
