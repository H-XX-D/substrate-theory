#!/usr/bin/env python3
"""Substrate-thermal BBN n/p ratio test (§18.40-§18.44, §18.63.3, §18.66).

Usage:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src python3 scripts/bbn_from_substrate_thermal_test.py

This script exercises `bbn_from_substrate_thermal.py` — a derivation of
the n/p ratio that goes through the substrate's *partition function*
explicitly, rather than plugging substrate Δm into the standard
Boltzmann formula.

What's substrate-derived (visible in the output below):

  1. ⟨φ²⟩_T = T²/12 from the substrate field-theory thermal correlator.
  2. log Z₁(M, T) = log[g (MT/2π)^(3/2)] − M/T from the saddle-point of
     the substrate path integral around a static kink solution.
  3. n_n/n_p = Z_n/Z_p = (m_n/m_p)^(3/2) exp(-Δm/T) — the Boltzmann
     factor falls out of substrate free energy, NOT plugged in.
  4. The (m_n/m_p)^(3/2) kinematic correction is genuinely substrate
     content; standard treatments drop it.
  5. Γ_n→p ∝ T⁵ from the substrate kink-mode density of states in the
     soft limit.
  6. H(T) = π√(g_⋆/90) T²/M_Pl: substrate FRW reduces to the standard
     form at BBN T (post-desaturation phase).

What's inherited (not yet substrate-derived):

  • G_F (electroweak vertex)
  • g_A (bound-state QCD effect)
  • τ_n (free-neutron lifetime, used for gap decay)
  • g_⋆ (relativistic-dof counting)
"""

from __future__ import annotations

import sys

from stiff_medium.bbn_from_substrate_thermal import (
    DM_NP_PDG_MEV,
    DM_NP_SUBSTRATE_MEV,
    G_A,
    G_F_MEV,
    G_STAR_BBN,
    M_KINK_MEV,
    M_N_MEV,
    M_P_MEV,
    M_PL_MEV,
    Y_P_OBSERVED,
    n_over_p_from_substrate_partition,
    predict_bbn_from_substrate_thermal,
    scan_proto_matter_strain,
    single_kink_partition_log,
    solve_substrate_freezeout,
    substrate_hubble_rate,
    substrate_phi_squared_thermal,
    substrate_thermal_weak_rate,
)


def banner(s: str) -> None:
    """Print a formatted section header."""
    print()
    print("=" * 76)
    print(s)
    print("=" * 76)


def main() -> int:
    """Run the full substrate-thermal BBN diagnostic."""

    banner(
        "BBN n/p ratio from a substrate thermal kink ensemble (§18.40-§18.44)"
    )
    print(
        "Substrate inputs:"
        f"\n  m_p (substrate, §18.62)   = {M_P_MEV} MeV"
        f"\n  m_n = m_p + Δm            = {M_N_MEV} MeV"
        f"\n  Δm (substrate, §18.63.3)  = {DM_NP_SUBSTRATE_MEV} MeV"
        f"\n  m_kink (substrate, §18.22)= {M_KINK_MEV/1000:.1f} GeV"
        f"\n  M_Pl (reduced)            = {M_PL_MEV:.3e} MeV"
    )
    print(
        "Inherited (not substrate-derived) inputs:"
        f"\n  G_F (electroweak)         = {G_F_MEV:.3e} MeV⁻²"
        f"\n  g_A (bound-state QCD)     = {G_A}"
        f"\n  g_⋆ at BBN epoch          = {G_STAR_BBN}"
    )
    print(f"PDG cross-check Δm: {DM_NP_PDG_MEV} MeV (substrate vs PDG: +{(DM_NP_SUBSTRATE_MEV-DM_NP_PDG_MEV)/DM_NP_PDG_MEV*100:.2f}%)")

    # ----------------------------------------------------------------------
    # Step 1: substrate thermal state and single-kink partition function
    # ----------------------------------------------------------------------
    banner("Step 1: Substrate thermal state ⟨φ²⟩_T and Z₁(M,T)")
    print("⟨φ²⟩_T  =  T² / 12   (3+1D massless free-scalar thermal correlator)")
    print()
    print(f"  {'T (MeV)':>10}  {'⟨φ²⟩_T (MeV²)':>16}  {'log Z₁(m_p,T)':>14}  {'log Z₁(m_n,T)':>14}")
    for T in (5.0, 1.0, 0.8, 0.5, 0.1):
        phi2 = substrate_phi_squared_thermal(T)
        log_Zp = single_kink_partition_log(M_P_MEV, T)
        log_Zn = single_kink_partition_log(M_N_MEV, T)
        print(f"  {T:>10.3f}  {phi2:>16.3e}  {log_Zp:>14.4f}  {log_Zn:>14.4f}")
    print()
    print("Each Z₁ value is dominated by exp(-M/T): at T=1 MeV and m_p=938 MeV,")
    print(f"M/T = {M_P_MEV/1.0:.0f} ⇒ free nucleons are exponentially rare in the")
    print("equilibrium thermal substrate at T ≪ m_p.  The MeV-scale BBN epoch is")
    print("therefore a balance of *ratios* of these tiny exponentials, not a")
    print("balance against a thermal nucleon density of order T³.")

    # ----------------------------------------------------------------------
    # Step 2-3: n/p ratio from substrate free energy
    # ----------------------------------------------------------------------
    banner("Step 2-3: n_n/n_p from substrate free-energy difference  (DERIVED)")
    print("Substrate result:")
    print("  Z_n/Z_p = (m_n/m_p)^(3/2) × exp(-Δm/T)")
    print("  F_n − F_p = -T ln(Z_n/Z_p) = Δm − (3T/2) ln(m_n/m_p)")
    print()
    print(f"  {'T (MeV)':>10}  {'n/p (substrate)':>17}  {'exp(-Δm/T)':>14}  "
          f"{'kin. corr.':>11}")
    for T in (5.0, 2.0, 1.0, 0.8, 0.5, 0.1):
        r = n_over_p_from_substrate_partition(T)
        print(
            f"  {T:>10.3f}  {r.n_p_ratio:>17.6f}  {r.boltzmann_only:>14.6f}  "
            f"{r.kinematic_corr:>11.6f}"
        )
    print()
    print("The kinematic correction (m_n/m_p)^(3/2) ≈ 1.00213 is independent of T")
    print("(it's a ratio of soliton-zero-mode Gaussian volumes).  This is the")
    print("part standard treatments drop; the substrate predicts it explicitly.")

    # ----------------------------------------------------------------------
    # Step 4: substrate-thermal weak rate vs FRW Hubble rate
    # ----------------------------------------------------------------------
    banner("Step 4-5: Γ(T) (substrate-thermal) vs H(T) (substrate FRW)")
    print("  Γ ∝ G_F² T⁵ from substrate kink-mode density of states in soft limit")
    print("  H = π √(g_⋆/90) T² / M_Pl   from substrate FRW (post-desaturation)")
    print()
    print(f"  {'T (MeV)':>10}  {'H (MeV)':>12}  {'Γ (MeV)':>12}  {'H/Γ':>8}  state")
    for T in (5.0, 2.0, 1.0, 0.8, 0.5, 0.1):
        H = substrate_hubble_rate(T)
        G = substrate_thermal_weak_rate(T)
        ratio = H / G
        state = "frozen" if H > G else "in equilibrium"
        print(f"  {T:>10.3f}  {H:>12.3e}  {G:>12.3e}  {ratio:>8.3f}  {state}")
    print()
    print("Crossover at H/Γ = 1 marks freeze-out — see Step 6 below.")

    # ----------------------------------------------------------------------
    # Step 6: freeze-out with substrate Δm
    # ----------------------------------------------------------------------
    banner("Step 6: Freeze-out (H = Γ) with substrate Δm and Y_p prediction")
    fo_substrate = solve_substrate_freezeout(delta_m_MeV=DM_NP_SUBSTRATE_MEV)
    fo_pdg = solve_substrate_freezeout(delta_m_MeV=DM_NP_PDG_MEV)

    print(f"With substrate Δm = {DM_NP_SUBSTRATE_MEV} MeV (§18.63.3):")
    print(f"  T_freeze         = {fo_substrate.T_freeze_MeV:.4f} MeV")
    print(f"  H(T_F)           = {fo_substrate.H_freeze_MeV:.3e} MeV")
    print(f"  Γ(T_F)           = {fo_substrate.Gamma_freeze_MeV:.3e} MeV")
    print(f"  n/p (substrate)  = {fo_substrate.n_p_freeze:.6f}")
    print(f"  exp(-Δm/T_F)     = {fo_substrate.n_p_freeze_naive:.6f}")
    print(f"  kinematic factor = {fo_substrate.kinematic_corr:.6f}")

    print(f"\nWith PDG Δm = {DM_NP_PDG_MEV} MeV (cross-check):")
    print(f"  T_freeze         = {fo_pdg.T_freeze_MeV:.4f} MeV")
    print(f"  n/p (substrate)  = {fo_pdg.n_p_freeze:.6f}")

    # Full BBN prediction:
    bbn_substrate = predict_bbn_from_substrate_thermal(delta_m_MeV=DM_NP_SUBSTRATE_MEV)
    bbn_pdg = predict_bbn_from_substrate_thermal(delta_m_MeV=DM_NP_PDG_MEV)

    print()
    print("Apply free-neutron β-decay during the gap to T_BBN ≈ 0.073 MeV:")
    print(f"  t_freeze         = {bbn_substrate.t_freeze_s:.3f} s")
    print(f"  t_BBN            = {bbn_substrate.t_BBN_s:.3f} s")
    print(f"  Δt               = {bbn_substrate.t_BBN_s-bbn_substrate.t_freeze_s:.3f} s")
    print(f"  decay factor     = {bbn_substrate.decay_factor:.4f}")
    print(f"  n/p at BBN onset = {bbn_substrate.n_p_BBN:.6f}")
    print()
    print("Helium-4 mass fraction Y_p = 2 (n/p)_BBN / (1 + (n/p)_BBN):")
    print()
    print(f"  Substrate Δm:  Y_p = {bbn_substrate.Y_p_predicted:.4f}  "
          f"(observed {Y_P_OBSERVED}, error {bbn_substrate.Y_p_frac_error*100:+.2f}%)")
    print(f"  PDG Δm:        Y_p = {bbn_pdg.Y_p_predicted:.4f}  "
          f"(error {bbn_pdg.Y_p_frac_error*100:+.2f}%)")
    print()
    print(f"  Observed:      Y_p = {Y_P_OBSERVED} ± 0.003 (Planck + light-element)")

    # ----------------------------------------------------------------------
    # What's substrate-dynamics vs what's inherited
    # ----------------------------------------------------------------------
    banner("Audit: substrate-dynamics vs inherited cosmology")
    print(
        "  substrate-derived in this calculation (NEW vs. bbn_predictions.py):"
        "\n    • ⟨φ²⟩_T = T²/12 from substrate Lagrangian §18.11 at finite T"
        "\n    • Z₁(M,T) = g (MT/2π)^(3/2) e^(−M/T) from soliton path-integral saddle"
        "\n    • n_n/n_p from substrate free-energy difference (Step 3)"
        "\n    • (m_n/m_p)^(3/2) kinematic correction (substrate-natural, ≈1.00213)"
        "\n    • T⁵ scaling of Γ from kink-mode density of states in soft limit"
        "\n    • Δm = 1.331 MeV from §18.63.3 (already substrate)"
        "\n    • H(T) FRW form from §18.40-§18.44, valid at BBN epoch"
    )
    print(
        "\n  inherited from outside the substrate framework:"
        "\n    • G_F = 1.166×10⁻¹¹ MeV⁻² (electroweak vertex, §18.75.1 deferred)"
        "\n    • g_A = 1.27 (bound-state QCD effect)"
        "\n    • τ_n = 879 s (free-neutron lifetime, anchor for gap decay)"
        "\n    • g_⋆ = 10.75 / 3.36 (relativistic dof counting; field content"
        "\n      is substrate-listed but the dof counting itself is bookkeeping)"
        "\n    • Numerical prefactor 1.5×(7π/30)(1+3g_A²) calibrated to PDG inputs"
    )

    # ----------------------------------------------------------------------
    # Sensitivity scan over the proto-matter strain σ_m (§18.66)
    # ----------------------------------------------------------------------
    banner("Sensitivity scan: pre-CMB proto-matter strain σ_m (§18.66)")
    print("Adding σ_m × M_Pl⁴ to the radiation energy density at BBN epoch")
    print("would boost H(T_F) and shift Y_p.  Cosmological bounds (Y_p < 0.252)")
    print("require σ_m ≲ 10⁻⁸⁶ at BBN; this scan demonstrates the substrate")
    print("framework's capability for such modifications.")
    print()
    scan = scan_proto_matter_strain()
    print(f"  {'σ_m':>10}  {'T_F (MeV)':>11}  {'H(T_F) MeV':>12}  "
          f"{'n/p':>10}  {'Y_p':>8}  {'ΔY_p / Y_p':>11}")
    for sigma, T_F, H, np_F, Yp, frac in scan.rows:
        print(f"  {sigma:>10.1e}  {T_F:>11.4f}  {H:>12.3e}  "
              f"{np_F:>10.5f}  {Yp:>8.4f}  {frac*100:>10.4f}%")
    print()
    print("Default σ_m = 0 reproduces the standard BBN result; nonzero σ_m")
    print("shifts T_F upward (H grows faster), boosting n/p_freeze and Y_p.")
    print("The substrate framework predicts σ_m ≈ 0 at BBN epoch (matter has")
    print("decoupled from substrate strain by then; §18.66.1 two-threshold")
    print("picture: σ_γ already crossed before T = 1 MeV regime is reached).")

    # ----------------------------------------------------------------------
    # Verdict
    # ----------------------------------------------------------------------
    banner("Verdict")
    Y_p = bbn_substrate.Y_p_predicted
    err_pct = bbn_substrate.Y_p_frac_error * 100
    if abs(err_pct) < 5.0:
        print(f"  Substrate Y_p = {Y_p:.4f}, observed {Y_P_OBSERVED} — agreement {err_pct:+.2f}%")
        print("  Substrate-thermal derivation reproduces standard SBBN within ±5%.")
        print("  The Boltzmann ratio is now DERIVED from the substrate partition")
        print("  function rather than asserted by analogy — Step 3 above.")
        verdict = 0
    else:
        print(f"  Substrate Y_p = {Y_p:.4f}, observed {Y_P_OBSERVED} — disagreement {err_pct:+.2f}%")
        print("  Substrate-thermal derivation deviates from observation; check inputs.")
        verdict = 1
    return verdict


if __name__ == "__main__":
    sys.exit(main())
