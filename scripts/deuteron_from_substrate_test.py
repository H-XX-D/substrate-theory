"""Deuteron binding from substrate kink-kink dynamics — direct V(r) construction.

This test driver runs the substrate deuteron calculation:

  1. **Long-range V_OPE(r)** from ``pion_exchange_substrate.V_OPE_substrate_MeV``:
     Yukawa kernel × (1/12)(m_π²/m_N²) × g²_πNN/(4π) × spin_isospin_factor.
     The Yukawa form e^{-m_π r}/r is geometric.  Substrate provides:
       - f_π = ½ σ ξ_QCD ≈ 91.22 MeV  (§18.61.8)
       - g_πNN = m_N · g_A^SU(6) / f_π_substrate ≈ 17.16  (Goldberger-Treiman)
     m_π and m_N are PDG-anchored (as in pion_exchange_substrate).

  2. **Short-range V_rep(r) from kink-overlap** (this module):
     V_rep(r) = n_eff · σ · ξ_QCD · exp(-r/ξ_QCD)
       - σ × ξ_QCD ≈ 182 MeV   (substrate energy per kink-overlap volume)
       - n_eff = 6              (Y-junction triangle 3×3 − 3 = 6 cross pairs)
       - r_core = ξ_QCD = 0.2 fm
     This is the substrate's natural "Pauli core" — kink-core overlap costs
     condensate-suppression energy proportional to σ × ξ × (overlap volume).

  3. **Solve radial Schrödinger** for u(r) = r ψ(r):
        -ℏ²/(2μ) u''(r) + V(r) u(r) = E u(r)
     with μ = m_N/2, sparse eigsh, n=1500 grid points, R_max = 25 fm.

The output reports the binding |E_ground|, rms radius, ⟨T⟩, ⟨V⟩, V(r) profile,
and a sensitivity sweep over the Y-junction overlap count n_eff.

Run:  PYTHONPATH=src python3 scripts/deuteron_from_substrate_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stiff_medium.deuteron_from_substrate import (
    B_DEUTERON_OBSERVED_MEV,
    N_EFF_KINK_PAIRS,
    SIGMA_XI_MEV,
    compute_deuteron_summary,
    print_deuteron_summary,
)
from stiff_medium.pion_exchange_substrate import (
    F_PI_MEV_SUBSTRATE,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
)


def main() -> None:
    """Run the substrate deuteron test."""
    print()
    print("=" * 78)
    print(" DEUTERON BINDING FROM SUBSTRATE — DIRECT V(r) CONSTRUCTION")
    print("=" * 78)
    print()
    print(" Strategy: V(r) = V_OPE^substrate(r) + V_rep^kink-overlap(r)")
    print()
    print(f"   V_OPE: substrate-derived from f_π = ½σξ = "
          f"{F_PI_MEV_SUBSTRATE:.2f} MeV")
    print(f"          (inherits from pion_exchange_substrate.py — no re-derivation)")
    print()
    print(f"   V_rep: substrate kink-overlap from σ × ξ_QCD = "
          f"{SIGMA_XI_MEV:.2f} MeV")
    print(f"          per Y-junction kink-pair, with N_eff = "
          f"{N_EFF_KINK_PAIRS:.1f} cross pairs")
    print()
    print(f"   Solve radial Schrödinger for u(r) = r ψ(r), μ = m_N/2,")
    print(f"   R_max = 25 fm, n_grid = 1500, sparse eigsh.")
    print()
    print(f"   Empirical B_d (PDG) = {B_DEUTERON_OBSERVED_MEV:.4f} MeV.")
    print(f"   Goal: predict to within ~30%.")
    print()

    summary = compute_deuteron_summary()
    print_deuteron_summary(summary)

    # --------------------------------------------------------------
    # Compact "headline" line at the end for easy programmatic checks
    # --------------------------------------------------------------
    rsd = summary.result_coupled
    rc = summary.result_central
    err = 100.0 * rsd.fractional_error
    print("=" * 78)
    print(" HEADLINE")
    print("=" * 78)
    print(f"   B_d (substrate, central-only)  = {rc.binding_MeV:.4f} MeV")
    print(f"   B_d (substrate, coupled S-D)   = {rsd.binding_MeV:.4f} MeV")
    print(f"   B_d (empirical)                = {rsd.b_observed_MeV:.4f} MeV")
    print(f"   fractional error (coupled S-D) = {err:+.1f}%")
    if abs(err) <= 30.0:
        print(f"   STATUS: within 30% target  -> PASS")
    elif abs(err) <= 50.0:
        print(f"   STATUS: within 50%  -> CLOSE (deuteron is barely bound;")
        print(f"           the substrate's V_C+V_T+V_rep predicts a real bound state)")
    else:
        print(f"   STATUS: outside 50%  -> see sensitivity sweep")
    print()


if __name__ == "__main__":
    main()
