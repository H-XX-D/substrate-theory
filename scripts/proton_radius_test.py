#!/usr/bin/env python3
"""Proton charge radius test: predict r_p from the Y-junction kink picture.

Usage:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src python3 scripts/proton_radius_test.py

This script:
1. Computes the Y-junction equilibrium radius R₀ from σ_QCD = 0.180 GeV²
   under two physically motivated assumptions (dimensional 1/√σ and the
   rotating-Y mass relation 2 M_p / (3πσ)).
2. Adds the intrinsic kink width contribution from ξ_QCD = 0.2 fm.
3. Compares the prediction to the empirical r_p^charge = 0.8409 fm
   (CODATA 2018 / muonic hydrogen).
4. Runs ±5% sensitivity scans on σ and ξ.
5. Gives an HONEST assessment of which factors are physically motivated
   vs phenomenological.

The honesty requirements (per the task spec):
    - Report the actual r_p the model gives, not a hand-tuned value.
    - Report what σ, ξ, and geometric factors went into the prediction.
    - Report which factors are physically motivated vs phenomenological.
    - Do NOT claim more precision than the underlying theory justifies.
"""

from __future__ import annotations

import sys

from stiff_medium.proton_radius import (
    HBARC_GEV_FM,
    M_PROTON_GEV,
    R_PROTON_CHARGE_EXP_FM,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
    compute_proton_radius_summary,
    equilibrium_radius_dimensional,
    equilibrium_radius_rotating_Y,
    intrinsic_r2_kink_1D,
    intrinsic_r2_kink_3D,
)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def hr() -> None:
    print("=" * 74)


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
    section("PROTON CHARGE RADIUS FROM SUBSTRATE Y-JUNCTION")

    print()
    kv("Substrate inputs:", "")
    kv("  σ_QCD =", f"{SIGMA_QCD_GEV2:.4f} GeV²  (from K(ξ) running)")
    kv("  ξ_QCD =", f"{XI_QCD_FM:.4f} fm   (kink coherence length)")
    kv("  ℏc =",    f"{HBARC_GEV_FM*1e3:.4f} MeV·fm")
    kv("  M_p (anchor for rotating-Y) =", f"{M_PROTON_GEV:.6f} GeV")
    print()
    kv("Empirical target:", "")
    kv("  r_p^charge =", f"{R_PROTON_CHARGE_EXP_FM:.4f} fm  (CODATA 2018 / μH)")

    # ------------------------------------------------------------------
    # Y-junction equilibrium radius
    # ------------------------------------------------------------------
    section("1) Y-JUNCTION EQUILIBRIUM RADIUS R₀")

    R0_dim = equilibrium_radius_dimensional(SIGMA_QCD_GEV2)
    R0_rot = equilibrium_radius_rotating_Y(SIGMA_QCD_GEV2, M_PROTON_GEV)

    print()
    print("  (A) Dimensional / variational  R₀ = 1/√σ")
    print("      Natural length built from σ alone.  Parameter-free in")
    print("      the substrate model — uses no proton-specific input.")
    kv("      R₀ =", f"{R0_dim:.4f} fm")

    print()
    print("  (B) Rotating Y-junction  L = 2 M_p / (3πσ)")
    print("      From the Nambu-Goto rotating-string mass formula")
    print("          M_p = (3π/2) σ L     ⇒     L = 2 M_p / (3πσ)")
    print("      Uses the empirical proton mass as an extra anchor.")
    kv("      L =", f"{R0_rot:.4f} fm")

    # ------------------------------------------------------------------
    # Intrinsic kink width contribution
    # ------------------------------------------------------------------
    section("2) INTRINSIC KINK WIDTH CONTRIBUTION  ⟨r²⟩_intrinsic")

    r2_1D = intrinsic_r2_kink_1D(XI_QCD_FM)
    r2_3D = intrinsic_r2_kink_3D(XI_QCD_FM)

    print()
    print("  Sine-Gordon kink charge density ∝ sech²(x/ξ) gives")
    print("      ⟨x²⟩ = (π²/12) ξ² ≈ 0.822 ξ²    [1D]")
    print("  Three independent transverse copies (isotropic 3D smear) gives")
    print("      ⟨r²⟩ = 3 × ⟨x²⟩ = (π²/4) ξ² ≈ 2.467 ξ²   [3D]")
    print()
    kv("  ⟨r²⟩_intrinsic (1D) =", f"{r2_1D:.4f} fm²   "
       f"(rms = {r2_1D**0.5:.4f} fm)")
    kv("  ⟨r²⟩_intrinsic (3D) =", f"{r2_3D:.4f} fm²   "
       f"(rms = {r2_3D**0.5:.4f} fm)")

    # ------------------------------------------------------------------
    # Full predictions
    # ------------------------------------------------------------------
    section("3) PROTON CHARGE RADIUS PREDICTIONS")

    summary = compute_proton_radius_summary(SIGMA_QCD_GEV2, XI_QCD_FM)

    print()
    print(f"    {'Configuration':<46}{'R₀ [fm]':>10}{'r_p [fm]':>10}{'err':>8}")
    print(f"    {'-' * 46}{'-' * 10}{'-' * 10}{'-' * 8}")
    for est in summary.estimates:
        err_pct = 100.0 * est.frac_error
        print(
            f"    {est.label:<46}"
            f"{est.R0_fm:>10.4f}"
            f"{est.r_p_fm:>10.4f}"
            f"{err_pct:>+7.1f}%"
        )

    print()
    print(f"    Empirical r_p = {R_PROTON_CHARGE_EXP_FM:.4f} fm")

    # ------------------------------------------------------------------
    # Sensitivity scans
    # ------------------------------------------------------------------
    section("4) SENSITIVITY: ±5% IN σ AND ξ")

    print()
    print(
        f"    {'Configuration':<32}"
        f"{'r_p [fm]':>10}"
        f"{'+5% σ':>10}"
        f"{'-5% σ':>10}"
        f"{'+5% ξ':>10}"
        f"{'-5% ξ':>10}"
    )
    print(f"    {'-' * 32}{'-' * 10}{'-' * 10}{'-' * 10}{'-' * 10}{'-' * 10}")
    for sens in summary.sensitivities:
        print(
            f"    {sens.label:<32}"
            f"{sens.nominal_r_p:>10.4f}"
            f"{sens.delta_sigma_plus_pct:>+9.2f}%"
            f"{sens.delta_sigma_minus_pct:>+9.2f}%"
            f"{sens.delta_xi_plus_pct:>+9.2f}%"
            f"{sens.delta_xi_minus_pct:>+9.2f}%"
        )

    # ------------------------------------------------------------------
    # Honest assessment
    # ------------------------------------------------------------------
    section("5) HONEST ASSESSMENT")

    # Pick the canonical reading: the parameter-free dimensional R₀ with
    # a 3D kink width (the most generous geometric assumption).
    canonical = next(
        e for e in summary.estimates
        if "dimensional" in e.label and "3D" in e.label
    )
    err_pct = 100.0 * canonical.frac_error

    print()
    print("  Inputs used (none fitted to the charge radius):")
    print("    • σ_QCD = 0.180 GeV²  — from K(ξ) running, anchored at the")
    print("      electron Compton scale via substrate_rg_running.py.")
    print("    • ξ_QCD = 0.2 fm     — kink width at the QCD scale, set by")
    print("      the substrate coherence length (substrate_primitives.py).")
    print("    • Y-junction topology with 3 quarks at equal distance R₀")
    print("      from the central vertex.  Geometric factor c_geom = 1.")
    print()
    print("  Physically motivated factors:")
    print("    • R₀ = 1/√σ (dimensional analysis, single dimensionful input)")
    print("    • Kink width contribution ⟨x²⟩ = (π²/12) ξ² (sine-Gordon)")
    print("    • Equilateral uud charge weighting → c_geom = 1 (exact)")
    print()
    print("  Phenomenological / modelling choices:")
    print("    • 1D vs 3D kink-width smear (factor 3 ambiguity in ⟨r²⟩_intr)")
    print("    • Whether to use dimensional R₀ or rotating-Y L (factor")
    print("      ~2 difference; rotating-Y uses M_p as extra anchor)")
    print()

    print(f"  Canonical (parameter-free) prediction:")
    print(f"    R₀ = 1/√σ + 3D kink width  →  r_p = {canonical.r_p_fm:.4f} fm")
    print(f"    Empirical              r_p = {R_PROTON_CHARGE_EXP_FM:.4f} fm")
    print(f"    Fractional error             = {err_pct:+.1f}%")
    print()

    # Also report the best estimate among all four
    best = min(summary.estimates, key=lambda e: abs(e.frac_error))
    best_err_pct = 100.0 * best.frac_error
    print(f"  Best of four estimates:")
    print(f"    {best.label}")
    print(f"    r_p = {best.r_p_fm:.4f} fm   (err {best_err_pct:+.1f}%)")
    print()

    # Range of predictions
    rps = [e.r_p_fm for e in summary.estimates]
    print(f"  Full range across the four estimates: "
          f"r_p ∈ [{min(rps):.3f}, {max(rps):.3f}] fm")
    print(f"  This 'simple Y-junction' bracket includes the empirical "
          f"value {R_PROTON_CHARGE_EXP_FM:.4f} fm: "
          f"{'YES' if min(rps) <= R_PROTON_CHARGE_EXP_FM <= max(rps) else 'NO'}")

    rp_min, rp_max = min(rps), max(rps)
    underestimate = R_PROTON_CHARGE_EXP_FM > rp_max
    print()
    print("  Bottom line:")
    print(f"    • All four physically motivated estimates lie in")
    print(f"      r_p ∈ [{rp_min:.3f}, {rp_max:.3f}] fm — the empirical 0.84 fm")
    print(f"      is {'OUTSIDE' if underestimate else 'INSIDE'} this range.")
    print("    • The simple Y-junction + sine-Gordon kink picture")
    print("      UNDERESTIMATES the proton charge radius by ~30-65%.")
    print("    • Likely missing physics: (i) the meson cloud, which adds a")
    print("      pion-loop contribution of order +0.1-0.2 fm² to ⟨r²⟩;")
    print("      (ii) sea-quark / gluon contributions that smear charge")
    print("      out beyond R₀; (iii) string fluctuations broadening the")
    print("      Y-arms.  These are all known to roughly double ⟨r²⟩ in")
    print("      conventional QCD models.")
    print("    • Sensitivity is ~2-3% per 5% in σ or ξ: the prediction")
    print("      is mathematically robust but parametrically too small.")
    print("    • Honest verdict: the substrate Y-junction picture gives the")
    print("      RIGHT order of magnitude (sub-fm, set by 1/√σ ~ 0.47 fm)")
    print("      but does not reproduce 0.84 fm without additional cloud /")
    print("      fluctuation contributions that we have not yet modelled.")
    hr()
    return 0


if __name__ == "__main__":
    sys.exit(main())
