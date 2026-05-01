"""Chemistry in the substrate framework.

How does substrate explain atoms, bonds, molecular geometry, reaction
kinetics, catalysis, thermochemistry, acid-base equilibria, and
electrochemistry — i.e. the bulk of practical chemistry?

Core principle: atoms and molecules ARE substrate strain patterns.
Electron orbitals = standing-wave substrate modes around nuclear strain
centers. Chemical bonds = strain bridges between atomic centers. Drag γ
in the Lagrangian → reaction irreversibility (2nd law of chemistry).

Substrate reproduces standard chemistry numbers via QM-equivalence; the
value-add is unified ontology — chemical bonds, nuclear strong force,
and electrical conduction are the SAME class of substrate strain bridge
at different scales.
"""

from __future__ import annotations
import math


PI = math.pi
K_B = 1.381e-23
N_A = 6.022e23
R_GAS = 8.314
EV_J = 1.602e-19
HBAR_J_S = 1.054571817e-34
M_E_KG = 9.109e-31


def main() -> None:
    print("Chemistry in the substrate framework")
    print("=" * 70)

    # ============== 1. ATOMIC STRUCTURE ==============
    print()
    print("=" * 70)
    print("1. ATOMIC STRUCTURE (orbitals as substrate standing waves)")
    print("=" * 70)
    print()
    print("Standard QM: electrons in atom occupy hydrogenic orbitals")
    print("  Energy levels E_n = -13.6 eV / n²  (Rydberg formula)")
    print("  Orbitals labeled by (n, l, m_l, m_s); shells fill by aufbau")
    print()
    print("Substrate explanation:")
    print("  - Nucleus = compact substrate strain center (positive winding)")
    print("  - Electron = bound substrate excitation orbiting nucleus")
    print("  - Quantization = substrate standing-wave boundary conditions")
    print("  - n = radial node count, l = angular node count")
    print("  - Pauli exclusion = topological non-overlap of strain modes")
    print()
    print("Hydrogen energy levels (substrate predicts SAME as Bohr/Schrödinger):")
    print(f"  {'n':>3s}    {'E_n [eV]':>10s}    {'mode interpretation':>30s}")
    for n in range(1, 6):
        E_n = -13.605693 / n**2
        if n == 1:
            desc = "ground (1s) — node-free"
        elif n == 2:
            desc = "2s/2p — 1 radial/ang node"
        elif n == 3:
            desc = "3s/3p/3d — 2 nodes total"
        else:
            desc = f"{n-1} substrate-mode nodes"
        print(f"  {n:>3d}    {E_n:>8.3f}      {desc:>30s}")
    print()

    print("PERIODIC TABLE (substrate-shell filling):")
    print("  Shell capacities: 2, 8, 8, 18, 18, 32, 32  (= 2·n² with l-block ordering)")
    print("  Substrate: each shell = next-higher standing-wave mode set")
    print()
    print(f"  {'period':>7s}    {'capacity':>9s}    {'orbitals':>20s}")
    periods = [
        (1, 2, '1s'),
        (2, 8, '2s 2p'),
        (3, 8, '3s 3p'),
        (4, 18, '4s 3d 4p'),
        (5, 18, '5s 4d 5p'),
        (6, 32, '6s 4f 5d 6p'),
        (7, 32, '7s 5f 6d 7p'),
    ]
    for p, cap, orb in periods:
        print(f"  {p:>7d}    {cap:>9d}    {orb:>20s}")
    print()

    # ============== 2. CHEMICAL BONDING ==============
    print()
    print("=" * 70)
    print("2. CHEMICAL BONDING (strain bridges between atoms)")
    print("=" * 70)
    print()
    print("Standard: covalent (shared e-pair), ionic (e-transfer), metallic")
    print("  (delocalized e-sea), hydrogen bond (dipole-dipole proton bridge).")
    print()
    print("Substrate:")
    print("  - Covalent = TWO atomic strain centers share one electron-mode")
    print("    bridge; the shared standing wave lowers total substrate energy")
    print("  - Ionic = one atom transfers electron-mode to another; resulting")
    print("    Coulomb attraction is long-range substrate strain coupling")
    print("  - Metallic = lattice-wide delocalized substrate-mode (Bloch wave)")
    print("    binds positive cores via shared electronic strain")
    print("  - H-bond = weak strain bridge through proton between two")
    print("    electronegative atoms; intermediate between vdW and covalent")
    print()
    print("All four are substrate strain bridges, differing only in strength,")
    print("range, and topology.")
    print()

    print("Bond energies and lengths (representative):")
    print(f"  {'bond':>10s}    {'E [kJ/mol]':>12s}    {'length [pm]':>12s}    {'type':>10s}")
    bonds = [
        ('H-H',     436, 74,  'covalent'),
        ('C-H',     413, 109, 'covalent'),
        ('C-C',     347, 154, 'covalent'),
        ('C=C',     614, 134, 'covalent (π)'),
        ('C#C',     839, 120, 'covalent (2π)'),
        ('O-H',     463, 96,  'covalent'),
        ('N-H',     391, 101, 'covalent'),
        ('O=O',     498, 121, 'covalent (π)'),
        ('N#N',     945, 110, 'covalent (2π)'),
        ('Na-Cl',   411, 236, 'ionic'),
        ('O...H-O', 21,  280, 'H-bond'),
    ]
    for name, e, l, t in bonds:
        print(f"  {name:>10s}    {e:>10d}      {l:>10d}      {t:>12s}")
    print()
    print("Substrate prediction: bond energy scales with strain-bridge")
    print("amplitude × overlap × (1 - drag dissipation per cycle).")
    print()

    # ============== 3. MOLECULAR GEOMETRY ==============
    print()
    print("=" * 70)
    print("3. MOLECULAR GEOMETRY (VSEPR as strain minimization)")
    print("=" * 70)
    print()
    print("Standard VSEPR: electron pairs around central atom arrange to")
    print("  minimize mutual repulsion → predict bond angles.")
    print()
    print("Substrate:")
    print("  - Each electron pair = local substrate strain lobe")
    print("  - Lobes minimize total ½K|∇u|² by maximizing angular separation")
    print("  - Lone pairs occupy more solid angle (no second nucleus pinning)")
    print("    → compress bonded angles slightly below ideal")
    print()
    print(f"  {'geometry':>20s}    {'pairs':>5s}    {'angle':>8s}    {'example':>10s}")
    geom = [
        ('Linear',             2, '180°',    'CO₂'),
        ('Trigonal planar',    3, '120°',    'BF₃'),
        ('Tetrahedral',        4, '109.5°',  'CH₄'),
        ('Trig. bipyramidal',  5, '90/120°', 'PF₅'),
        ('Octahedral',         6, '90°',     'SF₆'),
        ('Bent (water)',       4, '104.5°',  'H₂O'),
        ('Pyramidal (NH₃)',    4, '107°',    'NH₃'),
    ]
    for g, p, a, ex in geom:
        print(f"  {g:>20s}    {p:>5d}    {a:>8s}    {ex:>10s}")
    print()
    print("Tetrahedral 109.5° = arccos(-1/3) — substrate strain-energy minimum")
    print("for 4 equal lobes on a sphere; same value as classical Thomson problem.")
    print()

    # ============== 4. REACTION KINETICS ==============
    print()
    print("=" * 70)
    print("4. REACTION KINETICS (Arrhenius, substrate barrier crossing)")
    print("=" * 70)
    print()
    print("Standard: k = A·exp(-E_a/RT)   (Arrhenius rate law)")
    print("  E_a = activation energy, A = pre-exponential frequency factor")
    print()
    print("Substrate:")
    print("  - Reaction = transition between two substrate strain configurations")
    print("  - Transition state = saddle point on substrate energy landscape")
    print("  - Boltzmann tail of thermal substrate fluctuations crosses barrier")
    print("  - Pre-factor A = attempt frequency ~ k_B T/h (Eyring) of substrate mode")
    print()

    print("Worked example — k(T) for E_a = 75 kJ/mol, A = 1e13 s⁻¹:")
    print(f"  {'T [K]':>8s}    {'k [s⁻¹]':>14s}    {'half-life':>15s}")
    Ea = 75e3   # J/mol
    A = 1e13
    for T in (250, 298, 350, 400, 500, 700):
        k = A * math.exp(-Ea / (R_GAS * T))
        if k > 0:
            t_half = math.log(2) / k
            if t_half > 3.15e7:
                hl = f"{t_half/3.15e7:.2e} yr"
            elif t_half > 86400:
                hl = f"{t_half/86400:.2e} days"
            elif t_half > 60:
                hl = f"{t_half/60:.2e} min"
            else:
                hl = f"{t_half:.2e} s"
        else:
            hl = "∞"
        print(f"  {T:>8d}    {k:>12.3e}      {hl:>15s}")
    print()
    print("Rule of thumb (from Arrhenius): rate doubles per ~10 K near 300 K.")
    print()

    # ============== 5. CATALYSIS ==============
    print()
    print("=" * 70)
    print("5. CATALYSIS (substrate strain alignment lowers E_a)")
    print("=" * 70)
    print()
    print("Standard: catalyst provides alternate path with lower E_a;")
    print("  not consumed; does not shift equilibrium (only kinetics).")
    print()
    print("Substrate:")
    print("  - Catalyst surface/site offers PRE-ALIGNED strain template")
    print("  - Reactants bind in a near-transition-state geometry")
    print("  - Effective barrier dropped by template-stabilization energy")
    print("  - Drag γ on dissociation step regenerates free catalyst")
    print()
    print("Rate enhancement = exp(ΔE_a / RT). For ΔE_a = 40 kJ/mol at 300 K:")
    enhancement = math.exp(40e3 / (R_GAS * 300))
    print(f"  enhancement = exp(40000/(8.314·300)) = {enhancement:.3e}")
    print()
    print("Industrial catalysts (substrate framework view):")
    print(f"  {'process':>30s}    {'catalyst':>20s}    {'ΔE_a drop':>10s}")
    cats = [
        ('Haber (NH₃ synthesis)',       'Fe/K₂O',           '~120 kJ/mol'),
        ('Contact (H₂SO₄)',             'V₂O₅',             '~80 kJ/mol'),
        ('Catalytic cracking',          'Zeolite',          '~100 kJ/mol'),
        ('Auto exhaust (NOx, CO)',      'Pt/Pd/Rh',         '~80 kJ/mol'),
        ('Hydrogenation',               'Ni or Pt',         '~60 kJ/mol'),
        ('Enzyme (turnover up to 1e6)', 'protein active site','~50-100 kJ/mol'),
    ]
    for p, c, d in cats:
        print(f"  {p:>30s}    {c:>20s}    {d:>10s}")
    print()

    # ============== 6. THERMOCHEMISTRY ==============
    print()
    print("=" * 70)
    print("6. THERMOCHEMISTRY (ΔH_f, Hess's law, substrate energy conservation)")
    print("=" * 70)
    print()
    print("Standard: ΔH_rxn = Σ ΔH_f(products) - Σ ΔH_f(reactants)   [Hess]")
    print("  Path-independent: enthalpy is a state function.")
    print()
    print("Substrate:")
    print("  - ΔH = difference in substrate strain energy between configurations")
    print("  - State-function property = strain energy is determined by configuration,")
    print("    not by trajectory (drag γ dissipates path-dependent kinetic energy")
    print("    into heat, but FINAL strain energy is path-independent)")
    print()
    print("Standard enthalpies of formation ΔH_f° at 298 K:")
    print(f"  {'species':>15s}    {'ΔH_f° [kJ/mol]':>15s}")
    hf = [
        ('H₂O(l)',     -285.8),
        ('H₂O(g)',     -241.8),
        ('CO₂(g)',     -393.5),
        ('CO(g)',      -110.5),
        ('CH₄(g)',     -74.8),
        ('C₂H₆(g)',    -84.7),
        ('NH₃(g)',     -45.9),
        ('NaCl(s)',    -411.2),
        ('Glucose(s)', -1273.3),
        ('O₂(g)',      0.0),
    ]
    for s, h in hf:
        print(f"  {s:>15s}    {h:>13.1f}")
    print()
    print("Example — combustion of methane:")
    print("  CH₄ + 2 O₂ → CO₂ + 2 H₂O(l)")
    dH = -393.5 + 2*(-285.8) - (-74.8) - 2*0.0
    print(f"  ΔH = {dH:.1f} kJ/mol  (exothermic — substrate strain released as heat)")
    print()

    # ============== 7. ACID-BASE ==============
    print()
    print("=" * 70)
    print("7. ACID-BASE (pKa, water autoionization)")
    print("=" * 70)
    print()
    print("Standard:")
    print("  Water autoionization: 2 H₂O ⇌ H₃O⁺ + OH⁻,  K_w = 1e-14 at 25°C")
    print("  pH = -log[H₃O⁺],  pKa = -log Ka,  Henderson-Hasselbalch")
    print()
    print("Substrate:")
    print("  - Proton transfer = migration of a strain-bridge node")
    print("  - Stronger acid = looser O-H strain bridge (lower bond energy)")
    print("  - Solvent (water) provides hydrogen-bonded substrate network")
    print("    that stabilizes the resulting charged strain pattern")
    print()
    print(f"  {'acid':>20s}    {'pKa':>6s}    {'class':>20s}")
    pkas = [
        ('HCl',                  -7,    'strong'),
        ('H₂SO₄ (1st)',          -3,    'strong'),
        ('HNO₃',                 -1.4,  'strong'),
        ('H₃O⁺',                 -1.74, 'reference'),
        ('HF',                   3.17,  'weak'),
        ('Acetic (CH₃COOH)',     4.76,  'weak'),
        ('Carbonic (1st)',       6.35,  'weak'),
        ('H₂S',                  7.0,   'weak'),
        ('NH₄⁺',                 9.25,  'weak'),
        ('H₂O',                  15.7,  'reference'),
        ('CH₄',                  50.0,  'effectively non-acid'),
    ]
    for a, k, c in pkas:
        print(f"  {a:>20s}    {k:>6.2f}    {c:>20s}")
    print()
    print("At 25°C: pH + pOH = 14; neutral water pH = 7.")
    print()

    # ============== 8. ELECTROCHEMISTRY ==============
    print()
    print("=" * 70)
    print("8. ELECTROCHEMISTRY (E°, Nernst equation)")
    print("=" * 70)
    print()
    print("Standard:")
    print("  Cell potential: E_cell = E°_cathode - E°_anode")
    print("  Nernst:  E = E° - (RT/nF) ln Q,   F = 96485 C/mol")
    print("  ΔG = -nFE")
    print()
    print("Substrate:")
    print("  - Half-cell potential = substrate strain-energy difference per electron")
    print("    between reduced and oxidized atomic configurations")
    print("  - Electron transfer = hopping of a substrate bound-state mode")
    print("  - Nernst log term = configurational entropy of reactant strain modes")
    print()
    print("Standard reduction potentials E° at 25°C (vs SHE):")
    print(f"  {'half reaction':>40s}    {'E° [V]':>8s}")
    redox = [
        ('F₂ + 2e⁻ → 2 F⁻',                        2.87),
        ('O₃ + 2H⁺ + 2e⁻ → O₂ + H₂O',              2.07),
        ('MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4 H₂O',       1.51),
        ('Cl₂ + 2e⁻ → 2 Cl⁻',                      1.36),
        ('O₂ + 4H⁺ + 4e⁻ → 2 H₂O',                 1.23),
        ('Ag⁺ + e⁻ → Ag',                          0.80),
        ('Cu²⁺ + 2e⁻ → Cu',                        0.34),
        ('2 H⁺ + 2e⁻ → H₂  (SHE reference)',       0.00),
        ('Pb²⁺ + 2e⁻ → Pb',                       -0.13),
        ('Fe²⁺ + 2e⁻ → Fe',                       -0.44),
        ('Zn²⁺ + 2e⁻ → Zn',                       -0.76),
        ('Al³⁺ + 3e⁻ → Al',                       -1.66),
        ('Na⁺ + e⁻ → Na',                         -2.71),
        ('Li⁺ + e⁻ → Li',                         -3.04),
    ]
    for rxn, e in redox:
        print(f"  {rxn:>40s}    {e:>+6.2f}")
    print()

    print("Example — Daniell cell (Zn|Zn²⁺ || Cu²⁺|Cu):")
    E_cell = 0.34 - (-0.76)
    print(f"  E°_cell = E°(Cu) - E°(Zn) = 0.34 - (-0.76) = {E_cell:.2f} V")
    print(f"  ΔG° = -nFE = -2 · 96485 · {E_cell:.2f} = {-2*96485*E_cell/1000:.0f} kJ/mol")
    print()

    print("Nernst at 25°C with [Cu²⁺]=0.1 M, [Zn²⁺]=1.0 M:")
    Q = 1.0 / 0.1   # [Zn²⁺]/[Cu²⁺]
    E_nernst = E_cell - (R_GAS * 298 / (2 * 96485)) * math.log(Q)
    print(f"  E = {E_cell:.2f} - (RT/2F) ln({Q:.1f}) = {E_nernst:.4f} V")
    print()

    # ============== SUMMARY ==============
    print()
    print("=" * 70)
    print("Summary: substrate IS chemistry")
    print("=" * 70)
    print()
    print("Chemistry maps onto substrate framework cleanly:")
    print("  - Atoms = nuclear strain centers + bound electron modes")
    print("  - Bonds = strain bridges (covalent / ionic / metallic / H-bond)")
    print("  - Geometry = strain-energy minimization (VSEPR is exact)")
    print("  - Kinetics = Boltzmann-driven barrier crossing on strain landscape")
    print("  - Catalysis = pre-aligned strain template lowers barrier")
    print("  - Thermochem = strain-energy state function (Hess's law)")
    print("  - Acid-base = strain-bridge proton hopping")
    print("  - Electrochem = strain-energy difference per transferred electron-mode")
    print()
    print("Substrate ADDS NOTHING new to chemical numbers; QM-equivalence is exact.")
    print()
    print("Substrate ADDITIONS:")
    print("  - Unifies chemical bonds, nuclear strong force, electrical conduction")
    print("    as ONE class of substrate strain bridge at different scales:")
    print("      · nuclear:  fm scale, ~MeV/bond  (strong-force strain bridge)")
    print("      · chemical: pm scale, ~eV/bond   (electronic strain bridge)")
    print("      · metallic: nm scale, ~meV/mode  (delocalized strain bridge)")
    print("  - Drag γ provides physical mechanism for irreversibility (2nd law)")
    print("  - Reaction-coordinate saddle points = topological strain features")
    print()
    print("Practical impact: standard chemistry calculations unchanged.")
    print("Conceptual gain: chemistry is a SCALE of the same substrate physics")
    print("  that runs from QCD (nuclear) through condensed matter (electrical).")


if __name__ == "__main__":
    main()
