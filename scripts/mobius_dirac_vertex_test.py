"""Test driver: Möbius-Dirac vertex eigenvalues κ_n vs Foot parametrization.

Spec §18.30: leptons are excited states of an electron-kink with stress-loaded
vertex stiffness eigenvalues κ_n.  This script computes κ_n by solving the
Dirac equation on a 1D radial discretization of the 45° cone with Möbius
half-flux U(1) connection, sectored by Z₃ vertex symmetry.

We then compare the resulting m_n = √κ_n ratios to the Foot family
    m_n = M (1 + √2 cos(2πn/3 + δ))²
with empirical δ_emp ≈ 1.404π.

Run:
    PYTHONPATH=src python3 scripts/mobius_dirac_vertex_test.py
"""

from __future__ import annotations

import sys
import time

import numpy as np

from stiff_medium.mobius_dirac_vertex import (
    DELTA_EMP_PI,
    EMPIRICAL_RATIOS,
    M_E_MEV,
    M_FOOT_MEV,
    M_MU_MEV,
    M_TAU_MEV,
    compare_to_foot,
    run_mobius_dirac_vertex,
    solve_kappa_eigenvalues,
)


def _h(title: str) -> None:
    """Print a section header."""
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)


def _row(label: str, value, fmt: str = "") -> None:
    """Print a key-value row."""
    if fmt:
        print(f"  {label:<40}  {format(value, fmt)}")
    else:
        print(f"  {label:<40}  {value}")


def main() -> int:
    """Run the Möbius-Dirac vertex test and report."""
    print("=" * 76)
    print("Möbius-Dirac vertex eigenvalue test (spec §18.30)")
    print("=" * 76)
    print(
        "  Goal: solve 1D radial Dirac on a discrete 45° cone with Möbius\n"
        "  half-flux + Z₃ vertex closure.  Extract three κ eigenvalues and\n"
        "  compare m_n = √κ_n to the Foot parametrization.\n"
    )
    print(f"  Empirical Foot phase:      δ_emp/π = {DELTA_EMP_PI}")
    print(f"  Empirical Foot scale:      M_FOOT  = {M_FOOT_MEV} MeV")
    print(f"  Empirical (m_e, m_μ, m_τ): "
          f"({M_E_MEV} MeV, {M_MU_MEV} MeV, {M_TAU_MEV} MeV)")
    print(f"  Empirical ratios m/M_FOOT: "
          f"({EMPIRICAL_RATIOS[0]:.5f}, {EMPIRICAL_RATIOS[1]:.5f}, "
          f"{EMPIRICAL_RATIOS[2]:.5f})")

    # ------------------------------------------------------------------
    # Step 1: baseline run with default Z₃-sector labelling {−1, 0, +1}
    # ------------------------------------------------------------------
    _h("Step 1: baseline (z3_sector_offset = 0; m_z ∈ {-1, 0, +1})")

    t0 = time.time()
    result = run_mobius_dirac_vertex(
        N_radial=400,
        M_kink=1.0,
        xi=1.0,
        R_max=15.0,
        z3_sector_offset=0,
    )
    dt = time.time() - t0
    print(f"  Eigensolve time: {dt:.2f} s")

    k = result["kappa"]
    print()
    _row("Successful:", k.successful)
    _row("ℓ_eff per sector (sorted):", k.ell_eff)
    _row("Notes:", k.notes)
    _row("κ_0 (lowest):", k.kappa[0], ".6f")
    _row("κ_1 (middle):", k.kappa[1], ".6f")
    _row("κ_2 (highest):", k.kappa[2], ".6f")
    _row("E_n = √κ_n (sorted):", k.E)
    _row("Ratios κ_1/κ_0, κ_2/κ_0:",
         f"{k.kappa[1]/k.kappa[0]:.4f}, {k.kappa[2]/k.kappa[0]:.4f}")
    _row("Ratios E_1/E_0, E_2/E_0:",
         f"{k.E[1]/k.E[0]:.4f}, {k.E[2]/k.E[0]:.4f}")

    if k.successful and result["comparison"] is not None:
        c = result["comparison"]
        _h("Step 2: Foot fit to κ_n")
        _row("Best-fit δ (units of π):", c.delta_fit_pi, ".6f")
        _row("Best-fit M (natural units of √κ):", c.M_fit, ".6f")
        _row("|δ_fit − δ_emp| / π:", c.residual_delta_pi, ".6f")
        _row("Predicted (m_0, m_1, m_2)/M:", c.m_predicted_over_M)
        _row("Empirical (m_e, m_μ, m_τ)/M:", c.m_empirical_over_M)
        _row("Predicted m_μ/m_e:", c.ratio_mu_e_predicted, ".4f")
        _row("Target m_μ/m_e:", c.ratio_mu_e_target, ".4f")
        _row("Predicted m_τ/m_e:", c.ratio_tau_e_predicted, ".4f")
        _row("Target m_τ/m_e:", c.ratio_tau_e_target, ".4f")
        _row("Predicted Koide Q:", c.koide_q, ".6f")
        _row("Target Koide Q (= 2/3):", c.koide_target, ".6f")
        print()
        print("  VERDICT:")
        for line in c.verdict.split(". "):
            line = line.strip()
            if line:
                print(f"    {line}.")

    # ------------------------------------------------------------------
    # Step 3: try alternative Z₃ sector offsets to test robustness
    # ------------------------------------------------------------------
    _h("Step 3: scan z3_sector_offset (test robustness of δ_fit)")
    print()
    print(f"  {'offset':>6}  {'ℓ_eff vals':>20}  {'δ/π':>10}  "
          f"{'m1/m0':>10}  {'m2/m0':>10}  {'Q':>10}")
    print("  " + "-" * 74)
    for offset in (-2, -1, 0, 1, 2):
        try:
            r = run_mobius_dirac_vertex(
                N_radial=400, M_kink=1.0, xi=1.0, R_max=15.0,
                z3_sector_offset=offset,
            )
            kk = r["kappa"]
            cc = r["comparison"]
            if kk.successful and cc is not None and kk.kappa[0] > 0:
                m_pred = np.sort(np.sqrt(np.maximum(kk.kappa, 0)))
                if m_pred[0] > 0:
                    r10 = m_pred[1] / m_pred[0]
                    r20 = m_pred[2] / m_pred[0]
                else:
                    r10, r20 = float("nan"), float("nan")
                ell_str = ",".join(f"{x:+.1f}" for x in kk.ell_eff)
                print(f"  {offset:>6d}  {ell_str:>20}  "
                      f"{cc.delta_fit_pi:>10.4f}  "
                      f"{r10:>10.4f}  {r20:>10.4f}  {cc.koide_q:>10.4f}")
            else:
                print(f"  {offset:>6d}  --- failed: {kk.notes} ---")
        except Exception as exc:
            print(f"  {offset:>6d}  --- exception: {exc} ---")

    # ------------------------------------------------------------------
    # Step 4: scan M_kink (sets Dirac coupling; tests parameter sensitivity)
    # ------------------------------------------------------------------
    _h("Step 4: scan M_kink (Dirac coupling sensitivity)")
    print()
    print(f"  {'M_kink':>8}  {'κ_0':>12}  {'κ_1':>12}  {'κ_2':>12}  "
          f"{'δ/π':>10}  {'Q':>8}")
    print("  " + "-" * 70)
    for M in (0.5, 1.0, 2.0, 4.0, 8.0):
        try:
            r = run_mobius_dirac_vertex(
                N_radial=400, M_kink=M, xi=1.0, R_max=15.0 / M if M > 1 else 15.0,
                z3_sector_offset=0,
            )
            kk = r["kappa"]
            cc = r["comparison"]
            if kk.successful and cc is not None:
                print(f"  {M:>8.2f}  {kk.kappa[0]:>12.6f}  "
                      f"{kk.kappa[1]:>12.6f}  {kk.kappa[2]:>12.6f}  "
                      f"{cc.delta_fit_pi:>10.4f}  {cc.koide_q:>8.4f}")
            else:
                print(f"  {M:>8.2f}  --- failed: {kk.notes} ---")
        except Exception as exc:
            print(f"  {M:>8.2f}  --- exception: {exc} ---")

    # ------------------------------------------------------------------
    # Step 5: convergence test (vary N_radial)
    # ------------------------------------------------------------------
    _h("Step 5: convergence with N_radial")
    print()
    print(f"  {'N_radial':>10}  {'κ_0':>12}  {'κ_1':>12}  {'κ_2':>12}  "
          f"{'δ/π':>10}")
    print("  " + "-" * 60)
    for N in (100, 200, 400, 500):
        try:
            r = run_mobius_dirac_vertex(
                N_radial=N, M_kink=1.0, xi=1.0, R_max=15.0,
                z3_sector_offset=0,
            )
            kk = r["kappa"]
            cc = r["comparison"]
            if kk.successful and cc is not None:
                print(f"  {N:>10d}  {kk.kappa[0]:>12.6f}  "
                      f"{kk.kappa[1]:>12.6f}  {kk.kappa[2]:>12.6f}  "
                      f"{cc.delta_fit_pi:>10.4f}")
            else:
                print(f"  {N:>10d}  --- failed: {kk.notes} ---")
        except Exception as exc:
            print(f"  {N:>10d}  --- exception: {exc} ---")

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    _h("FINAL HONEST SUMMARY")

    if k.successful and result["comparison"] is not None:
        c = result["comparison"]
        if c.residual_delta_pi < 0.02:
            print(
                "  The minimal Möbius half-flux + Z₃ topology REPRODUCES the\n"
                f"  empirical Foot phase δ ≈ 1.404π (got {c.delta_fit_pi:.4f}π).\n"
                "  §18.30 is structurally complete for the lepton spectrum."
            )
        elif c.residual_delta_pi < 0.15:
            print(
                f"  The minimal topology gives δ_fit ≈ {c.delta_fit_pi:.4f}π,\n"
                f"  which is within {c.residual_delta_pi:.3f}π of empirical 1.404π.\n"
                "  Suggestive but not exact — additional model ingredients\n"
                "  (kink-profile-specific or curvature corrections) likely needed."
            )
        else:
            print(
                f"  The minimal topology gives δ_fit ≈ {c.delta_fit_pi:.4f}π,\n"
                f"  but empirical is 1.404π — a gap of {c.residual_delta_pi:.3f}π.\n"
                "\n"
                "  HONEST CONCLUSION: the Möbius half-flux + Z₃ topology alone\n"
                "  does not predict the empirical Foot phase.  The Z₃ vertex\n"
                "  fixes the structural form of three eigenvalues, and the\n"
                "  Möbius half-flux pushes ℓ_eff into the half-integer ladder\n"
                "  {-1/2, +1/2, +3/2}, but the resulting κ ratios are O(1) /\n"
                "  O(few) — far below the empirical (207, 3477).  This\n"
                "  matches the prior finding in lepton_derivation.py that\n"
                "  single-kink Dirac is bounded by ~√2.\n"
                "\n"
                "  What would need to be added (open questions for §18.30):\n"
                "  • A k-running stiffness model where κ_n ∝ (n+1)^k with\n"
                "    k ≈ 15 (already shown in foot_phase_derivation.py to\n"
                "    fit ratios but break Koide Q).\n"
                "  • A multi-vertex topology (e.g. baryon-Y junction) that\n"
                "    multiplies the centrifugal scale.\n"
                "  • Resolution of the kink-profile-specific factor that\n"
                "    sets the absolute scale of κ.\n"
                "\n"
                "  This is a NEGATIVE result for §18.30's claim of completeness\n"
                "  but a POSITIVE result for the spec's open-questions list:\n"
                "  the gap between minimal topology and empirical δ ≈ 1.404π\n"
                "  is now quantified."
            )
    else:
        print("  Eigensolver did not converge for all sectors.")
        print(f"  Notes: {k.notes}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
