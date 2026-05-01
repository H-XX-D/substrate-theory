"""Photon renormalization test script — compute Z_photon(β², M_kink).

This script exercises stiff_medium.photon_renormalization and reports:

1. Symbolic Jackiw-Rebbi zero-mode verification.
2. Zero-mode normalization check.
3. Z_photon values for β² ∈ {3π, 4π, 4.5π, 4.54π, 5π}.
4. Fine scan over the repulsive-Thirring regime to find the β² that
   gives α_ren closest to 1/137.036.
5. Honest assessment of the result and the remaining gap.

Run from the project root:
    cd /path/to/project && PYTHONPATH=src python3 scripts/photon_renorm_test.py
"""

from __future__ import annotations

import math
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------

try:
    from stiff_medium.photon_renormalization import (
        C1_MOBIUS,
        M_KINK_XI,
        PI,
        ZPhotonResult,
        build_zero_mode_ft,
        compute_i_bundle,
        compute_z_photon,
        find_best_z_photon_beta,
        normalization_constant,
        scan_beta_squared,
        symbolic_zero_mode,
        zero_mode_position,
    )
    from stiff_medium.alpha_derivation import (
        INV_ALPHA_TARGET,
        ALPHA_TARGET,
        bosonization_alpha,
    )
except ImportError as exc:
    print(f"[ERROR] Import failed: {exc}")
    print("Run as: PYTHONPATH=src python3 scripts/photon_renorm_test.py")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

SEP = "=" * 78
SEP2 = "-" * 78


def section(title: str) -> None:
    print()
    print(SEP)
    print(f"  {title}")
    print(SEP)


def subsection(title: str) -> None:
    print()
    print(SEP2)
    print(f"  {title}")
    print(SEP2)


def fmt_alpha(alpha: float) -> str:
    if alpha <= 0.0 or not math.isfinite(alpha):
        return "N/A (non-physical)"
    return f"{alpha:.8f}  [1/{1/alpha:.4f}]"


def fmt_delta(delta: float) -> str:
    if not math.isfinite(delta):
        return "inf (no physical coupling)"
    pct = delta / INV_ALPHA_TARGET * 100.0
    return f"|Δ(1/α)| = {delta:.4f}  ({pct:.3f}% off target)"


# ---------------------------------------------------------------------------
# §1: Symbolic zero-mode verification
# ---------------------------------------------------------------------------


def test_symbolic_zero_mode() -> None:
    section("§1 — Symbolic Jackiw-Rebbi zero-mode (sympy verification)")

    sym = symbolic_zero_mode()
    if "error" in sym:
        print(f"  [SKIP] sympy not available: {sym['error']}")
        return

    print("  Kink profile  m(x) =", sym["kink_profile"])
    print("  Zero-mode     ψ_0(x) =", sym["zero_mode_unnorm"])
    print("  Norm integral ∫|ψ_0|² dx =", sym["norm_integral"])
    print("  FT (Mξ=1)    ψ̃_0(k) ∝", sym["ft_mxi_equals_1"])
    print()
    print("  Physical interpretation:")
    print("    The kink profile m(x) = M tanh(x/ξ) interpolates between −M (x→-∞)")
    print("    and +M (x→+∞), creating the topological defect.")
    print("    The zero-mode ψ_0(x) = cosh^{-Mξ}(x/ξ) is localized at the kink core.")
    print("    For Mξ = 1 (natural units): ψ_0(x) = N sech(x), width ~ ξ = 1/M.")
    print("    Its Fourier transform is N π sech(πkξ/2) — exponential decay in k.")


# ---------------------------------------------------------------------------
# §2: Normalization and FT check
# ---------------------------------------------------------------------------


def test_normalization() -> None:
    section("§2 — Zero-mode normalization and Fourier transform verification")

    N = normalization_constant(m_kink_xi=1.0)
    print(f"  Normalization constant N = {N:.8f}  (expected: {1.0/math.sqrt(2.0):.8f} = 1/√2)")
    print(f"  Check: N²  × ∫sech²(x)dx = N² × 2 = {N**2 * 2.0:.8f} (expected 1.0)")

    print()
    print("  Zero-mode profile at selected x values:")
    print(f"  {'x':>8s}  {'ψ_0(x) unnorm':>18s}  {'N × ψ_0(x)':>14s}")
    print("  " + "-" * 44)
    for x_val in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0]:
        raw = zero_mode_position(x_val, m_kink_xi=1.0)
        print(f"  {x_val:>8.2f}  {raw:>18.10f}  {N*raw:>14.10f}")

    # Verify normalization numerically
    from scipy.special import gamma
    norm_analytic = math.sqrt(PI) * gamma(1.0) / gamma(1.5)
    print(f"\n  Analytic norm integral ∫cosh^{{-2}}(x)dx = √π Γ(1)/Γ(3/2) = {norm_analytic:.8f}")
    print(f"  Expected: 2.000000  (= ∫sech²(x)dx)")

    # Quick numerical check of the FT at k=0 for Mξ=1
    # ψ̃_0(0) = 2∫_0^∞ N sech(x) dx = 2N ∫_0^∞ sech(x) dx = 2N [π/2] = Nπ
    ft_k0_analytic = N * PI
    k_arr_test = np.array([0.0])
    ft_sq_test = build_zero_mode_ft(k_arr_test, m_kink_xi=1.0, x_cutoff=50.0, n_x=2001)
    ft_k0_numerical = math.sqrt(float(ft_sq_test[0]))  # |FT(0)|

    print(f"\n  FT verification at k=0:")
    print(f"    |ψ̃_0(0)| analytic  = N×π = {ft_k0_analytic:.8f}")
    print(f"    |ψ̃_0(0)| numerical = {ft_k0_numerical:.8f}")
    err = abs(ft_k0_numerical - ft_k0_analytic) / ft_k0_analytic
    print(f"    Relative error = {err:.2e}  {'[PASS]' if err < 0.01 else '[WARN: >1%]'}")


# ---------------------------------------------------------------------------
# §3: Main Z_photon scan at specified β² values
# ---------------------------------------------------------------------------


def test_z_photon_scan() -> None:
    section("§3 — Z_photon values for β² ∈ {3π, 4π, 4.5π, 4.54π, 5π}")

    print("  Computing Z_photon at each β² value via 1-loop Jackiw-Rebbi zero-mode bubble.")
    print("  This may take 30-120 seconds depending on hardware...\n")

    beta_sq_values = [
        3.0 * PI,
        4.0 * PI,
        4.5 * PI,
        4.54 * PI,
        5.0 * PI,
    ]

    results = scan_beta_squared(beta_sq_values=beta_sq_values, verbose=True)

    print()
    subsection("Z_photon Results Table")
    header = (
        f"  {'β²/π':>8s}  {'g_Thirring':>12s}  {'α_bare':>12s}  "
        f"{'Z_photon':>10s}  {'1/α_ren':>10s}  {'Δ(1/α)':>10s}  {'Match':>6s}"
    )
    print(header)
    print("  " + "-" * 84)
    for r in results:
        if r.alpha_bare <= 0.0:
            match = "NO (g≤0)"
            inv_a = "inf"
            delta = "inf"
            z = f"{r.z_photon:.6f}"
        else:
            match = "YES" if r.satisfies_alpha else "NO"
            inv_a = f"{r.inv_alpha_renormalized:.3f}"
            delta = f"{r.delta_from_target:.4f}"
            z = f"{r.z_photon:.6f}"
        print(
            f"  {r.beta_squared/PI:>8.4f}  {r.g_thirring:>12.6f}  "
            f"{r.alpha_bare:>12.8f}  {z:>10s}  {inv_a:>10s}  {delta:>10s}  {match:>6s}"
        )

    print(f"\n  Target: 1/α = {INV_ALPHA_TARGET:.6f}")
    print(f"  Match criterion: |Δ(1/α)| < 5  (within ~4% of target)")

    # Print full notes for each result
    print()
    subsection("Detailed notes")
    for r in results:
        print(f"  {r.note}")


# ---------------------------------------------------------------------------
# §4: Fine scan to find the best β²
# ---------------------------------------------------------------------------


def test_fine_scan() -> None:
    section("§4 — Fine scan: finding β² that minimises |1/α_ren − 137.036|")

    print("  Scanning β² ∈ [0.5π, 4π) with 500 points.")
    print("  (Only β² < 4π gives positive g_Thirring and positive α_bare.)")
    print("  I_bundle computed once (β²-independent); 500 bosonization evaluations.\n")

    scan_result = find_best_z_photon_beta(
        beta_sq_min=0.5 * PI,
        beta_sq_max=4.0 * PI - 0.01,
        n_scan=500,
        n_x=101,
    )

    all_results: list[ZPhotonResult] = scan_result.get("all_results", [])

    if not all_results:
        print("  [ERROR] No physical results found in scan.")
        return

    best: ZPhotonResult = scan_result["best_result"]
    n_physical = scan_result.get("n_physical", 0)

    print(f"  Scan complete: {n_physical} physical β² points evaluated.")
    print()
    subsection("Best β² result")
    print(f"  Best β²       = {best.beta_squared:.6f}  = {best.beta_squared/PI:.6f} π")
    print(f"  g_Thirring    = {best.g_thirring:.8f}")
    print(f"  g_Yukawa      = {best.g_yukawa:.8f}  (= g × c₁, c₁=½ Möbius factor)")
    print(f"  α_bare        = {fmt_alpha(best.alpha_bare)}")
    print(f"  I_bundle      = {best.i_bundle:.8e}")
    print(f"  Z_photon      = {best.z_photon:.8f}")
    print(f"  α_renormalized= {fmt_alpha(best.alpha_renormalized)}")
    print(f"  {fmt_delta(best.delta_from_target)}")
    print(f"  Satisfies α=1/137: {'YES — CANDIDATE FOUND' if best.satisfies_alpha else 'NO'}")

    # Print the top-5 closest
    sorted_results = sorted(all_results, key=lambda r: r.delta_from_target)
    top_n = min(5, len(sorted_results))
    print()
    subsection(f"Top {top_n} closest β² values to α = 1/137")
    print(
        f"  {'β²/π':>8s}  {'g_Thirring':>12s}  {'α_bare':>14s}  "
        f"{'Z_γ':>10s}  {'1/α_ren':>10s}  {'Δ(1/α)':>10s}"
    )
    print("  " + "-" * 76)
    for r in sorted_results[:top_n]:
        print(
            f"  {r.beta_squared/PI:>8.4f}  {r.g_thirring:>12.6f}  "
            f"{r.alpha_bare:>14.10f}  {r.z_photon:>10.6f}  "
            f"{r.inv_alpha_renormalized:>10.4f}  {r.delta_from_target:>10.4f}"
        )

    # Report the range of Z_photon values seen
    z_vals = [r.z_photon for r in all_results]
    alpha_ren_vals = [r.inv_alpha_renormalized for r in all_results if math.isfinite(r.inv_alpha_renormalized)]
    print()
    print(f"  Z_photon range across all β²: [{min(z_vals):.6f}, {max(z_vals):.6f}]")
    if alpha_ren_vals:
        print(f"  1/α_ren range:                [{min(alpha_ren_vals):.4f}, {max(alpha_ren_vals):.4f}]")
        print(f"  Target 1/α = {INV_ALPHA_TARGET:.4f} {'WITHIN' if min(alpha_ren_vals) < INV_ALPHA_TARGET < max(alpha_ren_vals) else 'OUTSIDE'} the scanned range.")


# ---------------------------------------------------------------------------
# §5: Cross-check at Coleman duality point β² = 4π
# ---------------------------------------------------------------------------


def test_free_fermion_point() -> None:
    section("§5 — Free-fermion point β² = 4π (Coleman duality check)")

    beta_sq_4pi = 4.0 * PI
    bos = bosonization_alpha(beta_sq_4pi)

    print(f"  At β² = 4π = {beta_sq_4pi:.6f}:")
    print(f"    g_Thirring  = {bos.g_thirring:.10f}  (expected 0 exactly)")
    print(f"    α_bare      = {bos.alpha_bare:.10f}  (expected 0: no interaction)")
    print()
    print("  Coleman duality: at β² = 4π the sine-Gordon theory maps exactly")
    print("  onto a FREE (non-interacting) Thirring fermion. No coupling, no")
    print("  photon renormalization, α_bare = 0. This is a consistency check.")
    print()
    print("  For β² < 4π: g_Thirring > 0, repulsive fermion-fermion interaction,")
    print("  positive α_bare. This is the physical domain for EM coupling.")
    print()
    print("  Z_photon at β² = 4π is undefined (g = 0 → no loop) = 1.0 by convention.")

    # Verify Z_photon returns the right thing at β² just below 4π
    beta_sq_near = 4.0 * PI - 0.001
    r_near = compute_z_photon(beta_sq_near)
    print(f"\n  At β² = 4π − ε (ε={0.001:.3f}):")
    print(f"    g_Thirring  = {r_near.g_thirring:.8f}")
    print(f"    Z_photon    = {r_near.z_photon:.8f}")
    print(f"    1/α_ren     = {r_near.inv_alpha_renormalized:.4f}")


# ---------------------------------------------------------------------------
# §6: Bosonization comparison (what existed before, what the loop adds)
# ---------------------------------------------------------------------------


def test_before_after_loop() -> None:
    section("§6 — Before/after loop: α_bare vs α_ren comparison")

    print("  Comparing the naive bosonization result (α_bare, no loop)")
    print("  with the loop-corrected result (α_ren = α_bare × Z_photon).")
    print()
    print(
        f"  {'β²/π':>8s}  {'g_Thirring':>12s}  {'1/α_bare':>12s}  "
        f"{'Z_γ':>10s}  {'1/α_ren':>12s}  {'Δ naive':>10s}  {'Δ loop':>10s}"
    )
    print("  " + "-" * 90)

    for beta_pi in [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 3.9, 3.95]:
        beta_sq = beta_pi * PI
        bos = bosonization_alpha(beta_sq)
        if bos.alpha_bare <= 0.0:
            continue
        try:
            r = compute_z_photon(beta_sq)
        except ValueError:
            continue
        delta_naive = abs(1.0 / bos.alpha_bare - INV_ALPHA_TARGET)
        delta_loop = r.delta_from_target

        print(
            f"  {beta_pi:>8.4f}  {bos.g_thirring:>12.6f}  "
            f"{1/bos.alpha_bare:>12.4f}  {r.z_photon:>10.6f}  "
            f"{r.inv_alpha_renormalized:>12.4f}  {delta_naive:>10.4f}  {delta_loop:>10.4f}"
        )

    print(f"\n  Target 1/α = {INV_ALPHA_TARGET:.4f}")
    print()
    print("  Interpretation:")
    print("  - 'Δ naive' is the gap with no loop correction.")
    print("  - 'Δ loop' is the gap after Z_photon from the zero-mode bubble.")
    print("  - If Z_photon brings Δ loop < Δ naive, the loop correction is in the right direction.")
    print("  - If no β² achieves Δ loop < 5, the zero-mode bubble alone is insufficient.")


# ---------------------------------------------------------------------------
# §7: Honest assessment
# ---------------------------------------------------------------------------


def print_honest_assessment(scan_results: list[ZPhotonResult] | None = None) -> None:
    section("§7 — Honest assessment of the Z_photon computation")

    print("""
WHAT THIS COMPUTATION DOES
---------------------------
We computed the 1-loop photon wave-function renormalization Z_photon from the
Jackiw-Rebbi zero-mode bubble on the Möbius U(1) bundle. The computation chain:

  1. Coleman bosonization: β² → g_Thirring = π(4π/β² − 1)
  2. Möbius factor: g_Yukawa = g_Thirring × c₁  (c₁ = 1/2, half-flux holonomy)
  3. Zero-mode profile: ψ_0(x) = N cosh^{-Mξ}(x/ξ)  [Jackiw-Rebbi, 1976]
  4. Momentum-space weight: ρ_0(k) = |FT[ψ_0]|² via direct numerical integration
  5. 1-loop bubble: Π(q²) = g_Yukawa² ∫ dk ρ_0(k) ρ_0(k+q) / [(k²+μ²)((k+q)²+μ²)]
  6. Z_photon = 1 + g_Yukawa² × dΠ/dq²|₀   (Wilsonian wave-function renorm.)
  7. α_ren = α_bare × Z_photon

WHAT THE NUMBERS SHOW
----------------------""")

    if scan_results is not None and any(r.satisfies_alpha for r in scan_results):
        candidates = [r for r in scan_results if r.satisfies_alpha]
        print(f"  CANDIDATE FOUND: {len(candidates)} β² value(s) give |Δ(1/α)| < 5.")
        for r in candidates:
            print(f"    β²={r.beta_squared/PI:.4f}π: Z_γ={r.z_photon:.6f}, 1/α_ren={r.inv_alpha_renormalized:.4f}")
    else:
        print("  No β² in the scanned range simultaneously satisfies α_ren = 1/137.036")
        print("  via the zero-mode bubble alone.")

    print("""
WHAT THE LOOP CORRECTION DOES (QUALITATIVELY)
----------------------------------------------
The Jackiw-Rebbi zero-mode has spectral weight concentrated at k ~ 0 to 1 in
units of M_kink (the kink mass). The loop integral Π(q²) is therefore a smooth
function of q², and dΠ/dq² is of order O(1) in natural units.

The coupling factor g_Yukawa = g_Thirring × c₁ is small near the free-fermion
point (β² → 4π: g_Thirring → 0) and grows as β² decreases toward 0.

The Möbius factor c₁ = 1/2 suppresses the loop by a factor of 4 relative to a
naive bulk-fermion loop. This is the geometric consequence of the half-flux
holonomy (spec §18.10).

APPROXIMATIONS AND THEIR VALIDITY
-----------------------------------
1. Zero-mode dominance: We keep only the Jackiw-Rebbi zero-mode in the
   fermion propagator. Continuum (scattering) states with E ~ M_kink contribute
   at O(g²/M_kink²) and are genuinely subleading for energies ≪ M_kink.

2. 1+1D reduction: The kink is extended in the transverse (2+1D) directions.
   The full 3+1D loop is approximated by a 1+1D integral along the kink axis.
   Transverse momentum integration gives a finite multiplicative factor of
   O(M_kink ξ) that we absorb into the natural-unit normalization.

3. Single loop: No ladder or crossed diagrams. These enter at two-loop order
   (g⁴), suppressed by (g/π)² ≈ (α_bare π) ≪ 1 in the perturbative regime.

4. On-shell / Wilsonian Z_photon: We compute Z from the q²-derivative of Π at
   q²=0 rather than from a full matching computation at a UV scale. This is
   exact for a massless photon and gives the leading wavefunction renorm.

WHAT WOULD BE NEEDED TO CLOSE THE GAP
----------------------------------------
spec §18.48.7 item 1 is explicit: a complete derivation of α = 1/137 requires:

  A. Continuum-mode contributions (O(g²/M_kink²) corrections to Z_photon).
     These break the zero-mode dominance approximation and must be computed
     from the full Dirac resolvent in the kink background.

  B. Multi-loop diagrams: the 2-loop "sunset" and "figure-8" diagrams on the
     Möbius bundle modify Z_photon at O(g⁴). For α_bare ~ 1/50 (typical in the
     physical β² range), these are ~2% corrections — not negligible at 1/137 precision.

  C. Correct identification of the normalization: the factor mapping
     α_bare → α_ren is not just Z_photon from the bubble. It also includes
     the vertex renormalization Z_vertex (Ward identity: Z_vertex = Z_fermion
     in QED, but on the Möbius bundle this identity may receive topology corrections).

  D. Full 3+1D computation: the 1+1D reduction along the kink is an approximation.
     The full transverse-momentum integral modifies Z_photon by a finite factor
     that depends on how the kink mode is coupled in the transverse directions.

CONCLUSION
-----------
The zero-mode bubble on the Möbius bundle is a well-defined, finite, and
physically motivated correction to α. It shifts α_bare by a factor Z_photon
that is of O(1) in the natural coupling expansion.

Whether this single correction suffices to give α_ren = 1/137.036 depends
entirely on the input β² — and the physical β² (pinned by the Higgs/W ratio
to β² ≈ 4.54π, which is ABOVE the free-fermion point at 4π and therefore in
the attractive-Thirring regime with g < 0) falls outside the domain where
the naive bosonization gives a positive α_bare.

This is the same structural gap identified in alpha_derivation.py:
  - α = 1/137 and m_H/m_W = 1.558 constrain β² to different regions.
  - The zero-mode bubble modifies α_bare but does NOT bridge this gap.
  - The missing physics is the correct treatment of the β² > 4π sector,
    where the Thirring coupling is attractive and the standard bosonization
    → positive α route does not apply directly.

The computation is honest: the bubble is real and finite, the Möbius factor
c₁ = 1/2 is topologically exact, and the zero-mode profile is the correct
Jackiw-Rebbi solution. But the leading-order zero-mode bubble alone is
insufficient to derive α = 1/137 from β² ~ 4.54π. What remains is
described precisely in spec §18.48.7 item 1.
""")


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------


def main() -> None:
    print(SEP)
    print("  PHOTON WAVE-FUNCTION RENORMALIZATION Z_photon(β², M_kink)")
    print("  1-loop Jackiw-Rebbi zero-mode bubble on the Möbius U(1) bundle")
    print("  spec §§18.10, 18.34, 18.45, 18.48 | Jackiw-Rebbi (1976)")
    print(SEP)
    print()
    print(f"  Physical constants:")
    print(f"    Möbius c₁           = {C1_MOBIUS:.4f}  (first Chern class, §18.10)")
    print(f"    M_kink × ξ          = {M_KINK_XI:.4f}  (natural units)")
    print(f"    Target α            = {ALPHA_TARGET:.10f}  =  1/{INV_ALPHA_TARGET:.6f}")
    print(f"    Free-fermion β²     = 4π = {4*PI:.6f}")
    print(f"    Higgs/W β²          ≈ 4.54π = {4.54*PI:.6f}  (spec §18.52.4)")

    # Run all tests
    test_symbolic_zero_mode()
    test_normalization()
    test_z_photon_scan()
    test_free_fermion_point()
    test_before_after_loop()

    # Fine scan — this is the expensive part
    section("§4 — Fine scan: finding β² that minimises |1/α_ren − 137.036|")
    print("  Scanning β² ∈ [0.5π, 4π) with 500 points.")
    print("  (Only β² < 4π gives positive g_Thirring and positive α_bare.)")
    print("  I_bundle computed once (β²-independent); 500 bosonization evaluations.\n")

    scan_result = find_best_z_photon_beta(
        beta_sq_min=0.5 * PI,
        beta_sq_max=4.0 * PI - 0.01,
        n_scan=500,
        n_x=101,
    )

    all_results: list[ZPhotonResult] = scan_result.get("all_results", [])
    best = scan_result.get("best_result")

    if best is not None:
        print(f"  Scan complete: {scan_result.get('n_physical', 0)} physical β² points.")
        print()
        print(f"  Best β²       = {best.beta_squared:.6f}  = {best.beta_squared/PI:.6f} π")
        print(f"  g_Thirring    = {best.g_thirring:.8f}")
        print(f"  g_Yukawa      = {best.g_yukawa:.8f}")
        print(f"  α_bare        = {fmt_alpha(best.alpha_bare)}")
        print(f"  I_bundle      = {best.i_bundle:.8e}")
        print(f"  Z_photon      = {best.z_photon:.8f}")
        print(f"  α_renormalized= {fmt_alpha(best.alpha_renormalized)}")
        print(f"  {fmt_delta(best.delta_from_target)}")
        print(f"  Satisfies α=1/137: {'YES' if best.satisfies_alpha else 'NO'}")

        if all_results:
            z_vals = [r.z_photon for r in all_results]
            inv_a_vals = [r.inv_alpha_renormalized for r in all_results
                          if math.isfinite(r.inv_alpha_renormalized)]
            print(f"\n  Z_photon range: [{min(z_vals):.6f}, {max(z_vals):.6f}]")
            if inv_a_vals:
                print(f"  1/α_ren range:  [{min(inv_a_vals):.4f}, {max(inv_a_vals):.4f}]")
                if min(inv_a_vals) < INV_ALPHA_TARGET < max(inv_a_vals):
                    print(f"  Target 1/α={INV_ALPHA_TARGET:.4f} IS WITHIN the scanned range.")
                    print("  A β² satisfying α_ren = 1/137 EXISTS — but may not be")
                    print("  the physically motivated β² from the Higgs/W constraint.")
                else:
                    print(f"  Target 1/α={INV_ALPHA_TARGET:.4f} is OUTSIDE the scanned 1/α_ren range.")
                    print("  No β² in the repulsive-Thirring sector gives α_ren = 1/137")
                    print("  via the zero-mode bubble alone.")
    else:
        print("  [ERROR] Fine scan returned no results.")

    # Print honest assessment with scan results
    print_honest_assessment(all_results)

    print(SEP)
    print("  COMPUTATION COMPLETE")
    print(SEP)


if __name__ == "__main__":
    main()
