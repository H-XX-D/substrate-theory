"""Cross-scale lepton-mass test driver — run K(xi) running against M_Foot.

Run:
    PYTHONPATH=src python3 scripts/lepton_masses_from_K_test.py

Honest assessment is printed at the end.
"""

from __future__ import annotations

import math

from stiff_medium.lepton_masses_from_K import (
    FM_TO_M,
    K_ELECTRON,
    K_QCD_TARGET,
    M_E_MEV,
    M_MU_MEV,
    M_TAU_MEV,
    SIGMA_QCD_GEV2,
    XI_ELECTRON,
    XI_QCD,
    K_running,
    fit_running_exponent,
    foot_scale_M,
    m_kink_kinematic_MeV,
    m_kink_phenomenological_MeV,
    run_full_analysis,
)


def hr(char: str = "=", n: int = 78) -> str:
    """Return a horizontal rule."""
    return char * n


def main() -> int:
    """Run the cross-scale lepton-mass analysis and print the honest report."""
    print(hr("="))
    print("CROSS-SCALE LEPTON-MASS TEST: does K(xi) running predict M_Foot?")
    print(hr("="))
    print()

    # ------------------------------------------------------------------
    # 1.  Substrate inputs
    # ------------------------------------------------------------------
    a = fit_running_exponent()
    print("1. Substrate K(xi) running (anchored at xi_e and xi_QCD)")
    print("-" * 78)
    print(f"   xi_e          = {XI_ELECTRON:.4e} m  (electron Compton)")
    print(f"   K_e           = {K_ELECTRON:.4e} Pa  (= hbar*c/xi_e^4)")
    print(f"   xi_QCD        = {XI_QCD:.4e} m  (= 0.2 fm)")
    print(f"   K_QCD_target  = {K_QCD_TARGET:.4e} Pa  "
          f"(so sigma = sigma_lat * K = {SIGMA_QCD_GEV2:.3f} GeV^2)")
    print(f"   exponent a    = {a:.4f}  in K(xi) = K_e (xi_e/xi)^a")
    print()

    # ------------------------------------------------------------------
    # 2.  Foot scale
    # ------------------------------------------------------------------
    M_foot = foot_scale_M()
    print("2. Foot scale M from PDG lepton masses")
    print("-" * 78)
    print(f"   m_e           = {M_E_MEV:.6f} MeV")
    print(f"   m_mu          = {M_MU_MEV:.4f} MeV")
    print(f"   m_tau         = {M_TAU_MEV:.2f} MeV")
    print(f"   M_Foot        = ((sqrt(m_e)+sqrt(m_mu)+sqrt(m_tau))/3)^2")
    print(f"                 = {M_foot:.4f} MeV")
    print()

    # ------------------------------------------------------------------
    # 3.  Substrate-derived candidates for M
    # ------------------------------------------------------------------
    report = run_full_analysis()

    print("3. Substrate candidates for M")
    print("-" * 78)
    print(f"   (A) m_kink(xi_e)  = 8 hbar c / xi_e            "
          f"= {report.M_kink_xi_e_MeV:.4f} MeV   (= 8 m_e)")
    print(f"   (B) sqrt(K_e * xi_e^3 * m_e c^2)               "
          f"= {report.M_dimensional_MeV:.4f} MeV   (= m_e identically)")
    print(f"   (C) Solve m_kink(xi*) = M_Foot for xi*:")
    print(f"        kinematic    xi*_kin = "
          f"{report.xi_star_kinematic_m:.4e} m  "
          f"= {report.xi_star_kinematic_fm:.4f} fm")
    print(f"        phenomenol.  xi*_phen = "
          f"{report.xi_star_phen_m:.4e} m  "
          f"= {report.xi_star_phen_fm:.4f} fm")
    print()
    print(f"        QCD band: [xi_QCD, xi_e] = "
          f"[{XI_QCD/FM_TO_M:.4f} fm, {XI_ELECTRON/FM_TO_M:.4f} fm]")
    print(f"        xi*_kin in band? "
          f"{report.xi_star_kin_in_QCD_band}")
    print(f"        xi*_phen in band? "
          f"{report.xi_star_phen_in_QCD_band}")
    print()

    # ------------------------------------------------------------------
    # 4.  Kink-mass curve at sample scales
    # ------------------------------------------------------------------
    print("4. m_kink(xi) at sample scales (kinematic vs phenomenological)")
    print("-" * 78)
    sample_xi = [
        ("xi_e",        XI_ELECTRON),
        ("xi_e/10",     XI_ELECTRON / 10.0),
        ("xi_e/100",    XI_ELECTRON / 100.0),
        ("xi_tau",      report.xi_tau_m),
        ("1 fm",        1.0 * FM_TO_M),
        ("xi_QCD",      XI_QCD),
    ]
    print(f"   {'label':<10s} {'xi (m)':>12s} {'xi (fm)':>10s} "
          f"{'m_kin (MeV)':>14s} {'m_phen (MeV)':>14s} {'K (Pa)':>13s}")
    for label, xi in sample_xi:
        m_kin = m_kink_kinematic_MeV(xi)
        m_phen = m_kink_phenomenological_MeV(xi)
        K = K_running(xi)
        print(f"   {label:<10s} {xi:12.4e} {xi/FM_TO_M:10.4f} "
              f"{m_kin:14.4e} {m_phen:14.4e} {K:13.4e}")
    print()

    # ------------------------------------------------------------------
    # 5.  Nambu-Goto cross-check at xi_tau
    # ------------------------------------------------------------------
    print("5. Nambu-Goto cross-check at xi_tau = hbar / (m_tau c)")
    print("-" * 78)
    print(f"   xi_tau                = {report.xi_tau_m:.4e} m "
          f"= {report.xi_tau_m/FM_TO_M:.4f} fm")
    print(f"   K(xi_tau)             = {K_running(report.xi_tau_m):.4e} Pa")
    print(f"   sigma(xi_tau)         = sigma_lat * K(xi_tau) = "
          f"{report.sigma_at_xi_tau_GeV2:.4f} GeV^2")
    print(f"   m_NG = sqrt(sigma*hc) = {report.m_NG_at_xi_tau_MeV:.4f} MeV")
    print(f"   m_tau (PDG)           = {M_TAU_MEV:.4f} MeV")
    print(f"   ratio m_NG/m_tau      = {report.ratio_m_NG_to_m_tau:.4f}")
    print()

    # ------------------------------------------------------------------
    # 6.  Summary table
    # ------------------------------------------------------------------
    print("6. Summary: lepton mass scale predictions vs observation")
    print("-" * 78)
    print(f"   {'Quantity':<40s} {'Value':>16s} {'Target':>16s}")
    print(f"   {'M_Foot (empirical)':<40s} "
          f"{report.M_foot_MeV:>14.4f} MeV "
          f"{'(reference)':>16s}")
    print(f"   {'m_kink(xi_e)':<40s} "
          f"{report.M_kink_xi_e_MeV:>14.4f} MeV "
          f"{report.M_foot_MeV:>14.4f} MeV")
    print(f"   {'M_kink / M_Foot':<40s} "
          f"{report.ratio_M_kink_to_M_foot:>14.4f}    "
          f"{'1.0 ideal':>16s}")
    print(f"   {'m_NG(xi_tau)':<40s} "
          f"{report.m_NG_at_xi_tau_MeV:>14.4f} MeV "
          f"{M_TAU_MEV:>14.4f} MeV")
    print(f"   {'m_NG(xi_tau) / m_tau':<40s} "
          f"{report.ratio_m_NG_to_m_tau:>14.4f}    "
          f"{'1.0 ideal':>16s}")
    print()

    # ------------------------------------------------------------------
    # 7.  Honest assessment
    # ------------------------------------------------------------------
    print(hr("="))
    print("HONEST ASSESSMENT")
    print(hr("="))

    # Computed ratios for the verdict
    rk = report.ratio_M_kink_to_M_foot
    rng = report.ratio_m_NG_to_m_tau
    xi_star = report.xi_star_kinematic_fm

    lines = []
    lines.append(
        f"   M_Foot                = {report.M_foot_MeV:.4f} MeV "
        f"(empirical mass scale of the Foot family)."
    )
    lines.append(
        f"   m_kink(xi_e) / M_Foot = {rk:.4f}.  "
        f"The kinematic kink mass at the electron Compton scale falls"
    )
    lines.append(
        f"                            short of M_Foot by a factor "
        f"~{1.0/rk:.2f}.  The kink at xi_e is 8 m_e ~ 4.09 MeV;"
    )
    lines.append(
        f"                            M_Foot ~ 313.84 MeV.  These differ by "
        f"~77x, so candidate (A) does NOT predict M_Foot."
    )
    lines.append("")
    lines.append(
        f"   xi*_kin (kinematic):    {xi_star:.4f} fm.  "
        f"This sits well within the band [xi_QCD={XI_QCD/FM_TO_M:.4f} fm, "
    )
    lines.append(
        f"                            xi_e={XI_ELECTRON/FM_TO_M:.2f} fm], "
        f"close to the muon Compton wavelength."
    )
    lines.append(
        f"                            But xi* is FORCED by m_kink = 8 hbar c "
        f"/ xi: it is just hbar c / (M_Foot/8)."
    )
    lines.append(
        f"                            The kinematic relation gives xi* "
        f"automatically; it does NOT involve K(xi)."
    )
    lines.append("")
    lines.append(
        f"   Phenomenological (running-K) prediction at xi*_phen = "
        f"{report.xi_star_phen_fm:.4e} fm."
    )
    lines.append(
        f"   With a = {report.a_running:.4f}, the running K makes m_kink_phen(xi) "
        f"diverge sharply from m_kink_kin(xi)"
    )
    lines.append(
        f"   away from the electron anchor.  At xi_QCD: "
        f"m_kin = {report.m_kink_kin_at_xi_QCD_MeV:.3e} MeV  vs  "
    )
    lines.append(
        f"   m_phen = {report.m_kink_phen_at_xi_QCD_MeV:.3e} MeV - the running K "
        f"violates the substrate identity hbar = K xi^4 / c"
    )
    lines.append(
        f"   away from xi_e.  The two formulas only coincide at xi_e by "
        f"construction."
    )
    lines.append("")
    lines.append(
        f"   m_NG(xi_tau) / m_tau  = {rng:.4f}.  The Nambu-Goto formula "
        f"with the running sigma at xi_tau"
    )
    lines.append(
        f"                            gives {report.m_NG_at_xi_tau_MeV:.1f} MeV "
        f"vs the observed {M_TAU_MEV:.1f} MeV.  No clean coincidence."
    )
    lines.append("")
    lines.append(
        f"   Candidate (B): sqrt(K_e * xi_e^3 * m_e c^2) "
        f"= {report.M_dimensional_MeV:.4f} MeV"
    )
    lines.append(
        f"   identically reduces to m_e (because K_e xi_e^3 = m_e c^2 from the "
        f"hbar = K xi^4 / c"
    )
    lines.append(
        f"   identity at xi_e).  It carries no NEW information; it just "
        f"recovers m_e."
    )
    lines.append("")
    lines.append(hr("-"))
    lines.append("   VERDICT")
    lines.append(hr("-"))
    lines.append(
        f"   The substrate K(xi) running ALONE does NOT predict the Foot "
        f"mass scale M_Foot ~ 313.86 MeV."
    )
    lines.append("")
    lines.append(
        f"   The natural mass scales reachable from K(xi) running at xi_e "
        f"are:"
    )
    lines.append(
        f"       - m_kink(xi_e)              = {report.M_kink_xi_e_MeV:.4f} MeV  "
        f"({report.M_kink_xi_e_MeV/M_E_MEV:.4f} m_e)"
    )
    lines.append(
        f"       - m_e (= sqrt(K_e xi_e^3 m_e c^2)) = "
        f"{report.M_dimensional_MeV:.4f} MeV"
    )
    lines.append(
        f"       - sigma_QCD = sigma_lat K(xi_QCD)  fixes the Regge slope, "
        f"used in regge_spectrum.py."
    )
    lines.append(
        f"   None of these is M_Foot.  The Foot scale carries information "
        f"from the LEPTON HIERARCHY (m_e, m_mu, m_tau)"
    )
    lines.append(
        f"   that the running K(xi) cannot produce - K(xi) only sets a single "
        f"scale at any given xi."
    )
    lines.append("")
    lines.append(
        f"   What IS missing - per spec sec 18.30 / 18.35:  "
        f"the Foot scale and phase delta come from the"
    )
    lines.append(
        f"   Mobius vertex calculation (3-generation closure of nested "
        f"stress-loaded vectors), NOT from the"
    )
    lines.append(
        f"   running stiffness.  The directional stiffness kappa_n in "
        f"m c^2 = hbar sqrt(kappa_n / I) is the"
    )
    lines.append(
        f"   distinct input that must be derived from the cone+Mobius "
        f"vertex topology - that is the open"
    )
    lines.append(
        f"   computation.  K(xi) is a coarse-grained substrate stiffness; "
        f"kappa_n is a vertex eigenvalue,"
    )
    lines.append(
        f"   and they are different objects.  M_Foot lives in the kappa_n "
        f"sector, not the K(xi) sector."
    )
    lines.append("")
    lines.append(
        f"   This is consistent with the meson Regge success: K(xi) "
        f"running PREDICTS the QCD string"
    )
    lines.append(
        f"   tension at xi_QCD, and that flows through to the meson "
        f"spectrum.  But the LEPTON sector is"
    )
    lines.append(
        f"   governed by a DIFFERENT structure (the vertex stiffness), so "
        f"K(xi) running has nothing to say"
    )
    lines.append(
        f"   about M_Foot.  The model partitions the physics correctly: "
        f"K(xi) for hadrons, kappa_n for leptons."
    )

    print("\n".join(lines))
    print()
    print(hr("="))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
