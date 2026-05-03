"""Test driver: does the substrate predict Newton's G?

Runs src/stiff_medium/newton_G_from_substrate.py and reports.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# Make src importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from stiff_medium.newton_G_from_substrate import (  # noqa: E402
    G_OBSERVED,
    K_E,
    RHO_E,
    XI_E,
    C_SI,
    HBAR_SI,
    M_E_SI,
    dimensional_candidates,
    hierarchy_check_substrate_only,
    newton_G_full_analysis,
    topological_prefactors,
)


def banner(s: str) -> None:
    print()
    print("=" * 78)
    print(s)
    print("=" * 78)


def main() -> None:
    banner("NEWTON'S G FROM SUBSTRATE PARAMETERS — HONEST ANALYSIS")
    print(f"  K_e   = {K_E:.4e} Pa")
    print(f"  ρ_e   = {RHO_E:.4e} kg/m³")
    print(f"  ξ_e   = {XI_E:.4e} m  (= λ_C(electron))")
    print(f"  c     = {C_SI:.4e} m/s")
    print(f"  ℏ     = {HBAR_SI:.4e} J·s")
    print(f"  m_e   = {M_E_SI:.4e} kg")
    print(f"  G_obs = {G_OBSERVED:.4e} m³ kg⁻¹ s⁻²    (target — NOT used as input)")

    # --- 1. Dimensional analysis ---------------------------------------------
    banner("1. DIMENSIONAL ANALYSIS — candidate G formulas")
    print("Constraints from the substrate model:")
    print("    c² = K/ρ              (wave speed)")
    print("    ℏ  = K ξ⁴ / c          (action quantum, §18.46.1)")
    print("    m_kink = 8 ℏ / (c ξ)   (sine-Gordon kink mass)")
    print()
    print("→ Only 2 independent dimensionful primitives. Pick (ξ, c); ρ, K, ℏ derived.")
    print("→ Up to a dimensionless prefactor, every G-formula reduces to one number.")
    print()
    print(f"{'name':<30}{'value':>16}{'value/G_obs':>16}")
    print("-" * 78)
    for d in dimensional_candidates():
        print(f"{d.name:<30}{d.value:>16.4e}{d.ratio_to_observed:>16.4e}")
        print(f"   formula: {d.formula}")
    print()
    print("Key observation: G_a, G_b, G_d agree numerically (constraint-consistent);")
    print("any small drift = numerical rounding in the substrate constants.")

    # --- 2. Topological prefactors -------------------------------------------
    banner("2. TOPOLOGICAL / GEOMETRIC PREFACTORS")
    print("Apply common geometric & coupling prefactors to G_a:")
    print()
    G_a = dimensional_candidates()[0].value
    print(f"{'prefactor':<25}{'value':>10}{'G_pred':>16}{'G_pred/G_obs':>18}")
    print("-" * 78)
    for p in topological_prefactors(G_a):
        print(f"{p.name:<25}{p.prefactor:>10.3e}{p.G_predicted:>16.4e}{p.ratio_to_observed:>18.4e}")
    print()
    print("None of these brings the prediction within ~10⁴⁰ of observation.")
    print("There is no 'clean prefactor' fix — the gap is too large.")

    # --- 3. Hierarchy check --------------------------------------------------
    banner("3. HIERARCHY CHECK — α_grav / α_EM")
    h = hierarchy_check_substrate_only()
    print(f"  α_EM            = e²/(4πε₀ℏc)        = {h['alpha_EM_substrate']:.4e}")
    print(f"  α_grav (obs)    = G_obs m_e²/(ℏc)    = {h['alpha_grav_observed']:.4e}")
    print(f"  α_grav (subst)  = G_subst m_e²/(ℏc)  = {h['alpha_grav_substrate_bare']:.4e}")
    print()
    print(f"  Observed:  α_grav/α_EM  = {h['alpha_grav_over_alpha_EM_observed']:.4e}")
    print(f"  Substrate: α_grav/α_EM  = {h['alpha_grav_over_alpha_EM_substrate_bare']:.4e}")
    print()
    print(f"  G_substrate (bare)  = {h['G_substrate_bare']:.4e}")
    print(f"  G_observed          = {h['G_observed']:.4e}")
    print(f"  required ε² (G_obs/G_subst) = {h['ratio_observed_over_substrate']:.4e}")
    print(f"  required ε                  = {h['epsilon_required']:.4e}")
    print()
    print(f"  Note: at ξ = λ_C(electron), m_e c ξ / ℏ = 1 by construction,")
    print(f"  so α_grav_substrate_bare = (ξ/λ_C)² ≈ 1 — completely WRONG sign of magnitude.")
    print()
    print(f"  Verdict: {h['verdict']}")

    # --- 4. Final assessment -------------------------------------------------
    banner("4. ASSESSMENT")
    full = newton_G_full_analysis()
    print(full["assessment"])
    print()
    print("Honest note:")
    print(full["honest_note"])

    print()
    banner("SUMMARY (one-line)")
    G_subst = h["G_substrate_bare"]
    log_gap = math.log10(G_subst / G_OBSERVED)
    print(
        f"Bare substrate: G ≈ {G_subst:.2e}   |  observed: {G_OBSERVED:.3e}   |  "
        f"off by 10^{log_gap:.1f}"
    )
    print(
        "→ The stiff-medium model does NOT predict Newton's G from K_e, ρ_e, ξ_e, c, ℏ alone."
    )
    print(
        "→ Bare substrate gives an EM-scale coupling. Gravity requires an unmodelled"
    )
    print(
        f"  suppression ε ≈ {h['epsilon_required']:.2e} (≈ m_e/M_Planck), open per §18.32."
    )


if __name__ == "__main__":
    main()
