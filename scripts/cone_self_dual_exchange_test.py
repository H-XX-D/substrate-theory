#!/usr/bin/env python3
"""Report the paired-branch self-dual cone mechanism."""

from __future__ import annotations

from stiff_medium.cone_self_dual_exchange import (
    assess_self_dual_exchange_mechanism,
)


def main() -> None:
    result = assess_self_dual_exchange_mechanism()

    print("CONE SELF-DUAL EXCHANGE MECHANISM")
    print("\nBalanced dual branch:")
    print(f"  linear bias = {result.balanced_linear_bias:+.6e}")
    print(f"  beta = {result.balanced_beta:.6e}")
    print(f"  minimum angle = {result.balanced_minimum_angle_deg:.6f} deg")
    print(f"  energy at minimum = {result.balanced_energy_at_minimum:.6e}")

    print("\nImbalanced branch check:")
    print(f"  imbalanced weight = {result.imbalanced_weight:.6f}")
    print(f"  linear bias = {result.imbalanced_linear_bias:+.6e}")
    print(f"  minimum angle = {result.imbalanced_minimum_angle_deg:.6f} deg")
    print(f"  shift from cone = {result.imbalanced_shift_deg:+.6f} deg")

    print("\nFailure controls:")
    print(
        "  single-branch minimum angle = "
        f"{result.single_branch_minimum_angle_deg:.6f} deg"
    )
    print(
        "  beta positive from branch stability = "
        f"{result.beta_positive_from_branch_stability}"
    )
    print(
        "  dual pair cancels quadratic bias = "
        f"{result.dual_pair_cancels_quadratic_bias}"
    )
    print(f"  conditional cone closure = {result.conditional_cone_closure}")
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
