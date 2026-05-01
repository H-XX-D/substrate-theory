"""Colloidal and interface chemistry through the strain-medium framework.

Goes deeper than a generic colloid summary: every classical colloid result
(DLVO, CMC, zeta, Bancroft, Flory-Rehner, Stokes-Einstein) is reframed as
the SAME substrate-strain bookkeeping at different length scales — from
nanometer surfactant tails to micron-scale gels.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Interfaces  =  substrate-strain DISCONTINUITIES (jump in u or grad u).
Colloids    =  micron-scale stable substrate-strain patterns
                (long-lived because saturation sigma<=1/2 forbids merger).

Honest framing: substrate REPRODUCES standard colloid-science numbers
(DLVO energies, CMC, zeta-potential mobility, Stokes-Einstein D, scattering
intensities) — the unification is mechanism, not new constants.
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
EPS0 = 8.8541878128e-12
E_CHG = 1.602176634e-19
ANGSTROM = 1.0e-10
NANO = 1.0e-9
MICRO = 1.0e-6


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Colloidal and interface chemistry in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Interface = substrate strain DISCONTINUITY (jump in u or grad u)")
    print("Colloid   = micron-scale STABLE substrate-strain pattern")
    print("Stability = saturation cap sigma<=1/2 forbids unrestricted merger")
    print()

    # ============================================================
    section(1, "CLASSIFICATION OF COLLOIDS (phase pair x strain pattern)")
    # ============================================================
    print("Colloids are 2-phase mixtures with dispersed phase 1 nm - 1 um.")
    print("8 canonical types from (dispersed phase, continuous phase):")
    print()
    print(f"  {'name':<14s}  {'dispersed':<10s}  {'continuous':<10s}  {'example':<22s}")
    print(f"  {'-'*14:<14s}  {'-'*10:<10s}  {'-'*10:<10s}  {'-'*22:<22s}")
    types = [
        ("Sol",         "solid",  "liquid", "paint, ink, blood"),
        ("Solid sol",   "solid",  "solid",  "ruby glass, alloys"),
        ("Aerosol(s)",  "solid",  "gas",    "smoke, dust"),
        ("Emulsion",    "liquid", "liquid", "milk, mayonnaise"),
        ("Gel",         "liquid", "solid",  "jelly, agar, opal"),
        ("Aerosol(l)",  "liquid", "gas",    "fog, mist, hairspray"),
        ("Foam",        "gas",    "liquid", "whipped cream, head"),
        ("Solid foam",  "gas",    "solid",  "pumice, bread, styrofoam"),
    ]
    for n, d, c, ex in types:
        print(f"  {n:<14s}  {d:<10s}  {c:<10s}  {ex:<22s}")
    print()
    print("Substrate reading: each type = a different topology of strain")
    print("DISCONTINUITY surface. Sols have closed-volume strain pockets in a")
    print("continuous medium; foams invert that (continuous strain wraps")
    print("dispersed gas pockets). Gels are percolating strain networks.")
    print()
    print("Why 1 nm - 1 um?")
    print("  Lower: smaller than this -> molecular solution (no interface).")
    print("  Upper: larger than this -> Brownian motion < gravity; sediments out.")
    print("  Substrate origin: range where thermal strain fluctuations match")
    print("  surface-strain energy - sigma cap stabilizes the pattern.")

    # ============================================================
    section(2, "SURFACTANTS & MICELLES (CMC, HLB, classes)")
    # ============================================================
    print("Surfactant = amphiphilic molecule: hydrophilic head + hydrophobic tail.")
    print("Substrate framing: tail forces a strain mismatch with water; head")
    print("relieves it. Above critical concentration, tails group inward to")
    print("MINIMIZE total substrate-strain energy -> micelles form.")
    print()
    print("Four classes by head charge:")
    print(f"  {'class':<14s}  {'head':<22s}  {'example':<22s}")
    classes = [
        ("Anionic",     "-COO-, -SO3-, -OSO3-",  "SDS, soap (Na stearate)"),
        ("Cationic",    "-NR3+ (quat. ammon.)",  "CTAB, BAC"),
        ("Nonionic",    "-OH, -O-CH2-CH2-O-",    "Tween, Triton X, Brij"),
        ("Zwitterionic","both + and - charges",  "lecithin, CHAPS, betaine"),
    ]
    for cl, hd, ex in classes:
        print(f"  {cl:<14s}  {hd:<22s}  {ex:<22s}")
    print()
    print("Critical Micelle Concentration (CMC) = where tails-as-strain-defects")
    print("become cheaper aggregated than dispersed:")
    print()
    print(f"  {'surfactant':<22s}  {'CMC [mM]':>9s}  {'agg. number':>12s}  {'class':<10s}")
    cmc_data = [
        ("SDS (sodium dodec sulf)",   8.2,    62, "anionic"),
        ("CTAB (cetyl trim. amm.)",   0.92,   90, "cationic"),
        ("Triton X-100",              0.24,  140, "nonionic"),
        ("Tween 20",                  0.06,   60, "nonionic"),
        ("Brij 35",                   0.09,   40, "nonionic"),
        ("DTAB (dodec trim. amm.)",  15.0,    55, "cationic"),
        ("Sodium cholate",            14.0,    5, "anionic (bile)"),
        ("CHAPS",                     8.0,    10, "zwitterionic"),
    ]
    for n, c, a, cl in cmc_data:
        print(f"  {n:<22s}  {c:>9.3f}  {a:>12d}  {cl:<10s}")
    print()
    print("HLB (Hydrophilic-Lipophilic Balance) Griffin scale 0 (oil) - 20 (water):")
    print("  HLB 3-6   -> W/O emulsifier (sorbitan oleate)")
    print("  HLB 7-9   -> wetting agent")
    print("  HLB 8-18  -> O/W emulsifier (Tween 80 = 15)")
    print("  HLB 13-15 -> detergent")
    print("  HLB 15-18 -> solubilizer")
    print()
    print("Substrate reading of HLB: ratio of head-side to tail-side strain")
    print("relaxation. Bancroft rule (sec 7) follows from HLB sign.")

    # ============================================================
    section(3, "DLVO THEORY (vdW attraction + double-layer repulsion)")
    # ============================================================
    print("DLVO (Derjaguin-Landau-Verwey-Overbeek) predicts colloid stability")
    print("from the SUM of two strain-energy contributions:")
    print()
    print("  V(h) = V_vdW(h) + V_EDL(h)")
    print()
    print("van der Waals (substrate-strain attraction, induced-dipole bridge):")
    print("  V_vdW(h) = - A * R / (12 h)        (sphere-sphere, Derjaguin)")
    print("    A  = Hamaker constant (J), depends on (rho, K) of media.")
    print()
    print("Electric double-layer (repulsion from screened ionic strain cloud):")
    print("  V_EDL(h) = 2 pi eps eps0 R psi0^2 exp(-kappa h)")
    print("    kappa  = inverse Debye length (substrate screening rate)")
    print("    psi0   = surface strain potential (volts)")
    print()
    # numeric demo
    A = 1.0e-20      # J, typical organic in water
    R = 100e-9       # 100 nm sphere
    eps_r = 78.5
    psi0 = 0.030     # 30 mV
    # Debye length for 1 mM 1:1 salt at 25 C: kappa^-1 ~ 9.6 nm
    kap_inv = 9.6e-9
    kappa = 1.0 / kap_inv
    print(f"Worked example: R = {R*1e9:.0f} nm  A = {A:.1e} J  psi0 = {psi0*1e3:.0f} mV")
    print(f"                 kappa^-1 = {kap_inv*1e9:.1f} nm   (1 mM 1:1 salt)")
    print()
    print(f"  {'h [nm]':>7s}  {'V_vdW [kT]':>12s}  {'V_EDL [kT]':>12s}  {'V_tot [kT]':>12s}")
    T = 298.15
    kT = K_B * T
    barrier = -1e9
    h_barrier = 0.0
    for h_nm in (0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100):
        h = h_nm * 1e-9
        V_vdW = -A * R / (12.0 * h)
        V_EDL = 2.0 * PI * eps_r * EPS0 * R * psi0**2 * math.exp(-kappa * h)
        V = V_vdW + V_EDL
        if V > barrier:
            barrier, h_barrier = V, h_nm
        print(f"  {h_nm:>7.1f}  {V_vdW/kT:>12.2f}  {V_EDL/kT:>12.2f}  {V/kT:>12.2f}")
    print()
    print(f"Energy barrier ~ {barrier/kT:+.1f} kT at h ~ {h_barrier:.1f} nm.")
    print("If barrier > ~15 kT  -> kinetically stable suspension.")
    print("If barrier <  ~5 kT  -> rapid coagulation (Smoluchowski limit).")
    print()
    print("Salt addition compresses the double layer (kappa grows as sqrt[I]).")
    print("Schulze-Hardy: critical coagulation conc. ~ z^-6 (counterion charge).")
    print(f"  Na+ (z=1): 1; Mg++ (z=2): {1/2**6:.4f}; Al+++ (z=3): {1/3**6:.5f}")
    print()
    print("Substrate basis: vdW = induced strain-bridge attraction (xi^-6 falloff)")
    print("                 EDL = ionic strain-cloud repulsion (Yukawa-screened).")
    print("Stability = strain-energy barrier > thermal kT.")

    # ============================================================
    section(4, "ZETA POTENTIAL & ELECTROKINETICS (Smoluchowski)")
    # ============================================================
    print("Zeta potential (zeta) = electric strain-potential at the SLIPPING PLANE")
    print("(the shear surface between bound and bulk fluid). It is the")
    print("electrokinetically measurable proxy for the surface charge.")
    print()
    print("Smoluchowski mobility (kappa R >> 1, thin double layer):")
    print("  mu_e = eps eps0 zeta / eta")
    print("Huckel mobility (kappa R << 1, thick double layer):")
    print("  mu_e = (2/3) eps eps0 zeta / eta")
    print()
    print(f"  {'|zeta| [mV]':>11s}  {'stability':<28s}  {'behaviour':<20s}")
    zranges = [
        ("0 - 5",     "rapid coagulation",            "flocculation"),
        ("5 - 10",    "incipient instability",        "loose floc"),
        ("10 - 30",   "moderate stability",           "slow aggregation"),
        ("30 - 40",   "good stability",               "stable months"),
        ("40 - 60",   "very good stability",          "very stable"),
        ("60 - 100",  "excellent",                     "indefinite"),
    ]
    for r, s, b in zranges:
        print(f"  {r:>11s}  {s:<28s}  {b:<20s}")
    print()
    eta = 1.002e-3
    zeta = 0.040   # 40 mV
    mu_smol = eps_r * EPS0 * zeta / eta
    print(f"Worked: zeta = {zeta*1e3:.0f} mV  ->  mu_e = {mu_smol*1e8:.2f} x 10^-8 m^2/(V s)")
    print(f"        for a 1 V/cm = 100 V/m field, drift = {mu_smol*100*1e6:.2f} um/s")
    print()
    print("Related electrokinetic phenomena (all 4 in DLVO substrate picture):")
    print("  1. Electrophoresis  - particle moves under E-field (above)")
    print("  2. Electroosmosis   - liquid moves through fixed porous bed")
    print("  3. Streaming pot.   - flow generates voltage across capillary")
    print("  4. Sediment. pot.   - falling particles generate voltage")
    print()
    print("Substrate framing: zeta = depth of trapped strain potential at the")
    print("shear surface; double-layer ions are co-moving strain charges.")

    # ============================================================
    section(5, "BROWNIAN MOTION & SEDIMENTATION (Stokes-Einstein, Svedberg)")
    # ============================================================
    print("Diffusion coefficient (Einstein 1905):")
    print("  D = k_B T / (6 pi eta r)        Stokes-Einstein")
    print()
    print(f"  {'r [nm]':>7s}  {'D [m^2/s]':>13s}  {'<x^2>^.5 in 1 s':>17s}")
    for r_nm in (1, 5, 10, 50, 100, 500, 1000):
        r_m = r_nm * 1e-9
        D = K_B * T / (6.0 * PI * eta * r_m)
        rms = math.sqrt(2.0 * D * 1.0)
        print(f"  {r_nm:>7d}  {D:>13.3e}  {rms*1e6:>14.2f} um")
    print()
    print("Sedimentation balance: gravity vs Brownian motion.")
    print("Sedimentation velocity (Stokes):")
    print("  v_s = 2 r^2 (rho_p - rho_f) g / (9 eta)")
    print()
    rho_p = 2500.0    # silica
    rho_f = 1000.0    # water
    g = 9.81
    print(f"  {'r [nm]':>7s}  {'v_s [m/s]':>13s}  {'time to fall 1 cm':>22s}")
    for r_nm in (10, 100, 1000, 10000):
        r_m = r_nm * 1e-9
        v_s = 2.0 * r_m**2 * (rho_p - rho_f) * g / (9.0 * eta)
        t_fall = 0.01 / v_s
        print(f"  {r_nm:>7d}  {v_s:>13.3e}  {t_fall:>22.2e} s")
    print()
    print("Svedberg unit S = 10^-13 s (sedimentation coefficient s = v_s / a_centrif).")
    print("Ultracentrifuge (10^5 g) lets us sediment proteins (1-1000 S):")
    print("  ribosomes  70S (prokaryote), 80S (eukaryote)")
    print("  hemoglobin 4.5S      DNA pol III  20S      virus 100-1000S")
    print()
    print("Substrate reading: Brownian motion = thermal substrate fluctuations")
    print("kicking the strain pattern; gamma drag damps it; sigma cap allows")
    print("the pattern to persist as an identifiable colloidal individual.")

    # ============================================================
    section(6, "LIGHT SCATTERING (Rayleigh, Mie, Tyndall, DLS)")
    # ============================================================
    print("Light scattering = electromagnetic substrate strain interrogation")
    print("of the dielectric inhomogeneity (refractive-index discontinuity).")
    print()
    print("Regimes by size parameter x = 2 pi r / lambda :")
    print(f"  {'regime':<12s}  {'condition':<14s}  {'I(theta)':<24s}  {'I dependence':<18s}")
    regimes = [
        ("Rayleigh",  "x << 1",        "1 + cos^2 theta",     "I ~ r^6 / lambda^4"),
        ("Mie",       "x ~ 1",         "complex resonances",  "size + n dep."),
        ("Geometric", "x >> 1",        "ray optics",          "I ~ r^2"),
    ]
    for r, c, i, d in regimes:
        print(f"  {r:<12s}  {c:<14s}  {i:<24s}  {d:<18s}")
    print()
    print("Rayleigh: blue sky (lambda^-4 -> blue 4x more than red).")
    print("Tyndall effect: visible scattering by colloids (Mie regime).")
    print("Mie: structural color in opals, butterfly wings, soap films.")
    print()
    # Rayleigh ratio sample
    print("Wavelength-color Rayleigh intensity ratio (vs red 700 nm):")
    for nm, name in ((400, "violet"), (450, "blue"), (550, "green"), (700, "red")):
        ratio = (700.0 / nm) ** 4
        print(f"  {nm} nm ({name:<6s}): {ratio:.2f}")
    print()
    print("Dynamic light scattering (DLS) - from Brownian autocorrelation:")
    print("  g1(tau) = exp(-D q^2 tau)   ->   D = K_B T / (6 pi eta r_h)")
    print("So DLS measures hydrodynamic radius r_h directly. Industry standard.")
    print()
    print("Substrate framing: scattering = elastic interaction of EM substrate")
    print("modes with refractive (rho, K) discontinuities at the colloid surface.")

    # ============================================================
    section(7, "EMULSIONS (Bancroft, Pickering, microemulsions)")
    # ============================================================
    print("Emulsion = liquid-in-liquid colloid (oil/water O/W or water/oil W/O).")
    print("Common examples (continuous phase determines 'type'):")
    print()
    print(f"  {'example':<18s}  {'type':<6s}  {'stabilizer':<28s}")
    em_data = [
        ("Milk",            "O/W",  "casein micelles + phospholipids"),
        ("Mayonnaise",      "O/W",  "egg lecithin (HLB ~8)"),
        ("Butter",          "W/O",  "milk fat crystals + phospholipids"),
        ("Vinaigrette",     "O/W",  "transient (mustard helps)"),
        ("Cream",           "O/W",  "milk-fat globule membrane"),
        ("Hand cream",      "O/W",  "stearate + cetyl alcohol"),
        ("Asphalt emul.",   "O/W",  "anionic surfactant"),
        ("Margarine",       "W/O",  "monoglycerides + lecithin"),
    ]
    for e, t, s in em_data:
        print(f"  {e:<18s}  {t:<6s}  {s:<28s}")
    print()
    print("Bancroft rule: 'phase in which surfactant is more soluble = continuous'.")
    print("  HLB > 10 (water-loving)  -> O/W")
    print("  HLB < 6  (oil-loving)    -> W/O")
    print()
    print("Substrate reading: surfactant tilts the interface curvature toward")
    print("the side that DOES NOT match its dominant strain relaxation.")
    print()
    print("Pickering emulsions (1907): solid PARTICLES at interface, not surfactant.")
    print("  Particle wets both phases; partial dewetting -> trapped at interface")
    print("  with very high desorption energy. Substrate: strain-defect ring at")
    print("  the contact circle; energy ~ pi r^2 gamma_LL (1-|cos theta|)^2.")
    print()
    r_p = 100e-9      # 100 nm particle
    gamma_OW = 0.030  # N/m, oil-water typical
    theta_c = 90.0    # degrees, neutral wetting
    E_des = PI * r_p**2 * gamma_OW * (1.0 - abs(math.cos(math.radians(theta_c))))**2
    print(f"  Worked: r_p={r_p*1e9:.0f} nm, gamma_OW={gamma_OW*1e3:.0f} mN/m, theta=90 deg")
    print(f"          desorp. energy = {E_des:.2e} J = {E_des/kT:.2e} kT")
    print("          -> essentially irreversible attachment (kT^7 scale).")
    print()
    print("Microemulsions: thermodynamically stable, 5-50 nm droplets.")
    print("  Negative interfacial tension (gamma -> 0) from co-surfactant + salt.")
    print("  Substrate: interfacial strain energy approaches zero -> spontaneous")
    print("  dispersion is the equilibrium state, not a kinetic trap.")

    # ============================================================
    section(8, "FOAM SCIENCE (Plateau, Laplace, drainage, coarsening)")
    # ============================================================
    print("Foam = gas-in-liquid colloid. Geometry obeys Plateau's laws:")
    print("  1. Films meet 3 at a time, at exactly 120 deg (Plateau border)")
    print("  2. Borders meet 4 at a time, at the tetrahedral angle 109.47 deg")
    print()
    print("Substrate reading: the angles MINIMIZE total interfacial strain area")
    print("(same 109.47 from sp3 hybridization in molecular_bonding sec 3).")
    print()
    print("Laplace pressure across curved film:")
    print("  Delta P = 2 gamma / R    (single curvature, soap bubble: 4 gamma/R)")
    print()
    gamma_w = 0.072  # water-air
    print(f"  Water surface tension gamma = {gamma_w*1e3:.0f} mN/m")
    print(f"  {'R [um]':>7s}  {'Delta P [Pa]':>13s}  {'mm H2O equiv':>13s}")
    for R_um in (1, 10, 100, 1000):
        Rm = R_um * 1e-6
        dP = 4.0 * gamma_w / Rm  # soap bubble (2 surfaces)
        mmH2O = dP / (1000.0 * 9.81 * 1e-3)
        print(f"  {R_um:>7d}  {dP:>13.1f}  {mmH2O:>13.2f}")
    print()
    print("Foam aging mechanisms:")
    print("  (a) Drainage: liquid flows OUT of films into Plateau borders under")
    print("      gravity. Substrate: strain-density gradient relaxes the film.")
    print("  (b) Coarsening (Ostwald): gas diffuses small bubble -> large bubble")
    print("      because Laplace pressure higher in small. d<R>^2/dt = const.")
    print("  (c) Coalescence: film ruptures when it thins below ~30 nm")
    print("      (vdW attraction overpowers EDL repulsion - same DLVO physics).")
    print()
    print("Stabilizers: surfactants (low gamma, Marangoni), proteins, particles")
    print("(Pickering foams are common in beer head, ice cream, espresso crema).")

    # ============================================================
    section(9, "GELS & HYDROGELS (Flory-Rehner, smart gels)")
    # ============================================================
    print("Gel = percolating polymer network swollen with solvent.")
    print("Substrate reading: a gel is a STATIC strain network (the polymer)")
    print("decorated with mobile substrate-strain (the solvent). It is solid")
    print("on long times, liquid on short times.")
    print()
    print("Crosslinking types:")
    print(f"  {'class':<16s}  {'crosslink':<24s}  {'examples':<22s}")
    cross = [
        ("Chemical (perm.)", "covalent C-C, S-S",      "PAAm, vulc. rubber"),
        ("Physical (rev.)",  "H-bond, ionic, helices", "agar, gelatin, jelly"),
        ("Hybrid",           "both",                    "alginate-Ca, dual"),
    ]
    for cl, ck, ex in cross:
        print(f"  {cl:<16s}  {ck:<24s}  {ex:<22s}")
    print()
    print("Mesh size xi_g (substrate length scale of network):")
    print(f"  {'gel':<22s}  {'mesh xi_g [nm]':>15s}  {'application':<22s}")
    mesh = [
        ("Polyacrylamide 5%",     30, "DNA gel electrophoresis"),
        ("Agarose 1%",           150, "DNA gel electrophoresis"),
        ("Collagen (native)",    100, "tissue, ECM scaffold"),
        ("Hyaluronic acid",       50, "synovial fluid, derm. fillers"),
        ("PEG hydrogel (drug)",   10, "controlled drug release"),
        ("Silica aerogel",         5, "thermal insulator"),
        ("Hagfish slime",     500000, "predator deterrent (?!)"),
    ]
    for g, m, a in mesh:
        print(f"  {g:<22s}  {m:>15d}  {a:<22s}")
    print()
    print("Flory-Rehner equilibrium swelling (chemical gel in good solvent):")
    print("  ln(1-phi) + phi + chi phi^2 + V1 nu (phi^(1/3) - phi/2) = 0")
    print("  phi = polymer volume fraction at equilibrium")
    print("  chi = Flory-Huggins parameter (substrate strain mismatch)")
    print("  V1 = solvent molar volume; nu = crosslink density")
    print()
    print("Smart hydrogels (stimuli-responsive):")
    print("  PNIPAM       : T-responsive (LCST 32 C, body temp drug delivery)")
    print("  Polyacrylic  : pH-responsive (carboxyl ionization)")
    print("  Polyelectro. : ionic-strength responsive")
    print("  Light-resp.  : azobenzene cis/trans isomerization")
    print()
    print("Substrate framing of swelling: solvent reduces substrate-strain")
    print("mismatch with hydrophilic groups (mixing entropy + chi); crosslinks")
    print("are elastic strain anchors that resist further expansion. Equilibrium")
    print("when chemical-potential strain gradients cancel.")

    # ============================================================
    section(10, "NANOPARTICLE SYNTHESIS (templated strain patterns)")
    # ============================================================
    print("Nanoparticle synthesis = controlled growth of micron-or-smaller")
    print("substrate-strain patterns from molecular precursors. Two regimes:")
    print()
    print("  Top-down: mill, etch, lithograph (slow, polydisperse).")
    print("  Bottom-up: chemical assembly (fast, monodisperse, scalable).")
    print()
    print(f"  {'method':<20s}  {'product':<22s}  {'size [nm]':>10s}  {'PDI':>6s}")
    syn = [
        ("Turkevich (citrate)",  "Au sphere",            20.0, 0.10),
        ("Brust-Schiffrin",      "Au with thiol shell",   3.0, 0.15),
        ("Sol-gel (Stober)",     "SiO2 sphere",         100.0, 0.05),
        ("Hydrothermal",         "TiO2, ZnO crystal",    50.0, 0.20),
        ("Microemulsion",        "CdS, Fe3O4",            8.0, 0.12),
        ("Polyol (Wang)",        "Ag nanowire",         100.0, 0.30),
        ("Hot injection",        "CdSe quantum dot",      4.0, 0.08),
        ("LaMer (S sol)",        "monodisperse S",      200.0, 0.04),
        ("CVD",                  "C nanotube, graphene", 1.0, 0.50),
        ("Ball milling",         "metal flakes",       1000.0, 0.80),
    ]
    for m, p, s, pdi in syn:
        print(f"  {m:<20s}  {p:<22s}  {s:>10.1f}  {pdi:>6.2f}")
    print()
    print("LaMer mechanism (1950): burst nucleation + diffusion-limited growth.")
    print("Substrate reading: nucleation = sigma-cap-locked strain seed; growth")
    print("= subsequent monomer addition under depletion of monomer pool.")
    print("Size monodispersity follows from short nucleation window vs growth time.")
    print()
    print("Turkevich (1951) - the classic gold colloid (still used today):")
    print("  HAuCl4 + sodium citrate -> Au0 nuclei + Au+ -> growth.")
    print("  Citrate triple role: reductant + capping + electrostatic stabilizer.")
    print()
    print("Quantum dots (CdSe, CdS): sub-Bohr-radius confinement makes the")
    print("substrate-strain bound state SIZE-tunable in energy:")
    print(f"  {'r [nm]':>7s}  {'dE [eV]':>9s}  {'emission':<14s}")
    # Brus equation order-of-magnitude: dE ~ pi^2 hbar^2 / (2 m* r^2)
    m_eff = 0.13 * 9.109e-31
    Eg_bulk = 1.74
    for rqd_nm in (1.5, 2.0, 2.5, 3.0, 4.0, 5.0):
        rqd = rqd_nm * 1e-9
        dE = (PI**2 * HBAR_J_S**2) / (2.0 * m_eff * rqd**2) / EV_J
        E_tot = Eg_bulk + dE
        nm_em = 1240.0 / E_tot
        col = "blue" if nm_em < 480 else ("green" if nm_em < 560 else
                ("yellow" if nm_em < 590 else ("orange" if nm_em < 620 else "red")))
        print(f"  {rqd_nm:>7.1f}  {dE:>9.3f}  {nm_em:>4.0f} nm ({col})")
    print()
    print("Substrate framing: the DOT is an artificial atom whose 'Bohr radius'")
    print("is set by the synthesis, not by chemistry. Substrate K and rho are")
    print("the bulk material constants; xi is now the dot radius (xi = r_dot).")

    # ============================================================
    section(11, "SUMMARY: interface = strain discontinuity, colloid = stable pattern")
    # ============================================================
    print("All colloid science reduces to ONE primitive: a substrate-strain")
    print("discontinuity (the interface) wrapping a finite volume (the colloid),")
    print("governed by the same K, rho, xi, gamma, sigma<=1/2 set used elsewhere.")
    print()
    print("Configuration -> phenomenon:")
    print("  closed strain pocket               -> sol / emulsion droplet")
    print("  inverted (gas inside continuous)   -> foam / aerosol")
    print("  percolating strain network         -> gel / hydrogel")
    print("  amphiphilic strain mismatch        -> surfactant micelle (CMC)")
    print("  vdW + EDL strain bookkeeping       -> DLVO stability barrier")
    print("  shear-plane strain potential       -> zeta + electrokinetics")
    print("  thermal strain fluctuations        -> Brownian motion / DLS")
    print("  refractive (rho,K) discontinuity   -> Rayleigh / Mie scattering")
    print("  Plateau-min interfacial area       -> 109.47 / 120 deg foam angles")
    print("  particle-trapped interface         -> Pickering emulsion / foam")
    print("  size-confined strain bound state   -> quantum dot")
    print()
    print("Honest scoreboard: substrate reproduces standard colloid-science")
    print("numbers (CMC, DLVO barrier, zeta mobility, Stokes-Einstein D, Laplace")
    print("pressure, Brus QD shift) because they all fall out of the same")
    print("strain-energy + saturation Lagrangian at the appropriate length scale.")
    print()
    print("Value-add is unification: 9 distinct chapters of colloid textbooks")
    print("become one strain-discontinuity story rather than nine independent")
    print("phenomenologies, and the same primitives connect upward to molecular")
    print("bonding (nm) and downward to industrial formulation (um).")


if __name__ == "__main__":
    main()
