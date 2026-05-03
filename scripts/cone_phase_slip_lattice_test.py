#!/usr/bin/env python3
"""Report the discrete phase-slip lattice origin for cone anchors."""

from __future__ import annotations

from stiff_medium.cone_phase_slip_lattice import assess_phase_slip_lattice_origin


def main() -> None:
    result = assess_phase_slip_lattice_origin()

    print("CONE PHASE-SLIP LATTICE ORIGIN")
    print("\nDiscrete chain topology:")
    print(f"  segment edge count = {result.segment_edge_count}")
    print(f"  segment endpoint count = {result.segment_endpoint_count}")
    print(f"  segment net charge = {result.segment_net_charge:+.6f}")
    print(f"  loop edge count = {result.loop_edge_count}")
    print(f"  loop endpoint count = {result.loop_endpoint_count}")
    print(f"  single-anchor is boundary control = {result.single_anchor_is_boundary}")
    print(
        "  topology selects open segment = "
        f"{result.topology_selects_open_segment}"
    )

    print("\nFinite symmetric anchor ratios:")
    for ratio, exchange, angle in result.ratio_scan:
        print(
            "  "
            f"k_sat/k_a = {ratio:.6e}, "
            f"g_eff = {exchange:.6e}, "
            f"angle = {angle:.6f} deg"
        )
    print(f"  min induced exchange = {result.min_induced_exchange:.6e}")
    print(f"  max induced exchange = {result.max_induced_exchange:.6e}")
    print(f"  max angle error = {result.max_angle_error_deg:.6e} deg")

    print("\nStatus:")
    print(
        "  stiffness ratio fixed by topology = "
        f"{result.stiffness_ratio_fixed_by_topology}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
