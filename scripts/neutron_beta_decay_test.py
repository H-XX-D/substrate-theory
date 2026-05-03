"""Free neutron beta decay — substrate-driven lifetime prediction (§18.75).

Computes Γ_n and τ_n from the substrate-predicted Δm_np = m_n − m_p and
the substrate kink mass m_e, plugging into the standard V-A formula

    Γ_n = (G_F² |V_ud|²)/(2 π³) × (1 + 3 g_A²) × m_e⁵ × f(ε₀).

Substrate inputs:
  * Δm_np = 1.293 MeV  (substrate, §18.63.3 / nucleon_mass_splitting.py)
  * m_e   = 0.511 MeV  (substrate kink-mass anchor)
  * Q     = Δm_np − m_e ≈ 0.782 MeV
  * g_A   = 5/3        (naïve SU(6) Y-junction substrate prediction)

Empirical inputs (collider / electroweak sector — §18.75 boundary):
  * G_F   = 1.1664×10⁻⁵ GeV⁻²
  * |V_ud| = 0.97373
  * g_A   = 1.2756  (alternate; for direct PDG comparison)
  * Sirlin-correction κ ≈ 1.0322 (radiative + Fermi function;
    f̃(ε₀) = κ · f(ε₀); reproduces textbook 1.6887 at empirical Δm)

Reports:
  (A) Substrate Δm + empirical g_A      → "best substrate" lifetime
  (B) Substrate Δm + SU(6) g_A = 5/3     → "all-substrate" lifetime
  (C) PDG Δm + empirical g_A             → sanity vs. textbook 884 s
  (D) Raw substrate Δm = 1.331 MeV       → without §18.63.3 EM correction

Empirical reference: τ_n = 879.4 ± 0.6 s (PDG 2024).
"""

from __future__ import annotations

from stiff_medium.neutron_beta_decay import (
    compute_all,
    phase_space_integral,
    G_A_EMPIRICAL,
    G_A_SU6,
    DELTA_M_NP_SUBSTRATE_MEV,
    DELTA_M_NP_EMPIRICAL_MEV,
    DELTA_M_NP_RAW_MEV,
    M_E_MEV,
    G_F_GEV2,
    V_UD,
    F_SIRLIN_CORRECTED_AT_EMP,
    KAPPA_SIRLIN,
    TAU_N_EMPIRICAL_S,
    TAU_N_UNCERTAINTY_S,
)


def banner(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def fmt_pct(x: float) -> str:
    sign = "+" if x >= 0 else "-"
    return f"{sign}{abs(x) * 100:.2f}%"


def report_one(label: str, res) -> None:
    print(f"  Variant: {label}")
    print(f"    Δm_np            = {res.delta_m_np_mev:.4f} MeV")
    print(f"    m_e              = {res.m_e_mev:.4f} MeV")
    print(f"    Q = Δm_np − m_e  = {res.Q_mev:.4f} MeV")
    print(f"    ε₀ = Δm_np / m_e = {res.epsilon_0:.4f}")
    print(f"    f_bare(ε₀)       = {res.f_bare:.4f}")
    print(f"    f̃ = κ · f_bare   = {res.f_corrected:.4f}   "
          f"(κ = {KAPPA_SIRLIN:.4f})")
    print(f"    g_A used         = {res.g_A_used:.4f}")
    print(f"    G_F              = {res.g_F_GeV_inv2:.4e} GeV⁻²")
    print(f"    |V_ud|           = {res.V_ud:.5f}")
    print(f"    Γ_n              = {res.gamma_inv_s:.4e}  s⁻¹")
    print(f"    τ_n predicted    = {res.tau_s:.2f}  s")
    print(f"    τ_n empirical    = {TAU_N_EMPIRICAL_S:.1f} ± "
          f"{TAU_N_UNCERTAINTY_S:.1f} s")
    print(f"    Fractional error = {fmt_pct(res.frac_error)}")
    print()


def main() -> None:
    banner("Free neutron beta decay — substrate prediction (§18.75)")
    print("Standard physics formula:")
    print("  Γ_n = (G_F² |V_ud|²)/(2π³) × (1 + 3 g_A²) × m_e⁵ × f(Q/m_e)")
    print()
    print("Substrate-anchored inputs:")
    print(f"  m_e                     = {M_E_MEV:.6f} MeV   (substrate)")
    print(f"  Δm_np  (§18.63.3)        = {DELTA_M_NP_SUBSTRATE_MEV:.4f} MeV "
          "(substrate, 2.9% prediction)")
    print(f"  Δm_np  (raw substrate)   = {DELTA_M_NP_RAW_MEV:.4f} MeV   "
          "(naïve substrate, no EM correction)")
    print()
    print("Empirical electroweak / CKM inputs (collider sector boundary):")
    print(f"  G_F                     = {G_F_GEV2:.4e} GeV⁻²")
    print(f"  |V_ud|                  = {V_UD:.5f}")
    print(f"  g_A (PDG empirical)     = {G_A_EMPIRICAL:.4f}")
    print(f"  g_A (substrate SU(6))   = {G_A_SU6:.4f} = 5/3")
    print(f"  f̃ at empirical Δm       = {F_SIRLIN_CORRECTED_AT_EMP:.4f}  "
          f"(textbook)")
    print(f"  Sirlin multiplicative κ = {KAPPA_SIRLIN:.4f}")

    banner("Phase-space integral f(ε₀) — closed-form check")
    eps0 = DELTA_M_NP_SUBSTRATE_MEV / M_E_MEV
    f_val = phase_space_integral(eps0)
    f_tilde = KAPPA_SIRLIN * f_val
    print(f"  ε₀                = {eps0:.4f}")
    print(f"  f(ε₀)  bare V-A   = {f_val:.4f}   (closed-form, 1/60 prefactor)")
    print(f"  f̃ = κ · f(ε₀)     = {f_tilde:.4f}   (κ = {KAPPA_SIRLIN:.4f})")
    print(f"  Sirlin uplift     = +{(KAPPA_SIRLIN - 1) * 100:.2f}%   "
          "(outer radiative + Fermi function)")

    all_res = compute_all()

    banner("(A)  Substrate Δm + empirical g_A — primary substrate prediction")
    report_one("substrate Δm = 1.293 MeV, empirical g_A = 1.2756",
               all_res.pred_substrate_emp_gA)

    banner("(B)  Substrate Δm + SU(6) g_A = 5/3 — clean substrate spin-flavour")
    report_one("substrate Δm = 1.293 MeV, SU(6) g_A = 5/3",
               all_res.pred_substrate_su6_gA)

    banner("(C)  PDG Δm + empirical g_A — V-A textbook sanity")
    report_one("Δm = 1.29333 MeV (PDG), empirical g_A",
               all_res.pred_pdg_inputs)

    banner("(D)  Raw substrate Δm (no EM correction) + empirical g_A")
    report_one("Δm = 1.331 MeV (raw §18.63.3), empirical g_A",
               all_res.pred_substrate_raw_dm)

    banner("SU(6) g_A — substrate prediction summary")
    su6 = all_res.su6
    print(f"  Substrate (SU(6))  g_A = {su6.g_A_su6:.4f}  (= 5/3)")
    print(f"  Empirical (PDG)    g_A = {su6.g_A_empirical:.4f}")
    print(f"  Quenching factor   = g_A_emp / g_A_su6 = "
          f"{su6.quenching_factor:.4f}")
    print(f"  SU(6) excess vs PDG = {fmt_pct(su6.relative_excess)}")
    print()
    print("  Interpretation: 5/3 is the naïve non-relativistic Y-junction")
    print("  spin-flavour algebra; the residual ~24% quenching is a")
    print("  known relativistic + pion-cloud correction not yet captured")
    print("  in the substrate framework (§18.30 vertex stress / cloud).")
    print()
    print("  In the rate Γ_n ∝ (1 + 3 g_A²):")
    A_factor = 1 + 3 * G_A_EMPIRICAL ** 2
    B_factor = 1 + 3 * G_A_SU6 ** 2
    print(f"    1 + 3 g_A²  (emp)   = {A_factor:.4f}")
    print(f"    1 + 3 g_A²  (SU(6)) = {B_factor:.4f}")
    print(f"    ratio (SU6 / emp)   = {B_factor / A_factor:.4f}")
    print(f"    so τ(SU6) / τ(emp)  = {A_factor / B_factor:.4f}")
    print(f"      (predicted: τ(SU6) ≈ {all_res.pred_substrate_su6_gA.tau_s:.1f} s,"
          f" τ(emp) ≈ {all_res.pred_substrate_emp_gA.tau_s:.1f} s)")

    banner("Verdict — neutron lifetime test (§18.75)")
    A_err = all_res.pred_substrate_emp_gA.frac_error
    B_err = all_res.pred_substrate_su6_gA.frac_error
    C_err = all_res.pred_pdg_inputs.frac_error
    D_err = all_res.pred_substrate_raw_dm.frac_error
    print(f"  τ_n empirical (PDG 2024)        = {TAU_N_EMPIRICAL_S} ± "
          f"{TAU_N_UNCERTAINTY_S} s")
    print()
    print("  Predictions:")
    print(f"   (A) substrate Δm + emp g_A     τ = "
          f"{all_res.pred_substrate_emp_gA.tau_s:7.2f} s   "
          f"({fmt_pct(A_err)})")
    print(f"   (B) substrate Δm + SU(6) g_A   τ = "
          f"{all_res.pred_substrate_su6_gA.tau_s:7.2f} s   "
          f"({fmt_pct(B_err)})")
    print(f"   (C) PDG Δm + emp g_A           τ = "
          f"{all_res.pred_pdg_inputs.tau_s:7.2f} s   "
          f"({fmt_pct(C_err)})")
    print(f"   (D) raw substrate Δm + emp g_A τ = "
          f"{all_res.pred_substrate_raw_dm.tau_s:7.2f} s   "
          f"({fmt_pct(D_err)})")
    print()
    if abs(A_err) < 0.05:
        print("  PASS:  substrate (Δm, m_e) + empirical (G_F, V_ud, g_A) reproduces"
              "\n         τ_n to within 5%.")
    else:
        print(f"  CHECK: substrate prediction error |{A_err*100:.2f}%| > 5%")
    print()
    print("  Honest scope (§18.75):")
    print("    • Δm_np and m_e come from the substrate (stable-matter domain).")
    print("    • G_F, V_ud are empirical electroweak inputs (collider sector).")
    print("    • g_A: substrate predicts the naïve 5/3 from SU(6); the residual"
          "\n      24% quenching is not yet captured (§18.30 open).")
    print("    • Net: with substrate Δm and empirical g_A, the lifetime"
          "\n      matches PDG to ~1%.  The substrate's contribution is the"
          "\n      Q-value, which appears as Γ ∝ Q⁵ × phase-space and is")
    print("      a stringent test (5× error amplification).")


if __name__ == "__main__":
    main()
