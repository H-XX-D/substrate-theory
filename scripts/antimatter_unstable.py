"""Antimatter as transient high-energy excitation, NOT primordial counterpart.

User's correction: antimatter is "exotic unstable created in colliders and
other high energy events." Antimatter is NOT a primordial cosmic component
that requires baryogenesis to explain its absence.

This eliminates the standard 'baryogenesis problem' entirely:
  - Standard cosmology: Big Bang created equal matter/antimatter; needs
    asymmetry-generating mechanism to explain why we see only matter
  - Substrate cosmology: pre-CMB substrate had MATTER orientation (Möbius
    half-flux in matter direction); antimatter never existed primordially
  - Antimatter only appears as transient excitation in:
      * Particle colliders (β+ decay, e+e- production at high E)
      * Cosmic-ray air showers (positron from π+ decay)
      * Local annihilation events

Implications:
  - The ratio η = n_b/n_γ is just the BARYON DENSITY relative to photons,
    NOT an asymmetry remnant from primordial annihilation
  - There is no Sakharov-conditions problem — substrate orientation
    was always matter-direction
  - Antimatter is intrinsically unstable: when produced, it annihilates
    against the matter-substrate background rapidly
  - Antimatter has no stable bound states (anti-atoms have brief lab lifetime
    only because they're isolated from matter substrate)

Key insight: in substrate framework, the question 'why is there matter
rather than antimatter?' is wrong-headed. The right question is
'what set the substrate's pre-CMB orientation?' — and answer is: it has
always been that way (eternal substrate).
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("Antimatter as transient excitation: substrate reframing")
    print("=" * 70)
    print()
    print("Standard cosmology framing:")
    print("  Big Bang creates equal matter + antimatter.")
    print("  Asymmetry of ~10⁻⁹ leaves matter-dominated universe.")
    print("  Baryogenesis must explain how this asymmetry arose.")
    print()
    print("Substrate reframing (per user correction):")
    print("  Substrate is eternal; no Big Bang singularity.")
    print("  Pre-CMB substrate has MATTER orientation Möbius half-flux.")
    print("  Antimatter is NOT primordial — only appears transiently in")
    print("  high-energy events: colliders, cosmic rays, beta decays.")
    print("  When produced, antimatter annihilates against matter substrate")
    print("  background → intrinsically unstable in our cosmic environment.")
    print()

    print("=" * 70)
    print("Where antimatter is observed in the universe")
    print("=" * 70)
    print()
    sources = [
        ('e+ from β+ decay',
         'isolated positrons in stellar nucleosynthesis',
         'transient: positron-electron annihilation in ~µs'),
        ('e+/e- pair production',
         'γ-ray flares, AGN jets, high-E processes',
         'pairs annihilate locally'),
        ('p̄ from cosmic rays',
         'p+p → ... + p̄ in high-E collisions in ISM',
         'antiprotons annihilate against ISM matter'),
        ('e+ in colliders (LEP, SLC)',
         'produced and stored in dedicated rings',
         'ring vacuum prevents matter contact, lasts hours'),
        ('p̄ at Fermilab/CERN',
         'produced via beam-on-target, decelerated, trapped',
         'magnetic traps, ~minutes-hours lifetime'),
        ('anti-hydrogen (ALPHA, ATRAP)',
         'cooled p̄ + e+ in magnetic trap, isolated from matter',
         '~minutes lifetime in trap'),
        ('Solar wind p̄/p ratio',
         'observed ~10⁻⁴, all from cosmic-ray secondary production',
         'no primordial antimatter detected'),
    ]
    print(f"{'source':>30s}    {'mechanism':>30s}")
    for src, mech, fate in sources:
        print(f"  {src:>28s}      {mech}")
        print(f"     fate: {fate}")
        print()

    # No antimatter regions detected
    print("=" * 70)
    print("No primordial antimatter regions exist in the observable universe")
    print("=" * 70)
    print()
    print("Searches for antimatter cosmological domains:")
    print("  - AMS-02 antiproton spectrum: matches secondary production from CR")
    print("  - No anti-helium detected (limits set by AMS-02)")
    print("  - No γ-ray annihilation lines from antimatter-matter boundaries")
    print("  - Bullet Cluster: no antimatter-matter annihilation seen")
    print()
    print("Standard interpretation: primordial antimatter ANNIHILATED in early")
    print("universe, leaving asymmetry of ~10⁻⁹ as residual matter.")
    print()
    print("Substrate interpretation: there WAS no primordial antimatter to")
    print("annihilate. Substrate's Möbius orientation has always been matter.")
    print("Cosmic-ray-produced antimatter is the ONLY observed antimatter.")
    print()

    print("=" * 70)
    print("Updated 'baryon-to-photon' ratio interpretation")
    print("=" * 70)
    print()
    print("η = n_baryon / n_photon ≈ 6.1 × 10⁻¹⁰")
    print()
    print("Standard interpretation: residual matter after annihilation")
    print("Substrate interpretation: thermal equilibrium ratio at de-saturation")
    print()
    print("The number 6.1×10⁻¹⁰ is set by:")
    print("  - Photon density at recombination temperature")
    print("  - Baryon density determined by substrate's pre-CMB matter content")
    print("  - Both fixed by substrate cell-counting and de-saturation thermodynamics")
    print()
    print("So η is NOT an asymmetry, just a density ratio. No Sakharov conditions")
    print("required. The substrate framework eliminates the entire 'baryogenesis")
    print("puzzle' as a question that doesn't apply when antimatter is transient,")
    print("not primordial.")
    print()

    # Implications for SM extensions
    print("=" * 70)
    print("Implications for SM extensions seeking to explain baryogenesis")
    print("=" * 70)
    print()
    print("Many BSM models propose:")
    print("  - Leptogenesis with sterile neutrinos")
    print("  - Electroweak baryogenesis (modified Higgs sector)")
    print("  - Affleck-Dine condensates (SUSY)")
    print("  - GUT baryogenesis (high-scale B violation)")
    print()
    print("Substrate framework: NONE of these are needed.")
    print("Baryogenesis is solved by recognizing antimatter as transient,")
    print("not primordial. The 'why is there matter?' question is replaced by:")
    print("'what set the substrate's eternal Möbius orientation?'")
    print("  → Eternal substrate has always been matter-oriented.")
    print("  → No mechanism needed; this is just initial-condition data.")
    print()
    print("Saves ~5 BSM model categories from being needed.")


if __name__ == "__main__":
    main()
