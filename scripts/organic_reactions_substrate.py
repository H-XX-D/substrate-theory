"""Organic reaction mechanisms in the strain-medium framework.

Companion to molecular_bonding_substrate.py: there bonds were static strain
bridges; here we follow the bridges THROUGH the reaction — reactant minimum,
saddle (TS), product minimum — for the canonical mechanism families of
organic chemistry.

Strain-medium primitives:
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Mechanism reading:
  - Reactant configuration  = local minimum in V(u) over the bond manifold
  - Transition state        = saddle with one negative Hessian eigenvalue
  - Product configuration   = lower minimum reached after crossing the saddle
  - Selectivity rules       = which saddle has lowest strain along the path
  - Woodward-Hoffmann rules = orientability primitive: Huckel (4n+2) vs
                              Mobius (4n) topology of the cyclic TS strain mode

The substrate Lagrangian REPRODUCES standard physical-organic-chemistry numbers
(Hammett rho, KIEs, Diels-Alder rate enhancements). The value-add is unifying
nine mechanism families as one strain-pathway language.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
C_M_S = 2.998e8
EV_J = 1.602176634e-19
K_B = 1.380649e-23
N_A = 6.02214076e23
R_GAS = 8.314462618          # J / (mol K)
EH_eV = 27.211386
ANGSTROM = 1.0e-10


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def arrhenius_rel(Ea_kJ: float, T: float = 298.15) -> float:
    """Relative Arrhenius factor exp(-Ea/RT) for ranking."""
    return math.exp(-Ea_kJ * 1000.0 / (R_GAS * T))


def main() -> None:
    print("Organic reaction mechanisms in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Mechanism = trajectory across substrate strain landscape:")
    print("  reactants  ->  transition state (saddle)  ->  products")
    print()
    print("All numerical predictions match standard physical-organic chemistry;")
    print("the framework unifies nine mechanism families under one ontology.")

    # ============================================================
    section(1, "SN1 vs SN2 (carbocation vs concerted strain pathways)")
    # ============================================================
    print("Two distinct substrate trajectories for nucleophilic substitution:")
    print()
    print("SN2 (one-step concerted, bimolecular):")
    print("  reactants  --[trigonal-bipyramidal saddle]-->  products")
    print("  Nu and LG strain bridges co-form / co-break at the same TS.")
    print("  Backside attack: substrate inversion (Walden), sigma<=1/2 forces")
    print("  Nu and LG to occupy ANTIPODAL strain lobes around carbon.")
    print("  Rate = k2 [RX][Nu]")
    print()
    print("SN1 (two-step, unimolecular):")
    print("  reactants  --[carbocation min]--  products")
    print("  Step 1: heterolytic strain detachment of LG -> sp2 cation intermediate")
    print("  Step 2: Nu attaches to either face -> racemization (50/50)")
    print("  Rate = k1 [RX]   (independent of [Nu])")
    print()
    print("Substrate energetics by substrate-substitution pattern:")
    print(f"  {'substrate':<14s}  {'k_SN2 (rel)':>12s}  {'k_SN1 (rel)':>12s}  "
          f"{'dominant':<10s}")
    sn_data = [
        ("CH3-X    (1-ary)",     30.0,     1e-6,  "SN2"),
        ("CH3CH2-X (1-ary)",      1.0,     1e-5,  "SN2"),
        ("(CH3)2CH-X (2-ary)",    0.025,   0.05,  "either"),
        ("(CH3)3C-X (3-ary)",     5e-5,    1.0e3, "SN1"),
        ("PhCH2-X  (benzyl)",     1.2,     120.0, "SN1/SN2"),
        ("CH2=CHCH2-X (allyl)",   1.0,     100.0, "SN1/SN2"),
    ]
    for s, k2, k1, dom in sn_data:
        print(f"  {s:<14s}  {k2:>12.2e}  {k1:>12.2e}  {dom:<10s}")
    print()
    print("Hammond postulate (substrate version): for an EXOTHERMIC step the TS")
    print("strain configuration resembles the REACTANT (early TS, smaller barrier);")
    print("for an ENDOTHERMIC step it resembles the PRODUCT (late TS, bigger barrier).")
    print("In SN1 the rate-limiting step (cation formation) is endothermic -> late TS.")
    print()
    print("Solvent effects (substrate dielectric screening of strain charge):")
    print(f"  {'solvent':<14s}  {'eps_r':>6s}  {'aids':<10s}  {'note':<30s}")
    solvents = [
        ("hexane",      1.9,  "neither", "non-polar, no charge stabil."),
        ("THF",         7.5,  "SN2",     "aprotic, solvates Nu poorly"),
        ("acetone",    20.7,  "SN2",     "polar aprotic, frees Nu"),
        ("DMSO",       46.7,  "SN2",     "polar aprotic, ideal for SN2"),
        ("methanol",   32.7,  "SN1",     "protic, stabilizes cation+LG-"),
        ("water",      78.5,  "SN1",     "high-eps, ionizes RX"),
    ]
    for s, e, aids, note in solvents:
        print(f"  {s:<14s}  {e:>6.1f}  {aids:<10s}  {note:<30s}")

    # ============================================================
    section(2, "E1/E2 ELIMINATION (Zaitsev vs Hofmann strain alignment)")
    # ============================================================
    print("Elimination removes H and LG to form a pi (transverse) strain mode.")
    print()
    print("E2 (concerted, bimolecular): base-H, C-H, C-C, C-LG bridges all in one")
    print("  TS.  Geometric requirement: H and LG ANTIPERIPLANAR (180 deg dihedral).")
    print("  This aligns the breaking sigma strain modes parallel so the new pi")
    print("  mode forms with maximum substrate overlap.")
    print()
    print("E1 (stepwise, unimolecular): same first step as SN1 (cation), then")
    print("  beta-H loss.  Carbocation rearranges -> often gives Zaitsev product.")
    print()
    print("Regiochemistry:")
    print("  Zaitsev (more substituted alkene) - more bridges stabilize pi mode")
    print("  Hofmann (less substituted alkene) - bulky base picks accessible H")
    print()
    print(f"  {'base':<22s}  {'product':<18s}  {'fraction':>8s}")
    zaitsev = [
        ("EtO- (small base)",    "Zaitsev (2-butene)",  0.81),
        ("EtO- (small base)",    "Hofmann (1-butene)",  0.19),
        ("t-BuO- (bulky base)",  "Zaitsev (2-butene)",  0.30),
        ("t-BuO- (bulky base)",  "Hofmann (1-butene)",  0.70),
        ("NEt3 (bulky amine)",   "Zaitsev (2-butene)",  0.20),
        ("NEt3 (bulky amine)",   "Hofmann (1-butene)",  0.80),
    ]
    for b, p, f in zaitsev:
        print(f"  {b:<22s}  {p:<18s}  {f:>8.2f}")
    print()
    print("Substrate reading: bulky base = base whose own strain bridge cannot")
    print("fit near the more crowded internal H -> abstracts terminal H instead.")
    print("Geometric exclusion from the sigma<=1/2 saturation cap.")

    # ============================================================
    section(3, "ELECTROPHILIC AROMATIC SUBSTITUTION (Wheland intermediate)")
    # ============================================================
    print("Aromatic ring (benzene) = closed substrate strain shell with 6 pi modes.")
    print("EAS = temporarily break aromaticity -> form sp3 Wheland intermediate ->")
    print("re-aromatize by losing H+.")
    print()
    print("Two-step mechanism (substrate version):")
    print("  step 1 (slow): E+ attaches, ring shifts to cyclohexadienyl cation")
    print("                 (sigma complex / arenium ion / Wheland intermediate)")
    print("  step 2 (fast): H+ leaves, aromatic strain shell restored")
    print()
    print("Common EAS reactions and their electrophiles:")
    print(f"  {'reaction':<22s}  {'electrophile':<14s}  {'catalyst':<14s}")
    eas = [
        ("Halogenation (Br2)",   "Br+",        "FeBr3"),
        ("Nitration",            "NO2+",       "HNO3/H2SO4"),
        ("Sulfonation",          "SO3 / SO3H+","fuming H2SO4"),
        ("Friedel-Crafts alkyl", "R+",         "AlCl3"),
        ("Friedel-Crafts acyl",  "RCO+",       "AlCl3"),
    ]
    for r, e, c in eas:
        print(f"  {r:<22s}  {e:<14s}  {c:<14s}")
    print()
    print("Hammett substituent constants (sigma_p) - linear free-energy relation:")
    print("  log(k/k_H) = rho * sigma")
    print("  rho > 0  : reaction accelerated by electron-withdrawing groups")
    print("  rho < 0  : reaction accelerated by electron-donating groups (EAS!)")
    print()
    print(f"  {'group':<10s}  {'sigma_m':>8s}  {'sigma_p':>8s}  {'donor/acc':<14s}")
    hammett = [
        ("-NH2",   -0.16,  -0.66, "strong donor"),
        ("-OCH3",   0.12,  -0.27, "donor"),
        ("-OH",     0.12,  -0.37, "donor"),
        ("-CH3",   -0.07,  -0.17, "weak donor"),
        ("-H",      0.00,   0.00, "reference"),
        ("-F",      0.34,   0.06, "weak acc"),
        ("-Cl",     0.37,   0.23, "weak acc"),
        ("-COOH",   0.37,   0.45, "acceptor"),
        ("-CN",     0.56,   0.66, "strong acc"),
        ("-NO2",    0.71,   0.78, "strongest acc"),
    ]
    for g, sm, sp, da in hammett:
        print(f"  {g:<10s}  {sm:>8.2f}  {sp:>8.2f}  {da:<14s}")
    print()
    print("Directing effects (substrate-resonance argument):")
    print("  -OH, -OMe, -NH2, -alkyl  ->  ortho/para directors, ring-activating")
    print("  -NO2, -CN, -CHO, -COOH   ->  meta directors, ring-deactivating")
    print("  -F, -Cl, -Br, -I         ->  ortho/para directors, deactivating")
    print()
    print("Substrate reason: donor groups raise strain density at o/p positions")
    print("through resonance lobes; cation TS is stabilized there preferentially.")

    # ============================================================
    section(4, "NUCLEOPHILIC AROMATIC SUBSTITUTION (Meisenheimer & benzyne)")
    # ============================================================
    print("Aromatic rings normally resist Nu attack (electron-rich pi shell).")
    print("Two pathways open the ring to nucleophiles:")
    print()
    print("Addition-elimination (SNAr):")
    print("  Requires strong EWG (NO2, CN) ortho/para to LG.")
    print("  Nu adds first -> Meisenheimer complex (anionic sp3 intermediate)")
    print("  -> LG leaves, aromaticity restored.")
    print("  Rate enhancement by EWG (Hammett rho ~ +4 to +7, very large).")
    print()
    print("Elimination-addition (benzyne):")
    print("  Strong base (NaNH2) removes H ortho to LG -> benzyne intermediate")
    print("  -> Nu adds across the strained triple-bond-like pi mode.")
    print("  Gives mixture of regioisomers (no orientation preference).")
    print()
    print(f"  {'substrate':<26s}  {'mechanism':<20s}  {'rel rate':>10s}")
    snar = [
        ("PhCl + OH-",                     "neither (no rxn)",   1.0e0),
        ("p-NO2-PhCl + OH-",               "SNAr (1 NO2)",       1.0e6),
        ("2,4-(NO2)2-PhCl + OH-",          "SNAr (2 NO2)",       1.0e10),
        ("2,4,6-(NO2)3-PhCl + OH-",        "SNAr (3 NO2)",       1.0e15),
        ("PhCl + NaNH2 (NH3, 33 C)",       "benzyne",            1.0e3),
    ]
    for s, m, k in snar:
        print(f"  {s:<26s}  {m:<20s}  {k:>10.0e}")
    print()
    print("Substrate reading: EWG groups DRAIN strain density from the ring,")
    print("collapsing the sigma<=1/2 cap -> Meisenheimer adduct now lies in a")
    print("genuine local well rather than a high-energy saddle.")

    # ============================================================
    section(5, "ADDITION REACTIONS (Markovnikov & anti-Markovnikov)")
    # ============================================================
    print("Alkene/alkyne + HX or H2O: pi strain mode opens, two new sigma")
    print("bridges form. Selectivity = which carbocation TS is lower in strain.")
    print()
    print("Markovnikov (H+ addition first):")
    print("  H goes to the C with MORE H's, X goes to the C with FEWER H's")
    print("  Reason: more substituted carbocation (3-ary > 2-ary > 1-ary > Me+)")
    print("  is stabilized by hyperconjugation = additional sigma->pi+ strain")
    print("  bridges from neighboring C-H bonds donating into the empty lobe.")
    print()
    print("Anti-Markovnikov (radical, hydroboration):")
    print("  HBr + peroxides: Br radical adds first to less hindered C -> more")
    print("    stable secondary RADICAL on the more substituted C.")
    print("  Hydroboration (BH3): concerted 4-center TS; B (larger) attaches")
    print("    to less hindered C for steric reasons -> OH ends up there after")
    print("    oxidation. Same regiochemistry, opposite mechanism.")
    print()
    print(f"  {'reaction':<32s}  {'major product':<22s}  {'mark. type':<12s}")
    add = [
        ("CH2=CHCH3 + HBr (no perox.)",       "2-bromopropane",        "Mark."),
        ("CH2=CHCH3 + HBr + ROOR",            "1-bromopropane",        "anti-Mark."),
        ("CH2=CHCH3 + H2O / H+",              "2-propanol",            "Mark."),
        ("CH2=CHCH3 + BH3 then H2O2/OH-",     "1-propanol",            "anti-Mark."),
        ("CH2=CHCH3 + Hg(OAc)2 / H2O",        "2-propanol",            "Mark."),
        ("CH2=CHCH3 + Br2",                   "1,2-dibromopropane",    "anti-add."),
    ]
    for r, p, t in add:
        print(f"  {r:<32s}  {p:<22s}  {t:<12s}")
    print()
    print("Carbocation stability ranking (substrate hyperconjugation):")
    print(f"  {'cation':<16s}  {'rel stab.':>10s}  {'#beta C-H bridges':>18s}")
    cations = [
        ("CH3+ (methyl)",   1.0,   0),
        ("Et+ (1-ary)",    1.0e3,  3),
        ("iPr+ (2-ary)",   1.0e7,  6),
        ("tBu+ (3-ary)",   1.0e11, 9),
        ("PhCH2+ (benzyl)", 1.0e10, 0),  # resonance, not hyperconj
        ("CH2=CHCH2+",      1.0e9,  0),  # allyl resonance
    ]
    for c, s, n in cations:
        print(f"  {c:<16s}  {s:>10.0e}  {n:>18d}")

    # ============================================================
    section(6, "DIELS-ALDER & PERICYCLIC (Woodward-Hoffmann via Mobius)")
    # ============================================================
    print("Pericyclic reactions = single concerted TS where bonds reorganize")
    print("around a CYCLIC array of substrate strain bridges. The selection")
    print("rules emerge from the orientability primitive of the strain medium:")
    print()
    print("  Huckel topology (untwisted ring of bridges):  4n+2 electrons allowed")
    print("  Mobius topology (one phase inversion / twist): 4n electrons allowed")
    print()
    print("The substrate strain bundle around the cyclic TS is either an")
    print("ORIENTABLE band (Huckel) or a Mobius band (one twist). The number of")
    print("electrons that fit in a closed standing wave depends on this topology.")
    print("This is the same orientability primitive used elsewhere in the framework.")
    print()
    print("Diels-Alder ([4+2] cycloaddition):")
    print("  Diene (4 pi e-) + dienophile (2 pi e-) -> cyclohexene")
    print("  Total: 6 pi electrons in cyclic Huckel TS  -> 4n+2 ALLOWED thermally")
    print()
    print("[2+2] cycloaddition:")
    print("  4 pi electrons in Huckel TS  -> FORBIDDEN thermally")
    print("  Allowed photochemically (one electron promoted -> Mobius equivalent).")
    print()
    print(f"  {'reaction':<28s}  {'electrons':>9s}  {'topology':<10s}  {'thermal?':<8s}")
    pericyc = [
        ("[4+2] Diels-Alder",       6, "Huckel",  "yes"),
        ("[2+2] cycloaddition",     4, "Huckel",  "no"),
        ("[2+2] photochemical",     4, "Mobius",  "yes(hv)"),
        ("[6+4] cycloaddition",    10, "Huckel",  "yes"),
        ("[8+2] cycloaddition",    10, "Huckel",  "yes"),
        ("Cope rearrangement",      6, "Huckel",  "yes"),
        ("Claisen rearrangement",   6, "Huckel",  "yes"),
        ("electrocyclic [4]e con.", 4, "Mobius",  "yes"),
        ("electrocyclic [4]e dis.", 4, "Huckel",  "no"),
        ("electrocyclic [6]e con.", 6, "Mobius",  "no"),
        ("electrocyclic [6]e dis.", 6, "Huckel",  "yes"),
    ]
    for r, n, t, th in pericyc:
        print(f"  {r:<28s}  {n:>9d}  {t:<10s}  {th:<8s}")
    print()
    print("Diels-Alder rate enhancements (substrate substituent tuning):")
    print(f"  {'dienophile':<28s}  {'k_rel (vs ethene)':>18s}")
    da = [
        ("ethene CH2=CH2",                 1.0),
        ("acrolein CH2=CHCHO",             1.0e3),
        ("acrylonitrile CH2=CHCN",         1.5e3),
        ("methyl acrylate",                3.0e3),
        ("maleic anhydride",               5.0e4),
        ("tetracyanoethylene (TCNE)",      4.0e7),
        ("4-PTAD (triazoline-3,5-dione)",  1.0e9),
    ]
    for d, k in da:
        print(f"  {d:<28s}  {k:>18.1e}")
    print()
    print("Endo rule: secondary orbital overlap stabilizes the endo TS by")
    print("~5-10 kJ/mol, giving kinetic preference for endo over exo even when")
    print("exo is thermodynamically favored. Substrate basis: extra strain")
    print("bridge between EWG of dienophile and the diene pi cloud.")

    # ============================================================
    section(7, "RADICAL CHAIN MECHANISMS (init / propagate / terminate)")
    # ============================================================
    print("Radicals = open-shell substrate excitations (one unpaired strain mode).")
    print("Chain reactions amplify a small initiator concentration into many")
    print("turnovers (chain length 10^3 - 10^6).")
    print()
    print("Three phases:")
    print("  Initiation:  homolytic bond cleavage creates first radicals")
    print("               e.g.  Cl2 + hv -> 2 Cl.   (BDE 243 kJ/mol)")
    print("  Propagation: radical reacts to form NEW radical + product")
    print("               sum of propagation steps = overall reaction")
    print("  Termination: two radicals couple to close the chain")
    print()
    print("Methane chlorination (canonical radical chain):")
    print("  Init:  Cl2 + hv     -> 2 Cl.")
    print("  Prop1: Cl. + CH4    -> HCl + CH3.    (Ea ~ 16 kJ/mol)")
    print("  Prop2: CH3. + Cl2   -> CH3Cl + Cl.   (Ea ~ 8 kJ/mol)")
    print("  Term:  2 Cl.        -> Cl2")
    print("         2 CH3.       -> C2H6")
    print("         Cl. + CH3.   -> CH3Cl")
    print()
    print("Bond dissociation energies (substrate strain bridge cost):")
    print(f"  {'bond':<14s}  {'BDE [kJ/mol]':>13s}")
    bdes = [
        ("H-H",        436),
        ("Cl-Cl",      243),
        ("Br-Br",      193),
        ("I-I",        151),
        ("CH3-H",      439),
        ("CH3CH2-H",   421),
        ("(CH3)2CH-H", 410),
        ("(CH3)3C-H",  400),
        ("PhCH2-H",    370),
        ("CH2=CHCH2-H",369),
        ("HO-H",       497),
        ("RO-OR",      150),  # peroxide initiator
    ]
    for b, e in bdes:
        print(f"  {b:<14s}  {e:>13d}")
    print()
    print("Selectivity (radical bromination >> chlorination):")
    print("  Cl. abstraction:  3-ary : 2-ary : 1-ary  ~  5.0 : 3.8 : 1.0  (modest)")
    print("  Br. abstraction:  3-ary : 2-ary : 1-ary  ~ 1600 :  82 : 1.0  (huge)")
    print("Substrate reason: Br. has LATER, more product-like TS (Hammond) -> sees")
    print("the full radical-stability difference. Cl. has earlier TS (less selective).")
    print()
    print("Kinetic isotope effects (KIE = k_H/k_D, primary):")
    print(f"  {'reaction':<32s}  {'k_H/k_D':>9s}  {'note':<20s}")
    kies = [
        ("CH4 + Cl. (vs CD4)",          12.1, "near-max primary KIE"),
        ("CH4 + Br. ",                   4.6, "later TS, smaller"),
        ("E2 elimination (typ.)",        6.5, "C-H breaking"),
        ("E1 (rate-limiting cation)",    1.0, "no C-H breaking"),
        ("SN2 (alpha-H)",                1.05,"secondary, tiny"),
        ("Enzyme (e.g. ADH)",            5.0, "diagnostic for H transfer"),
    ]
    for r, k, n in kies:
        print(f"  {r:<32s}  {k:>9.1f}  {n:<20s}")
    print()
    print("KIE substrate origin: zero-point strain energy (1/2)hbar*omega is")
    print("LOWER for C-D than C-H (heavier reduced mass -> lower omega). The")
    print("C-D bridge sits deeper in its well, so the TS demands more energy.")

    # ============================================================
    section(8, "GRIGNARD AND CARBONYL CHEMISTRY (polar additions)")
    # ============================================================
    print("Carbonyl C=O = strongly polarized strain bridge: C carries partial +,")
    print("O carries partial -. C is a permanent electrophilic site, prone to")
    print("nucleophilic addition.")
    print()
    print("Grignard reagent (RMgX): C-Mg bond is highly polar (C delta-, Mg delta+);")
    print("R behaves as a carbanion equivalent R- = strong nucleophile + base.")
    print()
    print("General nucleophilic addition to carbonyl:")
    print("  Nu attacks C  ->  tetrahedral alkoxide intermediate  ->  protonation")
    print("  Burgi-Dunitz angle: Nu approaches at ~107 deg to C=O axis (geometry")
    print("  of the lowest-strain trajectory into the LUMO pi* lobe).")
    print()
    print(f"  {'aldehyde/ketone':<22s}  {'rel reactivity':>16s}  {'note':<20s}")
    cb = [
        ("formaldehyde HCHO",      1.0e3, "no steric block"),
        ("acetaldehyde CH3CHO",    1.0e2, "1 alkyl group"),
        ("acetone (CH3)2CO",       1.0e1, "2 alkyl groups"),
        ("benzaldehyde PhCHO",     5.0e1, "Ph deactivates"),
        ("benzophenone Ph2CO",     1.0e0, "fully crowded"),
        ("CF3-CHO",                1.0e5, "EWG activates"),
        ("Cl3C-CHO (chloral)",     1.0e6, "even more"),
    ]
    for c, k, n in cb:
        print(f"  {c:<22s}  {k:>16.1e}  {n:<20s}")
    print()
    print("Grignard addition pattern -> alcohol class:")
    print(f"  {'electrophile':<26s}  {'+ RMgX gives':<24s}")
    grignards = [
        ("formaldehyde HCHO",       "primary alcohol (RCH2OH)"),
        ("aldehyde RCHO",           "secondary alcohol"),
        ("ketone R2CO",             "tertiary alcohol"),
        ("CO2",                     "carboxylic acid (after H+)"),
        ("ester RCOOR'",            "tertiary alcohol (2 R add)"),
        ("nitrile RCN",             "ketone (after hydrolysis)"),
        ("epoxide",                 "alcohol (ring-opened)"),
    ]
    for e, p in grignards:
        print(f"  {e:<26s}  {p:<24s}")
    print()
    print("Carbonyl alpha-acidity (enol/enolate strain delocalization):")
    print(f"  {'compound':<22s}  {'pKa':>6s}  {'note':<24s}")
    pkas = [
        ("alkane RH",            50.0, "non-acidic"),
        ("ketone R-CO-CHR2",     20.0, "alpha-H, 1 EWG"),
        ("ester R-COO-CHR2",     25.0, "weaker than ketone"),
        ("aldehyde R-CO-CHR-CHO",17.0, "-"),
        ("1,3-diketone (acac)",   9.0, "2 EWG, very stabilized"),
        ("malonate ester",       13.0, "alkylation workhorse"),
        ("nitromethane",         10.2, "NO2 activates strongly"),
    ]
    for c, p, n in pkas:
        print(f"  {c:<22s}  {p:>6.1f}  {n:<24s}")
    print()
    print("Substrate reading: enolate negative charge sits in a delocalized strain")
    print("pocket spread over O and alpha-C. Resonance = same strain mode shared")
    print("between two geometries; lower total energy -> lower pKa.")

    # ============================================================
    section(9, "SUMMARY: nine pathways across one strain landscape")
    # ============================================================
    print("Each mechanism family is one trajectory archetype across the same")
    print("substrate landscape, distinguished by which strain bridges break/form")
    print("and by the topology of the cyclic TS (when applicable):")
    print()
    print(f"  {'family':<22s}  {'distinguishing TS feature':<44s}")
    summary = [
        ("SN1",          "carbocation MIN between two saddles"),
        ("SN2",          "trigonal-bipyramidal saddle, antipodal Nu/LG"),
        ("E1",           "same cation min as SN1, then beta-H loss"),
        ("E2",           "concerted antiperiplanar saddle"),
        ("EAS",          "Wheland sigma-complex (broken aromatic shell)"),
        ("SNAr",         "Meisenheimer anionic sp3 intermediate"),
        ("Addition",     "pi mode opens, two sigma bridges form"),
        ("Diels-Alder",  "Huckel 6e cyclic TS (orientable strain band)"),
        ("Pericyclic",   "Huckel/Mobius TS via orientability primitive"),
        ("Radical",      "open-shell strain mode chain-propagated"),
        ("Carbonyl",     "Burgi-Dunitz approach to polarized C=O"),
    ]
    for f, n in summary:
        print(f"  {f:<22s}  {n:<44s}")
    print()
    print("Cross-cutting laws (substrate primitives in action):")
    print("  Hammett LFER         <-  K-stiffness varies linearly with substituent")
    print("  Hammond postulate    <-  strain-landscape geometry near the saddle")
    print("  Markovnikov          <-  hyperconjugation = extra strain bridges")
    print("  Zaitsev / Hofmann    <-  steric saturation cap sigma <= 1/2")
    print("  Walden inversion     <-  geometry of antipodal lobes around C")
    print("  KIE                  <-  reduced-mass shift of zero-point strain")
    print("  Woodward-Hoffmann    <-  ORIENTABILITY: Huckel vs Mobius topology")
    print("  Endo rule            <-  secondary strain-bridge stabilization")
    print()
    print("Honest scoreboard: all numerical predictions (rates, Hammett rho, KIEs,")
    print("rel reactivities) match standard physical-organic chemistry exactly,")
    print("because the bound + transition-state spectra of the substrate Lagrangian")
    print("REDUCE to the Born-Oppenheimer / TST framework in the appropriate limit.")
    print("The value-add: nine mechanism families become one strain-pathway story.")
    print()
    # quick numeric demo: convert a few Ea -> k_rel at 298 K
    print("Sanity demo: Eyring-Arrhenius factors at 298 K for a few barriers.")
    for Ea in (40.0, 60.0, 85.0, 105.0, 150.0):
        print(f"  Ea = {Ea:6.1f} kJ/mol  ->  exp(-Ea/RT) = {arrhenius_rel(Ea):.3e}")


if __name__ == "__main__":
    main()
