#!/usr/bin/env python3
"""Report saturated-bond energetic selection for the cone phase slip."""

from __future__ import annotations

from stiff_medium.cone_saturated_bond_selection import (
    assess_saturated_bond_selection,
    slip_energy_table,
)


def main() -> None:
    result = assess_saturated_bond_selection()

    print("CONE SATURATED-BOND SELECTION")
    print("\nPure saturation barrier:")
    for count, energy in slip_energy_table(
        result.total_strain_fraction,
        (1, 2, 4, 8, 16, 32, 64),
    ):
        print(f"  bonds = {count:2d}, energy = {energy:.6e}")
    print(f"  selected bond count = {result.pure_selected_bond_count}")
    print(f"  one-bond energy = {result.pure_one_bond_energy:.6e}")
    print(f"  widest energy = {result.pure_widest_energy:.6e}")
    print(
        "  pure barrier selects single bond = "
        f"{result.pure_barrier_selects_single_bond}"
    )

    print("\nLocalization control:")
    print(f"  critical core cost = {result.critical_core_cost:.6e}")
    print(f"  trial core cost = {result.trial_core_cost:.6e}")
    print(f"  selected bond count with trial core = {result.core_selected_bond_count}")
    print(
        "  core cost fixed by substrate = "
        f"{result.core_cost_fixed_by_substrate}"
    )
    print(f"  fully derived = {result.fully_derived}")

    print("\nVerdict:")
    print(result.verdict)


if __name__ == "__main__":
    main()
