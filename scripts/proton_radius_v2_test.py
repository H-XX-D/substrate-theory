#!/usr/bin/env python3
"""Proton charge radius v2 test: bare Y-junction + string fluctuations.

Usage:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src python3 scripts/proton_radius_v2_test.py

This script extends scripts/proton_radius_test.py (§18.60.2) by adding the
**transverse string-fluctuation contribution** that the bare Y-junction +
sine-Gordon kink picture was missing.

For each (R₀, fluct-formula) combination we report:
    r_p² = R₀² + ⟨δr²⟩_string_fluct + ⟨r²⟩_intrinsic_kink

and compare to the empirical r_p^charge = 0.8409 fm. We also report the
literature pion-cloud value Δ⟨r²⟩_πcloud ≈ 0.075 fm² as a cross-check
(NOT added to the substrate prediction, since pions are chiral kinks
whose effect is already inside the string-fluctuation broadening).

Honest reporting:
    - σ = 0.180 GeV² and ξ = 0.2 fm are NOT fitted to r_p.
    - Two R₀ choices (dimensional 1/√σ vs rotating-Y) and two
      fluct-formula choices (midpoint vs endpoint) bracket the prediction.
    - We report whether each estimate closes the 33% gap.
"""

from __future__ import annotations

import sys

from stiff_medium.proton_radius import (
    HBARC_GEV_FM,
    M_PROTON_GEV,
    R_PROTON_CHARGE_EXP_FM,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
)
from stiff_medium.proton_radius_v2 import (
    R2_PION_CLOUD_LIT_FM2,
    compute_proton_radius_v2_summary,
    string_fluctuation_per_dim_endpoint,
    string_fluctuation_per_dim_midpoint,
)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def hr() -> None:
    print("=" * 78)


def section(title: str) -> None:
    print()
    hr()
    print(f"  {title}")
    hr()


def kv(key: str, value: str, width: int = 38) -> None:
    print(f"    {key:<{width}}{value}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    section("PROTON CHARGE RADIUS V2 — Y-JUNCTION + STRING FLUCTUATIONS")

    print()
    kv("Substrate inputs (none fitted to r_p):", "")
    kv("  σ_QCD =", f"{SIGMA_QCD_GEV2:.4f} GeV²  (from K(ξ) running)")
    kv("  ξ_QCD =", f"{XI_QCD_FM:.4f} fm   (kink coherence length)")
    kv("  ℏc =",    f"{HBARC_GEV_FM*1e3:.4f} MeV·fm")
    kv("  M_p (rotating-Y anchor) =", f"{M_PROTON_GEV:.6f} GeV")

    print()
    kv("Empirical target:", "")
    kv("  r_p^charge =", f"{R_PROTON_CHARGE_EXP_FM:.4f} fm")
    kv("  r_p²       =", f"{R_PROTON_CHARGE_EXP_FM**2:.4f} fm²")

    # ------------------------------------------------------------------
    # Step 1: per-dimension string-fluctuation magnitude
    # ------------------------------------------------------------------
    section("1) PER-DIMENSION STRING FLUCTUATION  ⟨X⊥²⟩")

    summary = compute_proton_radius_v2_summary(SIGMA_QCD_GEV2, XI_QCD_FM)

    # Walk through the dimensional R₀ case to expose the numbers.
    R0_dim = summary.estimates[0].R0_fm
    rms_mid = string_fluctuation_per_dim_midpoint(
        SIGMA_QCD_GEV2, R0_dim, XI_QCD_FM
    )
    rms_end = string_fluctuation_per_dim_endpoint(
        SIGMA_QCD_GEV2, R0_dim, XI_QCD_FM
    )

    print()
    kv("R₀ (dimensional 1/√σ) =", f"{R0_dim:.4f} fm")
    kv("ξ_QCD =",                  f"{XI_QCD_FM:.4f} fm")
    kv("ln(R₀/ξ) =",                f"{__import__('math').log(R0_dim/XI_QCD_FM):.4f}")
    print()
    print("  Midpoint (fixed-fixed) formula:")
    print("      ⟨X⊥²⟩_per_dim = (1/(2π σ)) × ln(R₀/ξ)")
    kv("                =", f"{rms_mid:.5f} fm²  (rms = {rms_mid**0.5:.4f} fm)")
    print()
    print("  Endpoint (free) formula:")
    print("      ⟨X⊥²⟩_per_dim = (1/(π σ)) × ln(R₀/ξ)   [factor 2 × midpoint]")
    kv("                =", f"{rms_end:.5f} fm²  (rms = {rms_end**0.5:.4f} fm)")

    # ------------------------------------------------------------------
    # Step 2: full predictions with decomposition
    # ------------------------------------------------------------------
    section("2) FULL PREDICTIONS WITH 4-COMPONENT DECOMPOSITION")

    print()
    print(f"    All values in fm² (substrate r_p² = position + string + kink)")
    print()
    header = (
        f"    {'Configuration':<34}"
        f"{'R₀²':>8}"
        f"{'string':>9}"
        f"{'kink':>8}"
        f"{'r_p²':>8}"
        f"{'r_p':>8}"
        f"{'err':>8}"
    )
    print(header)
    print(f"    {'-' * 34}{'-' * 8}{'-' * 9}{'-' * 8}{'-' * 8}{'-' * 8}{'-' * 8}")
    for est in summary.estimates:
        err_pct = 100.0 * est.frac_error
        print(
            f"    {est.label:<34}"
            f"{est.r2_position:>8.4f}"
            f"{est.r2_string:>9.4f}"
            f"{est.r2_kink:>8.4f}"
            f"{est.r2_total:>8.4f}"
            f"{est.r_p_fm:>8.4f}"
            f"{err_pct:>+7.1f}%"
        )

    print()
    print(f"    Empirical r_p² = {R_PROTON_CHARGE_EXP_FM**2:.4f} fm²,  "
          f"r_p = {R_PROTON_CHARGE_EXP_FM:.4f} fm")

    # ------------------------------------------------------------------
    # Step 3: cross-check with literature pion-cloud value
    # ------------------------------------------------------------------
    section("3) CROSS-CHECK WITH LITERATURE PION-CLOUD VALUE")

    print()
    print("  Conventional QCD: pion cloud contributes Δ⟨r²⟩ ≈ 0.05-0.10 fm²")
    print("  (Hammer & Meißner, PPNP 2020).  In the substrate model, pions")
    print("  are chiral kinks; their effect on r_p is already inside the")
    print("  string-fluctuation broadening above (no double-counting).")
    print()
    print("  We add the literature value here as a CROSS-CHECK only:")
    print()
    print(f"    Δ⟨r²⟩_πcloud (lit) = {R2_PION_CLOUD_LIT_FM2:.4f} fm²")
    print()
    print(f"    {'Configuration':<34}"
          f"{'r_p²(sub)':>10}"
          f"{'+πlit':>8}"
          f"{'r_p':>8}"
          f"{'err':>8}")
    print(f"    {'-' * 34}{'-' * 10}{'-' * 8}{'-' * 8}{'-' * 8}")
    for est in summary.estimates:
        err_with_pion = (est.r_p_with_pion - R_PROTON_CHARGE_EXP_FM) \
                        / R_PROTON_CHARGE_EXP_FM * 100.0
        print(
            f"    {est.label:<34}"
            f"{est.r2_total:>10.4f}"
            f"{est.r2_pion_lit:>8.4f}"
            f"{est.r_p_with_pion:>8.4f}"
            f"{err_with_pion:>+7.1f}%"
        )

    # ------------------------------------------------------------------
    # Step 4: gap analysis
    # ------------------------------------------------------------------
    section("4) GAP ANALYSIS — DOES STRING FLUCTUATION CLOSE THE 33% GAP?")

    target_r2 = R_PROTON_CHARGE_EXP_FM ** 2
    print()
    print(f"  Empirical r_p² = {target_r2:.4f} fm²")
    print()
    print(f"    {'Configuration':<34}"
          f"{'r_p²(sub)':>10}"
          f"{'gap(fm²)':>10}"
          f"{'closed?':>10}")
    print(f"    {'-' * 34}{'-' * 10}{'-' * 10}{'-' * 10}")

    closed_count = 0
    for est in summary.estimates:
        gap = target_r2 - est.r2_total
        closed = abs(est.frac_error) < 0.05  # within 5% considered closed
        if closed:
            closed_count += 1
        marker = "YES (<5%)" if closed else f"NO ({est.frac_error*100:+.0f}%)"
        print(
            f"    {est.label:<34}"
            f"{est.r2_total:>10.4f}"
            f"{gap:>10.4f}"
            f"{marker:>10}"
        )

    print()
    print(f"    {closed_count} of {len(summary.estimates)} estimates close the gap.")

    # ------------------------------------------------------------------
    # Step 5: honest assessment
    # ------------------------------------------------------------------
    section("5) HONEST ASSESSMENT")

    canonical = summary.estimates[0]   # dimensional R₀ + midpoint fluct
    best = min(summary.estimates, key=lambda e: abs(e.frac_error))
    err_canon_pct = 100.0 * canonical.frac_error
    err_best_pct = 100.0 * best.frac_error

    print()
    print("  Decomposition of the canonical (most conservative) estimate:")
    print(f"    • R₀ (dimensional 1/√σ)   = {canonical.R0_fm:.4f} fm")
    print(f"    • r_p²_position    = R₀²                   = "
          f"{canonical.r2_position:.4f} fm²")
    print(f"    • r_p²_string-fluct (midpoint, 2D × log)  = "
          f"{canonical.r2_string:.4f} fm²")
    print(f"    • r_p²_intrinsic-kink (3D sech²)          = "
          f"{canonical.r2_kink:.4f} fm²")
    print(f"    • r_p²_total (substrate)                  = "
          f"{canonical.r2_total:.4f} fm²")
    print(f"    • r_p (substrate) = {canonical.r_p_fm:.4f} fm   "
          f"({err_canon_pct:+.1f}%)")
    print()
    print("  Decomposition of the BEST estimate (smallest error):")
    print(f"    • {best.label}")
    print(f"    • R₀                 = {best.R0_fm:.4f} fm")
    print(f"    • r_p²_position      = {best.r2_position:.4f} fm²")
    print(f"    • r_p²_string-fluct  = {best.r2_string:.4f} fm²")
    print(f"    • r_p²_intrinsic     = {best.r2_kink:.4f} fm²")
    print(f"    • r_p²_total         = {best.r2_total:.4f} fm²")
    print(f"    • r_p = {best.r_p_fm:.4f} fm  ({err_best_pct:+.1f}%)")
    print()

    # Bracket
    rps = [e.r_p_fm for e in summary.estimates]
    rp_min, rp_max = min(rps), max(rps)
    contains_target = rp_min <= R_PROTON_CHARGE_EXP_FM <= rp_max
    print(f"  Bracket of v2 predictions: r_p ∈ "
          f"[{rp_min:.4f}, {rp_max:.4f}] fm")
    print(f"  Empirical 0.8409 fm is "
          f"{'INSIDE' if contains_target else 'OUTSIDE'} this bracket.")
    print()

    # Verdict
    print("  Verdict on string-fluctuation contribution:")
    if any(abs(e.frac_error) < 0.05 for e in summary.estimates):
        print("    • At least one configuration closes the gap to <5%.")
        print("    • String fluctuations are the missing physics.")
    else:
        print("    • String fluctuations REDUCE the gap but do NOT close it.")
        gap_v1_pct = -33.3   # from §18.60.2 dimensional+3D estimate
        gap_v2_pct = err_canon_pct
        improvement = gap_v1_pct - gap_v2_pct
        print(f"    • Canonical v1 gap was −33.3%; v2 gap is "
              f"{gap_v2_pct:+.1f}%.")
        print(f"    • Improvement: {improvement:+.1f} percentage points.")
        print()
        print("    Residual physics still missing:")
        print("      (a) Endpoint amplification — the free-endpoint formula")
        print("          is a factor-2 enhancement that bridges much of the")
        print("          remaining gap (see endpoint-fluct rows above).")
        print("      (b) Sea-quark / gluon condensate smearing not captured")
        print("          by classical string + kink width.")
        print("      (c) Higher-order radial profile of the soliton — the")
        print("          sine-Gordon sech² is a 1D approximation; the full")
        print("          3D quark wavefunction in the linear potential")
        print("          carries an additional broadening of order ⟨r²⟩ ~")
        print("          1/σ that we have NOT added (would double-count R₀²).")

    print()
    print("  Bottom line:")
    print(f"    • v1 (no fluctuations):  r_p ≈ 0.50-0.56 fm  (−33% to −41%)")
    print(f"    • v2 (with fluctuations): r_p ∈ "
          f"[{rp_min:.3f}, {rp_max:.3f}] fm  "
          f"({err_canon_pct:+.1f}% to {100.0*best.frac_error:+.1f}%)")
    print(f"    • Gap reduction: {(-0.333 - canonical.frac_error)*100:+.1f}% "
          f"to {(-0.333 - best.frac_error)*100:+.1f}% percentage points.")
    print()
    print("  Inputs used (none fitted to r_p):")
    print("    • σ_QCD = 0.180 GeV²  (K(ξ) running)")
    print("    • ξ_QCD = 0.2 fm      (substrate coherence)")
    print("    • R₀ = 1/√σ           (dimensional, parameter-free)")
    print("       OR  R₀ = 2 M_p/(3πσ)  (rotating-Y, uses M_p)")
    print("    • Lüscher transverse-fluctuation formula for Nambu-Goto string")
    print()
    hr()
    return 0


if __name__ == "__main__":
    sys.exit(main())
