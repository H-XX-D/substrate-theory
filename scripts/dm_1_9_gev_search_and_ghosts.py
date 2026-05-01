"""Search for ~1.9 GeV DM signals + explanation of ghost particles.

PART 1: Where in observational data could a 1.9 GeV substrate-DM
candidate hide or appear? Comprehensive survey of:
  - Direct detection (XENON, LZ, PandaX, DAMIC, SuperCDMS)
  - Indirect detection (Fermi-LAT GeV excess, AMS-02 positrons)
  - Collider missing-energy / dijet / diphoton in 1-3 GeV window
  - Beam-dump experiments (NA64, SHiP, LDMX)
  - Astrophysical (Galactic Center, dwarf spheroidals)
  - Light dark photon / hidden photon constraints (BaBar, Belle, NA48)

PART 2: What are 'ghost particles' in QFT, and how does the substrate
framework reinterpret them?
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("Part 1: Signature search for ~1.9 GeV substrate DM")
    print("=" * 70)
    print()

    print("DIRECT DETECTION (would see if monopole channel present):")
    print("-" * 70)
    direct = [
        ('XENON-nT (2023)',  '> 6 GeV WIMP-N',  'No signal'),
        ('LZ (2024)',         '> 9 GeV WIMP-N', 'No signal'),
        ('PandaX-4T',         '> 4 GeV WIMP-N', 'No signal'),
        ('DAMIC-M',           '0.1 - 10 GeV',   'No signal at 10⁻⁴¹ cm²'),
        ('SuperCDMS-SNOLAB',  '0.5 - 10 GeV',   'No signal'),
        ('CRESST-III',        '0.1 - 1 GeV',    'No signal'),
        ('DarkSide-50',       '1.8 - 6 GeV',    'No signal'),
    ]
    print(f"{'experiment':>20s}  {'mass range':>20s}  {'1.9 GeV result':>30s}")
    for name, range_, result in direct:
        print(f"  {name:>18s}    {range_:>18s}    {result:>28s}")
    print()
    print("Substrate-DM at 1.9 GeV: cube cell, no monopole, dipole only via")
    print("higher multipoles. ALL these experiments primarily target the")
    print("monopole channel. Substrate-DM would be invisible to them.")
    print()

    print("INDIRECT DETECTION (DM annihilation/decay signatures):")
    print("-" * 70)
    print()
    indirect = [
        ('Fermi-LAT Galactic Center', '1-3 GeV γ-ray excess',
         'Long-standing ~3σ excess at ~1-2 GeV — '
         'COULD be 1.9 GeV DM annihilation signal'),
        ('AMS-02 positron fraction', 'rises above 10 GeV',
         'No specific 1.9 GeV feature; consistent with substrate-DM null'),
        ('IceCube high-E ν', '> TeV', 'irrelevant'),
        ('Planck CMB', 'spectral, polarization', 'limits DM annihilation'),
        ('Reticulum II dwarf', '< 100 GeV',
         'Marginal excess at GeV scale, ~2σ'),
    ]
    print(f"{'experiment':>30s}  {'channel':>22s}  {'status':>20s}")
    for name, ch, status in indirect:
        print(f"  {name:>28s}    {ch:>20s}")
        print(f"     → {status}")
    print()
    print("THE FERMI GeV EXCESS: persistent gamma-ray excess from Galactic")
    print("Center at ~1-3 GeV peak. Could be:")
    print("  - Millisecond pulsars (most likely conventional)")
    print("  - DM annihilation at ~30-50 GeV → bb (standard hypothesis)")
    print("  - DM annihilation at ~1.9 GeV → light-quark final states")
    print("    (substrate framework prediction!)")
    print()
    print("Substrate cube-DM at 1.9 GeV → annihilates via cube-substrate")
    print("coupling → produces low-energy quark pairs → diffuse 1-3 GeV")
    print("γ-ray signature matching observed Fermi excess.")
    print()

    print("COLLIDER SEARCHES in 1-3 GeV window:")
    print("-" * 70)
    print()
    collider = [
        ('LHC missing E_T', 'broad spectrum, no specific 2 GeV peak'),
        ('B-factories (BaBar, Belle II)', 'A\' / dark photon < 8 GeV'),
        ('NA48/2 (CERN)',     'light scalar < 100 MeV'),
        ('NA64 (CERN)',       'A\' < 1.5 GeV from missing-energy'),
        ('LHCb dimuon', 'dark photon < 70 GeV via di-μ'),
        ('Belle II', '~60 ab⁻¹ planned, dark sector at GeV scale'),
    ]
    print(f"{'experiment':>30s}  {'finding':>28s}")
    for name, finding in collider:
        print(f"  {name:>28s}    {finding}")
    print()
    print("Belle II is the most sensitive UPCOMING search for ~1-2 GeV")
    print("dark sector. Will reach mixing parameter ε² ~ 10⁻¹⁰ over the")
    print("next decade — substrate-cube-DM at 1.9 GeV is in this window.")
    print()

    print("ASTROPHYSICAL (DM halos, dwarf galaxies):")
    print("-" * 70)
    print()
    print("  Bullet cluster / cluster lensing: confirms DM is collisionless")
    print("  → substrate cube-DM (only quadrupole+ self-interaction) → ✓")
    print()
    print("  Dwarf spheroidal density profiles: show core-cusp tension")
    print("  → light DM (~1-10 GeV) with self-interaction can resolve")
    print("  → substrate cube-DM at 1.9 GeV with quadrupole self-coupling → ✓")
    print()
    print("  Cosmic 21cm absorption (EDGES anomaly): reported absorption")
    print("  at z ~ 17 deeper than ΛCDM expects. Could be due to DM-baryon")
    print("  scattering at ~1 GeV scale.")
    print("  → substrate cube-DM at 1.9 GeV could match")

    # ============== Part 2: Ghost particles ==============
    print()
    print()
    print("Part 2: What are 'ghost particles' in QFT?")
    print("=" * 70)
    print()
    print("In QFT, GHOST PARTICLES are auxiliary fields that:")
    print("  - Have negative-norm states (anti-commute when they 'should' commute)")
    print("  - Don't appear as physical asymptotic states")
    print("  - Are needed for mathematical consistency (gauge invariance)")
    print("  - Cancel un-physical degrees of freedom in path integrals")
    print()

    print("TYPES OF GHOSTS:")
    print()
    ghost_types = [
        ('Faddeev-Popov ghosts',
         'Gauge fixing in non-abelian gauge theories (QCD, EW). One ghost '
         'per gauge boson. Cancel un-physical longitudinal polarizations.'),
        ('Pauli-Villars ghosts',
         'Heavy regulator fields with wrong-sign kinetic term. Cancel '
         'UV divergences in loop integrals.'),
        ('BRST ghosts',
         'Generalize Faddeev-Popov; provide a global symmetry of the '
         'gauge-fixed action.'),
        ('Stueckelberg ghosts',
         'Restore gauge invariance for massive vector fields without Higgs.'),
        ('Goldstone ghosts',
         'Eaten by gauge bosons in Higgs mechanism (Goldstone boson '
         'becomes longitudinal mode of W/Z).'),
    ]
    for name, desc in ghost_types:
        print(f"  {name}:")
        print(f"    {desc}")
        print()

    print("=" * 70)
    print("Substrate framework interpretation of ghosts:")
    print("=" * 70)
    print()
    print("In substrate, ghosts are NOT separate particles — they're DEGREES")
    print("of FREEDOM that don't propagate physically because of constraints.")
    print()
    print("Specifically:")
    print("  - The 45° cone constraint REMOVES degrees of freedom from")
    print("    substrate strain (Lagrange multiplier λ_cone in MODEL.md §9)")
    print("  - Möbius half-flux topology FORBIDS certain modes")
    print("  - The B3 inventory has n_F = 12 'forbidden modes' (unphysical")
    print("    states that don't appear as real particles)")
    print()
    print("So in the substrate picture:")
    print("  Faddeev-Popov ghosts ↔ longitudinal modes removed by 45° cone")
    print("  Pauli-Villars ghosts ↔ substrate UV cutoff at φ_max (saturation)")
    print("  Goldstone modes      ↔ absorbed into Möbius half-flux of W/Z")
    print()
    print("No SEPARATE ghost particles — just SUBSTRATE constraints that")
    print("eliminate unphysical degrees of freedom geometrically.")
    print()
    print("Cleaner than QFT: in QFT you ADD ghosts to subtract bad d.o.f.;")
    print("in substrate you NEVER HAD the bad d.o.f. (constraints prevent them).")


if __name__ == "__main__":
    main()
