"""Test driver for the substrate chromomagnetic N-Δ splitting prediction.

Computes the substrate prediction Δm_NΔ from Möbius half-flux spin-spin
physics and compares to the empirical 293.7 MeV.  Uses ONLY substrate
primitives (σ, ξ_QCD) — no α_s import, no constituent quark mass input.

Run:
    python scripts/chromomagnetic_substrate_test.py
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.chromomagnetic_substrate import (
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
    XI_QCD_INV_GEV,
    DELTA_M_NDELTA_MEV,
    M_PROTON_MEV,
    M_DELTA_MEV,
    bare_kink_mass_GeV,
    compute_NDelta_splitting,
    constituent_kink_mass_GeV,
    mobius_alpha_at_QCD,
    print_full_report,
    sensitivity_sweep,
    total_spin_pair_sum,
    wavefunction_density_GeV3,
)


def main() -> None:
    print("=" * 78)
    print("  CHROMOMAGNETIC SPIN-SPIN INTERACTION IN THE STIFF MEDIUM SUBSTRATE")
    print("                  N-Δ ground-state splitting test")
    print("=" * 78)
    print()
    print(f"  Empirical N-Δ splitting:  {DELTA_M_NDELTA_MEV:.2f} MeV")
    print(f"  (m_p = {M_PROTON_MEV:.2f} MeV,  m_Δ = {M_DELTA_MEV:.1f} MeV)")
    print()
    print(f"  Substrate inputs:")
    print(f"    σ_QCD     = {SIGMA_QCD_GEV2:.4f} GeV²   (string tension)")
    print(f"    ξ_QCD     = {XI_QCD_FM:.3f} fm = {XI_QCD_INV_GEV:.4f} GeV⁻¹  "
          f"(coherence length)")
    print()
    alpha_M = mobius_alpha_at_QCD()
    psi_density = wavefunction_density_GeV3()
    m_K_eff = constituent_kink_mass_GeV()
    m_K_bare = bare_kink_mass_GeV()
    print(f"  Derived quantities (substrate primitives only):")
    print(f"    α_M(QCD)  = σ × ξ²            = {alpha_M:.4f}")
    print(f"    m_K_eff   = √σ                = {m_K_eff:.4f} GeV  "
          f"(substrate constituent kink mass)")
    print(f"    m_K_bare  = 8 ℏc / ξ_QCD      = {m_K_bare:.4f} GeV  (UV kink mass)")
    print(f"    |ψ(0)|²   = (3/4π) σ^{{3/2}}    = {psi_density:.4e} GeV³")
    print()

    # Spin-sum sanity-check
    print("  Spin-sum sanity check (3 spin-½ kinks):")
    print(f"    J = 1/2  (N): ⟨Σ S_i·S_j⟩ = {total_spin_pair_sum(0.5, 3):+.3f}  "
          f"(expect −0.750)")
    print(f"    J = 3/2  (Δ): ⟨Σ S_i·S_j⟩ = {total_spin_pair_sum(1.5, 3):+.3f}  "
          f"(expect +0.750)")
    print(f"    Δ-N spin sum:               = "
          f"{total_spin_pair_sum(1.5,3) - total_spin_pair_sum(0.5,3):+.3f}  "
          f"(expect +1.500)")
    print()

    print_full_report()
    print()

    # Final verdict
    print("=" * 78)
    print("  VERDICT")
    print("=" * 78)

    runs = sensitivity_sweep()
    default = runs[0][1]
    pct = 100.0 * default.fractional_error
    abs_pct = abs(pct)

    if abs_pct < 30.0:
        verdict = "MAJOR result — substrate predicts N-Δ within 30%."
    elif abs_pct < 100.0:
        verdict = "Significant — substrate captures the right scale but is off."
    else:
        verdict = "Order-of-magnitude only — geometry right, normalization off."

    print(f"  Substrate prediction: Δm_NΔ = {default.delta_m_predicted_MeV:.1f} MeV")
    print(f"  Observed:                    = {DELTA_M_NDELTA_MEV:.1f} MeV")
    print(f"  Fractional error:            = {pct:+.1f}%")
    print(f"  → {verdict}")
    print()
    print("  No α_s import, no constituent quark mass input.  All numbers come from")
    print("  σ, ξ_QCD, and the SU(3) Casimir (inherited via §18.49).")


if __name__ == "__main__":
    main()
