"""Test: Cabibbo angle from substrate Möbius bundle on (d, s) flavor.

Spec context: §§18.10, 18.30, 18.49, 18.64.3, 18.64.4.

WHAT THIS SCRIPT DOES
---------------------
1. Computes the substrate-derived (m_d, m_s):
     m_d = m_u_anchor + α × m_K(Airy)   ≈ 4.57 MeV
     m_s = (m_K² − m_π²) f_π² / |⟨q̄q⟩|  ≈ 119 MeV  (§18.64.2 bilinear GMOR)

2. Computes the substrate Möbius mixing element:
     ε = α × m_K(Airy) ≈ 2.41 MeV  (§18.64.4)

3. Diagonalises the 2×2 mass matrix [[m_d, ε], [ε, m_s]] and reads θ_C.

4. Cross-checks against:
   - GIM identity sin θ_C = √(m_d/m_s) with substrate masses,
   - Sweep of alternative substrate ε candidates,
   - Pure-topology angles from substrate-natural integers (2, 3, π only),
   - Numerical near-miss topology angles (5, 7, 14, 27, 55) for completeness.

5. Reports an honest assessment: which mechanism is "natural" vs "fitted",
   and whether multiple candidates work but none is forced.

Usage:
    cd "/Users/hendrixx./Desktop/untitled folder"
    PYTHONPATH=src python3 scripts/cabibbo_substrate_test.py
"""

from __future__ import annotations

import os
import sys

# Make sure src/ is on the path
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from stiff_medium.cabibbo_substrate import (
    compute_cabibbo_substrate_summary,
    format_summary_report,
    SIN_THETA_C_EMP,
    THETA_C_DEG_EMP,
)


def main() -> None:
    """Run the full substrate Cabibbo analysis and print the report."""
    summary = compute_cabibbo_substrate_summary()
    print(format_summary_report(summary))

    # Final one-line headline for parsing-friendliness
    print()
    print("=" * 100)
    print(" Headline numbers (for spec / audit ledger)")
    print("=" * 100)
    p = summary.primary
    print(f"  Substrate (m_d, m_s) MeV    : ({p.m_d_substrate_MeV:.4f}, "
          f"{p.m_s_substrate_MeV:.4f})")
    print(f"  ε hypothesis (A) α × m_K(Airy)  = {p.epsilon_alpha_mK_MeV:.4f} MeV  "
          f"→  θ_C = {p.primary_alpha_mK.theta_C_deg:.4f}° "
          f"(err {p.primary_alpha_mK.pct_error_deg:+.2f}%)")
    print(f"  ε hypothesis (B) σξ/(2π)=f_π/π  = {p.epsilon_flux_holo_MeV:.4f} MeV  "
          f"→  θ_C = {p.primary_flux_holonomy.theta_C_deg:.4f}° "
          f"(err {p.primary_flux_holonomy.pct_error_deg:+.2f}%)")
    print()
    print(f"  WINNER: {p.winning_hypothesis}")
    print(f"      θ_C = {p.theta_C_substrate_deg:.4f}°  (empirical 13.04°,  "
          f"err {p.pct_error_deg:+.2f}%)")
    print(f"      sin θ_C = {p.sin_theta_C_substrate:.4f}  (empirical 0.2255,  "
          f"err {(p.sin_theta_C_substrate - SIN_THETA_C_EMP) / SIN_THETA_C_EMP * 100.0:+.2f}%)")
    print()
    print(f"  GIM consistency (substrate)  : "
          f"sin θ_C = {summary.gim_with_subs_masses.sin_theta_C:.4f} "
          f"(err {summary.gim_with_subs_masses.pct_error_deg:+.2f}%)")
    print(f"  GIM consistency (PDG)        : "
          f"sin θ_C = {summary.gim_with_pdg_masses.sin_theta_C:.4f} "
          f"(err {summary.gim_with_pdg_masses.pct_error_deg:+.2f}%)")
    print()


if __name__ == "__main__":
    main()
