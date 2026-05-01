"""Double-slit with laser: substrate explanation of wave-particle duality.

Standard QM picture:
  - Photon is both wave and particle (duality)
  - Single photons through two slits: still get interference pattern
  - Mystery: which slit did the photon go through?
  - Mystery: how does a 'point particle' interfere with itself?

Substrate framework (MODEL.md §3.2):
  - Photon = transverse substrate wave (NOT a point particle)
  - The wave is ALWAYS extended; passes through both slits naturally
  - 'Particle detection' = localized energy transfer to one resonant absorber
  - Wave-particle duality DISSOLVES: just wave + quantized absorbers

Laser provides COHERENT substrate wave (all phases aligned), making
the interference pattern crisp and easily visible. Standard undergrad
physics demonstration.

Substrate predicts SAME interference pattern as QM (because both are
based on linear wave superposition). No quantitative difference.

But qualitatively, substrate ELIMINATES the 'mystery':
  - Wave goes through BOTH slits (always — it's an extended wave)
  - Detection = localized energy transfer to one absorber
  - No 'collapse', no 'superposition of paths', no 'measurement problem'
"""

from __future__ import annotations
import math


PI = math.pi
C_M_S = 2.998e8


def main() -> None:
    print("Double-slit experiment with laser: substrate explanation")
    print("=" * 70)
    print()
    print("Standard QM 'mystery':")
    print("  Single photon through two slits → interference on screen")
    print("  Many runs build up pattern (one photon at a time)")
    print("  How does a 'particle' interfere with itself?")
    print("  Which slit did the photon go through?")
    print("  → Wave-particle duality, complementarity principle")
    print()
    print("Substrate explanation:")
    print("  Photon = transverse substrate wave (extended, not a point)")
    print("  Wave goes through BOTH slits (naturally — it's a wave)")
    print("  Two wave components interfere on screen")
    print("  Energy distribution = standard interference pattern")
    print("  Absorber atoms in screen are QUANTIZED — only certain transitions")
    print("  When wave reaches an absorber, ONE absorber transitions →")
    print("    appears as 'single photon detection'")
    print()
    print("Key insight: the wave is REAL and EXTENDED at all times.")
    print("The 'particle' is the QUANTIZED RESPONSE of absorbers, not the")
    print("EM field itself.")
    print()

    # Setup
    wavelength_nm = 632.8  # HeNe laser red
    slit_separation_um = 100  # 0.1 mm
    screen_distance_m = 1.0
    print("=" * 70)
    print("Standard setup (HeNe laser red light)")
    print("=" * 70)
    print()
    print(f"  Wavelength λ = {wavelength_nm} nm = {wavelength_nm*1e-9:.3e} m")
    print(f"  Slit separation d = {slit_separation_um} μm")
    print(f"  Screen distance L = {screen_distance_m} m")
    print()
    fringe_spacing_mm = wavelength_nm*1e-9 * screen_distance_m / (slit_separation_um*1e-6) * 1000
    print(f"  Predicted fringe spacing y = λL/d = {fringe_spacing_mm:.4f} mm")
    print()
    print("Both QM and substrate predict THIS pattern (same wave equation).")
    print("Difference is interpretive, not quantitative.")
    print()

    # Substrate-specific predictions
    print("=" * 70)
    print("Substrate-specific predictions for double-slit (testable)")
    print("=" * 70)
    print()
    print("Most predictions match standard QM. But substrate makes a few")
    print("subtle distinguishing claims:")
    print()
    print("1. NO 'COLLAPSE': substrate wave continues to propagate after")
    print("   detection. Multi-detector experiments should see correlations")
    print("   that don't fit pure point-particle picture.")
    print("   → Standard QM also handles this (decoherence, measurement)")
    print("   → Substrate gives same predictions, no new test here")
    print()
    print("2. 'WHICH-SLIT' MEASUREMENT: putting a detector at one slit")
    print("   destroys the interference (standard QM and substrate agree).")
    print("   Substrate explanation: detector ABSORBS the wave at that slit,")
    print("   removing one of the two paths to the screen → no interference.")
    print()
    print("3. NO 'WAVEFUNCTION COLLAPSE' as a fundamental phenomenon:")
    print("   In substrate, what looks like collapse is just absorber transition.")
    print("   The substrate wave doesn't 'know' or 'choose' anything.")
    print()
    print("4. EXTREMELY-DELAYED-CHOICE EXPERIMENTS:")
    print("   Wheeler's delayed-choice experiment: insert/remove detector after")
    print("   photon has 'passed' the slits. Standard QM: photon reconfigures")
    print("   based on detector state (mysterious).")
    print("   Substrate: wave is extended throughout the apparatus the entire")
    print("   time. Removing detector after the wave has reached the slits")
    print("   doesn't 'change history' — the wave was extended from start.")
    print("   Outcome: same as standard QM at quantitative level.")
    print()

    # Subtle prediction
    print("=" * 70)
    print("Subtle substrate prediction worth investigating")
    print("=" * 70)
    print()
    print("If photons are extended substrate waves with finite COHERENCE")
    print("LENGTH set by substrate properties (rather than by emitter only),")
    print("then SINGLE-PHOTON double-slit at very long path-difference")
    print("(D > coherence length) should show NO interference — even though")
    print("standard QM expects interference for any monochromatic source.")
    print()
    print("Substrate coherence length L_c estimate:")
    print(f"  L_c ~ ℏ × c × Q_substrate / (frequency × kT_room)")
    print(f"  ~ very long for laser (μm to km depending on conditions)")
    print()
    print("This is hard to distinguish from standard QM (which also has")
    print("coherence-length-limited interference). But substrate sets a")
    print("FUNDAMENTAL upper bound on coherence even for ideal sources;")
    print("standard QM allows arbitrarily long coherence in principle.")
    print()
    print("Test: ultra-long-baseline single-photon interferometry. If a")
    print("substrate-set coherence floor exists, it would appear as a hard")
    print("limit on visible fringe contrast at very long path differences.")
    print()
    print("Practical: very hard to test (requires perfect monochromaticity")
    print("and very long stable interferometer baselines).")
    print()

    print("=" * 70)
    print("Bottom line")
    print("=" * 70)
    print()
    print("Double-slit with laser:")
    print("  - Standard demo, works in every undergrad lab")
    print("  - Substrate predicts SAME quantitative result as QM")
    print("  - Substrate INTERPRETATION cleaner: no wave-particle duality,")
    print("    no measurement problem, no collapse — just extended wave +")
    print("    quantized absorber response")
    print("  - Wave-particle duality dissolved: photon IS the wave;")
    print("    'particle' behavior comes from absorber quantization")
    print()
    print("The interpretive gain is large; quantitative predictions identical")
    print("to standard QM at all currently testable precision levels.")


if __name__ == "__main__":
    main()
