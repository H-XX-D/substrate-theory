"""Coordination chemistry and Werner complexes through the strain-medium framework.

Distinct from organometallic chemistry (those scripts focus on M-C bonds);
this one stays on PURE INORGANIC coordination: classical Werner complexes,
chelates, lanthanides/actinides, and bioinorganic centers (heme, B12, FeMoco).

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Coordination bond  =  substrate strain bridge between metal d/f orbital lobes
and ligand donor-atom lone-pair lobes (dative / Lewis acid-base bridge).

Substrate framing of headline phenomena:
  - chelate effect       = entropy from constrained substrate strain bridges
  - lanthanide contraction = substrate-strain shielding inefficiency in 4f
  - complex color        = d-d transition substrate-mode energy gap (10 Dq)
  - high/low spin        = sigma<=1/2 cap balanced against pairing strain
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
A0_M = 5.29177210903e-11
EH_eV = 27.211386
MU_B = 9.2740100783e-24   # Bohr magneton, J/T
ANGSTROM = 1.0e-10


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Coordination chemistry and Werner complexes in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Coordination bond  =  dative strain bridge")
    print("                     metal d/f lobe  <-->  ligand lone-pair lobe")
    print()
    print("Both electrons of the bond originate on the LIGAND donor atom; the")
    print("metal accepts strain-density into a vacant lobe.  Multi-tooth ligands")
    print("(chelates) form CLOSED-LOOP strain circuits around the metal.")
    print()

    # ============================================================
    section(1, "WERNER'S COORDINATION THEORY (1893)  --  primary vs secondary valence")
    # ============================================================
    print("Alfred Werner's break with classical valence theory:")
    print("  - PRIMARY valence  = oxidation state (charge), satisfied by counterions")
    print("  - SECONDARY valence = coordination number CN, satisfied by ligands")
    print("                       arranged in a fixed geometric polyhedron")
    print()
    print("Substrate reading:")
    print("  primary   = total saturation deficit at the metal (charge-strain)")
    print("  secondary = number of substrate strain bridges metal can host (CN)")
    print()
    print("Werner's diagnostic series:  CoCl3 . n NH3,  n = 6, 5, 4, 3")
    print(f"  {'compound':<22s}  {'AgNO3 ppt':>10s}  {'free Cl-':>9s}  {'inner sphere':<24s}")
    werner = [
        ("[Co(NH3)6]Cl3",      "3 Cl-",  "3", "6 NH3"),
        ("[Co(NH3)5Cl]Cl2",    "2 Cl-",  "2", "5 NH3 + 1 Cl-"),
        ("[Co(NH3)4Cl2]Cl",    "1 Cl-",  "1", "4 NH3 + 2 Cl- (cis/trans)"),
        ("[Co(NH3)3Cl3]",      "0 Cl-",  "0", "3 NH3 + 3 Cl- (fac/mer)"),
    ]
    for c, ag, fr, inn in werner:
        print(f"  {c:<22s}  {ag:>10s}  {fr:>9s}  {inn:<24s}")
    print()
    print("All four have CN=6 even though primary valence is fixed at 3+.")
    print("Substrate: 6 strain-bridge slots are a GEOMETRIC property of the d-shell")
    print("envelope (octahedral lobe arrangement), independent of overall charge.")

    # ============================================================
    section(2, "COORDINATION NUMBERS 2-9  AND  GEOMETRIES")
    # ============================================================
    print("Each CN selects a polyhedron that maximizes the angular separation")
    print("of substrate strain bridges around the metal (min-strain criterion).")
    print()
    print(f"  {'CN':>3s}  {'geometry':<24s}  {'min angle':>10s}  {'examples':<28s}")
    geoms = [
        (2, "linear",                     180.0, "[Ag(NH3)2]+, [CuCl2]-"),
        (3, "trigonal planar",            120.0, "[HgI3]-, [Cu(CN)3]2-"),
        (4, "tetrahedral",                109.47, "[Zn(NH3)4]2+, [FeCl4]-"),
        (4, "square planar",               90.0, "[Pt(NH3)4]2+, [Ni(CN)4]2-"),
        (5, "trigonal bipyramidal",        90.0, "[Fe(CO)5], [CuCl5]3-"),
        (5, "square pyramidal",            90.0, "[VO(acac)2], [Ni(CN)5]3-"),
        (6, "octahedral",                  90.0, "[Co(NH3)6]3+, [Fe(CN)6]4-"),
        (7, "pentagonal bipyramidal",      72.0, "[V(CN)7]4-, [UO2F5]3-"),
        (7, "capped trigonal prism",       70.5, "[NbF7]2-, [TaF7]2-"),
        (8, "square antiprism",            70.5, "[Mo(CN)8]4-, [Zr(acac)4]"),
        (8, "dodecahedron",                73.7, "[Mo(CN)8]4- (alt), [Zr(ox)4]4-"),
        (9, "tricapped trig prism",        69.5, "[Nd(H2O)9]3+, [ReH9]2-"),
    ]
    for cn, g, a, ex in geoms:
        print(f"  {cn:>3d}  {g:<24s}  {a:>10.2f}  {ex:<28s}")
    print()
    print("Tetrahedral vs square planar at CN=4:")
    print("  Tetrahedral wins for d0, d5 high-spin, d10 (no preference).")
    print("  Square planar wins for d8 (Pt2+, Pd2+, Ni2+ with strong-field L)")
    print("  because the empty d_{x2-y2} lobe avoids axial strain saturation.")
    print()
    print("Substrate angles via min-strain on the unit sphere:")
    print(f"  tetrahedral:  arccos(-1/3)        = {math.degrees(math.acos(-1/3)):.4f} deg")
    print(f"  octahedral:   90, 180             = exact")
    print(f"  square antiprism (CN=8) twist     = 45 deg between squares")

    # ============================================================
    section(3, "ISOMERISM IN COORDINATION COMPOUNDS")
    # ============================================================
    print("Several distinct isomerism types arise from the same substrate-bridge")
    print("topology but different bridge identifications:")
    print()
    print("(a) GEOMETRIC isomerism  (cis / trans, fac / mer)")
    print("    Octahedral [MA4B2]:  cis (90 deg apart) or trans (180 deg apart).")
    print("    Octahedral [MA3B3]:  fac (one face) or mer (one meridian).")
    print("    Square planar [MA2B2]:  cis or trans (Pt cisplatin = active drug).")
    print()
    print("(b) OPTICAL isomerism  (Delta / Lambda)")
    print("    [M(L-L)3] tris-chelate, e.g. [Co(en)3]3+, lacks mirror plane.")
    print("    Two enantiomers labeled Delta (right-helix) and Lambda (left).")
    print("    Substrate: chirality of the closed strain-bridge circuit.")
    print()
    print("(c) IONIZATION isomerism")
    print("    [Co(NH3)5Br]SO4   vs   [Co(NH3)5SO4]Br")
    print("    Different ligand inside the inner coordination sphere.")
    print()
    print("(d) HYDRATE (solvate) isomerism")
    print("    [Cr(H2O)6]Cl3    violet")
    print("    [Cr(H2O)5Cl]Cl2 . H2O   blue-green")
    print("    [Cr(H2O)4Cl2]Cl . 2H2O  green")
    print()
    print("(e) LINKAGE isomerism")
    print("    Ambidentate ligand binds through two different atoms.")
    print(f"  {'ligand':<10s}  {'mode A':<14s}  {'mode B':<14s}  {'example':<22s}")
    link = [
        ("SCN-",   "M-SCN (S, soft)", "M-NCS (N, hard)", "[Co(NH3)5SCN]2+ vs NCS"),
        ("NO2-",   "M-NO2 (N, nitro)", "M-ONO (O, nitrito)", "[Co(NH3)5NO2]2+ pair"),
        ("CN-",    "M-CN (C, common)", "M-NC (N, isocyano)", "Prussian blue mixed"),
        ("CO",     "M-CO (C)",       "M-OC (rare)",     "Fe(CO)5"),
    ]
    for lg, a, b, ex in link:
        print(f"  {lg:<10s}  {a:<14s}  {b:<14s}  {ex:<22s}")
    print()
    print("HSAB pattern: hard metals (Cr3+, Co3+) prefer hard donor (N/O);")
    print("soft metals (Pt2+, Hg2+) prefer soft donor (S, P, Se).  Substrate:")
    print("hard = stiff, localized strain bridge; soft = polarizable diffuse one.")

    # ============================================================
    section(4, "CHELATE EFFECT AND MACROCYCLIC EFFECT  (substrate entropy)")
    # ============================================================
    print("CHELATE effect: a polydentate ligand binds more strongly than the")
    print("same number of monodentate equivalents.")
    print()
    print(f"  {'reaction':<48s}  {'log K':>7s}")
    chel = [
        ("[Ni(H2O)6]2+ + 6 NH3 -> [Ni(NH3)6]2+ + 6 H2O",    8.6),
        ("[Ni(H2O)6]2+ + 3 en  -> [Ni(en)3]2+   + 6 H2O",  18.3),
        ("[Ni(H2O)6]2+ + EDTA  -> [Ni(EDTA)]2-  + 6 H2O",  18.6),
    ]
    for r, k in chel:
        print(f"  {r:<48s}  {k:>7.1f}")
    print()
    print("Substrate entropy explanation (Delta S dominated):")
    print("  Releasing 6 H2O from 6 NH3 bind   -> Delta n = 0     (no entropy gain)")
    print("  Releasing 6 H2O from 3 en  bind   -> Delta n = +3    (entropy gain)")
    print("  Releasing 6 H2O from 1 EDTA bind  -> Delta n = +6    (entropy gain)")
    print()
    R = 8.314
    T = 298.15
    print(f"  Each freed H2O: ~ +R = {R:.2f} J/(mol K) translational entropy")
    for n_free in (0, 3, 6):
        dS = n_free * R
        dG = -T * dS
        print(f"   Delta n = {n_free}:  T Delta S ~ {T*dS/1000:.2f} kJ/mol  ->  Delta G shift {dG/1000:+.2f}")
    print()
    print("MACROCYCLIC effect: pre-organized rings (porphyrin, crown ether,")
    print("cryptand) bind even more strongly than open polydentates.")
    print("  log K(crown-6, K+) = 6.1   vs   log K(EDTA, K+) ~ 1.0")
    print()
    print("Substrate basis: macrocycle is a CLOSED strain-bridge circuit pre-built")
    print("with no rotational disorder cost.  The pre-formed circuit means the")
    print("metal slots into an already-saturated geometric template.")

    # ============================================================
    section(5, "EDTA AND ANALYTICAL APPLICATIONS")
    # ============================================================
    print("EDTA (ethylenediaminetetraacetic acid):")
    print("  H4Y, hexadentate (4 carboxylate-O + 2 amine-N donors).")
    print("  Forms 1:1 [MY](n-4) complex with virtually any di- or trivalent metal.")
    print()
    print("Conditional stability constants K' at pH 10 (for complexometric titration):")
    print(f"  {'metal':<6s}  {'log K(MY)':>10s}  {'pM color change':<24s}")
    edta = [
        ("Mg2+",  8.7,  "Eriochrome Black T"),
        ("Ca2+", 10.7,  "Eriochrome / Calmagite"),
        ("Mn2+", 13.9,  "Eriochrome Black T"),
        ("Fe3+", 25.1,  "Salicylic acid (pH 2)"),
        ("Cu2+", 18.8,  "Murexide"),
        ("Zn2+", 16.5,  "Eriochrome Black T"),
        ("Pb2+", 18.0,  "Xylenol orange"),
        ("Ni2+", 18.6,  "Murexide"),
    ]
    for m, k, ind in edta:
        print(f"  {m:<6s}  {k:>10.1f}  {ind:<24s}")
    print()
    print("Applications: water hardness (Ca/Mg titration), heavy-metal sequestration,")
    print("food preservation (Fe sequestration prevents oxidation), Pb chelation")
    print("therapy (CaNa2EDTA displaces Pb2+ from biological binding sites).")
    print()
    print("Substrate reading: EDTA wraps a 6-bridge strain cage around the metal,")
    print("competitive with any biological binding site of similar denticity.")

    # ============================================================
    section(6, "LANTHANIDES AND ACTINIDES  (4f / 5f orbitals)")
    # ============================================================
    print("4f and 5f orbitals are RADIALLY CONTRACTED inside the [Xe] / [Rn] core,")
    print("so f-electrons hardly participate in covalent bonding.  Coordination is")
    print("dominantly IONIC and STERIC (driven by ligand-ligand repulsion).")
    print()
    print("Typical lanthanide CN = 8, 9; actinide CN reaches 12 (UO2(NO3)3-).")
    print()
    print("LANTHANIDE CONTRACTION:  ionic radius shrinks across the row.")
    print(f"  {'ion':<6s}  {'r (CN=6) [pm]':>14s}  {'shells':<14s}")
    lan = [
        ("La3+",  103, "4f0"),
        ("Ce3+",  101, "4f1"),
        ("Nd3+",   98, "4f3"),
        ("Sm3+",   96, "4f5"),
        ("Eu3+",   95, "4f6"),
        ("Gd3+",   94, "4f7"),
        ("Tb3+",   92, "4f8"),
        ("Ho3+",   90, "4f10"),
        ("Yb3+",   87, "4f13"),
        ("Lu3+",   86, "4f14"),
    ]
    for ion, r, c in lan:
        print(f"  {ion:<6s}  {r:>14d}  {c:<14s}")
    print()
    print("Total contraction La->Lu: 17 pm over 14 elements (~1%/electron added).")
    print()
    print("Substrate explanation:")
    print("  Each added 4f electron screens nuclear charge POORLY because 4f is a")
    print("  radially compact strain-mode (high-ell, many nodes inside outer s/p).")
    print("  Net effective Z_eff felt by 5s/5p/6s rises -> outer envelope shrinks.")
    print("  This is a LOCAL substrate-shielding inefficiency — not a new effect.")
    print()
    print("Consequence: post-lanthanide row (Hf, Ta, W, Re...) has nearly identical")
    print("ionic radii to its 4d-row analog (Zr, Nb, Mo, Tc) -> hard to separate.")
    print()
    print("LUMINESCENCE: Eu3+ (red, 615 nm) and Tb3+ (green, 545 nm) display")
    print("sharp f-f emission lines because 4f-4f transitions are weakly coupled")
    print("to lattice vibrations (substrate strain bridges to ligands are weak).")
    print()
    f_emis = [
        ("Eu3+", "5D0 -> 7F2",  615, "red", "europium phosphors, anti-counterfeit"),
        ("Tb3+", "5D4 -> 7F5",  545, "green", "green CRT phosphors, MRI contrast"),
        ("Tm3+", "1G4 -> 3H6",  475, "blue",  "tri-color displays"),
        ("Er3+", "4I13/2 -> 4I15/2", 1530, "IR", "fiber-optic amplifiers"),
        ("Nd3+", "4F3/2 -> 4I11/2", 1064, "IR", "Nd:YAG laser"),
    ]
    print(f"  {'ion':<6s}  {'transition':<22s}  {'lambda [nm]':>11s}  {'color':<6s}  {'use':<32s}")
    for ion, tr, lam, col, use in f_emis:
        print(f"  {ion:<6s}  {tr:<22s}  {lam:>11d}  {col:<6s}  {use:<32s}")

    # ============================================================
    section(7, "IUPAC NOMENCLATURE OF COORDINATION COMPOUNDS")
    # ============================================================
    print("Rules (1990, updated 2005):")
    print("  1) Cation named first, then anion.")
    print("  2) Within complex: ligands alphabetical, then metal.")
    print("  3) Anionic ligands end -o:  chloro -> chlorido (2005), oxalato, cyanido.")
    print("  4) Neutral: water -> aqua, NH3 -> ammine, CO -> carbonyl, NO -> nitrosyl.")
    print("  5) Multiplicity: di-, tri-, tetra- for simple; bis-, tris-, tetrakis- for")
    print("     complex/already-prefixed ligands (e.g. bis(ethylenediamine)).")
    print("  6) Metal oxidation state in Roman numerals; -ate suffix if anion.")
    print()
    print(f"  {'formula':<32s}  {'name':<46s}")
    nom = [
        ("[Co(NH3)6]Cl3",         "hexaamminecobalt(III) chloride"),
        ("[Cr(H2O)6]Cl3",         "hexaaquachromium(III) chloride"),
        ("K3[Fe(CN)6]",           "potassium hexacyanidoferrate(III)"),
        ("[Pt(NH3)2Cl2]",         "diamminedichloridoplatinum(II)"),
        ("Na[Co(en)2Cl2]",        "sodium dichloridobis(ethylenediamine)cobaltate(III)"),
        ("[Cu(NH3)4]SO4",         "tetraamminecopper(II) sulfate"),
        ("[Fe(CO)5]",             "pentacarbonyliron(0)"),
        ("[Ni(dmg)2]",            "bis(dimethylglyoximato)nickel(II)"),
    ]
    for f, n in nom:
        print(f"  {f:<32s}  {n:<46s}")

    # ============================================================
    section(8, "COLOR & SPECTRA  (d-d, LMCT, MLCT, intervalence)")
    # ============================================================
    print("Crystal-field splitting 10 Dq in an octahedral complex:")
    print("  d-orbitals split into  t2g (lower)  and  eg (upper).")
    print("  Photon promoting an electron t2g -> eg has energy h nu = 10 Dq.")
    print()
    print("Spectrochemical series (10 Dq increases L to R):")
    print("  I- < Br- < S2- < SCN- < Cl- < NO3- < F- < OH- < ox2- < H2O")
    print("    < NCS- < CH3CN < py < NH3 < en < bipy < phen < NO2- < PPh3 < CN- < CO")
    print()
    print(f"  {'complex':<22s}  {'10 Dq [cm-1]':>13s}  {'lambda_max [nm]':>16s}  {'color':<14s}")
    colors = [
        ("[Ti(H2O)6]3+",   20300,  493, "violet"),
        ("[V(H2O)6]3+",    17800,  562, "blue-green"),
        ("[Cr(H2O)6]3+",   17400,  574, "violet"),
        ("[Cr(NH3)6]3+",   21500,  465, "yellow"),
        ("[Cr(CN)6]3-",    26600,  376, "yellow"),
        ("[Mn(H2O)6]2+",   21000,  476, "v. pale pink"),
        ("[Fe(H2O)6]2+",   10400,  962, "pale green"),
        ("[Fe(CN)6]4-",    33000,  303, "yellow"),
        ("[Co(H2O)6]2+",    9300, 1075, "pink"),
        ("[Co(NH3)6]3+",   22900,  437, "yellow-orange"),
        ("[Ni(H2O)6]2+",    8500, 1176, "green"),
        ("[Cu(H2O)6]2+",   12600,  794, "blue"),
    ]
    for c, dq, lam, col in colors:
        print(f"  {c:<22s}  {dq:>13d}  {lam:>16d}  {col:<14s}")
    print()
    print("Numerical conversion: lambda [nm] = 1e7 / wavenumber [cm-1]")
    for dq in (10000, 20000, 30000):
        lam = 1e7 / dq
        print(f"  10 Dq = {dq:5d} cm-1   ->   lambda = {lam:6.0f} nm")
    print()
    print("Other transition types:")
    print("  LMCT  ligand-to-metal CT     MnO4-  permanganate (intense purple)")
    print("                               CrO4 2-  yellow")
    print("  MLCT  metal-to-ligand CT     [Ru(bipy)3]2+  orange (pi* of bipy)")
    print("  IVCT  intervalence CT        Prussian blue [FeIII Fe(II)(CN)6]")
    print()
    print("Substrate reading: each transition pumps a strain quantum across the")
    print("metal-ligand bridge.  Bridge stiffness K (set by ligand field) sets nu.")

    # ============================================================
    section(9, "MAGNETISM OF COMPLEXES (high-spin / low-spin, mu_eff)")
    # ============================================================
    print("Spin-only formula:   mu_eff = sqrt( n (n + 2) )   in units of mu_B")
    print("where n = number of unpaired electrons.")
    print()
    print(f"  {'n':>3s}  {'mu_eff [mu_B]':>15s}  {'examples':<32s}")
    for n in range(0, 8):
        mu = math.sqrt(n * (n + 2))
        ex_map = {
            0: "d6 LS [Co(NH3)6]3+, [Fe(CN)6]4-",
            1: "d1 [Ti(H2O)6]3+ ; d5 LS [Fe(CN)6]3-",
            2: "d2 [V(H2O)6]3+ ; d8 [Ni(H2O)6]2+",
            3: "d3 [Cr(H2O)6]3+",
            4: "d4 HS [Cr(H2O)6]2+ ; d6 HS [Fe(H2O)6]2+",
            5: "d5 HS [Mn(H2O)6]2+, [Fe(H2O)6]3+",
            6: "(rare; super-octahedral or f-shells)",
            7: "f7 Gd3+",
        }
        print(f"  {n:>3d}  {mu:>15.3f}  {ex_map.get(n, ''):<32s}")
    print()
    print("High-spin vs low-spin (octahedral d4-d7):")
    print("  weak-field L (H2O, F-, Cl-)   ->  10 Dq < pairing energy P  ->  HIGH SPIN")
    print("  strong-field L (CN-, CO, NO2-) ->  10 Dq > P  ->  LOW SPIN")
    print()
    print("Substrate balance: pairing energy = saturation cost from sigma<=1/2")
    print("constraint forcing two strain modes into the same lobe.  10 Dq = strain-")
    print("bridge stiffness gap between t2g and eg lobes.  Whichever wins decides.")
    print()
    print("Curie law:  chi_M = N_A mu_eff^2 mu_B^2 / (3 k_B T)")
    print(f"At T = {T:.1f} K, n=5, mu_eff = {math.sqrt(5*7):.3f} mu_B:")
    mu = math.sqrt(5 * 7) * MU_B
    chi = N_A * mu**2 / (3 * K_B * T)
    print(f"  molar susceptibility chi_M ~ {chi:.3e} m^3/mol  (typical d5 HS)")

    # ============================================================
    section(10, "BIOINORGANIC METALLOCENTERS")
    # ============================================================
    print("Nature uses coordination chemistry as molecular machinery.  Each center")
    print("is a tuned substrate strain template selecting one reaction channel.")
    print()
    print(f"  {'center':<14s}  {'metal':<6s}  {'ligand cage':<28s}  {'role':<22s}")
    bio = [
        ("Heme b",        "Fe",  "porphyrin + His + O2/CO",   "O2 transport (Hb)"),
        ("Heme a",        "Fe",  "porphyrin + His + Cu (CcO)","O2 -> H2O reduction"),
        ("Chlorophyll a", "Mg",  "chlorin macrocycle",        "photosynthesis e- pump"),
        ("Cobalamin B12", "Co",  "corrin + Bzm + R (Me/CN)",  "methyl/radical transfer"),
        ("FeMoco",        "Fe7Mo", "S-bridged + homocitrate", "N2 -> 2 NH3 fixation"),
        ("Cytochrome c",  "Fe",  "heme + His + Met",          "electron transport chain"),
        ("Plastocyanin",  "Cu",  "2 His + Cys + Met (T1)",    "PSI -> PSII e- transfer"),
        ("Ferritin",      "Fe",  "oxo-hydroxo cluster",       "iron storage (~4500 Fe)"),
        ("Carbonic anh.", "Zn",  "3 His + OH-/H2O",           "CO2 + H2O -> HCO3-"),
        ("Carboxypept.",  "Zn",  "2 His + Glu + H2O",         "peptide hydrolysis"),
        ("Mn4CaO5 OEC",   "Mn4Ca", "carboxylates + oxo bridges","2 H2O -> O2 (PSII)"),
        ("CO dehydrogen.","Ni-Fe","Ni-Fe-S cluster",          "CO2 <-> CO interconv."),
    ]
    for n, m, lig, r in bio:
        print(f"  {n:<14s}  {m:<6s}  {lig:<28s}  {r:<22s}")
    print()
    print("Three motifs to notice (substrate framing):")
    print("  - PORPHYRIN class (heme, chlorophyll, B12 corrin):")
    print("    pre-formed 4-N macrocyclic strain template with axial slot for")
    print("    substrate (O2, CO2, R-CH3) and trans-axial protein anchor.")
    print()
    print("  - MULTI-METAL CLUSTERS (FeMoco, OEC, [4Fe-4S]):")
    print("    coupled strain bridges allow MULTI-ELECTRON chemistry (4 e- for")
    print("    O2 reduction, 6 e- for N2 fixation) that single sites cannot manage.")
    print()
    print("  - HARD-LEWIS-ACID Zn (carbonic anhydrase, peptidases):")
    print("    Zn2+ has no d-d color and no redox chemistry; pure Lewis-acidic")
    print("    polarization of bound water lowers pKa from 14 to ~7 -> active OH-.")
    print()
    print("Substrate unification: every biological metal center is a ligand-built")
    print("'strain die' — a fixed-geometry template that channels substrate strain")
    print("through one specific reaction trajectory at near-perfect selectivity.")

    # ============================================================
    section(11, "SUMMARY:  one bridge type, many cages")
    # ============================================================
    print("Coordination chemistry = donor-acceptor strain-bridge geometry.")
    print()
    print("  CN  -> polyhedron      = min-strain arrangement of bridges")
    print("  isomerism             = which bridge connects to which lobe")
    print("  chelate / macrocycle  = entropy from CLOSED-LOOP strain circuits")
    print("  EDTA                  = hexadentate cage; analytical workhorse")
    print("  4f / 5f               = compact strain modes; weak ligand field; sharp lines")
    print("  color (10 Dq)         = bridge stiffness sets t2g <-> eg gap")
    print("  high vs low spin      = sigma<=1/2 cap balanced against bridge K")
    print("  mu_eff = sqrt(n(n+2)) = unpaired strain modes contribute mu_B each")
    print("  bioinorganic centers  = pre-organized strain templates for catalysis")
    print()
    print("Honest scoreboard: substrate REPRODUCES the standard ligand-field, MO,")
    print("and crystal-field results because the bound-state spectrum of the")
    print("substrate Lagrangian reduces to the Schrodinger equation.  Value-add")
    print("is unification: Werner counting, isomer enumeration, chelate entropy,")
    print("lanthanide contraction, color, magnetism, and bioinorganic catalysis")
    print("all become facets of the same strain-bridge / saturation calculus.")


if __name__ == "__main__":
    main()
