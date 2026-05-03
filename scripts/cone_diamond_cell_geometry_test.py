#!/usr/bin/env python3
"""Report the saturated diamond-cell cone automorphism candidate."""

from __future__ import annotations

from stiff_medium.cone_diamond_cell_geometry import assess_diamond_cell_geometry


def main() -> None:
    result = assess_diamond_cell_geometry()

    print("CONE DIAMOND-CELL GEOMETRY")
    print("\nSymmetric saturated diamond:")
    print(f"  graph automorphism residual = {result.symmetric_graph_residual:.6e}")
    print(f"  branch automorphism residual = {result.symmetric_branch_residual:.6e}")
    print(f"  stationary branch weight = {result.symmetric_stationary_weight:.12f}")
    print(f"  linear bias = {result.symmetric_linear_bias:+.6e}")
    print(f"  minimum angle = {result.symmetric_minimum_angle_deg:.6f} deg")

    print("\nAnchor-split control:")
    print(f"  anchor split = {result.broken_anchor_split:+.6f}")
    print(f"  graph automorphism residual = {result.broken_graph_residual:.6e}")
    print(f"  branch automorphism residual = {result.broken_branch_residual:.6e}")
    print(
        "  branch energy split / T = "
        f"{result.broken_branch_energy_over_temp:.6f}"
    )
    print(f"  generator commutator norm = {result.broken_commutator_norm:.6e}")
    print(f"  stationary branch weight = {result.broken_stationary_weight:.12f}")
    print(f"  linear bias = {result.broken_linear_bias:+.6e}")
    print(f"  minimum angle = {result.broken_minimum_angle_deg:.6f} deg")
    print(f"  angle shift = {result.broken_angle_shift_deg:+.6f} deg")

    print("\nStatus:")
    print(
        "  diamond cell forces automorphism = "
        f"{result.diamond_cell_forces_automorphism}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
