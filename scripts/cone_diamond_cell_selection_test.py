#!/usr/bin/env python3
"""Report the minimal-cell selection audit for the cone diamond geometry."""

from __future__ import annotations

from stiff_medium.cone_diamond_cell_selection import assess_diamond_cell_selection


def main() -> None:
    result = assess_diamond_cell_selection()

    print("CONE DIAMOND-CELL SELECTION")
    print(f"total graphs scanned = {result.total_graphs_scanned}")

    print("\nFull constraints:")
    print(f"  selected min edge count = {result.selected_min_edge_count}")
    print(f"  selected min graph count = {result.selected_min_graph_count}")
    print(f"  selected signature = {', '.join(result.selected_signature)}")
    print(f"  selected is diamond = {result.selected_is_diamond}")
    print(
        "  diamond unique under constraints = "
        f"{result.diamond_unique_under_constraints}"
    )

    print("\nDropped-constraint controls:")
    print(
        "  without direct exchange min edge count = "
        f"{result.without_direct_min_edge_count}"
    )
    print(
        "  without direct exchange signature = "
        f"{', '.join(result.without_direct_signature)}"
    )
    print(
        "  without two anchors min edge count = "
        f"{result.without_two_anchors_min_edge_count}"
    )
    print(
        "  without two anchors signature = "
        f"{', '.join(result.without_two_anchors_signature)}"
    )

    print("\nStatus:")
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
