"""Test driver: does substrate K(ξ) running reproduce QCD α_s(Q²)?

The §18.61.1 Möbius coupling α_M = σ × ξ² ≈ 0.185 happens to be near
α_s near the QCD scale (≈ 0.4-0.5 at 1 GeV, lower at the QCD breakdown
scale ≈ 0.987 GeV ⇔ ξ_QCD = 0.2 fm).  But does α_M (or any other
combination of substrate primitives) ALSO match α_s at higher scales —
α_s(M_Z) = 0.118?

Strategy: extend the fitted K(ξ) running (a ≈ -5.69, K decreases as ξ
shrinks below ξ_e) to scales from 0.2 GeV to 1 TeV, evaluate FIVE
candidate dimensionless substrate couplings, and compare each to the
PDG α_s(Q) at standard reference points.

Key candidates:
  A. α_M = σ × ξ²       (the §18.61.1 coupling, σ in GeV² × ξ in GeV⁻¹)
  B. α_lat = σ ξ² / ℏc  (substrate-natural fully dimensionless)
  C. α_C = ℏc / (K ξ⁴)  (action-quantum residual)
  D. α_D = power-law decrease normalised at the QCD scale
  E. α_E = QCD-style logarithmic fit to A at Q=1 GeV and M_Z

Run:
    python scripts/alpha_s_running_test.py
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.alpha_s_running_from_K import (
    print_full_report,
    run_full_comparison,
)


def main() -> None:
    """Run the full comparison and print the report."""
    print_full_report()
    print()
    print("=" * 78)
    print(" Numerical sanity checks")
    print("=" * 78)
    summary = run_full_comparison()

    def pick(target_Q: float):
        """Pick the CouplingPoint nearest to target_Q [GeV]."""
        return min(summary.points, key=lambda p: abs(p.Q_GeV - target_Q))

    qcd_pt = pick(0.9866)        # ξ ≈ 0.2 fm → Q ≈ 0.987 GeV (the §18.61.1 anchor)
    one_pt = pick(1.0)
    mz_pt = pick(91.1876)
    high_pt = summary.points[-1]
    low_pt = summary.points[0]

    print()
    print(f"At Q ≈ {low_pt.Q_GeV:.4f} GeV (ξ ≈ {low_pt.xi_m * 1e15:.3f} fm):")
    print(f"  σ                  = {low_pt.sigma_GeV2:.4e} GeV²")
    print(f"  α_M = σ ξ²         = {low_pt.alpha_M_naive:.4e}")
    print()
    print(f"At Q ≈ {qcd_pt.Q_GeV:.4f} GeV (ξ = {qcd_pt.xi_m * 1e15:.3f} fm,"
          f" §18.61.1 anchor):")
    print(f"  σ                  = {qcd_pt.sigma_GeV2:.4f} GeV²    (target 0.180 ✓)")
    print(f"  α_M = σ ξ²         = {qcd_pt.alpha_M_naive:.4f}     (spec ≈ 0.185 ✓)")
    print()
    print(f"At Q = {one_pt.Q_GeV:.4f} GeV:")
    print(f"  σ                  = {one_pt.sigma_GeV2:.4f} GeV²")
    print(f"  α_M = σ ξ²         = {one_pt.alpha_M_naive:.4f}")
    pdg_str = (f"{one_pt.alpha_s_pdg:.4f}" if one_pt.alpha_s_pdg == one_pt.alpha_s_pdg
               else "—")
    print(f"  PDG α_s(1 GeV)     ≈ {pdg_str}")
    print()
    print(f"At Q = M_Z = {mz_pt.Q_GeV:.4f} GeV:")
    print(f"  σ                  = {mz_pt.sigma_GeV2:.4e} GeV²")
    print(f"  α_M = σ ξ²         = {mz_pt.alpha_M_naive:.4e}")
    print(f"  PDG α_s(M_Z)        = {mz_pt.alpha_s_pdg:.4f}")
    if mz_pt.alpha_s_pdg > 0:
        print(f"  α_M(M_Z) / α_s_PDG  = {mz_pt.alpha_M_naive / mz_pt.alpha_s_pdg:.4e}")
    print()
    print(f"At Q = {high_pt.Q_GeV:.0f} GeV:")
    print(f"  σ                  = {high_pt.sigma_GeV2:.4e} GeV²")
    print(f"  α_M = σ ξ²         = {high_pt.alpha_M_naive:.4e}")
    pdg_str_h = (f"{high_pt.alpha_s_pdg:.4f}"
                 if high_pt.alpha_s_pdg == high_pt.alpha_s_pdg else "—")
    print(f"  PDG α_s({high_pt.Q_GeV:.0f} GeV) ≈ {pdg_str_h}")
    print()


if __name__ == "__main__":
    main()
