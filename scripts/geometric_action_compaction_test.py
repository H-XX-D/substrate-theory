#!/usr/bin/env python3
"""Report the candidate compact geometric action."""

from __future__ import annotations

from stiff_medium.geometric_action_compaction import (
    assess_geometric_compaction,
    compact_geometric_action,
)


def main() -> None:
    action = compact_geometric_action()
    assessment = assess_geometric_compaction()

    print("GEOMETRIC ACTION COMPACTION")
    print("\nCandidate Lagrangian:")
    print(f"  {action.lagrangian}")
    print(f"  {action.potential}")
    print(f"  {action.covariant_derivative}")
    print(f"  {action.cone_geometry}")
    print(f"  {action.dark_sector}")
    print(f"  status: {action.status}")

    print("\nStructural checks:")
    print(f"  cone residual, 45 degree gradient = {assessment.cone_residual_45deg:+.3e}")
    print(f"  cone residual, parallel gradient = {assessment.cone_residual_parallel:+.3e}")
    print(
        "  cone residual, perpendicular gradient = "
        f"{assessment.cone_residual_perpendicular:+.3e}"
    )
    print(
        "  Mobius phase after 2pi = "
        f"{assessment.mobius_phase_2pi_real:+.3f}"
        f"{assessment.mobius_phase_2pi_imag:+.3e}i"
    )
    print(
        "  Mobius phase after 4pi = "
        f"{assessment.mobius_phase_4pi_real:+.3f}"
        f"{assessment.mobius_phase_4pi_imag:+.3e}i"
    )
    print(f"  stress projector rank = {assessment.stress_projector_rank}")
    print(
        "  cone variational minimum = "
        f"{assessment.cone_variational_minimum_deg:.6f} deg"
    )
    print(
        "  cone variational curvature = "
        f"{assessment.cone_variational_curvature:.6e}"
    )
    print(
        "  cone lattice self-dual exchange required = "
        f"{assessment.cone_lattice_self_dual_required}"
    )
    print(
        "  cone lattice bias shift = "
        f"{assessment.cone_lattice_bias_shift_deg:+.6f} deg"
    )
    print(
        "  cone lattice beta positive required = "
        f"{assessment.cone_lattice_beta_positive_required}"
    )
    print(
        "  cone forced by current lattice symmetry = "
        f"{assessment.cone_forced_by_current_lattice_symmetry}"
    )
    print(
        "  cone self-dual conditional closure = "
        f"{assessment.cone_self_dual_conditional_closure}"
    )
    print(
        "  cone self-dual imbalance shift = "
        f"{assessment.cone_self_dual_imbalanced_shift_deg:+.6f} deg"
    )
    print(
        "  cone self-dual fully derived = "
        f"{assessment.cone_self_dual_fully_derived}"
    )
    print(
        "  cone detailed balance equal weight = "
        f"{assessment.cone_detailed_balance_equal_weight}"
    )
    print(
        "  cone detailed balance split shift = "
        f"{assessment.cone_detailed_balance_split_shift_deg:+.6f} deg"
    )
    print(
        "  cone detailed balance rate shift = "
        f"{assessment.cone_detailed_balance_rate_shift_deg:+.6f} deg"
    )
    print(
        "  cone detailed balance fully derived = "
        f"{assessment.cone_detailed_balance_fully_derived}"
    )
    print(
        "  cone cell automorphism closes generator = "
        f"{assessment.cone_cell_automorphism_closes_generator}"
    )
    print(
        "  cone cell split shift = "
        f"{assessment.cone_cell_split_shift_deg:+.6f} deg"
    )
    print(
        "  cone cell fully derived = "
        f"{assessment.cone_cell_fully_derived}"
    )
    print(
        "  cone diamond cell forces automorphism = "
        f"{assessment.cone_diamond_cell_forces_automorphism}"
    )
    print(
        "  cone diamond anchor-split shift = "
        f"{assessment.cone_diamond_anchor_split_shift_deg:+.6f} deg"
    )
    print(
        "  cone diamond fully derived = "
        f"{assessment.cone_diamond_fully_derived}"
    )
    print(
        "  cone diamond unique under selection = "
        f"{assessment.cone_diamond_unique_under_selection}"
    )
    print(
        "  cone diamond selection min edges = "
        f"{assessment.cone_diamond_selection_min_edges}"
    )
    print(
        "  cone diamond selection fully derived = "
        f"{assessment.cone_diamond_selection_fully_derived}"
    )
    print(
        "  cone anchor-induced exchange = "
        f"{assessment.cone_anchor_induced_exchange}"
    )
    print(
        "  cone anchor exchange strength = "
        f"{assessment.cone_anchor_exchange_strength:.6f}"
    )
    print(
        "  cone anchor fully derived = "
        f"{assessment.cone_anchor_fully_derived}"
    )
    print(
        "  cone two-anchor topology selected = "
        f"{assessment.cone_two_anchor_topology_selected}"
    )
    print(
        "  cone anchor compliance finite = "
        f"{assessment.cone_anchor_compliance_finite}"
    )
    print(
        "  cone two-anchor fully derived = "
        f"{assessment.cone_two_anchor_fully_derived}"
    )
    print(
        "  cone phase-slip lattice segment selected = "
        f"{assessment.cone_phase_slip_lattice_segment_selected}"
    )
    print(
        "  cone phase-slip stiffness ratio fixed = "
        f"{assessment.cone_phase_slip_stiffness_ratio_fixed}"
    )
    print(
        "  cone phase-slip ratio-scan angle error = "
        f"{assessment.cone_phase_slip_ratio_scan_angle_error_deg:.6e} deg"
    )
    print(
        "  cone saturation barrier selects single bond = "
        f"{assessment.cone_saturation_barrier_selects_single_bond}"
    )
    print(
        "  cone saturated-bond core cost fixed = "
        f"{assessment.cone_saturated_bond_core_cost_fixed}"
    )
    print(f"  K_eff/K = {assessment.stiffness_ratio:.12e}")
    print(f"  dark speed = {assessment.dark_speed_km_s:.6f} km/s")
    print(f"  scale speed = {assessment.scale_speed_km_s:.6f} km/s")
    print(f"  speed error = {assessment.speed_error_pct:+.3e}%")
    print(f"  lambda multiplier replaced = {assessment.lambda_multiplier_replaced}")

    print("\nVerdict:")
    print(assessment.verdict)


if __name__ == "__main__":
    main()
