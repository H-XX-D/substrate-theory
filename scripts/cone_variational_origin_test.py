#!/usr/bin/env python3
"""Report equal-partition variational origin for the cone geometry."""

from __future__ import annotations

from stiff_medium.cone_variational_origin import assess_cone_variational_origin


def main() -> None:
    result = assess_cone_variational_origin()

    print("CONE VARIATIONAL ORIGIN")
    print(f"minimum angle = {result.minimum_angle_deg:.6f} deg")
    print(f"penalty at minimum = {result.penalty_at_minimum:.6e}")
    print(f"penalty at 0 deg = {result.penalty_at_0_deg:.6e}")
    print(f"penalty at 90 deg = {result.penalty_at_90_deg:.6e}")
    print(f"curvature at minimum = {result.curvature_at_minimum:.6e}")
    print(f"cone residual at minimum = {result.cone_residual_at_minimum:+.6e}")
    print(
        "selected without balance term = "
        f"{result.selected_without_balance_term}"
    )
    print(f"verdict = {result.verdict}")


if __name__ == "__main__":
    main()
