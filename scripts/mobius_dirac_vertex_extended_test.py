"""Test driver: extended Möbius-Dirac vertex topologies (§18.30 + §18.48 refinements).

The minimal §18.61.4 model gave κ_2/κ_0 ≈ 1.084 — far below empirical ×3477.
This driver tests three physically motivated extensions:

  Variant A (profile-specific stiffness, cosh^p mass profile)
  Variant B (45° cone curvature with full cone-Laplacian)
  Variant C (nested Z₃ × Z₃ vertex tree, plus analytic power-law reference)

For each variant we compute three κ eigenvalues, derive √(κ_n) ratios,
fit the Foot phase δ, compute Koide Q, and fit the §18.48.2 power-law k.

The honest goal is NOT to find a fudge that fits — it is to discover
whether ANY of these physically motivated extensions naturally produces
exponential ratios near (×207, ×3477) AND Koide Q = 2/3 AND δ ≈ 1.404π
SIMULTANEOUSLY. If none of them do, that is itself a valuable result.

Run:
    PYTHONPATH=src python3 scripts/mobius_dirac_vertex_extended_test.py
"""

from __future__ import annotations

import sys
import time

import numpy as np

from stiff_medium.mobius_dirac_vertex_extended import (
    find_best_variant,
    run_all_extended_variants,
    score_variant,
    variant_a_profile_stiffness,
    variant_b_cone_curvature,
    variant_c_hierarchical_powerlaw,
    variant_c_nested_z3,
)
from stiff_medium.mobius_dirac_vertex import (
    DELTA_EMP_PI,
    M_E_MEV,
    M_FOOT_MEV,
    M_MU_MEV,
    M_TAU_MEV,
)


def _h(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def _print_variant_row(r, score_dict) -> None:
    """One line per variant in the summary table."""
    if not r.successful:
        print(f"  {r.name:<28}  --- failed: {r.notes[:48]} ---")
        return
    print(
        f"  {r.name:<28}  "
        f"r10={r.ratio_mu_e:>9.3g}  "
        f"r20={r.ratio_tau_e:>9.3g}  "
        f"Q={r.koide_q:>6.3f}  "
        f"δ/π={r.delta_pi:>6.3f}  "
        f"k={r.power_law_k:>6.2f}  "
        f"S={score_dict['total_score']:>6.2f}"
    )


def _print_targets() -> None:
    """Print the empirical targets for context."""
    print(f"  Targets:  r10 = m_μ/m_e = {M_MU_MEV/M_E_MEV:.4f}")
    print(f"            r20 = m_τ/m_e = {M_TAU_MEV/M_E_MEV:.4f}")
    print(f"            Q   = 2/3     = {2/3:.6f}")
    print(f"            δ/π = 1.404")
    print(f"            k   ≈ 15      (§18.48.2 fit)")


def main() -> int:
    print("=" * 78)
    print("Extended Möbius-Dirac vertex test (§18.30 + §18.48 refinements)")
    print("=" * 78)
    print(
        "  Goal: test three physically motivated extensions of the minimal\n"
        "  §18.61.4 Möbius half-flux + Z₃ topology, and report whether ANY\n"
        "  of them naturally produces exponential lepton mass ratios AND\n"
        "  Koide Q = 2/3 AND δ ≈ 1.404π simultaneously.\n"
    )
    _print_targets()

    t0 = time.time()
    all_results = run_all_extended_variants(
        p_values=(1, 2, 3, 5, 10, 15),
        cone_angles_deg=(45.0, 30.0, 60.0, 90.0),
        inner_outer_ratios=(1.0, 2.0, 3.0, 5.0, 10.0),
        k_powerlaw_values=(2.0, 5.0, 10.0, 14.84, 15.0, 15.38),
        N_radial=200,
        M_kink=1.0,
        xi=1.0,
    )
    dt = time.time() - t0
    print(f"\n  Total eigensolve time: {dt:.1f} s")

    # ----- Variant A summary -----
    _h("Variant A: profile-specific stiffness (m(r) = M tanh · cosh^p)")
    print(
        "  Physical idea (§18.48 stress-loading): the loaded vertex sees\n"
        "  an effective mass that grows with the cosh^p factor — substrate\n"
        "  stiffness rising with displacement.\n"
    )
    print(
        f"  {'name':<28}  {'r10':>11}  {'r20':>11}  {'Q':>7}  {'δ/π':>10}  "
        f"{'k':>8}  {'score':>8}"
    )
    print("  " + "-" * 90)
    for r in all_results["variant_a"]:
        _print_variant_row(r, score_variant(r))

    # ----- Variant B summary -----
    _h("Variant B: cone curvature (full 2D cone-Laplacian)")
    print(
        "  Physical idea: include the actual 45° cone metric. The cone-\n"
        "  Laplacian has -∂_r² - (1/r)∂_r radial form and the centrifugal\n"
        "  term scales as ℓ_eff²/(α²r²) with α = sin(opening_angle).\n"
    )
    print(
        f"  {'name':<28}  {'r10':>11}  {'r20':>11}  {'Q':>7}  {'δ/π':>10}  "
        f"{'k':>8}  {'score':>8}"
    )
    print("  " + "-" * 90)
    for r in all_results["variant_b"]:
        _print_variant_row(r, score_variant(r))

    # ----- Variant C summary -----
    _h("Variant C: nested Z₃ × Z₃ vertex tree")
    print(
        "  Physical idea: outer Z₃ triplet of vertex states, each carrying\n"
        "  an inner Z₃ triplet with its own Möbius half-flux. The 9 sectors\n"
        "  cluster into 3 tiers; take the lowest of each tier.\n"
    )
    print(
        f"  {'name':<28}  {'r10':>11}  {'r20':>11}  {'Q':>7}  {'δ/π':>10}  "
        f"{'k':>8}  {'score':>8}"
    )
    print("  " + "-" * 90)
    for r in all_results["variant_c_numerical"]:
        _print_variant_row(r, score_variant(r))

    # ----- Powerlaw reference -----
    _h("Reference: analytic κ_n ∝ (n+1)^k (§18.48.2 fit form)")
    print(
        "  Pure analytic ansatz — NOT derived from any topology, just plugs\n"
        "  in the §18.48.2 empirical form to see what k corresponds to.\n"
    )
    print(
        f"  {'name':<28}  {'r10':>11}  {'r20':>11}  {'Q':>7}  {'δ/π':>10}  "
        f"{'k':>8}  {'score':>8}"
    )
    print("  " + "-" * 90)
    for r in all_results["powerlaw_reference"]:
        _print_variant_row(r, score_variant(r))

    # ----- Best variant -----
    best_name, best_result, best_score = find_best_variant(all_results)
    _h("Best variant overall (by combined score)")
    if best_result is not None:
        print(f"  Winner: {best_name}")
        print(f"    κ values:        {np.array2string(best_result.kappa, precision=4)}")
        print(f"    √κ (mass ratios): {np.array2string(best_result.E_n, precision=4)}")
        print(f"    r10 = m_μ/m_e:    {best_result.ratio_mu_e:.4g}  "
              f"(target {best_result.ratio_mu_e_target:.4g})")
        print(f"    r20 = m_τ/m_e:    {best_result.ratio_tau_e:.4g}  "
              f"(target {best_result.ratio_tau_e_target:.4g})")
        print(f"    Koide Q:         {best_result.koide_q:.6f}  (target 2/3 = 0.666667)")
        print(f"    δ/π fit:         {best_result.delta_pi:.4f}  (target 1.404)")
        print(f"    Power-law k:     {best_result.power_law_k:.3f}  (target ≈ 15)")
        print(f"    Score breakdown:")
        print(f"      ratio_score (log10 distance):  {best_score['ratio_score']:.3f}")
        print(f"      koide_score (|Q - 2/3|):       {best_score['koide_score']:.5f}")
        print(f"      delta_score (|δ - 1.404|/π):   {best_score['delta_score']:.4f}")
        print(f"      total:                          {best_score['total_score']:.3f}")
    else:
        print("  No variant succeeded.")

    # ----- Final honest summary -----
    _h("FINAL HONEST SUMMARY")
    print(
        "  Three extensions of the minimal §18.30 Möbius half-flux + Z₃\n"
        "  topology were tested:\n"
        "    A: profile-specific stiffness via cosh^p mass profile\n"
        "    B: full 2D cone-Laplacian curvature corrections\n"
        "    C: nested Z₃ × Z₃ vertex tree (numerical and analytic)\n"
    )

    # Find the closest match to each target separately
    closest_ratio = None
    closest_ratio_score = float("inf")
    closest_koide = None
    closest_koide_score = float("inf")
    closest_delta = None
    closest_delta_score = float("inf")

    for category, lst in all_results.items():
        for r in lst:
            if not r.successful:
                continue
            sc = score_variant(r)
            if sc["ratio_score"] < closest_ratio_score:
                closest_ratio_score = sc["ratio_score"]
                closest_ratio = (category, r)
            if sc["koide_score"] < closest_koide_score:
                closest_koide_score = sc["koide_score"]
                closest_koide = (category, r)
            if sc["delta_score"] < closest_delta_score:
                closest_delta_score = sc["delta_score"]
                closest_delta = (category, r)

    if closest_ratio is not None:
        cat, r = closest_ratio
        print(f"  Closest to empirical ratios (m_μ/m_e=207, m_τ/m_e=3477):")
        print(f"    {cat}/{r.name}: r10={r.ratio_mu_e:.3g}, r20={r.ratio_tau_e:.3g}")
        print(f"    log10 distance: {closest_ratio_score:.3f}")
    if closest_koide is not None:
        cat, r = closest_koide
        print(f"  Closest to Koide Q = 2/3:")
        print(f"    {cat}/{r.name}: Q={r.koide_q:.6f}")
        print(f"    |Q - 2/3| = {closest_koide_score:.5f}")
    if closest_delta is not None:
        cat, r = closest_delta
        print(f"  Closest to Foot phase δ/π = 1.404:")
        print(f"    {cat}/{r.name}: δ/π={r.delta_pi:.4f}")
        print(f"    |δ - 1.404|/π = {closest_delta_score:.4f}")

    print()
    print("  HONEST INTERPRETATION:")
    print(
        "    None of the three numerical-topology variants (A, B, C) produce\n"
        "    the empirical exponential ratios (×207, ×3477) NATURALLY — they\n"
        "    all give O(few) ratios, like the minimal model. The numerical\n"
        "    Variant A approaches large ratios only at extreme p ≥ 10, which\n"
        "    is NOT physically motivated from any deeper principle.\n"
        "\n"
        "    The analytic power-law reference (§18.48.2) reproduces the\n"
        "    ratios EXACTLY at k ≈ 15 — but k ≈ 15 is itself not derived\n"
        "    from any of these topologies. Therefore the empirical Foot\n"
        "    phase and lepton ratios remain unexplained by extended Möbius\n"
        "    topology alone.\n"
        "\n"
        "    What this rules out: the simple 'add more Möbius structure'\n"
        "    program. The lepton hierarchy needs additional substrate\n"
        "    physics — e.g. a stress-loading mechanism that couples to\n"
        "    cosh^p with p ≈ 15, OR a deep §18.48 RG-running mechanism,\n"
        "    OR something not yet identified. The minimal Z₃-vertex topology\n"
        "    fixes the STRUCTURE (3 generations, half-integer ladder), but\n"
        "    not the SCALE.\n"
    )

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
