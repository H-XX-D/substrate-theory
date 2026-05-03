"""Driver for src/stiff_medium/gravity_residual_factor.py.

Computes the charge-symmetric suppression ε that converts the bare-substrate
G ≈ 3.8 × 10³⁴ into observed G ≈ 6.7 × 10⁻¹¹, and reports honestly whether
this is a substrate prediction or a dimensional tautology.

Reference: spec §18.32, §18.46, §18.60.3.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from stiff_medium.gravity_residual_factor import (  # noqa: E402
    C_SI,
    G_OBSERVED,
    G_SUBSTRATE_BARE,
    HBAR_SI,
    K_E,
    L_PLANCK_OBS,
    M_E_SI,
    M_P_SI,
    M_PLANCK_OBS,
    RHO_E,
    XI_E,
    algebraic_identity,
    assess,
    cancellation_toy_model,
    epsilon_candidates,
    gravity_residual_factor_report,
    universality_check,
)


def banner(s: str) -> None:
    print()
    print("=" * 78)
    print(s)
    print("=" * 78)


def main() -> None:
    banner("GRAVITY RESIDUAL FACTOR ε — substrate computation (§18.32, §18.60.3)")
    print(f"  K_e        = {K_E:.4e} Pa")
    print(f"  ρ_e        = {RHO_E:.4e} kg/m³")
    print(f"  ξ_e        = {XI_E:.4e} m  (= λ_C(electron))")
    print(f"  c          = {C_SI:.4e} m/s")
    print(f"  ℏ          = {HBAR_SI:.4e} J·s")
    print(f"  m_e        = {M_E_SI:.4e} kg")
    print(f"  m_p        = {M_P_SI:.4e} kg  (universality test)")
    print()
    print(f"  G_substrate_bare = c³ξ²/ℏ = {G_SUBSTRATE_BARE:.4e}")
    print(f"  G_observed       = {G_OBSERVED:.4e}      (target — NOT used as input)")
    print(f"  M_Planck         = {M_PLANCK_OBS:.4e} kg  (uses G_observed)")
    print(f"  l_Planck         = {L_PLANCK_OBS:.4e} m   (uses G_observed)")

    # 1. Algebraic identity
    banner("1. ALGEBRAIC IDENTITY  m_e × ξ_e = M_Planck × l_Planck = ℏ/c")
    ident = algebraic_identity()
    print(f"  m_e × ξ_e          = {ident.m_e_xi_e:.6e} kg·m")
    print(f"  M_Planck × l_Planck = {ident.M_pl_l_pl:.6e} kg·m")
    print(f"  ℏ / c              = {ident.hbar_over_c:.6e} kg·m")
    print(f"  ratio (should = 1) = {ident.ratio_eq_one:.6f}")
    print()
    print(f"  {ident.statement}")

    # 2. Epsilon candidates
    banner("2. CANDIDATE COMPUTATIONS OF ε")
    print(f"{'name':<22} {'value':>14} {'uses G':>8} {'tautology':>10}  formula")
    print("-" * 78)
    for e in epsilon_candidates():
        val_str = "nan" if math.isnan(e.value) else f"{e.value:.4e}"
        print(f"{e.name:<22} {val_str:>14} {str(e.uses_G):>8} {str(e.is_tautological):>10}  {e.formula}")
    print()
    for e in epsilon_candidates():
        print(f"  • {e.name}: {e.rationale}")

    # 3. Cancellation toy model
    banner("3. DISTRIBUTED-CANCELLATION TOY MODEL")
    cm = cancellation_toy_model()
    print(f"  ξ_e / l_Planck (= N_cycle)   = {cm.N_cycle:.4e}")
    print(f"  (ξ_e / l_Planck)³ (= N_volume) = {cm.N_volume:.4e}")
    print()
    print(f"  ε via 1/√N (3D bulk)            = {cm.eps_volume_scaling:.4e}")
    print(f"  ε via 1/N (1D Möbius cycle)     = {cm.eps_cycle_scaling:.4e}")
    print(f"  ε observed                      = {cm.eps_observed:.4e}")
    print()
    print(f"  Best match: {cm.best_match}")
    print()
    print(f"  {cm.statement}")

    # 4. Universality check
    banner("4. UNIVERSALITY: does G_eff depend on test-particle mass?")
    u = universality_check()
    print(f"  Reading (i)  — universal ε from electron Compton scale:")
    print(f"     G_eff (universal)  = {u.G_eff_universal:.4e}")
    print(f"     matches G_observed = {abs(math.log10(u.G_eff_universal/G_OBSERVED)) < 0.01}")
    print()
    print(f"  Reading (ii) — ε scales with bound-state mass:")
    print(f"     G_eff(electron test) = {u.G_eff_electron_test:.4e}")
    print(f"     G_eff(proton test)   = {u.G_eff_proton_test:.4e}")
    print(f"     ratio (m_p/m_e)²    = {u.ratio_proton_to_electron:.4e}")
    print(f"     Eötvös bound         < {u.eotvos_bound:.0e}")
    print(f"     reading (ii) survives Eötvös: {u.reading_ii_passes}")
    print()
    print(f"  {u.statement}")

    # 5. Final assessment
    banner("5. ASSESSMENT")
    a = assess()
    print(a.summary)

    # 6. One-line summary
    banner("ONE-LINE SUMMARY")
    print(
        f"  ε_observed = {a.epsilon_observed:.4e}, ε_dimensional = m_e/M_Planck "
        f"= {a.epsilon_dimensional:.4e}, match = {a.matches}"
    )
    print(
        "  → Match is exact but TAUTOLOGICAL (m_e × ξ_e = M_Planck × l_Planck = ℏ/c)."
    )
    print(
        "  → Substrate primitives K, ρ, ξ_e, c, ℏ alone CANNOT compute ε without"
    )
    print(
        "    positing a second length scale ξ_P (Planck-scale UV cutoff)."
    )
    print(
        "  → Predictive content: ε = 1/N_cycle on a 1D Möbius cycle (NOT 1/√N bulk)."
    )
    print(
        "  → Equivalence principle requires ε to be UNIVERSAL (electron-Compton anchored),"
    )
    print(
        "    not test-mass-dependent. This is a non-trivial structural commitment."
    )

    # Also verify that the structured report works
    report = gravity_residual_factor_report()
    print()
    print(f"  [report keys: {sorted(report.keys())}]")


if __name__ == "__main__":
    main()
