"""Why BH mergers radiate GW but NO photons — substrate explanation.

User insight: BH-BH mergers produce gravitational waves but essentially
NO electromagnetic counterpart. This follows directly from the substrate
picture of BHs as saturated regions where the future cone has tilted
past 90°.

Observational fact:
  LIGO/Virgo: 100s of binary BH mergers detected
  Confirmed EM counterpart: ZERO
  (one marginal claim from GW190521 — disputed)

  Neutron star mergers (GW170817): BOTH GW and EM detected
  Reason: NS material is OUTSIDE event horizon → photons CAN escape

Substrate explanation:

  GRAVITATIONAL WAVES are bulk substrate-strain perturbations.
  They propagate from any region — including saturated interiors —
  because they're TRANSVERSE in the substrate field, not constrained
  by the cone-tilting at horizons.

  PHOTONS are also transverse substrate modes BUT they need to
  propagate OUT of the merger region. From inside saturated BH
  interiors (cone tilted past 90°), no outward-propagating
  trajectory exists. So no photons escape.

  When matter is OUTSIDE the horizon (NS-NS merger), photons can
  freely escape — both GW and EM signals detected.

  When BOTH merging objects are saturated (BH-BH), the merger
  energy goes into substrate-strain ripples (GW) but cannot
  propagate outward as transverse-mode (EM) photons.

This is a STRUCTURAL prediction of the substrate framework that
distinguishes it from any "BH = vacuum spacetime curvature" picture.
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("BH mergers: GW yes, EM no — substrate explanation")
    print("=" * 70)
    print()
    print("Observational fact (LIGO/Virgo + EM follow-up since 2015):")
    print()
    events = [
        ('BH-BH (GW150914)',     'first detection',     'GW only, no EM'),
        ('BH-BH (~150 events)',  'O1-O4 runs',          'GW only, no EM in any'),
        ('NS-NS (GW170817)',     'multimessenger',      'GW + γ-ray + optical + radio + ν'),
        ('NS-BH (GW200115)',     '4 events 2024',       'GW only, no EM'),
        ('BH-BH GW190521',       'most massive',        'marginal optical claim — disputed'),
    ]
    print(f"{'event class':>25s}    {'examples':>20s}    {'EM signal':>30s}")
    for cls, ex, em in events:
        print(f"  {cls:>23s}      {ex:>18s}      {em:>30s}")
    print()
    print("Empirical pattern: BH-BH = GW only; NS-NS = GW + EM.")
    print()

    print("=" * 70)
    print("Substrate explanation")
    print("=" * 70)
    print()
    print("GRAVITATIONAL WAVES = bulk substrate-strain ripples")
    print("  - Transverse mode in (∇²P) field = strain perturbation")
    print("  - Propagates from any substrate state (saturated or not)")
    print("  - Cone-tilting at horizon doesn't block them — they're bulk")
    print()
    print("PHOTONS = transverse mode in P field (substrate strain)")
    print("  - Must propagate OUTWARD from emission region")
    print("  - Inside saturated BH (cone tilted >90°), outward future-cone")
    print("    direction doesn't exist → no outward propagation possible")
    print("  - From OUTSIDE horizon: photons propagate normally")
    print()
    print("NS-NS merger: matter OUTSIDE horizons")
    print("  - Both GW (bulk strain) and EM (outward-propagating photons) emitted")
    print()
    print("BH-BH merger: matter INSIDE horizons (saturated)")
    print("  - GW emitted (bulk strain ripple from merger geometry)")
    print("  - EM cannot escape (cone tilted past 90° → no outward future)")
    print("  - Result: GW only, no EM")
    print()

    print("=" * 70)
    print("Why GW can escape but EM cannot")
    print("=" * 70)
    print()
    print("Both GW and EM are transverse substrate modes. Why does GW escape")
    print("from saturated regions but EM doesn't?")
    print()
    print("Answer: GW is a perturbation of the SUBSTRATE STRUCTURE itself,")
    print("not propagation OF excitations THROUGH substrate. It's the bulk")
    print("medium responding to the merger geometry — a wave IN the substrate")
    print("strain pattern, not a wave OF an excitation in substrate.")
    print()
    print("EM is propagation OF a transverse excitation through substrate.")
    print("It needs a 'forward direction' in spacetime to propagate. Inside")
    print("a saturated BH where future-cone has tilted past 90°, there is")
    print("no forward direction outward — only forward direction inward.")
    print("So EM trapped inside; GW (bulk strain) carries no propagation")
    print("constraint — it just IS the substrate strain pattern of the merger.")
    print()
    print("Analogy: think of a vibrating crystal lattice (GW) vs sound wave")
    print("traveling through it (EM). The lattice vibration affects everything")
    print("globally; the sound wave needs a direction to go.")
    print()

    # Quantitative
    print("=" * 70)
    print("Quantitative predictions for BH-BH merger luminosity")
    print("=" * 70)
    print()
    print("GW luminosity (peak): L_GW ~ c⁵/G ~ 10⁵⁹ erg/s")
    print("EM luminosity from inside BHs: ZERO")
    print("EM luminosity from circumbinary disk (if present): ~10⁴⁰-10⁴⁴ erg/s")
    print()
    print("Substrate prediction: any BH-BH merger γ-ray signal must come")
    print("from MATTER OUTSIDE the horizons (e.g., circumbinary disk gas")
    print("being shocked by the merger). NOT from the BH-BH event itself.")
    print()
    print("Observational test:")
    print("  - GW190521 marginal optical signal: comes from a circum-AGN gas")
    print("    being disturbed by recoil (NOT from inside the merging BHs)")
    print("  - This is consistent with substrate prediction")
    print("  - Confirmation if more BH-BH mergers in dense gas environments show")
    print("    similar circum-environment-only signatures")
    print()

    # Also Hawking radiation case
    print("=" * 70)
    print("Why isn't Hawking radiation suppressed by the same mechanism?")
    print("=" * 70)
    print()
    print("Hawking radiation comes from quantum substrate fluctuations at")
    print("the horizon — where cone is exactly tilted to 90°.")
    print()
    print("At the horizon, δσ < 0 fluctuations momentarily tip cone back")
    print("below 90° → outward propagation becomes briefly possible →")
    print("photon escapes. This is the substrate version of pair production")
    print("at horizon (Hawking 1976).")
    print()
    print("From DEEP INSIDE the BH (cone fully tilted >>90°), no such")
    print("fluctuation can ever point outward → no photon emission from")
    print("interior. All emission is at the horizon surface.")
    print()
    print("BH-BH merger case: the merging BHs are surrounded by saturated")
    print("substrate. Their interaction is a GLOBAL substrate strain change")
    print("(GW), not localized photon production. Hence GW only.")


if __name__ == "__main__":
    main()
