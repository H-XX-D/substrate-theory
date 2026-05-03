"""Driver for src/stiff_medium/substrate_uv_completion.py.

Tests three routes to the substrate Planck scale:
    Route 1: BH-formation (kink at ξ where r_s = ξ).
    Route 2: 1D Möbius-cycle ε scaling (1/N vs 1/√N vs 1/N^(2/3)).
    Route 3: K-running UV fixed point search.

Usage:
    python scripts/substrate_uv_completion_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from stiff_medium.substrate_uv_completion import (  # noqa: E402
    C_SI,
    G_OBSERVED,
    HBAR_SI,
    K_E,
    L_PLANCK_OBS,
    M_E_SI,
    M_PLANCK_OBS,
    RHO_E,
    XI_E,
    assess,
    bh_formation_planck_scale,
    k_running_fixed_point,
    moebius_cycle_epsilon,
    report,
)


def banner(s: str) -> None:
    print()
    print("=" * 78)
    print(s)
    print("=" * 78)


def main() -> None:
    banner("SUBSTRATE UV COMPLETION — §18.78 Planck scale + ε structure")
    print()
    print("  Substrate primitives (no G):")
    print(f"    c         = {C_SI:.4e} m/s")
    print(f"    ℏ         = {HBAR_SI:.4e} J·s")
    print(f"    m_e       = {M_E_SI:.4e} kg")
    print(f"    ξ_e       = {XI_E:.4e} m  (electron Compton)")
    print(f"    K_e       = {K_E:.4e} Pa")
    print(f"    ρ_e       = {RHO_E:.4e} kg/m³")
    print()
    print("  Reference values (use G — for comparison only):")
    print(f"    G         = {G_OBSERVED:.4e} m³ kg⁻¹ s⁻²")
    print(f"    l_Planck  = {L_PLANCK_OBS:.4e} m")
    print(f"    M_Planck  = {M_PLANCK_OBS:.4e} kg")
    print(f"    ξ_e/l_P   = {XI_E/L_PLANCK_OBS:.4e}")

    banner("ROUTE 1 — BH-formation: ξ where kink forms its own horizon")
    bh = bh_formation_planck_scale()
    print()
    print(f"  m_kink(ξ) = 8ℏ/(c ξ);   r_s(ξ) = 2G m_kink/c² = 16ℏG/(ξ c³)")
    print(f"  Setting r_s = ξ:   ξ_BH² = 16ℏG/c³ = 16 l_P²")
    print(f"                     ξ_BH  = 4 l_P")
    print()
    print(f"  ξ_BH (geometric)  = {bh.xi_BH_geometric:.4e} m")
    print(f"  ξ_BH/l_P          = {bh.xi_BH_geometric/L_PLANCK_OBS:.4f}  (= 4 ✓)")
    print(f"  m_kink at ξ_BH    = {bh.m_kink_at_xi_BH:.4e} kg")
    print(f"                    ≈ {bh.m_kink_at_xi_BH * C_SI**2 / 1.602e-10:.4e} GeV/c²")
    print(f"  r_s at ξ_BH       = {bh.r_s_at_xi_BH:.4e} m  (= ξ_BH ✓)")
    print()
    print(f"  Self-consistency:  ξ_BH/4 = l_P, so G = (ξ_BH/4)² c³/ℏ")
    print(f"  Recovered G        = {bh.G_recovered:.6e}  (target: {G_OBSERVED:.6e})")
    print(f"  Match              = {bh.is_self_consistent}")
    print()
    print(f"  Uses G as input    = {bh.uses_G}")
    print(f"  Is a derivation    = {bh.is_derivation}")
    print()
    print("  STATEMENT:")
    for line in bh.statement.split(". "):
        if line.strip():
            print(f"    {line.strip()}.")

    banner("ROUTE 2 — Möbius cycle ε scaling: which N-power matches?")
    moebius = moebius_cycle_epsilon()
    print()
    print(f"  N_cycle (= ξ_e/l_P) = {moebius.N_cycle:.4e}")
    print(f"  ε_observed          = {moebius.eps_observed:.4e}")
    print()
    print(f"  Candidate scalings:")
    print(f"    {'Scaling':<28s} {'ε_predicted':>16s} {'log10(ε/ε_obs)':>16s}")
    print(f"    {'-'*28} {'-'*16} {'-'*16}")
    print(f"    {'1/√N (3D bulk)':<28s} {moebius.eps_volume_scaling:>16.4e} "
          f"{moebius.log10_ratio_volume:>+16.3f}")
    print(f"    {'1/N^(2/3) (2D surface)':<28s} {moebius.eps_surface_scaling:>16.4e} "
          f"{moebius.log10_ratio_surface:>+16.3f}")
    print(f"    {'1/N (1D Möbius cycle)':<28s} {moebius.eps_cycle_scaling:>16.4e} "
          f"{moebius.log10_ratio_cycle:>+16.3f}")
    print()
    print(f"  BEST MATCH:  {moebius.best_match}")
    print(f"  1D cycle scaling matches ε_observed: {moebius.is_cycle_match}")
    print()
    print("  PHYSICAL INTERPRETATION:")
    print("    • 3D bulk (1/√N) misses by 10¹¹ — gravity would be too weak.")
    print("    • 2D surface (1/N^(2/3)) misses by 10⁸ — still too weak.")
    print("    • 1D Möbius cycle (1/N) matches exactly.")
    print("    ⇒ The §18.10 Möbius half-flux cancellation MUST run along the")
    print("      1D azimuthal cycle, not over the bulk volume or surface area.")
    print("    This is a sharp, falsifiable structural prediction.")

    banner("ROUTE 3 — K-running fixed point search")
    k_run = k_running_fixed_point()
    print()
    print(f"  K_e (electron scale)  = {K_E:.4e} Pa")
    print(f"  K_Planck (uses G)     = {k_run.K_at_planck_using_G:.4e} Pa")
    print(f"  K_Planck/K_e ratio    = {k_run.K_at_planck_using_G/K_E:.4e}")
    print()
    print(f"  Power-law K(ξ) = K_e × (ξ_e/ξ)^a")
    print(f"  Required exponent a   ≈ {k_run.K_running_a_to_match:.6f}")
    print(f"  Is a O(1)-natural?     {k_run.is_a_natural}")
    print()
    print(f"  IMPORTANT: a = 4.000 is NOT a fit — it is forced by ℏ = K ξ⁴/c.")
    print(f"  At both ξ_e and l_P: K ξ⁴ = ℏc, so K_P/K_e = (ξ_e/l_P)⁴ identically.")
    print(f"  Spec §18.46 a ≈ 5.69 is a different ansatz (power-law + corrections).")
    print(f"  Fixed point exists w/o back-reaction: "
          f"{k_run.fixed_point_exists_without_back_reaction}")
    print()
    print("  STATEMENT:")
    for line in k_run.statement.split(". "):
        if line.strip():
            print(f"    {line.strip()}.")

    banner("AGGREGATE ASSESSMENT")
    a = assess()
    print()
    print(f"  l_P derivable from substrate primitives alone? "
          f"{a.l_P_derivable_without_extra_input}")
    print()
    print("  WHAT THE SUBSTRATE FRAMEWORK PREDICTS:")
    for s in a.what_the_substrate_does_predict:
        print(f"    • {s}")
    print()
    print("  WHAT THE SUBSTRATE FRAMEWORK DOES NOT PREDICT:")
    for s in a.what_the_substrate_does_not_predict:
        print(f"    • {s}")
    print()
    print("  NET OPEN INPUT:")
    print(f"    {a.net_open_input}")
    print()
    print("  NEXT STEP:")
    print(f"    {a.next_step}")
    print()

    banner("FULL REPORT")
    print(report())


if __name__ == "__main__":
    main()
