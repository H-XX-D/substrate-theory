"""Crystallography and solid-state chemistry through the strain-medium framework.

Crystals = periodic substrate-strain patterns.  Defects = topological strain
singularities.  Phase transitions = substrate-strain reorganization events.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Atoms occupy minima of the periodic substrate-strain potential.  The discrete
translation symmetry of a crystal is the SYMMETRY OF THE STRAIN GROUND STATE,
not an external scaffold imposed on top of matter.

Honest framing: substrate REPRODUCES standard crystallography (Bragg's law,
230 space groups, Madelung sums) - the value-add is unification of crystals,
defects, and phase transitions as one strain-pattern story.
"""

from __future__ import annotations
import math


PI = math.pi
HBAR_J_S = 1.054571817e-34
C_M_S = 2.998e8
EV_J = 1.602176634e-19
K_B = 1.380649e-23
N_A = 6.02214076e23
ANGSTROM = 1.0e-10
EPS0 = 8.8541878128e-12


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Crystallography and solid-state chemistry in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Crystal      = periodic minimum of substrate strain potential V(u)")
    print("Defect       = topological singularity in the strain field")
    print("Phase trans. = reorganization of the strain ground state")
    print()

    # ============================================================
    section(1, "14 BRAVAIS LATTICES & 7 CRYSTAL SYSTEMS")
    # ============================================================
    print("Substrate principle: a crystal is the periodic ground state of the")
    print("strain field u(r).  Translation symmetry T_R u(r) = u(r) selects a")
    print("Bravais lattice {R = n1 a1 + n2 a2 + n3 a3}.  The 7 crystal systems")
    print("are the 7 ways to maximize symmetry of the strain unit cell.")
    print()
    print(f"  {'system':<14s}  {'a,b,c':<14s}  {'angles':<22s}  {'#Bravais':>8s}")
    print(f"  {'-'*14:<14s}  {'-'*14:<14s}  {'-'*22:<22s}  {'-'*8:>8s}")
    systems = [
        ("Triclinic",    "a!=b!=c",       "alpha!=beta!=gamma",      1),
        ("Monoclinic",   "a!=b!=c",       "alpha=gamma=90, beta!=90", 2),
        ("Orthorhombic", "a!=b!=c",       "alpha=beta=gamma=90",     4),
        ("Tetragonal",   "a=b!=c",        "alpha=beta=gamma=90",     2),
        ("Trigonal",     "a=b=c",         "alpha=beta=gamma!=90",    1),
        ("Hexagonal",    "a=b!=c",        "alpha=beta=90, gamma=120", 1),
        ("Cubic",        "a=b=c",         "alpha=beta=gamma=90",     3),
    ]
    total = 0
    for s, ax, ang, n in systems:
        print(f"  {s:<14s}  {ax:<14s}  {ang:<22s}  {n:>8d}")
        total += n
    print(f"  {'TOTAL':<14s}  {'':<14s}  {'':<22s}  {total:>8d}")
    print()
    print("The 14 Bravais lattices (P=primitive, I=body-centered,")
    print("F=face-centered, C=base-centered, R=rhombohedral):")
    print()
    bravais = [
        ("Triclinic",    ["P"]),
        ("Monoclinic",   ["P", "C"]),
        ("Orthorhombic", ["P", "C", "I", "F"]),
        ("Tetragonal",   ["P", "I"]),
        ("Trigonal",     ["R"]),
        ("Hexagonal",    ["P"]),
        ("Cubic",        ["P (sc)", "I (bcc)", "F (fcc)"]),
    ]
    for s, types in bravais:
        print(f"  {s:<14s}  {', '.join(types)}")
    print()
    print("Substrate explanation: each Bravais lattice is the minimum-strain")
    print("packing of the substrate unit-cell strain pattern under the symmetry")
    print("constraints of its system.  The 14-fold count comes from the discrete")
    print("ways periodic + point symmetries can be COMPATIBLE.")

    # ============================================================
    section(2, "230 SPACE GROUPS (substrate symmetry classification)")
    # ============================================================
    print("Combine 14 Bravais lattices x 32 crystallographic point groups,")
    print("permitting screw axes and glide planes.  Result: exactly 230 space")
    print("groups (Fedorov, Schoenflies, Barlow ~1890).")
    print()
    print("Substrate origin: the strain ground state must be invariant under")
    print("its own symmetry group.  Point operations (rotation, mirror, inversion)")
    print("acting on local strain modes, combined with translations, give a")
    print("DISCRETE finite list because of the crystallographic restriction:")
    print("only 1, 2, 3, 4, 6 fold rotations tile space (NO 5, 7, 8 fold).")
    print()
    print("Why no 5-fold periodic crystals?  A 5-fold rotation cannot tile R^3")
    print("with one repeating unit.  Quasicrystals (Shechtman 1984) escape by")
    print("being aperiodic - their substrate strain pattern is icosahedral but")
    print("not lattice-periodic.")
    print()
    print(f"  {'system':<14s}  {'#point groups':>14s}  {'#space groups':>14s}")
    sg_counts = [
        ("Triclinic",     2,   2),
        ("Monoclinic",    3,  13),
        ("Orthorhombic",  3,  59),
        ("Tetragonal",    7,  68),
        ("Trigonal",      5,  25),
        ("Hexagonal",     7,  27),
        ("Cubic",         5,  36),
    ]
    tp, ts = 0, 0
    for s, p, g in sg_counts:
        print(f"  {s:<14s}  {p:>14d}  {g:>14d}")
        tp += p; ts += g
    print(f"  {'TOTAL':<14s}  {tp:>14d}  {ts:>14d}")
    print()
    print("32 point groups + 14 Bravais lattices --> 230 space groups.")
    print("The orientability primitive forbids no operation here (all 230 are")
    print("orientable); chiral pairs split into 65 enantiomorphic Sohncke groups.")

    # ============================================================
    section(3, "MILLER INDICES & X-RAY DIFFRACTION (Bragg)")
    # ============================================================
    print("Miller indices (hkl) label families of parallel lattice planes.")
    print("Plane spacing for cubic system:  d_hkl = a / sqrt(h^2 + k^2 + l^2)")
    print()
    print("Bragg's law:  n lambda = 2 d sin(theta)")
    print()
    print("Substrate derivation: an X-ray is a substrate transverse wave with")
    print("wavelength lambda.  Periodic strain modulation in the crystal acts as")
    print("a diffraction grating.  Constructive interference between planes")
    print("requires path difference = n lambda  =>  Bragg condition.")
    print()
    a_cu = 3.615   # angstrom, Cu lattice parameter
    lam_Cu_Ka = 1.5418  # angstrom, Cu K-alpha
    print(f"Worked example: Cu metal (FCC, a = {a_cu} A) with Cu K-alpha radiation")
    print(f"  lambda = {lam_Cu_Ka} A")
    print()
    print(f"  {'(hkl)':<8s}  {'d [A]':>8s}  {'2 theta [deg]':>14s}  {'allowed?':>10s}")
    planes = [(1,0,0), (1,1,0), (1,1,1), (2,0,0), (2,1,0),
              (2,1,1), (2,2,0), (3,1,1), (2,2,2), (4,0,0)]
    for h, k, l in planes:
        d = a_cu / math.sqrt(h*h + k*k + l*l)
        # Bragg, n=1
        sin_th = lam_Cu_Ka / (2.0 * d)
        if sin_th > 1.0:
            two_th_str = "    --"
        else:
            two_th = 2.0 * math.degrees(math.asin(sin_th))
            two_th_str = f"{two_th:>14.2f}"
        # FCC selection rule: h,k,l all even or all odd
        all_even = (h % 2 == 0) and (k % 2 == 0) and (l % 2 == 0)
        all_odd  = (h % 2 == 1) and (k % 2 == 1) and (l % 2 == 1)
        allowed = "yes" if (all_even or all_odd) else "no"
        print(f"  ({h}{k}{l})   {d:>8.3f}  {two_th_str}  {allowed:>10s}")
    print()
    print("FCC selection rule (h,k,l all even or all odd) follows from the")
    print("structure factor F_hkl = sum_j f_j exp(2 pi i (h x_j + k y_j + l z_j)).")
    print("For FCC basis (000, 1/2 1/2 0, 1/2 0 1/2, 0 1/2 1/2): F=4f when")
    print("parities match, F=0 otherwise -> SUBSTRATE INTERFERENCE selects.")

    # ============================================================
    section(4, "RECIPROCAL LATTICE & BRILLOUIN ZONES")
    # ============================================================
    print("Direct lattice  {R = n1 a1 + n2 a2 + n3 a3}")
    print("Reciprocal lattice  {G : exp(i G . R) = 1 for all R}")
    print()
    print("  b1 = 2 pi (a2 x a3) / [a1 . (a2 x a3)]   (cyclic for b2, b3)")
    print()
    print("Substrate meaning: G's are the wavevectors at which substrate strain")
    print("modes couple coherently to the periodic potential.  Bloch's theorem:")
    print("  psi_k(r) = exp(i k . r) u_k(r)   with u_k(r+R) = u_k(r)")
    print("comes directly from translation invariance of the substrate Lagrangian.")
    print()
    print("Brillouin zone (BZ) = Wigner-Seitz cell of the reciprocal lattice.")
    print("All physical k-states live in the 1st BZ; outside is redundant by G.")
    print()
    print(f"  {'lattice':<10s}  {'reciprocal':<14s}  {'1st BZ shape':<24s}")
    bz = [
        ("simple cubic", "simple cubic", "cube"),
        ("FCC",          "BCC",          "rhombic dodecahedron"),
        ("BCC",          "FCC",          "truncated octahedron"),
        ("hexagonal",    "hexagonal",    "hexagonal prism"),
    ]
    for d, r, b in bz:
        print(f"  {d:<10s}  {r:<14s}  {b:<24s}")
    print()
    print("High-symmetry points (FCC example): Gamma (000), X (face), L (corner),")
    print("K (edge), W (vertex).  Electronic band structures E_n(k) are plotted")
    print("along Gamma-X-W-L-Gamma-K paths in the BZ.")

    # ============================================================
    section(5, "POINT DEFECTS (vacancies, interstitials, F/S pairs)")
    # ============================================================
    print("Point defects = LOCAL departures from the periodic strain ground state.")
    print()
    print(f"  {'defect':<22s}  {'description':<38s}")
    pdefs = [
        ("Vacancy",                 "missing atom (strain hole)"),
        ("Interstitial",            "extra atom in interstice (strain bulge)"),
        ("Substitutional impurity", "wrong atom at lattice site"),
        ("Frenkel pair",            "vacancy + self-interstitial"),
        ("Schottky defect",         "cation+anion vacancy pair (ionic)"),
        ("Color center (F-center)", "electron trapped in anion vacancy"),
    ]
    for d, desc in pdefs:
        print(f"  {d:<22s}  {desc:<38s}")
    print()
    print("Equilibrium vacancy concentration (Boltzmann):")
    print("  n_v / N = exp(-E_v / k_B T)")
    print()
    T = 1000.0  # K
    print(f"At T = {T:.0f} K:")
    print(f"  {'metal':<10s}  {'E_v [eV]':>9s}  {'n_v/N':>14s}")
    metals = [("Cu", 1.28), ("Al", 0.67), ("Au", 0.94), ("Ni", 1.40), ("W", 3.6)]
    for m, ev in metals:
        nv = math.exp(-ev * EV_J / (K_B * T))
        print(f"  {m:<10s}  {ev:>9.2f}  {nv:>14.3e}")
    print()
    print("Substrate origin: each vacancy or interstitial is a localized strain")
    print("perturbation costing E_v.  Boltzmann weight comes from the substrate")
    print("free-energy balance F = E - T S (more vacancies -> more configurational")
    print("entropy, balancing the strain cost).")

    # ============================================================
    section(6, "LINE DEFECTS (dislocations as topological strain)")
    # ============================================================
    print("Edge dislocation  : extra half-plane of atoms ending in a line.")
    print("Screw dislocation : helical strain ramp around a line.")
    print()
    print("Burgers vector b: closure failure of a circuit around the line.")
    print("Topological charge:  oint du = b  != 0  (non-trivial winding).")
    print()
    print("Substrate framing: dislocations are TOPOLOGICAL DEFECTS of the strain")
    print("field u - the same class as vortex lines in superfluids and disclinations")
    print("in liquid crystals.  Connect to mechanical script: the elastic energy")
    print("per unit length is")
    print()
    print("  E_disloc / L = (G b^2 / 4 pi (1-nu)) * ln(R/r_core)    (edge)")
    print("  E_disloc / L = (G b^2 / 4 pi)        * ln(R/r_core)    (screw)")
    print()
    print("where G = K (substrate shear modulus), nu = Poisson ratio.")
    print()
    G_Cu = 48e9     # Pa, Cu shear modulus
    b_Cu = 2.55e-10 # m, Cu Burgers vector along <110>
    nu = 0.34
    R = 1e-6
    rc = 5e-10
    E_edge_per_m = G_Cu * b_Cu**2 / (4 * PI * (1 - nu)) * math.log(R/rc)
    E_screw_per_m = G_Cu * b_Cu**2 / (4 * PI) * math.log(R/rc)
    print(f"Cu (G={G_Cu/1e9:.0f} GPa, b={b_Cu*1e10:.2f} A, nu={nu:.2f}, R/rc={R/rc:.0e}):")
    print(f"  edge :  E/L = {E_edge_per_m*1e9:.2f} nJ/m  =  {E_edge_per_m / EV_J * 1e-10:.2f} eV/A")
    print(f"  screw:  E/L = {E_screw_per_m*1e9:.2f} nJ/m  =  {E_screw_per_m / EV_J * 1e-10:.2f} eV/A")
    print()
    print("Plastic deformation = motion of dislocations through the strain field.")
    print("Yield stress (Peierls-Nabarro) sigma_PN ~ G exp(-2 pi w / b), where w =")
    print("dislocation core width.  Same K that sets sound speed sets dislocation")
    print("energy and yield - one substrate stiffness, three observables.")

    # ============================================================
    section(7, "PLANAR DEFECTS (grain boundaries, stacking faults, twins)")
    # ============================================================
    print("Planar defects = 2D substrate strain interfaces.")
    print()
    print(f"  {'defect':<24s}  {'gamma [mJ/m^2]':>14s}  {'description':<28s}")
    pl = [
        ("Low-angle GB (5 deg)",      80, "wall of edge dislocations"),
        ("High-angle GB (random)",   600, "incoherent strain mismatch"),
        ("Twin boundary (Cu)",        24, "mirror reflection of lattice"),
        ("Twin boundary (Fe-bcc)",   190, "less coherent, higher cost"),
        ("Stacking fault (Cu)",       45, "ABCABC -> ABCBCA (FCC slip)"),
        ("Stacking fault (Al)",      135, "high gamma -> narrow ribbons"),
        ("Anti-phase boundary",      100, "ordered alloy phase shift"),
    ]
    for d, g, desc in pl:
        print(f"  {d:<24s}  {g:>14d}  {desc:<28s}")
    print()
    print("Substrate explanation: each planar defect is an interface between two")
    print("strain ground states (different orientations, stacking sequences, or")
    print("phases).  The interfacial energy gamma is the per-area strain mismatch.")
    print()
    print("Coherent boundaries (twins) cost much less than incoherent ones because")
    print("the strain field can match across them with mild distortion.")
    print()
    print("Stacking faults link to FCC vs HCP - both are close-packed, differing")
    print("only in stacking sequence (FCC: ABCABC; HCP: ABABAB).  A single stacking")
    print("fault in FCC inserts a one-layer 'HCP slab' - tiny strain energy penalty.")

    # ============================================================
    section(8, "CLOSE PACKING (FCC vs HCP, both eta = 0.7405)")
    # ============================================================
    print("Pack identical hard spheres to maximize density.  Two equally optimal")
    print("solutions exist:")
    print()
    print("  FCC  ABCABC stacking  (cubic close packed)")
    print("  HCP  ABABAB stacking  (hexagonal close packed)")
    print()
    eta_close = PI / (3.0 * math.sqrt(2.0))
    print(f"Both have packing fraction eta = pi / (3 sqrt 2) = {eta_close:.6f}")
    print(f"Kepler conjecture (proved 2014, Hales) -> {eta_close*100:.2f}% is optimal.")
    print()
    print("Substrate framing: the K_4 tetrahedral local arrangement of 4 nearest")
    print("neighbors around each sphere is the same in FCC and HCP - only the")
    print("LONG-RANGE stacking differs.  The substrate strain density (and its")
    print("packing fraction) is set by LOCAL geometry, not by global stacking.")
    print()
    print(f"  {'structure':<10s}  {'eta':>10s}  {'CN':>4s}  {'examples':<28s}")
    pf = [
        ("FCC",      eta_close,           12, "Cu, Al, Ni, Au, Ag, Pb"),
        ("HCP",      eta_close,           12, "Mg, Zn, Ti, Co, Zr, Be"),
        ("BCC",      PI*math.sqrt(3)/8,    8, "Fe (alpha), W, Cr, Mo, Na"),
        ("Diamond",  PI*math.sqrt(3)/16,   4, "C (diamond), Si, Ge, Sn(g)"),
        ("Sim cubic",PI/6.0,               6, "Po (only known example)"),
    ]
    for s, e, cn, ex in pf:
        print(f"  {s:<10s}  {e:>10.4f}  {cn:>4d}  {ex:<28s}")
    print()
    print("BCC packing (eta = pi sqrt 3 / 8 = 0.6802):")
    print(f"  {PI*math.sqrt(3)/8:.6f} - bcc has CN = 8 not 12, so less dense.")
    print(f"Diamond cubic (eta = pi sqrt 3 / 16 = {PI*math.sqrt(3)/16:.4f}):")
    print("  CN = 4 (sp3 tetrahedral covalent), so very loose - lots of voids.")

    # ============================================================
    section(9, "IONIC CRYSTALS & MADELUNG CONSTANTS")
    # ============================================================
    print("Ionic crystal cohesive energy (per ion pair):")
    print()
    print("  U_lattice = - (M e^2 / 4 pi eps0 r0) (1 - 1/n)")
    print()
    print("M = Madelung constant = sum over all ion pairs of (+/-)/d_ij,")
    print("a CONDITIONALLY CONVERGENT lattice sum that depends only on geometry.")
    print()
    print("Substrate origin: the substrate Coulomb sum at each site, with sign")
    print("alternating by ionic charge, gives M.  The (1 - 1/n) factor is the")
    print("balance against short-range substrate REPULSION (Born exponent n,")
    print("from sigma <= 1/2 saturation cap acting at contact).")
    print()
    print(f"  {'structure':<14s}  {'M':>10s}  {'CN+':>4s}  {'CN-':>4s}  {'example':<14s}")
    mad = [
        ("NaCl (rock-salt)", 1.74756,   6, 6, "NaCl, KCl, MgO"),
        ("CsCl",             1.76267,   8, 8, "CsCl, CsBr, NH4Cl"),
        ("ZnS (sphalerite)", 1.63806,   4, 4, "ZnS, GaAs, CdTe"),
        ("ZnS (wurtzite)",   1.64132,   4, 4, "ZnS, ZnO, GaN"),
        ("Fluorite (CaF2)",  2.51939,   8, 4, "CaF2, ZrO2, UO2"),
        ("Rutile (TiO2)",    2.408,     6, 3, "TiO2, SnO2, MnO2"),
        ("Perovskite ABO3",  "~12-24",  12,6, "SrTiO3, BaTiO3, CaTiO3"),
        ("Corundum Al2O3",   25.0312,   6, 4, "Al2O3, Cr2O3, Fe2O3"),
    ]
    for s, m, cp, cn, ex in mad:
        if isinstance(m, float):
            print(f"  {s:<14s}  {m:>10.5f}  {cp:>4d}  {cn:>4d}  {ex:<14s}")
        else:
            print(f"  {s:<14s}  {m:>10s}  {cp:>4d}  {cn:>4d}  {ex:<14s}")
    print()
    # NaCl worked example
    M_NaCl = 1.74756
    r0 = 2.82e-10  # m, NaCl Na-Cl distance
    n_born = 8.0
    e2_4pe0 = (1.602176634e-19)**2 / (4 * PI * EPS0)  # J m
    U_per_pair = -M_NaCl * e2_4pe0 / r0 * (1 - 1/n_born)
    U_kJ_per_mol = U_per_pair * N_A / 1000.0
    print(f"NaCl worked example (M={M_NaCl}, r0={r0*1e10:.2f} A, n={n_born:.0f}):")
    print(f"  U_lattice = {U_kJ_per_mol:.1f} kJ/mol  (experimental: -787 kJ/mol)")
    print(f"  Match: {abs(U_kJ_per_mol - (-787))/787*100:.1f}%")
    print()
    print("Born-Haber cycle uses U_lattice + ionization + electron affinity")
    print("+ atomization + sublimation = formation enthalpy - all consistent.")

    # ============================================================
    section(10, "POLYMORPHISM & ALLOTROPES (one substance, many strains)")
    # ============================================================
    print("Same atoms, different substrate strain configurations -> different")
    print("crystals.  Stability set by Gibbs free energy G = H - T S + p V.")
    print()
    print("Carbon allotropes (the textbook example):")
    print()
    print(f"  {'phase':<14s}  {'CN':>4s}  {'hybrid':<6s}  {'rho [g/cc]':>10s}  {'stable':<22s}")
    carbon = [
        ("Diamond",     4, "sp3", 3.515, "high P (HPHT) or meta"),
        ("Graphite",    3, "sp2", 2.267, "ambient P, all T"),
        ("Lonsdaleite", 4, "sp3", 3.51,  "shock impact"),
        ("Fullerene C60", 3, "sp2/sp3", 1.65, "ambient (molecular xtal)"),
        ("Carbon nanotube", 3, "sp2", 1.4, "ambient (1D)"),
        ("Graphene",    3, "sp2", "2D",  "ambient (2D sheet)"),
        ("Amorphous C", "var", "mix", 1.8, "ambient (no LRO)"),
        ("Q-carbon",    4, "sp3+sp2", 3.8, "metastable (laser quench)"),
    ]
    for p, cn, h, r, s in carbon:
        rs = f"{r:.3f}" if isinstance(r, float) else str(r)
        cns = f"{cn}" if isinstance(cn, int) else str(cn)
        print(f"  {p:<14s}  {cns:>4s}  {h:<6s}  {rs:>10s}  {s:<22s}")
    print()
    print("Other notable polymorphs:")
    print()
    other = [
        ("SiO2",    "quartz / cristobalite / tridymite / coesite / stishovite"),
        ("CaCO3",   "calcite (R-3c) / aragonite (Pmcn) / vaterite"),
        ("TiO2",    "rutile / anatase / brookite"),
        ("Fe",      "alpha (BCC) / gamma (FCC) / delta (BCC) / epsilon (HCP)"),
        ("S",       "alpha (orthorhombic S8) / beta (monoclinic) / liquid chain"),
        ("Sn",      "alpha (gray, diamond, <13 C) / beta (white, tetragonal)"),
        ("H2O",     "ice Ih, Ic, II-XIX (19+ phases under various P,T)"),
        ("Ice VII", "cubic, stable >2 GPa - found in deep-Earth diamond inclusions"),
    ]
    for s, desc in other:
        print(f"  {s:<10s}  {desc}")
    print()
    print("Substrate framing: the same atoms can settle into multiple LOCAL minima")
    print("of V(u).  Which minimum wins depends on (T, P) via the Gibbs energy.")
    print("Phase transitions = the system tunnels or jumps between strain minima.")
    print()
    print("Iron alpha->gamma at 912 C: BCC->FCC reconfiguration of the strain")
    print("ground state.  The substrate is the SAME, only its periodic minimum")
    print("changes - explains why all polymorphs are accessible without changing")
    print("the underlying primitives K, rho, xi.")

    # ============================================================
    section(11, "SUMMARY: crystals, defects, and phases as one strain story")
    # ============================================================
    print("All of crystallography reduces to the SAME substrate Lagrangian L,")
    print("now with a periodic potential V(u).  Configuration -> phenomenon:")
    print()
    print("  periodic minimum of V(u)         -> Bravais lattice (14)")
    print("  symmetry of strain unit cell     -> crystal system (7) / point group (32)")
    print("  + screw axes / glide planes      -> space group (230)")
    print("  diffraction of substrate waves   -> Bragg's law / Miller indices")
    print("  reciprocal of translation group  -> Brillouin zone / Bloch states")
    print("  local strain perturbation        -> point defect (vacancy, interstitial)")
    print("  topological strain singularity   -> dislocation (edge / screw)")
    print("  2D strain interface              -> grain boundary, twin, stacking fault")
    print("  K_4 nearest-neighbor packing     -> close packing (eta = 0.7405)")
    print("  alternating-sign Coulomb sum     -> Madelung constant (NaCl, CsCl, ...)")
    print("  multiple V(u) local minima       -> polymorphs / allotropes (C, Fe, H2O)")
    print("  jump between minima              -> phase transition (alpha-gamma Fe, etc.)")
    print()
    print("Honest scoreboard: substrate predicts THE SAME numbers as classical")
    print("crystallography (Bragg angles, Madelung sums, dislocation energies)")
    print("because periodicity + linear elasticity + Coulomb on the substrate")
    print("REDUCES to standard solid-state theory in the long-wavelength limit.")
    print()
    print("Value-add: 14 lattices + 230 groups + defects + close packing + ionic")
    print("cohesion + polymorphism are all CONFIGURATIONS of one strain field,")
    print("rather than 11 disconnected empirical chapters.")


if __name__ == "__main__":
    main()
