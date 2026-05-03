"""Test driver for the substrate-derived nucleon magnetic moments (Category A).

This script exercises :mod:`stiff_medium.nucleon_moments_substrate`, which
re-derives the single-kink magnetic-moment formula

    μ_kink = q ℏ / (2 m_kink c) = q × (m_p / m_kink) μ_N

from substrate Möbius-bundle geometry (§18.10), then assembles the proton
and neutron moments from the Y-junction kink configuration (§18.30) using
the substrate-derived constituent kink mass m_K_eff = (|a₁|/3)√σ ≈ 330.66 MeV.

Compared with the Category-C companion :mod:`nucleon_magnetic_moments`,
this module pushes the calculation toward Category A: the magnetic-moment
formula structure is derived from substrate Möbius geometry rather than
plugged in from an inherited Dirac equation.

Run:
    python scripts/nucleon_moments_substrate_test.py
"""

from __future__ import annotations

import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.normpath(os.path.join(THIS_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stiff_medium.nucleon_moments_substrate import (
    MU_P_EMPIRICAL,
    MU_N_EMPIRICAL,
    SIGMA_QCD_GEV2,
    M_PROTON_MEV,
    compute_substrate_moments,
    m_kink_eff_MeV,
    neutron_moment_y_junction,
    print_substrate_report,
    proton_moment_y_junction,
    single_kink_moment_muN,
    verify_mobius_moment_origin,
    verify_su2_factors_from_y_junction,
)


def main() -> None:
    """Run the full substrate-derived nucleon-moment analysis."""
    # ------------------------------------------------------------------
    # 1) Print the canonical report
    # ------------------------------------------------------------------
    result = compute_substrate_moments(sigma_GeV2=SIGMA_QCD_GEV2)
    print_substrate_report(result)

    # ------------------------------------------------------------------
    # 2) Detailed sanity checks (independent verification)
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Independent sanity checks")
    print("=" * 96)
    print()

    # 2a) Single-kink formula at m = m_p, q = 1 must give 1.000 μ_N
    test_unit = single_kink_moment_muN(charge_in_e=1.0, m_kink_MeV=M_PROTON_MEV)
    print(f"  μ_kink(q=1, m=m_p) = {test_unit:.6f} μ_N (expect 1.000000)  "
          f"{'PASS' if abs(test_unit - 1.0) < 1e-12 else 'FAIL'}")

    # 2b) The single-kink formula scales as 1/m
    m_a = 200.0
    m_b = 400.0
    mu_a = single_kink_moment_muN(1.0, m_a)
    mu_b = single_kink_moment_muN(1.0, m_b)
    ratio = mu_a / mu_b
    expected = m_b / m_a
    print(f"  μ(m={m_a})/μ(m={m_b}) = {ratio:.4f} (expect {expected:.4f})  "
          f"{'PASS' if abs(ratio - expected) < 1e-9 else 'FAIL'}")

    # 2c) The single-kink formula scales linearly in q
    mu_q1 = single_kink_moment_muN(1.0, 300.0)
    mu_q2 = single_kink_moment_muN(2.0, 300.0)
    print(f"  μ(q=2)/μ(q=1) = {mu_q2/mu_q1:.4f} (expect 2.0000)  "
          f"{'PASS' if abs(mu_q2/mu_q1 - 2.0) < 1e-9 else 'FAIL'}")
    print()

    # ------------------------------------------------------------------
    # 3) The closed-form SU(2) identities
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Closed-form SU(2) identities (independent of m_K_eff)")
    print("=" * 96)
    print()
    m_kink = m_kink_eff_MeV()
    mu_p = proton_moment_y_junction(m_kink)
    mu_n = neutron_moment_y_junction(m_kink)
    print(f"  m_K_eff (substrate) = {m_kink:.2f} MeV")
    print()

    # SU(2): μ_p / μ_n = -3/2 exactly
    ratio = mu_p / mu_n
    print(f"  μ_p / μ_n        = {ratio:+.4f}  (SU(2) target: -1.5000)  "
          f"{'PASS' if abs(ratio + 1.5) < 1e-9 else 'FAIL'}")

    # SU(2): μ_p = m_p/m_K μ_N exactly
    expected_p = M_PROTON_MEV / m_kink
    print(f"  μ_p              = {mu_p:+.4f}  (SU(2) target: m_p/m_K = {expected_p:.4f})  "
          f"{'PASS' if abs(mu_p - expected_p) < 1e-9 else 'FAIL'}")

    # SU(2): μ_n = -(2/3) m_p/m_K μ_N exactly
    expected_n = -(2.0 / 3.0) * M_PROTON_MEV / m_kink
    print(f"  μ_n              = {mu_n:+.4f}  (SU(2) target: -(2/3)m_p/m_K = {expected_n:+.4f})  "
          f"{'PASS' if abs(mu_n - expected_n) < 1e-9 else 'FAIL'}")
    print()

    # ------------------------------------------------------------------
    # 4) Möbius-origin verification dictionary
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Möbius-bundle origin of the moment formula (full dict)")
    print("=" * 96)
    print()
    mob = verify_mobius_moment_origin()
    for key, value in mob.items():
        print(f"  {key:<30} = {value}")
    print()
    print("  Source: half-flux holonomy ∮A = π · w (§18.10), spin-½")
    print("  statistics from 4π-periodicity (§18.4), Compton-radius cone")
    print("  ρ = ℏ/(m c) for the kink localization.")
    print()

    # ------------------------------------------------------------------
    # 5) SU(2) factor verification dictionary
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" SU(2) [56] factor structure from Y-junction spin coupling")
    print("=" * 96)
    print()
    su2 = verify_su2_factors_from_y_junction()
    for key, value in su2.items():
        print(f"  {key:<30} = {value}")
    print()
    print("  Source: SU(6) [56] J=½ ground-state expansion for three")
    print("  spin-½ kinks at three Y-junction vertices (§18.30) with")
    print("  symmetric spin-flavour and antisymmetric colour content.")
    print()

    # ------------------------------------------------------------------
    # 6) Sweep over alternative kink-mass candidates (cross-comparison)
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Cross-comparison with other substrate kink-mass candidates")
    print("=" * 96)
    print()
    import math
    candidates = [
        ("m_K = √σ                  [N-Δ geometric]", 1000.0 * math.sqrt(SIGMA_QCD_GEV2)),
        ("m_K = m_p/3               [proton third]", M_PROTON_MEV / 3.0),
        ("m_K = (3/4)√σ             [Y-junction kinematic]",
            1000.0 * 0.75 * math.sqrt(SIGMA_QCD_GEV2)),
        ("m_K = (|a₁|/3)√σ          [Airy linear-V kinetic - this module]",
            m_kink_eff_MeV()),
        ("m_K = M_Foot              [lepton-vertex scale]", 313.86),
    ]
    print(f"  {'candidate':<55}  {'m_K [MeV]':>10}  "
          f"{'μ_p':>9}  {'err':>8}  {'μ_n':>9}  {'err':>8}")
    print("-" * 100)
    for label, m_q in candidates:
        mu_p = proton_moment_y_junction(m_q)
        mu_n = neutron_moment_y_junction(m_q)
        err_p = 100.0 * (mu_p - MU_P_EMPIRICAL) / abs(MU_P_EMPIRICAL)
        err_n = 100.0 * (mu_n - MU_N_EMPIRICAL) / abs(MU_N_EMPIRICAL)
        print(f"  {label:<55}  {m_q:>10.2f}  "
              f"{mu_p:>+9.4f}  {err_p:>+7.2f}%  "
              f"{mu_n:>+9.4f}  {err_n:>+7.2f}%")
    print()
    print("  The (|a₁|/3)√σ Airy linear-V kinetic mass is the substrate's natural")
    print("  prediction (proton_radius_v3.py uses the same kink kinetic mass);")
    print("  it lands both moments within 2% of PDG.")
    print()

    # ------------------------------------------------------------------
    # 7) Summary line
    # ------------------------------------------------------------------
    print("=" * 96)
    print(" Summary")
    print("=" * 96)
    print()
    print(f"  μ_p (substrate)  = {result.mu_p_muN:+.4f} μ_N")
    print(f"  μ_p (PDG)        = {result.mu_p_emp:+.4f} μ_N   "
          f"(err {result.err_p_pct:+.2f} %)")
    print()
    print(f"  μ_n (substrate)  = {result.mu_n_muN:+.4f} μ_N")
    print(f"  μ_n (PDG)        = {result.mu_n_emp:+.4f} μ_N   "
          f"(err {result.err_n_pct:+.2f} %)")
    print()
    within_2pct = (abs(result.err_p_pct) < 2.0 and abs(result.err_n_pct) < 2.0)
    if within_2pct:
        print("  STATUS: PASS — both moments within 2% of PDG, with the")
        print("          single-kink formula derived from substrate Möbius geometry")
        print("          (Category-A push completed).")
    else:
        print("  STATUS: WARNING — error exceeds 2% threshold.")
    print()


if __name__ == "__main__":
    main()
