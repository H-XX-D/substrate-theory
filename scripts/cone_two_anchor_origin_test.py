#!/usr/bin/env python3
"""Report the two-anchor phase-slip-origin mechanism."""

from __future__ import annotations

from stiff_medium.cone_two_anchor_origin import assess_two_anchor_origin


def main() -> None:
    result = assess_two_anchor_origin()

    print("CONE TWO-ANCHOR ORIGIN")
    print("\nPhase-slip endpoints:")
    print(f"  endpoint count = {result.endpoint_count}")
    print(f"  signed endpoint charge = {result.signed_endpoint_charge:+.6f}")
    print(f"  single-anchor charge = {result.single_anchor_charge:+.6f}")
    print(
        "  two-anchor topology selected = "
        f"{result.two_anchor_topology_selected}"
    )

    print("\nSaturation compliance:")
    print(
        "  reference barrier curvature = "
        f"{result.reference_barrier_curvature:.6e}"
    )
    print(
        "  near-cap barrier curvature = "
        f"{result.near_cap_barrier_curvature:.6e}"
    )
    print(f"  finite anchor compliance = {result.finite_anchor_compliance}")

    print("\nCone closure:")
    print(
        "  shared anchor exchange strength = "
        f"{result.shared_anchor_exchange_strength:.6f}"
    )
    print(f"  cone angle = {result.cone_angle_deg:.6f} deg")
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
