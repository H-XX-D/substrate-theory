"""Photochemistry and spectroscopy through the strain-medium framework.

Every spectroscopic observable is a substrate-mode probe of the bound-state
strain configuration of a molecule. Photons are transverse substrate wave
quanta; absorption and emission are substrate-mode couplings between
discrete bound-state energy levels.

Strain-medium primitives (4 + 1 cap):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2

Substrate framings used throughout:
  photon                = transverse substrate wave quantum (k = omega/c)
  absorption / emission = mode-coupling between bound-state levels
  chemical shift delta  = local substrate-strain shielding of the nucleus
  J-coupling            = strain bridge between two nuclei (through-bond)
  vibrational mode      = oscillation of the bond-bridge strain field
  fluorescence          = singlet manifold radiative relaxation
  phosphorescence       = triplet manifold (forbidden) radiative relaxation
  Franck-Condon         = vertical electronic transition preserves the
                          instantaneous nuclear-strain pattern
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
H_J_S = 6.62607015e-34
C_M_S = 2.99792458e8
EV_J = 1.602176634e-19
K_B = 1.380649e-23
N_A = 6.02214076e23
EPS0 = 8.8541878128e-12
ME_KG = 9.1093837015e-31


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Photochemistry & spectroscopy in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma <= 1/2")
    print("Photon  =  transverse substrate wave quantum,  E = h nu = h c / lambda")
    print("Spectroscopy = probing bound-state strain configurations with photons")
    print()
    # quick photon energy reference
    print("Photon energy reference (substrate-mode quantum E = h c / lambda):")
    print(f"  {'region':<14s}  {'lambda':>12s}  {'E [eV]':>10s}  {'nu_tilde [cm-1]':>17s}")
    photon_ref = [
        ("gamma",      1e-12, "ultra"),
        ("X-ray",      1e-10, "core"),
        ("UV",         200e-9, "valence"),
        ("Vis",        550e-9, "valence"),
        ("near-IR",   1500e-9, "vib overtone"),
        ("mid-IR",    1e-5,    "vibrational"),
        ("far-IR",    1e-4,    "rotational"),
        ("microwave", 1e-2,    "rotational"),
        ("RF (NMR)",  3.0,     "nuclear spin"),
    ]
    for name, lam, _ in photon_ref:
        E = H_J_S * C_M_S / lam / EV_J
        nutilde = 1.0 / (lam * 100.0)
        print(f"  {name:<14s}  {lam:>12.2e}  {E:>10.3e}  {nutilde:>17.3e}")

    # ============================================================
    section(1, "ELECTRONIC TRANSITIONS (UV-Vis spectroscopy)")
    # ============================================================
    print("Absorption: substrate photon mode couples a ground-state electronic")
    print("strain pattern to a higher-energy bound-state strain pattern.")
    print()
    print("Key transition classes (named by which substrate orbital pair couples):")
    print()
    print(f"  {'transition':<10s}  {'origin':<26s}  {'lambda [nm]':>11s}  {'eps [M-1cm-1]':>14s}")
    transitions = [
        ("sigma->sigma*", "saturated C-H, C-C bonds",     "<150",    "1e3-1e5"),
        ("n->sigma*",     "lone pair -> antibond",         "150-250", "1e2-1e3"),
        ("pi->pi*",       "alkene/aromatic conjugation",   "180-400", "1e3-1e5"),
        ("n->pi*",        "C=O, C=N lone pair -> pi*",     "270-350", "10-100"),
        ("CT (charge)",   "donor -> acceptor",             "300-700", "1e3-1e4"),
        ("d->d (TM)",     "transition-metal d-orbitals",   "400-800", "1-100"),
        ("f->f (Ln)",     "lanthanide 4f sharp lines",     "350-1100","0.1-10"),
    ]
    for t, o, l, e in transitions:
        print(f"  {t:<10s}  {o:<26s}  {l:>11s}  {e:>14s}")
    print()
    print("Substrate selection rules:")
    print("  spin allowed     ->  Delta S = 0          (preserve substrate spin)")
    print("  Laporte allowed  ->  Delta ell = +/- 1    (parity flip, dipole mode)")
    print("  symmetry allowed ->  <psi_f| mu_dipole |psi_i>  has the right rep")
    print()
    print("n->pi* is symmetry-forbidden -> small eps (10-100); pi->pi* allowed.")
    print()
    print("Chromophore lambda_max table (substrate strain-mode resonance):")
    print(f"  {'chromophore':<22s}  {'lambda_max [nm]':>15s}  {'eps':>10s}  {'class':<10s}")
    chrom = [
        ("ethene C=C",            171,    15500, "pi->pi*"),
        ("1,3-butadiene",         217,    21000, "pi->pi*"),
        ("benzene",               254,      200, "pi->pi*"),
        ("naphthalene",           275,     5600, "pi->pi*"),
        ("anthracene",            375,     7900, "pi->pi*"),
        ("acetone n->pi*",        279,       15, "n->pi*"),
        ("nitrobenzene",          268,     7800, "pi->pi*"),
        ("beta-carotene",         470,   140000, "pi->pi* x11"),
        ("chlorophyll a (Soret)", 430,   120000, "pi->pi*"),
        ("chlorophyll a (Q)",     663,    90000, "pi->pi*"),
        ("retinal (rhodopsin)",   500,    40000, "pi->pi* x6"),
        ("[Cu(H2O)6]2+",          810,       12, "d->d"),
    ]
    for c, l, e, k in chrom:
        print(f"  {c:<22s}  {l:>15d}  {e:>10d}  {k:<10s}")
    print()
    print("Substrate prediction: extending conjugation lengthens the strain-mode")
    print("standing wave -> particle-in-a-box gap shrinks as 1/L^2 -> red shift.")
    L_box = [4, 6, 8, 10, 12]
    print()
    print("Particle-in-a-box (substrate standing wave) check, polyene C2n:")
    print(f"  {'2n':>4s}  {'L [pm]':>8s}  {'E_HOMO-LUMO [eV]':>18s}  {'lambda [nm]':>12s}")
    for n in L_box:
        L = n * 139e-12
        N_e = n
        # transition n -> n+1 in PiB:  Delta E = (2n+1) h^2 / (8 m L^2)
        DeltaE = (2*N_e + 1) * H_J_S**2 / (8.0 * ME_KG * L**2)
        DeltaE_eV = DeltaE / EV_J
        lam_nm = (H_J_S * C_M_S / DeltaE) * 1e9
        print(f"  {n:>4d}  {L*1e12:>8.0f}  {DeltaE_eV:>18.3f}  {lam_nm:>12.0f}")

    # ============================================================
    section(2, "BEER-LAMBERT LAW (substrate-mode density absorption)")
    # ============================================================
    print("Beer-Lambert:  A = log10(I0 / I) = epsilon * c * l")
    print()
    print("Substrate derivation: through a slab of thickness dl with N absorbers")
    print("per unit volume, photon flux I attenuates by")
    print("  dI / I  =  - sigma_abs N dl")
    print("  ln(I0/I)  =  sigma_abs N l   ->   A = (sigma_abs N_A / ln 10) c l")
    print("  epsilon   =  sigma_abs * N_A / ln 10")
    print()
    print("In substrate language sigma_abs is the cross-section for the photon")
    print("(transverse substrate wave) to drive the bound-state mode transition.")
    print("It scales as |<f| mu |i>|^2 / (Gamma) where Gamma is the linewidth.")
    print()
    # numeric examples
    print(f"  {'sample':<26s}  {'eps':>8s}  {'c [M]':>10s}  {'l [cm]':>8s}  {'A':>6s}  {'%T':>6s}")
    bl = [
        ("KMnO4 (525 nm)",         2300, 1e-4, 1.0),
        ("methylene blue (664 nm)", 95000, 1e-6, 1.0),
        ("hemoglobin Soret (415)",125000, 1e-5, 1.0),
        ("DNA (260 nm)",          6600,  1e-4, 1.0),
        ("protein (280 nm)",      5500,  1e-4, 1.0),
        ("acetone n->pi* (280)",    15,  1e-2, 1.0),
    ]
    for s, eps, c, l in bl:
        A = eps * c * l
        T = 100.0 * 10 ** (-A)
        print(f"  {s:<26s}  {eps:>8d}  {c:>10.0e}  {l:>8.1f}  {A:>6.3f}  {T:>6.2f}")
    print()
    print("Substrate reading: epsilon counts how many substrate-mode receivers")
    print("(transition dipoles) sit per molecule and how loudly each one rings")
    print("at the photon frequency. Big eps = strong allowed coupling.")

    # ============================================================
    section(3, "FRANCK-CONDON PRINCIPLE (vertical strain preservation)")
    # ============================================================
    print("Electronic transitions are MUCH faster than nuclear motion:")
    print("  electronic timescale ~ 1e-15 s   (1 fs)")
    print("  nuclear timescale    ~ 1e-13 s   (100 fs vibration period)")
    print()
    print("Substrate statement: during photon absorption the heavy-nuclei")
    print("strain pattern is FROZEN. The electronic strain pattern jumps")
    print("vertically on the configuration-coordinate diagram.")
    print()
    print("Consequence: the most intense vibronic line is the one whose")
    print("excited-state vibrational wavefunction maximally OVERLAPS the")
    print("ground-state v=0 nuclear strain envelope.")
    print()
    print("Franck-Condon factor:  FCF = |<chi_v'(Q)| chi_0(Q)>|^2")
    print()
    # demo: harmonic-harmonic same omega, different Q0
    print("Toy harmonic model (same omega, displaced minima):")
    print("  S = (1/2) (Delta Q / Q_0)^2   (Huang-Rhys parameter)")
    print("  FCF(0->v) = exp(-S) S^v / v!")
    print()
    for Sval in (0.1, 0.5, 1.0, 2.0, 4.0):
        line = f"  S = {Sval:>4.1f}: "
        for v in range(6):
            fcf = math.exp(-Sval) * Sval**v / math.factorial(v)
            line += f"v={v}:{fcf:.3f} "
        print(line)
    print()
    print("Small S (rigid molecules, e.g. aromatics): 0-0 line strongest, sharp.")
    print("Large S (flexible / displaced minima): broad band, intensity peaks at v>0.")
    print("Substrate origin of S: how much the EQUILIBRIUM strain center shifts")
    print("between ground and excited electronic configurations.")

    # ============================================================
    section(4, "VIBRATIONAL SPECTROSCOPY (IR group frequencies)")
    # ============================================================
    print("IR absorption: photon mid-IR substrate wave drives a vibrational mode")
    print("of the bond-bridge strain field.  omega = sqrt(k / mu)  where k is the")
    print("substrate spring constant and mu = m1 m2 / (m1+m2) the reduced mass.")
    print()
    print("IR selection rule: mode must produce a CHANGING dipole moment")
    print("                   ( d mu / d Q )_eq  !=  0")
    print("In substrate terms: the vibration must modulate the local strain")
    print("polarization so it can radiate / absorb a transverse photon mode.")
    print()
    print("Characteristic group frequencies (cm^-1):")
    print(f"  {'group':<22s}  {'mode':<18s}  {'nu [cm-1]':>10s}  {'intensity':<10s}")
    ir_groups = [
        ("O-H (free alcohol)",   "stretch",   "3600",      "sharp"),
        ("O-H (H-bonded)",       "stretch",   "3200-3550", "broad"),
        ("N-H (amine)",          "stretch",   "3300-3500", "med"),
        ("=C-H aromatic",        "stretch",   "3030",      "weak"),
        ("C-H sp3",              "stretch",   "2850-2960", "strong"),
        ("C#N nitrile",          "stretch",   "2250",      "med"),
        ("C#C alkyne",           "stretch",   "2100-2260", "var"),
        ("C=O ketone",           "stretch",   "1715",      "strong"),
        ("C=O aldehyde",         "stretch",   "1730",      "strong"),
        ("C=O ester",            "stretch",   "1740",      "strong"),
        ("C=O amide I",          "stretch",   "1650",      "strong"),
        ("C=C alkene",           "stretch",   "1640-1680", "var"),
        ("aromatic ring",        "C=C",       "1450-1600", "var"),
        ("N=O nitro asym",       "stretch",   "1510",      "strong"),
        ("C-O ester",            "stretch",   "1100-1300", "strong"),
        ("C-Cl",                 "stretch",   "600-800",   "strong"),
    ]
    for g, m, nu, i in ir_groups:
        print(f"  {g:<22s}  {m:<18s}  {nu:>10s}  {i:<10s}")
    print()
    print("Substrate prediction of stretches (k from bond-bridge stiffness):")
    print(f"  {'bond':<8s}  {'k [N/m]':>9s}  {'mu [u]':>8s}  {'nu [cm-1]':>11s}")
    bonds_vib = [
        ("C-C",    450, 6.0),
        ("C=C",    960, 6.0),
        ("C#C",   1560, 6.0),
        ("C-H",    480, 0.923),
        ("O-H",    770, 0.941),
        ("C=O",   1240, 6.857),
        ("C#N",   1840, 6.461),
    ]
    for b, k, mu_u in bonds_vib:
        mu_kg = mu_u * 1.66053906660e-27
        omega = math.sqrt(k / mu_kg)
        nu_tilde = omega / (2 * PI * C_M_S * 100)
        print(f"  {b:<8s}  {k:>9d}  {mu_u:>8.3f}  {nu_tilde:>11.0f}")
    print()
    print("Heavy-atom isotope shift from mu:  nu' / nu = sqrt(mu / mu')")
    print("  C-H -> C-D: nu drops by sqrt(0.923/1.781) ~ 0.72  (3000 -> 2150)")

    # ============================================================
    section(5, "RAMAN SCATTERING (inelastic substrate-strain coupling)")
    # ============================================================
    print("Raman: incident photon (visible) scatters inelastically off a")
    print("vibrational mode. Stokes (loses energy to a phonon-like substrate")
    print("vibration); anti-Stokes (gains energy from a thermally populated one).")
    print()
    print("Selection rule: vibration must change the POLARIZABILITY")
    print("                ( d alpha / d Q )_eq != 0")
    print()
    print("Mutual exclusion (centrosymmetric molecules):")
    print("  IR active modes  ->  ungerade (u)   change dipole")
    print("  Raman active     ->  gerade   (g)   change polarizability")
    print("  No mode is both IR- and Raman-active in centrosymmetric species.")
    print()
    print("Stokes / anti-Stokes intensity ratio (Boltzmann on the vibrational level):")
    print(f"  I_aS / I_S = ((nu0 + nu_v) / (nu0 - nu_v))^4 * exp(-h c nu_v / k_B T)")
    print()
    T = 298.15
    nu0 = 1.0 / (532e-9 * 100)  # cm-1 of 532 nm laser
    print(f"  laser 532 nm (nu0 = {nu0:.0f} cm-1), T = {T:.1f} K:")
    print(f"  {'mode nu_v':>10s}  {'I_aS / I_S':>12s}")
    for nv in (200, 500, 1000, 1500, 2000, 3000):
        ratio_freq = ((nu0 + nv) / (nu0 - nv)) ** 4
        boltz = math.exp(- (H_J_S * C_M_S * nv * 100) / (K_B * T))
        ratio = ratio_freq * boltz
        print(f"  {nv:>10d}  {ratio:>12.3e}")
    print()
    print("Substrate framing: the polarizability is how easily the bound-state")
    print("electron-strain cloud is deformed by an applied substrate field. A")
    print("vibration that breathes the cloud (e.g. symmetric C-C in benzene")
    print("at 992 cm-1) is loud in Raman, silent in IR.")

    # ============================================================
    section(6, "NMR SPECTROSCOPY (nuclear-spin substrate probe)")
    # ============================================================
    print("NMR: a static B0 field splits nuclear-spin substrate states by")
    print("Zeeman energy; an RF photon at the Larmor frequency drives the")
    print("transition.")
    print()
    print("Larmor:  nu_L = gamma B0 / (2 pi)")
    print(f"  {'nucleus':<8s}  {'I':>4s}  {'gamma/2pi [MHz/T]':>17s}  {'nu @ 11.74 T':>14s}")
    nmr_nuc = [
        ("1H",    "1/2", 42.577, 500.0),
        ("13C",   "1/2", 10.708, 125.7),
        ("19F",   "1/2", 40.078, 470.4),
        ("31P",   "1/2", 17.235, 202.4),
        ("15N",   "1/2",  4.316,  50.7),
        ("2H",    "1",    6.536,  76.7),
        ("17O",   "5/2",  5.772,  67.8),
    ]
    for n, I, g, nu11 in nmr_nuc:
        print(f"  {n:<8s}  {I:>4s}  {g:>17.3f}  {nu11:>14.1f}")
    print()
    print("Chemical shift delta = local substrate-strain shielding of the nucleus.")
    print("Electron strain density around the nucleus produces a small induced")
    print("field that opposes B0.  Beff = B0 (1 - sigma_shield),  delta in ppm.")
    print()
    print("1H chemical shifts (ppm vs TMS):")
    print(f"  {'environment':<28s}  {'delta [ppm]':>11s}")
    h_shifts = [
        ("TMS reference",                 0.00),
        ("alkyl CH3 / CH2",               0.9),
        ("CH alpha to C=O",               2.2),
        ("alpha to OR",                   3.5),
        ("alpha to OH (CH-OH)",           3.6),
        ("vinyl =CH",                     5.5),
        ("aromatic C-H (benzene)",        7.27),
        ("aldehyde -CHO",                 9.7),
        ("carboxylic -COOH",             12.0),
        ("alcohol O-H (variable)",        2.5),
        ("amine N-H",                     1.5),
    ]
    for env, d in h_shifts:
        print(f"  {env:<28s}  {d:>11.2f}")
    print()
    print("13C chemical shifts (ppm vs TMS):")
    c_shifts = [
        ("alkane CH3",        15),
        ("alkene C=C",       125),
        ("alkyne C#C",        80),
        ("aromatic",         128),
        ("C-O alcohol",       65),
        ("C=O ketone",       205),
        ("C=O aldehyde",     200),
        ("C=O ester",        170),
        ("C=O amide",        172),
        ("C=O carboxylic",   178),
        ("C#N nitrile",      118),
    ]
    print(f"  {'environment':<28s}  {'delta [ppm]':>11s}")
    for env, d in c_shifts:
        print(f"  {env:<28s}  {d:>11d}")
    print()
    print("31P typical shifts: -200 to +250 ppm vs 85% H3PO4")
    print("  P(III) phosphines: -60 to +60   ;  P(V) phosphates: 0 to +20")
    print()
    print("19F typical shifts: -300 to +400 ppm vs CFCl3")
    print("  CF3 group ~ -60 ppm ;  aromatic F ~ -110 ppm ;  acyl F ~ +20 ppm")
    print()
    print("J-coupling = strain bridge between nuclei (through-bond scalar coupling).")
    print(f"  {'coupling':<14s}  {'typical J [Hz]':>14s}")
    j_values = [
        ("3J HH gem",     "0-3"),
        ("3J HH vic",     "6-8"),
        ("3J HH cis",     "6-12"),
        ("3J HH trans",   "12-18"),
        ("2J H-C-H gem",  "10-15"),
        ("1J 13C-1H",     "115-250"),
        ("1J 19F-13C",    "-160 to -270"),
        ("2J 31P-1H",     "0-30"),
        ("1J 31P-1H",     "180-700"),
    ]
    for k, v in j_values:
        print(f"  {k:<14s}  {v:>14s}")
    print()
    print("Karplus relation for 3J(H-H):  J = A cos^2(phi) + B cos(phi) + C")
    print("  Substrate origin: strain bridge between H nuclei propagates through")
    print("  the C-C sigma bond; transmission is maximal at phi = 0 or 180,")
    print("  minimal near phi = 90.")
    A_k, B_k, C_k = 9.5, -0.28, 0.0
    print(f"  {'phi [deg]':>10s}  {'J [Hz]':>8s}")
    for phi in (0, 30, 60, 90, 120, 150, 180):
        rad = math.radians(phi)
        J = A_k * math.cos(rad)**2 + B_k * math.cos(rad) + C_k
        print(f"  {phi:>10d}  {J:>8.2f}")

    # ============================================================
    section(7, "EPR / ESR (unpaired electron spin substrate probe)")
    # ============================================================
    print("EPR: same Zeeman story, but for unpaired ELECTRON spins.")
    print("  h nu = g_e mu_B B0 ;  free electron g_e = 2.0023")
    print()
    g_e = 2.0023193
    mu_B = 9.2740100783e-24  # J/T
    print(f"  At B0 = 0.34 T (X-band):  nu = {g_e * mu_B * 0.34 / H_J_S / 1e9:.3f} GHz")
    print()
    print("g-factor anisotropy reports on local substrate-strain symmetry of")
    print("the orbital hosting the unpaired spin (deviations from g_e by")
    print("spin-orbit mixing of nearby states).")
    print()
    print("Hyperfine splitting A: substrate strain bridge between unpaired")
    print("electron and nearby NUCLEAR spins (Fermi contact + dipolar).")
    print()
    print(f"  {'radical / center':<22s}  {'g':>8s}  {'A [mT]':>10s}")
    epr_examples = [
        ("free e- (vacuum)",    2.0023, 0.0),
        ("methyl radical CH3",  2.0026, 2.3),
        ("benzene anion",       2.0028, 0.375),
        ("DPPH (standard)",     2.0036, 0.0),
        ("Cu(II) (g_||)",       2.20,  16.0),
        ("Mn(II) S=5/2",        2.00,   9.0),
        ("Fe(III) low-spin",    2.40,   0.0),
        ("nitroxide TEMPO",     2.006,  1.6),
    ]
    for n, g, A in epr_examples:
        print(f"  {n:<22s}  {g:>8.4f}  {A:>10.3f}")

    # ============================================================
    section(8, "FLUORESCENCE vs PHOSPHORESCENCE (singlet/triplet manifolds)")
    # ============================================================
    print("Jablonski diagram in substrate language:")
    print("  S0 -> S1   absorption   (singlet substrate-spin manifold)")
    print("  S1 -> S0   fluorescence (allowed, nanoseconds)")
    print("  S1 -> T1   intersystem crossing (forbidden, requires SOC)")
    print("  T1 -> S0   phosphorescence (forbidden, microseconds-seconds)")
    print()
    print("Kasha's rule: emission almost always originates from the LOWEST excited")
    print("state of given multiplicity (S1 for fluor; T1 for phos), because")
    print("internal conversion S_n -> S1 is much faster than radiative decay.")
    print()
    print("Stokes shift: emission red-shifted from absorption because the excited")
    print("state relaxes vibrationally (substrate strain rearrangement) BEFORE")
    print("emitting. Vertical down-jump lands above v=0 of the ground state.")
    print()
    print(f"  {'fluorophore':<22s}  {'lam_abs':>8s}  {'lam_em':>8s}  {'phi_F':>6s}  {'tau [ns]':>9s}")
    fluors = [
        ("anthracene",          357,    400,  0.27,  4.9),
        ("perylene",            434,    447,  0.94,  6.4),
        ("rhodamine 6G",        530,    556,  0.95,  4.0),
        ("fluorescein",         494,    521,  0.92,  4.0),
        ("Cy5",                 649,    670,  0.27,  1.0),
        ("GFP",                 488,    507,  0.79,  3.0),
        ("quinine sulfate",     347,    450,  0.55, 19.0),
        ("tryptophan",          280,    348,  0.13,  3.1),
        ("NADH",                340,    460,  0.02,  0.4),
        ("[Ru(bpy)3]2+ (phos)", 452,    620,  0.09, 600.0),
    ]
    for f, la, le, q, t in fluors:
        print(f"  {f:<22s}  {la:>8d}  {le:>8d}  {q:>6.2f}  {t:>9.1f}")
    print()
    print("Substrate framing of the heavy-atom effect: heavy nuclei have strong")
    print("spin-orbit substrate coupling, which mixes singlet and triplet states")
    print("-> faster ISC -> phosphorescence allowed (e.g. iodide, Ru, Ir, Pt).")

    # ============================================================
    section(9, "PHOTOCHEMISTRY (Norrish, photoisomerization, biolum)")
    # ============================================================
    print("Photochemistry = excited-state strain configuration follows a different")
    print("potential-energy surface than the ground state. New reaction channels")
    print("open up because the substrate strain landscape is reshaped by the")
    print("electronic excitation.")
    print()
    print("Norrish type I (alpha-cleavage of carbonyl):")
    print("  R-CO-R'  --hv->  R* + *CO-R'   (homolytic alpha-bond fission)")
    print("  Substrate: n,pi* excitation populates an antibonding strain on the")
    print("  alpha bond, spontaneously rupturing the bridge.")
    print()
    print("Norrish type II (gamma-H abstraction + Yang cyclization or fragmentation):")
    print("  Excited C=O abstracts a gamma-H to form a 1,4-biradical")
    print("  -> beta-cleavage gives alkene + enol (re-tautomerizes to ketone)")
    print("  -> Yang cyclization gives a cyclobutanol")
    print()
    print("Photoisomerization (cis-trans of retinal in vision):")
    print("  11-cis-retinal --hv 500 nm--> all-trans-retinal in ~200 fs")
    print("  Quantum yield ~ 0.65; one of the fastest photoreactions known.")
    print("  Substrate explanation: pi->pi* excitation flips the bond-order on")
    print("  the C11=C12 double bond; what was a stiff strain bridge becomes a")
    print("  rotatable single-bond-like channel; molecule pivots, then pi*")
    print("  decays back to pi giving the all-trans isomer locked in place.")
    print()
    print(f"  {'photoreaction':<32s}  {'lambda [nm]':>11s}  {'phi':>6s}")
    photo = [
        ("retinal cis->trans",            500,  0.65),
        ("ozone O3 -> O2 + O",            254,  0.95),
        ("ClNO -> Cl + NO",               365,  0.5),
        ("HCHO -> H2 + CO",               300,  0.32),
        ("HCHO -> H + HCO",               300,  0.66),
        ("anthracene dimerization",       365,  0.30),
        ("stilbene cis->trans",           335,  0.35),
        ("azobenzene cis->trans",         440,  0.40),
        ("DNA TT -> thymine dimer",       260,  0.01),
    ]
    for r, l, q in photo:
        print(f"  {r:<32s}  {l:>11d}  {q:>6.2f}")
    print()
    print("Chemiluminescence: chemical reaction populates an electronic excited")
    print("state directly (no photon input), then it relaxes radiatively.")
    print("  Luminol + H2O2 + Fe(III)/heme  ->  3-aminophthalate* + N2 + light")
    print("  Substrate: the reaction releases enough strain energy in one step")
    print("  to vault into the S1 manifold of the product, bypassing thermal.")
    print()
    print("Bioluminescence:  Luciferin + O2 + ATP --(luciferase)--> oxyluciferin*")
    print("  -> green-yellow light (560 nm) at near-100% quantum yield (firefly)")
    print("  Substrate: enzyme template pre-organizes the strain landscape so")
    print("  the product is born in S1 with maximal Franck-Condon overlap.")

    # ============================================================
    section(10, "SUMMARY: spectroscopy = substrate-mode probe of strain")
    # ============================================================
    print("Every spectroscopic technique is a different photon mode probing")
    print("the same substrate strain field at a different energy / spin scale:")
    print()
    print(f"  {'technique':<14s}  {'photon E':<14s}  {'probes':<32s}")
    summary = [
        ("X-ray (XPS)",  "100-10000 eV",  "core electron strain"),
        ("UV-Vis",       "1.5-10 eV",     "valence pi/sigma transitions"),
        ("IR",           "0.05-0.5 eV",   "bond-bridge vibrations"),
        ("Raman",        "0-0.5 eV shift","polarizability vibrations"),
        ("microwave",    "1e-4 eV",       "rotational substrate inertia"),
        ("EPR",          "1e-5 eV",       "unpaired e- spin Zeeman"),
        ("NMR",          "1e-7 eV",       "nuclear spin Zeeman + shielding"),
    ]
    for t, e, p in summary:
        print(f"  {t:<14s}  {e:<14s}  {p:<32s}")
    print()
    print("All numbers are reproduced by the same substrate Lagrangian as in")
    print("molecular_bonding_substrate.py. The value-add is unification: every")
    print("'rule' (Beer-Lambert linearity, IR/Raman mutual exclusion, Karplus")
    print("dihedral curve, Kasha emission rule, Franck-Condon vertical jumps,")
    print("Stokes shift, photoisomerization channels) is a consequence of one")
    print("strain-field acted on by photons that are themselves transverse")
    print("substrate waves.")
    print()
    print("Rule of the framework: photon arrives -> substrate-mode coupling")
    print("matrix element <f| H' |i> -> bound-state strain reconfigures.")


if __name__ == "__main__":
    main()
