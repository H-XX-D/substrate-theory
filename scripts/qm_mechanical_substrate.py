"""Quantum mechanics phenomena as mechanical substrate behavior.

The substrate framework reduces QM phenomena to MECHANICAL behavior of a
3D stiff elastic medium. Each 'mystery' of QM has a mechanical analog:

  - Wave-particle duality       → extended wave + quantized absorbers
  - Tunneling                    → sub-barrier substrate-strain leakage
  - Entanglement                 → correlated substrate-strain patterns
  - Bell-test violations         → coordinated rotation in shared substrate
  - EPR paradox                  → no instantaneous signal; correlations from common origin
  - Measurement problem          → absorber transition (no collapse)
  - Heisenberg uncertainty       → strain-momentum trade-off in substrate
  - Quantum coherence            → substrate-wave phase relations
  - Quantum decoherence          → substrate strain dissipation via drag γ

This isn't a hand-waving 'mechanical analog' — it's literally what the
substrate framework says is happening. The substrate is a real elastic
medium with all the standard mechanical properties (K, ρ, ξ, γ) plus
quantum field theory in that medium.
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("Quantum mechanics as substrate mechanical behavior")
    print("=" * 70)
    print()

    # Tunneling
    print("=" * 70)
    print("1. Quantum tunneling = substrate-strain leakage through barriers")
    print("=" * 70)
    print()
    print("Standard QM: particle 'tunnels' through classically forbidden region")
    print("with probability T ~ exp(-2 ∫ √(2m(V-E))/ℏ dx)")
    print()
    print("Substrate: tunneling is well-known in CLASSICAL elastic media:")
    print("  - Acoustic waves in non-uniform media")
    print("  - Frustrated total internal reflection in optics (evanescent waves)")
    print("  - Sound through air gaps in walls")
    print()
    print("Same mechanism: substrate strain field has nonzero amplitude in")
    print("'forbidden' regions, decaying exponentially. Particle = bound state")
    print("of substrate strain; tunneling = leakage of that strain pattern.")
    print()
    print("This is purely classical wave behavior in a stiff medium.")
    print("Quantum 'spookiness' comes from absorber quantization, not the wave.")
    print()

    # Heisenberg uncertainty
    print("=" * 70)
    print("2. Heisenberg uncertainty = strain-momentum trade-off")
    print("=" * 70)
    print()
    print("Standard QM: Δx · Δp ≥ ℏ/2 (fundamental limit)")
    print()
    print("Substrate: a localized strain pattern needs broader frequency content.")
    print("This is the classical wave-mechanical duality (Fourier-transform pair):")
    print("  Δx · Δk ≥ 1/2  (Heisenberg-Gabor uncertainty for any wave)")
    print()
    print("Multiplying by ℏ (which substrate derives = K ξ⁴/c):")
    print("  ℏ Δk = Δp")
    print("  Δx · Δp ≥ ℏ/2")
    print()
    print("Standard QM 'uncertainty principle' = Heisenberg-Gabor classical")
    print("wave-Fourier theorem applied to the substrate field. Not mysterious.")
    print()

    # Entanglement
    print("=" * 70)
    print("3. Entanglement = correlated substrate-strain patterns")
    print("=" * 70)
    print()
    print("Standard QM: two particles in singlet state |↑↓⟩ - |↓↑⟩ have")
    print("perfectly anti-correlated spins regardless of measurement basis.")
    print("Looks like 'spooky action at a distance' (Einstein).")
    print()
    print("Substrate: when two photons are emitted from a SINGLE atomic")
    print("transition (e.g., parametric down-conversion), they share a")
    print("common origin in the substrate strain field. Their RELATIVE")
    print("phases are SET at emission and propagate without change (no drag")
    print("on transverse modes).")
    print()
    print("When measured at separated detectors, the correlations SEEN are:")
    print("  - Pre-existing in the substrate field (set at emission)")
    print("  - Rotated by detector orientations (basis transformation)")
    print("  - Manifest as classical correlations + quantum measurement")
    print()
    print("No 'spooky action at a distance' — the substrate field carries")
    print("the correlation information continuously between emission and")
    print("detection. Bell violations happen because the substrate's")
    print("Möbius half-flux topology gives non-local rotational coupling")
    print("between the two photon modes.")
    print()

    # Bell tests
    print("=" * 70)
    print("4. Bell test violations = substrate non-local rotation coupling")
    print("=" * 70)
    print()
    print("Bell inequality: any LOCAL HIDDEN-VARIABLE theory predicts")
    print("|S| ≤ 2 for the CHSH correlation function S.")
    print("Quantum predicts |S| = 2√2 ≈ 2.83.")
    print("Experiments (Aspect, then Hensen 2015 loophole-free) confirm 2.83.")
    print()
    print("Substrate: the elastic medium is GLOBALLY connected, not local.")
    print("A change in substrate strain at point A affects substrate field")
    print("everywhere instantly (because medium response is set by the")
    print("equation of motion, not by a particle propagating).")
    print()
    print("BUT: this is not a SIGNAL — it's a substrate response. No")
    print("information can be transmitted faster than c (because substrate")
    print("WAVES propagate at c). Yet correlations from common origin can")
    print("manifest non-locally.")
    print()
    print("This is the substrate version of 'no-signaling theorem': you can")
    print("have non-local correlations without superluminal signaling.")
    print()
    print("Classical analog: two coins flipped simultaneously show correlations")
    print("when examined at distant locations. No information transmitted;")
    print("just shared origin. Substrate generalizes to continuous fields.")
    print()

    # Decoherence
    print("=" * 70)
    print("5. Decoherence = substrate drag γ damping coherent strain")
    print("=" * 70)
    print()
    print("Standard QM: coherent superposition decays into classical mixture")
    print("via 'environmental decoherence' — interaction with many DOF washes")
    print("out phase relations.")
    print()
    print("Substrate: drag γ (already in Lagrangian) causes coherent strain")
    print("modes to lose phase information over time τ ~ 1/Γ_decoh = ω/Q.")
    print()
    print("So the substrate's drag mechanism — which derives α and gives mass —")
    print("ALSO explains decoherence. Same parameter γ, different physics:")
    print("  - At particle scale: drag → mass (cone-bouncing)")
    print("  - At quantum-coherence scale: drag → decoherence")
    print("  - At BH horizon: drag fluctuations → Hawking radiation")
    print()
    print("Single substrate parameter γ, three macroscopic phenomena.")
    print()

    # EPR paradox
    print("=" * 70)
    print("6. EPR paradox = nothing paradoxical in substrate")
    print("=" * 70)
    print()
    print("EPR (1935): if QM is complete, then either:")
    print("  (a) Reality is non-local (action at distance), or")
    print("  (b) QM is incomplete (hidden variables)")
    print()
    print("Substrate: there ARE hidden variables — they're the substrate")
    print("strain field configuration. But they're NOT 'particle properties'")
    print("(which is what EPR meant by hidden). They're CONTINUOUS FIELD")
    print("DEGREES OF FREEDOM in the substrate.")
    print()
    print("Bell tests rule out LOCAL hidden variables, but substrate is")
    print("a non-local field theory (substrate everywhere). So Bell")
    print("violations are CONSISTENT with substrate (just like with QM).")
    print()
    print("EPR's dichotomy is false: substrate is BOTH non-local in field")
    print("structure AND complete (no extra hidden particles needed).")
    print()

    # Schrödinger cat
    print("=" * 70)
    print("7. Schrödinger's cat = decohered substrate strain pattern")
    print("=" * 70)
    print()
    print("Standard QM: cat in box is in superposition |alive⟩ + |dead⟩")
    print("until observation 'collapses' to one.")
    print()
    print("Substrate: macroscopic objects (cats) interact with the substrate")
    print("via ~10²³ atoms × drag γ. Decoherence time τ ~ exp(-N) is essentially")
    print("zero for any macroscopic system. The cat is ALWAYS classical")
    print("(either alive or dead); the 'superposition' is a mathematical")
    print("convenience that has no physical meaning at the cat scale.")
    print()
    print("Quantum behavior is only seen at scales where decoherence time")
    print("exceeds experiment duration — i.e., for individual particles.")
    print()
    print("No paradox: the cat is alive-or-dead at all times in substrate.")


if __name__ == "__main__":
    main()
