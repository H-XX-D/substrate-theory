"""Analytical chemistry through the strain-medium framework.

Covers separations (chromatography, electrophoresis), spectrometric
detection (mass spec, atomic spec), electrochemical analysis, and
classical wet methods (titration, gravimetry).

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability

Substrate framing:
  Separation = different strain-bridge formation rates between an
    analyte and the stationary-phase substrate.
  Detection = readout of an ionized / excited substrate strain pattern
    through coupling to an external probe field (E, B, photons, current).

Honest framing: substrate REPRODUCES standard analytical performance
numbers (LOD, resolution, mass accuracy) — it does not replace them.
The value-add is unification: every separation principle and every
detector becomes one strain-bridge story rather than ten chapters.
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
E_CHARGE = 1.602176634e-19
M_E = 9.1093837015e-31
M_U = 1.66053906660e-27


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Analytical chemistry in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Separation = differential strain-bridge affinities (analyte / phase)")
    print("Detection  = readout of an ionized/excited substrate strain pattern")
    print()

    # ============================================================
    section(1, "CHROMATOGRAPHY THEORY (van Deemter, plates, resolution)")
    # ============================================================
    print("Chromatography = analyte molecules partition between a mobile and a")
    print("stationary substrate phase. Substrate reading: each phase offers a")
    print("DIFFERENT bridge geometry to the analyte's strain modes; the")
    print("retention time = mean dwell on the stationary bridge.")
    print()
    print("van Deemter equation for plate height H as a function of velocity v:")
    print()
    print("    H(v) = A + B/v + C v")
    print()
    print("  A = eddy diffusion (multipath strain dispersion in packed bed)")
    print("  B = longitudinal molecular diffusion (substrate random-walk)")
    print("  C = mass-transfer resistance (slow strain re-equilibration)")
    print()
    print("Optimum velocity v_opt = sqrt(B/C); H_min = A + 2 sqrt(B C).")
    print()
    A_vd = 0.0015   # m  (eddy term)
    B_vd = 1.5e-7   # m^2/s
    C_vd = 0.05     # s
    v_opt = math.sqrt(B_vd / C_vd)
    H_min = A_vd + 2 * math.sqrt(B_vd * C_vd)
    print(f"  Example (HPLC-like): A = {A_vd*1e3:.2f} mm  B = {B_vd:.1e} m^2/s  C = {C_vd:.3f} s")
    print(f"  v_opt = sqrt(B/C) = {v_opt*1e3:.3f} mm/s")
    print(f"  H_min = {H_min*1e6:.1f} micrometres")
    print()
    print("Plate count N for a column of length L:")
    print("    N = L / H = 16 (t_R / w)^2 = 5.545 (t_R / w_1/2)^2")
    L_col = 0.15
    N_plates = L_col / H_min
    print(f"  L = {L_col*100:.0f} cm  ->  N = {N_plates:.0f} theoretical plates")
    print()
    print("Resolution between two adjacent peaks (1 and 2):")
    print("    R = (t2 - t1) / ((w1 + w2)/2) ; baseline R >= 1.5")
    print()
    print("Substrate emergence: A,B,C are different geometric facets of the")
    print("same strain-bridge dynamics (multipath, diffusion, slow exchange).")

    # ============================================================
    section(2, "GAS CHROMATOGRAPHY (GC)")
    # ============================================================
    print("Mobile phase: inert carrier gas (He, H2, N2). Stationary phase:")
    print("polymer film coated on a capillary column wall, or packed bed.")
    print("Volatile analytes (T_b < ~400 C) partition into the polymer film.")
    print()
    print("Common stationary phases:")
    print(f"  {'phase':<12s}  {'chemistry':<32s}  {'polarity':<10s}  {'use':<14s}")
    gc_phases = [
        ("DB-1 / OV-1",  "100% PDMS",                   "non-polar",   "general"),
        ("DB-5",         "5% phenyl 95% PDMS",          "low",         "general"),
        ("DB-17",        "50% phenyl 50% PDMS",         "mid",         "drugs/PAH"),
        ("DB-WAX",       "PEG (Carbowax)",              "polar",       "alcohols"),
        ("DB-1701",      "14% cyanopropyl",             "mid-polar",   "pesticides"),
        ("Chiral beta",  "beta-cyclodextrin",           "chiral",      "enantiomers"),
    ]
    for n, c, p, u in gc_phases:
        print(f"  {n:<12s}  {c:<32s}  {p:<10s}  {u:<14s}")
    print()
    print("Capillary vs packed:")
    print("  Capillary:  0.1-0.5 mm i.d., 10-100 m, N=10^5, narrow peaks.")
    print("  Packed:     2-4 mm i.d., 1-3 m,  N=10^3-10^4, high capacity.")
    print()
    print("Detectors (substrate readout of GC eluate):")
    print(f"  {'det':<6s}  {'principle':<38s}  {'LOD (typ)':<12s}  {'selectivity':<14s}")
    gc_det = [
        ("FID",  "C-H combustion ions in H2 flame",       "1 pg C",      "C-H only"),
        ("TCD",  "thermal conductivity vs carrier",        "1 ng",        "universal"),
        ("ECD",  "e- capture by halogens / NO2",          "0.1 pg",      "halog/NO2"),
        ("NPD",  "alkali-bead enhanced N/P ions",          "0.4 pg N",    "N, P"),
        ("FPD",  "S/P chemiluminescence in H2 flame",      "20 pg S",     "S, P"),
        ("MS",   "ion source + mass analyzer",            "0.1-10 pg",   "universal"),
    ]
    for d, p, l, s in gc_det:
        print(f"  {d:<6s}  {p:<38s}  {l:<12s}  {s:<14s}")
    print()
    print("Substrate framing: detector = transducer between molecular strain")
    print("pattern and a measurable observable (current, voltage, ion count).")

    # ============================================================
    section(3, "HPLC (high-performance liquid chromatography)")
    # ============================================================
    print("Mobile phase: liquid pumped at 100-400 bar through a packed column")
    print("of 1.7-5 micrometre porous particles (silica or hybrid).")
    print()
    print("Modes (defined by relative polarity of mobile vs stationary):")
    print(f"  {'mode':<18s}  {'stationary':<18s}  {'mobile':<22s}  {'analyte':<12s}")
    modes = [
        ("Normal phase",    "polar (silica)",   "non-polar (hexane)",   "polar"),
        ("Reverse phase",   "non-polar (C18)",  "polar (water/MeCN)",   "non/mid"),
        ("HILIC",           "polar (silica)",   "high MeCN + water",    "polar"),
        ("Ion exchange",    "charged resin",    "buffer + salt grad",   "ions"),
        ("Size exclusion",  "porous gel",       "buffer (no interact)", "MW sep"),
        ("Affinity",        "ligand-bound",     "buffer / displacer",   "biomol"),
    ]
    for m, s, mo, a in modes:
        print(f"  {m:<18s}  {s:<18s}  {mo:<22s}  {a:<12s}")
    print()
    print("Isocratic vs gradient elution:")
    print("  Isocratic = constant mobile composition (simple, slow for wide log P).")
    print("  Gradient  = increasing organic % over time (sharper peaks, fast).")
    print()
    print("Common reverse-phase columns:")
    print(f"  {'column':<14s}  {'ligand':<22s}  {'pore':<8s}  {'particle':<8s}  {'use':<14s}")
    cols = [
        ("C18 (ODS)",    "octadecyl",            "100 A",   "1.7-5 um", "general RP"),
        ("C8",           "octyl",                "100 A",   "3-5 um",   "less hydrof"),
        ("C4",           "butyl",                "300 A",   "5 um",     "proteins"),
        ("Phenyl",       "phenyl-hexyl",         "100 A",   "3-5 um",   "aromatics"),
        ("CN",           "cyanopropyl",          "100 A",   "5 um",     "polar mid"),
        ("HILIC silica", "bare silica (HILIC)",  "100 A",   "1.7-5 um", "polar/sugars"),
        ("BEH C18",      "ethylene-bridged",     "130 A",   "1.7 um",   "UPLC"),
    ]
    for c, lig, p, part, u in cols:
        print(f"  {c:<14s}  {lig:<22s}  {p:<8s}  {part:<8s}  {u:<14s}")
    print()
    print("Substrate reading: stationary ligand offers a particular strain-")
    print("bridge geometry; analyte retention = how well its strain modes")
    print("match that geometry (k' partition coefficient).")

    # ============================================================
    section(4, "ION CHROMATOGRAPHY & ION-EXCHANGE RESINS")
    # ============================================================
    print("Ion exchange = ions in solution swap with counter-ions on a charged")
    print("resin. Substrate reading: charged strain pocket on the resin")
    print("matches/mismatches the strain pattern of the solution ion.")
    print()
    print(f"  {'resin':<14s}  {'fixed group':<22s}  {'counter ion':<12s}  {'use':<16s}")
    resins = [
        ("Strong acid",  "-SO3-",                 "H+ or Na+",   "Cation IC"),
        ("Weak acid",    "-COO-",                 "H+ or Na+",   "soft cations"),
        ("Strong base",  "-N(CH3)3+",             "Cl- or OH-",  "Anion IC"),
        ("Weak base",    "-NH2 / -NHR / -NR2",    "Cl- or OH-",  "weak anions"),
        ("Chelating",    "iminodiacetate",        "H+",          "trace metals"),
    ]
    for r, fg, ci, u in resins:
        print(f"  {r:<14s}  {fg:<22s}  {ci:<12s}  {u:<16s}")
    print()
    print("Selectivity (typical relative affinity at low conc):")
    print("  Cations: Cs+ > Rb+ > K+ > Na+ > Li+   (larger ion -> tighter strain pocket)")
    print("  Anions:  ClO4- > I- > NO3- > Br- > Cl- > F- > OH-")
    print()
    print("Suppressed conductivity detection lowers background, giving LOD")
    print("of 0.1-10 ppb for common inorganic anions (F-, Cl-, NO3-, SO4 2-).")

    # ============================================================
    section(5, "MASS SPECTROMETRY (ionization + analyzer + detector)")
    # ============================================================
    print("MS = (ionize) + (separate by m/z) + (count ions). Substrate reading:")
    print("ionized analyte = a charged substrate strain pattern accelerated")
    print("through E and B fields; the trajectory encodes m/z.")
    print()
    print("Ionization sources:")
    print(f"  {'source':<8s}  {'matrix':<14s}  {'energy':<10s}  {'fragments':<12s}  {'analyte':<14s}")
    ion_src = [
        ("EI",     "vacuum",         "70 eV",     "many",        "GC volatiles"),
        ("CI",     "reagent gas",    "low",       "few",         "GC, soft EI"),
        ("ESI",    "solvent spray",  "very soft", "few/none",    "LC, polar"),
        ("APCI",   "corona disch.",  "soft",      "some",        "LC, mid pol"),
        ("APPI",   "UV photons",     "soft",      "few",         "non-polar"),
        ("MALDI",  "matrix + UV",    "soft",      "few",         "biomol/poly"),
        ("DESI",   "charged spray",  "soft",      "few",         "imaging"),
        ("ICP",    "Ar plasma",      "very hard", "atomic",      "elements"),
    ]
    for s, m, e, f, a in ion_src:
        print(f"  {s:<8s}  {m:<14s}  {e:<10s}  {f:<12s}  {a:<14s}")
    print()
    print("Mass analyzers (substrate trajectories in E/B fields):")
    print(f"  {'analyzer':<12s}  {'principle':<26s}  {'R (FWHM)':<12s}  {'mass acc':<10s}")
    analyzers = [
        ("Quadrupole",  "RF/DC stability",          "1-3 k",       "100 ppm"),
        ("Ion trap",    "RF trap + scan",           "1-4 k",       "100 ppm"),
        ("TOF",         "drift time t = L sqrt(m/2zU)", "10-60 k", "1-5 ppm"),
        ("Q-TOF",       "Q select + TOF",           "20-60 k",     "1-3 ppm"),
        ("Orbitrap",    "axial harmonic in trap",   "60-500 k",    "<1-3 ppm"),
        ("FT-ICR",      "cyclotron in B (7-21 T)",  ">10^6",       "<0.1 ppm"),
        ("Magnetic",    "B-field momentum sep",     "10-100 k",    "1-10 ppm"),
    ]
    for a, p, r, ma in analyzers:
        print(f"  {a:<12s}  {p:<26s}  {r:<12s}  {ma:<10s}")
    print()
    # demo TOF math
    U = 5000.0  # accelerating volts
    L_tof = 1.0  # m drift
    print(f"TOF demo: U = {U} V, drift L = {L_tof} m")
    for mz in (200.0, 500.0, 2000.0):
        m_kg = mz * M_U
        v = math.sqrt(2 * E_CHARGE * U / m_kg)
        t_us = (L_tof / v) * 1e6
        print(f"  m/z = {mz:6.0f}  ->  v = {v:.3e} m/s   t_drift = {t_us:.2f} us")
    print()
    # demo cyclotron
    B_field = 7.0
    print(f"FT-ICR demo: B = {B_field} T")
    for mz in (200.0, 500.0, 2000.0):
        m_kg = mz * M_U
        f_c = E_CHARGE * B_field / (2 * PI * m_kg)
        print(f"  m/z = {mz:6.0f}  ->  f_cyclotron = {f_c/1e3:.1f} kHz")
    print()
    print("EI fragmentation patterns (textbook):")
    print("  Alpha cleavage at heteroatom (N, O, S) -> stable acylium / iminium")
    print("  McLafferty (gamma-H + 6-membered TS) -> radical + neutral alkene")
    print("  Retro-Diels-Alder (cyclohexenes) -> diene + dienophile cations")
    print("  Tropylium (C7H7+, m/z 91) for benzyl groups")
    print("  Acylium (RCO+) for ketones / esters")

    # ============================================================
    section(6, "TANDEM MS (MS/MS) — fragmentation as strain rupture")
    # ============================================================
    print("MS/MS: select a precursor ion (MS1), fragment it in a cell, scan")
    print("the products (MS2). The fragmentation step is where chemical")
    print("structural info comes from. Substrate reading: rupture a chosen")
    print("bond's strain bridge by injecting energy.")
    print()
    print(f"  {'method':<8s}  {'energy source':<26s}  {'spectrum':<22s}  {'use':<14s}")
    msms = [
        ("CID",  "collision with N2/Ar",       "b/y (peptides), even", "small mol"),
        ("HCD",  "higher-energy CID (Orbitrap)","b/y, immonium",       "shotgun prot"),
        ("ETD",  "e- transfer from radical",   "c/z (peptides)",       "PTMs (phos)"),
        ("EThcD","ETD + HCD supplemental",     "c/z + b/y",            "tough peps"),
        ("UVPD", "193 nm photons",             "abcxyz, side chains",  "top-down"),
        ("IRMPD","IR photons (resonant)",      "b/y",                  "FT-MS"),
    ]
    for m, e, sp, u in msms:
        print(f"  {m:<8s}  {e:<26s}  {sp:<22s}  {u:<14s}")
    print()
    print("Acquisition modes:")
    print("  Product ion scan : fix MS1, scan MS2  -> structure of one ion")
    print("  Precursor scan   : scan MS1, fix MS2  -> all parents of a fragment")
    print("  Neutral loss     : MS1 - MS2 = const  -> compounds losing same neutral")
    print("  SRM / MRM        : fix both           -> targeted quant (low LOD)")

    # ============================================================
    section(7, "ELECTROCHEMICAL ANALYSIS")
    # ============================================================
    print("Three-electrode cell: working (W), reference (R), counter (C).")
    print("Substrate reading: applied potential drives charge-carrier strain")
    print("across the W/solution interface; current = ionic strain flux.")
    print()
    print("Cyclic voltammetry (CV): scan E linearly, reverse, plot i vs E.")
    print("  Reversible diagnostic: dE_p = E_pa - E_pc = 59 / n   mV  (25 C)")
    print("  Peak current (Randles-Sevcik):")
    print("    i_p = 2.69e5 n^1.5 A D^0.5 C v^0.5    (in A, units cgs-mixed)")
    print()
    n_e = 1
    A_cm2 = 0.07     # cm^2 (3 mm disk)
    D_cm2s = 7.6e-6  # cm^2/s for ferricyanide
    C_M = 1.0e-3     # mol/L (1 mM)
    v_Vs = 0.1       # V/s
    i_p_A = 2.69e5 * n_e**1.5 * A_cm2 * D_cm2s**0.5 * C_M * v_Vs**0.5
    print(f"  Demo: 1 mM Fe(CN)6^3-, 3-mm GC disk, 100 mV/s")
    print(f"        i_p = {i_p_A*1e6:.2f} uA  (Randles-Sevcik)")
    print(f"        dE_p (n=1) = 59 mV ideal")
    print()
    print(f"  {'technique':<22s}  {'waveform':<26s}  {'LOD (typ)':<12s}  {'use':<14s}")
    echem = [
        ("Cyclic voltammetry",      "linear sweep + reverse",  "1e-5 M",     "mechanism"),
        ("Linear sweep",            "single ramp",             "1e-5 M",     "irreversible"),
        ("Differential pulse (DPV)","staircase + pulse",       "1e-8 M",     "trace anal"),
        ("Square wave (SWV)",       "square + staircase",      "1e-9 M",     "fast trace"),
        ("DC polarography",         "ramp on Hg drop",         "1e-5 M",     "metals"),
        ("Stripping (ASV)",         "deposit then anodic str", "1e-11 M",    "Pb,Cd,Zn,Cu"),
        ("Amperometry",             "fixed E, plot i vs t",    "1e-7 M",     "biosensor"),
        ("Coulometry",              "fixed E, integrate Q",    "100% conv",  "absolute"),
        ("Potentiometry / ISE",     "i=0, measure E vs activity","1e-6 M",   "pH, F-, K+"),
        ("EIS (impedance)",         "AC small signal sweep",   "n/a",        "interfaces"),
    ]
    for t, w, l, u in echem:
        print(f"  {t:<22s}  {w:<26s}  {l:<12s}  {u:<14s}")
    print()
    print("Amperometric biosensors: glucose oxidase + Pt or mediator. Glucose")
    print("oxidation produces H2O2 -> oxidized at +0.6 V vs Ag/AgCl -> i propto C.")
    print("Substrate reading: enzyme template snaps glucose strain pattern into")
    print("an electron-transferable geometry (catalysis chapter).")

    # ============================================================
    section(8, "ATOMIC SPECTROSCOPY (AAS, ICP-OES, ICP-MS)")
    # ============================================================
    print("Atomize sample, then probe the free atoms (or their ions) by")
    print("absorption / emission / mass. Substrate reading: atomic strain")
    print("eigenmodes excited or ionized in a plasma.")
    print()
    print(f"  {'method':<10s}  {'source':<22s}  {'readout':<14s}  {'LOD typical':<14s}")
    atom_spec = [
        ("FAAS",      "air-acetylene flame",   "absorbance",    "ppm to ppb"),
        ("GFAAS",     "graphite furnace",      "absorbance",    "0.01-1 ppb"),
        ("CV-AAS",    "Hg cold vapor",         "absorbance",    "0.001 ppb (Hg)"),
        ("HG-AAS",    "hydride generation",    "absorbance",    "0.01 ppb (As,Se)"),
        ("ICP-OES",   "Ar plasma 6000-10000K", "emission",      "0.1-100 ppb"),
        ("ICP-MS",    "Ar plasma -> MS",       "ion count",     "0.001-1 ppt"),
        ("HR-ICP-MS", "magnetic-sector ICP",   "ion count",     "0.0001 ppt"),
        ("XRF",       "X-ray fluorescence",    "emission",      "ppm (bulk)"),
    ]
    for m, s, r, l in atom_spec:
        print(f"  {m:<10s}  {s:<22s}  {r:<14s}  {l:<14s}")
    print()
    print("ICP-MS detection limit advantage:")
    print("  At plasma 7500 K, k_B T / h_nu ~ 0.1 -> high ionization fraction for")
    print("  IP < 8 eV elements -> nearly all atoms become single ions countable")
    print("  in TOF/Q analyzer. Background ~ 1 cps -> ppt sensitivity.")
    print()
    print("Common interferences (ICP-MS, low-resolution):")
    print("  40Ar16O on 56Fe       -> use H2/He cell or HR-MS")
    print("  40Ar40Ar on 80Se      -> use H2 cell")
    print("  35Cl16O on 51V        -> matrix-match or HR")
    print("  138Ba2+ on 69Ga       -> doubly charged ion")

    # ============================================================
    section(9, "TITRATIONS, GRAVIMETRY, VOLUMETRIC ANALYSIS")
    # ============================================================
    print("Classical wet methods: stoichiometric reaction to a sharp endpoint.")
    print("Substrate reading: stoichiometric saturation = strain-bridge")
    print("balance reached (cap sigma <= 1/2 enforces 1:1, 1:2 etc).")
    print()
    print("Titration types:")
    print(f"  {'type':<18s}  {'reaction':<26s}  {'endpoint':<22s}")
    titr = [
        ("Acid-base",        "H+ + OH- -> H2O",           "indicator / pH meter"),
        ("Redox",            "ox + ne- -> red",           "Pt potential / colour"),
        ("Complexometric",   "Mn+ + EDTA -> [M-EDTA]",    "EBT / ISE"),
        ("Precipitation",    "Ag+ + Cl- -> AgCl(s)",      "Mohr / Volhard / Fajans"),
        ("Karl Fischer",     "I2 + SO2 + H2O -> 2HI+SO3", "biamperometric"),
        ("Non-aqueous",      "weak acid in HClO4/AcOH",   "potentiometric"),
    ]
    for t, r, e in titr:
        print(f"  {t:<18s}  {r:<26s}  {e:<22s}")
    print()
    print("Gravimetry: weigh a precipitate of known stoichiometry.")
    print("  Example: SO4 2- as BaSO4 (M = 233.39 g/mol) ->")
    print("    mass ratio SO4/BaSO4 = 96.06/233.39 = 0.4116")
    print("  Modern role: very accurate for one analyte, slow, niche.")
    print()
    print("Volumetric glass class A (NIST/ISO):")
    print("  burette 50 mL +/- 0.05 mL  (0.10 percent)")
    print("  pipette 25 mL +/- 0.03 mL  (0.12 percent)")
    print("  vol flask 1 L +/- 0.40 mL  (0.04 percent)")

    # ============================================================
    section(10, "CALIBRATION, LOD / LOQ, METHOD VALIDATION (ISO/ICH)")
    # ============================================================
    print("Calibration model (linear, typical):")
    print("  Signal y = m C + b ;  fit by least squares; report R^2, residuals.")
    print()
    print("Detection / quantitation limits (3-sigma / 10-sigma, IUPAC):")
    print("  LOD = 3 s_blank / m       (or 3.3 s_y/m via residuals)")
    print("  LOQ = 10 s_blank / m")
    print()
    s_blank = 0.20    # signal units
    slope = 50.0      # signal / (mg/L)
    LOD = 3 * s_blank / slope
    LOQ = 10 * s_blank / slope
    print(f"  Demo: s_blank = {s_blank}, slope = {slope}/(mg/L)")
    print(f"        LOD = {LOD*1e3:.2f} ug/L      LOQ = {LOQ*1e3:.2f} ug/L")
    print()
    print("Validation parameters (ICH Q2(R1), ISO 17025):")
    print(f"  {'parameter':<14s}  {'definition':<46s}  {'criterion':<10s}")
    val = [
        ("Specificity", "no co-elution / interference",                  "qualitative"),
        ("Linearity",   "y = mC+b over working range",                   "R^2 > 0.999"),
        ("Range",       "LOQ to upper linear limit",                     "covers spec"),
        ("Accuracy",    "recovery vs reference",                         "98-102%"),
        ("Precision",   "RSD of replicate measurements",                 "RSD < 2%"),
        ("LOD / LOQ",   "lowest C reliably detected / quantified",       "see above"),
        ("Robustness",  "invariance to small method changes",            "qualitative"),
        ("Stability",   "sample / std hold time vs response",            "drift < 5%"),
    ]
    for p, d, c in val:
        print(f"  {p:<14s}  {d:<46s}  {c:<10s}")
    print()
    print("Substrate framing: validation = mapping the operating window in")
    print("which the strain-bridge response stays linear and reproducible.")
    print("Outside that window, saturation (sigma->1/2) curls the calibration.")

    # ============================================================
    section(11, "SAMPLE PREPARATION (SPE, derivatization, digestion)")
    # ============================================================
    print("Real samples need cleanup BEFORE analysis. Substrate framing:")
    print("preparation = pre-selecting the analyte's strain pattern from a")
    print("noisy matrix, by retaining it on a templated phase or chemically")
    print("converting it to a more measurable form.")
    print()
    print("Solid-phase extraction (SPE) sorbents:")
    print(f"  {'sorbent':<12s}  {'chemistry':<22s}  {'analyte':<20s}")
    spe = [
        ("C18",       "octadecyl silica",        "non-polar organics"),
        ("HLB",       "hydrophilic-lipophilic",  "broad range"),
        ("MCX",       "mixed-mode cation",       "basic drugs"),
        ("MAX",       "mixed-mode anion",        "acidic drugs"),
        ("Florisil",  "MgSilicate",              "pesticides cleanup"),
        ("Alumina",   "Al2O3 (acidic/basic)",    "pigments / vitamins"),
        ("Silica",    "bare SiO2",               "polar from non-polar"),
        ("MIP",       "molecular-imprint poly",  "templated single target"),
    ]
    for s, c, a in spe:
        print(f"  {s:<12s}  {c:<22s}  {a:<20s}")
    print()
    print("Common derivatization reagents:")
    print(f"  {'reagent':<10s}  {'reacts with':<18s}  {'product':<20s}  {'use':<10s}")
    deriv = [
        ("BSTFA",     "OH, NH, COOH",   "TMS ether/amide",  "GC-MS"),
        ("MSTFA",     "OH, NH, COOH",   "TMS ether/amide",  "GC-MS"),
        ("PFBBr",     "COOH, phenols",  "PFB ester",        "GC-ECD"),
        ("Dansyl-Cl", "amines",         "fluor sulfonamide", "HPLC-fluo"),
        ("OPA",       "primary amines", "isoindole",         "HPLC-fluo"),
        ("FMOC-Cl",   "amines",         "FMOC carbamate",   "HPLC-UV/fluo"),
        ("DNPH",      "carbonyls",      "hydrazone",        "HPLC-UV"),
        ("PITC",      "amino acids",    "PTC-AA",           "HPLC-UV"),
    ]
    for r, w, p, u in deriv:
        print(f"  {r:<10s}  {w:<18s}  {p:<20s}  {u:<10s}")
    print()
    print("Microwave-assisted acid digestion (for ICP-OES / ICP-MS):")
    print("  HNO3 + H2O2 (or HF for silicates), sealed PTFE vessels, 200 C,")
    print("  10-30 min. Total dissolution; trace elements preserved; no fume hood.")
    print()
    print("Other techniques: QuEChERS (pesticides in food), liquid-liquid")
    print("extraction (LLE), SPME (solid-phase micro-extraction), dialysis,")
    print("ultrafiltration, lyophilization, headspace (for volatiles).")

    # ============================================================
    section(12, "SUMMARY: one strain-bridge, eight detector geometries")
    # ============================================================
    print("Every analytical technique above reduces to two substrate primitives:")
    print()
    print("  1. SEPARATION  =  differential strain-bridge formation between")
    print("                    analyte and stationary phase (or field gradient).")
    print("  2. DETECTION   =  readout of an excited / ionized / oxidized")
    print("                    substrate strain pattern via coupling to a")
    print("                    measurable observable (current, photon, ion).")
    print()
    print("Configuration -> technique:")
    print("  partition between liquid-gas phases    -> GC")
    print("  partition between liquid-liquid phases -> HPLC")
    print("  charge-pocket affinity                 -> IC / IEX")
    print("  size-pore exclusion                    -> SEC")
    print("  E/B trajectory of charged strain       -> MS analyzer")
    print("  potential-driven interfacial flux      -> CV / SWV / amperometry")
    print("  plasma-excited atomic eigenmode        -> ICP-OES / ICP-MS")
    print("  resonant photon absorption             -> AAS / IR / UV-Vis")
    print("  stoichiometric saturation              -> titration / gravimetry")
    print()
    print("Honest scoreboard: substrate REPRODUCES standard analytical numbers")
    print("(LOD ppt-ppb, mass accuracy < 1 ppm, R 1.5 baseline) — it does")
    print("not replace them. The value-add is that all separation principles")
    print("and all detector geometries collapse to one strain-bridge story")
    print("rather than ten unrelated empirical chapters.")


if __name__ == "__main__":
    main()
