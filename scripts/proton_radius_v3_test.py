#!/usr/bin/env python3
"""Proton charge radius v3 test: 3-body wavefunction + string fluctuations + kink.

Usage:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src python3 scripts/proton_radius_v3_test.py

This script extends scripts/proton_radius_v2_test.py (§18.61.3) by replacing
the single-string equilibrium length R₀ = 1/√σ with the actual 3-body
wavefunction spread ⟨r²⟩_3body computed by:

    (1) Variational Gaussian ψ(r) ∝ exp(-α r²/2) in V(r) = σ r;
        analytic minimisation gives α_min and ⟨r²⟩ = 3/(2α_min).

    (2) Numerical sparse-matrix radial Schrödinger for the s-wave
        eigenstate: -ℏ²/(2μ) u'' + σ r u = E u.  Cross-check.

The remaining gap from v2 (~22%) should close if the 3-body spread is
larger than R₀² = 1/σ — which it is, since the wavefunction has tails
beyond the equilibrium turning point.

Inputs (NONE fitted to r_p):
    σ_QCD = 0.180 GeV²    (K(ξ) running)
    ξ_QCD = 0.2 fm        (substrate coherence)
    m_eff = √σ ≈ 0.424 GeV (chromomagnetic substrate)

Empirical target:
    r_p^charge = 0.8409 fm  (CODATA / muonic hydrogen)
"""

from __future__ import annotations

import sys

from stiff_medium.proton_radius import (
    HBARC_GEV_FM,
    R_PROTON_CHARGE_EXP_FM,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
    intrinsic_r2_kink_3D,
)
from stiff_medium.proton_radius_v3 import (
    compute_proton_radius_v3_summary,
    m_eff_from_sigma,
    proton_radius_full_v3,
    solve_radial_schrodinger_numerical,
    solve_variational_quark_wavefunction,
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
    section("PROTON CHARGE RADIUS V3 — 3-BODY WAVEFUNCTION + STRING + KINK")

    m_eff = m_eff_from_sigma(SIGMA_QCD_GEV2)

    print()
    kv("Substrate inputs (none fitted to r_p):", "")
    kv("  σ_QCD =",   f"{SIGMA_QCD_GEV2:.4f} GeV²")
    kv("  ξ_QCD =",   f"{XI_QCD_FM:.4f} fm")
    kv("  m_eff = √σ =", f"{m_eff:.4f} GeV  ≈ {m_eff*1e3:.1f} MeV")
    kv("  ℏc =",       f"{HBARC_GEV_FM*1e3:.4f} MeV·fm")
    print()
    kv("Empirical target:", "")
    kv("  r_p^charge =", f"{R_PROTON_CHARGE_EXP_FM:.4f} fm")
    kv("  r_p²       =", f"{R_PROTON_CHARGE_EXP_FM**2:.4f} fm²")

    # ------------------------------------------------------------------
    # Step 1: variational Gaussian
    # ------------------------------------------------------------------
    section("1) VARIATIONAL GAUSSIAN  ψ(r) ∝ exp(-α r²/2)")

    var = solve_variational_quark_wavefunction(SIGMA_QCD_GEV2, m_eff)

    print()
    print("  Energy expectation (3D Gaussian, ℏ = 1):")
    print("      E(α) = (3 α)/(4 μ) + 2 σ / √(π α)")
    print("  Stationarity:  α_min = [(4 μ σ)/(3 √π)]^(2/3)")
    print()
    kv("  α_min =", f"{var.alpha_min_GeV2:.6f} GeV²")
    kv("  E_min =", f"{var.E_min_GeV:.4f} GeV   ≈ {var.E_min_GeV*1e3:.0f} MeV")
    kv("  ⟨r²⟩  =", f"{var.r2_GeV_inv2:.4f} GeV⁻²")
    kv("  ⟨r²⟩  =", f"{var.r2_fm2:.4f} fm²")
    kv("  √⟨r²⟩ =", f"{var.r_rms_fm:.4f} fm")

    # Compare with single-string R₀ = 1/√σ
    R0_single = HBARC_GEV_FM / SIGMA_QCD_GEV2 ** 0.5
    print()
    print("  Compare to single-string equilibrium:")
    kv("    R₀ (1/√σ)         =", f"{R0_single:.4f} fm")
    kv("    R₀² (single)      =", f"{R0_single**2:.4f} fm²")
    kv("    ⟨r²⟩_3body / R₀² =", f"{var.r2_fm2 / R0_single**2:.3f}")

    # ------------------------------------------------------------------
    # Step 2: numerical cross-check
    # ------------------------------------------------------------------
    section("2) NUMERICAL CROSS-CHECK — SPARSE RADIAL SCHRÖDINGER")

    num = solve_radial_schrodinger_numerical(
        SIGMA_QCD_GEV2, m_eff, N_r=200, R_max_GeV_inv=30.0
    )

    print()
    kv("  Grid:", f"N_r = {num.N_r}, R_max = {num.R_max_GeV_inv:.1f} GeV⁻¹  "
                  f"(≈ {num.R_max_GeV_inv * HBARC_GEV_FM:.2f} fm)")
    kv("  E_0 =", f"{num.E_GeV:.4f} GeV   ≈ {num.E_GeV*1e3:.0f} MeV")
    kv("  ⟨r²⟩  =", f"{num.r2_GeV_inv2:.4f} GeV⁻²")
    kv("  ⟨r²⟩  =", f"{num.r2_fm2:.4f} fm²")
    kv("  √⟨r²⟩ =", f"{num.r_rms_fm:.4f} fm")
    print()
    diff_r2 = (num.r2_fm2 - var.r2_fm2) / var.r2_fm2 * 100.0
    diff_E  = (num.E_GeV - var.E_min_GeV) / var.E_min_GeV * 100.0
    kv("  Δ⟨r²⟩ (num − var) / var =", f"{diff_r2:+.2f}%")
    kv("  ΔE   (num − var) / var =", f"{diff_E:+.2f}%")
    print()
    print("  Cross-check note: variational E is an UPPER bound on the true")
    print("  ground-state energy.  We expect E_num ≤ E_var and a slightly")
    print("  larger ⟨r²⟩_num because the true Airy ground state has fatter")
    print("  outer tails than the Gaussian.")

    # ------------------------------------------------------------------
    # Step 3: full v3 prediction with decomposition
    # ------------------------------------------------------------------
    section("3) FULL V3 PREDICTION  r_p² = ⟨r²⟩_3body + string + kink")

    summary = compute_proton_radius_v3_summary(SIGMA_QCD_GEV2, XI_QCD_FM, m_eff)

    print()
    print(f"    r²_kink (3D sech²) = {intrinsic_r2_kink_3D(XI_QCD_FM):.4f} fm²")
    print()
    header = (
        f"    {'method / Lüscher':<28}"
        f"{'⟨r²⟩_3b':>10}"
        f"{'r²_str':>9}"
        f"{'r²_kink':>9}"
        f"{'r_p²':>9}"
        f"{'r_p':>8}"
        f"{'err':>9}"
    )
    print(header)
    print(f"    {'-' * 28}{'-' * 10}{'-' * 9}{'-' * 9}{'-' * 9}{'-' * 8}{'-' * 9}")
    for est in summary.estimates:
        which_lusch = "endpoint" if est.r2_string > 0 and \
                       _approx_endpoint(est) else "midpoint"
        label = f"{est.method} / {which_lusch}"
        err_pct = 100.0 * est.frac_error
        print(
            f"    {label:<28}"
            f"{est.r2_3body:>10.4f}"
            f"{est.r2_string:>9.4f}"
            f"{est.r2_kink:>9.4f}"
            f"{est.r2_total:>9.4f}"
            f"{est.r_p_fm:>8.4f}"
            f"{err_pct:>+8.1f}%"
        )

    print()
    print(f"    Empirical r_p² = {R_PROTON_CHARGE_EXP_FM**2:.4f} fm²,  "
          f"r_p = {R_PROTON_CHARGE_EXP_FM:.4f} fm")

    # ------------------------------------------------------------------
    # Step 4: gap closure analysis
    # ------------------------------------------------------------------
    section("4) GAP CLOSURE — DOES THE 3-BODY WAVEFUNCTION CLOSE THE 22% GAP?")

    target_r2 = R_PROTON_CHARGE_EXP_FM ** 2
    closed_count = 0
    print()
    print(f"    {'configuration':<28}"
          f"{'r_p²(sub)':>11}"
          f"{'gap(fm²)':>10}"
          f"{'closed?':>14}")
    print(f"    {'-' * 28}{'-' * 11}{'-' * 10}{'-' * 14}")
    for est in summary.estimates:
        which_lusch = "endpoint" if _approx_endpoint(est) else "midpoint"
        label = f"{est.method} / {which_lusch}"
        gap = target_r2 - est.r2_total
        closed = abs(est.frac_error) < 0.05
        if closed:
            closed_count += 1
        marker = "YES (<5%)" if closed else f"NO ({est.frac_error*100:+.0f}%)"
        print(
            f"    {label:<28}"
            f"{est.r2_total:>11.4f}"
            f"{gap:>10.4f}"
            f"{marker:>14}"
        )
    print()
    print(f"    {closed_count} of {len(summary.estimates)} v3 estimates close the gap.")

    # ------------------------------------------------------------------
    # Step 5: canonical and best, side-by-side with v2
    # ------------------------------------------------------------------
    section("5) HONEST ASSESSMENT — V3 vs V2 vs EMPIRICAL")

    canonical = summary.estimates[0]   # variational + midpoint
    best = min(summary.estimates, key=lambda e: abs(e.frac_error))

    print()
    print("  Canonical v3 estimate (variational, midpoint Lüscher):")
    print(f"    • method        = {canonical.method}")
    print(f"    • √⟨r²⟩_3body  = {canonical.r_rms_3body:.4f} fm  "
          f"(replaces v2's R₀ = {HBARC_GEV_FM/SIGMA_QCD_GEV2**0.5:.4f} fm)")
    print(f"    • ⟨r²⟩_3body   = {canonical.r2_3body:.4f} fm²")
    print(f"    • r²_string     = {canonical.r2_string:.4f} fm²")
    print(f"    • r²_kink       = {canonical.r2_kink:.4f} fm²")
    print(f"    • r²_total      = {canonical.r2_total:.4f} fm²")
    print(f"    • r_p           = {canonical.r_p_fm:.4f} fm   "
          f"({canonical.frac_error*100:+.1f}%)")
    print()
    print("  Best v3 estimate (smallest |error|):")
    which_lusch = "endpoint" if _approx_endpoint(best) else "midpoint"
    print(f"    • {best.method} / {which_lusch}")
    print(f"    • √⟨r²⟩_3body  = {best.r_rms_3body:.4f} fm")
    print(f"    • ⟨r²⟩_3body   = {best.r2_3body:.4f} fm²")
    print(f"    • r²_string     = {best.r2_string:.4f} fm²")
    print(f"    • r²_kink       = {best.r2_kink:.4f} fm²")
    print(f"    • r²_total      = {best.r2_total:.4f} fm²")
    print(f"    • r_p           = {best.r_p_fm:.4f} fm   "
          f"({best.frac_error*100:+.1f}%)")
    print()

    # Bracket
    rps = [e.r_p_fm for e in summary.estimates]
    rp_min, rp_max = min(rps), max(rps)
    contains_target = rp_min <= R_PROTON_CHARGE_EXP_FM <= rp_max
    print(f"  Bracket of v3 predictions: r_p ∈ [{rp_min:.4f}, {rp_max:.4f}] fm")
    print(f"  Empirical 0.8409 fm is "
          f"{'INSIDE' if contains_target else 'OUTSIDE'} this bracket.")
    print()

    # Verdict
    print("  Verdict:")
    if abs(best.frac_error) < 0.05:
        print(f"    • Best v3 closes the gap to within 5% of empirical.")
        print(f"      The 3-body wavefunction supplies the missing ⟨r²⟩.")
    elif abs(best.frac_error) < 0.10:
        print(f"    • Best v3 reduces the gap to ~{abs(best.frac_error)*100:.0f}%.")
        print(f"      Substantial closure but not yet within 5%.")
    else:
        print(f"    • Best v3 still off by {best.frac_error*100:+.0f}%.")
        print(f"      The 3-body wavefunction alone does not close the gap.")
    print()

    # Comparison with v1 (-33%) and v2 (-22% canonical)
    print("  Progression:")
    print(f"    • v1 (bare Y-junction):                r_p ≈ 0.50-0.56 fm  (-33% to -41%)")
    print(f"    • v2 (Y-junction + string fluct):       r_p ≈ 0.62-0.65 fm  (-22% to -23%)")
    print(f"    • v3 (3-body wf + string + kink):       r_p ∈ [{rp_min:.3f}, {rp_max:.3f}] fm  "
          f"({canonical.frac_error*100:+.1f}% to {best.frac_error*100:+.1f}%)")
    print()
    print("  Inputs used (none fitted to r_p):")
    print("    • σ_QCD = 0.180 GeV²,  ξ_QCD = 0.2 fm,  m_eff = √σ ≈ 0.424 GeV")
    print("    • Schrödinger eqn for one effective constituent in V(r) = σ r")
    print("    • Lüscher transverse-fluctuation log with R₀_eff = √⟨r²⟩_3body")
    print("    • Sine-Gordon sech² kink width contribution")
    print()
    hr()
    return 0


def _approx_endpoint(est) -> bool:
    """Detect whether endpoint or midpoint Lüscher was used.

    The endpoint formula gives exactly 2× the midpoint value.  We compare
    the per-dim contribution to a midpoint reference computed from
    R₀_eff = √⟨r²⟩_3body.
    """
    import math
    if est.r2_string == 0:
        return False
    if est.r_rms_3body <= est.xi_fm:
        return False  # log < 0
    log_arg = math.log(est.r_rms_3body / est.xi_fm)
    midpoint_per_dim_GeV_inv2 = log_arg / (2.0 * math.pi * est.sigma_GeV2)
    midpoint_per_dim_fm2 = midpoint_per_dim_GeV_inv2 * HBARC_GEV_FM ** 2
    midpoint_total = 2.0 * midpoint_per_dim_fm2
    # Closer to midpoint or endpoint (= 2 × midpoint)?
    ratio = est.r2_string / midpoint_total
    return ratio > 1.5


if __name__ == "__main__":
    sys.exit(main())
