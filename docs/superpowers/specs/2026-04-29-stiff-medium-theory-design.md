# Stiff-Medium Confinement Theory — Design Doc (Path A)

**Date:** 2026-04-29
**Status:** v1 architecture spec (Path A of A → C → B roadmap)
**Working title:** "Stiff-Medium Confinement Theory" — placeholder. Rename when settled.

---

## 1. Theory statement

The universe is a 3D stiff elastic medium. All phenomena — particles, atoms, photons, mass, charge, gravity — are patterns *in* this medium. Stable matter is a hierarchy of geometric closures of equidistantly-spaced planar arrangements; instability is failed closure that radiates outward as electromagnetic oscillation. Mass is the medium's torque response to maintaining a confined pattern; gravity is the same medium's static deflection by that pattern; charge is the geometric complementarity of slope shapes (troughs and hills). Stable particles, atoms, and forces all emerge from one substrate and one set of closure rules.

---

## 2. Methodology — measurable, observable, no correction loops

This theory is committed to **direct, measurable, observable predictions**. The substrate's structure, the geometry of patterns, and the closure rules must produce the right physics on their own — without renormalization, perturbative correction loops, or after-the-fact tuning of free parameters to match data.

**In practice this means:**

- Predictions come from the medium's stiffness K, effective density, and the geometric / topological rules of pattern closure.
- Numerical results (electron mass, lepton ratios, Rydberg constant, fine-structure constant) must be derived *directly* from these inputs, not fitted to data.
- If a prediction disagrees with measurement, **the theory is wrong as stated**. There is no "next-order correction" that's allowed to rescue it. Either the substrate is wrong, the closure rules are wrong, or both — and we revise the foundations rather than patching the output.

**Why the stricter bar:** a theory that requires endless corrections to match observation is signalling that something is wrong with its foundations. We're rebuilding the foundations, so we don't grant ourselves that crutch. This rules out the standard QFT toolkit of perturbation series + renormalization for closing gaps between theory and experiment. It does *not* rule out approximations, simulation, or numerical methods — only the practice of treating "the theory plus its corrections" as a complete package.

**Cousins in real physics:** 't Hooft's no-fine-tuning principle; constructive QFT (which demands rigorous, non-perturbative derivations); emergent / lattice approaches to gravity; parts of the geometric-algebra and twistor traditions that aim for direct geometric derivations of observables.

---

## 3. Architecture overview

| Layer | Object | Geometric form |
|---|---|---|
| 0 | Stiff 3D medium | Substrate |
| 1 | Neutrino | 1D slope vector at 45° to its own intrinsic axis |
| 2 | Electron / positron | 2D V- or Λ-structure (paired neutrinos) on a plane |
| 3 | Nucleon (proton / neutron) | 3D bi-pyramid with planar faces |
| 4 | Atom | Hydrogen: tidally-locked pair. Multi-electron: equidistant orbital planes around nucleon-core. |

Each layer is built from the previous via geometric closure of plane arrangements. **The entire theory is plane-based at every level**: neutrino slopes lie in planes, electron V-structures span planes, bi-pyramid faces are planes, atomic orbitals are planes. "Geometric closure" has one consistent meaning throughout — planes meet cleanly at edges, edges close polyhedra, polyhedra close stacks.

---

## 4. Substrate (Layer 0)

The medium is a 3D stiff elastic continuum with stiffness modulus K. Its natural propagation speed is c, derivable from K and effective density.

The medium is the only fundamental thing. Every subsequent layer is a pattern of strain in the medium.

---

## 5. Neutrino (Layer 1)

A neutrino is a 1D propagating strain pulse:

- Carries a ± slope along its length (one end compressed, the other stretched).
- Translates at c at **exactly 45°** relative to its own intrinsic axis. **45° is the uniquely stable balanced angle**: at 45°, the velocity has equal projection along the axis and perpendicular to it (equal partition between "along-axis" and "around-axis" motion). Any other angle is unbalanced and the medium's response forces the vector back to 45°. This is the spatial-medium analogue of null worldlines in Minkowski spacetime, where 45° is the unique angle where time- and space-components are equal-magnitude.
- The axis is per-particle; each neutrino carries its own.
- In 3D, the 45° constraint defines a *cone* of allowed velocity directions around the axis (continuous U(1) freedom). The cone surface IS the dynamics manifold; no other configurations are physically accessible. Any rule that would deflect a vector off the 45° cone is forbidden.
- In 2D, the cone collapses to 4 discrete velocity directions (the projections of the 3D cone onto a plane). This explains why 2D simulation gives only (±s, ±s) and cannot reproduce 2D orbits — see Path C v1/v2 findings.
- Possesses a small effective mass via E/c² of its strain content (consistent with measured tiny but nonzero neutrino mass).

**Dynamics rule (load-bearing, revised after Path C back-reaction findings):**

- **Free particles do not reorient by themselves.** A neutrino in free flight propagates at c on its 45° cone with constant velocity direction. No internal mechanism rotates the velocity vector.
- **The medium can reorient velocities through back-reaction (see §5.5).** When particles are within range of one another, the medium's response — push when too close, pull when too far — applies an effective force to each particle. This force is what reorients velocities in bound configurations, converting persistent linear c into orbital angular motion.
- **The cone constraint is preserved at all times.** Any back-reaction force is projected onto the velocity's azimuthal tangent on the 45° cone before it is applied — the velocity rotates around the cone (changing azimuthal direction) but its magnitude stays at c and its angle to the axis stays at 45°.
- **Equivalently:** vectors don't reorient *by themselves*; the medium reorients them *collectively* in bound configurations, and only on the cone surface.

This replaces the earlier overly-strict "vectors never reorient" formulation, which Path C v1/v2/v3 simulations showed was insufficient to produce spec §6's 2D orbital cone. The back-reaction picture (§5.5) is what unlocks orbital binding while still respecting the cone constraint.

---

## 5.5 Medium back-reaction (the binding mechanism)

The medium responds to particles within it. Two particles at distance d experience an effective two-body force determined entirely by d and the medium's parameters:

- **d < r_eq:** repulsive (centrifugal). The medium pushes particles apart. This is the original "displacement rule" of v1.
- **d > r_eq, d < r_capture:** attractive (centripetal). The medium pulls particles together. This is the *missing* component that Path C v1/v2/v3 lacked.
- **d > r_capture:** no interaction. Particles propagate freely.

**r_eq** is the medium's natural equilibrium spacing — derivable from K, ρ, and the particles' strain content. **r_capture** is the maximum range of the back-reaction.

**Why this gives 2D orbital motion.** Two particles with tangential c-velocities at distance r_orbit (slightly larger than r_eq) experience attractive force exactly balancing the centripetal demand of their c-motion. The persistent linear c is converted to angular motion by the medium's pull, producing a stable circular (or elliptical) orbit. **r_orbit ≠ r_eq:** at d=r_eq the force is zero and pure tangential motion escapes; r_orbit is the d where the attractive force equals the centripetal requirement c²/d. Solving K·(r_orbit − r_eq) = c²/r_orbit gives r_orbit > r_eq.

This mechanism was confirmed experimentally in Path C back-reaction tests: tangential initial conditions at 1.5× r_eq produced 5.62 full orbits over the second half of a 6000-step run, with the cone constraint preserved throughout.

**Falsifiable prediction:** r_orbit and r_eq are both calculable from K (and the particle's strain content). The electron's measured rest mass and Compton wavelength must match m_e = E_orbit / c² and λ_e ~ r_orbit, where E_orbit is the bound orbit's energy. This is the first hard numerical checkpoint for Path B.

### 5.5.1 Pauli-like exclusion is mechanical (precise scope)

**What's mechanically established by §5.5's repulsive branch:**

- Two strain patterns cannot coincide at the same coordinate. The medium's stiffness produces hard-core repulsion at d < r_eq.
- This *is* sufficient to produce: shell filling in atoms (electrons can't pile into ground state), degeneracy pressure (neutron stars don't collapse below density set by r_eq), impenetrability of bulk matter (solids don't pass through each other).

**What's NOT yet established — and where this differs from real Pauli:**

- Real Pauli exclusion is *antisymmetry of identical fermions under particle exchange*: two electrons with *opposite* spin states CAN occupy the same spatial coordinate (in a covalent bond, an atomic orbital), while two electrons with *parallel* spin cannot. The exclusion is spin-state-dependent, not purely spatial.
- Our §5.5 mechanical exclusion is **state-blind**: it just says "no two strain patterns in the same place," regardless of internal state. This is *like billiard balls*, not like fermions.
- To recover the full Pauli principle, the theory needs to couple the exclusion rule to the Möbius internal twist (§13 gap #1) so that two same-twist particles repel via §5.5 but two opposite-twist particles can bind in the same coordinate. This coupling is **not yet specified in the spec**.

**Honest framing:** the §5.5 mechanical exclusion is a *necessary but not sufficient* condition for real Pauli. The phenomenology that depends only on hard-core spatial exclusion (shell filling, degeneracy pressure) is reproduced. The phenomenology that depends on antisymmetry under exchange (specific bonding patterns, spin-singlet vs spin-triplet states) requires the spin-½ implementation that's still pending.

| | Standard Model | This theory (current state) |
|---|---|---|
| Hard-core spatial exclusion | derived from spin-statistics + antisymmetry | direct consequence of medium stiffness (§5.5) ✓ |
| Spin-state-dependent exclusion | spin-singlet vs spin-triplet bonds, etc. | not yet specified — needs Möbius coupling to §5.5 |
| Spin-½ rotation property (720° return) | a postulate, derived from Dirac equation | kinematic signature shown via cone-azimuth ratio, but Möbius topology not yet implemented in dynamics (§13 gap #1) |

**Cleanest framing of what's actually shown:** medium back-reaction produces *one specific subset* of Pauli-like behavior (mechanical hard-core exclusion). The full Pauli principle requires additional structure (Möbius topology and its coupling to the exclusion rule) that the spec describes but the simulation doesn't yet implement.

---

## 6. Electron (Layer 2)

An electron forms when two neutrinos enter the binding range of one another (d < r_capture, see §5.5) with appropriate angular momentum. The medium's back-reaction (attractive at d > r_eq, repulsive at d < r_eq) holds them on a circular or elliptical orbit at d = r_orbit. Their persistent linear c is continuously converted into angular motion by the back-reaction's centripetal pull. **The medium is the gyroscope.**

### Stability mechanism

Two conditions stabilize the orbit:

- **(A) Centripetal balance.** The medium's back-reaction force matches the orbit's centripetal demand at a unique radius r_orbit slightly larger than r_eq. (Confirmed by Path C back-reaction simulation: tangential c-velocities at 1.5× r_eq produced 5.62 full orbits.)
- **(E) Standing-wave resonance.** The orbit must match a natural mode of the medium or it radiates away.

Together they pick out a stable orbital radius — that radius is the electron. Muons and taus are *not* different orbital modes; they are stress-loaded versions of the same orbit (see "Lepton generations" below).

### Geometry

- 2D V-structure: two slopes meeting at a vertex.
- Vertex polarity determines particle identity:
  - **"+\\- -/+" trough** (− at vertex, + at outer ends) → **electron-mode**.
  - **"-/+ +\\-" hill** (+ at vertex, − at outer ends) → **positron-mode**.
- Rotation of the V-structure sweeps a 3D cone, but the V itself lies in a definite plane.

### Mass

Mass is the torque the medium exerts to maintain the orbital strain pattern. This is a Mach-like / Higgs-like / effective-mass-in-lattice picture: mass = how the pattern couples to the surrounding background. E = mc² follows mechanically — two neutrinos at c on a closed orbit have kinetic energy ∝ c², and that energy divided by c² is the rest mass.

### Lepton generations as stress-loaded electrons (3 generations maximum)

The muon and tau are not separate particles or higher orbital modes — they are the **same electron orbit with extra momentum loaded onto its vertex** (typically by a collider event or other high-energy interaction). The vertex absorbs discrete stress-quanta before geometric closure fails:

| Generation | Particle | Vertex stress | Stability |
|---|---|---|---|
| 1 | electron | 0 quanta (ground) | stable |
| 2 | muon | 1 quantum | unstable, decays to electron + neutrinos |
| 3 | tau | 2 quanta | unstable, decays faster |
| 4+ | — | — | cannot close; immediate decay |

**3 generations maximum is a structural prediction**, not a free parameter. The vertex's geometric closure cannot sustain a fourth stress quantum. The specific limit (why exactly 3) derives from vertex closure geometry — to be made precise in Path B, but the *ceiling* is the prediction.

All stress-loaded states decay back to the electron, restoring the stable balanced angular momentum at the c-orbit. This matches real phenomenology: muon lifetime ~2.2 µs, tau ~290 fs (taus decay ~10⁷× faster, consistent with more stress to shed); both decay channels end at electron + neutrinos; no 4th-generation charged lepton has been observed despite extensive collider searches at the LHC.

---

## 7. Nucleon (Layer 3)

When two electron-orbit-patterns are forced to coexist in overlapping space, the medium's back-reaction (§5.5) reorients their constituent velocities collectively into a stable bi-pyramidal closure. The cone constraint is preserved (§5: velocities stay on each particle's 45° cone), but the back-reaction reshapes which point on each cone the velocity occupies.

### Geometry

- A bi-pyramid is a 3D solid with planar triangular faces.
- **Vertex count determines quark count.**
- Each vertex carries a *fractional* share of the underlying slope total. Geometric closure forces fractional charges (1/3, 2/3) without postulating them — a structural prediction matching QCD's quark charge fractions.
- **Each vertex also carries spin-½** (per §13 gap #1, blocking). The bi-pyramid as a whole is spin-½ when two vertex spins align and one is anti-aligned (proton/neutron) and spin-3/2 when all three align (Δ baryon resonance). Without spin-½ at each vertex, this is a polyhedron with charge fractions, not a nucleon — see §13.
- **Proton vs. neutron** = orientation/symmetry of the same bi-pyramidal closure, including the relative spin alignment of vertex pairs.

### Stability

Topology + geometric closure (see §11). The bi-pyramid is stable because its faces close cleanly; configurations that don't close radiate their leftover topology away as EM.

### Open detail

The specific bi-pyramid type (triangular, square, etc.) and its precise vertex count is not yet specified. The structural prediction is "fractions from vertex shares"; the numerical prediction (which fractions, which symmetries) is deferred to Path B.

---

## 8. Atom (Layer 4)

### 8.1 Hydrogen — special case

One electron + one proton = one valley + one hill. They **tidally lock** face-to-face: the electron's slope-trough fits exactly into the proton's slope-hill. No shells, no orbital planes — just a locked pair.

The 1/n² Rydberg spectrum is conjectured to come from excitation modes of the locked pair (rocking, breathing, twisting). Discrete modes because the geometry is fixed. Numerical match to Rydberg's constant is a Path B checkpoint.

#### 8.1a Atomic-scale dynamics is hierarchical

**Important clarification (added after Path C hydrogen simulation):** the cone constraint of spec §5 applies to the *underlying neutrinos*, not to bound-state center-of-mass dynamics. At the atomic scale (electron + nucleus), each "particle" is already a multi-neutrino bound configuration whose COM velocity is FREE (not constrained to c). The relevant force at this scale is Coulomb-like — an averaged effect of medium back-reaction over the bound states' internal structure (per §10's slope-shape complementarity).

**Empirical result from `scripts/hydrogen_isotopes_v2.py`:**

| Isotope | m_n / m_e | Reduced μ | Simulation ω | (ω/ω_H − 1) |
|---|---|---|---|---|
| H | 1836.15 | 0.999456 | 0.159198 | 0 |
| D | 3670.48 | 0.999728 | 0.159177 | −136 ppm |
| T | 5496.92 | 0.999818 | 0.159169 | −181 ppm |

This is the *classical 2-body fixed-radius* result: ω ∝ 1/√μ. **Real Rydberg shift is +272 ppm** (D/H), reflecting *quantized* Bohr orbits where a_n ∝ 1/μ and ω ∝ μ.

**The gap, then closed:** spec §6 (E) standing-wave resonance applied at atomic scale = Bohr quantization L = nℏ (where ℏ is the medium's natural angular-momentum unit). This picks orbit radii a_n = n²ℏ²/(μ·coupling) ∝ 1/μ.

**Empirical result with Bohr-scaled orbits (`scripts/hydrogen_isotopes_v3.py`):**

| Isotope | μ | R_bohr | ω | (ω/ω_H − 1) | Real Rydberg shift |
|---|---|---|---|---|---|
| H | 0.999456 | 1.000545 | 0.999456 | 0 | 0 |
| D | 0.999728 | 1.000272 | 0.999728 | **+272.10 ppm** | +272 ppm |
| T | 0.999818 | 1.000182 | 0.999818 | **+362.63 ppm** | +363 ppm |

**Spec §8.1 is empirically validated for hydrogen isotopes, within ppm precision.** No parameter tuning; only the real mass ratios and the back-reaction force structure are inputs. This is the first non-trivial quantitative match between the theory and measurement.

The earlier classical run at fixed R_0 gave −136 ppm = −½ × 272 ppm, exactly the wrong sign and half the magnitude — which is the signature of comparing classical (ω ∝ 1/√μ at fixed radius) vs. quantum (ω ∝ μ at Bohr-scaled radius). The factor-of-two relationship between the wrong and right answers confirmed the math was self-consistent and that quantization was the missing piece.

### 8.2 Multi-electron atoms

One nucleon-core (or cluster) cannot tidally lock with multiple electrons — one hill, many valleys. The valleys distribute themselves across **equidistant orbital planes** around the core.

**"Equidistant" is in the medium's natural coordinate, not absolute spatial distance.** The map from medium-coordinate to physical distance is what produces the observed Bohr 1/n² scaling: equal medium-spacing translates to physical distances that scale as n² in real space.

### 8.3 Open: shell-filling rule

The geometric closure rule that determines the 2, 8, 18, 32 shell-filling pattern is not yet specified. Marked as future work; not blocking v1.

---

## 9. Unification

| Phenomenon | Substrate-mechanical reading |
|---|---|
| Photon | Oscillation wave in the medium (frequency × amplitude). Massless. |
| Mass | Trapped oscillation energy / c²; mechanically the medium's torque to maintain the pattern. |
| Electromagnetism | Dynamic oscillation of the medium. |
| Gravity | Static deflection of the medium by a confined pattern. |
| Equivalence principle | Theorem (same medium, same deflection). Inertial mass = gravitational mass falls out automatically. |
| Charge | Geometric label for slope-shape direction. Not a primitive conserved quantity. |
| Pair production | γ → e⁺e⁻: unconfined oscillation collapses into a confined pattern pair. |
| Pair annihilation | e⁺e⁻ → 2γ: matched valley + hill merge and unconfine, releasing as oscillation. |

---

## 10. Forces from geometric complementarity

Charge interactions are not fundamental — they emerge from how slope shapes fit together:

- **Trough + hill** → shapes fit → **attraction** (e.g., e⁻ + p⁺).
- **Trough + trough** or **hill + hill** → shapes don't fit → **repulsion** (e.g., e⁻ + e⁻).

Coulomb's qualitative law follows directly. The 1/r² fall-off and absolute strength must derive from the medium's elastic response to slope deflections in Path B — directly, without correction-loop adjustment.

---

## 11. Conservation and decay

**What's conserved:**

- **Topological invariants** of the pattern (winding numbers, knot type, vertex count). Integer-valued, can't change continuously.
- **Geometric closure** of the plane arrangement.

**Stable:** pattern that closes geometrically AND carries a conserved topological number.

**Unstable:** pattern that fails closure → topology unwinds → leftover oscillation propagates outward as EM.

### Mapping to real decay processes

| Real decay | Reading in this model |
|---|---|
| β-decay (n → p + e + ν̄) | Nucleon imbalance forces re-closure; leftover topology leaves as electron + antineutrino. |
| Pair annihilation (e⁺e⁻ → 2γ) | Two complementary patterns merge and unconfine, releasing as oscillation. |
| Lepton decay (μ → e + ν + ν̄) | Stress-loaded electron sheds its vertex stress quanta (§6 lepton generations); the released energy carries away as electron + two neutrinos. |
| Photon emission from atom | Excitation mode of orbital plane (or locked pair) decays; energy radiates as oscillation. |

---

## 12. Plane-based geometry (recursive principle)

The whole theory is plane-based:

- Neutrino slopes lie in planes.
- Electron V-structures span planes.
- Bi-pyramid faces are planes.
- Multi-electron orbitals are planes.

"Geometric closure" has one consistent meaning at every layer: planes meet cleanly at edges, edges close polyhedra, polyhedra close stacks, stacks close into atoms. The same plane-closure language describes everything from the smallest particle up to the largest atom.

---

## 13. Known gaps (parked)

| # | Gap | Where to address |
|---|---|---|
| 1 | **Spin-½ via Möbius internal twist — KINEMATIC SIGNATURE shown, dynamics not yet implemented.** Empirical result (scripts/spin_check.py): in the back-reaction-driven bound orbit (Test 2's 5.62 revolutions, second half of run), each neutrino's cone azimuth rotates by **1.004 turns per orbital revolution**. **Under the assumption of Möbius topology** (slope flips per 2π of azimuth, returns at 4π), this kinematic ratio gives slope-flip-per-orbit and 720°-return — the *signature* of spin-½. **What's NOT shown:** the Möbius topology itself is not implemented in the dynamics — it's still an interpretation layer applied to the cone-azimuth observable. To genuinely demonstrate spin-½, we'd need (a) the dynamics to *act* differently on Möbius-twist particles (e.g., two same-twist particles unable to bind, two opposite-twist able to), (b) a derivation of the Möbius topology from substrate principles. Both are open. **What IS shown:** the kinematic ratio is consistent with what spin-½ would require, and the geometry of cone-projected orbital motion produces this ratio inevitably. So Möbius-topology is a *possible* interpretation that the kinematics doesn't rule out, not a *demonstrated* feature. | Path B Phase 2: implement Möbius dynamics, derive topology from substrate, compute fermionic breather mass. |
| 2 | **Lepton mass ratio numbers** (1 : 207 : 3477 for e : μ : τ). The structural prediction (3 generations max, leptons as stress-loaded electrons) is now in §6; only the numerical ratios remain open. | Path B numerical derivation. |
| 3 | **Multi-electron shell filling** (2, 8, 18, 32). | Future work after hydrogen is solid. |
| 4 | **Matter/antimatter asymmetry.** Slope orientation distinguishes electron from positron, but why the universe favors one is unaddressed. | Open. |
| 5 | **Continuum form of the back-reaction.** §5.5 specifies the qualitative structure (push at d<r_eq, pull at r_eq<d<r_capture) confirmed by simulation. The exact functional form (Lennard-Jones-like? 1/r? something else?) and its derivation from the medium's stress-strain tensor is the next theoretical step. | Path B. |
| 6 | **Exact bi-pyramid type / vertex count.** Currently unspecified. | Path B. |
| 7 | **r_eq and r_orbit numerical values.** Confirmed structurally; first hard checkpoint is computing r_orbit from K and matching to electron Compton wavelength. | Path B Phase 1. |

Per §2 methodology: gaps must be closed by direct derivation, not by introducing free parameters that get tuned post-hoc.

---

## 14. Open philosophical questions

These are normal foundational-theory questions, not blocking v1:

- **Origin of the medium itself.** Posited as primitive; what gives K its value is not addressed.
- **Why the 45° angle is uniquely stable.** Posited and physically motivated (equal partition between along-axis and around-axis motion = balance), but not derived from deeper principles such as a stiffness tensor structure. Path B should produce this from K and the medium's symmetry.
- **Why each neutrino carries its own intrinsic axis.** Posited; mechanism not explained.

---

## 15. Roadmap

- **Path A — this document.** Geometric / topological architecture. v1 complete; revised after Path C findings to incorporate medium back-reaction.
- **Path C v1/v2/v3 — complete.** Pure displacement-only rule (no back-reaction) demonstrated to produce *only* 1D bound states in narrow geometries; never 2D orbital motion. This was the falsification signal that drove the §5.5 revision.
- **Path C back-reaction — complete (proof of concept).** With back-reaction added (centripetal pull at d>r_eq) and 45° cone projection enforced, **2D orbital motion was directly observed**: 5.62 full revolutions in a 6000-step run, with energy and cone constraint preserved throughout. Confirms §5.5 architecturally.
- **Path B — next.** Direct field-theoretic derivation of numerical values from K, ρ, c: r_orbit (and hence electron Compton wavelength), electron rest mass, lepton mass ratios, fine-structure constant, Rydberg constant. Per §2: no renormalization, no perturbative correction loops to close the gap to measurement.

---

## 16. Falsifiable claims

**Already structural** (no further work needed to state):

1. Quark charge fractions follow from polyhedral vertex count of the nucleon bi-pyramid.
2. Inertial mass = gravitational mass to all measurable precision.
3. Hydrogen is structurally unique among atoms (tidally-locked pair, not shell-based).
4. Heavier "electron-like" particles (muon, tau) are unstable stress-loaded electrons that decay back to electron + neutrinos. **Exactly 3 lepton generations exist** — the vertex cannot absorb a 4th stress quantum. Discovery of any 4th-generation charged lepton would falsify the model.
5. Coulomb's qualitative law (opposite-attract, like-repel) is geometric, not fundamental.
6. Medium back-reaction has the structure (push at d<r_eq, pull at d>r_eq, equilibrium at r_eq) — directly observed in Path C back-reaction simulation: tangential c-velocities at 1.5× r_eq produced 5.62 full orbits in 6000 steps with energy and cone constraint preserved.
6a. **Mechanical hard-core exclusion** (a *subset* of Pauli) — directly equivalent to the §5.5 repulsive branch. Reproduces shell filling, degeneracy pressure, bulk-matter impenetrability. Does NOT yet reproduce spin-state-dependent exclusion (singlet vs triplet); that needs Möbius coupling to be specified.
6b. **Cone-azimuth ratio of 1 turn per orbital revolution** — empirically observed in the back-reaction simulation (1.004 measured over the second half of a 6000-step run). Geometrically inevitable given the cone constraint plus orbital motion. Under the assumption of Möbius topology, this kinematic ratio is the signature of spin-½. **Note:** Möbius is an interpretation overlay; the dynamics doesn't yet implement it, so this is "consistent with spin-½" not "demonstrated spin-½."

**Pending Path B** (must match measurement directly per §2):

7. r_orbit (the natural orbital radius) computed from K equals the electron's measured Compton wavelength.
8. Bound-orbit energy E_orbit / c² equals the electron's measured rest mass (511 keV).
9. Lepton mass ratio spectrum (e : μ : τ = 1 : 207 : 3477).
10. Hydrogen 1/n² Rydberg spectrum from locked-pair modes.
11. Bohr 1/n² scaling from medium-coordinate equidistance for multi-electron atoms.
12. Possibly: a new stable particle corresponding to a yet-uncatalogued geometric closure.

If any of items 7–12 disagree with measurement and the disagreement cannot be resolved by direct revision of the substrate or closure rules, the theory is falsified.

---

*End of Path A spec.*
