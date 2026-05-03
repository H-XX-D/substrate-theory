"""Test substrate K(xi) running against heavy quark masses (charm, bottom, top).

Runs heavy_quark_masses.run_full_analysis() and prints the verdict.

Honest result: the single power-law K(xi) anchored at the electron Compton
scale and the QCD scale does NOT predict m_c, m_b, m_t through the
Nambu-Goto sqrt(sigma hbar c) mass formula.  The substrate framework
captures hadronic string tension and lepton Compton scales, but heavy-quark
current masses appear to require additional physics (Higgs-Yukawa, or a
regime change in K(xi) below xi_QCD).

Usage
-----
    python scripts/heavy_quark_masses_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make src/ importable when run directly
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from stiff_medium.heavy_quark_masses import (  # noqa: E402
    K_ELECTRON,
    K_QCD_TARGET,
    M_C_GEV,
    M_B_GEV,
    M_T_GEV,
    SIGMA_QCD_GEV2,
    XI_ELECTRON,
    XI_QCD,
    fit_running_exponent_a,
    run_full_analysis,
)


def _hr(width: int = 78, char: str = "-") -> str:
    """Horizontal rule string."""
    return char * width


def main() -> int:
    """Run the full heavy-quark mass test and print results.

    Returns:
        Exit code (0 = success).
    """
    print(_hr(78, "="))
    print("Substrate heavy-quark mass test")
    print(_hr(78, "="))
    print()

    print("ANCHORS:")
    print(f"  xi_e   = {XI_ELECTRON:.4e} m   (electron Compton)")
    print(f"  K_e    = {K_ELECTRON:.4e} Pa")
    print(f"  xi_QCD = {XI_QCD:.4e} m   (= 0.2 fm)")
    print(f"  K_QCD  = {K_QCD_TARGET:.4e} Pa  (so sigma = {SIGMA_QCD_GEV2:.3f} GeV^2)")
    print()

    a = fit_running_exponent_a()
    print(f"Fitted exponent a in K(xi) = K_e (xi_e/xi)^a:  a = {a:.6f}")
    print(f"  (Sign convention: a < 0 means K DECREASES toward small xi.)")
    print()

    print("HEAVY QUARK CURRENT MASSES (PDG 2024):")
    print(f"  m_c (MS-bar 2 GeV) = {M_C_GEV:.3f} GeV")
    print(f"  m_b (MS-bar)       = {M_B_GEV:.3f} GeV")
    print(f"  m_t (pole)         = {M_T_GEV:.1f}  GeV")
    print()

    summary = run_full_analysis()

    print(_hr(78, "-"))
    print("Per-quark substrate predictions")
    print(_hr(78, "-"))
    header = (
        f"{'q':>3} {'m_emp [GeV]':>12} {'xi_q [m]':>12}"
        f" {'K(xi_q) [Pa]':>14} {'sigma [GeV^2]':>14}"
        f" {'m_NG [GeV]':>12} {'m_NG/m_emp':>12}"
    )
    print(header)
    for p in summary.predictions:
        print(
            f"{p.name:>3} {p.m_emp_GeV:>12.3f} {p.xi_q:>12.3e}"
            f" {p.K_at_xi_q:>14.3e} {p.sigma_at_xi_q_GeV2:>14.3e}"
            f" {p.m_NG_GeV:>12.3e} {p.m_NG_over_m_emp:>12.3e}"
        )
    print()

    print(_hr(78, "-"))
    print("Implied 'fix' if running tracked observed heavy-quark masses")
    print(_hr(78, "-"))
    header2 = (
        f"{'q':>3} {'K_required [Pa]':>18} {'a_implied':>12}"
        f" {'sigma_ratio':>14}"
    )
    print(header2)
    for p in summary.predictions:
        print(
            f"{p.name:>3} {p.K_emp_required_Pa:>18.3e} {p.a_implied_emp:>12.3f}"
            f" {p.sigma_ratio_to_QCD:>14.3e}"
        )
    print()

    print(f"  b (log) needed to force charm:  {summary.b_log_to_charm:.4e}")
    print(f"  b (log) needed to force bottom: {summary.b_log_to_bottom:.4e}")
    if summary.b_log_to_charm * summary.b_log_to_bottom > 0 and abs(
        summary.b_log_to_charm / summary.b_log_to_bottom - 1.0
    ) < 0.5:
        print("  -> Log-running coefficients are CONSISTENT (within 50%).")
    else:
        print("  -> Log-running coefficients DIFFER strongly between c and b:")
        print("     a single new beta-function does NOT fix both simultaneously.")
    print()

    print(_hr(78, "="))
    print("HONEST ASSESSMENT")
    print(_hr(78, "="))
    for line in summary.notes:
        print(line)
    print()

    print(_hr(78, "="))
    print(f"VERDICT: {summary.verdict}")
    print(_hr(78, "="))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
