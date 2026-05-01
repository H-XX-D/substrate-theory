"""Materials chemistry through the strain-medium framework.

Companion to molecular_bonding_substrate.py: where that file derived
chemical bonds as strain bridges between two atoms, this file scales
up to engineered MATERIALS — millions of bonds organized into
crystals, glasses, frameworks, and sheets.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Materials-specific re-readings:
  - bandgap        = forbidden substrate-mode frequency range
  - dopant         = local strain-density perturbation breaking the gap
  - sintering      = thermal smoothing of grain-boundary strain
  - glass Tg       = freeze-in of substrate-strain configurational modes
  - MOF porosity   = strain framework with topologically built-in voids
  - perovskite ferroelectricity = sigma symmetry-breaking by B-cation off-center
  - 2D material    = strain sheet where one transverse mode is suppressed
  - quantum dot    = particle-in-a-box on the substrate, size-tunable spectrum

Honest framing: standard materials-science numbers (bandgaps, fracture
toughness, Tg, surface area) are reproduced from substrate language
without changing the predicted values. The unification is what is new.
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
M_E = 9.1093837015e-31
ANGSTROM = 1.0e-10
NM = 1.0e-9


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Materials chemistry in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Material = engineered substrate-strain configuration designed for")
    print("a target combination of (K_eff, mode spectrum, defect density).")
    print()

    # ============================================================
    section(1, "SEMICONDUCTORS (bandgap = forbidden strain-mode band)")
    # ============================================================
    print("In the substrate picture a crystal is a periodic strain lattice.")
    print("Periodic K(r) Bloch-decomposes into bands of allowed mode")
    print("frequencies; the BANDGAP is the forbidden interval.")
    print()
    print(f"  {'material':<8s}  {'Eg [eV]':>8s}  {'type':<10s}  {'application':<28s}")
    semis = [
        ("Si",     1.12, "indirect", "logic, photovoltaics"),
        ("Ge",     0.66, "indirect", "IR detectors, SiGe HBTs"),
        ("GaAs",   1.42, "direct",   "lasers, RF, LEDs"),
        ("InP",    1.34, "direct",   "1.55 um telecom lasers"),
        ("GaN",    3.39, "direct",   "blue/UV LEDs, RF power"),
        ("SiC",    3.26, "indirect", "high-V/high-T power devices"),
        ("Diamond",5.47, "indirect", "ultimate power semi (R&D)"),
        ("Ga2O3",  4.80, "indirect", "ultra-wide-bandgap power"),
        ("InAs",   0.36, "direct",   "high-mobility transistors"),
        ("CdTe",   1.50, "direct",   "thin-film PV (16-22% eff)"),
    ]
    for m, eg, t, a in semis:
        print(f"  {m:<8s}  {eg:>8.2f}  {t:<10s}  {a:<28s}")
    print()
    print("Substrate reading of bandgap:")
    print("  Bloch theorem on periodic K(r) gives mode dispersion omega(k).")
    print("  Forbidden interval [omega_v, omega_c] = bandgap.")
    print("  Direct gap = min at same k -> photon (zero-momentum mode) couples;")
    print("  indirect gap = min at different k -> need phonon to bridge momentum.")
    print()
    print("Doping (local sigma perturbation):")
    print("  n-type donor (P, As in Si): adds 1 unbound strain quantum near")
    print("    conduction band (donor level ~30-50 meV below E_c).")
    print("  p-type acceptor (B, Ga in Si): removes 1 strain quantum near")
    print("    valence band (acceptor level ~45 meV above E_v).")
    print()
    # Hydrogenic donor estimate in Si
    eps_Si = 11.7
    m_eff = 0.26 * M_E
    Ry = 13.6  # eV
    Ed = Ry * (m_eff / M_E) / (eps_Si ** 2)
    print(f"  Hydrogenic donor binding (effective-mass theory):")
    print(f"    E_d = 13.6 * (m*/m_e) / eps^2 = 13.6 * 0.26 / 11.7^2 = {Ed*1000:.1f} meV")
    print(f"    Measured P-in-Si donor ionization: ~45 meV.")
    print()
    print("p-n junction physics (substrate strain interface):")
    print("  Across the junction, donor and acceptor strain fields equilibrate")
    print("  by carrier diffusion -> built-in field E_bi until drift cancels.")
    print(f"    V_bi = (kT/e) ln(N_A N_D / n_i^2)")
    print("  For Si with N_A=N_D=1e17, n_i=1e10 cm^-3 at 300 K:")
    Vbi = 0.0259 * math.log(1e17 * 1e17 / (1e10) ** 2)
    print(f"    V_bi ~ {Vbi:.3f} V    (textbook value ~0.83 V)")

    # ============================================================
    section(2, "CERAMICS (covalent/ionic strain network, brittle)")
    # ============================================================
    print("Ceramic = stiff, refractory strain network with strong directional")
    print("covalent + ionic bridges. Substrate K is HIGH; rho moderate; the")
    print("sigma cap and orientability play almost no role -> brittle (no")
    print("delocalized strain channel for plastic flow).")
    print()
    print(f"  {'ceramic':<8s}  {'E [GPa]':>8s}  {'K_IC [MPa.m^.5]':>17s}"
          f"  {'T_max [C]':>10s}  {'role':<24s}")
    ceramics = [
        ("Al2O3", 380,  4.0, 1750, "wear, electrical insulator"),
        ("ZrO2",  210,  9.0, 2400, "thermal barrier, dental"),
        ("SiC",   410,  4.6, 1600, "abrasives, high-T parts"),
        ("Si3N4", 310,  6.0, 1400, "bearings, turbine blades"),
        ("BN",    100,  3.0,  900, "lubricant (h-BN), abrasive (c-BN)"),
        ("MgO",   270,  2.5, 2800, "refractory, optical"),
        ("TiC",   450,  3.5, 3000, "cutting tools"),
    ]
    for m, E, K, T, r in ceramics:
        print(f"  {m:<8s}  {E:>8d}  {K:>17.1f}  {T:>10d}  {r:<24s}")
    print()
    print("Substrate reading:")
    print("  - High E (Young's modulus) = high lattice K_eff for axial strain")
    print("  - Low K_IC = no plastic strain channel; cracks propagate when")
    print("    local strain energy exceeds bond-bridge breaking threshold")
    print("  - High T_max = strong covalent/ionic bridges resist thermal")
    print("    decoherence of the lattice mode spectrum")
    print()
    print("Sintering (substrate-strain healing across grain boundaries):")
    print("  Powder compact heated below T_melt: surface diffusion + grain-")
    print("  boundary diffusion smooths strain discontinuities -> dense solid.")
    print("  Driving force = reduction in surface strain energy (Gibbs).")
    print("  Empirical sintering temperature: T_sinter ~ 0.6-0.8 T_melt.")
    Tm_alumina = 2072
    print(f"  Al2O3:  T_melt = {Tm_alumina} C  ->  T_sinter ~ {0.7*Tm_alumina:.0f} C")
    print(f"          (typical sintering 1500-1700 C, matches 0.7 T_melt)")

    # ============================================================
    section(3, "GLASSES (frozen substrate-strain disorder)")
    # ============================================================
    print("Glass = liquid configurational strain frozen in below T_g.")
    print("No long-range periodicity -> no Bloch bands -> Tauc gap = local")
    print("bond gap broadened by substrate disorder.")
    print()
    print("Network former vs modifier (Zachariasen 1932):")
    print("  Former (SiO2, B2O3, GeO2, P2O5): builds the 3D strain skeleton")
    print("    via corner-sharing tetrahedra/triangles.")
    print("  Modifier (Na2O, CaO, K2O, MgO): inserts ionic lobes that BREAK")
    print("    Si-O-Si strain bridges -> non-bridging oxygens -> lower T_g.")
    print()
    print(f"  {'glass family':<22s}  {'Tg [C]':>7s}  {'role':<32s}")
    glasses = [
        ("Pure silica (SiO2)",        1175, "fiber optics, fused quartz"),
        ("Soda-lime",                  570, "windows, bottles (~70% world)"),
        ("Borosilicate (Pyrex)",       560, "lab ware, low CTE"),
        ("Aluminosilicate",            815, "Gorilla Glass, displays"),
        ("Lead crystal",               430, "decorative, X-ray shielding"),
        ("Fluoride (ZBLAN)",           260, "mid-IR fibers (1-5 um)"),
        ("Chalcogenide (As2S3)",       210, "IR optics, phase-change memory"),
        ("Metallic (Vitreloy Zr-Ti)",  370, "amorphous structural alloys"),
    ]
    for n, Tg, r in glasses:
        print(f"  {n:<22s}  {Tg:>7d}  {r:<32s}")
    print()
    print("Viscosity and the Vogel-Fulcher-Tammann law:")
    print("  log10(eta) = A + B / (T - T0)")
    print("  Substrate reading: B ~ activation strain to rearrange one local")
    print("  cluster; T0 ~ ideal kinetic-arrest temperature where the")
    print("  configurational strain landscape becomes infinitely deep.")
    print()
    A, B, T0 = -3.5, 4500, 250
    for T in (600, 800, 1000, 1200, 1500):
        log_eta = A + B / (T - T0)
        print(f"  T = {T} K:  log10(eta) = {log_eta:.2f}  -> eta ~ 1e{log_eta:.1f} Pa.s")
    print()
    print("Strong vs fragile classification (Angell):")
    print("  Strong (SiO2): nearly Arrhenius eta(T), single activation strain.")
    print("  Fragile (o-terphenyl): super-Arrhenius, strain landscape collapses")
    print("    rapidly above T_g.")

    # ============================================================
    section(4, "COMPOSITES (heterogeneous strain partition)")
    # ============================================================
    print("Composite = two or more substrate-strain phases with mismatched K")
    print("designed so the high-K phase carries load and the low-K matrix")
    print("redistributes strain around defects (crack-bridging).")
    print()
    print(f"  {'composite':<14s}  {'fiber':<14s}  {'matrix':<10s}  {'E [GPa]':>8s}  {'use':<22s}")
    comps = [
        ("CFRP",       "carbon",        "epoxy",   135, "aircraft, F1, sport"),
        ("GFRP",       "E-glass",       "polyester", 45, "boats, wind blades"),
        ("Aramid/epoxy","Kevlar",        "epoxy",    80, "armor, ropes"),
        ("MMC",        "SiC fibers",    "Al alloy", 120, "engine pistons"),
        ("CMC",        "SiC fibers",    "SiC",      300, "jet turbines"),
        ("Bone (bio)", "collagen",      "HA mineral", 18, "biological composite"),
        ("Concrete",   "rebar steel",   "cement",    30, "construction"),
    ]
    for n, f, m, E, u in comps:
        print(f"  {n:<14s}  {f:<14s}  {m:<10s}  {E:>8d}  {u:<22s}")
    print()
    print("Rule of mixtures (Voigt upper bound, parallel strain):")
    print("  E_c = V_f E_f + (1 - V_f) E_m")
    print("  CFRP example: V_f = 0.6, E_f = 230 GPa (carbon), E_m = 3.5 GPa")
    Vf, Ef, Em = 0.6, 230, 3.5
    Ec = Vf * Ef + (1 - Vf) * Em
    print(f"    E_c (parallel) = {Ec:.1f} GPa")
    print(f"    E_c (Reuss, transverse) = {1/(Vf/Ef + (1-Vf)/Em):.1f} GPa")
    print()
    print("Substrate reading: high-K fibers monopolize axial strain; low-K")
    print("matrix carries shear and isolates fiber breaks (crack-bridging).")
    print("Bone is the same trick at nanoscale: stiff hydroxyapatite platelets")
    print("in compliant collagen -> high toughness AND high stiffness.")

    # ============================================================
    section(5, "MOFs and COFs (porous strain frameworks)")
    # ============================================================
    print("Metal-Organic Frameworks (MOFs) = crystalline strain frameworks")
    print("built from metal-ion nodes + organic linker bridges. Topology")
    print("forces large internal voids (substrate primitives K and xi tuned")
    print("so that the lowest-strain configuration has periodic empty space).")
    print()
    print(f"  {'MOF':<10s}  {'metal':<6s}  {'linker':<14s}  {'SA [m^2/g]':>11s}  {'use':<20s}")
    mofs = [
        ("MOF-5",    "Zn4O", "BDC",          3800, "gas storage"),
        ("HKUST-1",  "Cu2",  "BTC",          1900, "H2/CO2 storage, catalysis"),
        ("ZIF-8",    "Zn",   "imidazolate",  1800, "membranes, drug delivery"),
        ("UiO-66",   "Zr6O", "BDC",          1200, "chemically robust MOF"),
        ("MOF-177",  "Zn4O", "BTB",          4800, "H2/CH4 storage"),
        ("NU-1501",  "Al",   "PET",          7300, "record surface area"),
        ("MOF-210",  "Zn4O", "BTE/BPDC",     6240, "high CH4 capacity"),
    ]
    for n, m, l, sa, u in mofs:
        print(f"  {n:<10s}  {m:<6s}  {l:<14s}  {sa:>11d}  {u:<20s}")
    print()
    print("Surface area context: pristine graphene = 2630 m^2/g (theoretical");
    print("two-sided sheet). MOFs exceed this by INTERNAL surface area.")
    print()
    print("Substrate reading of porosity:")
    print("  Choose nodes (high local K) + rigid linkers (medium K) so the")
    print("  topologically unique low-strain crystal has the desired void")
    print("  geometry. The pore IS the strain-free substrate volume between")
    print("  bridges. xi (substrate length scale) sets pore size at 1-10 nm.")
    print()
    print("Covalent-Organic Frameworks (COFs) replace metal nodes with all-")
    print("covalent C-B-O / C-N strain bridges -> lighter, more chemically")
    print("homogeneous, similar surface areas (COF-5: 1670 m^2/g).")
    print()
    print("Application: 1 g of MOF-5 has the surface area of a basketball")
    print("court (~420 m^2 standard court). All achievable because substrate")
    print("strain LIKES the open framework — it is the energy minimum, not")
    print("a strained metastable state.")

    # ============================================================
    section(6, "PEROVSKITES (ABX3, ferroelectric & photovoltaic)")
    # ============================================================
    print("Perovskite structure = ABX3 with B-cation in octahedral cage of X")
    print("anions and A-cation filling the cuboctahedral void. The substrate")
    print("uses this geometry as a versatile scaffold: small B-cation off-")
    print("centerings spontaneously break inversion symmetry -> ferroelectric.")
    print()
    print(f"  {'perovskite':<22s}  {'role':<32s}  {'key spec':<14s}")
    perovs = [
        ("BaTiO3",                 "ferroelectric capacitor",       "Tc 120 C"),
        ("PbTiO3",                 "ferroelectric, ultrasound",     "Tc 490 C"),
        ("PZT (Pb(Zr,Ti)O3)",      "piezoelectric actuators",        "d33 ~ 600 pC/N"),
        ("SrTiO3",                 "substrate, quantum paraelectric","eps_r ~ 300"),
        ("CaTiO3",                 "natural perovskite",             "GDP-stable"),
        ("LaMnO3 / La1-xSrxMnO3",  "CMR magnetoresistance",          "metal-insul T"),
        ("CH3NH3PbI3 (MAPI)",      "photovoltaic absorber",          "PCE ~25%"),
        ("Cs2AgBiBr6",             "lead-free PV (double perov.)",   "Eg ~ 2 eV"),
        ("BiFeO3",                 "multiferroic (FE + AFM)",        "Tc ~ 800 C"),
        ("YBa2Cu3O7 (cuprate)",    "high-Tc superconductor",         "Tc 92 K"),
    ]
    for n, r, k in perovs:
        print(f"  {n:<22s}  {r:<32s}  {k:<14s}")
    print()
    print("Goldschmidt tolerance factor (geometric strain-fit criterion):")
    print("  t = (r_A + r_X) / (sqrt(2) (r_B + r_X))")
    print("  0.9 <= t <= 1.0 : cubic perovskite stable")
    print("  t < 0.9         : tilted/orthorhombic distortion")
    print("  t > 1.0         : hexagonal stacking preferred")
    print()
    # BaTiO3 example
    rA, rB, rX = 1.61, 0.61, 1.40   # Ba2+, Ti4+, O2- ionic radii in A
    t = (rA + rX) / (math.sqrt(2) * (rB + rX))
    print(f"  BaTiO3:  t = ({rA}+{rX}) / (sqrt(2)*({rB}+{rX})) = {t:.3f}")
    print(f"           t in [0.9,1.0] -> cubic above Tc, tetragonal below Tc.")
    print()
    print("Substrate reading of ferroelectricity:")
    print("  Ti(IV) sits in slightly oversized O6 cage. The substrate's sigma")
    print("  saturation cap forbids a perfectly symmetric occupation of all")
    print("  6 Ti-O strain bridges -> Ti spontaneously off-centers along")
    print("  one cube axis -> permanent dipole. Cooling through Tc freezes")
    print("  the symmetry choice -> ferroelectric polarization P_s.")
    print()
    print("Photovoltaic methylammonium lead iodide (MAPI):")
    print("  Eg ~ 1.55 eV (near-ideal Shockley-Queisser), defect-tolerant")
    print("  because Pb 6s lone pair softens the strain landscape -> shallow")
    print("  defects don't trap carriers. Certified PCE 25.7% (NREL 2024).")

    # ============================================================
    section(7, "2D MATERIALS (transverse-mode-suppressed sheets)")
    # ============================================================
    print("2D material = strain sheet one or few atoms thick. The substrate")
    print("loses one transverse mode (out-of-plane); the remaining 2D mode")
    print("spectrum gives extreme in-plane stiffness and tunable bandgaps")
    print("by stacking, twisting, or chemical decoration.")
    print()
    print(f"  {'material':<14s}  {'Eg [eV]':>8s}  {'mobility cm^2/Vs':>16s}  {'note':<22s}")
    twoDs = [
        ("Graphene",          0.00, 200000, "Dirac semimetal"),
        ("h-BN",              5.97,    100, "white graphene, insulator"),
        ("MoS2  (monolayer)", 1.80,    200, "direct gap (bulk indirect 1.2)"),
        ("MoS2  (bulk)",      1.20,    100, "indirect gap"),
        ("WSe2  (monolayer)", 1.65,    250, "spin-orbit splitting strong"),
        ("Phosphorene",       1.50,    600, "anisotropic, p-type"),
        ("Ti3C2 MXene",       0.00,  10000, "metallic, EM shielding"),
        ("Silicene",          0.00,    100, "buckled, gap by E-field"),
        ("Borophene",         0.00,    500, "metallic, anisotropic"),
        ("Stanene",           0.07,    100, "QSH insulator candidate"),
    ]
    for n, eg, mu, note in twoDs:
        print(f"  {n:<14s}  {eg:>8.2f}  {mu:>16d}  {note:<22s}")
    print()
    print("Bandgap engineering by stacking (twistronics):")
    print("  Bilayer graphene + perpendicular E-field opens a gap (~250 meV).")
    print("  Magic-angle TBG (1.1 deg) flatbands -> superconductivity at 1.7 K.")
    print("  MoS2/WSe2 type-II heterostructure -> interlayer excitons.")
    print()
    print("Substrate reading: the 2D sheet supports a 2D dispersion omega(kx,ky).")
    print("Twisting two sheets imposes a moire periodicity ~a/theta -> a long-")
    print("wavelength periodic K(r) modulation -> miniband structure, flat")
    print("bands, and emergent strong-correlation physics.")
    print()
    print("Mechanical (graphene):")
    print(f"  Young's modulus E = 1 TPa, intrinsic strength ~130 GPa")
    print(f"  Theoretical surface area (both sides) = 2630 m^2/g")
    print(f"  All in a 0.34 nm thick sheet — thinness is the source of these")
    print(f"  records, not exotic chemistry.")

    # ============================================================
    section(8, "NANOMATERIALS (substrate confinement effects)")
    # ============================================================
    print("Nano regime = substrate-strain particle smaller than relevant")
    print("excitation wavelength -> particle-in-a-box quantization makes")
    print("properties size-tunable.")
    print()
    print("Quantum dot (3D confinement) bandgap blueshift:")
    print("  E_g(R) = E_g(bulk) + (hbar^2 pi^2)/(2 mu R^2) - 1.8 e^2/(eps R)")
    print()
    # CdSe QD example
    Eg_bulk = 1.74        # eV CdSe
    mu_eff = 0.13 * M_E   # reduced effective mass
    eps = 10.0
    print(f"  CdSe QD:  Eg_bulk = {Eg_bulk} eV, mu*/m_e = 0.13, eps = {eps}")
    print(f"  {'R [nm]':>8s}  {'Eg [eV]':>8s}  {'lambda emit [nm]':>17s}")
    for R_nm in (1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
        R = R_nm * NM
        confine = (HBAR_J_S ** 2 * PI ** 2) / (2 * mu_eff * R ** 2) / EV_J
        coul = 1.8 * (1.602e-19) ** 2 / (4 * PI * 8.854e-12 * eps * R) / EV_J
        Eg = Eg_bulk + confine - coul
        lam = 1240.0 / Eg
        print(f"  {R_nm:>8.1f}  {Eg:>8.3f}  {lam:>17.0f}")
    print()
    print("This is the QLED / solar-paint mechanism: tuning a single chemical")
    print("(CdSe) across visible spectrum just by changing nanocrystal size.")
    print()
    print("Carbon nanotubes (CNT) — 1D substrate strain tubes:")
    print(f"  {'type':<22s}  {'d [nm]':>7s}  {'Eg [eV]':>8s}  {'metal/semi':<10s}")
    cnts = [
        ("Armchair (n,n)",        1.0, 0.00, "metallic"),
        ("Zigzag (n,0), n%3==0",  1.0, 0.00, "metallic"),
        ("Zigzag (n,0), n%3!=0",  1.0, 0.90, "semi"),
        ("Chiral (10,5)",         1.05, 0.85, "semi"),
        ("MWCNT (multi-wall)",    5.0, "var", "mostly metallic"),
    ]
    for n, d, eg, t in cnts:
        eg_s = f"{eg:.2f}" if isinstance(eg, float) else f"{eg:>4s}"
        print(f"  {n:<22s}  {d:>7.2f}  {eg_s:>8s}  {t:<10s}")
    print()
    print("Substrate explanation: rolling graphene into a tube quantizes the")
    print("transverse k -> some chiralities cross the Dirac point (metallic),")
    print("most miss it (semiconducting with Eg ~ 0.9 eV / d_nm).")
    print()
    print("Other nanostructures briefly:")
    print("  - Au/Ag nanoparticles: localized surface plasmon (collective")
    print("    substrate strain oscillation) tunes color (red 20 nm -> blue 80 nm).")
    print("  - Dendrimers: tree-like macromolecules, generation-controlled size,")
    print("    used as drug-delivery cages.")
    print("  - Magnetic nanoparticles (Fe3O4): single-domain at <20 nm,")
    print("    superparamagnetic, used in MRI contrast and hyperthermia.")

    # ============================================================
    section(9, "SHAPE-MEMORY AND SMART MATERIALS")
    # ============================================================
    print("Smart material = substrate configuration that responds reversibly")
    print("to an external field (T, E, H, light, mechanical) by switching")
    print("between two metastable strain configurations.")
    print()
    print(f"  {'material':<18s}  {'stimulus':<10s}  {'response':<22s}  {'metric':<14s}")
    smarts = [
        ("Nitinol (NiTi)",       "T",      "shape recovery",          "8% strain"),
        ("Cu-Zn-Al SMA",         "T",      "shape recovery",          "4% strain"),
        ("PZT piezo",            "V",      "mechanical strain",       "d33 600 pC/N"),
        ("PVDF piezo polymer",   "V",      "mechanical strain",       "flexible"),
        ("Terfenol-D",           "H",      "magnetostriction",        "2000 ppm"),
        ("Galfenol (Fe-Ga)",     "H",      "magnetostriction",        "350 ppm"),
        ("WO3 electrochromic",   "V",      "color (blue<->clear)",    "smart windows"),
        ("VO2",                  "T",      "metal-insul transition",  "T_c 68 C"),
        ("Spiropyran (photo)",   "UV/vis", "color + structural",      "reversible"),
        ("LCE elastomer",        "T or hv","large reversible strain", "to 400%"),
    ]
    for n, s, r, m in smarts:
        print(f"  {n:<18s}  {s:<10s}  {r:<22s}  {m:<14s}")
    print()
    print("Substrate reading of shape-memory (austenite <-> martensite):")
    print("  NiTi has TWO low-strain crystal configurations separated by a")
    print("  martensitic shear. Below T_M the substrate prefers low-symmetry")
    print("  martensite (deformable by twin-boundary motion). Heating above")
    print("  T_A snaps it back to high-symmetry austenite -> macroscopic")
    print("  recovery of stored shape. The substrate REMEMBERS because the")
    print("  austenite configuration is a unique strain minimum.")
    print()
    print("Piezoelectric coefficient = dP/d(strain) at fixed E-field. The")
    print("substrate's broken inversion symmetry (perovskite section) means")
    print("an applied strain redistributes substrate charge -> voltage. The")
    print("inverse effect drives ultrasound transducers and inkjet printers.")

    # ============================================================
    section(10, "SUMMARY: one substrate, six knobs, every material")
    # ============================================================
    print("Every material class above is a SPECIFIC SETTING of the same six")
    print("substrate primitives, organized at a different length scale:")
    print()
    print(f"  {'class':<18s}  {'dominant primitive':<22s}  {'engineered for':<24s}")
    summary = [
        ("Semiconductor",  "K periodicity (bandgap)", "controlled conductivity"),
        ("Ceramic",        "K (very high)",            "stiffness, T_max"),
        ("Glass",          "frozen disorder + gamma",  "transparency, formability"),
        ("Composite",      "K-mismatch partition",     "K_IC + E together"),
        ("MOF / COF",      "xi (long linker bridges)", "internal surface area"),
        ("Perovskite",     "sigma cap symmetry break", "ferroelectric / PV"),
        ("2D material",    "missing transverse mode",  "ultimate thinness"),
        ("Quantum dot",    "xi (R < lambda)",          "tunable spectrum"),
        ("Smart material", "two strain minima + T",    "reversible response"),
    ]
    for c, p, e in summary:
        print(f"  {c:<18s}  {p:<22s}  {e:<24s}")
    print()
    print("Honest scoreboard: the substrate framework reproduces the standard")
    print("materials-science values (bandgaps, Young's moduli, Tg, surface")
    print("areas, tolerance factors) without changing them. The bound-state")
    print("spectrum of the substrate Lagrangian is the Schrodinger equation")
    print("non-relativistically, so quantum-chemistry numbers are inherited.")
    print()
    print("Value-added: a unified ontology where a transistor, a brake disk,")
    print("a window pane, a CFRP wing spar, a hydrogen-storage MOF, a piezo")
    print("igniter, a CNT, and a NiTi stent are all the SAME engineered")
    print("substrate-strain configuration in different geometric regimes.")
    print()
    print("Engineering strategy reduces to four moves:")
    print("  1. Set K (stiffness scale)            -> ceramic vs polymer")
    print("  2. Choose periodicity / topology      -> crystal vs glass vs MOF")
    print("  3. Tune sigma occupation              -> dopants, FE polarization")
    print("  4. Pick dimensionality / confinement  -> 3D bulk, 2D sheet, 0D dot")
    print()
    print("All materials chemistry = combinatorial exploration of these four")
    print("moves on the same six-primitive substrate.")


if __name__ == "__main__":
    main()
