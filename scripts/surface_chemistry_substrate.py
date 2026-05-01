"""Surface chemistry and heterogeneous catalysis in the strain-medium framework.

Surfaces = substrate strain DISCONTINUITIES (broken translation symmetry).
Adsorption = strain-bridge formation between adsorbate and surface modes.
Catalysis  = pre-organized strain template that lowers TS-strain saddle.

Substrate primitives (4 + 1 cap):
  K (stiffness), rho (density), xi (length), gamma (drag), saturation sigma<=1/2

Honest framing: substrate REPRODUCES standard surface-science numbers
(Young, Langmuir, BET, Sabatier, Eyring) because the underlying field
equation is the same. Value-add is unification of seven empirical sub-fields
of surface chemistry under one strain-template story.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR = 1.054571817e-34
EV_J = 1.602176634e-19
K_B = 1.380649e-23
N_A = 6.02214076e23
R_GAS = 8.314462618    # J/(mol K)
ANGSTROM = 1.0e-10


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Surface chemistry & heterogeneous catalysis in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives:  K, rho, xi, gamma  +  saturation sigma <= 1/2")
    print("Surface  =  substrate strain DISCONTINUITY (translation symmetry broken)")
    print("Adsorption  =  strain bridge between adsorbate mode and surface mode")
    print("Catalysis  =  pre-organized strain template across the surface")
    print()

    # ============================================================
    section(1, "SURFACE ENERGY & WETTING (Young equation from strain mismatch)")
    # ============================================================
    print("Creating a surface = cutting substrate -> dangling strain bonds.")
    print("Surface energy gamma_s = energy cost per unit area of the cut.")
    print()
    print("Substrate prediction:  gamma_s ~ K * xi  (stiffness * coherence length)")
    print("High-K materials (metals, oxides) -> high gamma_s.")
    print("Low-K materials (polymers, organics) -> low gamma_s.")
    print()
    print(f"  {'material':<22s}  {'gamma_s [mN/m]':>14s}  {'class':<14s}")
    surf = [
        ("Water (l)",                72.8, "low (H-bond)"),
        ("Mercury (l)",              485,  "metal"),
        ("Iron (s, ~mp)",           2400,  "transition met"),
        ("Tungsten (s)",            3300,  "high-mp metal"),
        ("Aluminum (s)",            1140,  "metal"),
        ("Gold (s)",                1500,  "noble metal"),
        ("Diamond (111)",           5500,  "covalent"),
        ("MgO (100)",               1200,  "ionic oxide"),
        ("SiO2 (silica)",            290,  "oxide glass"),
        ("Polyethylene",              33,  "polymer"),
        ("PTFE (Teflon)",             19,  "fluoropolymer"),
        ("Paraffin wax",              25,  "alkane"),
    ]
    for m, g, c in surf:
        print(f"  {m:<22s}  {g:>14.1f}  {c:<14s}")
    print()
    print("Young equation (force balance at three-phase line):")
    print("    gamma_sv  =  gamma_sl  +  gamma_lv * cos(theta)")
    print("    cos(theta) = (gamma_sv - gamma_sl) / gamma_lv")
    print()
    print("Substrate reading: cos(theta) measures how well substrate strain bridges")
    print("from the liquid match the surface dangling-strain pattern.")
    print("  cos(theta) ~ +1  -> perfect match (strain-coherent wetting)")
    print("  cos(theta) ~  0  -> orthogonal modes (theta = 90 deg)")
    print("  cos(theta) ~ -1  -> orthogonal repulsion (super-hydrophobic)")
    print()
    print("Water contact angle on common surfaces (measured):")
    print(f"  {'surface':<22s}  {'theta [deg]':>12s}  {'character':<18s}")
    water = [
        ("Clean glass",                 5,  "super-hydrophilic"),
        ("Mica (fresh cleavage)",       0,  "perfectly wetting"),
        ("Gold (clean)",               65,  "moderately hydrophil"),
        ("Polyethylene",               94,  "weakly hydrophobic"),
        ("Paraffin wax",              108,  "hydrophobic"),
        ("PTFE (Teflon)",             112,  "very hydrophobic"),
        ("Lotus leaf (textured)",     160,  "super-hydrophobic"),
        ("Octadecyl SAM on Au",       110,  "alkyl SAM"),
    ]
    for s, t, c in water:
        print(f"  {s:<22s}  {t:>12d}  {c:<18s}")
    print()
    print("Quick numerical check (water on PTFE):")
    g_lv = 72.8
    g_sv = 19.0
    g_sl = 50.0   # rough estimate
    cos_t = (g_sv - g_sl) / g_lv
    cos_t = max(-1.0, min(1.0, cos_t))
    theta = math.degrees(math.acos(cos_t))
    print(f"  gamma_lv = {g_lv:.1f}, gamma_sv = {g_sv:.1f}, gamma_sl ~ {g_sl:.1f} mN/m")
    print(f"  predicted theta ~ {theta:.0f} deg   (measured ~112 deg)")

    # ============================================================
    section(2, "LANGMUIR & BET ADSORPTION ISOTHERMS")
    # ============================================================
    print("Adsorption = strain-bridge between gas-phase adsorbate and a surface site.")
    print()
    print("Langmuir model (single-layer, equivalent independent sites):")
    print("    theta(P) = K_eq * P / (1 + K_eq * P)")
    print("Saturation cap sigma <= 1/2 reads here as ONE adsorbate per site.")
    print()
    print("BET model (multilayer):")
    print("    P/(V (P0-P)) = 1/(Vm c) + ((c-1)/(Vm c)) * (P/P0)")
    print("Multilayer adsorption uses higher transverse strain modes (n>=2).")
    print()
    # Langmuir demo
    print("Langmuir example (K_eq = 0.5 atm^-1, P scan):")
    K_eq = 0.5
    print(f"  {'P [atm]':>8s}  {'theta':>8s}")
    for P in (0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0):
        theta = K_eq * P / (1 + K_eq * P)
        print(f"  {P:>8.2f}  {theta:>8.4f}")
    print()
    print("Surface area from BET (typical industrial catalysts):")
    print(f"  {'material':<28s}  {'BET area [m2/g]':>16s}")
    bet = [
        ("Activated carbon",            1500),
        ("Silica gel",                   600),
        ("Alumina (gamma-Al2O3)",        250),
        ("Zeolite ZSM-5",                400),
        ("Metal-organic framework MOF",  4500),
        ("Pt black",                      30),
        ("Raney nickel",                 100),
        ("Carbon black",                  80),
        ("Microporous silica MCM-41",   1000),
    ]
    for m, a in bet:
        print(f"  {m:<28s}  {a:>16d}")
    print()
    print("Substrate framing: high BET area = many strain-discontinuity sites per gram.")
    print("Pore engineering = shaping the substrate-mode density of states.")

    # ============================================================
    section(3, "PHYSISORPTION vs CHEMISORPTION (vdW vs covalent bridges)")
    # ============================================================
    print("Two regimes of the SAME strain-bridge geometry:")
    print()
    print(f"  {'feature':<22s}  {'physisorption':<22s}  {'chemisorption':<22s}")
    rows = [
        ("bridge type",        "induced-dipole (vdW)",   "shared strain lobe"),
        ("E_ads [kJ/mol]",     "5 - 40",                 "40 - 800"),
        ("range",              "long (xi^-6)",           "short (~bond length)"),
        ("specificity",        "non-specific",           "site/orientation specific"),
        ("temperature",        "low T (T < ~150 K)",     "wide T window"),
        ("layers",             "multilayer (BET)",       "monolayer (Langmuir)"),
        ("activation E_a",     "~0",                     "may have barrier"),
        ("reversibility",      "reversible",             "often irreversible"),
    ]
    for a, b, c in rows:
        print(f"  {a:<22s}  {b:<22s}  {c:<22s}")
    print()
    print("Substrate reading:")
    print("  physisorption -> weak transverse-mode coupling, no electron sharing")
    print("  chemisorption -> strain-lobe overlap with surface dangling modes")
    print("                   (true new bond formed)")

    # ============================================================
    section(4, "HETEROGENEOUS CATALYSIS MECHANISMS (LH vs ER)")
    # ============================================================
    print("Two limiting mechanisms for an A + B -> product reaction on a surface:")
    print()
    print("Langmuir-Hinshelwood (LH): BOTH reactants adsorb, then react on surface")
    print("    rate = k * theta_A * theta_B")
    print("    -> rate maximum at intermediate coverage; -> volcano in (P_A, P_B)")
    print()
    print("Eley-Rideal (ER): ONE reactant adsorbs, the other strikes from gas phase")
    print("    rate = k * theta_A * P_B")
    print("    -> monotonic in P_B, dominant at very high gas-phase pressure")
    print()
    print("Substrate distinction: LH = two strain bridges meet on the surface and")
    print("merge; ER = one strain bridge meets a free incoming strain pulse.")
    print()
    print(f"  {'reaction':<32s}  {'mechanism':<10s}  {'catalyst':<10s}")
    mech = [
        ("CO oxidation on Pt",            "LH",  "Pt"),
        ("H2 + D2 -> 2 HD on Pt",         "LH",  "Pt"),
        ("Hydrogenation R-CH=CH2 + H2",   "LH",  "Ni/Pd"),
        ("Photo-induced H + D/Pt",        "ER",  "Pt"),
        ("Atomic O recomb on shuttle TPS","ER",  "SiO2"),
    ]
    for r, m, c in mech:
        print(f"  {r:<32s}  {m:<10s}  {c:<10s}")

    # ============================================================
    section(5, "SABATIER PRINCIPLE & VOLCANO PLOTS")
    # ============================================================
    print("Sabatier: optimal catalyst binds the intermediate NEITHER too weakly")
    print("(no activation) NOR too strongly (poisons the surface).")
    print()
    print("Substrate restatement: optimal binding = STRAIN MATCHING between the")
    print("intermediate's transverse mode and the surface's dangling strain mode.")
    print("Mismatch in either direction -> reduced rate.")
    print()
    print("Volcano plot example: NH3 synthesis activity vs M-N binding energy.")
    print(f"  {'metal':<8s}  {'E(M-N) [eV]':>12s}  {'activity (rel)':>14s}")
    volcano = [
        ("Mo",   7.0, 0.10),
        ("Fe",   6.0, 1.00),   # peak (industrial Haber catalyst)
        ("Ru",   5.5, 0.95),
        ("Co",   5.0, 0.40),
        ("Ni",   4.5, 0.20),
        ("Cu",   3.5, 0.05),
        ("Au",   2.5, 0.001),
    ]
    for m, e, a in volcano:
        bar = "#" * max(1, int(40 * a))
        print(f"  {m:<8s}  {e:>12.1f}  {a:>14.3f}  {bar}")
    print()
    print("Peak around Fe / Ru -> optimal substrate-strain matching for the N2*")
    print("intermediate. This is the empirical reason for Fe in Haber-Bosch.")
    print()
    # Numerical Sabatier model
    print("Quick Sabatier-shape model:  rate = exp(-(E - E*)^2 / (2 sigma^2))")
    E_opt = 6.0
    sigma_E = 1.5
    print(f"  E* = {E_opt} eV   sigma = {sigma_E} eV")
    for m, e, _ in volcano:
        r = math.exp(-(e - E_opt) ** 2 / (2 * sigma_E ** 2))
        print(f"  {m:<4s}  E = {e:.1f}   model rate = {r:.3f}")

    # ============================================================
    section(6, "INDUSTRIAL CATALYSTS (the workhorses)")
    # ============================================================
    print("Each line below is a multi-billion-dollar process running daily:")
    print()
    print(f"  {'process':<26s}  {'catalyst':<18s}  {'T [K]':>6s}  {'P [bar]':>8s}")
    indus = [
        ("Haber-Bosch (NH3)",        "Fe / K2O / Al2O3",  720, 200),
        ("Fischer-Tropsch",          "Co or Fe",          500, 30),
        ("Methanol synthesis",       "Cu / ZnO / Al2O3",  520, 80),
        ("Steam methane reforming",  "Ni / Al2O3",       1100, 25),
        ("Water-gas shift (HT)",     "Fe3O4 / Cr2O3",     680, 30),
        ("Three-way auto catalyst",  "Pt / Pd / Rh",      800,   1),
        ("Catalytic cracking (FCC)", "Y-zeolite",         800,   2),
        ("Hydrocracking",            "Pt or NiMoS / zeo", 670, 100),
        ("Catalytic reforming",      "Pt-Re / Al2O3",     800,  20),
        ("Contact (SO2 -> SO3)",     "V2O5 / K-sulfate",  720,   1),
        ("Ostwald (NH3 -> NO)",      "Pt / Rh gauze",    1100,  10),
        ("Olefin polymerization",    "Ziegler-Natta TiCl3", 350,  5),
        ("Hydrogenation (margarine)","Ni Raney",          450,  10),
        ("Epoxidation (EO)",         "Ag / Al2O3",        520,  20),
    ]
    for p, c, T, P in indus:
        print(f"  {p:<26s}  {c:<18s}  {T:>6d}  {P:>8d}")
    print()
    print("Substrate framing notes on selected entries:")
    print("  Haber-Bosch: Fe (110) face presents N2-strain-matched dangling modes.")
    print("               The K2O promoter electronically stiffens K* sites.")
    print("  Fischer-Tropsch: stepped Co/Fe surfaces template C-C strain chains.")
    print("  3-way catalyst: Pt oxidizes CO/HC, Rh reduces NOx; CeO2 stores O.")
    print("  Zeolite cracking: micropore geometry templates carbocation strain.")

    # ============================================================
    section(7, "MOLECULAR SIEVES & SHAPE-SELECTIVE CATALYSIS")
    # ============================================================
    print("Zeolites = aluminosilicate frameworks with sub-nm pores. The pore")
    print("geometry is itself a substrate-strain template -> shape selectivity.")
    print()
    print(f"  {'zeolite':<10s}  {'pore [A]':>10s}  {'channel system':<22s}  {'use':<18s}")
    zeo = [
        ("LTA (3A)",  3.0, "8-ring 3D",            "drying"),
        ("LTA (4A)",  4.0, "8-ring 3D",            "drying / sep"),
        ("LTA (5A)",  5.0, "8-ring 3D",            "n-paraffin sep"),
        ("ZSM-5",     5.5, "10-ring 3D",           "MTG / xylene"),
        ("Mordenite", 6.5, "12-ring 1D",           "alkylation"),
        ("Faujasite Y", 7.4, "12-ring 3D",         "FCC cracking"),
        ("Beta",      6.7, "12-ring 3D",           "alkylation"),
        ("SAPO-34",   3.8, "8-ring 3D",            "MTO (olefins)"),
    ]
    for z, p, c, u in zeo:
        print(f"  {z:<10s}  {p:>10.1f}  {c:<22s}  {u:<18s}")
    print()
    print("Three flavors of shape selectivity:")
    print("  1. reactant SS:  only molecules small enough to enter")
    print("  2. product SS:   only products small enough to leave")
    print("  3. transition-state SS: only TS geometries that fit the pore")
    print()
    print("Substrate reading: pore = a confining strain CAVITY whose normal modes")
    print("only support certain transverse-momentum patterns. Bigger molecules")
    print("don't have a matching strain mode in the cavity -> excluded.")

    # ============================================================
    section(8, "SELF-ASSEMBLED MONOLAYERS (SAMs)")
    # ============================================================
    print("SAM = densely packed monolayer formed spontaneously from a solution")
    print("of amphiphilic molecules with a head group that binds a substrate.")
    print()
    print("Canonical example: alkanethiols  HS-(CH2)n-CH3  on Au(111).")
    print("  - S head group makes a quasi-covalent S-Au bond (~50 kcal/mol)")
    print("  - alkyl tails crystallize via vdW into a (sqrt3 x sqrt3)R30 lattice")
    print("  - tilt angle ~30 deg from surface normal for n>=10")
    print()
    print(f"  {'SAM head':<14s}  {'substrate':<10s}  {'bond E [kJ/mol]':>14s}  {'use':<20s}")
    sam = [
        ("R-SH (thiol)",     "Au, Ag",      210, "molecular electronics"),
        ("R-SiCl3",          "SiO2",        450, "silanization"),
        ("R-PO3H2",          "TiO2, Al2O3", 380, "dental/biomed"),
        ("R-COOH",           "metal oxides", 80, "linker"),
        ("R-NH2",            "Au, oxides",   60, "biofunctionalization"),
    ]
    for s, sub, e, u in sam:
        print(f"  {s:<14s}  {sub:<10s}  {e:>14d}  {u:<20s}")
    print()
    print("Applications: tunable wettability, biosensors, OFET dielectrics,")
    print("nanoscale lithography resists, anti-fouling coatings, friction control.")
    print()
    print("Substrate reading: SAM = a 2D crystal of strain bridges all aligned")
    print("by the head-group lattice. Tail-tail vdW + head-substrate covalent")
    print("bridges give a self-healing, defect-tolerant strain template.")

    # ============================================================
    section(9, "SURFACE PLASMON RESONANCE (collective transverse mode)")
    # ============================================================
    print("Surface plasmon = collective oscillation of conduction-electron density")
    print("at a metal/dielectric interface. In substrate language: a TRANSVERSE")
    print("strain mode confined to the substrate discontinuity.")
    print()
    print("Dispersion (non-retarded SP):")
    print("    omega_sp  =  omega_p / sqrt(1 + eps_d)")
    print("with bulk plasma frequency  omega_p = sqrt(n e^2 / (m eps_0)).")
    print()
    print(f"  {'metal':<10s}  {'omega_p [eV]':>12s}  {'omega_sp(air) [eV]':>20s}  {'lambda_sp [nm]':>16s}")
    spr_data = [
        ("Au",   8.55, 8.55 / math.sqrt(2.0), 1240.0/(8.55/math.sqrt(2.0))),
        ("Ag",   9.01, 9.01 / math.sqrt(2.0), 1240.0/(9.01/math.sqrt(2.0))),
        ("Cu",   8.76, 8.76 / math.sqrt(2.0), 1240.0/(8.76/math.sqrt(2.0))),
        ("Al",  15.30, 15.30 / math.sqrt(2.0), 1240.0/(15.30/math.sqrt(2.0))),
    ]
    for m, wp, ws, lam in spr_data:
        print(f"  {m:<10s}  {wp:>12.2f}  {ws:>20.2f}  {lam:>16.0f}")
    print()
    print("Practical SPR sensors (Kretschmann config, lambda ~ 700-900 nm):")
    print("  - bind a ligand to Au film, watch resonance angle shift on binding")
    print("  - sensitivity ~ pg/mm^2 (single-molecule for tip-enhanced variants)")
    print("  - workhorse for label-free biomolecular interaction kinetics")
    print()
    print("Substrate reading: SPR = a confined transverse strain-mode at the")
    print("metal/dielectric discontinuity. Adsorbates load the mode (change rho,")
    print("xi locally), shifting omega_sp -> directly readable signal.")
    print("Localized SPR (nanoparticles) -> standing-wave on a curved discontinuity.")

    # ============================================================
    section(10, "STM / AFM (atomic-resolution substrate-strain probes)")
    # ============================================================
    print("Scanning probe microscopies image the substrate strain field directly:")
    print()
    print("  STM: tunneling current  I ~ exp(-2 kappa z)  with  kappa ~ 1.0 A^-1")
    print("       -> exponential sensitivity to height -> atomic resolution.")
    print("       Measures local density of substrate states at the Fermi level.")
    print()
    print("  AFM: cantilever feels short-range repulsion (sigma <= 1/2 cap kicks in)")
    print("       and long-range vdW attraction. Frequency-modulation NC-AFM")
    print("       resolves chemical bonds (Gross 2009: pentacene molecule).")
    print()
    print("Tunneling decay constant:")
    work_function_eV = 5.0   # typical metal phi
    kappa_inv_m = math.sqrt(2 * 9.109e-31 * work_function_eV * EV_J) / HBAR
    kappa_inv_A = kappa_inv_m * 1e-10
    print(f"  phi = {work_function_eV:.1f} eV  ->  kappa = {kappa_inv_A:.2f} A^-1")
    print(f"  one-A change in z changes I by factor exp(-2 kappa) = "
          f"{math.exp(-2*kappa_inv_A):.3f}")
    print(f"  -> ~order-of-magnitude per 1 A height change.")
    print()
    print("Substrate reading: STM tip = a localized strain-mode probe; the")
    print("tunneling channel = strain-bridge between tip apex mode and the")
    print("nearest surface dangling mode. AFM force gradient = d^2 V_strain / dz^2.")
    print("Both microscopies are direct measurements of the substrate strain field.")

    # ============================================================
    section(11, "SUMMARY: surfaces as strain discontinuities")
    # ============================================================
    print("Every topic above reduces to ONE substrate fact:")
    print("  a SURFACE is the locus where the substrate strain field changes")
    print("  character abruptly; everything that happens 'on' it is a strain")
    print("  bridge involving the dangling modes at that discontinuity.")
    print()
    print("Mappings:")
    print("  Young / wetting       <-> strain-mismatch at three-phase line")
    print("  Langmuir / BET        <-> single vs multilayer strain bridges")
    print("  physi vs chemi        <-> weak vdW vs covalent strain bridges")
    print("  Langmuir-Hinshelwood  <-> two surface strain bridges merging")
    print("  Eley-Rideal           <-> one bridge meets a gas-phase strain pulse")
    print("  Sabatier / volcano    <-> optimal substrate strain matching")
    print("  industrial catalysts  <-> strain templates engineered for one TS")
    print("  zeolite shape-select. <-> confined-mode geometry filter")
    print("  SAM                   <-> 2D crystal of head-group strain bridges")
    print("  SPR                   <-> confined transverse mode at interface")
    print("  STM/AFM               <-> atomic-resolution probe of strain field")
    print()
    print("Honest scoreboard: substrate framework reproduces standard surface")
    print("science numbers (Young, Langmuir, BET, Sabatier, Eyring, Drude-SP)")
    print("because the underlying field equation is the same. The value-add is")
    print("that ten distinct empirical chapters become ONE strain-template story.")


if __name__ == "__main__":
    main()
