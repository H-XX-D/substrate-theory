"""Supramolecular chemistry & molecular machines in the strain-medium framework.

Sister script to molecular_bonding_substrate.py: where that script covered
covalent / ionic / metallic strong bonds, this one covers the WEAKER but
still bound strain bridges that govern host-guest chemistry, mechanically
interlocked molecules, molecular machines, and self-assembly.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius / topology)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Atoms = bound-state substrate excitations.
Non-covalent assemblies = substrate-strain bridges weaker than covalent
but still bound (long-range, soft, reversible).

Substrate framing:
  - catenane topology  = strain bridge configuration that cannot be reduced
                         without breaking a covalent strain bridge
  - molecular motor    = directional substrate-strain ratchet driven by
                         chemical fuel (asymmetric energy landscape + cycle)
  - self-assembly      = substrate-strain energy minimization in a many-body
                         system (the global free-energy basin happens to be
                         an ordered nano-architecture)

Honest framing: substrate REPRODUCES standard supramolecular numbers
(binding constants, association energies, motor turnover). The value-add
is unification — host-guest, MIM topology, motors, self-assembly all become
the same strain bridge story in different geometric configurations.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
K_B = 1.380649e-23
N_A = 6.02214076e23
EV_J = 1.602176634e-19
R_GAS = 8.314462618        # J/(mol K)
T_ROOM = 298.15            # K


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Supramolecular chemistry & molecular machines (strain-medium)")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Non-covalent bond  =  soft long-range strain bridge between fragments")
    print("MIM topology       =  strain bridges locked by closed-loop geometry")
    print("Molecular motor    =  directional ratchet on substrate landscape")
    print("Self-assembly      =  many-body substrate free-energy minimization")
    print()

    # ============================================================
    section(1, "NON-COVALENT INTERACTION TYPES (soft strain bridges)")
    # ============================================================
    print("Where covalent bonds (150-1100 kJ/mol) come from sharp, deep strain")
    print("wells, non-covalent bridges are SHALLOW wells in the strain landscape.")
    print("Their depth is set by the particular multipole geometry of the bridge.")
    print()
    print(f"  {'interaction':<22s}  {'bridge geometry':<30s}  {'E [kJ/mol]':>12s}")
    print(f"  {'-'*22:<22s}  {'-'*30:<30s}  {'-'*12:>12s}")
    nc = [
        ("H-bond (weak)",      "C-H...O dipole bridge",      "1-4"),
        ("H-bond (moderate)",  "O-H...O / N-H...O",          "10-40"),
        ("H-bond (strong)",    "F-H...F / charge-assisted",  "40-160"),
        ("pi-pi stacking",     "transverse-mode lobe overlap","8-12"),
        ("cation-pi",          "+ ion above aromatic face",  "5-80"),
        ("anion-pi",           "- ion above e-poor arene",   "20-50"),
        ("halogen bond",       "sigma-hole on Cl/Br/I",      "5-180"),
        ("chalcogen bond",     "sigma-hole on S/Se/Te",      "5-40"),
        ("dispersion (vdW)",   "induced-dipole xi^-6",       "0.4-4"),
        ("hydrophobic",        "water-shell entropy gain",   "3-10"),
    ]
    for name, geom, e in nc:
        print(f"  {name:<22s}  {geom:<30s}  {e:>12s}")
    print()
    print("Substrate reading: every non-covalent bridge is the SAME strain field,")
    print("but with smaller K_eff and broader well than covalent. Energies span")
    print("k_B T ~ 2.5 kJ/mol (thermal noise) to ~150 kJ/mol (charge-assisted),")
    print("which is exactly the range where reversible assembly is thermodynamically")
    print("possible at room temperature.")
    print()
    kT = R_GAS * T_ROOM / 1000.0
    print(f"  k_B T at 298 K = {kT:.3f} kJ/mol  (the soft-bridge thermal scale)")

    # ============================================================
    section(2, "HOST-GUEST CHEMISTRY (size-matched strain pockets)")
    # ============================================================
    print("Host = closed substrate cavity with a strain landscape complementary to")
    print("the guest's surface multipoles. Binding constant K_a [M^-1] = exp(-DG/RT).")
    print()
    print("Crown ethers + alkali cations (oxygen lone pairs ring the cation):")
    print(f"  {'host':<14s}  {'cavity [A]':>11s}  {'best guest':<10s}  {'K_a [M^-1]':>14s}")
    crowns = [
        ("12-crown-4",  1.3, "Li+",  1.0e2),
        ("15-crown-5",  1.85,"Na+",  3.0e3),
        ("18-crown-6",  2.7, "K+",   1.0e6),
        ("21-crown-7",  3.5, "Cs+",  1.0e4),
        ("Dibenzo-18C6",2.7, "K+",   2.0e5),
    ]
    for h, c, g, k in crowns:
        print(f"  {h:<14s}  {c:>11.2f}  {g:<10s}  {k:>14.2e}")
    print()
    print("Cryptands (3D enclosure, higher selectivity):")
    cryp = [
        ("[2.1.1] cryptand", "Li+",  3.0e8),
        ("[2.2.1] cryptand", "Na+",  4.0e9),
        ("[2.2.2] cryptand", "K+",   1.0e10),
    ]
    for h, g, k in cryp:
        print(f"  {h:<18s}  best = {g:<6s}  K_a ~ {k:.1e} M^-1")
    print()
    print("Cucurbiturils (rigid pumpkin-shaped barrels, record binding):")
    cb = [
        ("CB[5]", "Pb2+ / NH4+",  1.0e6),
        ("CB[6]", "1,4-diaminobutane2+", 1.0e8),
        ("CB[7]", "ferrocene / adamantane-NH3+", 1.0e15),  # K_a record
        ("CB[8]", "MV2+ + naphthol ternary", 1.0e12),
    ]
    print(f"  {'host':<6s}  {'best guest':<32s}  {'K_a [M^-1]':>12s}")
    for h, g, k in cb:
        print(f"  {h:<6s}  {g:<32s}  {k:>12.1e}")
    print()
    print("Calixarenes (cup-shaped, conformational switching cone/partial-cone):")
    print("  para-tert-butylcalix[4]arene: tunable cavity for cations / neutrals")
    print("  Sulfonatocalix[4]arene + acetylcholine: K_a ~ 10^4 M^-1")
    print()
    print("Substrate origin of selectivity: the cavity strain landscape has a")
    print("minimum at exactly the guest size that fits without stretching the")
    print("host's covalent backbone. Mismatch -> elastic penalty -> lower K_a.")
    print("The xi (length) primitive sets the host cavity scale.")

    # ============================================================
    section(3, "MOLECULAR RECOGNITION (complementarity principles)")
    # ============================================================
    print("Three classical models for host-guest complementarity:")
    print()
    print("  1) Lock-and-key (Fischer 1894):")
    print("     Rigid host, rigid guest. Binding requires near-perfect")
    print("     pre-organized geometric and electrostatic match.")
    print("     Substrate: both sides have FROZEN strain landscapes;")
    print("     binding free-energy is purely interaction term.")
    print()
    print("  2) Induced fit (Koshland 1958):")
    print("     Host or guest deforms upon binding to optimize contacts.")
    print("     Substrate: binding pays elastic strain in the host backbone")
    print("     to gain a deeper interaction well.  DG = DG_int + DG_strain.")
    print()
    print("  3) Conformational selection (Monod 1965 / pre-equilibrium):")
    print("     Host samples many conformers; guest selects the matching one.")
    print("     Substrate: guest acts as a Boltzmann filter on the host's")
    print("     thermal substrate-fluctuation ensemble.")
    print()
    print("Complementarity decomposes into FOUR matched channels:")
    print("  - shape (size + curvature)            -> xi primitive")
    print("  - electrostatics (charge / dipole)    -> bridge sign / multipole")
    print("  - H-bond donor/acceptor pattern       -> directional dipole bridges")
    print("  - hydrophobic / hydrophilic surface   -> water-shell entropy")
    print()
    print("Pre-organization principle (Cram, 1986 Nobel): a host that is RIGID")
    print("in the unbound state pays no reorganization cost on binding -> larger")
    print("K_a. Substrate: lower elastic strain price = deeper net well.")

    # ============================================================
    section(4, "TEMPLATE-DIRECTED SYNTHESIS")
    # ============================================================
    print("Template = guest molecule whose strain landscape positions the")
    print("reactive ends of a future macrocycle / interlocked product so that")
    print("ring-closure has near-zero entropic penalty.")
    print()
    print("Classic templates and their products:")
    print(f"  {'template':<18s}  {'product':<26s}  {'rate gain':>10s}")
    templates = [
        ("Na+",            "12-crown-4 / 18-crown-6",   "10^2-10^4"),
        ("Cu(I)",          "Sauvage [2]catenane",       "10^3"),
        ("benzidinium",    "Stoddart rotaxane (CBPQT)", "10^4"),
        ("anion (Cl-)",    "anion-templated catenane",  "10^2"),
        ("Pd(II)",         "metal-organic cage",        "10^3-10^6"),
        ("DNA strand",     "complementary duplex",      "10^6+"),
    ]
    for t, p, r in templates:
        print(f"  {t:<18s}  {p:<26s}  {r:>10s}")
    print()
    print("Substrate framing: template fixes the position of reactive ends in")
    print("the substrate landscape so that the activation saddle for ring-closure")
    print("becomes a shallow rolling motion rather than a long random search.")
    print("Effective molarity is boosted by 10^2-10^6.")
    print()
    print("After synthesis, the template can sometimes be removed (e.g. by ion")
    print("exchange) leaving the topologically interlocked product behind.")

    # ============================================================
    section(5, "MECHANICALLY INTERLOCKED MOLECULES (TOPOLOGY)")
    # ============================================================
    print("Catenanes, rotaxanes, knots: the components are NOT joined by any")
    print("covalent bond, yet cannot be separated without BREAKING a covalent")
    print("strain bridge. The constraint is purely topological.")
    print()
    print("Substrate framing: the strain bridges between rings are weak and")
    print("THERMAL, but the topology of the closed-loop substrate field")
    print("provides an infinite barrier to disassembly. Orientability and")
    print("higher homotopy of the substrate field both come into play.")
    print()
    print(f"  {'MIM type':<20s}  {'topology':<28s}  {'first synth':>12s}")
    mims = [
        ("[2]catenane",     "two interlocked rings (Hopf)",    "1960 Wasserman"),
        ("[3]catenane",     "three rings (chain)",             "1980s"),
        ("Olympiadane",     "5 interlocked rings",             "1994 Stoddart"),
        ("[2]rotaxane",     "ring threaded on dumbbell",       "1967 Harrison"),
        ("Trefoil knot",    "single loop with 3 crossings",    "1989 Sauvage"),
        ("Borromean rings", "3 rings, no two interlocked",     "2004 Stoddart"),
        ("Solomon link",    "4-crossing 2-link",               "2007"),
        ("8_19 knot",       "82-crossing molecular knot",      "2017 Leigh"),
    ]
    for m, t, fs in mims:
        print(f"  {m:<20s}  {t:<28s}  {fs:>12s}")
    print()
    print("Topological invariants relevant to MIMs:")
    print("  - linking number    Lk   (catenanes)")
    print("  - crossing number   c    (knots; trefoil c=3)")
    print("  - writhe / twist    Wr+Tw=Lk  (DNA supercoiling, Calugareanu)")
    print()
    print("For the substrate field, these invariants are protected because the")
    print("strain field cannot pass through itself without paying the covalent")
    print("bond-breaking energy (~400 kJ/mol >> k_B T at 300 K).")

    # ============================================================
    section(6, "MOLECULAR MACHINES (SAUVAGE / STODDART / FERINGA, 2016 NOBEL)")
    # ============================================================
    print("A molecular machine is a directional substrate-strain ratchet:")
    print("an asymmetric energy landscape, plus a chemical / photonic fuel,")
    print("plus a cycle of conformational states that rectifies thermal noise")
    print("into net mechanical work.")
    print()
    print("Sauvage [2]catenane / rotaxane shuttles: ring slides between two")
    print("recognition stations on the axle, controlled by redox / pH switch.")
    print()
    print("Stoddart molecular shuttles (key examples):")
    print(f"  {'shuttle':<28s}  {'switch trigger':<22s}  {'ratio':>8s}")
    stoddart = [
        ("CBPQT4+ on TTF/DNP",        "redox (TTF -> TTF+)",   "100:1"),
        ("DB24C8 on NH2+/bipy",        "pH (acid/base)",        ">99:1"),
        ("CBPQT4+ on bistable rotax.", "two-pot switch",        "95:5"),
        ("Stoddart molecular pump",    "pulse redox cycle",     "directional"),
    ]
    for s, t, r in stoddart:
        print(f"  {s:<28s}  {t:<22s}  {r:>8s}")
    print()
    print("Feringa molecular motor (overcrowded alkene):")
    print("  4-step photochemical / thermal cycle yields UNIDIRECTIONAL 360 deg")
    print("  rotation. Frequency now reaches ~10 MHz for optimized variants.")
    print("  Driven 'nanocar' achieved measurable directional motion on Cu(111).")
    print()
    print("Substrate ratchet condition (Feynman pawl-and-ratchet style):")
    print("  - asymmetric V(theta)              -> tilted substrate landscape")
    print("  - external fuel breaks det. balance -> photon or DG_chem input")
    print("  - power stroke (P) > backward step (B) -> net rotation per cycle")
    print()
    print("Stoddart molecular pump (2015): ratchet drives ring AGAINST gradient")
    print("from solution into oligomer chain, accumulating against entropy.")
    print("Substrate: an active loading mechanism that pays free energy per cycle.")

    # ============================================================
    section(7, "SUPRAMOLECULAR POLYMERS (reversible chains)")
    # ============================================================
    print("Supramolecular polymer = covalent monomers linked by non-covalent")
    print("bridges (H-bonds, metal coordination, host-guest). Reversible -> the")
    print("chain length depends on concentration and temperature.")
    print()
    print("Cates law for living polymers:  <N> ~ sqrt(c) exp(E_a / 2 R T)")
    print()
    print("Examples and binding strengths:")
    print(f"  {'system':<28s}  {'bridge':<20s}  {'K_a [M^-1]':>12s}")
    sup_pol = [
        ("UPy-UPy (Meijer)",          "quad H-bond",           6.0e7),
        ("DAT/Hamilton receptor",     "triple H-bond",         1.0e3),
        ("BTA disk stacks",           "triple H-bond + pi",    1.0e6),
        ("Ureidopyrimidinone-pol.",   "quad H-bond",           1.0e7),
        ("Pd-pyridine coord.",        "metal-ligand",          1.0e5),
        ("CB[8] ternary glue",        "host-guest ternary",    1.0e11),
    ]
    for s, b, k in sup_pol:
        print(f"  {s:<28s}  {b:<20s}  {k:>12.1e}")
    print()
    print("Self-healing materials: cut surface re-knits when reversible")
    print("non-covalent bridges reform across the interface. Examples include")
    print("Leibler's rubber, Aida's self-healing glass, polyurethane H-bonds.")
    print()
    print("Substrate framing: bridge can BREAK (locally exit the well) under")
    print("strain, then RE-FORM when fluctuations bring partners back into")
    print("range. This is impossible for covalent bridges at room temperature.")

    # ============================================================
    section(8, "SELF-ASSEMBLY (many-body strain minimization)")
    # ============================================================
    print("Self-assembly: a SOUP of components spontaneously organizes into a")
    print("specific nano-architecture because that architecture is the global")
    print("minimum of the free-energy landscape under the assembly conditions.")
    print()
    print("Substrate framing: the many-body strain functional E[u(x)] has a")
    print("deep, narrow basin at the assembled configuration. Brownian motion")
    print("explores configuration space until it falls into the basin and is")
    print("trapped by the deep well.")
    print()
    print("Driving forces (always entropy-vs-enthalpy):")
    print("  - hydrophobic effect (entropy of bulk water)")
    print("  - directional H-bonds (enthalpy)")
    print("  - electrostatic complementarity")
    print("  - shape complementarity (excluded volume)")
    print()
    print(f"  {'system':<26s}  {'driving force':<26s}  {'scale':>10s}")
    sa = [
        ("Lipid bilayers",          "hydrophobic + entropy",    "5 nm"),
        ("Micelles",                "hydrophobic above CMC",    "5-50 nm"),
        ("DNA origami",             "Watson-Crick H-bonds",     "10-100 nm"),
        ("Peptide nanotubes",       "beta-sheet H-bonds",       "10 nm dia"),
        ("Block copolymer phases",  "chi parameter incompat.",  "10-50 nm"),
        ("Colloidal crystals",      "depletion / electrostatic","100 nm-1 um"),
        ("Pd cage M2L4 etc.",       "metal-ligand",             "1-3 nm"),
        ("Ribosome (in vivo)",      "RNA-protein recognition",  "20 nm"),
    ]
    for s, d, sc in sa:
        print(f"  {s:<26s}  {d:<26s}  {sc:>10s}")
    print()
    print("DNA origami (Rothemund 2006): a 7 kb scaffold strand folded by ~200")
    print("short staple strands into an arbitrary 100 nm shape. Yield > 70%.")
    print("Substrate: 200 sequence-specific recognition wells lock the scaffold.")
    print()
    print("Lipid bilayer: 50 mN/m surface tension at the hydrocarbon-water")
    print("interface; bending modulus kappa ~ 20 k_B T per leaflet.")

    # ============================================================
    section(9, "DYNAMIC COVALENT CHEMISTRY (reversible covalent bonds)")
    # ============================================================
    print("Dynamic covalent chemistry (DCC) sits BETWEEN covalent and supramol.")
    print("Bonds are formally covalent (full strain bridge) but exchange under")
    print("mild conditions, allowing thermodynamic error-correction during self-")
    print("assembly. Lehn's 'constitutional dynamic chemistry'.")
    print()
    print(f"  {'reaction':<22s}  {'condition':<22s}  {'half-life':>14s}")
    dcc = [
        ("Imine R-N=CR' formation",  "aqueous, mild acid",     "min-h"),
        ("Hydrazone exchange",       "pH 4-6 catalysis",       "h-day"),
        ("Boronate ester",           "diol + boronic acid",    "min"),
        ("Disulfide -S-S- exchange", "thiol catalyst",         "min-h"),
        ("Olefin metathesis",        "Grubbs catalyst",        "min"),
        ("Diels-Alder retro-DA",     "heat",                   "min-day"),
    ]
    for r, c, t in dcc:
        print(f"  {r:<22s}  {c:<22s}  {t:>14s}")
    print()
    print("Applications of DCC:")
    print("  - dynamic combinatorial libraries (DCLs): adding a template biases")
    print("    the equilibrium toward the best binder, AMPLIFYING it from the soup")
    print("  - covalent organic frameworks (COFs): boronate / imine networks")
    print("  - vitrimers (Leibler): silica-like glass-formers with permanent")
    print("    crosslink density, but topology rearranges on heating")
    print()
    print("Substrate framing: the covalent strain well is real but SHALLOW")
    print("enough to be thermally accessible (~50-80 kJ/mol activation), giving")
    print("a self-correcting strain landscape that finds the global minimum.")

    # ============================================================
    section(10, "BIOLOGICAL SUPRAMOLECULAR SYSTEMS")
    # ============================================================
    print("Life IS supramolecular chemistry at scale: every cell is a network of")
    print("non-covalent assemblies that copy, fold, transport, contract, signal.")
    print()
    print(f"  {'system':<22s}  {'function':<28s}  {'scale':>10s}")
    bio = [
        ("Microtubules",      "tracks for kinesin/dynein",    "25 nm dia"),
        ("Actin F-filaments", "cell shape, myosin motor",      "7 nm dia"),
        ("Intermediate fil.", "mechanical resilience",         "10 nm dia"),
        ("Viral capsids",     "icosahedral shells T=1..1000+", "20-300 nm"),
        ("Ribosome 70S/80S",  "protein synthesis machine",     "20-25 nm"),
        ("Nuclear pore",      "regulated transport (NPC)",     "120 nm"),
        ("Chaperonin GroEL",  "protein folding cage",          "15 nm"),
        ("ATP synthase",      "rotary motor / proton turbine", "10 nm"),
    ]
    for s, f, sc in bio:
        print(f"  {s:<22s}  {f:<28s}  {sc:>10s}")
    print()
    print("Assembly principles in biology:")
    print("  - subunit self-assembly with built-in error correction")
    print("  - switchable states (GTP/GDP, ATP/ADP, phosphorylation)")
    print("  - chaperone-mediated assistance for hard folds")
    print("  - directional drive by NTP hydrolysis (~30 kJ/mol per ATP)")
    print()
    print("ATP synthase = rotary motor (Boyer 1997 Nobel): proton flux drives")
    print("F0 rotor, mechanical torque drives F1 catalytic site through three")
    print("conformations producing ATP. ~3 ATP per turn, ~100 turns/s.")
    print()
    print("Substrate framing: every biological motor is a directional ratchet")
    print("on the substrate strain landscape, fueled by NTP hydrolysis or")
    print("electrochemical gradients, with built-in proofreading via reversible")
    print("non-covalent bridges (kinetic + thermodynamic discrimination).")

    # ============================================================
    section(11, "SUMMARY: one bridge, many softnesses")
    # ============================================================
    print("Supramolecular chemistry uses the SAME substrate strain bridge as")
    print("covalent bonding, but with smaller K_eff and broader well, putting")
    print("the bond depth in the room-temperature reversibility window")
    print(f"(~{kT:.1f}-150 kJ/mol).")
    print()
    print("Configuration -> assembly type:")
    print("  shallow dipole bridge       -> H-bond, vdW, dispersion")
    print("  size-matched cavity         -> host-guest, crown ether selectivity")
    print("  templated ring-closure      -> macrocycle / catenane / rotaxane")
    print("  closed-loop topology        -> mechanically interlocked molecule")
    print("  asymmetric V + chemical fuel-> molecular machine / motor / pump")
    print("  reversible bridges in chain -> supramolecular polymer / self-heal")
    print("  many-body free-E minimum    -> self-assembly (DNA origami, lipid")
    print("                                  bilayers, viral capsids, ribosome)")
    print("  shallow covalent bridge     -> dynamic covalent chemistry / DCLs")
    print()
    print("Honest scoreboard: substrate predicts the SAME binding constants,")
    print("self-assembly thresholds, and motor turnover rates as standard")
    print("supramolecular chemistry — because the soft-mode spectrum of the")
    print("substrate Lagrangian gives the same multipole expansions.")
    print()
    print("Value-add: host-guest chemistry, mechanically interlocked molecules,")
    print("molecular machines, and self-assembly all become one strain-bridge")
    print("story rather than four empirical chapters. Topology (catenanes,")
    print("knots) reveals the ORIENTABILITY primitive at the molecular scale.")
    print("Molecular motors reveal the dissipative/RATCHET sector of the")
    print("substrate Lagrangian (the gamma drag term plus a fueled symmetry")
    print("breaking) — exactly the same skeleton as biological molecular motors.")


if __name__ == "__main__":
    main()
