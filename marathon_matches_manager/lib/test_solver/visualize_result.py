import re
import statistics
from typing import List, Optional

import numpy as np
from asciichartpy import plot
from rich.console import Console
from rich.table import Table

from marathon_matches_manager.lib.test_solver.model import TestResult


def draw_histogram(
    scores: List[float],
    width: Optional[int] = None,
    pin_count: Optional[int] = None,
    height: Optional[int] = None,
    pin_width: Optional[int] = None,
):
    if width is None:
        width = min(30, max(2, len(scores) // 3))

    if pin_width is None:
        pin_width = max(1, round(70 / width))

    if pin_count is None:
        pin_count = max(2, round(width * pin_width // 20))

    min_score = min(scores)
    max_score = max(scores)

    bins = np.linspace(min_score, max_score, width + 1)
    histogram_data, _ = np.histogram(scores, bins=bins)

    # Resample histogram_data based on pin width
    histogram_data = np.repeat(histogram_data, pin_width)

    if height is None:
        height = min(30, max(1, max(histogram_data) - min(histogram_data)))

    chart = plot(histogram_data, {"height": height})

    # Replace float y-axis labels with int and remove duplicates
    chart = re.sub(r"(\d+)\.\d+", r"\1", chart)
    chart_lines = chart.split("\n")
    seen = set()

    for idx in reversed(range(len(chart_lines))):
        line = chart_lines[idx]
        label = line.split()[0]
        if label in seen:
            label_start_idx = line.find(label)
            offset = label_start_idx + len(label)
            chart_lines[idx] = " " * offset + line[offset:]
        else:
            seen.add(label)

    chart = "\n".join(chart_lines)

    # Print the chart and the x-axis
    print(chart)

    # Calculate the scores to display on x-axis
    x_labels = np.linspace(min_score, max_score, pin_count)

    space_width = max(0, (width - 1) * pin_width - sum(map(len, map(str, map(round, x_labels[:-1])))))
    while space_width < len(x_labels) - 1:
        pin_count -= 1
        x_labels = np.linspace(min_score, max_score, pin_count)
        space_width = max(0, (width - 1) * pin_width - sum(map(len, map(str, map(round, x_labels[:-1])))))

    res_space_count = space_width

    print(" " * (8 - ((len(str(round(x_labels[0]))) + len(str(round(x_labels[-1])))) // 4) + pin_width // 2), end="")
    for idx, label in enumerate(x_labels):
        print(str(round(label)), end="")
        if idx != len(x_labels) - 1:
            space_count = res_space_count // (len(x_labels) - idx - 1)
            print(" " * space_count, end="")
            res_space_count -= space_count

    print()


def display_results(test_results: List[TestResult]):
    table = Table(show_header=True, header_style="#00a381")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_column("Corresponding Case")
    table.add_column("Index")

    for idx in range(len(test_results[0].result)):
        results = [float(test_result.result[idx]) for test_result in test_results]

        avg = sum(results) / len(results)
        median = statistics.median(results)
        max_val = max(results)
        min_val = min(results)

        max_idx = results.index(max_val)
        min_idx = results.index(min_val)

        max_case = str(test_results[max_idx].case.file_name)
        min_case = str(test_results[min_idx].case.file_name)

        table.add_row("Average", f"{avg:.2f}", "-", "-")
        table.add_row("Median", f"{median:.2f}", "-", "-")
        table.add_row("Max Value", f"{max_val:.2f}", max_case[:20], str(max_idx))
        table.add_row("Min Value", f"{min_val:.2f}", min_case[:20], str(min_idx))

        if idx != len(test_results[0].result) - 1:
            table.add_row("", "", "")

    Console().print(table)
