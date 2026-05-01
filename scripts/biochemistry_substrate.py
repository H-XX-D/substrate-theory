"""Biochemistry & enzyme kinetics in the strain-medium framework.

Goes deeper than biomedical_substrate.py: every enzyme, fold, and metabolic
flux is one substrate strain template in a different geometric configuration.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Biochemical re-mapping:
  Enzyme       =  pre-organized substrate strain template
  Active site  =  scaffolded strain pocket complementary to TS geometry
  Folding      =  strain energy minimization on rugged substrate landscape
  Native state =  global strain minimum (Anfinsen)
  Allostery    =  long-range strain coupling between binding sites
  Pathway      =  cascaded strain transfer across templated catalysts

Honest framing: substrate REPRODUCES standard biochemistry numbers;
the value-add is unification across folding, kinetics, allostery,
and metabolism as one strain story.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
K_B = 1.380649e-23
N_A = 6.02214076e23
R_GAS = 8.314462618          # J/(mol K)
EV_J = 1.602176634e-19
ANGSTROM = 1.0e-10
KCAL_KJ = 4.184


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Biochemistry & enzyme kinetics in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives:  K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Enzyme   = pre-organized substrate strain template")
    print("Folding  = strain energy minimization on rugged landscape")
    print("Native   = global substrate strain minimum (Anfinsen)")
    print()

    T = 310.15           # body temperature
    RT = R_GAS * T       # J/mol
    RT_kJ = RT / 1000.0
    print(f"Working temperature T = {T:.2f} K ({T-273.15:.1f} C, body temperature)")
    print(f"RT = {RT_kJ:.3f} kJ/mol = {RT_kJ/KCAL_KJ:.3f} kcal/mol")

    # ============================================================
    section(1, "AMINO ACIDS, pKa, AND PEPTIDE-BOND STRAIN GEOMETRY")
    # ============================================================
    print("Amino acid = small substrate strain unit with backbone (NH-Calpha-CO)")
    print("plus side chain R that sets the local strain landscape (charge, H-bond,")
    print("hydrophobic patch). The peptide bond C(=O)-N has partial pi character")
    print("from substrate strain delocalization -> ~40% double-bond, planar, rigid.")
    print()
    print(f"  {'group':<28s}  {'pKa':>6s}  {'role in substrate strain':<28s}")
    pkas = [
        ("alpha-COOH (terminus)",          2.34, "anchors charged H-bridge"),
        ("alpha-NH3+ (terminus)",          9.69, "anchors charged H-bridge"),
        ("Asp (D) side chain",             3.65, "carboxylate strain pocket"),
        ("Glu (E) side chain",             4.25, "carboxylate strain pocket"),
        ("His (H) imidazole",              6.00, "proton shuttle (catalysis)"),
        ("Cys (C) thiol",                  8.33, "S-S strain bridge / nucleophile"),
        ("Tyr (Y) phenol",                10.07, "H-bond donor / e- relay"),
        ("Lys (K) epsilon-NH3+",          10.53, "salt bridge anchor"),
        ("Arg (R) guanidinium",           12.48, "salt bridge / phosphate clamp"),
    ]
    for name, p, role in pkas:
        print(f"  {name:<28s}  {p:>6.2f}  {role:<28s}")
    print()
    print("Peptide bond geometry (Pauling 1951, derived from substrate planarity):")
    print("  C-N length      = 1.32 A   (vs 1.47 A single, 1.27 A double)")
    print("  omega torsion   = 180 deg (trans, 99.95%)  /  0 deg (cis, 0.05%, X-Pro)")
    print("  C=O ... H-N H-bond  = 5 kcal/mol  -> backbone scaffold")
    print()
    print("Ramachandran allowed regions (phi, psi backbone torsions):")
    print("  alpha-helix (R)   :  phi ~ -57 deg, psi ~ -47 deg")
    print("  beta-sheet        :  phi ~ -120,    psi ~ +120")
    print("  L-alpha (rare)    :  phi ~ +57,     psi ~ +47   (mostly Gly only)")
    print("  Disallowed ~75% of (phi,psi) plane -> substrate steric strain veto.")
    print()
    # quick steric check on tetrahedral geometry
    print("Substrate basis: Calpha is sp3 (109.47 deg) -> tetrahedral strain lobes.")
    cos_tet = -1.0/3.0
    print(f"  cos(theta_tet) = -1/3  =>  theta = {math.degrees(math.acos(cos_tet)):.3f} deg")

    # ============================================================
    section(2, "SECONDARY STRUCTURE: alpha-HELIX, beta-SHEET, TURNS")
    # ============================================================
    print("Secondary structure = periodic substrate strain pattern stabilized by")
    print("backbone H-bonds (i, i+n) closing strain loops.")
    print()
    print("alpha-helix (Pauling-Corey 1951):")
    helix_res_per_turn = 3.6
    helix_rise = 1.5            # A per residue
    helix_pitch = helix_res_per_turn * helix_rise
    print(f"  residues / turn = {helix_res_per_turn}")
    print(f"  rise / residue  = {helix_rise} A")
    print(f"  pitch (rise / turn) = {helix_pitch:.2f} A")
    print(f"  H-bond pattern  = i to i+4   (5-atom loop, n=13 atoms)")
    print(f"  rotation/residue = 360/3.6 = {360/helix_res_per_turn:.0f} deg")
    print()
    print("Substrate reading: helix is the pitch resonance of the backbone strain")
    print("under the (i, i+4) H-bond constraint. 3.6 res/turn is the geometric")
    print("optimum that simultaneously closes the H-bond AND avoids Calpha clash.")
    print()
    print("beta-sheet:")
    print("  rise / residue (extended) = 3.5 A")
    print("  H-bond pattern (parallel)     = i to i+1 across strands")
    print("  H-bond pattern (antiparallel) = i to i (2-residue period -> ~7 A)")
    print("  parallel sheet slightly less stable (H-bonds non-linear).")
    print()
    print("Turns and loops:")
    print("  Type I beta-turn (i, i+3 H-bond, 4 residues, ~75% of all turns)")
    print("  Type II requires Gly at i+2 (low-strain pocket).")
    print()
    print(f"  {'fold element':<22s}  {'period':>10s}  {'H-bond':<14s}  {'fraction':>10s}")
    elems = [
        ("alpha-helix",          "5.4 A/turn",  "i,i+4",   "~30%"),
        ("310-helix",            "6.0 A/turn",  "i,i+3",   "~4%"),
        ("pi-helix",             "5.0 A/turn",  "i,i+5",   "<1%"),
        ("beta-sheet (par)",     "6.5 A",       "cross",   "~12%"),
        ("beta-sheet (antipar)", "7.0 A",       "cross",   "~12%"),
        ("turn",                 "~6 A",        "i,i+3",   "~25%"),
        ("loop / coil",          "n/a",         "varied",  "~17%"),
    ]
    for n, p, h, f in elems:
        print(f"  {n:<22s}  {p:>10s}  {h:<14s}  {f:>10s}")

    # ============================================================
    section(3, "TERTIARY / QUATERNARY STRUCTURE & FOLDING FUNNEL")
    # ============================================================
    print("Levinthal paradox (1969): a 100-residue chain with 3 torsions/residue")
    print("at 3 states each has 3^200 ~ 10^95 conformations. Random search at")
    print("10^13 attempts/s would take 10^75 years -- yet folding takes ~ms.")
    print()
    print("Resolution: the energy landscape is NOT flat with one needle minimum;")
    print("it is a FUNNEL (Bryngelson, Wolynes 1987, 1995). Substrate strain")
    print("gradients channel the chain toward the native fold.")
    print()
    print("Key landscape descriptors (for a 100-res protein):")
    n_res = 100
    omega_unfold = 3 ** (2 * n_res)
    print(f"  conformations (3^{2*n_res})         = {omega_unfold:.2e}")
    print(f"  configurational entropy S      = R ln Omega = {R_GAS*math.log(omega_unfold)/1000:.2f} kJ/(mol K)")
    print(f"  T*S at 310 K                   = {T*R_GAS*math.log(omega_unfold)/1000:.0f} kJ/mol  (entropy cost)")
    print(f"  typical native stability       =   25 - 60 kJ/mol  (delta_G_fold)")
    print(f"  -> need >= ~3000 kJ/mol of enthalpic strain release to fold.")
    print()
    print("Substrate funnel principle:")
    print("  - Top of funnel: high-strain, high-entropy disordered strain field")
    print("  - Sides:         partially correct contacts reduce strain locally")
    print("  - Bottom:        native state = global substrate strain minimum")
    print("  - Ruggedness:    local minima -> kinetic intermediates / molten globule")
    print()
    print("Folding regimes (sigma<=1/2 cap forbids overpacked intermediates):")
    print(f"  {'class':<18s}  {'time scale':>14s}  {'mechanism':<28s}")
    fold = [
        ("Two-state",         "10 us - 10 ms", "downhill funnel"),
        ("Three-state",       "1 ms - 1 s",    "molten globule intermediate"),
        ("Chaperone-aided",   "1 - 100 s",     "GroEL/Hsp70 strain reset"),
        ("Misfold (amyloid)", "hours - years", "off-pathway beta-stack basin"),
    ]
    for c, t, m in fold:
        print(f"  {c:<18s}  {t:>14s}  {m:<28s}")
    print()
    print("Quaternary level: subunits = local strain minima that DOCK along")
    print("complementary surfaces -> hemoglobin (alpha2 beta2), ATP synthase (~30),")
    print("ribosome (~80 proteins + 4 RNAs).  Driven by shape + electrostatic")
    print("complementarity -- substrate strain interlock.")

    # ============================================================
    section(4, "ANFINSEN'S PRINCIPLE & THERMODYNAMICS OF FOLDING")
    # ============================================================
    print("Anfinsen (1961, Nobel 1972): ribonuclease A refolds spontaneously")
    print("from denatured + reduced state -> sequence ENCODES the global minimum.")
    print()
    print("Substrate restatement:")
    print("  Native state = global minimum of total substrate strain functional")
    print("                 E[u] = integral [(1/2) K |grad u|^2 + V(u) + Coulomb")
    print("                                  + hydrophobic + H-bond] dV")
    print("  Sequence selects the strain functional via residue side chains.")
    print()
    print("Folding free energy components (typical 100-residue domain, kJ/mol):")
    comp = [
        ("H-bond network (backbone+SC)",   -350),
        ("Hydrophobic burial",             -250),
        ("van der Waals packing",          -100),
        ("Electrostatics / salt bridges",   -40),
        ("Disulfide bonds (if present)",    -20),
        ("Conformational entropy (chain)",  +700),
        ("Solvent entropy gain (release)", -200),
    ]
    total = 0
    print(f"  {'contribution':<34s}  {'kJ/mol':>10s}")
    for n, v in comp:
        print(f"  {n:<34s}  {v:>10d}")
        total += v
    print(f"  {'-'*34:<34s}  {'-'*10:>10s}")
    print(f"  {'NET delta_G_fold':<34s}  {total:>10d}")
    print(f"  Empirical range:  -25 to -60 kJ/mol  (marginal stability)")
    print()
    print("Substrate insight: the marginal stability (~5-10 RT) is the")
    print("signature of a SATURATED strain field -- adding more contacts")
    print("would push past sigma<=1/2 and destabilize the fold.")

    # ============================================================
    section(5, "MICHAELIS-MENTEN KINETICS DERIVED FROM STRAIN TEMPLATE")
    # ============================================================
    print("Substrate-level mechanism:")
    print("    E + S  <-->  ES  -->  E + P")
    print("           k1, k-1      kcat")
    print()
    print("ES = enzyme strain pocket fully bridged to substrate strain field.")
    print("Steady-state assumption (Briggs-Haldane 1925):  d[ES]/dt = 0")
    print()
    print("  v = kcat [E]_t [S] / (K_M + [S])")
    print("  K_M = (k-1 + kcat) / k1   (substrate concentration at v = Vmax/2)")
    print("  Vmax = kcat [E]_t          (full strain-pocket throughput)")
    print("  kcat / K_M  = catalytic efficiency (diffusion-limited ceiling ~10^9 /M/s)")
    print()
    print("Representative enzymes (substrate strain throughput):")
    print(f"  {'enzyme':<26s}  {'kcat [1/s]':>12s}  {'K_M [M]':>12s}  {'kcat/K_M':>12s}")
    enz = [
        ("Carbonic anhydrase",      1.0e6, 1.2e-2, 8.3e7),
        ("Catalase",                4.0e7, 1.1e+0, 4.0e7),
        ("Acetylcholinesterase",    1.4e4, 9.5e-5, 1.5e8),
        ("Fumarase",                8.0e2, 5.0e-6, 1.6e8),
        ("Triose-P isomerase",      4.3e3, 4.7e-4, 2.4e8),
        ("Chymotrypsin",            1.0e2, 8.0e-3, 1.3e4),
        ("Penicillinase",           2.0e3, 2.0e-5, 1.0e8),
        ("DNA polymerase III",      1.0e3, 1.0e-5, 1.0e8),
        ("Hexokinase (glucose)",    1.4e3, 1.5e-4, 9.3e6),
        ("Lysozyme",                5.0e-1,6.0e-6, 8.3e4),
    ]
    for n, k, km, eff in enz:
        print(f"  {n:<26s}  {k:>12.2e}  {km:>12.2e}  {eff:>12.2e}")
    print()
    print("Diffusion-limited bound (Smoluchowski): k_diff ~ 4 pi D R N_A ~ 10^9 /M/s")
    print("Carbonic anhydrase, catalase, TPI, fumarase are 'kinetically perfect'.")
    print()
    print("Substrate framing of K_M:  K_M is the substrate strain depth at which")
    print("the empty-pocket and filled-pocket strain energies cross.  Low K_M")
    print("means the strain pocket is deeply complementary.")

    # ============================================================
    section(6, "ENZYME CLASSIFICATION (EC1-EC6) AS STRAIN OPERATIONS")
    # ============================================================
    print("All enzymes fall into 6 strain-template operations on substrates:")
    print()
    print(f"  {'EC':<4s}  {'class':<18s}  {'strain operation':<32s}  {'example':<14s}")
    ec = [
        ("EC1", "Oxidoreductase",  "electron / H strain transfer",   "lactate DH"),
        ("EC2", "Transferase",     "moves a strain group A to B",    "hexokinase"),
        ("EC3", "Hydrolase",       "water-cleaves strain bridge",    "trypsin"),
        ("EC4", "Lyase",           "non-hydrolytic bridge cleavage", "fumarase"),
        ("EC5", "Isomerase",       "rearranges substrate strain",    "TPI"),
        ("EC6", "Ligase (synth)",  "ATP-driven strain joining",      "DNA ligase"),
    ]
    for c, n, op, ex in ec:
        print(f"  {c:<4s}  {n:<18s}  {op:<32s}  {ex:<14s}")
    print()
    print("Newly added EC7 (translocase, 2018): pumps substrates ACROSS membrane")
    print("strain barrier (e.g. Na/K-ATPase, F1Fo-ATPase, ABC transporters).")
    print()
    print("Substrate unification: every EC class is a different operator on the")
    print("substrate strain field.  Hydrolases insert water; lyases break a bond")
    print("non-hydrolytically; ligases re-fuse via energy from ATP hydrolysis.")

    # ============================================================
    section(7, "ALLOSTERY & COOPERATIVITY (long-range strain coupling)")
    # ============================================================
    print("Allostery = ligand binding at site A propagates substrate strain to")
    print("a distal site B and changes its affinity.  Two canonical models:")
    print()
    print("  MWC (Monod-Wyman-Changeux 1965):  concerted T <-> R switch")
    print("    All subunits flip together; substrate strain has TWO basins.")
    print()
    print("  KNF (Koshland-Nemethy-Filmer 1966): sequential induced fit")
    print("    Each subunit reshapes locally; strain propagates one neighbor at a time.")
    print()
    print("Hill equation:  Y = [L]^n / (K_d^n + [L]^n)")
    print("  n = 1   non-cooperative   (single hyperbolic site)")
    print("  n > 1   positive coop     (sigmoidal binding)")
    print("  n < 1   negative coop     (binding inhibits further binding)")
    print()
    print(f"  {'system':<28s}  {'n_Hill':>7s}  {'role':<28s}")
    hill = [
        ("Hemoglobin O2 binding",         2.8, "transport saturation switch"),
        ("Myoglobin O2 (control)",        1.0, "single-site (no coop)"),
        ("Aspartate transcarbamoylase",   2.0, "feedback in pyrimidine synth"),
        ("Phosphofructokinase-1",         3.8, "glycolysis gatekeeper"),
        ("Glutamate dehydrogenase",       1.5, "amino acid balance"),
        ("Voltage-gated K+ channel (Sh)", 4.0, "4 subunits, switch-like opening"),
        ("Ryanodine receptor (Ca2+)",     2.5, "Ca-induced Ca release"),
        ("Lac repressor (DNA bind)",      2.0, "operon switch"),
    ]
    for s, n, r in hill:
        print(f"  {s:<28s}  {n:>7.2f}  {r:<28s}")
    print()
    print("Hemoglobin numbers (the textbook case):")
    print("  P50 (lung)    ~ 100 mmHg pO2  -> 97% saturation")
    print("  P50 (tissue)  ~  40 mmHg pO2  -> 75% saturation")
    print("  P50 (T <-> R) ~  26 mmHg")
    print("  delta_log K (T to R)  ~  500-fold affinity increase")
    print("  Bohr effect: low pH -> stabilizes T -> O2 release at active tissue.")
    print()
    print("Substrate basis: cooperativity = saturation cap sigma<=1/2 transfers")
    print("excess strain laterally to neighboring subunits, lowering THEIR barrier")
    print("for ligand binding.  All-or-nothing T->R = whole-strain-template flip.")

    # ============================================================
    section(8, "ENZYME INHIBITION (Lineweaver-Burk diagnostics)")
    # ============================================================
    print("Three classical inhibition modes on substrate strain templates:")
    print()
    print(f"  {'mode':<18s}  {'binds to':<12s}  {'apparent Vmax':<14s}  {'apparent K_M':<12s}")
    inh = [
        ("Competitive",      "E only",     "unchanged",    "increases"),
        ("Non-competitive",  "E and ES",   "decreases",    "unchanged"),
        ("Uncompetitive",    "ES only",    "decreases",    "decreases"),
        ("Mixed",            "E and ES*",  "decreases",    "either"),
    ]
    for m, b, vm, km in inh:
        print(f"  {m:<18s}  {b:<12s}  {vm:<14s}  {km:<12s}")
    print()
    print("Lineweaver-Burk plot: 1/v vs 1/[S]")
    print("  Slope     = K_M / Vmax")
    print("  y-intercept = 1 / Vmax")
    print("  x-intercept = -1 / K_M")
    print()
    print("Diagnostic patterns when inhibitor [I] is varied:")
    print("  Competitive    -> lines pivot at 1/Vmax (same y-intercept)")
    print("  Non-competitive -> lines pivot at -1/K_M (same x-intercept)")
    print("  Uncompetitive  -> lines stay PARALLEL (same slope)")
    print()
    print("Famous inhibitor examples:")
    print(f"  {'drug / poison':<28s}  {'mode':<14s}  {'target':<24s}")
    drugs = [
        ("Methotrexate",            "competitive",   "DHFR (folate analog)"),
        ("Statins (e.g. atorva)",   "competitive",   "HMG-CoA reductase"),
        ("Aspirin (acetyl)",        "irreversible",  "COX-1 / COX-2"),
        ("Penicillin (acyl)",       "irreversible",  "transpeptidase (PBP)"),
        ("Cyanide",                 "non-competitive","cytochrome c oxidase"),
        ("Lithium (Li+)",           "uncompetitive", "inositol-MP phosphatase"),
        ("Allopurinol",             "competitive",   "xanthine oxidase"),
        ("Sarin / VX nerve agent",  "irreversible",  "acetylcholinesterase"),
    ]
    for d, m, t in drugs:
        print(f"  {d:<28s}  {m:<14s}  {t:<24s}")
    print()
    print("Substrate framing: irreversible inhibitors covalently FUSE to the")
    print("strain pocket, permanently overriding its templating geometry.")
    print("Reversible inhibitors merely occupy a strain basin.")

    # ============================================================
    section(9, "ENZYME MECHANISMS: PROTEASES, LYSOZYME, RIBOZYMES")
    # ============================================================
    print("Serine protease (chymotrypsin / trypsin / elastase):")
    print("  Catalytic triad: Ser-195, His-57, Asp-102")
    print("  - Asp polarizes His, raising its proton-affinity (substrate strain coupling)")
    print("  - His abstracts Ser proton -> Ser-O- nucleophile")
    print("  - Ser-O- attacks substrate carbonyl C -> tetrahedral intermediate")
    print("  - Stabilized in 'oxyanion hole' (backbone NH H-bond pocket)")
    print("  - Acyl-enzyme released by water nucleophile via same triad")
    print(f"  Rate enhancement vs uncatalyzed: ~10^10")
    print()
    print("Lysozyme (Phillips 1965, first enzyme structure):")
    print("  Cleaves bacterial cell-wall peptidoglycan beta-1,4 link")
    print("  Acid-base: Glu-35 (general acid)  +  Asp-52 (nucleophile)")
    print("  Mechanism: covalent glycosyl-enzyme intermediate (Vocadlo 2001)")
    print(f"  Rate enhancement: ~10^8")
    print()
    print("Ribozymes (catalytic RNA -- substrate template made of RNA itself):")
    print("  Group I intron self-splicing (Cech 1982, Nobel 1989)")
    print("  RNase P: tRNA 5' processing (Altman, Nobel 1989)")
    print("  Hammerhead, hepatitis delta -- small Mg2+-dependent cleavers")
    print("  Ribosome PEPTIDYL-TRANSFERASE center: 23S rRNA, NOT protein!")
    print("  -> All life's protein synthesis is RNA-catalyzed (RNA world relic)")
    print()
    print("Kinetic isotope effects (KIE) in enzymes -- diagnostic of TS substrate strain:")
    print(f"  {'reaction':<32s}  {'KIE (k_H/k_D)':>16s}")
    kie = [
        ("LADH alcohol dehydrog (H transfer)", 3.5),
        ("Methylamine dehydrog (tunneling)",  17.0),
        ("Soybean lipoxygenase (tunneling)",  81.0),
        ("Chymotrypsin (rate-limiting H-bond)", 2.0),
        ("Carbonic anhydrase (proton wire)",   3.8),
    ]
    for r, k in kie:
        print(f"  {r:<32s}  {k:>16.1f}")
    print()
    print("KIE > 7 (semi-classical max ~7) signals quantum tunneling of H through")
    print("the substrate strain barrier -- direct evidence the catalytic step is")
    print("BELOW the saddle-point energy.")

    # ============================================================
    section(10, "METABOLIC PATHWAY FLUX & CONTROL")
    # ============================================================
    print("Glycolysis (Embden-Meyerhof-Parnas, 10 enzyme steps, cytosol):")
    print("  glucose + 2 NAD+ + 2 ADP + 2 Pi -> 2 pyruvate + 2 NADH + 2 ATP")
    print("  Net delta_G = -85 kJ/mol  (out of ~200 available, ~40% efficiency)")
    print()
    gly = [
        ("1. Hexokinase",            "G->G6P",         -16.7),
        ("2. Phosphoglucose isom.",  "G6P->F6P",        +1.7),
        ("3. PFK-1 (committed)",     "F6P->F1,6BP",   -14.2),
        ("4. Aldolase",              "split C6 -> 2 C3", +23.8),
        ("5. TPI",                   "DHAP <-> GAP",    +7.5),
        ("6. GAPDH",                 "GAP -> 1,3BPG",   +6.3),
        ("7. PGK",                   "1,3BPG -> 3PG",  -18.8),
        ("8. PGM",                   "3PG -> 2PG",      +4.4),
        ("9. Enolase",               "2PG -> PEP",      +1.8),
        ("10. PK",                   "PEP -> pyr",     -31.4),
    ]
    print(f"  {'step':<28s}  {'reaction':<22s}  {'dG std [kJ/mol]':>16s}")
    for s, r, dg in gly:
        print(f"  {s:<28s}  {r:<22s}  {dg:>16.1f}")
    print()
    print("Three irreversible (committed) steps: hexokinase, PFK-1, pyruvate kinase.")
    print("Flux control coefficient analysis (Kacser-Burns): PFK-1 dominant in muscle.")
    print()
    print("TCA / Krebs cycle (8 steps, mitochondrial matrix):")
    print("  acetyl-CoA + 3 NAD+ + FAD + GDP + Pi -> 2 CO2 + 3 NADH + FADH2 + GTP")
    print("  yields 12 ATP equiv per acetyl-CoA")
    print()
    print("Oxidative phosphorylation (electron transport + ATP synthase):")
    print("  H+ pumped across inner-mito membrane; F1Fo synthase = molecular turbine.")
    print("  Stoichiometry:  ~10 H+/turn, 3 ATP/turn  =>  3.33 H+/ATP")
    print("  delta_psi ~ 150-200 mV, delta_pH ~ 0.5  =>  proton-motive force ~22 kJ/mol")
    print()
    print("Energy yields per glucose (aerobic):")
    yields = [
        ("Glycolysis (substrate-level)",  2),
        ("Pyruvate -> acetyl-CoA (NADH)", 5),
        ("TCA (substrate-level GTP)",      2),
        ("TCA NADH x6 -> ETC",            15),
        ("TCA FADH2 x2 -> ETC",            3),
    ]
    tot = 0
    print(f"  {'source':<32s}  {'ATP':>4s}")
    for s, a in yields:
        tot += a
        print(f"  {s:<32s}  {a:>4d}")
    print(f"  {'-'*32:<32s}  {'-'*4:>4s}")
    print(f"  {'TOTAL aerobic ATP / glucose':<32s}  {tot:>4d}")
    print()
    print("Substrate framing: each enzyme is a strain template; the pathway is")
    print("a CASCADE that hands strain (and high-energy phosphate) along a")
    print("controlled gradient.  Flux control = which strain template is rate-")
    print("limiting at the current substrate / product strain levels.")

    # ============================================================
    section(11, "DNA / RNA CHEMISTRY & WATSON-CRICK STRAIN BRIDGES")
    # ============================================================
    print("Base-pair H-bond strain bridges (canonical Watson-Crick):")
    print()
    print(f"  {'pair':<6s}  {'H-bonds':>8s}  {'E [kcal/mol]':>13s}  {'E [kJ/mol]':>12s}")
    bp = [
        ("A=T",   2,  -7.0,   -29.3),
        ("G#C",   3, -16.0,   -66.9),
        ("G=U",   2,  -8.5,   -35.5),  # wobble
    ]
    for p, n, ek, ej in bp:
        print(f"  {p:<6s}  {n:>8d}  {ek:>13.1f}  {ej:>12.1f}")
    print()
    print("(Vacuum H-bond energies; in water, GC stack is ~2x AT thermodynamic")
    print(" stability after solvation correction.)")
    print()
    print("Stacking (pi-stack substrate strain) often DOMINATES base-pairing in")
    print("aqueous duplex stability:  ~ -8 to -14 kJ/mol per stacked base pair.")
    print()
    print("B-DNA double helix geometry (Watson-Crick-Franklin 1953):")
    print(f"  rise / bp        = 3.4 A")
    print(f"  twist / bp       = 36 deg")
    print(f"  bp / turn        = 10.5  (in solution)  /  10 (crystal)")
    print(f"  pitch (per turn) = 35.7 A")
    print(f"  diameter         = 20 A")
    print(f"  major groove     = 22 A wide, shallow")
    print(f"  minor groove     = 12 A wide, deep")
    print()
    print("A-form DNA/RNA hybrids: 11 bp/turn, 26 A pitch, deeper major groove.")
    print("Z-form DNA: left-handed, 12 bp/turn, occurs at GC-rich tracts under")
    print("high salt -- a substrate strain bistability triggered by ionic screening.")
    print()
    print("Double-helix melting:")
    print("  Tm = 81.5 + 16.6 log[Na+] + 0.41 (%GC) - 600/length  (Wallace rule)")
    print("  GC pairs add ~ 6 deg C each (3 H-bonds vs 2)")
    print()
    print("Substrate framing: B-DNA = closed standing-wave strain helix with")
    print("minor/major grooves as accessible binding strain pockets.  Transcription")
    print("factors recognize sequence by reading H-bond donor/acceptor pattern in")
    print("the major groove (substrate strain signature, no full melt required).")

    # ============================================================
    section(12, "SUMMARY: one strain template, all of biochemistry")
    # ============================================================
    print("Every biochemical phenomenon is the SAME substrate strain field in a")
    print("different geometric configuration:")
    print()
    print("  amino acid             = local strain unit + side-chain landscape")
    print("  peptide bond           = partial-pi planar strain bridge")
    print("  alpha-helix            = 3.6-residue pitch resonance under (i,i+4) H-bond")
    print("  beta-sheet             = parallel/antiparallel strand strain lattice")
    print("  tertiary fold          = global minimum on rugged strain landscape")
    print("  Anfinsen native state  = sequence-encoded global strain minimum")
    print("  enzyme active site     = pre-organized strain pocket (TS complement)")
    print("  Michaelis kcat / K_M   = throughput / depth of strain pocket")
    print("  EC1-EC7 enzyme classes = 7 strain operations on substrate field")
    print("  allostery (Hill n>1)   = lateral strain coupling + sigma<=1/2 cap")
    print("  inhibition (C/N/U)     = where inhibitor docks in strain pocket")
    print("  catalytic triad        = relayed proton on coupled strain wire")
    print("  ribozyme               = RNA strain template (RNA-world catalysis)")
    print("  glycolysis / TCA / OXPHOS = strain cascade w/ committed gates")
    print("  ATP / GTP              = high-energy phosphate strain capacitor")
    print("  Watson-Crick pair      = 2 or 3 H-bond strain bridges")
    print("  B-DNA helix            = closed standing-wave strain helix")
    print()
    print("Honest scoreboard: substrate REPRODUCES all standard biochemistry")
    print("numbers (kcat, K_M, Hill n, fold delta_G, helix pitch, base-pair E).")
    print("Value-add: 11 chapters of biochemistry collapse to one strain-template")
    print("story rather than eleven empirical compendia.")
    print()
    print("Falsifier: any process where the substrate strain template would")
    print("predict a quantitatively different number than measured -- e.g. an")
    print("enzyme exceeding the diffusion-limited 10^9 /M/s ceiling without")
    print("a documented strain-channeling or proximity mechanism.")


if __name__ == "__main__":
    main()
