"""Test driver for the substrate prediction of nucleon magnetic moments.

Computes μ_p and μ_n from the SU(2)-flavour additive-quark-moment formulas
using a constituent kink mass m_K_eff drawn from substrate primitives —
NEVER from the QCD-fitted 336 MeV.  Several substrate-natural mass
candidates are swept; the one that best reproduces the empirical pair
(μ_p = +2.793, μ_n = −1.913) μ_N is identified.

Run:
    python scripts/nucleon_magnetic_moments_test.py
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.nucleon_magnetic_moments import (
    MU_P_EMPIRICAL,
    MU_N_EMPIRICAL,
    SIGMA_QCD_GEV2,
    M_PROTON_MEV,
    compute_nucleon_moments_summary,
    isoscalar_moment_substrate,
    isovector_moment_substrate,
    m_kink_geometric_MeV,
    m_kink_proton_third_MeV,
    m_kink_y_junction_kinematic_MeV,
    m_kink_linear_potential_MeV,
    m_kink_foot_MeV,
    print_full_report,
    proton_moment_SU2,
    neutron_moment_SU2,
)


def main() -> None:
    """Run the full nucleon-moment substrate analysis."""
    summary = compute_nucleon_moments_summary(
        sigma_GeV2=SIGMA_QCD_GEV2,
        m_proton_MeV=M_PROTON_MEV,
        threshold=0.05,
    )
    print_full_report(summary)

    # ------------------------------------------------------------------
    # Closed-form sanity: SU(2) gives μ_p / μ_n = −3/2 exactly
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Closed-form sanity checks (independent of m_K_eff)")
    print("=" * 96)
    print()
    for label, m_q in [
        ("(a) m_K = √σ", m_kink_geometric_MeV()),
        ("(b) m_K = m_p/3", m_kink_proton_third_MeV()),
        ("(c) m_K = (3/4)√σ", m_kink_y_junction_kinematic_MeV()),
        ("(d) m_K = (a₁/3)√σ", m_kink_linear_potential_MeV()),
        ("(e) m_K = M_Foot", m_kink_foot_MeV()),
    ]:
        mu_p = proton_moment_SU2(m_q)
        mu_n = neutron_moment_SU2(m_q)
        ratio = mu_p / mu_n
        iso_sum = isoscalar_moment_substrate(m_q)
        iso_diff = isovector_moment_substrate(m_q)
        print(f"  {label:<22}  μ_p/μ_n = {ratio:+.4f}  "
              f"(SU(2) target: −1.500)")
        print(f"  {'':22}  μ_p+μ_n  = {iso_sum:+.4f}  "
              f"(empirical: {MU_P_EMPIRICAL + MU_N_EMPIRICAL:+.4f})")
        print(f"  {'':22}  μ_p-μ_n  = {iso_diff:+.4f}  "
              f"(empirical: {MU_P_EMPIRICAL - MU_N_EMPIRICAL:+.4f})")
        print()

    # ------------------------------------------------------------------
    # Sign structure (the cleanest substrate prediction)
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" SIGN STRUCTURE TEST (cleanest substrate prediction)")
    print("=" * 96)
    print()
    sign_p_correct = all(
        proton_moment_SU2(m_q) > 0
        for m_q in (200.0, 313.0, 350.0, 424.0, 500.0, 600.0)
    )
    sign_n_correct = all(
        neutron_moment_SU2(m_q) < 0
        for m_q in (200.0, 313.0, 350.0, 424.0, 500.0, 600.0)
    )
    print(f"  μ_p > 0 for all reasonable m_K_eff: {sign_p_correct}")
    print(f"  μ_n < 0 for all reasonable m_K_eff: {sign_n_correct}")
    print()
    print("  These signs are forced by:")
    print("    1. Up-kink charge e_u = +2/3 e and down-kink charge e_d = −1/3 e.")
    print("    2. SU(2) spin-flavour structure of the J=1/2 baryon ground state.")
    print("    3. m_K_eff > 0 (any positive constituent mass).")
    print()

    # ------------------------------------------------------------------
    # Diagnostic: empirical-best m_K_eff
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" DIAGNOSTIC: which m_K_eff would land BOTH moments within 5%?")
    print("=" * 96)
    print()
    # Solve for m_q such that μ_p_pred = MU_P_EMPIRICAL exactly:
    #   μ_p = m_p / m_q  → m_q = m_p / μ_p_emp
    m_for_p = M_PROTON_MEV / MU_P_EMPIRICAL
    # And for μ_n: μ_n = −(2/3) m_p / m_q → m_q = −(2/3) m_p / μ_n_emp
    m_for_n = -(2.0 / 3.0) * M_PROTON_MEV / MU_N_EMPIRICAL
    print(f"  m_K_eff that exactly reproduces μ_p = +2.793: {m_for_p:.2f} MeV")
    print(f"  m_K_eff that exactly reproduces μ_n = −1.913: {m_for_n:.2f} MeV")
    print(f"  The two empirical moments prefer different m_K_eff values,")
    print(f"  reflecting the well-known SU(6) → SU(3)-flavour breaking.")
    print(f"  The substrate's nearest natural mass is then the question.")
    print()


if __name__ == "__main__":
    main()
