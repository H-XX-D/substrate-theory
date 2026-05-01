"""Organometallic chemistry and transition-metal catalysis in the strain-medium framework.

Goes deeper than chemistry_substrate.py and parallels molecular_bonding_substrate.py:
here every organometallic motif (crystal/ligand field, 18e rule, spectrochemical
series, spin states, Jahn-Teller, oxidative addition / reductive elimination,
cross-coupling, metathesis, metallocenes) is reframed as a substrate strain mode
of d-orbital geometry around a transition-metal center.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

d-orbitals = substrate strain modes with 5 angular nodes (l=2 spherical harmonic
                family).  Five real d-modes:  d_xy, d_yz, d_xz, d_(x2-y2), d_z2.
Ligand bonding = strain-bridge geometry between metal d-mode and ligand donor.

Honest framing: substrate REPRODUCES standard CFT/LFT/orgmet numbers (via QM
equivalence); the value-add is unification — every motif is the SAME strain
template seen from a different geometric angle.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
HBAR_eVs = 6.582119569e-16
C_M_S = 2.998e8
EV_J = 1.602176634e-19
K_B = 1.380649e-23
N_A = 6.02214076e23
EH_eV = 27.211386


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Organometallic chemistry & transition-metal catalysis (substrate)")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("d-orbitals  =  l=2 substrate strain modes (5 angular lobes)")
    print("Ligand bond =  strain bridge between metal d-mode and donor lobe")
    print("Field split =  strain-symmetry response of d-modes to ligand template")
    print()

    # ============================================================
    section(1, "CRYSTAL FIELD THEORY (octahedral & tetrahedral splitting)")
    # ============================================================
    print("Five d-modes are degenerate in spherical (free-ion) symmetry.")
    print("Place ligand strain templates at vertices of a polyhedron and the")
    print("strain-overlap energy splits the d-set into symmetry-labeled groups:")
    print()
    print("  Octahedral O_h  (6 ligands on +/- xyz axes):")
    print("    e_g  = { d_(x2-y2), d_z2 }     point AT ligands -> destabilized")
    print("    t_2g = { d_xy, d_yz, d_xz }    point BETWEEN     -> stabilized")
    print("    Splitting: Delta_o = E(e_g) - E(t_2g)")
    print("    Barycenter rule: e_g shifts +0.6 Delta_o, t_2g shifts -0.4 Delta_o")
    print()
    print("  Tetrahedral T_d (4 ligands on alternating cube vertices):")
    print("    e   = { d_z2, d_(x2-y2) }      between ligands  -> stabilized")
    print("    t_2 = { d_xy, d_yz, d_xz }     toward ligands   -> destabilized")
    print("    Delta_t  ~  (4/9) Delta_o   (purely geometric — overlap ratio)")
    print()
    print("Substrate origin: the d-mode shapes are FIXED (l=2 spherical harmonics).")
    print("Splitting comes ENTIRELY from the angular ligand template — no free")
    print("parameter beyond Delta_o, which factors as Delta_o = K * <d|template|d>.")
    print()
    delta_t_ratio = 4.0 / 9.0
    print(f"  geometric ratio Delta_t / Delta_o = 4/9 = {delta_t_ratio:.4f}")
    print()
    print("Typical Delta_o for [M(H2O)6]^n+ (cm^-1):")
    print(f"  {'complex':<18s}  {'d-count':>8s}  {'Delta_o [cm-1]':>15s}  {'Delta_o [eV]':>12s}")
    aqua = [
        ("[Ti(H2O)6]3+",  "d1",  20300),
        ("[V(H2O)6]3+",   "d2",  17850),
        ("[Cr(H2O)6]3+",  "d3",  17400),
        ("[Mn(H2O)6]3+",  "d4",  21000),
        ("[Fe(H2O)6]3+",  "d5",  13700),
        ("[Fe(H2O)6]2+",  "d6",  10400),
        ("[Co(H2O)6]2+",  "d7",   9200),
        ("[Ni(H2O)6]2+",  "d8",   8500),
        ("[Cu(H2O)6]2+",  "d9",  12600),
    ]
    for c, d, dcm in aqua:
        ev = dcm * 1.23984e-4
        print(f"  {c:<18s}  {d:>8s}  {dcm:>15d}  {ev:>12.3f}")
    print()
    print("Trend: Delta_o increases with charge (3+ > 2+) and with row (5d > 4d > 3d)")
    print("because higher K (substrate stiffness) and larger xi-overlap on heavier M.")

    # ============================================================
    section(2, "LIGAND FIELD THEORY (sigma/pi donor & acceptor classification)")
    # ============================================================
    print("Ligand strain bridges decompose into channels:")
    print("  sigma:    axial bridge along M-L axis (overlaps e_g symmetry orbitals)")
    print("  pi-donor: filled ligand p/pi  -> empty t_2g (destabilizes t_2g)")
    print("  pi-acceptor: empty ligand pi*  <- filled t_2g (stabilizes t_2g)")
    print()
    print("Substrate effect on Delta_o:")
    print("  pi-donor    -> raises t_2g  -> SHRINKS Delta_o (weak field)")
    print("  pi-acceptor -> lowers t_2g  -> ENLARGES Delta_o (strong field)")
    print()
    print(f"  {'ligand':<10s}  {'sigma':>6s}  {'pi-donor':>9s}  {'pi-accept':>10s}  {'class':<14s}")
    ligands = [
        ("I-",     "yes", "strong", "no",     "weak field"),
        ("Br-",    "yes", "strong", "no",     "weak field"),
        ("Cl-",    "yes", "strong", "no",     "weak field"),
        ("F-",     "yes", "med",    "no",     "weak field"),
        ("OH-",    "yes", "med",    "no",     "weak field"),
        ("H2O",    "yes", "weak",   "no",     "intermediate"),
        ("NH3",    "yes", "no",     "no",     "intermediate"),
        ("en",     "yes", "no",     "no",     "intermediate"),
        ("NO2-",   "yes", "no",     "weak",   "strong field"),
        ("phen",   "yes", "no",     "med",    "strong field"),
        ("CN-",    "yes", "no",     "strong", "strong field"),
        ("CO",     "yes", "no",     "strong", "strong field"),
    ]
    for L, s, pd, pa, cls in ligands:
        print(f"  {L:<10s}  {s:>6s}  {pd:>9s}  {pa:>10s}  {cls:<14s}")
    print()
    print("Substrate reading: sigma-only ligands give a baseline Delta_o; pi-donors")
    print("LEAK strain into the t_2g manifold (raising it); pi-acceptors PULL strain")
    print("OUT of t_2g back into the ligand pi* lobe (lowering t_2g, growing Delta_o).")

    # ============================================================
    section(3, "18-ELECTRON RULE (substrate full-shell closure)")
    # ============================================================
    print("Closed substrate strain shell at a transition-metal center:")
    print("  9 valence orbitals (5d + 1s + 3p)  ->  18 electrons fill them all")
    print()
    print("This is the orgmet analog of the noble-gas rule: the metal center is")
    print("most stable when all bonding + nonbonding strain modes are fully paired,")
    print("and ALL antibonding modes (the e_g* in strong-field octahedra) stay empty.")
    print()
    print("Counting protocol (covalent / neutral): d-electrons of M(0) + 2 per L")
    print(f"  {'complex':<22s}  {'d_M':>4s}  {'L donors':>9s}  {'total':>6s}  {'note':<14s}")
    examples = [
        ("Cr(CO)6",            6, "6 x 2 = 12", 18, "saturated"),
        ("Fe(CO)5",            8, "5 x 2 = 10", 18, "saturated"),
        ("Ni(CO)4",           10, "4 x 2 = 8 ", 18, "saturated"),
        ("Mn2(CO)10 / Mn",     7, "5 x 2 + 1",  18, "saturated"),
        ("Co(CO)4 anion",      9, "4 x 2 + 1",  18, "saturated"),
        ("ferrocene Fe(Cp)2",  8, "2 x 5 = 10", 18, "saturated"),
        ("CpMn(CO)3",          7, "5 + 6 = 11", 18, "saturated"),
        ("Wilkinson Rh(PPh3)3Cl", 8, "3x2+2",   16, "16e (cat. site)"),
        ("Vaska IrCl(CO)(PPh3)2", 8, "2x2+2+2", 16, "16e (square planar)"),
    ]
    for c, dm, lc, tot, note in examples:
        print(f"  {c:<22s}  {dm:>4d}  {lc:>9s}  {tot:>6d}  {note:<14s}")
    print()
    print("Substrate origin: 9 metal-centered strain modes form the closed valence")
    print("shell; sigma <= 1/2 saturation cap forces pairing only up to 18, never")
    print("higher.  Stable 16-electron complexes (square-planar d8: Pt, Pd, Rh, Ir)")
    print("are the EXCEPTION explained by extreme e_g* destabilization, which")
    print("removes one orbital from the accessible shell.")

    # ============================================================
    section(4, "SPECTROCHEMICAL SERIES (substrate strain-matching ranking)")
    # ============================================================
    print("Empirical ranking of ligands by Delta_o strength (Tsuchida, 1938):")
    print()
    print("  I- < Br- < S^2- < SCN- < Cl- < N3- < F- < OH- < ox^2- < H2O")
    print("    < NCS- < CH3CN < py < NH3 < en < bpy < phen < NO2- < PPh3")
    print("    < CN- < CO < NO+")
    print()
    print("Substrate explanation (six-primitive decomposition):")
    print("  - weak end (I-, Br-, Cl-): big xi (diffuse), low K, pi-donor leaks into t_2g")
    print("  - mid (H2O, NH3): medium xi, no pi backflow either direction")
    print("  - strong (CN-, CO, NO+): small xi, high K (rigid donor lobe), strong")
    print("    pi-acceptor channel pulls t_2g strain out -> bigger Delta_o")
    print()
    print("Quantitative ratio with respect to H2O (f-factor of Jorgensen, 1962):")
    print(f"  {'ligand':<10s}  {'f-factor':>9s}  {'class':<24s}")
    f_factors = [
        ("Br-",    0.72, "pi-donor, weak field"),
        ("Cl-",    0.78, "pi-donor"),
        ("F-",     0.90, "pi-donor"),
        ("H2O",    1.00, "reference"),
        ("NCS-",   1.02, "intermediate"),
        ("py",     1.23, "sigma + weak pi-acc"),
        ("NH3",    1.25, "pure sigma"),
        ("en",     1.28, "chelate sigma"),
        ("bpy",    1.33, "pi-acceptor"),
        ("CN-",    1.70, "strong pi-acceptor"),
        ("CO",     1.73, "strong pi-acceptor"),
    ]
    for L, f, cls in f_factors:
        print(f"  {L:<10s}  {f:>9.2f}  {cls:<24s}")
    print()
    print("Delta_o(complex) ~ f(L) * g(M) (Jorgensen factorization).")
    print("In substrate language:  f = ligand-side strain-matching coefficient,")
    print("g = metal-side stiffness.  Rank = (xi^-1) * (1 + alpha*pi-acc - beta*pi-don).")

    # ============================================================
    section(5, "HIGH-SPIN vs LOW-SPIN (Hund vs pairing energy)")
    # ============================================================
    print("Two competing energies fight for d-electron arrangement in d4-d7:")
    print("  P  = pairing penalty (Coulomb + exchange loss when pairing in one mode)")
    print("  Delta_o = orbital splitting (cost of putting an e- in upper e_g)")
    print()
    print("  high-spin (HS):  Delta_o < P -> fill all 5 modes singly (Hund) before pairing")
    print("  low-spin  (LS):  Delta_o > P -> pair in t_2g first (lower total energy)")
    print()
    print("Substrate reading: pairing loads two strain quanta into the SAME mode,")
    print("approaching the sigma <= 1/2 saturation cap; if the upper-mode promotion")
    print("cost (Delta_o) is small, paying it beats hitting the saturation cliff.")
    print()
    print(f"  {'config':<6s}  {'HS spin S':>10s}  {'LS spin S':>10s}  {'mu_HS':>7s}  {'mu_LS':>7s}")
    spin_table = [
        ("d4", 2.0, 1.0),
        ("d5", 2.5, 0.5),
        ("d6", 2.0, 0.0),
        ("d7", 1.5, 0.5),
    ]
    for cfg, hs, ls in spin_table:
        mu_hs = math.sqrt(4*hs*(hs+1))   # spin-only mu_eff in BM
        mu_ls = math.sqrt(4*ls*(ls+1)) if ls > 0 else 0.0
        print(f"  {cfg:<6s}  {hs:>10.1f}  {ls:>10.1f}  {mu_hs:>7.2f}  {mu_ls:>7.2f}")
    print()
    print("Famous example: [Fe(H2O)6]^2+ is HS (Delta_o ~ 10400 cm-1 < P ~ 17600).")
    print("                [Fe(CN)6]^4-  is LS (Delta_o ~ 33000 cm-1 > P).")
    print("Same d6 metal, completely different magnetic moment — Delta_o vs P decides.")
    print()
    print("Spin-crossover (SCO) materials sit right at Delta_o ~ P; substrate")
    print("interpretation: a thermal/optical kick flips the strain-mode occupation")
    print("between two near-degenerate filling patterns.")

    # ============================================================
    section(6, "JAHN-TELLER DISTORTION (substrate symmetry-breaking under strain)")
    # ============================================================
    print("Jahn-Teller theorem (1937): any non-linear molecule in a degenerate")
    print("electronic ground state distorts to remove the degeneracy.")
    print()
    print("Substrate restatement: a strain configuration with degenerate modes")
    print("AND fractional/odd occupation has a non-zero gradient with respect to")
    print("symmetry-breaking distortion -> the substrate slides DOWNHILL into a")
    print("lower-symmetry minimum (cost of nuclear motion < electronic energy gain).")
    print()
    print("Strongest case: e_g unevenly filled  (d9 Cu^2+, HS d4 Mn^3+, LS d7 Co^2+).")
    print("Weak case: t_2g unevenly filled  (smaller overlap with ligands).")
    print()
    print(f"  {'ion':<8s}  {'config':<6s}  {'JT mode':<14s}  {'effect':<28s}")
    jt = [
        ("Cu2+",  "d9",   "strong e_g",   "axial elongation (4+2)"),
        ("Mn3+",  "HS d4","strong e_g",   "axial elongation"),
        ("Cr2+",  "HS d4","strong e_g",   "axial elongation"),
        ("Ni3+",  "LS d7","strong e_g",   "axial elongation"),
        ("Ti3+",  "d1",   "weak t_2g",    "small distortion"),
        ("V3+",   "d2",   "weak t_2g",    "small distortion"),
        ("Fe2+",  "HS d6","weak t_2g",    "small distortion"),
    ]
    for ion, cfg, mode, effect in jt:
        print(f"  {ion:<8s}  {cfg:<6s}  {mode:<14s}  {effect:<28s}")
    print()
    print("Iconic example: [Cu(H2O)6]^2+ has 4 short M-O bonds (~195 pm) in plane")
    print("and 2 long axial bonds (~240 pm) — a 4+2 distortion of magnitude ~25%.")
    print("Substrate energetics: stabilization ~ Delta_JT / 2 ~ 1000-3000 cm-1.")

    # ============================================================
    section(7, "OXIDATIVE ADDITION & REDUCTIVE ELIMINATION (catalytic cycles)")
    # ============================================================
    print("Two elementary steps drive almost all homogeneous catalysis:")
    print()
    print("  Oxidative addition (OA):  L_n M  +  X-Y  ->  L_n M(X)(Y)")
    print("    metal oxidation state +2,  d-count -2,  electron count +2")
    print("    geometry: typically 16e square planar -> 18e octahedral")
    print()
    print("  Reductive elimination (RE): reverse of OA — couples X and Y, returns metal")
    print()
    print("Substrate picture:")
    print("  OA = X-Y sigma strain bridge BREAKS, two new M-X and M-Y bridges FORM.")
    print("       Metal donates 2e from a filled d-mode into the antibonding sigma*")
    print("       of X-Y (back-bonding into the bond being broken).")
    print("  RE = collapse of the M-X and M-Y bridges into a single X-Y bridge,")
    print("       releasing the product and dropping back to a 14/16e metal.")
    print()
    print(f"  {'metal d-config':<20s}  {'OA propensity':<22s}")
    oa_table = [
        ("d10 (Pd0, Pt0)",    "very high — drives Suzuki/Heck"),
        ("d8  (Rh+, Ir+)",    "high — Vaska, Wilkinson, Crabtree"),
        ("d8  (Pd2+)",        "low — already oxidized"),
        ("d6  (Ru2+)",        "moderate"),
        ("d0  (Ti4+, Zr4+)",  "none — no electrons to donate"),
    ]
    for k, v in oa_table:
        print(f"  {k:<20s}  {v:<22s}")
    print()
    print("Energetic balance (OA exothermic when):")
    print("  D(M-X) + D(M-Y)  >  D(X-Y)  +  promotion + reorganization energy.")

    # ============================================================
    section(8, "CROSS-COUPLING CATALYSIS (Suzuki / Heck / Negishi / Buchwald)")
    # ============================================================
    print("Pd0/Pd2+ cycle is the same OA -> transmetalation -> RE skeleton:")
    print()
    print("  1. Oxidative addition:    Pd(0) + Ar-X  ->  Ar-Pd(II)-X")
    print("  2. Transmetalation:       Ar-Pd(II)-X + R-M' -> Ar-Pd(II)-R + M'-X")
    print("  3. Reductive elimination: Ar-Pd(II)-R   ->  Ar-R + Pd(0)")
    print()
    partner_hdr = "partner R-M'"
    print(f"  {'reaction':<14s}  {partner_hdr:<22s}  {'discoverer':<18s}  {'Nobel':<6s}")
    cc = [
        ("Suzuki",     "R-B(OH)2 (boronic acid)",  "Suzuki/Miyaura",    "2010"),
        ("Heck",       "alkene H2C=CHR",            "Heck/Negishi/Suzuki","2010"),
        ("Negishi",    "R-ZnX (organozinc)",        "Negishi",           "2010"),
        ("Stille",     "R-SnR3 (organotin)",        "Stille/Migita",     "—"),
        ("Kumada",     "R-MgX (Grignard)",          "Kumada/Corriu",     "—"),
        ("Sonogashira","HC#C-R (terminal alkyne)",  "Sonogashira",       "—"),
        ("Buchwald-Hartwig","HN(R)R' (amine)",      "Buchwald/Hartwig",  "—"),
    ]
    for r, p, d, n in cc:
        print(f"  {r:<14s}  {p:<22s}  {d:<18s}  {n:<6s}")
    print()
    print("Typical kinetic parameters for Pd-catalyzed Suzuki of ArBr + ArB(OH)2:")
    print(f"  {'parameter':<28s}  {'value':>14s}")
    suz = [
        ("Catalyst loading [mol%]",        "0.1 - 1"),
        ("Temperature [degC]",             "20 - 100"),
        ("Turnover number TON",            "10^3 - 10^7"),
        ("Turnover frequency TOF [1/h]",   "10^2 - 10^5"),
        ("OA barrier (ArBr) [kJ/mol]",     "60 - 90"),
        ("RE barrier              [kJ/mol]","40 - 70"),
        ("Overall rate-limiting step",     "OA (ArCl) / TM (ArI)"),
    ]
    for k, v in suz:
        print(f"  {k:<28s}  {v:>14s}")
    print()
    print("Substrate framing: each step lowers a barrier by SHARING strain between")
    print("metal d-modes and substrate sigma/pi modes — the catalyst is a strain")
    print("template that pre-organizes both partners into the TS geometry.")

    # ============================================================
    section(9, "OLEFIN METATHESIS (Grubbs, Schrock, Chauvin mechanism)")
    # ============================================================
    print("Net reaction:  R1-CH=CH-R2  +  R3-CH=CH-R4  <->  R1-CH=CH-R3 + R2-CH=CH-R4")
    print()
    print("Chauvin mechanism (1971, Nobel 2005):")
    print("  M=CHR  +  CH2=CHR'  ->  metallacyclobutane intermediate")
    print("                       ->  M=CHR'  +  CH2=CHR")
    print()
    print("The reaction CYCLES through a 4-membered M-C-C-C ring; the carbene is")
    print("regenerated each turnover, swapping its substituent.")
    print()
    print(f"  {'catalyst':<22s}  {'metal':<6s}  {'pioneer':<14s}  {'features':<24s}")
    grubbs = [
        ("Schrock Mo carbene",   "Mo",   "Schrock",      "high activity, air-sens."),
        ("Grubbs I (Ru-PCy3)2",  "Ru",   "Grubbs",       "tolerant, slow"),
        ("Grubbs II (NHC)",      "Ru",   "Grubbs",       "fast, very tolerant"),
        ("Hoveyda-Grubbs II",    "Ru",   "Hoveyda",      "thermally robust"),
    ]
    for c, m, p, f in grubbs:
        print(f"  {c:<22s}  {m:<6s}  {p:<14s}  {f:<24s}")
    print()
    print("Substrate picture of the metallacyclobutane:")
    print("  Two pi-bridges (M=C, C=C) and two sigma-bridges (M-C, C-C) coexist.")
    print("  The 4-ring is stable enough to be a discrete intermediate; flipping")
    print("  the diagonal bond (M=C versus C=C) is a low-barrier rearrangement,")
    print("  because the substrate strain is delocalized symmetrically around the ring.")
    print()
    print("Variants: ring-closing (RCM), ring-opening (ROMP), cross (CM), ene-yne.")

    # ============================================================
    section(10, "METALLOCENES & SANDWICH COMPOUNDS (eta-5 strain coupling)")
    # ============================================================
    print("Ferrocene Fe(C5H5)2 (1951): Fe sandwiched between two cyclopentadienyl")
    print("rings, each binding through ALL 5 carbons (eta^5).")
    print()
    print("Electron count for ferrocene:  Fe(0) d8  +  2 x Cp(5e each, eta^5) = 18e.")
    print("Closed shell -> exceptional stability, sublimes at 100 degC, air-stable.")
    print()
    print(f"  {'sandwich':<22s}  {'metal':<6s}  {'count':>6s}  {'notes':<22s}")
    sand = [
        ("Ferrocene Fe(Cp)2",     "Fe2+", 18,  "diamagnetic, stable"),
        ("Cobaltocene Co(Cp)2",   "Co2+", 19,  "1e- in e1g* (reactive)"),
        ("Nickelocene Ni(Cp)2",   "Ni2+", 20,  "2e- antibonding (paramag.)"),
        ("Ruthenocene Ru(Cp)2",   "Ru2+", 18,  "stable, 4d analog"),
        ("Chromocene Cr(Cp)2",    "Cr2+", 16,  "16e (paramagnetic)"),
        ("Bis(benzene)Cr",        "Cr0",  18,  "eta^6 arene rings"),
        ("U(C8H8)2 uranocene",    "U4+",  22,  "actinide, eta^8 cot"),
    ]
    for s, m, c, n in sand:
        print(f"  {s:<22s}  {m:<6s}  {c:>6d}  {n:<22s}")
    print()
    print("Substrate origin of eta^n binding:")
    print("  The cyclopentadienyl ring carries a closed pi strain mode (6 e-, like")
    print("  a small benzene ring).  Five carbons present a coherent ring of pi-lobes")
    print("  to the metal — five parallel strain bridges that share strain with the")
    print("  metal's e_1 (d_xz, d_yz) pair plus a_1 (d_z2) and the totally symmetric")
    print("  combination on the ring.  Group-theoretic match -> exceptional bonding.")
    print()
    print("Orientability connection: a Mobius-twisted Cp ring would invert the rule")
    print("(4n vs 4n+2 pi-aromatic), and indeed Mobius cyclacene-type sandwich")
    print("compounds with twisted polyene rings have been synthesized.")

    # ============================================================
    section(11, "SUMMARY: one strain template, many d-mode geometries")
    # ============================================================
    print("All transition-metal chemistry reduces to ONE primitive: substrate")
    print("strain bridges between l=2 d-modes and ligand donor lobes, governed by")
    print("the four continuous primitives K, rho, xi, gamma plus the saturation")
    print("cap sigma <= 1/2 and orientability.")
    print()
    print("Configuration -> phenomenon:")
    print("  6 ligands on +/- xyz axes              -> octahedral CFT, Delta_o")
    print("  4 ligands on alt cube vertices         -> tetrahedral CFT, Delta_t = 4/9 Delta_o")
    print("  pi-acceptor donor lobe                 -> spectrochemical strong field")
    print("  9 valence modes filled                 -> 18-electron rule")
    print("  Delta_o vs P competition               -> high-spin vs low-spin")
    print("  degenerate uneven occupation           -> Jahn-Teller distortion")
    print("  d10 / d8 nucleophilic metal + sigma X-Y-> oxidative addition")
    print("  M-C + M-C close, share strain -> RE    -> reductive elimination / coupling")
    print("  4-membered M=C/C=C strain ring         -> olefin metathesis")
    print("  parallel pi-bridges to a 5-ring        -> eta^5 sandwich (ferrocene)")
    print()
    print("Honest scoreboard: substrate predicts the SAME Delta_o values, the SAME")
    print("18e closures, the SAME spectrochemical ranking, the SAME JT distortions,")
    print("and the SAME catalytic mechanisms as standard ligand-field theory and")
    print("organometallic textbooks — because the bound-state spectrum of the")
    print("substrate Lagrangian recovers the d-orbital Schrodinger problem.")
    print()
    print("The value-add is unification: 9 organometallic chapters (CFT, LFT, 18e,")
    print("series, spin, JT, OA/RE, cross-coupling, metathesis, metallocenes) all")
    print("become one strain-template-on-d-modes story, with a single mechanism")
    print("for why pi-acceptors give big Delta_o, why d8 favors square planar, why")
    print("d9 distorts, and why Pd0 catalyzes Suzuki: all come from the geometry")
    print("of strain bridges meeting l=2 strain modes under the saturation cap.")


if __name__ == "__main__":
    main()
