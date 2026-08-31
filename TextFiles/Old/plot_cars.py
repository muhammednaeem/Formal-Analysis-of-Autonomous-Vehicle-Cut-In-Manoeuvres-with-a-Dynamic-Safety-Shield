#!/usr/bin/env python3
"""
Read clock_values.txt and generate vehicle-path plots.

Place this script inside:
    UPPAAL_Model_cutin/TextFiles/

Expected project structure:

UPPAAL_Model_cutin/
├── TextFiles/
│   ├── clock_values.txt
│   └── plot_cars.py
└── figures/
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle


USE_LATEST_RUN = True
MAX_SHIELD_RECTANGLES = 100
DPI = 300

TEXTFILES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEXTFILES_DIR.parent

INPUT_FILE = TEXTFILES_DIR / "clock_values.txt"
FIGURES_DIR = PROJECT_DIR / "figures"

CARS_PATH_FILE = FIGURES_DIR / "CarsPath.png"
SHIELD_PATH_FILE = FIGURES_DIR / "CarsPath(safetyshield).png"

COLUMN_NAMES = [
    "T",
    "X_Ego",
    "Y_Ego",
    "X_rear",
    "Y_rear",
    "X_slow",
    "Y_slow",
    "S_left_edge",
    "S_right_edge",
    "S_bottom_edge",
    "S_top_edge",
]


def load_clock_values(file_path: Path) -> np.ndarray:
    """Load rows containing exactly 11 numeric values."""
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()

            if not stripped:
                continue

            parts = stripped.split()

            if len(parts) != len(COLUMN_NAMES):
                print(
                    f"Skipping line {line_number}: expected "
                    f"{len(COLUMN_NAMES)} values, found {len(parts)}.",
                    file=sys.stderr,
                )
                continue

            try:
                row = [float(value) for value in parts]
            except ValueError:
                print(
                    f"Skipping line {line_number}: contains non-numeric data.",
                    file=sys.stderr,
                )
                continue

            if not np.all(np.isfinite(row)):
                print(
                    f"Skipping line {line_number}: contains NaN or infinity.",
                    file=sys.stderr,
                )
                continue

            rows.append(row)

    if not rows:
        raise ValueError(f"No valid data rows were found in {file_path}")

    return np.asarray(rows, dtype=float)


def keep_latest_run(data: np.ndarray) -> np.ndarray:
    """
    Keep only the latest appended UPPAAL run.

    A new run is detected when T becomes smaller than the previous T value.
    """
    if len(data) < 2:
        return data

    reset_indices = np.where(np.diff(data[:, 0]) < 0)[0]

    if reset_indices.size == 0:
        return data

    return data[reset_indices[-1] + 1:]


def add_plot_limits(
    ax,
    x_values: np.ndarray,
    y_values: np.ndarray,
) -> None:
    """
    Set independent x and y limits.

    Do not use axis('equal'), because the longitudinal range is much larger
    than the lateral range and would flatten the lane-change trajectory.
    """
    x_values = np.asarray(x_values, dtype=float)
    y_values = np.asarray(y_values, dtype=float)

    x_min = np.nanmin(x_values)
    x_max = np.nanmax(x_values)
    y_min = np.nanmin(y_values)
    y_max = np.nanmax(y_values)

    x_range = x_max - x_min
    y_range = y_max - y_min

    x_padding = max(0.02 * x_range, 1.0)
    y_padding = max(0.12 * y_range, 0.25)

    ax.set_xlim(x_min - x_padding, x_max + x_padding)
    ax.set_ylim(y_min - y_padding, y_max + y_padding)
    ax.set_aspect("auto")


def configure_axes(ax, title: str) -> None:
    ax.set_title(title)
    ax.set_xlabel("Longitudinal position, x (m)")
    ax.set_ylabel("Lateral position, y (m)")
    ax.grid(True, alpha=0.3)


def plot_vehicle_paths(data: np.ndarray, output_file: Path) -> None:
    """Plot the trajectories of the ego, rear, and slow cars."""
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(data[:, 1], data[:, 2], linewidth=2.2, label="Ego car")
    ax.plot(data[:, 3], data[:, 4], linewidth=2.2, label="Rear car")
    ax.plot(data[:, 5], data[:, 6], linewidth=2.2, label="Slow car")

    ax.scatter(data[0, 1], data[0, 2], marker="o", s=35)
    ax.scatter(data[0, 3], data[0, 4], marker="o", s=35)
    ax.scatter(data[0, 5], data[0, 6], marker="o", s=35)

    all_x = np.concatenate((data[:, 1], data[:, 3], data[:, 5]))
    all_y = np.concatenate((data[:, 2], data[:, 4], data[:, 6]))

    add_plot_limits(ax, all_x, all_y)
    configure_axes(ax, "Vehicle Paths")
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_file, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def shield_sample_indices(number_of_rows: int) -> np.ndarray:
    count = min(number_of_rows, MAX_SHIELD_RECTANGLES)

    if count <= 1:
        return np.array([0], dtype=int)

    return np.unique(
        np.linspace(0, number_of_rows - 1, count, dtype=int)
    )


def plot_vehicle_paths_with_shield(
    data: np.ndarray,
    output_file: Path,
) -> None:
    """Plot all car trajectories and the ego-car safety shield."""
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(data[:, 1], data[:, 2], linewidth=2.2, label="Ego car")
    ax.plot(data[:, 3], data[:, 4], linewidth=2.2, label="Rear car")
    ax.plot(data[:, 5], data[:, 6], linewidth=2.2, label="Slow car")

    left_edges = data[:, 7]
    right_edges = data[:, 8]
    bottom_edges = data[:, 9]
    top_edges = data[:, 10]

    valid_shield_rows = []

    for index in shield_sample_indices(len(data)):
        left = min(left_edges[index], right_edges[index])
        right = max(left_edges[index], right_edges[index])
        bottom = min(bottom_edges[index], top_edges[index])
        top = max(bottom_edges[index], top_edges[index])

        width = right - left
        height = top - bottom

        if width <= 0 or height <= 0:
            continue

        valid_shield_rows.append(index)

        ax.add_patch(
            Rectangle(
                (left, bottom),
                width,
                height,
                fill=True,
                alpha=0.08,
                linewidth=0.6,
            )
        )

    # Draw the final shield boundary more clearly.
    left = min(left_edges[-1], right_edges[-1])
    right = max(left_edges[-1], right_edges[-1])
    bottom = min(bottom_edges[-1], top_edges[-1])
    top = max(bottom_edges[-1], top_edges[-1])

    if right > left and top > bottom:
        ax.add_patch(
            Rectangle(
                (left, bottom),
                right - left,
                top - bottom,
                fill=False,
                linewidth=1.5,
            )
        )

    all_x_parts = [data[:, 1], data[:, 3], data[:, 5]]
    all_y_parts = [data[:, 2], data[:, 4], data[:, 6]]

    if valid_shield_rows:
        shield_rows = np.asarray(valid_shield_rows, dtype=int)
        all_x_parts.extend(
            [left_edges[shield_rows], right_edges[shield_rows]]
        )
        all_y_parts.extend(
            [bottom_edges[shield_rows], top_edges[shield_rows]]
        )

    all_x = np.concatenate(all_x_parts)
    all_y = np.concatenate(all_y_parts)

    add_plot_limits(ax, all_x, all_y)
    configure_axes(ax, "Vehicle Paths with Ego-Car Safety Shield")

    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(alpha=0.15))
    labels.append("Ego safety shield")
    ax.legend(handles, labels)

    fig.tight_layout()
    fig.savefig(output_file, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_clock_values(INPUT_FILE)

    if USE_LATEST_RUN:
        data = keep_latest_run(data)

    if len(data) == 0:
        raise ValueError("The selected UPPAAL run contains no data.")

    plot_vehicle_paths(data, CARS_PATH_FILE)
    plot_vehicle_paths_with_shield(data, SHIELD_PATH_FILE)

    print(f"Processed {len(data)} data rows.")
    print(f"Created: {CARS_PATH_FILE}")
    print(f"Created: {SHIELD_PATH_FILE}")


if __name__ == "__main__":
    main()
