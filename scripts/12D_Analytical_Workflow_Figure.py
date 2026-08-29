"""
12D_Analytical_Workflow_Figure.py

Objective:
    Recreate Figure 1 for the manuscript with clearly visible arrows.

Outputs:
    Figure_1_Analytical_Framework.png  (600 dpi)
    Figure_1_Analytical_Framework.pdf  (vector)
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle


# -----------------------------------------------------------------------------
# 1. OUTPUT SETTINGS
# -----------------------------------------------------------------------------

from config import PROJECT_DIR

OUTPUT_DIR = PROJECT_DIR / "Maps" / "Manuscript_Figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PNG_PATH = OUTPUT_DIR / "Figure_1_Analytical_Framework.png"
PDF_PATH = OUTPUT_DIR / "Figure_1_Analytical_Framework.pdf"


# -----------------------------------------------------------------------------
# 2. FIGURE SETTINGS
# -----------------------------------------------------------------------------

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

fig, ax = plt.subplots(figsize=(8.3, 10.2))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")
ax.set_xlim(0, 10)
ax.set_ylim(0.82, 12.3)
ax.axis("off")


# -----------------------------------------------------------------------------
# 3. COLOURS AND DRAWING FUNCTIONS
# -----------------------------------------------------------------------------

EDGE_COLOUR = "#263746"
TEXT_COLOUR = "#14232E"
ARROW_COLOUR = "#17324D"

STAGE_COLOURS = [
    "#D9EAF7",  # Data preparation
    "#DDEFD8",  # Spatial analysis
    "#FFF1CC",  # Index construction
    "#FBE0CF",  # Suitability modelling
    "#E5DDF4",  # Candidate screening
]


def add_stage_box(number, y, title, lines, colour):
    """Draw one rounded workflow stage."""

    x = 1.0
    width = 8.0
    height = 1.52

    stage_box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.035,rounding_size=0.08",
        linewidth=1.6,
        edgecolor=EDGE_COLOUR,
        facecolor=colour,
        zorder=3,
    )
    ax.add_patch(stage_box)

    number_circle = Circle(
        (x + 0.55, y + height - 0.40),
        radius=0.18,
        facecolor="#28516E",
        edgecolor="none",
        zorder=4,
    )
    ax.add_patch(number_circle)
    ax.text(
        x + 0.55,
        y + height - 0.40,
        str(number),
        ha="center",
        va="center",
        fontsize=9.0,
        fontweight="bold",
        color="white",
        zorder=5,
    )

    ax.text(
        x + width / 2,
        y + height - 0.34,
        title,
        ha="center",
        va="center",
        fontsize=12.2,
        fontweight="bold",
        color=TEXT_COLOUR,
        zorder=5,
    )

    ax.text(
        x + width / 2,
        y + 0.54,
        "\n".join(lines),
        ha="center",
        va="center",
        fontsize=9.4,
        linespacing=1.23,
        color=TEXT_COLOUR,
        zorder=5,
    )

    return x, y, width, height


def add_vertical_arrow(upper_box, lower_box):
    """Connect two stages with a bold, high-contrast arrow."""

    upper_x, upper_y, upper_width, _ = upper_box
    lower_x, lower_y, lower_width, lower_height = lower_box

    start = (upper_x + upper_width / 2, upper_y - 0.05)
    end = (lower_x + lower_width / 2, lower_y + lower_height + 0.05)

    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=25,
        linewidth=3.2,
        edgecolor=ARROW_COLOUR,
        facecolor=ARROW_COLOUR,
        shrinkA=0,
        shrinkB=0,
        connectionstyle="arc3,rad=0",
        clip_on=False,
        zorder=2,
    )
    ax.add_patch(arrow)


# -----------------------------------------------------------------------------
# 4. TITLE
# -----------------------------------------------------------------------------

ax.text(
    5,
    12.05,
    "Analytical Framework for Prioritising Existing Fuel Stations",
    ha="center",
    va="top",
    fontsize=16.2,
    fontweight="bold",
    color=TEXT_COLOUR,
)
ax.text(
    5,
    11.60,
    "for EV-Charging Infrastructure in Metropolitan Accra",
    ha="center",
    va="top",
    fontsize=14.0,
    fontweight="bold",
    color=TEXT_COLOUR,
)


# -----------------------------------------------------------------------------
# 5. FIVE-STAGE ANALYTICAL WORKFLOW
# -----------------------------------------------------------------------------

stages = [
    add_stage_box(
        1,
        9.62,
        "Data preparation",
        [
            "Fuel stations",
            "Population raster",
            "Activity destinations and substations",
            "Data cleaning and projection",
        ],
        STAGE_COLOURS[0],
    ),
    add_stage_box(
        2,
        7.48,
        "Spatial analysis",
        [
            "Nearest-feature distance calculation",
            "Population estimation within 1 km buffers",
            "Indicator normalization",
        ],
        STAGE_COLOURS[1],
    ),
    add_stage_box(
        3,
        5.34,
        "Index construction",
        [
            "Residential Demand Index (RDI)",
            "Destination Demand Index (DDI)",
            "Grid Accessibility Index (GAI)",
        ],
        STAGE_COLOURS[2],
    ),
    add_stage_box(
        4,
        3.20,
        "Suitability modelling",
        [
            "Equal-weight multi-criteria decision analysis",
            "Overall Suitability Index and ranking",
            "Jenks Natural Breaks classification",
            "Weight and population-buffer sensitivity",
        ],
        STAGE_COLOURS[3],
    ),
    add_stage_box(
        5,
        1.06,
        "Candidate screening",
        [
            "Very High-suitability shortlist",
            "Physical-site assessment",
            "Non-compensatory screening decisions",
            "Final candidate recommendations",
        ],
        STAGE_COLOURS[4],
    ),
]

for upper_stage, lower_stage in zip(stages[:-1], stages[1:]):
    add_vertical_arrow(upper_stage, lower_stage)


# -----------------------------------------------------------------------------
# 6. SAVE PUBLICATION-QUALITY OUTPUTS
# -----------------------------------------------------------------------------

plt.subplots_adjust(left=0.04, right=0.96, top=0.98, bottom=0.01)
fig.savefig(
    PNG_PATH,
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.03,
    facecolor="white"
)
fig.savefig(
    PDF_PATH,
    bbox_inches="tight",
    pad_inches=0.03,
    facecolor="white"
)
plt.close(fig)

print("Figure 1 created successfully.")
print(f"PNG: {PNG_PATH}")
print(f"PDF: {PDF_PATH}")
