# Path B — Phase 0.2 + Phase 1: Model Choice and Linearization

**Date:** 2026-04-29
**Status:** Phase 0.2 complete, Phase 1.1 complete, Phase 1.2 in progress.
**Scope:** This document covers the model choice, linearization (deriving c² = K/ρ), and the start of the soliton ansatz for the neutrino. The full soliton solution and bound-state energy calculation are deferred to subsequent sessions.

---

## Phase 0.2: Choice of continuum model

**Candidates considered:**

1. **Linear elasticity + nonlinear stiffening** (chosen). Field u(x, t) is the medium's local 3D displacement vector; Lagrangian is kinetic minus elastic potential. Linear part gives c² = K/ρ directly. Nonlinear correction adds soliton support.
2. **Sine-Gordon-like phase field.** Closed-form solitons exist, but native 1+1D; requires Skyrme-style construction for 3D.
3. **Skyrme model.** Native 3D and good for nucleons, but the connection to the stiffness K and the medium picture is less direct.

**Decision: Option 1.** Maps the spec's language ("stiff isotropic 3D medium with stiffness K and density ρ") onto field theory most directly, and gives c² = K/ρ in one line of algebra.

---

## Phase 1.1: Linearization — derive c² = K/ρ

**Field:** u(x, t) ∈ ℝ³, the medium's local displacement vector.

**Lagrangian density** (linear elasticity for an isotropic stiff continuum):

```
ℒ = ½ ρ |∂u/∂t|² − ½ K (∇·u)² − ½ G |∇×u|²
```

where:
- ρ is the medium's effective density.
- K is the bulk stiffness modulus (resists compression/dilatation; couples to the longitudinal divergence of u).
- G is the shear modulus (resists shear; couples to the curl of u).

**Equation of motion** (Euler-Lagrange):

```
ρ ∂²u/∂t² = K ∇(∇·u) + G ∇²u_⊥
```

where u_⊥ is the transverse (divergence-free) part.

**Plane wave solutions:**

For longitudinal waves (∇×u = 0, so u parallel to k):
```
ω² = (K/ρ) |k|²    →    c_L = √(K/ρ).
```

For transverse waves (∇·u = 0, so u perpendicular to k):
```
ω² = (G/ρ) |k|²    →    c_T = √(G/ρ).
```

**Physical interpretation:**
- A "stiff medium" with K ≫ G is dominated by longitudinal waves. The natural wave speed is c = √(K/ρ).
- The spec's "wave speed c" refers to the longitudinal speed in the spec's stiff regime. Transverse modes propagate slower; if the spec wants c to be the only speed, then either G = K (incompatible with "stiff" meaning of bulk dominance) or transverse modes are forbidden by the dynamics structure.

**Result for spec §4 (Substrate):**
```
c² = K/ρ                                     [Phase 1.1, ✓]
```

This is the first concrete derivation linking the substrate parameters K and ρ to the observable c. **Per spec §2, no parameters were tuned.**

---

## Phase 1.2: Soliton ansatz for the neutrino

A neutrino is a 1D localized strain pulse propagating at c on its 45° cone. To support a *localized* (non-radiating) solution, we need a nonlinear correction to the elastic Lagrangian.

**Simplest nonlinear extension** — adds a cubic stiffening term:

```
ℒ_nl = − ¼ α (∇·u)⁴
```

where α > 0 has dimensions of [energy / volume / strain⁴]. This is the φ⁴-style correction; physically, it represents the medium's strain potential getting steeper at large amplitude (super-linear stiffness).

**Equation of motion (longitudinal mode, 1D for now):**

Let u be the longitudinal displacement along the propagation direction, dependent only on x and t. Then ∇·u = ∂u/∂x, and:

```
ρ ∂²u/∂t² = K ∂²u/∂x² + α ∂/∂x[(∂u/∂x)³]
```

**Soliton ansatz** — try u(x, t) = U(ξ) where ξ = x − vt (traveling wave at speed v):

```
ρ v² U'' = K U'' + α ((U')³)'
```

Let φ = U' (the strain). Then U'' = φ', and:

```
(ρ v² − K) φ' = α (φ³)' = 3α φ² φ'.
```

If φ' ≠ 0:
```
ρ v² − K = 3α φ²
φ² = (ρ v² − K) / (3α)
```

For φ to be real, we need ρv² > K — i.e., the soliton must move *faster* than the linear wave speed c = √(K/ρ). This is **inconsistent with the spec** (neutrinos move at exactly c). So a pure cubic-stiffening Lagrangian doesn't admit subluminal solitons.

**Two ways to fix this** (open at end of session):

A. **Include a confining potential** — add a term like −½ m² u² that gives the field a rest mass scale. This is the "massive scalar field" approach. Solitons exist as kinks of this potential and propagate at c only in the massless limit. For the spec to give neutrinos exactly at c, m → 0 for the neutrino field (consistent with the spec's small but nonzero neutrino mass — m → small).

B. **Use a sine-Gordon-style potential** — V(u) = K λ² (1 − cos(u/λ)) for some length scale λ. The kink soliton φ_kink(ξ) = 4 arctan(exp(γξ/λ)) propagates at c=1 (in natural units) and has a definite energy E_kink = 8K λ. This is the cleanest analytical model and is what most heterodox field theories of particles use.

**Decision (deferred to next session):** the spec language ("stiff medium" with strain) leans toward option A, but the analytic tractability of option B is much greater. The right move is probably to use option B as a model and verify it reproduces the right phenomenology, then map it onto option A in a second pass.

---

## Phase 1.3 (deferred): the neutrino's energy

Given a soliton solution u_ν(x − ct), the neutrino's energy is:

```
E_ν = ∫ [ ½ρ (∂u/∂t)² + ½K (∇·u)² + ¼α (∇·u)⁴ ] d³x
```

For sine-Gordon-style kinks, this is `E_ν = 8 K λ` (in 1D; the 3D extension multiplies by transverse profile area).

**This is the next task** for a future session: pick option A or B, write down the explicit kink, and compute E_ν symbolically.

---

## Phase 2 (deferred): two-soliton bound state and r_orbit

Once E_ν is known, the two-soliton effective interaction is:

```
V_int(d) = E_pair(d) − 2 E_ν
```

where E_pair(d) is the energy of the configuration with two solitons at separation d. The medium's response to having two strain pulses at distance d gives V_int(d). For sine-Gordon kink-antikink, V_int(d) is known analytically (the breather solution).

The orbit equation is:
```
K_eff (r_orbit − r_eq) = m_ν c² / r_orbit
```

where K_eff and r_eq are derived from V_int's expansion around its minimum, and m_ν = E_ν/c².

**Phase 2.2 numerical checkpoint:** compute m_e^model = E_orbit(r_orbit) / c² and compare to 511 keV.

This is the moment of truth for the theory and is the work for the next session(s).

---

## What this session accomplished

1. **Phase 0.2 (model choice):** linear elasticity + nonlinear correction, picked.
2. **Phase 1.1:** derived c² = K/ρ from the linear elasticity Lagrangian. **First concrete substrate-to-observable result.**
3. **Phase 1.2 (started):** wrote down the cubic-stiffening Lagrangian and the soliton ansatz. Found that pure cubic stiffening doesn't support subluminal solitons; need to add either a mass term (option A) or use sine-Gordon-style potential (option B).

## What's left

4. **Phase 1.2 (finish):** pick option A or B, derive the explicit kink solution u_ν.
5. **Phase 1.3:** compute E_ν symbolically.
6. **Phase 2.1:** compute V_int(d) for two solitons.
7. **Phase 2.2:** find r_orbit and compute m_e^model. Compare to 511 keV. **First hard numerical checkpoint.**

This is at least 2–3 more focused sessions, ideally with computer algebra (sympy or Mathematica) for the soliton energy integrals. Phase 2.2 is the gate — if m_e^model agrees with 511 keV, the theory is in business; if not, per spec §2, we revise the substrate or back-reaction structure (no correction loops allowed).

---

## Per spec §2 — methodology check

- **No free parameters tuned.** K, ρ, α (or λ), and the soliton type are the only choices, and they were made on physical grounds (matching the spec's "stiff medium").
- **No renormalization.** All energies and lengths derive directly from the Lagrangian.
- **Falsifiable.** Phase 2.2 will produce a specific number for m_e; if it doesn't match measurement, the model is wrong as stated, and we revise the foundations rather than adding correction terms.
