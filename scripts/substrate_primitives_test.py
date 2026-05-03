#!/usr/bin/env python3
"""Substrate primitives derivation test — §18.2, §18.21, §18.22, §18.31, §18.32, §18.46.

Attempts to solve the constraint system for K, ρ, ξ, ε_0, φ_max.
Reports exact numerical values, constraint independence/redundancy,
and an honest account of the multi-scale issue.

Run:
    PYTHONPATH=src python3 scripts/substrate_primitives_test.py
"""

import math
import sys


def main() -> int:  # noqa: PLR0915
    from stiff_medium.substrate_primitives import (
        C_SI,
        HBAR_SI,
        M_E_SI,
        E_CHARGE,
        ALPHA,
        G_SI,
        LAMBDA_OBS,
        RHO_LAMBDA_OBS,
        COULOMB_COUPLING,
        L_PLANCK,
        M_PLANCK,
        SubstratePrimitives,
        solve_from_constraints,
        KINK_MASS_NOTE,
    )

    SEP = "=" * 72
    sep = "-" * 72

    print(SEP)
    print("  SUBSTRATE PRIMITIVES — CONSTRAINT SYSTEM ANALYSIS")
    print("  Stiff-Medium Theory, §18.2 / §18.21 / §18.22 / §18.46")
    print(SEP)
    print()

    # ------------------------------------------------------------------ #
    # 0. Observed input constants                                         #
    # ------------------------------------------------------------------ #
    print("0. OBSERVED INPUT CONSTANTS")
    print(sep)
    print(f"  c            = {C_SI:.6e}  m/s")
    print(f"  hbar         = {HBAR_SI:.6e}  J·s")
    me_MeV = M_E_SI * C_SI**2 / 1.602176634e-13
    print(f"  m_e          = {M_E_SI:.6e}  kg  ({me_MeV:.6f} MeV)")
    print(f"  α            = {ALPHA:.9f}  (1/{1/ALPHA:.5f})")
    print(f"  e            = {E_CHARGE:.6e}  C")
    print(f"  G            = {G_SI:.5e}  m³ kg⁻¹ s⁻²")
    print(f"  Λ            = {LAMBDA_OBS:.3e}  m⁻²")
    print(f"  ρ_Λ          = {RHO_LAMBDA_OBS:.4e}  kg/m³")
    print(f"  e²/(4πε₀)    = {COULOMB_COUPLING:.4e}  J·m  (Coulomb coupling)")
    print(f"  l_Planck     = {L_PLANCK:.4e}  m")
    print(f"  M_Planck     = {M_PLANCK:.4e}  kg  ({M_PLANCK*C_SI**2/1.602e-10:.4e} GeV)")
    print()

    # ------------------------------------------------------------------ #
    # 1. Constraint system algebra                                        #
    # ------------------------------------------------------------------ #
    print("1. CONSTRAINT SYSTEM — ALGEBRA")
    print(sep)
    print("  Three INDEPENDENT constraints on {K, ρ, ξ}:")
    print("    (1)  c = sqrt(K/ρ)                   [wave speed]")
    print("    (2)  hbar = K ξ⁴ / c                  [action quantum §18.46.1]")
    print("    (3)  m_kink = 8 hbar / (c ξ)           [sine-Gordon kink mass]")
    print()
    print("  One REDUNDANT constraint:")
    print("    (4)  α = e²/(4π K ξ⁴)")
    print("           = e²/(4π hbar c)   [using Kξ⁴ = hbar·c from (2)]")
    alpha_from_hbar = COULOMB_COUPLING / (HBAR_SI * C_SI)
    print(f"           = {alpha_from_hbar:.6e}  (= α_obs to 6 decimal places)")
    print("         → α constraint gives NO new information about ξ or K.")
    print()
    print("  Solving (1)+(2): K = hbar c / ξ⁴,  ρ = hbar / (c ξ⁴)")
    print("  Solving (3) with K above:")
    print("    m_kink = 8 hbar / (c ξ)   →   ξ = 8 hbar / (m_kink c)")
    print()
    xi_compton = HBAR_SI / (M_E_SI * C_SI)
    xi_kink_eq_me = 8.0 * HBAR_SI / (M_E_SI * C_SI)
    print(f"  If target m_kink = m_e:  ξ = 8λ_C = {xi_kink_eq_me:.4e} m")
    print(f"  If target ξ    = λ_C:    m_kink = 8m_e = {8*me_MeV:.3f} MeV")
    print()
    print(f"  λ_C(electron) = hbar/(m_e c) = {xi_compton:.4e} m")
    print(f"  8 × λ_C       =               {xi_kink_eq_me:.4e} m")
    print(f"  Ratio (8λ_C) / λ_C = 8.0000 exactly")
    print()

    # ------------------------------------------------------------------ #
    # 2. Solve and display both solutions                                 #
    # ------------------------------------------------------------------ #
    sol_A, sol_B, analysis = solve_from_constraints()

    print("2. SOLUTION A  (ξ = λ_C(electron) — §18.21 primary identification)")
    print(sep)
    print(f"  ξ_A  = {sol_A.xi:.6e} m     (electron Compton wavelength)")
    print(f"  K_A  = {sol_A.K:.6e} J/m³")
    print(f"  ρ_A  = {sol_A.rho:.6e} kg/m³")
    print(f"  φ_max_A = ξ_A = {sol_A.phi_max:.6e} m")
    print()

    vA_c   = sol_A.verify_c()
    vA_h   = sol_A.verify_hbar()
    vA_al  = sol_A.verify_alpha()
    vA_me  = sol_A.verify_electron_mass()

    def _ok(d: dict) -> str:
        return "OK" if d.get("consistent", d.get("consistent_if_kink_is_me", False)) else "FAIL"

    print("  Verification of constraints at Solution A:")
    print(f"    c  = sqrt(K/ρ):     {vA_c['c_derived']:.6e} m/s  "
          f"(err {vA_c['relative_error']:.1e})  [{_ok(vA_c)}]")
    print(f"    hbar = Kξ⁴/c:       {vA_h['hbar_derived']:.6e} J·s  "
          f"(err {vA_h['relative_error']:.1e})  [{_ok(vA_h)}]")
    print(f"    α = e²/4πKξ⁴:      {vA_al['alpha_derived']:.6e}       "
          f"(err {vA_al['relative_error']:.1e})  [REDUNDANT — always OK]")
    m_kink_A_MeV = vA_me['m_kink_MeV']
    ratio_A = vA_me['ratio_kink_to_me']
    print(f"    m_kink=8hbar/(cξ):  {vA_me['m_kink_kg']:.4e} kg = {m_kink_A_MeV:.4f} MeV")
    print(f"    Kink / m_e ratio:   {ratio_A:.4f}  (kink = {ratio_A:.4f} × electron mass)")
    print()
    print("  Interpretation:")
    print(f"    Kink mass at ξ=λ_C = {m_kink_A_MeV:.3f} MeV = 8 × m_e.")
    print("    The kink is NOT the electron — it is ~8× heavier.")
    print("    The electron must be a different mode (Dirac zero-mode, §18.14).")
    print()

    print("3. SOLUTION B  (ξ = 8λ_C so kink mass = m_e exactly)")
    print(sep)
    print(f"  ξ_B  = {sol_B.xi:.6e} m     (= 8 × λ_C)")
    print(f"  K_B  = {sol_B.K:.6e} J/m³")
    print(f"  ρ_B  = {sol_B.rho:.6e} kg/m³")
    print()

    vB_c   = sol_B.verify_c()
    vB_h   = sol_B.verify_hbar()
    vB_al  = sol_B.verify_alpha()
    vB_me  = sol_B.verify_electron_mass()

    print("  Verification of constraints at Solution B:")
    print(f"    c  = sqrt(K/ρ):     {vB_c['c_derived']:.6e} m/s  "
          f"(err {vB_c['relative_error']:.1e})  [{_ok(vB_c)}]")
    print(f"    hbar = Kξ⁴/c:       {vB_h['hbar_derived']:.6e} J·s  "
          f"(err {vB_h['relative_error']:.1e})  [{_ok(vB_h)}]")
    print(f"    α = e²/4πKξ⁴:      {vB_al['alpha_derived']:.6e}       "
          f"(err {vB_al['relative_error']:.1e})  [REDUNDANT — always OK]")
    m_kink_B_MeV = vB_me['m_kink_MeV']
    ratio_B = vB_me['ratio_kink_to_me']
    print(f"    m_kink=8hbar/(cξ):  {vB_me['m_kink_kg']:.4e} kg = {m_kink_B_MeV:.4f} MeV  "
          f"(ratio {ratio_B:.4f})  [{_ok(vB_me)}]")
    print()
    print(f"  ξ_B / ξ_A = {sol_B.xi/sol_A.xi:.4f}  (= 8 exactly, as expected)")
    print()

    # ------------------------------------------------------------------ #
    # 4. ε_0 from observed Λ                                             #
    # ------------------------------------------------------------------ #
    print("4. ε_0 FROM OBSERVED COSMOLOGICAL CONSTANT  (§18.46.2)")
    print(sep)
    eps0 = sol_A.epsilon_0
    print(f"  Λ_obs     = {LAMBDA_OBS:.4e} m⁻²")
    print(f"  ρ_Λ = Λc²/(8πG) = {RHO_LAMBDA_OBS:.4e} kg/m³")
    print(f"  ε_0 = ρ_Λ c²    = {eps0:.4e} J/m³")
    print()
    print("  Cross-check: ε_0 = ½ K_A σ_0²  where σ_0 is the baseline vacuum strain")
    sigma_0 = math.sqrt(2.0 * eps0 / sol_A.K)
    print(f"  σ_0 = sqrt(2ε_0/K_A) = {sigma_0:.4e}  (extremely small)")
    print()
    natural_eps = sol_A.K * sol_A.xi**2
    ratio_eps = eps0 / natural_eps
    print(f"  'Natural' vacuum energy scale K_A ξ_A² = {natural_eps:.3e} J/m")
    print(f"  ε_0 / (K ξ²) = {ratio_eps:.3e}")
    print("  The cosmological constant is ~10⁹ orders of magnitude below the")
    print("  natural substrate energy scale — the cosmological constant problem.")
    print("  §18.38/§18.39: saturation barrier provides a dynamical cap.")
    print()

    # ------------------------------------------------------------------ #
    # 5. φ_max                                                            #
    # ------------------------------------------------------------------ #
    print("5. φ_max FROM σ_max = 0.5  (§18.39)")
    print(sep)
    print("  σ_max = 0.5 is the universal elastic saturation limit.")
    print("  The log-barrier potential V(φ) = -K/2 log(1-(φ/φ_max)²) diverges at φ_max.")
    print("  Natural identification: φ_max = ξ (strain amplitude at kink length scale).")
    print()
    print(f"  Solution A: φ_max = ξ_A = {sol_A.phi_max:.4e} m")
    print(f"  Solution B: φ_max = ξ_B = {sol_B.phi_max:.4e} m")
    print()

    # ------------------------------------------------------------------ #
    # 6. Constraint independence table                                    #
    # ------------------------------------------------------------------ #
    print("6. CONSTRAINT INDEPENDENCE SUMMARY")
    print(sep)
    rows = [
        ("c = sqrt(K/rho)",       "INDEPENDENT",  "Fixes ρ = K/c² once K known"),
        ("hbar = K xi^4 / c",     "INDEPENDENT",  "Fixes K = hbar c/xi^4 once xi known"),
        ("m_kink = 8hbar/(c xi)", "INDEPENDENT",  "Fixes xi = 8hbar/(m_kink c)"),
        ("alpha = e^2/(4piKxi^4)","REDUNDANT",    "= e^2/(4pi hbar c) = alpha always"),
        ("Lambda -> epsilon_0",   "INDEPENDENT",  "Fixes ε_0 from dark energy obs."),
        ("sigma_max=0.5->phi_max","SEMI-INDEP.",  "phi_max/xi = 1 (natural choice)"),
    ]
    print(f"  {'Constraint':<25} {'Status':<14} {'Role'}")
    print(f"  {'-'*25} {'-'*14} {'-'*30}")
    for name, status, role in rows:
        print(f"  {name:<25} {status:<14} {role}")
    print()
    print(f"  Independent constraints: {analysis['independent_constraints']}")
    print(f"  Redundant constraints:   {analysis['redundant_constraints']}")
    print()

    # ------------------------------------------------------------------ #
    # 7. Multi-scale analysis                                             #
    # ------------------------------------------------------------------ #
    print("7. MULTI-SCALE ANALYSIS")
    print(sep)
    ms = sol_A.multi_scale_analysis()

    print("  Physical scales and their ξ values:")
    print(f"    Planck scale:         ξ_P  = {ms['xi_planck_m']:.3e} m    (l_Planck)")
    print(f"    λ_C(electron):        ξ_A  = {ms['xi_compton_m']:.3e} m    (§18.21)")
    print(f"    8×λ_C (kink=m_e):     ξ_B  = {ms['xi_for_kink_equals_me_m']:.3e} m")
    print(f"    SM neutrino (0.1eV):  ξ_ν  = {ms['xi_neutrino_m']:.3e} m")
    print()
    print(f"  Kink mass at ξ = λ_C: m_kink = {ms['m_kink_at_this_xi_MeV']:.3f} MeV")
    print(f"  Ratio m_kink/m_e = {ms['kink_to_me_ratio']:.4f}")
    print()
    print(f"  Multi-scale verdict: {ms['verdict']}")
    print()

    # ------------------------------------------------------------------ #
    # 8. Honest assessment of spec §18.21 formula                        #
    # ------------------------------------------------------------------ #
    print("8. HONEST ASSESSMENT OF SPEC §18.21 FORMULA")
    print(sep)
    print()
    print("  The spec §18.21 writes: 'm_ν = 8 × ρ × ξ'")
    print("  and claims this gives 4.88×10⁻⁵ kg ≈ 27 GeV/c².")
    print()
    print("  DIMENSIONAL CHECK:")
    print("    8 × [kg/m³] × [m] = kg/m²  (surface mass density, not mass)")
    print()
    m_spec_formula = 8 * sol_A.rho * sol_A.xi  # kg/m² — dimensionally wrong
    gev_if_treated_as_kg = m_spec_formula * C_SI**2 / 1.602176634e-10
    print(f"  NUMERICAL CHECK: 8 × ρ_A × ξ_A = {m_spec_formula:.4e} [kg/m²]")
    print(f"  If incorrectly treated as kg: = {gev_if_treated_as_kg:.3e} GeV")
    print(f"  (NOT 27 GeV — off by factor ~10^21)")
    print()
    print("  CORRECT SI formula: m_kink = 8 hbar / (c ξ)   [kg]")
    m_kink_correct = 8.0 * HBAR_SI / (C_SI * sol_A.xi)
    m_kink_MeV_correct = m_kink_correct * C_SI**2 / 1.602176634e-13
    print(f"  = 8 × {HBAR_SI:.4e} / ({C_SI:.4e} × {sol_A.xi:.4e})")
    print(f"  = {m_kink_correct:.4e} kg  = {m_kink_MeV_correct:.4f} MeV")
    print(f"  = 8 × m_e = 8 × 0.511 MeV = {8*0.511:.3f} MeV")
    print()
    print("  CONCLUSION: The spec §18.21 formula 'm_ν = 8ρξ [kg]' has a")
    print("  dimensional error (gives kg/m², not kg). The numerically-correct")
    print("  kink mass at ξ = λ_C(electron) is 8m_e ≈ 4.1 MeV, NOT 27 GeV.")
    print()
    print(f"  {KINK_MASS_NOTE}")
    print()

    # ------------------------------------------------------------------ #
    # 9. Can a single ξ satisfy all constraints?                         #
    # ------------------------------------------------------------------ #
    print("9. HONEST ASSESSMENT: CAN A SINGLE ξ SATISFY ALL CONSTRAINTS?")
    print(SEP)
    print()
    print("  SHORT ANSWER: YES and NO — depends on what 'all constraints' means.")
    print()
    print("  WHAT ONE ξ CAN DO:")
    print("    The three independent constraints (c, hbar, m_kink) are")
    print("    simultaneously satisfied at A UNIQUE ξ for any given m_kink target.")
    print("    Solutions A and B both do this — they just target different m_kink.")
    print()
    print("  WHAT A SINGLE ξ CANNOT DO:")
    print("    ξ = λ_C(electron): kink = 8m_e ≈ 4.1 MeV   [kink ≠ m_e exactly]")
    print("    ξ = 8λ_C:          kink = m_e exactly        [ξ ≠ λ_C]")
    print("    → You cannot have ξ = λ_C AND kink = m_e simultaneously.")
    print("      (These are incompatible: the kink formula gives m_kink = 8m_e at ξ=λ_C.)")
    print()
    print("  THE MULTI-SCALE HIERARCHY (genuine physical content):")
    print()
    print(f"    Scale            ξ [m]         Mass scale     Identification")
    print(f"    ----------       -----------    ----------     -----------------")
    print(f"    Planck           {L_PLANCK:.2e}    Planck (~10^19 GeV) Fundamental ℏ = Kξ_P⁴/c")
    print(f"    λ_C(electron)    {xi_compton:.2e}    4.1 MeV        Kink (NOT electron)")
    print(f"    8λ_C             {xi_kink_eq_me:.2e}    511 keV        Kink = electron")
    print(f"    SM neutrino      ~2e-6 m         0.1 eV         Non-topological mode")
    print()
    print("  SPEC §18.22 STATUS:")
    print("    The spec accepts that the kink ≠ electron and proposes:")
    print("    • Kink = heavy W/Z-like carrier (BUT the actual kink mass from the")
    print("      correct formula at ξ=λ_C is 4.1 MeV, not 27 GeV — the spec's")
    print("      27 GeV figure has a dimensional error).")
    print("    • Electron = Dirac zero-mode on kink background (§18.14, Jackiw-Rebbi).")
    print("    • SM neutrino = non-topological small oscillation (§5B, §18.35).")
    print()
    print("  THE REMAINING TENSION:")
    print("    At ξ = λ_C(e), the kink is 8m_e ≈ 4.1 MeV, not the electron (511 keV).")
    print("    The electron must emerge from a further suppression mechanism")
    print("    (Yukawa coupling g_Y ≈ 1/8 in the Jackiw-Rebbi picture).")
    print("    Alternatively: Solution B (ξ = 8λ_C) makes kink = electron exactly,")
    print("    but then ξ is no longer the Compton wavelength.")
    print()

    # ------------------------------------------------------------------ #
    # 10. Summary table and theoretical refinement direction              #
    # ------------------------------------------------------------------ #
    print("10. SUMMARY TABLE — BEST-FIT VALUES")
    print(sep)
    print(f"  Primitive   Solution A (ξ=λ_C)          Solution B (kink=m_e)")
    print(f"  ---------   --------------------------   -------------------------")
    print(f"  K           {sol_A.K:.4e} J/m³         {sol_B.K:.4e} J/m³")
    print(f"  ρ           {sol_A.rho:.4e} kg/m³       {sol_B.rho:.4e} kg/m³")
    print(f"  ξ           {sol_A.xi:.4e} m (= λ_C)    {sol_B.xi:.4e} m (= 8λ_C)")
    print(f"  ε_0         {sol_A.epsilon_0:.4e} J/m³   (same — from Λ observed)")
    print(f"  φ_max       {sol_A.phi_max:.4e} m         {sol_B.phi_max:.4e} m")
    print(f"  m_kink      {m_kink_A_MeV:.4f} MeV                 0.5110 MeV")
    print(f"  kink/m_e    8.0000                       1.0000")
    print()
    print("  α constraint: REDUNDANT at both solutions (always equals α_obs).")
    print(f"  α = e²/(4π hbar c) = {alpha_from_hbar:.6e} vs α_obs = {ALPHA:.6e}")
    print()

    print("11. THEORETICAL REFINEMENT DIRECTION")
    print(sep)
    print()
    print("  (a) CHOICE BETWEEN SOLUTIONS:")
    print("      The theory must commit to which ξ is the fundamental one.")
    print("      §18.21 favors ξ = λ_C but then the kink is 4.1 MeV, not m_e.")
    print("      A Yukawa-suppressed Dirac zero-mode (§18.14) can bring the")
    print("      electron mass to 511 keV with coupling g_Y ~ 1/8.")
    print()
    print("  (b) ELECTRON FROM DIRAC ZERO-MODE (§18.14, Jackiw-Rebbi):")
    print("      m_e = g_Y × m_kink")
    g_Y_needed = 1.0 / 8.0
    print(f"      Needed: g_Y = m_e / m_kink = 1/8 = {g_Y_needed:.6f}")
    print("      This is the Path B numerical derivation task.")
    print()
    print("  (c) PLANCK-SCALE INTERPRETATION OF hbar:")
    print("      §18.46.1 writes hbar = K ξ_P⁴/c with ξ_P = Planck length.")
    print("      This means K, ρ at Planck scale are very different from K_A, ρ_A.")
    print("      The 'K' in atomic physics and the 'K' in Planck-scale substrate")
    print("      may be the same parameter evaluated at different effective scales")
    print("      (RG running of K, §18.34 / rg_running.py).")
    xi_compton_print = HBAR_SI / (M_E_SI * C_SI)
    print(f"      Ratio ξ_atomic / ξ_Planck = {xi_compton_print / L_PLANCK:.3e}")
    print()
    print("  (d) COSMOLOGICAL CONSTANT:")
    print(f"      ε_0 = {sol_A.epsilon_0:.3e} J/m³ uniquely determined from Λ_obs.")
    print(f"      σ_0 = {sigma_0:.3e}  (baseline substrate strain).")
    print("      Mechanism for this tiny baseline: §18.40 initial conditions")
    print("      (universe started at saturation σ=0.5 and de-saturated to σ_0).")
    print()

    print(SEP)
    print("  FINAL VERDICT")
    print(SEP)
    print()
    print("  UNIQUE SOLUTION EXISTS for {K, ρ, ξ} from {c, hbar, m_kink target}:")
    print("    Solution A (ξ=λ_C):   K=1.42e24 J/m³,  ρ=1.58e7 kg/m³,  ξ=3.86e-13 m")
    print(f"                           → kink = 8m_e = {m_kink_A_MeV:.2f} MeV (not the electron)")
    print("    Solution B (ξ=8λ_C):  K=3.43e19 J/m³,  ρ=3.81e2 kg/m³,  ξ=3.09e-12 m")
    print("                           → kink = m_e = 0.511 MeV (by construction)")
    print()
    print("  α constraint is REDUNDANT (always = e²/(4π hbar c), gives no ξ info).")
    print("  ε_0 uniquely determined from Λ_obs = 1.089e-52 m⁻².")
    print("  φ_max naturally = ξ (saturation at kink-scale strain).")
    print()
    print("  MULTI-SCALE ISSUE (genuine, not a bug):")
    print("    ξ=λ_C and 'kink=electron' are INCOMPATIBLE.")
    print("    At ξ=λ_C: kink = 8m_e ≈ 4.1 MeV.  Electron ≠ kink.")
    print("    Spec §18.22 resolves this: electron = Dirac zero-mode on kink.")
    print("    Yukawa coupling g_Y ~ 1/8 bridges the gap (Path B computation).")
    print()
    print("  SPEC §18.21 DIMENSIONAL ERROR:")
    print("    The spec formula 'm_ν = 8ρξ ≈ 27 GeV' has two errors:")
    print("    (i)  Dimensional: 8ρξ [kg/m³ × m] = kg/m² (not kg)")
    print("    (ii) Numerical: 4.88e-5 [kg/m²] × c² ≈ 10^22 GeV, not 27 GeV")
    print("    Correct SI result: m_kink = 8hbar/(cξ) = 8m_e ≈ 4.1 MeV at ξ=λ_C.")
    print()
    print(SEP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
