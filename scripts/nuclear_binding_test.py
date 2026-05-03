"""Nuclear binding energies of light stable nuclei from substrate primitives.

This script takes the substrate-derived QCD-scale primitives (σ, ξ_QCD, f_π)
and predicts binding energies for the simplest stable nuclei:

    ²H (deuteron), ³He, ³H, ⁴He, ⁶Li, ⁸Be, ¹²C

Two paths:

  1.  Variational OPE Gaussian for the deuteron
        ψ ∝ exp(-r²/2a²);  V_OPE = -(g²/4π)·(m_π²/12m_N²)·e^(-mπr)/r
        Minimise ⟨T⟩ + ⟨V⟩ over a;  predict B(²H) and r_d.

  2.  Substrate semi-empirical mass formula for ³He/³H/⁴He/⁶Li, plus
      α-cluster picture for ⁸Be (2α) and ¹²C (3α).

Inputs (substrate-fixed; nothing fitted to nuclear binding):

  σ       = 0.180 GeV²        (regge_spectrum.py)
  ξ_QCD   = 0.2 fm
  f_π     = ½ σ ξ = 91.22 MeV (pion_decay_constant.py, §18.61.8)
  α       = 1/137.036         (substrate-derived, §18.61.5)
  g_A     = 1.27              (axial coupling, empirical)
  m_N     = 938.92 MeV        (PDG anchor)
  m_π     = 138.04 MeV        (isospin-averaged PDG anchor)

Run:  PYTHONPATH=src python3 scripts/nuclear_binding_test.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stiff_medium.nuclear_binding import (
    F_PI_MEV_SUBSTRATE,
    SIGMA_QCD_GEV2,
    XI_QCD_FM,
    compute_nuclear_binding_summary,
    print_summary,
)


def main() -> None:
    """Run the full substrate nuclear-binding test and print results."""
    print()
    print("=" * 78)
    print(" NUCLEAR BINDING OF LIGHT NUCLEI FROM SUBSTRATE PRIMITIVES")
    print("=" * 78)
    print()
    print(" Substrate inputs:")
    print(f"   σ_QCD = {SIGMA_QCD_GEV2:.4f} GeV²")
    print(f"   ξ_QCD = {XI_QCD_FM:.3f} fm")
    print(f"   f_π   = {F_PI_MEV_SUBSTRATE:.3f} MeV     (½ σ ξ; substrate)")
    print()
    print(" Method:")
    print("   ²H:                 numerical radial Schrödinger w/ substrate OPE")
    print("   ³He, ³H, ⁴He:       OPE pair-count × shell-saturation κ")
    print("   ⁶Li:                substrate Bethe-Weizsäcker SEMF")
    print("   ⁸Be, ¹²C:           α-cluster picture (n_α × B(⁴He) + cluster pairs)")
    print()

    # Run the calculation with the default tensor enhancement factor.
    # The factor 7.0 is the only phenomenological knob (see solve_deuteron);
    # it absorbs the OPE tensor force which dominates deuteron binding
    # but cannot be resolved in pure S-wave.
    summary = compute_nuclear_binding_summary(
        f_pi_MeV=F_PI_MEV_SUBSTRATE,
        tensor_enhancement_factor=7.0,
    )
    print_summary(summary)

    # Sensitivity sweep for the deuteron over the tensor enhancement factor
    print("=" * 78)
    print(" SENSITIVITY: deuteron binding vs tensor enhancement factor")
    print(" (factor=7 captures S-D mixing not resolvable in pure S-wave)")
    print("=" * 78)
    print()
    print(f"   {'factor':>7} {'rms [fm]':>10} {'<T> [MeV]':>11} {'<V> [MeV]':>11} "
          f"{'E [MeV]':>10} {'B [MeV]':>10}")
    for factor in [4.0, 5.0, 6.0, 6.5, 7.0, 7.5, 8.0, 9.0, 10.0]:
        from stiff_medium.nuclear_binding import solve_deuteron
        d = solve_deuteron(tensor_enhancement_factor=factor)
        print(f"   {factor:>7.2f} {d.rms_radius_fm:>10.3f} {d.kinetic_MeV:>11.3f} "
              f"{d.potential_MeV:>11.3f} {d.E_total_MeV:>10.3f} {d.binding_MeV:>10.3f}")
    print()

    # Aggregate quality
    abs_errs = [abs(p.fractional_error) for p in summary.predictions]
    n = len(abs_errs)
    n_under_10 = sum(1 for e in abs_errs if e <= 0.10)
    n_under_20 = sum(1 for e in abs_errs if e <= 0.20)

    print("=" * 78)
    print(" SUBSTRATE-PHYSICS BOTTOM LINE")
    print("=" * 78)
    print()
    print("  • The substrate's f_π = ½ σ ξ_QCD = 91.22 MeV gives, via")
    print("    Goldberger-Treiman with empirical g_A = 1.27, a pion-nucleon")
    print(f"    coupling g_πNN = {summary.g_piNN:.2f} (cf. empirical 13.5).")
    print()
    print("  • One-pion-exchange Yukawa potential V_OPE(r) follows directly,")
    print("    with NO additional fit.  The deuteron radial-Schrödinger")
    print("    calculation needs ONE phenomenological knob (tensor")
    print("    enhancement factor ≈ 7) that absorbs the OPE tensor force,")
    print("    which dominates deuteron binding but cannot be resolved in")
    print("    pure S-wave.  Same factor (matter-averaged at 20%) sets the")
    print("    SEMF coefficients.")
    print()
    print(f"  • Bottom-line accuracy on {n} nuclei:")
    print(f"      Within 10%: {n_under_10}/{n}")
    print(f"      Within 20%: {n_under_20}/{n}")
    print()
    print("  • What the substrate captures:")
    print("      - Pion exchange as the long-range nuclear force")
    print("      - Goldberger-Treiman coupling from f_π")
    print("      - Coulomb energy from substrate α")
    print("      - α-cluster structure for A=4n nuclei")
    print()
    print("  • What requires further substrate work:")
    print("      - Tensor force and SD mixing in the deuteron (dominant")
    print("        contribution; we use a phenomenological scalar factor)")
    print("      - Asymmetry coefficient a_a (kinetic Fermi-gas + symmetry")
    print("        potential — needs Pauli-blocked many-body)")
    print("      - Pairing scale a_p (BCS-like residual interaction)")
    print()


if __name__ == "__main__":
    main()
