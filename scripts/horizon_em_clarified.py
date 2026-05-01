"""Clarified: EM outside horizon escapes; only EM that crossed horizon is trapped.

User correction: my earlier framing was imprecise. The accurate picture:

  EVENT HORIZON is the boundary.
  Outside the horizon (σ < 1/2, cone < 90°): EM propagates normally,
  including light from accretion disks, jets, magnetospheres, hot gas.
  This light CAN reach distant observers.

  Inside the horizon (σ = 1/2, cone tilted past 90°): EM has no outward
  future direction. Light that has already crossed inward cannot be
  received by external observers — that's WHAT a BH is.

For mergers:
  NS-NS: no horizon present (NS is dense star, not BH). All matter
  is outside any horizon → photons escape freely → multimessenger.

  BH-BH in vacuum: TWO horizons present, surrounded by ~empty space.
  No matter outside horizons to make photons → EM silence.

  BH-BH in dense gas (AGN): horizons surrounded by accretion disk.
  Accretion gas DOES emit EM. Substrate predicts circumbinary EM
  signatures — and these are sometimes seen (GW190521 candidate).

So the real reason BH-BH is usually EM silent is:
  - Most stellar-mass BH binaries are in low-density environments
  - Pure vacuum binary: only GW from spacetime ripple
  - In dense environment: EM possible from circum-environment
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("Horizon causality clarified: only matter inside horizon is trapped")
    print("=" * 70)
    print()
    print("Standard horizon causality (consistent with substrate cone-tilting):")
    print()
    print("  OUTSIDE event horizon (σ < 1/2):")
    print("    Cone tilt < 90°")
    print("    Outward future direction exists")
    print("    EM propagates normally")
    print("    Light from accretion disks, jets, magnetospheres → escapes")
    print()
    print("  INSIDE event horizon (σ = 1/2 saturated):")
    print("    Cone tilt > 90°")
    print("    No outward future direction")
    print("    EM that crossed inward cannot escape outward")
    print("    Information from inside cannot be received outside")
    print()
    print("=" * 70)
    print("Why BH-BH mergers are typically EM silent")
    print("=" * 70)
    print()
    print("BH-BH mergers radiate GW from the inspiral and merger of two horizons.")
    print("EM signal depends entirely on what matter is OUTSIDE the horizons.")
    print()
    cases = [
        ('Stellar-mass BH-BH in galactic field',
         'low gas density (~1 atom/cm³)',
         'almost no EM — GW only'),
        ('BH-BH in star cluster',
         'low gas density',
         'weak EM if any (some gas heating possible)'),
        ('BH-BH in AGN disk (e.g., GW190521 candidate)',
         'dense gas around supermassive BH',
         'circumbinary disk shocking → POSSIBLE EM signature'),
        ('Primordial BH mergers',
         'no surrounding matter',
         'GW only, no EM'),
        ('NS-NS merger (e.g., GW170817)',
         'two neutron stars (no horizons)',
         'multimessenger — all photons escape'),
        ('NS-BH merger',
         'NS material outside BH horizon, kicked off',
         'GW + KILONOVA EM signature (some events show)'),
    ]
    print(f"{'merger type':>40s}    {'environment':>30s}    {'EM signature':>30s}")
    for typ, env, em in cases:
        print(f"  {typ:>38s}      {env:>28s}      {em:>28s}")
    print()

    print("=" * 70)
    print("Empirical pattern (LIGO/Virgo to date)")
    print("=" * 70)
    print()
    print("BH-BH events: ~150 detections, 0-1 marginal EM counterpart")
    print("  GW190521: tentative AGN-flare association (Graham+ 2020)")
    print("  Could be circum-disk gas response, not from horizons themselves")
    print()
    print("NS-NS: GW170817 + a few candidates")
    print("  All show multimessenger signatures")
    print("  EM from outside the (non-existent or marginal) horizons")
    print()
    print("Pattern matches substrate prediction:")
    print("  EM from BH-BH merger requires gas/matter outside horizons")
    print("  Most merger environments have insufficient matter → EM silent")

    print()
    print("=" * 70)
    print("Substrate-specific test")
    print("=" * 70)
    print()
    print("Substrate predicts that EM signal accompanying BH-BH merger MUST come")
    print("from circum-environment, not from inside horizons. Tests:")
    print()
    print("1. Spectral lines: any EM signal should show signatures of")
    print("   circum-environment gas (specific atomic transitions, ionization),")
    print("   NOT broad continuum from 'inside the BH'")
    print()
    print("2. Spatial offset: EM should be co-spatial with circum-environment")
    print("   (e.g., AGN disk), not centered on the BH-BH coalescence point")
    print()
    print("3. Time delay: EM signal arrival should be delayed relative to GW peak")
    print("   by light-travel-time across circum-environment, not strictly co-arrival")
    print()
    print("All three of these are testable with future LIGO + Roman + Vera Rubin")
    print("multi-messenger campaigns. Substrate predicts they will all confirm")
    print("circum-environment origin (no EM from inside the merging BHs).")


if __name__ == "__main__":
    main()
