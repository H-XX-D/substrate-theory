"""Test driver for the substrate hyperon mass spectrum (§18.64).

Predicts the full J=1/2 octet (N, Λ, Σ, Ξ) plus J=3/2 Ω⁻ from substrate
primitives σ and ξ_QCD, anchoring m_s_struct from one hyperon (default Λ).

Run:
    python scripts/hyperon_spectrum_test.py
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.hyperon_spectrum import (
    HYPERON_TABLE,
    M_K_CHROMO_GEV,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
    XI_QCD_INV_GEV,
    K_substrate_GeV3,
    chromomag_pair_coupling_MeV,
    compute_hyperon_spectrum,
    print_full_report,
    sensitivity_sweep,
    solve_m_q_struct_MeV,
)


def main() -> None:
    print("=" * 80)
    print("  HYPERON MASS SPECTRUM FROM SUBSTRATE PRIMITIVES (§18.64)")
    print("    J=1/2 octet (N, Λ, Σ, Ξ) + J=3/2 Ω⁻")
    print("=" * 80)
    print()
    print("  Substrate inputs (NO QCD constituent quark mass imported):")
    print(f"    σ_QCD          = {SIGMA_QCD_GEV2:.4f} GeV²   "
          f"(string tension, §18.49.5)")
    print(f"    ξ_QCD          = {XI_QCD_FM:.3f} fm = "
          f"{XI_QCD_INV_GEV:.4f} GeV⁻¹")
    print(f"    α_M(QCD)       = σ ξ² = "
          f"{SIGMA_QCD_GEV2 * XI_QCD_INV_GEV ** 2:.4f}  "
          f"(Möbius coupling)")
    print(f"    m_K_chromo     = √σ = {1000.0 * M_K_CHROMO_GEV:.2f} MeV  "
          f"(geometric ℏc/R₀)")
    print(f"    K_substrate    = {K_substrate_GeV3():.4e} GeV³  "
          f"(chromomag contact)")
    print(f"    chromo pair    = {chromomag_pair_coupling_MeV():.2f} MeV  "
          f"(K/m_q²)")
    print()

    # Anchor 1: structure mass from proton
    m_q_struct = solve_m_q_struct_MeV()
    print("  Step 1 — light-quark structure mass from proton anchor:")
    print(f"    m_q_struct     = {m_q_struct:.2f} MeV")
    print("    (solves m_p = 3 m_q_struct - (3/4) × chromo pair coupling)")
    print()

    # Default run (anchor Λ)
    result = compute_hyperon_spectrum()
    print("  Step 2 — strange-quark structure mass from Λ anchor:")
    print(f"    m_s_struct     = {result.m_s_struct_MeV:.2f} MeV")
    print(f"    Δ_s = m_s − m_q = {result.delta_s_MeV:+.2f} MeV  "
          f"(ONLY flavour input)")
    print()

    print("-" * 80)
    print(" PREDICTIONS")
    print("-" * 80)
    print(f"    {'baryon':<10} {'quark':<6} {'J':<5} "
          f"{'pred [MeV]':>11} {'PDG [MeV]':>11} {'err':>9}")
    quark_lookup = {
        "N(939)": "uud",
        "Λ":      "uds",
        "Σ":      "uus/uds/dds",
        "Ξ":      "uss/dss",
        "Ω⁻":     "sss",
        "Δ(1232)": "uud",
    }
    for p in result.predictions:
        tag = ""
        if p.name == result.anchor_name:
            tag = "  ← anchor"
        elif p.name == "N(939)":
            tag = "  (proton-anchor)"
        spec = next(h for h in HYPERON_TABLE if h.name == p.name)
        print(
            f"    {p.name:<10} {quark_lookup[p.name]:<13} "
            f"J={spec.J:<3}"
            f"{p.mass_pred_MeV:>11.2f} {p.mass_pdg_MeV:>11.2f}"
            f" {100.0 * p.frac_err:>+8.2f}%{tag}"
        )
    print()
    print(f"  Max |err| over predicted (non-anchor) baryons: "
          f"{100.0 * result.max_abs_err:.2f}%")
    print()

    # Highlight the cleanest predictions
    print("-" * 80)
    print(" Pure predictions (zero-fit checks)")
    print("-" * 80)
    purest = [p for p in result.predictions
              if p.name not in (result.anchor_name, "N(939)")]
    for p in purest:
        print(
            f"  {p.name:<10}  pred {p.mass_pred_MeV:7.2f} MeV   "
            f"PDG {p.mass_pdg_MeV:7.2f} MeV   "
            f"err {100.0 * p.frac_err:+6.2f}%"
        )
    print()

    print("-" * 80)
    print(" Σ-Λ splitting (zero-parameter test)")
    print("-" * 80)
    # Both Σ and Λ are uds J=1/2; the difference is pure spin-coupling
    sigma = next(p for p in result.predictions if p.name == "Σ")
    lam = next(p for p in result.predictions if p.name == "Λ")
    pred_split = sigma.mass_pred_MeV - lam.mass_pred_MeV
    obs_split = sigma.mass_pdg_MeV - lam.mass_pdg_MeV
    print(f"  Σ − Λ predicted = {pred_split:.2f} MeV")
    print(f"  Σ − Λ observed  = {obs_split:.2f} MeV")
    err = (pred_split - obs_split) / obs_split
    print(f"  fractional err  = {100.0 * err:+.2f}%")
    print("  (Λ uses c_qq = -3/4 — light spin singlet,")
    print("   Σ uses c_qq = +1/4 with c_qs = -1 — light spin triplet.")
    print("   No extra fit parameter; the splitting comes from spin algebra.)")
    print()

    # Full sensitivity sweep
    print("-" * 80)
    print(" Sensitivity sweep")
    print("-" * 80)
    print(f"  {'variant':<48}{'m_s [MeV]':>13}{'max |err|':>13}")
    for label, res in sensitivity_sweep():
        print(
            f"  {label:<48}{res.m_s_struct_MeV:>13.2f}"
            f"{100.0 * res.max_abs_err:>+12.2f}%"
        )
    print()

    # Verdict
    print("-" * 80)
    print(" Verdict")
    print("-" * 80)
    if result.max_abs_err < 0.05:
        print(f"  PASS — all predicted hyperons within 5% of PDG.")
    else:
        print(f"  Worst prediction: {100.0 * result.max_abs_err:.2f}% off PDG.")
    print()


if __name__ == "__main__":
    main()
