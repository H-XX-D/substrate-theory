#!/usr/bin/env python3
"""Report the cone quartic lattice-symmetry audit."""

from __future__ import annotations

from stiff_medium.cone_lattice_microgeometry import (
    allowed_orientation_selectors,
    assess_cone_lattice_microgeometry,
)


def main() -> None:
    result = assess_cone_lattice_microgeometry()

    print("CONE LATTICE MICROGEOMETRY AUDIT")
    print("\nAllowed selectors without self-dual exchange:")
    for term in allowed_orientation_selectors(self_dual_exchange=False):
        print(f"  - {term}")
    print("\nAllowed selectors with self-dual exchange:")
    for term in allowed_orientation_selectors(self_dual_exchange=True):
        print(f"  - {term}")

    print("\nNumerical gates:")
    print(
        "quadratic bias allowed without dual = "
        f"{result.quadratic_bias_allowed_without_dual}"
    )
    print(f"self-dual exchange required = {result.self_dual_exchange_required}")
    print(
        "quartic minimum angle = "
        f"{result.quartic_minimum_angle_deg:.6f} deg"
    )
    print(
        "quartic curvature at minimum = "
        f"{result.quartic_curvature_at_minimum:.6e}"
    )
    print(
        "biased minimum angle = "
        f"{result.biased_minimum_angle_deg:.6f} deg"
    )
    print(f"bias shift = {result.bias_shift_deg:+.6f} deg")
    print(
        "negative-beta minimum angle = "
        f"{result.negative_beta_minimum_angle_deg:.6f} deg"
    )
    print(f"beta positive required = {result.beta_positive_required}")
    print(f"cone forced by current symmetry = {result.cone_forced_by_current_symmetry}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
