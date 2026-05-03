#!/usr/bin/env python3
"""Report the elastic-cell origin for the swap-degenerate cone generator."""

from __future__ import annotations

from stiff_medium.cone_swap_generator_origin import assess_swap_generator_origin


def main() -> None:
    result = assess_swap_generator_origin()

    print("CONE SWAP-GENERATOR ORIGIN")
    print("\nAutomorphic elastic cell:")
    print(f"  automorphism residual = {result.automorphic_residual:.6e}")
    print(f"  generator commutator norm = {result.automorphic_commutator_norm:.6e}")
    print(f"  stationary branch weight = {result.automorphic_stationary_weight:.12f}")
    print(f"  linear bias = {result.automorphic_linear_bias:+.6e}")
    print(f"  minimum angle = {result.automorphic_minimum_angle_deg:.6f} deg")

    print("\nBroken-cell control:")
    print(
        "  branch energy split / T = "
        f"{result.split_branch_energy_over_temp:.6f}"
    )
    print(f"  automorphism residual = {result.split_automorphism_residual:.6e}")
    print(f"  generator commutator norm = {result.split_commutator_norm:.6e}")
    print(f"  stationary branch weight = {result.split_stationary_weight:.12f}")
    print(f"  linear bias = {result.split_linear_bias:+.6e}")
    print(f"  minimum angle = {result.split_minimum_angle_deg:.6f} deg")
    print(f"  angle shift = {result.split_angle_shift_deg:+.6f} deg")

    print("\nStatus:")
    print(
        "  cell automorphism closes generator = "
        f"{result.cell_automorphism_closes_generator}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
