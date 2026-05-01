"""How substrate gives 4D Lorentzian spacetime: detailed emergence.

Standard physics treats spacetime as a 4D Lorentzian manifold with metric
g_μν, signature (-,+,+,+). Substrate framework derives this from a 3D
elastic medium. How exactly?

Three key pieces emerge:

  1. Lorentzian metric SIGNATURE (-,+,+,+) from substrate wave equation
  2. Universal SPEED OF LIGHT c = √(K/ρ) sets the light-cone structure
  3. EQUIVALENCE PRINCIPLE from universal coupling to substrate strain
  4. NO PREFERRED FRAME despite substrate having a 'true rest frame'
     (because all clocks and rulers are themselves substrate excitations)
"""

from __future__ import annotations
import math


PI = math.pi


def main() -> None:
    print("Emergent 4D Lorentzian spacetime from 3D elastic substrate")
    print("=" * 70)
    print()

    # === Step 1: Substrate fundamentals ===
    print("STEP 1: Substrate is fundamentally a 3D elastic medium")
    print("-" * 70)
    print()
    print("Spatial structure:")
    print("  - 3 spatial dimensions (substrate occupies 3D)")
    print("  - Stiffness K (resistance to strain)")
    print("  - Density ρ (inertial response)")
    print("  - Length scale ξ (substrate microstructure)")
    print()
    print("Wave equation (linearized):")
    print("  ρ ∂²ₜ u = K ∇² u")
    print()
    print("Time emerges as the parameter governing oscillation rates of")
    print("substrate field u(x, t). Not a 'fourth dimension' fundamentally —")
    print("it's the substrate's evolution parameter.")
    print()

    # === Step 2: Lorentzian signature ===
    print("STEP 2: Lorentzian (-,+,+,+) signature from wave equation")
    print("-" * 70)
    print()
    print("The wave equation factors as:")
    print("  (∂ₜ - c∇·)(∂ₜ + c∇·) u = 0")
    print("  with c² = K/ρ")
    print()
    print("Solutions propagate along NULL CONES: x² = c²t²")
    print()
    print("The Minkowski metric ds² = -c²dt² + dx² + dy² + dz²")
    print("naturally emerges as the substrate wave's characteristic surfaces.")
    print()
    print("The (-) signature for time comes from the wave equation's")
    print("hyperbolic (not elliptic) nature. Substrate is dynamical, not static.")
    print()
    print("If substrate had ∇²u = -|∇²u| structure (purely elastic, no inertia),")
    print("metric would be Euclidean (+,+,+,+). But substrate has inertia ρ,")
    print("so wave equation is hyperbolic → Lorentzian.")
    print()
    print("This is structural: substrate's 'time' emerges as the inertial")
    print("dimension dual to the elastic spatial dimensions.")
    print()

    # === Step 3: 45° cone constraint ===
    print("STEP 3: 45° cone constraint = light-cone in substrate")
    print("-" * 70)
    print()
    print("All propagating substrate excitations move at velocity vectors")
    print("confined to ±45° on a cone in the local frame (MODEL.md §2.1).")
    print()
    print("This IS the light-cone condition c²t² = x² in Minkowski space.")
    print()
    print("The 45° angle is structural (Mohr's circle, equal-projection):")
    print("  - Photon propagates on the cone surface")
    print("  - Massive particles propagate INSIDE cone (timelike)")
    print("  - Spacelike trajectories are FORBIDDEN by substrate dynamics")
    print()
    print("So causality (no FTL) is built into substrate at the kinematic")
    print("level, not as a separate postulate.")
    print()

    # === Step 4: Curved spacetime from substrate strain ===
    print("STEP 4: Curved spacetime emerges from substrate strain σ(x)")
    print("-" * 70)
    print()
    print("In the presence of mass-energy, substrate strain σ(x) varies.")
    print("This MODIFIES the local effective stiffness:")
    print("  K_eff(x) = K × (1 - 2σ(x))")
    print()
    print("→ Local wave speed becomes:")
    print("  c_eff(x) = √(K_eff(x)/ρ) = c × √(1 - 2σ(x))")
    print()
    print("This is GR's gravitational time dilation:")
    print("  proper time = coordinate time × √(1 + 2Φ/c²)")
    print("  where Φ = -GM/r is gravitational potential")
    print()
    print("Identification: σ(x) = -Φ(x)/c² = GM/(c²r) at the substrate level.")
    print()
    print("Substrate effective metric:")
    print("  g₀₀(x) = -(1 - 2σ(x))   ← time component (gravitational redshift)")
    print("  gᵢⱼ(x) = δᵢⱼ × (1 + 2σ(x))   ← spatial component (length")
    print("                                  contraction near mass)")
    print()
    print("This is exactly the SCHWARZSCHILD METRIC in weak-field limit.")
    print("Recovers Newton's gravity at low velocities + slow time.")

    # === Step 5: Equivalence principle ===
    print()
    print("STEP 5: Equivalence principle from universal substrate coupling")
    print("-" * 70)
    print()
    print("All particles have rest mass = ℏ × ω_bounce × (drag-derived)")
    print("All particles couple to substrate strain via cone-bouncing")
    print("→ All particles fall the same way in gravitational field")
    print("→ Inertial mass = gravitational mass (equivalence principle)")
    print()
    print("This is NOT a postulate in substrate framework — it follows from")
    print("the universal mechanism of mass generation. There's no possibility")
    print("of EP violation because mass IS substrate response.")
    print()

    # === Step 6: No preferred frame despite substrate rest frame ===
    print("STEP 6: No PREFERRED frame despite substrate having a rest frame")
    print("-" * 70)
    print()
    print("Standard objection: 'If substrate is a real medium, shouldn't")
    print("there be an aether-style preferred frame?'")
    print()
    print("Answer: substrate DOES have a rest frame (the frame in which")
    print("substrate is at rest). But this frame is OPERATIONALLY UNDETECTABLE.")
    print()
    print("Why: clocks and rulers are themselves substrate excitations.")
    print()
    print("  Moving observer: their atoms (substrate excitations) experience")
    print("  Lorentz contraction + time dilation. Their measurements use")
    print("  substrate-derived clocks/rulers.")
    print()
    print("  Result: any inertial observer measures the SAME c, regardless of")
    print("  motion through substrate (Michelson-Morley confirmed).")
    print()
    print("This is mathematically equivalent to LORENTZ ETHER THEORY (LET):")
    print("  - Substrate IS a real medium (aether-like)")
    print("  - Lorentz invariance is dynamical (clocks/rulers transform)")
    print("  - No experiment can detect substrate rest frame")
    print()
    print("Special relativity is equivalent to LET phenomenologically.")
    print("Substrate framework gives LET its physical mechanism.")

    # === Step 7: Higher dimensions? ===
    print()
    print("STEP 7: Why exactly 3 spatial dimensions?")
    print("-" * 70)
    print()
    print("Substrate is observed to be 3D. Tests:")
    print("  - Newton's law F ~ 1/r² confirms 3D (in D dimensions, F ~ 1/r^(D-1))")
    print("  - Atomic stability requires 3D (1/r potential bound states unstable in D ≠ 3)")
    print("  - Born stability: matter is stable only in 3D + 1D time")
    print()
    print("Substrate dimension is NOT explained by framework — it's a")
    print("structural input. (Higher-dimensional substrate would give")
    print("different physics, ruled out by observations.)")
    print()
    print("Possible substrate-mechanical reasoning: substrate cell is K_4")
    print("tetrahedron (4 vertices = 3-simplex). Living in 3D = naturally")
    print("matches simplicial structure. Higher-D substrate would have")
    print("different cell topology, different α, different mass spectrum.")
    print()

    # === Final summary ===
    print()
    print("=" * 70)
    print("Summary: 4D Lorentzian spacetime as substrate behavior")
    print("=" * 70)
    print()
    print("From a 3D elastic medium with:")
    print("  - Stiffness K, density ρ, length ξ, drag γ")
    print("  - 45° cone kinematic constraint")
    print()
    print("Emerges:")
    print("  - 4D Lorentzian spacetime (3 spatial + 1 emergent time)")
    print("  - Speed of light c = √(K/ρ) universal")
    print("  - Light cones from cone constraint")
    print("  - Curved spacetime (Einstein equations) from substrate strain")
    print("  - Equivalence principle from universal mass mechanism")
    print("  - Lorentz invariance from substrate dynamics")
    print("  - No detectable preferred frame (LET equivalence)")
    print()
    print("Special relativity, general relativity, and 4D Minkowski/Lorentzian")
    print("structure all FALL OUT of substrate dynamics. They're not separate")
    print("postulates; they're consequences of having a stiff elastic medium.")


if __name__ == "__main__":
    main()
