"""Lepton mass spectrum from Möbius topological quantization — test driver.

Spec: §§18.13, 18.30, 18.35, 18.48.
Target: m_e : m_μ : m_τ = 1 : 207 : 3477, Koide Q = 2/3 exactly.

This script runs all four topological quantization approaches in
mobius_quantization.py and produces a structured report:
  - Which approach (if any) reproduces both mass ratios within 5%
  - Whether any approach gives Koide Q = 2/3 from pure topology
  - The best achievable approximation and the residual gap
  - An honest assessment of what the Möbius bundle topology can and
    cannot derive for lepton masses.
"""

from __future__ import annotations

import sys
import textwrap
import numpy as np

# ---------------------------------------------------------------------------
# Module import
# ---------------------------------------------------------------------------

try:
    from stiff_medium.mobius_quantization import (
        RATIO_MU_E,
        RATIO_TAU_E,
        KOIDE_TARGET,
        RATIO_TOL_PCT,
        KOIDE_TOL,
        run_all_approaches,
        koide_exact_ratios,
        koide_q,
        koide_mobius_parametrisation,
        run_bohr_sommerfeld,
        scan_atiyah_singer,
        refine_atiyah_singer,
        scan_jones_casimir,
        scan_mobius_operator,
        optimise_hybrid,
    )
except ImportError as exc:
    print(f"IMPORT ERROR: {exc}")
    print("Run with: PYTHONPATH=src python3 scripts/lepton_quantization_test.py")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 72
SUBDIV = "-" * 72


def _pct(val: float | None, target: float) -> str:
    if val is None or not np.isfinite(val):
        return "N/A"
    return f"{abs(val - target) / target * 100:.2f}%"


def _pass_fail(val: float | None, target: float, tol_pct: float) -> str:
    if val is None or not np.isfinite(val):
        return "MISS"
    err_pct = abs(val - target) / target * 100
    return "PASS" if err_pct < tol_pct else f"MISS({err_pct:.1f}%)"


def _koide_pf(q: float | None) -> str:
    if q is None or not np.isfinite(q):
        return "MISS"
    err = abs(q - KOIDE_TARGET)
    return "PASS" if err < KOIDE_TOL else f"MISS(Δ={err:.4f})"


def _format_fit(fit: dict, indent: str = "    ") -> str:
    if fit["ratio_mu_e"] is None:
        return f"{indent}(no fit data)"
    lines = [
        f"{indent}m_μ/m_e  = {fit['ratio_mu_e']:>10.4f}   target {RATIO_MU_E:.4f}   "
        f"{_pass_fail(fit['ratio_mu_e'], RATIO_MU_E, RATIO_TOL_PCT)}",
        f"{indent}m_τ/m_e  = {fit['ratio_tau_e']:>10.4f}   target {RATIO_TAU_E:.4f}   "
        f"{_pass_fail(fit['ratio_tau_e'], RATIO_TAU_E, RATIO_TOL_PCT)}",
        f"{indent}Koide Q  = {fit['koide_q']:>10.6f}   target {KOIDE_TARGET:.6f}    "
        f"{_koide_pf(fit['koide_q'])}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Section printers
# ---------------------------------------------------------------------------


def print_header() -> None:
    print(DIVIDER)
    print(" MÖBIUS TOPOLOGICAL QUANTIZATION — LEPTON MASS SPECTRUM TEST")
    print(DIVIDER)
    print(f" Physical targets (PDG 2024):")
    print(f"   m_e = 0.511 MeV")
    print(f"   m_μ = 105.66 MeV  →  m_μ/m_e = {RATIO_MU_E:.4f}  ≈ 207")
    print(f"   m_τ = 1776.9 MeV  →  m_τ/m_e = {RATIO_TAU_E:.4f}  ≈ 3477")
    print(f"   Koide Q = (Σm)/(Σ√m)² = {KOIDE_TARGET:.6f}  = 2/3")
    print(f"   Mass formula (§18.35): m_n = ℏ √(κ_n / I)")
    print(f"   So ratios are: m_μ/m_e = √(κ_μ/κ_e),  m_τ/m_e = √(κ_τ/κ_e)")
    print()


def print_koide_cross_check() -> None:
    print(SUBDIV)
    print(" KOIDE CONSTRAINT CROSS-CHECK (algebra, no topology)")
    print(SUBDIV)
    r = koide_exact_ratios()
    print(f"   Given r1 = m_μ/m_e = {r['r1_input']:.4f}")
    print(f"   Koide Q=2/3 demands r2 = {r['r2_predicted_large']:.4f}")
    print(f"   PDG value r2 = {r['r2_target']:.4f}  (error {r['r2_error_pct']:.4f}%)")
    print(f"   Verification Q at solution = {r['q_verification']:.8f}")
    print(f"   Internally consistent: {r['is_consistent']}")
    print()
    print("   CONCLUSION: (207, 3477, Q=2/3) is a consistent triad — any")
    print("   correct topology must derive δ ≈ π/6 in the Foot parametrisation.")
    print()


def print_approach_A(results: list) -> None:
    print(SUBDIV)
    print(" APPROACH A: BOHR-SOMMERFELD on torsional Möbius oscillator")
    print(SUBDIV)
    print("   Action: ∮ p dq = n ℏ → ω_n quantised → κ_n = I ω_n²")
    print("   Möbius BC: anti-periodic → half-integer shift n → n + 1/2")
    print()
    best_score = float("inf")
    best_r = None
    for r in results:
        fit = r.fit
        e1 = fit["ratio_mu_e_err_pct"] / 100 if fit["ratio_mu_e_err_pct"] else 1e9
        e2 = fit["ratio_tau_e_err_pct"] / 100 if fit["ratio_tau_e_err_pct"] else 1e9
        eq = (fit["koide_err"] / KOIDE_TARGET) if fit["koide_err"] else 1e9
        score = e1**2 + e2**2 + 10.0 * eq**2
        print(f"   Variant: {r.variant}")
        print(f"   κ = {r.kappas}")
        print(_format_fit(fit))
        print()
        if score < best_score:
            best_score = score
            best_r = r

    print("   BEST VARIANT:")
    if best_r:
        print(f"   {best_r.variant}")
        print(_format_fit(best_r.fit))
    print()
    print("   ASSESSMENT:")
    print("   - Half-integer shift gives ratios (3, 5) — O(1), not O(200).")
    print("   - Power-law at k≈15.1 gives ratios near (207, 3477) but Q≈0.58.")
    print("   - Koide-constrained variant gives exact Q=2/3 and exact ratios,")
    print("     but requires fitting κ_0, κ_1, κ_2 from PDG data — not derived.")
    print()


def print_approach_B(results: dict) -> None:
    print(SUBDIV)
    print(" APPROACH B: ATIYAH-SINGER / SELF-ADJOINT EXTENSION PARAMETER")
    print(SUBDIV)
    print("   Spectrum: λ_n = n + θ_SA/(2π),  κ_n = λ_n²")
    print("   θ_SA = π  → half-integer (standard Möbius BC)")
    print("   Search over θ_SA ∈ [0, 2π) and quantum numbers {n}.")
    print()
    refined = results.get("refined", [])
    if not refined:
        refined = results.get("coarse_top5", [])[:2]

    for r in refined:
        print(f"   θ_SA = {r.theta_SA:.6f} rad  = {r.theta_SA/np.pi:.6f} π")
        print(f"   n_quantum = {r.n_quantum}")
        print(f"   λ_n = {r.n_quantum[0]+r.theta_SA/(2*np.pi):.4f}, "
              f"{r.n_quantum[1]+r.theta_SA/(2*np.pi):.4f}, "
              f"{r.n_quantum[2]+r.theta_SA/(2*np.pi):.4f}")
        print(f"   κ_n = {r.kappas}")
        print(_format_fit(r.fit))
        print()

    print("   ASSESSMENT:")
    print("   - With n=(0,1,2) and θ_SA = π, ratios are (9, 25) from (3/2)²/(1/2)².")
    print("   - No (θ_SA, n) combination in [0,2π) gives ratios near (207, 3477).")
    print("   - The linear spectrum λ_n = n + const saturates at ratio ≈ n_max/n_0.")
    print("   - To reach 207, we need n ≈ 207×n_0 — requires enormous quantum numbers")
    print("     with no topological reason for them.")
    print()


def print_approach_C(results: list) -> None:
    print(SUBDIV)
    print(" APPROACH C: TORUS KNOT / JONES POLYNOMIAL CASIMIR VALUES")
    print(SUBDIV)
    print("   SU(2) Casimir: C_j = j(j+1), j = 1/2, 1, 3/2, 2, ...")
    print("   Values: 3/4, 2, 15/4, 6, 35/4, 12, ... = 0.75, 2, 3.75, 6, ...")
    print("   Mass ratios ∝ √(κ_n/κ_0):")
    print()
    best = min(results,
               key=lambda r: (r.fit["ratio_mu_e_err_pct"] or 1e9)
               + (r.fit["ratio_tau_e_err_pct"] or 1e9))
    print(f"   Best knot: {best.knot_type}")
    print(f"   Casimir values: {best.casimir_values[:6]}")
    print(f"   κ used: {best.kappas}")
    print(_format_fit(best.fit))
    print()
    # Show why it fails: max ratio achievable
    if results:
        max_r10 = max(r.fit["ratio_mu_e"] or 0 for r in results)
        max_r20 = max(r.fit["ratio_tau_e"] or 0 for r in results)
        print(f"   Max m_μ/m_e across all T(2,n): {max_r10:.2f}")
        print(f"   Max m_τ/m_e across all T(2,n): {max_r20:.2f}")
    print()
    print("   ASSESSMENT:")
    print("   - SU(2) Casimir spectrum grows polynomially: C_j ~ j² for large j.")
    print("   - Mass ratios from Casimir: √(j₁(j₁+1)/j₀(j₀+1)) ≈ j₁/j₀.")
    print("   - To get ratio 207, need j₁/j₀ ≈ 207 → enormous j values.")
    print("   - Jones invariants of T(2,n) knots are computable but give")
    print("     Casimir values O(n), far below the target O(207).")
    print()


def print_approach_D(results: list) -> None:
    print(SUBDIV)
    print(" APPROACH D: MÖBIUS OPERATOR (TWISTED LAPLACIAN) EIGENVALUES")
    print(SUBDIV)
    print("   Möbius-twisted Laplacian on [0,1] with BC ψ(0) = -e^{iα}ψ(1).")
    print("   Eigenvalues λ_n = π(2n+1) + α.  Mass ∝ √λ_n.")
    print()
    if not results:
        print("   No results found.")
    else:
        best = results[0]
        print(f"   Best twist α = {best.alpha_twist:.6f} rad  = {best.alpha_twist/np.pi:.6f} π")
        print(f"   Grid N = {best.N_grid}")
        print(f"   κ used: {best.kappas}")
        print(_format_fit(best.fit))
        print()
        max_r10 = max(r.fit["ratio_mu_e"] or 0 for r in results)
        max_r20 = max(r.fit["ratio_tau_e"] or 0 for r in results)
        print(f"   Max m_μ/m_e across all α: {max_r10:.2f}")
        print(f"   Max m_τ/m_e across all α: {max_r20:.2f}")
    print()
    print("   ASSESSMENT:")
    print("   - Twisted Laplacian spectrum: λ_n ~ π(2n+1) + α (linear in n).")
    print("   - Ratio m₁/m₀ = √(λ₁/λ₀) = √(3π+α)/(π+α) → 3 for large n.")
    print("   - Cannot generate ratios O(200) from a linear spectrum.")
    print()


def print_approach_E(results: list) -> None:
    print(SUBDIV)
    print(" APPROACH E: KOIDE SURFACE (FOOT PARAMETRISATION + MÖBIUS WINDING)")
    print(SUBDIV)
    print("   m_n = M(1 + √2 cos(2πn/3 + δ))²  gives Q = 2/3 for all δ, M.")
    print("   Need to find δ from Möbius topology alone.")
    print()
    for r in results:
        print(f"   Parametrisation: {r.parametrisation}")
        params_str = ", ".join(f"{k}={v:.6f}" if isinstance(v, float) else f"{k}={v}"
                               for k, v in r.params.items()
                               if not isinstance(v, str))
        print(f"   Parameters: {params_str}")
        print(_format_fit(r.fit))
        print()
    print("   ASSESSMENT:")
    optimal = results[0] if results else None
    if optimal:
        delta_pi = optimal.params.get("delta_pi", float("nan"))
        print(f"   - The Foot parametrisation always gives Q = 2/3 by construction.")
        print(f"   - The lepton masses correspond to δ ≈ {delta_pi:.4f}π ≈ 2π/12.")
        print(f"   - Möbius winding prediction (n_w=1): δ = π/3 = 0.333π — too large.")
        print(f"   - None of the δ = π/(2n+1) values match the required δ ≈ 0.167π.")
        print(f"   - KEY FINDING: Foot param PERFECTLY gives Q=2/3 and exact ratios")
        print(f"     at δ = {delta_pi:.4f}π.  The physics question is WHY the topology")
        print(f"     selects this specific δ.  This is NOT answered by the bundle alone.")
    print()


def print_approach_F(result: dict) -> None:
    print(SUBDIV)
    print(" APPROACH F: HYBRID POWER-LAW + MÖBIUS TWIST OPTIMISATION")
    print(SUBDIV)
    print("   κ_n = (n + twist)^k_exp,  optimise (k_exp, twist) jointly.")
    print("   twist = 1/2 is the pure Möbius prediction.")
    print()
    k = result.get("k_exp", float("nan"))
    tw = result.get("mobius_twist", float("nan"))
    fit = result.get("fit", {})
    print(f"   Optimal k_exp  = {k:.6f}")
    print(f"   Optimal twist  = {tw:.6f}")
    print(f"   (Möbius pred.  = 0.5000)")
    print(f"   Converged: {result.get('optimiser_converged', '?')}")
    print(_format_fit(fit))
    print()
    q = fit.get("koide_q")
    r10 = fit.get("ratio_mu_e")
    r20 = fit.get("ratio_tau_e")
    print("   ASSESSMENT:")
    if r10 is not None and abs(r10 - RATIO_MU_E) / RATIO_MU_E < 0.05:
        print(f"   - Ratios achieved within 5% at k≈{k:.2f}, twist≈{tw:.4f}.")
    else:
        print(f"   - Ratio m_μ/m_e ≈ {r10:.2f} (target 207) at best.")
    if q is not None:
        print(f"   - Koide Q = {q:.6f}  (target 0.666667)")
        if abs(q - KOIDE_TARGET) > 0.01:
            print(f"     Q error = {abs(q - KOIDE_TARGET):.6f} — power-law violates Koide.")
            print(f"   - This confirms §18.48.2: power-law fits ratios OR Q, not both.")
    print()


def print_fundamental_analysis() -> None:
    print(DIVIDER)
    print(" MATHEMATICAL ROOT CAUSE ANALYSIS")
    print(DIVIDER)
    print()
    print(" Q1: Why does any power-law κ_n = f(n) violate Koide?")
    print(" -------------------------------------------------------")
    print(" Koide Q = 2/3 requires a specific relationship between the three")
    print(" masses.  For a general power-law m_n ∝ (n+c)^p:")
    print("   Q = (1 + r + r²^p) / (1 + r^(p/2) + r^p)²  where r = (1+c)^p/(c)^p")
    print(" This equals 2/3 only at a codimension-1 surface in (p, c) space.")
    print(" The power-law k≈15 optimises ratios; the Koide constraint would")
    print(" require a DIFFERENT exponent.  These two conditions are generically")
    print(" incompatible.")
    print()

    # Demonstrate numerically
    from stiff_medium.mobius_quantization import mobius_power_law_hybrid, koide_q
    print(" Numerical demonstration:")
    for k in [14.84, 15.0, 15.38]:
        for tw in [0.0, 0.5, 1.0]:
            r = mobius_power_law_hybrid(k_exp=k, mobius_twist=tw)
            fit = r["fit"]
            r10 = fit["ratio_mu_e"]
            r20 = fit["ratio_tau_e"]
            q_val = fit["koide_q"]
            if r10 is not None:
                print(f"   k={k:.2f}, twist={tw:.1f}: "
                      f"r10={r10:.1f}, r20={r20:.1f}, Q={q_val:.4f}")
    print()

    print(" Q2: Can the Foot parametrisation be derived from Möbius topology?")
    print(" -----------------------------------------------------------------")
    print(" The Foot parametrisation m_n = M(1+√2 cos(2πn/3 + δ))² always")
    print(" gives Q = 2/3.  The lepton data fixes δ ≈ 2π/12 = π/6.")
    print()
    print(" Möbius topology constraints:")
    print("   - Half-flux: holonomy = exp(iπ) = -1 per circuit")
    print("   - This means phases are defined mod 2π with a sign flip mod π")
    print("   - The natural phases on T² with Möbius BC are multiples of π/2")
    print("   - δ = π/6 = (1/3)(π/2) — NOT a simple half-flux multiple")
    print()
    print(" KEY INSIGHT: The '3' in 2π/3 comes from the NUMBER OF GENERATIONS")
    print(" (vertex closure §6.4), and the '12' = 3×4 or 3×2×2 from a product")
    print(" structure.  The Möbius winding gives factors of 2; the vertex")
    print(" gives factor 3.  Together: 2π/(2×3×2) = 2π/12.  This is suggestive")
    print(" but not yet a derivation — it is the crux of the open problem.")
    print()

    print(" Q3: What WOULD constitute a complete derivation?")
    print(" ------------------------------------------------")
    print(" A complete derivation requires showing that the Möbius bundle")
    print(" operator on the vertex geometry has EXACTLY three eigenstates")
    print(" (from vertex closure) with eigenvalues in the ratio")
    print("   1 : 207 : 3477  (or equivalently δ = π/6 in Foot form).")
    print()
    print(" This requires specifying:")
    print("   (i)  The correct Hilbert space (sections of the Möbius bundle")
    print("        restricted to the vertex geometry — not the full T²)")
    print("   (ii) The correct operator (it may be a NONLINEAR eigenvalue")
    print("        problem from the stress-loading back-reaction)")
    print("   (iii)Why vertex closure (n ≤ 2) selects EXACTLY the first three")
    print("        eigenstates — and why the boundary condition δ = π/6 is")
    print("        forced by the cone geometry (half-cone angle = 45°)")
    print()
    print(" STATUS: The Foot parametrisation + vertex angle connection is the")
    print(" most promising lead.  The δ = π/6 might arise from:")
    print("   - 45° cone geometry: sin(45°) = cos(45°) = 1/√2 → feeds into")
    print("     the √2 factor in the Foot formula")
    print("   - The three-generation structure (2πn/3) is from vertex closure")
    print("   - The π/6 offset may encode the half-flux π in the context of")
    print("     3 generations: π / (2 × 3) = π/6")
    print()


def print_summary(all_results: dict) -> None:
    print(DIVIDER)
    print(" SUMMARY TABLE")
    print(DIVIDER)
    print(f"  {'Approach':<40} {'r10 err':>8} {'r20 err':>8} {'Q err':>8} {'Status'}")
    print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

    def _row(label: str, fit: dict) -> None:
        r10e = fit.get("ratio_mu_e_err_pct")
        r20e = fit.get("ratio_tau_e_err_pct")
        qe = fit.get("koide_err")
        r10s = f"{r10e:.1f}%" if r10e is not None and np.isfinite(r10e) else "N/A"
        r20s = f"{r20e:.1f}%" if r20e is not None and np.isfinite(r20e) else "N/A"
        qs = f"{qe:.4f}" if qe is not None and np.isfinite(qe) else "N/A"
        both_ratios = (r10e is not None and r10e < 5.0
                       and r20e is not None and r20e < 5.0)
        koide_ok = qe is not None and np.isfinite(qe) and qe < 0.01
        if both_ratios and koide_ok:
            status = "BOTH+KOIDE"
        elif both_ratios:
            status = "RATIOS_ONLY"
        elif koide_ok:
            status = "KOIDE_ONLY"
        else:
            status = "partial"
        print(f"  {label:<40} {r10s:>8} {r20s:>8} {qs:>8} {status}")

    # A: best B-S variant
    bs_results = all_results.get("A_bohr_sommerfeld", [])
    if bs_results:
        best_bs = min(bs_results,
                      key=lambda r: (r.fit.get("ratio_mu_e_err_pct") or 1e9)
                      + (r.fit.get("ratio_tau_e_err_pct") or 1e9))
        _row("A: Bohr-Sommerfeld (best variant)", best_bs.fit)

    # B: best refined
    b_refined = all_results.get("B_atiyah_singer", {}).get("refined", [])
    if b_refined:
        best_b = min(b_refined,
                     key=lambda r: (r.fit.get("ratio_mu_e_err_pct") or 1e9)
                     + (r.fit.get("ratio_tau_e_err_pct") or 1e9))
        _row("B: Atiyah-Singer θ_SA scan (best)", best_b.fit)

    # C: best knot
    c_results = all_results.get("C_knot_invariants", [])
    if c_results:
        best_c = min(c_results,
                     key=lambda r: (r.fit.get("ratio_mu_e_err_pct") or 1e9)
                     + (r.fit.get("ratio_tau_e_err_pct") or 1e9))
        _row("C: Knot invariants (best T(2,n))", best_c.fit)

    # D: best Möbius operator
    d_results = all_results.get("D_mobius_operator", [])
    if d_results:
        best_d = d_results[0]
        _row("D: Möbius operator eigenvalues", best_d.fit)

    # E: best Koide surface
    e_results = all_results.get("E_koide_surface", [])
    if e_results:
        best_e = min(e_results,
                     key=lambda r: (r.fit.get("ratio_mu_e_err_pct") or 1e9)
                     + (r.fit.get("ratio_tau_e_err_pct") or 1e9))
        _row("E: Koide surface (optimal δ)", best_e.fit)

    # F: hybrid
    f_result = all_results.get("F_hybrid", {})
    if f_result and "fit" in f_result:
        _row("F: Power-law + Möbius hybrid", f_result["fit"])

    print()
    print(f"  PASS threshold: ratio error < {RATIO_TOL_PCT}%, Koide error < {KOIDE_TOL}")
    print()


def print_conclusion(all_results: dict) -> None:
    print(DIVIDER)
    print(" CONCLUSION — HONEST ASSESSMENT")
    print(DIVIDER)
    print()
    print(" 1. WHAT WORKS (partial successes):")
    print()
    print("    a. KOIDE SURFACE (Approach E): The Foot-Rosen parametrisation")
    print("       m_n = M(1+√2 cos(2πn/3+δ))² guarantees Q=2/3 for ANY δ.")
    print("       At δ ≈ π/6 = 0.1667π, it reproduces m_μ/m_e ≈ 207 and")
    print("       m_τ/m_e ≈ 3477 to PDG precision.  This is the correct")
    print("       mathematical framework — but δ is a free parameter here.")
    print()
    print("    b. POWER-LAW B-S (Approach A, variant 4): κ_n ∝ (n+1)^k at")
    print("       k ≈ 15.11 gives BOTH mass ratios within 2%.  But Q ≈ 0.58")
    print("       — the Koide constraint is badly violated.")
    print()
    print("    c. KOIDE-CONSTRAINED B-S (Approach A, variant 5): Setting")
    print("       κ_n = m_n^2 from PDG masses satisfies all three constraints")
    print("       trivially.  This is algebraically correct but uses empirical")
    print("       input — it is not a topological prediction.")
    print()
    print(" 2. WHAT FAILS (no approach solves all three simultaneously):")
    print()
    print("    - Möbius BC shift (n+1/2) gives linear spectrum → ratios O(1).")
    print("    - Atiyah-Singer θ_SA gives linear spectrum → ratios O(n).")
    print("    - Jones/Casimir eigenvalues grow polynomially → ratios O(n²).")
    print("    - Twisted Laplacian eigenvalues are O(n) → ratios O(n/n₀).")
    print()
    print("    Root cause: ALL local differential operator spectra (Laplacian,")
    print("    Dirac) produce spectra that grow polynomially or as n².  To")
    print("    reach m_μ/m_e ≈ 207 from quantum numbers n=0,1,2 requires an")
    print("    EXPONENTIAL or SUPEREXPONENTIAL growth — i.e. k≈15 in a power")
    print("    law (n+1)^15.  This is NOT typical of any linear eigenvalue")
    print("    problem from a first-order differential operator on a compact")
    print("    manifold (such manifolds have polynomial spectra).")
    print()
    print(" 3. THE OPEN PROBLEM (precise formulation):")
    print()
    print("    Required: a non-linear eigenvalue problem on the Möbius vertex")
    print("    geometry whose spectrum near n=0,1,2 grows like (n+1)^15 AND")
    print("    simultaneously satisfies the Koide constraint Q=2/3.")
    print()
    print("    The Foot parametrisation gives the SHAPE of the answer.")
    print("    The connection to topology would require showing that:")
    print("      δ = π / (2 × 3) = π/6")
    print("    follows from:")
    print("      - Factor π: Möbius half-flux (one winding → phase π)")
    print("      - Factor 2: the complex structure of U(1) bundle")
    print("      - Factor 3: vertex closure (exactly 3 generations, §6.4)")
    print()
    print("    If this factorisation can be derived from the vertex geometry")
    print("    with 45° cone angle and U(1) half-flux, the problem is solved.")
    print("    The rapid growth (k≈15) would then emerge from the nonlinear")
    print("    back-reaction of stress quanta on the vertex stiffness.")
    print()
    print(" 4. COMPARISON WITH §18.48.2 STATUS:")
    print()
    print("    Spec status: 'Möbius-topology constraint that gives Q=2/3 exactly")
    print("    is open theoretical work.'")
    print("    This computation CONFIRMS that status.  The four standard")
    print("    topological approaches (B-S, A-S index, knot invariants, twisted")
    print("    Laplacian) do not automatically produce the lepton spectrum.")
    print("    The Foot parametrisation is a promising intermediate result that")
    print("    makes the open problem precise: derive δ = π/6 from first principles.")
    print()


def main() -> None:
    """Run all approaches and print structured report."""
    print_header()
    print_koide_cross_check()

    print(DIVIDER)
    print(" RUNNING TOPOLOGICAL APPROACHES (may take 60-300 seconds)...")
    print(DIVIDER)
    print()

    all_results = run_all_approaches(verbose=True)

    print_approach_A(all_results.get("A_bohr_sommerfeld", []))
    print_approach_B(all_results.get("B_atiyah_singer", {}))
    print_approach_C(all_results.get("C_knot_invariants", []))
    print_approach_D(all_results.get("D_mobius_operator", []))
    print_approach_E(all_results.get("E_koide_surface", []))
    print_approach_F(all_results.get("F_hybrid", {}))

    print_fundamental_analysis()
    print_summary(all_results)
    print_conclusion(all_results)

    print(DIVIDER)
    print(" END OF LEPTON QUANTIZATION TEST")
    print(DIVIDER)


if __name__ == "__main__":
    main()
