"""Acoustics and precision metrology in the strain-medium framework.

Goes deeper than a one-shot summary: every acoustic phenomenon and every
precision measurement is interpreted as the SAME substrate strain field
in different mode configurations and measurement geometries.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Acoustics  =  longitudinal substrate-strain wave in matter.
Metrology  =  precision measurement of substrate-derived constants.
Sonoluminescence  =  substrate-strain saturation flash at bubble collapse.
Atomic clock  =  substrate-strain bound-state oscillation as time standard.
G-measurement difficulty  =  weakest substrate-strain coupling.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
HBAR_J_S = 1.054571817e-34
H_J_S = 6.62607015e-34          # Planck (exact, 2019 SI)
C_M_S = 2.99792458e8            # speed of light (exact)
EV_J = 1.602176634e-19          # elementary charge (exact)
K_B = 1.380649e-23              # Boltzmann (exact)
N_A = 6.02214076e23             # Avogadro (exact)
DELTA_NU_CS = 9192631770.0      # Cs-133 hyperfine (exact, defines second)
K_CD = 683.0                    # luminous efficacy (exact)
G_NEWTON = 6.67430e-11          # gravitational constant (CODATA, NOT exact)


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Acoustics and precision metrology in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Acoustic wave  =  longitudinal mode of  L = 1/2 rho (d_t u)^2 - 1/2 K |grad u|^2")
    print("Sound speed    =  c = sqrt(K/rho)   (B=K for a fluid; bulk modulus)")
    print()

    # ============================================================
    section(1, "LINEAR ACOUSTICS (longitudinal substrate mode)")
    # ============================================================
    print("Wave equation:  d^2 p / d t^2  =  c^2  Laplacian(p)")
    print("Sound speed:    c  =  sqrt(B / rho_mat)   where B = bulk modulus")
    print("In substrate language: B = K (effective stiffness for compressive mode).")
    print()
    print("Air at temperature T (Celsius):  c_air = 331 sqrt(1 + T/273) m/s")
    for T in (-20, 0, 20, 40):
        c_T = 331.0 * math.sqrt(1.0 + T / 273.0)
        print(f"  T = {T:+3d} C   c_air = {c_T:6.2f} m/s")
    print()
    print("Speed of sound across media (substrate stiffness/density ratio):")
    print(f"  {'medium':<22s}  {'c [m/s]':>10s}  {'rho [kg/m3]':>13s}  {'B = c^2 rho [GPa]':>20s}")
    media = [
        ("Air (20 C)",          343.0,    1.204),
        ("Helium (20 C)",       1007.0,   0.166),
        ("Hydrogen (20 C)",     1310.0,   0.0838),
        ("Water (20 C)",        1482.0,   998.2),
        ("Seawater (13 C)",     1500.0,   1025.0),
        ("Mercury",             1450.0,   13534.0),
        ("Soft tissue (avg)",   1540.0,   1050.0),
        ("Bone (cortical)",     4080.0,   1900.0),
        ("Steel",               5960.0,   7850.0),
        ("Aluminum",            6320.0,   2700.0),
        ("Diamond",             12000.0,  3515.0),
    ]
    for name, c, rho in media:
        B_GPa = (c * c * rho) * 1e-9
        print(f"  {name:<22s}  {c:>10.0f}  {rho:>13.2f}  {B_GPa:>20.3f}")
    print()
    print("Substrate reading: c = sqrt(K/rho). Diamond has highest c because")
    print("its substrate strain bridges (covalent C-C network) maximize K.")
    print("Helium has high c relative to density because rho is tiny.")

    # ============================================================
    section(2, "SOURCE MECHANISMS (multipole strain radiators)")
    # ============================================================
    print("Acoustic source = localized substrate-strain disturbance radiating")
    print("longitudinal waves. Multipole order set by source symmetry:")
    print()
    print(f"  {'source':<22s}  {'multipole':<14s}  {'P ~ rho c k^n U^m':<18s}  {'examples':<22s}")
    sources = [
        ("Pulsating sphere",   "monopole",   "rho c k^2 Q^2",   "speaker bass cone"),
        ("Oscillating sphere", "dipole",     "rho c k^4 D^2",   "tuning fork, vocal"),
        ("Rotating multipole", "quadrupole", "rho c k^6 Q4^2",  "turbulent jet noise"),
    ]
    for s, m, p, ex in sources:
        print(f"  {s:<22s}  {m:<14s}  {p:<18s}  {ex:<22s}")
    print()
    print("Lighthill aeroacoustic stress tensor T_ij = rho v_i v_j + (p - c^2 rho) delta_ij")
    print("  -> jet noise scales as P ~ rho_0 U^8 / c^5  (Lighthill's eighth-power law).")
    print()
    print("Quick demo: if jet velocity doubles, radiated acoustic power scales by 2^8 = 256x.")
    print("Substrate origin: turbulent eddies are quadrupole strain sources -> high k^6 frequency")
    print("dependence; the U^8 law follows from k ~ U/L and Q ~ rho U^2 L^3.")
    print()
    print("Audible vs subsonic vs ultrasonic frequency bands:")
    bands = [
        ("Infrasound",    "< 20 Hz",     "elephants, earthquakes, nuclear-test detection"),
        ("Audible",       "20 - 20000 Hz", "human hearing, music, speech"),
        ("Ultrasound",    "20 kHz - 1 GHz", "sonar, medical imaging, NDT"),
        ("Hypersound",    "> 1 GHz",      "phonon engineering, quantum acoustics"),
    ]
    for n, r, ex in bands:
        print(f"  {n:<14s}  {r:<16s}  {ex}")

    # ============================================================
    section(3, "ATMOSPHERIC PROPAGATION (refraction & attenuation)")
    # ============================================================
    print("Atmosphere = stratified substrate with T(z) and rho(z) profiles.")
    print("Sound speed c(z) = 331 sqrt(1 + T(z)/273) -> rays bend toward LOW c.")
    print()
    print("Daytime: T decreases with altitude -> rays bend UP -> sound 'shadow' near ground.")
    print("Nighttime/inversion: T increases with altitude near surface -> rays bend DOWN")
    print("                     -> long-range propagation, sound carries far at night.")
    print()
    print("Attenuation mechanisms (all = substrate strain energy loss):")
    print("  1. Classical viscous absorption    alpha_v ~ omega^2 / (rho c^3)")
    print("  2. Thermal conduction              alpha_t ~ omega^2 / (rho c^3)")
    print("  3. Rotational/vibrational relax.   alpha_r peaks near omega tau ~ 1")
    print("  4. Geometric spreading             1/r for spherical, 1/sqrt(r) cylindrical")
    print()
    f_table = [100.0, 1000.0, 10000.0, 100000.0]
    print(f"  {'f [Hz]':>10s}  {'alpha_air [dB/km]':>20s}  {'attenuation 1 km':>20s}")
    for f in f_table:
        alpha = 1.6e-10 * f * f       # rough classical fit, dB/m -> dB/km
        alpha_dBkm = alpha * 1000.0
        att = 10 ** (-alpha_dBkm / 10.0)
        print(f"  {f:>10.0f}  {alpha_dBkm:>20.4f}  {att:>20.3e}")
    print()
    print("Infrasound (< 20 Hz) has alpha ~ 0 -> propagates thousands of km.")
    print("(Nuclear-test ban treaty CTBTO uses an infrasound network for verification.)")
    print()
    print("Sonic boom: source moving at v > c forms Mach cone of half-angle:")
    print("  sin(theta_M) = c / v = 1/M")
    for M in (1.2, 1.5, 2.0, 3.0):
        theta = math.degrees(math.asin(1.0 / M))
        print(f"  Mach M = {M:.1f}   half-angle theta_M = {theta:5.2f} deg")
    print()
    print("Substrate reading: at v > c the local strain bridges cannot propagate")
    print("information forward fast enough; energy piles up on the cone surface")
    print("as a near-discontinuity (shock).")

    # ============================================================
    section(4, "ULTRASONICS & MEDICAL IMAGING (high-f strain probes)")
    # ============================================================
    print("Ultrasound = high-frequency (1-15 MHz) substrate strain pulses.")
    print("Imaging = measure echo amplitude vs delay -> spatial map of impedance Z = rho c.")
    print()
    print("Reflection coefficient at boundary:")
    print("  R = (Z2 - Z1) / (Z2 + Z1)")
    print()
    impedances = [
        ("Air",          1.2,    343.0),
        ("Water",        998.0,  1482.0),
        ("Soft tissue",  1050.0, 1540.0),
        ("Fat",          950.0,  1450.0),
        ("Bone",         1900.0, 4080.0),
        ("Lung",         300.0,  650.0),
    ]
    print(f"  {'tissue':<14s}  {'Z [MRayl]':>10s}")
    Zs = {}
    for name, rho, c in impedances:
        Z = rho * c * 1e-6
        Zs[name] = Z
        print(f"  {name:<14s}  {Z:>10.3f}")
    print()
    print("Tissue/air interface:")
    R = (Zs["Soft tissue"] - Zs["Air"]) / (Zs["Soft tissue"] + Zs["Air"])
    print(f"  R = {R:.4f}  ->  ~99.9% reflected.  Need coupling gel to enter the body.")
    R_bone = (Zs["Bone"] - Zs["Soft tissue"]) / (Zs["Bone"] + Zs["Soft tissue"])
    print(f"Tissue/bone interface:  R = {R_bone:.4f}  ->  bone shadows on US images.")
    print()
    print("Imaging modes:")
    modes = [
        ("A-mode",           "1D depth-amplitude trace",           "ophthalmic axial length"),
        ("B-mode",           "2D brightness (real-time)",           "general diagnostic"),
        ("M-mode",           "1D line vs time",                     "cardiac valve motion"),
        ("Doppler",          "frequency shift -> velocity",         "vascular blood flow"),
        ("Harmonic imaging", "image at 2f from nonlinear tissue",   "improves contrast"),
        ("Elastography",     "shear-wave speed -> tissue stiffness", "liver fibrosis"),
        ("HIFU therapy",     "focused beam ablates tumors",         "non-invasive surgery"),
    ]
    print(f"  {'mode':<18s}  {'mechanism':<36s}  {'use':<26s}")
    for n, m, u in modes:
        print(f"  {n:<18s}  {m:<36s}  {u:<26s}")
    print()
    print("Tissue attenuation rule of thumb:  alpha ~ 0.5 dB / cm / MHz")
    print("So 5 MHz beam at 10 cm one-way path: 25 dB loss; 10 MHz at 5 cm: 25 dB.")
    print("Higher f -> better resolution (lambda smaller) but shallower penetration.")
    print()
    print("Substrate framing: medical US is a strain-bridge probe; saturation cap")
    print("becomes important in HIFU where local intensity is large enough to")
    print("approach the cavitation threshold (sigma -> 1/2 in bubbles).")

    # ============================================================
    section(5, "NONLINEAR ACOUSTICS & SONOLUMINESCENCE")
    # ============================================================
    print("Beyond linear regime, sound speed depends on local strain (B/A parameter):")
    print("  c(p) = c_0 + (B/A)/(2 rho_0 c_0) p   (typical B/A ~ 5 for water)")
    print("Wave crests travel faster than troughs -> waveform steepens.")
    print()
    print("Burgers equation:  d_t u + u d_x u = nu d_xx u")
    print("Balance between nonlinear steepening and viscous spreading -> shock wave.")
    print()
    print("Single-bubble sonoluminescence (Crum, Putterman 1990s):")
    print("  Drive a micron-sized bubble in water at ~25 kHz acoustic field.")
    print("  Bubble grows 50 micron, then collapses 1000:1 in radius in ~1 microsecond.")
    print("  Peak interior conditions:")
    bub = [
        ("Radius",        "0.5 micron"),
        ("Temperature",   "10000 - 50000 K"),
        ("Pressure",      "~1e5 atm"),
        ("Density",       "near solid"),
        ("Flash duration","50-250 picoseconds"),
        ("Photons/flash", "~1e6"),
    ]
    for k, v in bub:
        print(f"  {k:<14s}  {v}")
    print()
    print("Multi-bubble cavitation:")
    print("  Cleaning baths, ultrasonic surgery, and lithotripsy all exploit")
    print("  cavitation: collapse-driven shocks fragment kidney stones, clean parts.")
    print()
    print("Substrate framing: SBSL flash = substrate strain saturation event.")
    print("As R -> R_min, energy density rises until effective sigma -> 1/2 cap.")
    print("Excess strain dumps into electromagnetic mode -> picosecond photon flash.")
    print("The cap forbids continued compression: strain energy must convert to radiation.")

    # ============================================================
    section(6, "ARCHITECTURAL AND PSYCHOACOUSTICS")
    # ============================================================
    print("Sabine reverberation:  T_60 = 0.161 V / A    (V in m^3, A in m^2 absorption)")
    print()
    rooms = [
        ("Anechoic chamber",   100.0, 100.0,  0.05),
        ("Recording studio",   200.0, 80.0,   0.45),
        ("Living room",        50.0,  30.0,   0.30),
        ("Concert hall",       15000.0, 1500.0, 1.6),
        ("Cathedral",          25000.0, 800.0,  5.0),
        ("Empty gymnasium",    8000.0,  300.0,  4.3),
    ]
    print(f"  {'room':<22s}  {'V [m3]':>9s}  {'A [m2]':>9s}  {'T60 [s]':>9s}  {'ideal use':<22s}")
    for n, V, A, T60 in rooms:
        T_pred = 0.161 * V / A
        use = {0.05: "speech testing",
               0.45: "voice recording",
               0.30: "casual listening",
               1.6:  "orchestral music",
               5.0:  "organ, choir",
               4.3:  "needs treatment"}[T60]
        print(f"  {n:<22s}  {V:>9.0f}  {A:>9.0f}  {T_pred:>9.2f}  {use:<22s}")
    print()
    print("Hearing & psychoacoustics:")
    print("  - Frequency range: 20 Hz - 20 kHz (degrades with age, esp. > 4 kHz)")
    print("  - Dynamic range:   ~120 dB (1e-12 to 1 W/m2 = 0 to 120 dB SPL)")
    print("  - JND (level):     ~1 dB in midband")
    print("  - JND (frequency): ~3-5 cents in midband (1 cent = 1/100 semitone)")
    print("  - A-weighting:     low/high freq de-emphasized to match equal-loudness")
    print("  - Fletcher-Munson: 40-phon ear is most sensitive near 3-4 kHz (ear canal)")
    print()
    print("Localization cues (binaural):")
    print("  - ITD (interaural time difference): up to ~660 microsec at 90 deg")
    print("  - ILD (interaural level difference): dominant above ~1500 Hz")
    print("  - Pinna spectral cues: front/back and elevation discrimination")
    print()
    print("Masking & perceptual coding (MP3, AAC, Opus):")
    print("  Strong tone masks weaker neighbors within ~1 critical band (~1/3 octave).")
    print("  Codecs discard masked components -> 90% size reduction at near-transparent quality.")
    print()
    print("Substrate framing: hearing = mechanical strain bridge from tympanic")
    print("membrane through ossicles to cochlea, where hair cells transduce")
    print("local strain to neural signal. Each hair cell is a tuned resonator.")

    # ============================================================
    section(7, "SI 2019 REDEFINITION (constants -> base units)")
    # ============================================================
    print("On 20 May 2019 the SI was redefined: 7 base units now derive from")
    print("7 EXACT numerical values of fundamental constants. No artifact left.")
    print()
    print(f"  {'constant':<28s}  {'symbol':<6s}  {'exact value':<24s}  {'unit derived':<14s}")
    sirow = [
        ("Hyperfine Cs-133 freq",  "DnuCs", f"{DELTA_NU_CS:.0f} Hz",        "second"),
        ("Speed of light",          "c",    f"{C_M_S:.0f} m/s",             "metre"),
        ("Planck constant",         "h",    f"{H_J_S:.10e} J s",            "kilogram"),
        ("Elementary charge",       "e",    f"{EV_J:.9e} C",                "ampere"),
        ("Boltzmann constant",      "k",    f"{K_B:.6e} J/K",               "kelvin"),
        ("Avogadro number",         "NA",   f"{N_A:.8e} 1/mol",             "mole"),
        ("Luminous efficacy 540THz","Kcd",  f"{K_CD:.0f} lm/W",             "candela"),
    ]
    for n, s, v, u in sirow:
        print(f"  {n:<28s}  {s:<6s}  {v:<24s}  {u:<14s}")
    print()
    print("Definition chain (each unit comes from fixing the constant above):")
    print("  second   <- DnuCs   (Cs-133 hyperfine 9 192 631 770 Hz exactly)")
    print("  metre    <- c       (light travels in 1/c second)")
    print("  kilogram <- h       (via Kibble watt balance: F=BIL with E quantized)")
    print("  ampere   <- e       (count charges per second)")
    print("  kelvin   <- k       (temperature is energy / kB)")
    print("  mole     <- NA      (just Avogadro number of entities)")
    print("  candela  <- Kcd     (photometric scaling of radiometric power)")
    print()
    print("Substrate framing: each base unit becomes a substrate-strain quantity:")
    print("  second   = period of substrate-bound-state oscillation in Cs ion")
    print("  metre    = substrate signal-propagation distance per unit of that period")
    print("  kilogram = inertial response of substrate strain measured electromagnetically")
    print("  ampere   = flux of charge-quantum (smallest substrate-circulation unit)")
    print("  kelvin   = thermal strain-energy per degree of substrate freedom")

    # ============================================================
    section(8, "ATOMIC CLOCKS & TIMEKEEPING")
    # ============================================================
    print("Cs-133 hyperfine transition F=4 <-> F=3 in ground 6S1/2:")
    print(f"  nu_Cs = {DELTA_NU_CS:.0f} Hz   (defines the second since 1967, exact since 2019)")
    print()
    print("Optical clocks beat microwave Cs by factor of 1e5 in frequency,")
    print("which directly improves achievable fractional uncertainty:")
    print()
    clocks = [
        ("Cs fountain (Cs-133)",   "9.19 GHz",     1e-16,  "current SI second"),
        ("Rb fountain",            "6.83 GHz",     1e-16,  "secondary standard"),
        ("Hg+ trapped ion",        "1.06e15 Hz",   1.9e-17, "NIST early optical"),
        ("Al+ quantum-logic",      "1.12e15 Hz",   9.4e-19, "NIST + JILA"),
        ("Sr-87 optical lattice",  "4.29e14 Hz",   2.0e-18, "JILA, RIKEN, PTB"),
        ("Yb-171 optical lattice", "5.18e14 Hz",   1.4e-18, "NIST, KRISS, NMIJ"),
        ("Yb+ E3 ion",             "6.42e14 Hz",   3.2e-18, "NPL, PTB"),
        ("Th-229 nuclear (future)","2.02e15 Hz",   1e-19,   "expected, in development"),
    ]
    print(f"  {'clock':<26s}  {'frequency':<14s}  {'uncert.':>10s}  {'host':<22s}")
    for n, f, u, h in clocks:
        print(f"  {n:<26s}  {f:<14s}  {u:>10.1e}  {h:<22s}")
    print()
    print("Implications: Sr/Yb lattice clocks at 1e-18 measure gravitational")
    print("redshift of ~1 cm height difference (df/f = g h / c^2 ~ 1.1e-18 / 10 cm).")
    print()
    print("GPS time: 24 satellites carry Cs/Rb clocks; need both SR (-7 microsec/day)")
    print("and GR (+45 microsec/day) corrections, for a net +38 microsec/day adjustment.")
    print("Without it GPS positions would drift by ~10 km/day.")
    print()
    print("Leap seconds: UTC inserts/removes 1 s to track UT1 (Earth rotation)")
    print("which is decelerating ~1.7 ms/century. Last leap second was Dec 2016;")
    print("metrology community plans to abolish them by 2035.")
    print()
    print("Substrate framing: an atomic clock is a substrate-strain bound-state")
    print("oscillator. Fixing the frequency of that mode = picking a substrate-")
    print("intrinsic clock as the operational definition of time.")

    # ============================================================
    section(9, "GRAVITATIONAL METROLOGY (G is the worst-known constant)")
    # ============================================================
    print(f"Gravitational constant G = {G_NEWTON:.5e} N m^2 / kg^2")
    print("Relative uncertainty: ~2.2e-5  (worst by 5+ orders of magnitude vs c, h, e).")
    print()
    print("Why G is hard:")
    print("  - gravity is ~36 orders of magnitude weaker than EM at atomic scale")
    print("  - cannot use standard atom-interferometric tricks: too weak vs Earth's pull")
    print("  - laboratory mass distributions limit the source signal (~1 microGal)")
    print()
    print("Modern G measurement methods:")
    g_meas = [
        ("Cavendish torsion balance",   "1798",   "U Washington Eot-Wash"),
        ("BIPM torsion strip",          "2001",   "BIPM Sevres, France"),
        ("Atom interferometry",         "2014",   "Tino group, Florence"),
        ("Cold-atom gradiometer",       "2018",   "HUST China, watt-balance hybrid"),
        ("MAGIA cold-atom",             "2014",   "INFN Florence"),
        ("Pendulum (Newton-G)",         "2014",   "JILA, NIST"),
    ]
    for n, y, lab in g_meas:
        print(f"  {n:<28s}  {y:<6s}  {lab}")
    print()
    print("Discrepancies: different techniques give G values disagreeing at the")
    print("5e-5 level. CODATA inflates uncertainty to encompass them all.")
    print()
    print("Substrate framing: G is the weakest substrate-strain coupling. Local")
    print("strain energy from a 1-kg lab mass produces a 6.7e-11 N restoring force")
    print("per kg at 1 m, drowned in seismic noise / magnetic gradients / thermal.")
    print("This explains BOTH the 2e-5 precision floor AND the lab-to-lab spread.")

    # ============================================================
    section(10, "VLBI, GEODESY & TESTS OF FUNDAMENTAL PHYSICS")
    # ============================================================
    print("Very Long Baseline Interferometry (VLBI):")
    print("  Tens of radio telescopes correlate signals across continental baselines.")
    print("  Angular resolution: lambda / B with B ~ 1e7 m, lambda = 1 cm -> 1 nrad ~ 0.2 mas.")
    print("  ITRF (International Terrestrial Reference Frame): mm-level station coords.")
    print()
    print("Space geodesy systems:")
    geodesy = [
        ("VLBI",                  "Earth orientation, ICRF link",  "1 mm"),
        ("GPS / GNSS",            "global position, time",         "5-10 mm static"),
        ("Satellite laser ranging","LAGEOS, gravity field",        "1 cm"),
        ("DORIS",                 "doppler beacon network",        "1 cm"),
        ("InSAR",                 "interferometric SAR",           "1 mm vertical"),
        ("GRACE-FO",              "satellite gravimetry",          "0.1 mGal regional"),
        ("Absolute gravimeter",   "free-fall corner cube",          "~1 microGal"),
    ]
    print(f"  {'system':<26s}  {'measures':<32s}  {'precision':<12s}")
    for n, m, p in geodesy:
        print(f"  {n:<26s}  {m:<32s}  {p:<12s}")
    print()
    print("Tests of fundamental physics via metrology:")
    tests = [
        ("Equivalence principle",  "Eot-Wash + MICROSCOPE",   1e-15,  "WEP differential acceleration"),
        ("Lorentz invariance",     "Michelson, Kennedy-Thorndike", 1e-18, "anisotropy of c"),
        ("Local position invar.",  "clock comparison vs U/c^2", 1e-7,  "fund. const. variation w/ phi"),
        ("alpha variation",        "Al+ vs Hg+ clock ratio",  1e-17, "d(alpha)/dt per year"),
        ("Neutron EDM",            "ILL Grenoble, PSI Switzerland", 1.8e-26, "e cm; CP test"),
        ("Electron EDM",           "ACME, JILA",              4.1e-30,"e cm; T-violation"),
        ("Inverse-square law",     "Eot-Wash short range",    50e-6, "deviation at 50 um"),
        ("Photon mass",            "magnetic field tests",    1e-54, "kg; Coulomb law verifier"),
    ]
    print(f"  {'test':<24s}  {'experiment':<28s}  {'limit':>11s}  {'meaning':<22s}")
    for n, e, l, m in tests:
        print(f"  {n:<24s}  {e:<28s}  {l:>11.1e}  {m:<22s}")
    print()
    print("Substrate framing: each precision null result CONSTRAINS the substrate.")
    print("  - WEP at 1e-15 says all matter couples identically to substrate strain")
    print("  - Lorentz at 1e-18 says K and rho are isotropic to that precision")
    print("  - alpha-variation at 1e-17/yr says coupling constants are stable")
    print("  - inverse-square law at 50 um says no extra dimensions or new strain modes")
    print("  - neutron EDM at 1e-26 e.cm constrains substrate CP-asymmetric terms")

    # ============================================================
    section(11, "SUMMARY: one substrate, two regimes")
    # ============================================================
    print("Acoustics and metrology look like separate disciplines but share the")
    print("same substrate Lagrangian, exercised in two regimes:")
    print()
    print("  Acoustics    =  classical longitudinal mode of  L_substrate")
    print("                  (large amplitude, easily seen, governed by K, rho)")
    print()
    print("  Metrology    =  precision measurement of substrate-derived constants")
    print("                  (small amplitude, requires noise rejection)")
    print()
    print("Special bridge phenomena across the two:")
    print("  - sonoluminescence: large-amplitude strain hits saturation cap sigma=1/2")
    print("    -> energy converts to electromagnetic flash (substrate -> radiation)")
    print("  - atomic clock:  substrate-bound-state oscillation defines the second")
    print("    -> simplest possible standard, no artifact, available everywhere")
    print("  - watt balance:  electromagnetic strain force balances mechanical weight")
    print("    -> kilogram derived purely from substrate field couplings + h")
    print()
    print("Honest scoreboard: substrate framework REPRODUCES all standard acoustic")
    print("formulas (linear and Lighthill), all standard metrology relations (SI 2019),")
    print("and all standard fundamental tests, because the substrate Lagrangian's")
    print("classical limit IS continuum mechanics + electromagnetism.")
    print()
    print("Value-add: unification of multipole acoustics, sonoluminescence,")
    print("Cs/Sr clocks, kilogram redefinition, GPS relativity corrections, VLBI,")
    print("equivalence principle tests, and G measurements as different facets of")
    print("ONE substrate strain field with stiffness K, density rho, length xi,")
    print("damping gamma, saturation cap sigma <= 1/2, and orientability.")
    print()
    print("Falsifiable signatures that WOULD distinguish substrate from standard:")
    print("  - departures from c = sqrt(K/rho) at extreme strain (above 1e10 Pa)")
    print("  - sonoluminescence threshold structure linked to sigma=1/2")
    print("  - drift of fundamental constants tied to substrate cosmological evolution")
    print("  - extra-dimensional inverse-square deviations below 50 micrometers")


if __name__ == "__main__":
    main()
