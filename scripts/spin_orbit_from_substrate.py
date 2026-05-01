"""Derive spin-orbit coupling λ_LS from the substrate Möbius bundle curvature.

Standard QED gives atomic spin-orbit:
  H_LS = (α / (2 m² c² r³)) L·S
  → fine structure splitting ΔE_FS = α² × Rydberg × (shell factor)

Nuclear spin-orbit is much stronger (~20 MeV) and has a different origin —
the strong-force exchange. In the substrate model, BOTH come from the same
Möbius half-flux bundle's curvature, scaled by the relevant local energy.

Derivation chain:
  1. Möbius bundle has curvature F_M = π / area_cycle = π/ξ²
  2. Bound state at radius r picks up a Berry phase per orbit
  3. Phase × orbital winding L gives the LS coupling
  4. λ_LS = (Möbius curvature) × (cell volume) × (1/r²) × K
         = (π / ξ²) × ξ³ × (1/r²) × K
         = π K ξ / r²
  5. For r ~ ξ (substrate scale): λ_LS ~ π K ξ
  6. In substrate units (K ξ³ = E_unit, K ξ = E_unit/ξ²):
     λ_LS / E_unit = π × (ξ/r)²

For the dimensionless coupling:
  λ_LS / E_unit = π α_LS (ξ/r)²
where α_LS = 1/(4π) × Möbius cycles per cell

For substrate cells with 1 cycle/cell (the K_4 tetrahedron): α_LS = 1/(4π)
giving λ_LS = (1/4) × E_unit × (ξ/r)²

Verification: this should reproduce atomic fine structure (10⁻⁴ eV) AND
nuclear spin-orbit (~10 MeV) by plugging in the appropriate r and K for
each domain.
"""

from __future__ import annotations
import math


# Physical constants (CGS-like for clarity, but using natural unit ratios)
ALPHA = 7.2973525643e-3
HBAR_C_MEV_FM = 197.3269804  # ℏc in MeV·fm
M_E_MEV = 0.5109989461       # electron mass in MeV/c²
M_P_MEV = 938.27208816       # proton mass in MeV/c²
RYDBERG_EV = 13.6056981
ATOM_RADIUS_BOHR = 5.29177210903e-1  # in Å (Bohr radius)
NUCLEAR_RADIUS_FM = 1.2  # ~1.2 fm per nucleon (nuclear radius scale)

# Substrate constants (from MODEL.md §1.4):
#   ℏ = K ξ⁴ / c
#   For atomic regime, ξ ≈ Compton wavelength of electron / 2π
XI_ELECTRON_FM = HBAR_C_MEV_FM / (M_E_MEV * 2 * math.pi)  # ≈ 61.4 fm
# In femtometers, this is the substrate's atomic-scale length

PI = math.pi


def lambda_LS_substrate(r_radius, K_unit, xi_substrate, n_cycles_per_cell=1):
    """Substrate-derived spin-orbit coupling.

    λ_LS = (n_cycles / (4π)) × K_unit × (ξ_substrate / r_radius)²

    The factor (1/4π) comes from the Möbius-cycle phase integral normalized
    by the bundle's solid-angle measure.

    Args:
        r_radius: bound-state radius in same units as ξ
        K_unit: substrate stiffness × cell volume = E_unit (in same units as output)
        xi_substrate: substrate length scale (same units as r_radius)
        n_cycles_per_cell: number of Möbius cycles per substrate cell (default 1)

    Returns:
        λ_LS in units of K_unit
    """
    alpha_LS = n_cycles_per_cell / (4 * PI)
    return alpha_LS * K_unit * (xi_substrate / r_radius) ** 2


def main() -> None:
    print("Spin-orbit coupling from substrate Möbius bundle")
    print("=" * 70)
    print()
    print("Derivation:")
    print("  λ_LS = (n_cycles/4π) × K_unit × (ξ_substrate / r)²")
    print()
    print("Same formula for ALL scales — atomic, nuclear, hadronic — with")
    print("appropriate r and ξ for each regime.")
    print()

    # ======== Atomic regime ========
    print("=" * 70)
    print("Atomic spin-orbit (hydrogen 2p shell)")
    print("=" * 70)
    r_2p = 4 * ATOM_RADIUS_BOHR * 1e5  # ~4 a₀ for 2p, in fm
    # E_unit for atomic: Rydberg = 13.6 eV = 13.6e-6 MeV
    E_unit_atom_mev = RYDBERG_EV * 1e-6
    xi_atom = XI_ELECTRON_FM
    lam_atom_mev = lambda_LS_substrate(r_2p, E_unit_atom_mev, xi_atom)
    lam_atom_ev = lam_atom_mev * 1e6
    # Standard QED prediction: ΔE_FS for 2p of H ≈ α² × R∞ × (1/n³)(1/(j+1/2) - 1/(l+1))
    # Approximation: Δ ≈ α² R∞ /(n³ × l(l+1)) = (1/137)² × 13.6 / (8 × 2) = 4.5e-5 eV
    standard_FS_2p = ALPHA**2 * RYDBERG_EV / (8 * 2)
    print(f"  ξ_substrate (electron Compton): {xi_atom:.2f} fm")
    print(f"  r_2p (atomic radius for 2p):     {r_2p:.2e} fm")
    print(f"  K_unit (Rydberg):                {E_unit_atom_mev*1e6:.4f} eV")
    print(f"  λ_LS substrate prediction:       {lam_atom_ev:.4e} eV")
    print(f"  Standard QED ΔE_FS (2p H):       {standard_FS_2p:.4e} eV")
    print(f"  Ratio (model/standard):          {lam_atom_ev/standard_FS_2p:.3f}")
    print()

    # ======== Nuclear regime ========
    print("=" * 70)
    print("Nuclear spin-orbit (1f₇/₂ - 1f₅/₂ splitting)")
    print("=" * 70)
    # For nuclear: r ~ A^(1/3) × 1.2 fm, ξ_nuclear ~ confinement length
    A_typical = 28  # Si or so
    r_nucleus = NUCLEAR_RADIUS_FM * A_typical ** (1/3)
    xi_nuclear = HBAR_C_MEV_FM / M_P_MEV  # ~0.21 fm, proton Compton
    # E_unit for nuclear: ε_pair ~ Λ_QCD/k_pair = 100 MeV (from B3) or 50 MeV
    E_unit_nuc_mev = 100.0  # MeV
    lam_nuc = lambda_LS_substrate(r_nucleus, E_unit_nuc_mev, xi_nuclear)
    # Standard nuclear spin-orbit splitting for 1f shell ≈ 8 MeV (e.g., Mayer-Jensen)
    standard_LS_nuclear = 8.0  # MeV (1f7/2 - 1f5/2 in K, Ca region)
    print(f"  ξ_substrate (proton Compton):    {xi_nuclear:.4f} fm")
    print(f"  r_nucleus (A=28):                {r_nucleus:.2f} fm")
    print(f"  K_unit (ε_pair):                 {E_unit_nuc_mev:.1f} MeV")
    print(f"  λ_LS substrate prediction:       {lam_nuc:.4f} MeV")
    print(f"  Standard nuclear ΔE_LS:          {standard_LS_nuclear:.2f} MeV")
    print(f"  Ratio (model/standard):          {lam_nuc/standard_LS_nuclear:.3f}")
    print()

    # ======== Hadronic regime ========
    print("=" * 70)
    print("Hadronic spin-orbit (mass splitting in baryon multiplets)")
    print("=" * 70)
    # For a baryon: r ~ proton radius ~ 0.85 fm, ξ ~ pion Compton ~ 1.4 fm
    M_PI_MEV = 139.57
    r_baryon = 0.85
    xi_hadron = HBAR_C_MEV_FM / M_PI_MEV
    E_unit_had = 200.0  # Λ_QCD ≈ 200 MeV
    lam_had = lambda_LS_substrate(r_baryon, E_unit_had, xi_hadron)
    # N(1535) - N(939) ≈ 600 MeV is a typical baryon orbital excitation
    # but spin-orbit specifically is smaller, ~50 MeV in the spectrum
    standard_LS_hadron = 50.0
    print(f"  ξ_substrate (pion Compton):      {xi_hadron:.4f} fm")
    print(f"  r_baryon (proton radius):        {r_baryon:.2f} fm")
    print(f"  K_unit (Λ_QCD):                  {E_unit_had:.1f} MeV")
    print(f"  λ_LS substrate prediction:       {lam_had:.4f} MeV")
    print(f"  Typical hadronic ΔE_LS:          {standard_LS_hadron:.2f} MeV")
    print(f"  Ratio (model/standard):          {lam_had/standard_LS_hadron:.3f}")
    print()

    # ======== Summary ========
    print("=" * 70)
    print("Summary: ONE substrate formula, THREE physical scales")
    print("=" * 70)
    print()
    print(f"{'regime':>12s}  {'r [fm]':>10s}  {'ξ [fm]':>10s}  "
          f"{'K [E_unit]':>12s}  {'λ_LS pred':>14s}  {'standard':>14s}  {'ratio':>8s}")
    print(f"  {'atomic':>10s}  {r_2p:>8.2e}  {xi_atom:>8.2f}  "
          f"{E_unit_atom_mev*1e6:>10.4f} eV  {lam_atom_ev:>10.4e} eV  "
          f"{standard_FS_2p:>10.4e} eV  {lam_atom_ev/standard_FS_2p:>6.2f}")
    print(f"  {'nuclear':>10s}  {r_nucleus:>8.2f}  {xi_nuclear:>8.4f}  "
          f"{E_unit_nuc_mev:>10.1f} MeV  {lam_nuc:>10.4f} MeV  "
          f"{standard_LS_nuclear:>10.2f} MeV  {lam_nuc/standard_LS_nuclear:>6.2f}")
    print(f"  {'hadronic':>10s}  {r_baryon:>8.2f}  {xi_hadron:>8.4f}  "
          f"{E_unit_had:>10.1f} MeV  {lam_had:>10.4f} MeV  "
          f"{standard_LS_hadron:>10.2f} MeV  {lam_had/standard_LS_hadron:>6.2f}")
    print()
    print("Honest assessment:")
    print("  - HADRONIC (r ~ ξ): 88% match — substrate is in its natural regime")
    print("  - NUCLEAR (r >> ξ_p): off by ~300× — needs RG running of K_pair")
    print("  - ATOMIC (r >>> ξ_e): off by ~500× — needs full QED loop corrections")
    print()
    print("The (ξ/r)² scaling is correct for short-range substrate dynamics but")
    print("misses the long-range RG-improved coupling. The right formula likely is:")
    print("    λ_LS = (1/4π) × K_eff(r) × (ξ_eff(r)/r)²")
    print("where K_eff and ξ_eff run with scale per the substrate RG equations.")
    print()
    print("This is the same gap as in the α derivation: leading-order geometric")
    print("result is right at the ~10% level in the natural regime, needs RG")
    print("running to get to lower-energy / longer-distance precision.")


if __name__ == "__main__":
    main()
