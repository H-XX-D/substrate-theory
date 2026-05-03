#!/usr/bin/env python3
"""Report the local detailed-balance branch-weight closure."""

from __future__ import annotations

from stiff_medium.cone_detailed_balance import assess_detailed_balance_closure


def main() -> None:
    result = assess_detailed_balance_closure()

    print("CONE DETAILED-BALANCE CLOSURE")
    print("\nSwap-symmetric exchange:")
    print(f"  commutator norm = {result.symmetric_commutator_norm:.6e}")
    print(f"  stationary branch weight = {result.symmetric_stationary_weight:.12f}")
    print(f"  linear bias = {result.symmetric_linear_bias:+.6e}")
    print(f"  minimum angle = {result.symmetric_minimum_angle_deg:.6f} deg")

    print("\nEnergy-splitting control:")
    print(f"  delta E / T = {result.split_energy_over_temp:.6f}")
    print(f"  stationary branch weight = {result.split_stationary_weight:.12f}")
    print(f"  linear bias = {result.split_linear_bias:+.6e}")
    print(f"  minimum angle = {result.split_minimum_angle_deg:.6f} deg")
    print(f"  angle shift = {result.split_angle_shift_deg:+.6f} deg")

    print("\nRate-imbalance control:")
    print(f"  rate imbalance = {result.rate_imbalance:+.6f}")
    print(f"  stationary branch weight = {result.imbalanced_stationary_weight:.12f}")
    print(f"  commutator norm = {result.imbalanced_commutator_norm:.6e}")
    print(f"  minimum angle = {result.imbalanced_minimum_angle_deg:.6f} deg")

    print("\nStatus:")
    print(
        "  detailed balance closes equal weight = "
        f"{result.detailed_balance_closes_equal_weight}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
