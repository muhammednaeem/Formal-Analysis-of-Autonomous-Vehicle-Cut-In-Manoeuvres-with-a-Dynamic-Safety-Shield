#!/usr/bin/env python3
"""
Plot vehicle paths with main rotated safety shield and inner rotated shield.

Place this file inside:
    UPPAAL_Model_cutin/TextFiles/plot_cars.py

Expected clock_values.txt row format, 23 values:
T
X_Ego Y_Ego
X_rear Y_rear
X_slow Y_slow
main shield:  S_front_left_x S_front_left_y S_front_right_x S_front_right_y
              S_rear_right_x S_rear_right_y S_rear_left_x S_rear_left_y
inner shield: IS_front_left_x IS_front_left_y IS_front_right_x IS_front_right_y
              IS_rear_right_x IS_rear_right_y IS_rear_left_x IS_rear_left_y
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Polygon

USE_LATEST_RUN = True
MAX_SHIELD_POLYGONS = 120
DPI = 300
SAFETY_SHIELD_PLOT_MODE = "auto"  # "auto" keeps the y-axis readable for the full trajectory

TEXTFILES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEXTFILES_DIR.parent

INPUT_FILE = TEXTFILES_DIR / "clock_values.txt"
FIGURES_DIR = PROJECT_DIR / "figures"

CARS_PATH_FILE = FIGURES_DIR / "CarsPath.png"
SHIELD_PATH_FILE = FIGURES_DIR / "CarsPath(safetyshield).png"
SHIELD_EQUAL_ZOOM_FILE = FIGURES_DIR / "CarsPath(safetyshield_equal_zoom).png"

COLUMN_NAMES = [
    "T",
    "X_Ego", "Y_Ego",
    "X_rear", "Y_rear",
    "X_slow", "Y_slow",
    "S_front_left_x", "S_front_left_y",
    "S_front_right_x", "S_front_right_y",
    "S_rear_right_x", "S_rear_right_y",
    "S_rear_left_x", "S_rear_left_y",
    "IS_front_left_x", "IS_front_left_y",
    "IS_front_right_x", "IS_front_right_y",
    "IS_rear_right_x", "IS_rear_right_y",
    "IS_rear_left_x", "IS_rear_left_y",
]

T = 0
X_EGO, Y_EGO = 1, 2
X_REAR, Y_REAR = 3, 4
X_SLOW, Y_SLOW = 5, 6

S_FRONT_LEFT_X, S_FRONT_LEFT_Y = 7, 8
S_FRONT_RIGHT_X, S_FRONT_RIGHT_Y = 9, 10
S_REAR_RIGHT_X, S_REAR_RIGHT_Y = 11, 12
S_REAR_LEFT_X, S_REAR_LEFT_Y = 13, 14

IS_FRONT_LEFT_X, IS_FRONT_LEFT_Y = 15, 16
IS_FRONT_RIGHT_X, IS_FRONT_RIGHT_Y = 17, 18
IS_REAR_RIGHT_X, IS_REAR_RIGHT_Y = 19, 20
IS_REAR_LEFT_X, IS_REAR_LEFT_Y = 21, 22


def load_clock_values(file_path: Path) -> np.ndarray:
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    rows = []
    expected = len(COLUMN_NAMES)

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            parts = stripped.split()
            if len(parts) != expected:
                print(
                    f"Skipping line {line_number}: expected {expected} values, found {len(parts)}.",
                    file=sys.stderr,
                )
                continue

            try:
                row = [float(value) for value in parts]
            except ValueError:
                print(f"Skipping line {line_number}: non-numeric data.", file=sys.stderr)
                continue

            if not np.all(np.isfinite(row)):
                print(f"Skipping line {line_number}: NaN or infinity.", file=sys.stderr)
                continue

            rows.append(row)

    if not rows:
        raise ValueError(f"No valid rows found in {file_path}")

    return np.asarray(rows, dtype=float)


def keep_latest_run(data: np.ndarray) -> np.ndarray:
    if len(data) < 2:
        return data

    reset_indices = np.where(np.diff(data[:, T]) < 0)[0]
    if reset_indices.size == 0:
        return data

    return data[reset_indices[-1] + 1:]


def configure_axes(ax, title: str) -> None:
    ax.set_title(title, pad=10)
    ax.set_xlabel("Longitudinal position, x (m)", labelpad=8)
    ax.set_ylabel("Lateral position, y (m)", labelpad=10)
    ax.tick_params(axis="both", labelsize=10)
    ax.grid(True, alpha=0.3)


def vehicle_xy(data: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.concatenate((data[:, X_EGO], data[:, X_REAR], data[:, X_SLOW]))
    y = np.concatenate((data[:, Y_EGO], data[:, Y_REAR], data[:, Y_SLOW]))
    return x, y


def main_shield_points(row: np.ndarray) -> np.ndarray:
    return np.array(
        [
            [row[S_FRONT_LEFT_X], row[S_FRONT_LEFT_Y]],
            [row[S_FRONT_RIGHT_X], row[S_FRONT_RIGHT_Y]],
            [row[S_REAR_RIGHT_X], row[S_REAR_RIGHT_Y]],
            [row[S_REAR_LEFT_X], row[S_REAR_LEFT_Y]],
        ],
        dtype=float,
    )


def inner_shield_points(row: np.ndarray) -> np.ndarray:
    return np.array(
        [
            [row[IS_FRONT_LEFT_X], row[IS_FRONT_LEFT_Y]],
            [row[IS_FRONT_RIGHT_X], row[IS_FRONT_RIGHT_Y]],
            [row[IS_REAR_RIGHT_X], row[IS_REAR_RIGHT_Y]],
            [row[IS_REAR_LEFT_X], row[IS_REAR_LEFT_Y]],
        ],
        dtype=float,
    )


def is_valid_polygon(points: np.ndarray) -> bool:
    return (
        points.shape == (4, 2)
        and np.all(np.isfinite(points))
        and np.ptp(points[:, 0]) > 0
        and np.ptp(points[:, 1]) > 0
    )


def sample_indices(number_of_rows: int) -> np.ndarray:
    count = min(number_of_rows, MAX_SHIELD_POLYGONS)
    if count <= 1:
        return np.array([0], dtype=int)
    return np.unique(np.linspace(0, number_of_rows - 1, count, dtype=int))


def set_auto_limits(ax, x_values: np.ndarray, y_values: np.ndarray) -> None:
    x_min, x_max = np.nanmin(x_values), np.nanmax(x_values)
    y_min, y_max = np.nanmin(y_values), np.nanmax(y_values)

    x_range = max(x_max - x_min, 1.0)
    y_range = max(y_max - y_min, 1.0)

    ax.set_xlim(x_min - max(0.03 * x_range, 2.0), x_max + max(0.03 * x_range, 2.0))
    ax.set_ylim(y_min - max(0.15 * y_range, 0.4), y_max + max(0.15 * y_range, 0.4))
    ax.set_aspect("auto")


def set_equal_zoom_limits(ax, data: np.ndarray, shield_x: np.ndarray, shield_y: np.ndarray) -> None:
    x_values = np.concatenate((data[:, X_EGO], shield_x))
    y_values = np.concatenate((data[:, Y_EGO], shield_y))

    x_min, x_max = np.nanmin(x_values), np.nanmax(x_values)
    y_min, y_max = np.nanmin(y_values), np.nanmax(y_values)

    x_range = max(x_max - x_min, 1.0)
    y_range = max(y_max - y_min, 1.0)

    ax.set_xlim(x_min - max(0.08 * x_range, 5.0), x_max + max(0.08 * x_range, 5.0))
    ax.set_ylim(y_min - max(0.30 * y_range, 3.0), y_max + max(0.30 * y_range, 3.0))
    ax.set_aspect("equal", adjustable="box")


def shield_size(points: np.ndarray) -> tuple[float, float]:
    front_width = np.linalg.norm(points[0] - points[1])
    rear_width = np.linalg.norm(points[3] - points[2])
    left_length = np.linalg.norm(points[0] - points[3])
    right_length = np.linalg.norm(points[1] - points[2])
    return (left_length + right_length) / 2, (front_width + rear_width) / 2


def print_size_check(data: np.ndarray) -> None:
    main_len, main_wid = shield_size(main_shield_points(data[-1]))
    inner_len, inner_wid = shield_size(inner_shield_points(data[-1]))
    print(f"Main shield last sample:  length ≈ {main_len:.3f} m, width ≈ {main_wid:.3f} m")
    print(f"Inner shield last sample: length ≈ {inner_len:.3f} m, width ≈ {inner_wid:.3f} m")


def plot_vehicle_paths(data: np.ndarray, output_file: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(data[:, X_EGO], data[:, Y_EGO], linewidth=2.2, label="Ego car")
    ax.plot(data[:, X_REAR], data[:, Y_REAR], linewidth=2.2, label="Rear car")
    ax.plot(data[:, X_SLOW], data[:, Y_SLOW], linewidth=2.2, label="Slow car")

    ax.scatter(data[0, X_EGO], data[0, Y_EGO], marker="o", s=35)
    ax.scatter(data[0, X_REAR], data[0, Y_REAR], marker="o", s=35)
    ax.scatter(data[0, X_SLOW], data[0, Y_SLOW], marker="o", s=35)

    x, y = vehicle_xy(data)
    set_auto_limits(ax, x, y)
    configure_axes(ax, "Vehicle Paths")
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_file, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_paths_with_two_shields(data: np.ndarray, output_file: Path, mode: str = SAFETY_SHIELD_PLOT_MODE) -> None:
    fig, ax = plt.subplots(figsize=(14, 7), constrained_layout=True)

    ax.plot(data[:, X_EGO], data[:, Y_EGO], linewidth=2.2, label="Ego car")
    ax.plot(data[:, X_REAR], data[:, Y_REAR], linewidth=2.2, label="Rear car")
    ax.plot(data[:, X_SLOW], data[:, Y_SLOW], linewidth=2.2, label="Slow car")

    all_shield_x = []
    all_shield_y = []

    for index in sample_indices(len(data)):
        outer = main_shield_points(data[index])
        inner = inner_shield_points(data[index])

        if is_valid_polygon(outer):
            all_shield_x.extend(outer[:, 0])
            all_shield_y.extend(outer[:, 1])
            ax.add_patch(Polygon(outer, closed=True, fill=True, alpha=0.05, linewidth=0.5))

        if is_valid_polygon(inner):
            all_shield_x.extend(inner[:, 0])
            all_shield_y.extend(inner[:, 1])
            ax.add_patch(Polygon(inner, closed=True, fill=True, alpha=0.12, linewidth=0.5))

    final_outer = main_shield_points(data[-1])
    final_inner = inner_shield_points(data[-1])

    if is_valid_polygon(final_outer):
        ax.add_patch(Polygon(final_outer, closed=True, fill=False, linewidth=1.7))
        all_shield_x.extend(final_outer[:, 0])
        all_shield_y.extend(final_outer[:, 1])

    if is_valid_polygon(final_inner):
        ax.add_patch(Polygon(final_inner, closed=True, fill=False, linewidth=1.7, linestyle="--"))
        all_shield_x.extend(final_inner[:, 0])
        all_shield_y.extend(final_inner[:, 1])

    all_shield_x = np.asarray(all_shield_x, dtype=float)
    all_shield_y = np.asarray(all_shield_y, dtype=float)

    if mode == "equal_zoom" and len(all_shield_x) > 0:
        set_equal_zoom_limits(ax, data, all_shield_x, all_shield_y)
    else:
        vx, vy = vehicle_xy(data)
        if len(all_shield_x) > 0:
            vx = np.concatenate((vx, all_shield_x))
            vy = np.concatenate((vy, all_shield_y))
        set_auto_limits(ax, vx, vy)

    configure_axes(ax, "Vehicle Paths with Main and Inner Safety Shields")

    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(alpha=0.08))
    labels.append("Main shield")
    handles.append(Patch(alpha=0.18))
    labels.append("Inner shield")
    ax.legend(handles, labels, loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0.0)

    fig.savefig(output_file, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    data = load_clock_values(INPUT_FILE)
    if USE_LATEST_RUN:
        data = keep_latest_run(data)

    if len(data) == 0:
        raise ValueError("No data in selected UPPAAL run.")

    print_size_check(data)
    plot_vehicle_paths(data, CARS_PATH_FILE)
    # Full trajectory view: readable y-axis, good for paper figures.
    plot_paths_with_two_shields(data, SHIELD_PATH_FILE, mode="auto")

    # Equal-scale view: useful only for checking the true physical shield shape.
    # This can look vertically compressed when the x-range is very large.
    plot_paths_with_two_shields(data, SHIELD_EQUAL_ZOOM_FILE, mode="equal_zoom")

    print(f"Processed {len(data)} rows.")
    print(f"Created: {CARS_PATH_FILE}")
    print(f"Created: {SHIELD_PATH_FILE}")
    print(f"Created: {SHIELD_EQUAL_ZOOM_FILE}")


if __name__ == "__main__":
    main()
