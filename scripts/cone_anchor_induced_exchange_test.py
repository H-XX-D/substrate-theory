#!/usr/bin/env python3
"""Report anchor-mediated branch exchange for the cone diamond cell."""

from __future__ import annotations

from stiff_medium.cone_anchor_induced_exchange import assess_anchor_induced_exchange


def main() -> None:
    result = assess_anchor_induced_exchange()

    print("CONE ANCHOR-INDUCED EXCHANGE")
    print("\nShared finite anchors:")
    print(f"  branch-anchor stiffness = {result.branch_anchor_stiffness:.6f}")
    print(f"  anchor pin stiffness = {result.anchor_pin_stiffness:.6f}")
    print(f"  induced exchange = {result.induced_exchange:.6f}")
    print(f"  analytic exchange = {result.analytic_exchange:.6f}")
    print(f"  fixed-anchor exchange = {result.fixed_anchor_exchange:.6f}")
    print(f"  branch automorphism residual = {result.branch_automorphism_residual:.6e}")
    print(f"  stationary branch weight = {result.stationary_weight:.12f}")
    print(f"  linear bias = {result.linear_bias:+.6e}")
    print(f"  minimum angle = {result.minimum_angle_deg:.6f} deg")
    print(f"  generator commutator norm = {result.generator_commutator_norm:.6e}")

    print("\nLimits:")
    print(f"  soft-anchor exchange = {result.soft_anchor_limit_exchange:.6f}")
    print(f"  rigid-anchor exchange = {result.rigid_anchor_limit_exchange:.6e}")

    print("\nStatus:")
    print(
        "  exchange induced by finite anchors = "
        f"{result.exchange_induced_by_finite_anchors}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
