"""Stellar physics, evolution, and supernovae in the strain-medium framework.

Stars  =  self-gravitating substrate-strain configurations balancing thermal
and radiation pressure (outward strain) against gravity (inward strain).
Nuclear burning  =  K_4 fusion reorganization releasing  epsilon_face * N
quanta of strain energy per cycle.
Saturation  sigma -> 1/2  defines the black-hole horizon (full-strain wall).

Strain-medium primitives (4 + cap):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap  sigma <= 1/2.

Honest framing: substrate REPRODUCES standard stellar-structure numbers
because the bound-state spectrum of self-gravitating strain matter is
the Lane-Emden / TOV equation in the appropriate limit. Value-add =
unification of pressure/degeneracy/horizon as ONE saturation phenomenon.
"""

from __future__ import annotations
import math


# ---- universal constants (SI unless noted) ----
G = 6.67430e-11
C = 2.998e8
HBAR = 1.054571817e-34
K_B = 1.380649e-23
SIGMA_SB = 5.670374419e-8
M_PROTON = 1.67262192e-27
M_ELECTRON = 9.1093837015e-31
M_NEUTRON = 1.67492749e-27
M_SUN = 1.98892e30
R_SUN = 6.957e8
L_SUN = 3.828e26
T_SUN = 5772.0
PC_M = 3.0857e16
YEAR_S = 3.15576e7
GYR_S = 1.0e9 * YEAR_S
EV_J = 1.602176634e-19
MEV_J = 1.0e6 * EV_J


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Stellar physics, evolution, and supernovae in strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma <= 1/2")
    print("Star = self-gravitating strain configuration in pressure equilibrium")
    print("Burning = K_4 strain reorganization releasing epsilon_face * N quanta")
    print("Black hole = saturation sigma -> 1/2 (future cone tilts past 90 deg)")
    print()

    # ============================================================
    section(1, "STELLAR STRUCTURE EQUATIONS (strain pressure balance)")
    # ============================================================
    print("Four coupled ODEs in radius r govern any spherical star:")
    print()
    print("  (1) Hydrostatic equilibrium:   dP/dr   = -G M(r) rho(r) / r^2")
    print("  (2) Mass continuity:           dM/dr   =  4 pi r^2 rho(r)")
    print("  (3) Energy generation:         dL/dr   =  4 pi r^2 rho(r) eps(r)")
    print("  (4) Energy transport (rad):    dT/dr   = -3 kappa rho L / (16 pi a c r^2 T^3)")
    print()
    print("Substrate reading:")
    print("  P    = strain-density pressure (thermal + radiation + degenerate)")
    print("  rho  = mass-strain density")
    print("  eps  = K_4 face reorganization rate (nuclear epsilon_nuc + grav)")
    print("  L    = outward strain-energy flux carried by photon/neutrino modes")
    print("  kappa= opacity = inverse mean free path of strain modes")
    print()
    print("Boundary conditions: M(0)=0, L(0)=0; P(R)=0, T(R)=T_eff at surface.")
    print()
    print("Dimensional sanity at solar center (Eddington estimate):")
    P_c = G * M_SUN ** 2 / R_SUN ** 4
    rho_c_est = 3.0 * M_SUN / (4.0 * math.pi * R_SUN ** 3) * 50  # ~150 g/cc
    T_c_est = P_c * M_PROTON / (rho_c_est * K_B)
    print(f"  P_c ~ G M^2 / R^4    = {P_c:.3e} Pa     (measured ~2.5e16)")
    print(f"  rho_c ~ 50 <rho>     = {rho_c_est:.1e} kg/m^3  (measured ~1.5e5)")
    print(f"  T_c  ~ P mu / (rho k)= {T_c_est:.2e} K     (measured ~1.57e7)")
    print()
    print("Convective transport replaces eqn (4) where Schwarzschild criterion is")
    print("violated (|d ln T / d ln P| > (gamma-1)/gamma). Substrate: convection =")
    print("bulk strain transport when the radiative gradient exceeds the cap.")

    # ============================================================
    section(2, "MAIN SEQUENCE: M-L, M-R, lifetime")
    # ============================================================
    print("Hydrogen-burning core in approximate homologous equilibrium gives")
    print("scaling laws (with break around 1 M_sun between pp and CNO):")
    print()
    print("  L  ~  M^3.5     (radiative envelope, mid-mass)")
    print("  R  ~  M^0.7     (low-mass)  ;  R ~ M^0.5 (high-mass)")
    print("  T_eff ~ M^0.5")
    print("  tau_MS = E_avail / L  ~  (M c^2 * 0.007 * 0.1) / L  ~  M^-2.5")
    print()
    print(f"  {'Star':<14s}  {'M [Msun]':>9s}  {'L [Lsun]':>10s}  {'R [Rsun]':>9s}  {'tau_MS':>10s}")
    ms = [
        ("M5V red dwarf", 0.20,    0.005, 0.30, "1000 Gyr"),
        ("K5V",           0.70,    0.16,  0.72,  "70 Gyr"),
        ("Sun (G2V)",     1.00,    1.00,  1.00,  "10 Gyr"),
        ("F5V",           1.40,    3.5,   1.30,  "4 Gyr"),
        ("A0V Vega",      2.10,   40.0,   2.30,  "0.5 Gyr"),
        ("B5V",           5.40,   600.0,  3.40,  "94 Myr"),
        ("O9V",          20.0,    52000.0, 7.40, "8 Myr"),
        ("O3V",          60.0,    790000.0,13.5, "3 Myr"),
    ]
    for n, m, l, r, t in ms:
        print(f"  {n:<14s}  {m:>9.2f}  {l:>10.3g}  {r:>9.2f}  {t:>10s}")
    print()
    print("Cross-check L = M^3.5 prediction:")
    for m, l_obs in [(0.2, 0.005), (1.0, 1.0), (5.4, 600), (20.0, 52000)]:
        l_pred = m ** 3.5
        err = (l_pred - l_obs) / l_obs * 100
        print(f"  M={m:5.2f}  L_pred={l_pred:10.2f}  L_obs={l_obs:10.2f}  err={err:+6.1f}%")
    print()
    print("Substrate: more strain mass -> deeper gravitational strain well ->")
    print("higher core T (steeper P gradient) -> nuclear rate eps ~ T^4 (pp) or")
    print("T^17 (CNO) -> super-linear L. The cap on radiative flux (Eddington)")
    print("eventually wins for very massive stars: L_Edd = 4 pi G M c / kappa.")
    L_Edd_per_M = 4.0 * math.pi * G * C / 0.34   # opacity ~ 0.34 m^2/kg (electron sc.)
    print(f"  Eddington luminosity / M = {L_Edd_per_M:.3e} W / kg")
    print(f"  L_Edd (1 Msun)           = {L_Edd_per_M*M_SUN/L_SUN:.3e} L_sun")

    # ============================================================
    section(3, "NUCLEAR BURNING STAGES (K_4 face reorganization)")
    # ============================================================
    print("Each burning stage releases substrate strain energy by reorganizing")
    print("baryon faces into a more bound (fewer-face) configuration.")
    print()
    print(f"  {'stage':<14s}  {'fuel->ash':<16s}  {'T_ign [K]':>10s}  {'Q [MeV]':>8s}  {'duration':>10s}")
    stages = [
        ("pp chain",     "4 H -> He4",       1.5e7,  26.7,  "10 Gyr"),
        ("CNO cycle",    "4 H -> He4 (cat)", 1.7e7,  25.0,  "1 Gyr"),
        ("3-alpha",      "3 He4 -> C12",     1.0e8,   7.3,  "1 Myr"),
        ("C burning",    "2 C12 -> Mg/Ne",   6.0e8,  13.9,  "1000 yr"),
        ("Ne burning",   "Ne20 -> O+Mg",     1.2e9,   4.0,  "1 yr"),
        ("O burning",    "2 O16 -> Si",      1.5e9,  16.5,  "180 days"),
        ("Si burning",   "Si28 -> Fe56",     2.7e9,  ~0,    "1 day"),
    ]
    # cleanup the ~0
    for name, fa, t, q, dur in stages:
        qstr = f"{q}" if isinstance(q, (int, float)) else str(q)
        print(f"  {name:<14s}  {fa:<16s}  {t:>10.1e}  {qstr:>8}  {dur:>10s}")
    print()
    print("Iron-56 is the substrate strain minimum per nucleon (8.79 MeV/A).")
    print("No K_4 reorganization beyond Fe releases energy -> core collapses.")
    print()
    print("pp-chain step (substrate epsilon_face * 4 protons -> He4):")
    Q_pp = 26.73
    eta_solar = 0.007
    print(f"  Q(4H -> He4) = {Q_pp:.2f} MeV  =  {Q_pp*EV_J*1e6:.3e} J")
    print(f"  efficiency   = (Q / 4 m_p c^2) = {Q_pp*MEV_J/(4*M_PROTON*C**2)*100:.3f}%")
    print(f"  Sun's H-fuel: 0.1 * M_sun * 0.007 c^2 = {0.1*M_SUN*0.007*C**2:.2e} J")
    tau_sun = 0.1 * M_SUN * 0.007 * C**2 / L_SUN / GYR_S
    print(f"  tau_MS(Sun)  = E / L = {tau_sun:.2f} Gyr  (matches ~10 Gyr)")
    print()
    print("Onion-shell structure of pre-SN massive star (substrate face cascade):")
    print("    H envelope -> He -> C/O -> O/Ne/Mg -> Si -> Fe core")
    print("Each shell sits at the T,rho where the next K_4 reorganization ignites.")

    # ============================================================
    section(4, "HR DIAGRAM (substrate temperature-luminosity map)")
    # ============================================================
    print("HR diagram = projection of the stellar parameter manifold onto")
    print("(log T_eff, log L). Three primary populations:")
    print()
    print("  Main sequence : core H burning, L ~ T_eff^a (a~5 to 8)")
    print("  Giants/sgnts  : shell burning, expanded envelope, low T_eff, high L")
    print("  White dwarfs  : degenerate cinders, low L, high T_eff")
    print()
    print("Spectral types (Harvard classification: O B A F G K M):")
    print(f"  {'class':<5s}  {'T_eff [K]':>12s}  {'color':<10s}  {'example':<22s}  {'mass [Msun]':>11s}")
    spectra = [
        ("O",  35000.0, "blue",     "Mintaka (delta Ori)",    25.0),
        ("B",  18000.0, "blue-wht", "Rigel (B8 Iab)",         18.0),
        ("A",   8500.0, "white",    "Vega (A0V), Sirius A",    2.1),
        ("F",   6500.0, "yellow-w", "Procyon (F5IV)",          1.4),
        ("G",   5500.0, "yellow",   "Sun (G2V)",               1.0),
        ("K",   4500.0, "orange",   "Aldebaran (K5III)",       0.8),
        ("M",   3200.0, "red",      "Proxima (M5.5V)",         0.20),
        ("L/T/Y", 1500.0, "brown",  "Brown dwarfs",            0.05),
    ]
    for cls, t, c, ex, m in spectra:
        print(f"  {cls:<5s}  {t:>12.0f}  {c:<10s}  {ex:<22s}  {m:>11.2f}")
    print()
    print("Stefan-Boltzmann sanity:  L = 4 pi R^2 sigma T_eff^4")
    L_sun_check = 4.0 * math.pi * R_SUN ** 2 * SIGMA_SB * T_SUN ** 4
    print(f"  Sun:  L_pred = {L_sun_check:.3e} W   L_obs = {L_SUN:.3e} W "
          f"  err = {(L_sun_check-L_SUN)/L_SUN*100:+.2f}%")
    print()
    print("Substrate: T_eff = surface strain temperature; L = total radiated strain")
    print("flux. Each evolutionary track is a line of constant total strain mass M")
    print("through the (T,L) plane as core composition (and hence boundary cond.) shifts.")

    # ============================================================
    section(5, "STELLAR EVOLUTION BY INITIAL MASS")
    # ============================================================
    print("Final fate is set almost entirely by initial mass M_i (and metallicity Z).")
    print()
    print(f"  {'M_i [Msun]':<14s}  {'fate':<32s}  {'remnant':<18s}")
    fate = [
        ("< 0.08",        "brown dwarf (no H burning)",     "BD (no remnant)"),
        ("0.08 - 0.5",    "M dwarf, never beyond pp",       "He WD eventually"),
        ("0.5 - 8",       "RGB -> AGB -> planetary nebula", "C/O white dwarf"),
        ("8 - 10",        "super-AGB or e-capture SN",      "O/Ne/Mg WD or NS"),
        ("10 - 25",       "core-collapse SN II/Ib/Ic",      "neutron star"),
        ("25 - 40",       "CCSN with fallback",             "black hole"),
        ("40 - 130",      "Wolf-Rayet, weak SN or direct",  "stellar BH"),
        ("130 - 250",     "pair-instability SN (no rem.)",  "no remnant"),
        ("> 250",         "direct collapse",                "massive BH"),
    ]
    for m, f, r in fate:
        print(f"  {m:<14s}  {f:<32s}  {r:<18s}")
    print()
    print("Substrate: heavier initial strain configuration -> deeper gravitational")
    print("well -> hotter core -> ignites later burning stages -> larger Fe core ->")
    print("collapse pushes saturation past 1/2 in a smaller fraction of the star.")
    print()
    print("Sun's future timeline (substrate version):")
    timeline = [
        ("now",                 4.6, "main sequence, core H burning"),
        ("subgiant",           10.5, "core H exhausted, shell burning"),
        ("RGB tip",            12.2, "He flash, R~170 R_sun"),
        ("horizontal branch",  12.3, "core He burning"),
        ("AGB",                12.4, "shell He+H burning, thermal pulses"),
        ("planetary nebula",   12.45,"envelope ejection (~50% mass loss)"),
        ("white dwarf",        12.5, "C/O WD, ~0.6 M_sun, R~Earth"),
    ]
    print(f"  {'phase':<22s}  {'t [Gyr]':>10s}  {'description':<40s}")
    for ph, t, d in timeline:
        print(f"  {ph:<22s}  {t:>10.2f}  {d:<40s}")

    # ============================================================
    section(6, "WHITE DWARFS (electron-degeneracy strain saturation)")
    # ============================================================
    print("WD support: electron Fermi pressure from substrate sigma <= 1/2 cap")
    print("on per-momentum-cell occupancy (fermionic exclusion).")
    print()
    print("Non-relativistic degeneracy:  P_NR = (h^2 / 5 m_e) (3/8pi)^(2/3) n_e^(5/3)")
    print("Ultra-relativistic limit:     P_UR = (hc / 4)     (3/8pi)^(1/3) n_e^(4/3)")
    print()
    print("Mass-radius relation:  R ~ M^(-1/3)  (stiffer matter shrinks under more M)")
    print()
    print("Chandrasekhar mass derivation (substrate version):")
    print("  At UR limit P scales as rho^(4/3) with NO new K, so equilibrium gives")
    print("  a UNIQUE mass independent of R:")
    print("    M_Ch ~ (hbar c / G)^(3/2) / (mu_e m_p)^2 * a_const")
    M_Pl = math.sqrt(HBAR * C / G)
    M_Ch_calc = 3.10 * M_Pl ** 3 / (M_PROTON ** 2 * 2.0 ** 2)  # mu_e=2
    print(f"    M_Ch  =  3.10 * M_Pl^3 / (mu_e^2 m_p^2)")
    print(f"          =  {M_Ch_calc/M_SUN:.3f}  M_sun     (textbook 1.46 M_sun)")
    print()
    print(f"  {'WD':<16s}  {'M [Msun]':>9s}  {'R [Rearth]':>11s}  {'T_eff [K]':>10s}")
    wds = [
        ("Sirius B",      1.018,  0.84, 25193.0),
        ("Procyon B",     0.604,  1.20,  7740.0),
        ("40 Eri B",      0.573,  1.36, 16500.0),
        ("Stein 2051 B",  0.675,  1.10,  7100.0),
        ("Van Maanen 2",  0.68,   1.30,  6220.0),
    ]
    for n, m, r, t in wds:
        print(f"  {n:<16s}  {m:>9.3f}  {r:>11.2f}  {t:>10.0f}")
    print()
    print("Substrate reading: WD = strain-saturated electron sea at sigma -> 1/2.")
    print("Above M_Ch the strain saturation can no longer balance gravity in the")
    print("ultra-relativistic regime -> collapse to NS (or thermonuclear runaway -> SN Ia).")

    # ============================================================
    section(7, "NEUTRON STARS (nuclear-density strain saturation)")
    # ============================================================
    print("NS support: neutron Fermi pressure + nuclear repulsive core (substrate")
    print("hard-core volume ~ xi^3 per baryon, with K_nuc setting compressibility).")
    print()
    print("Rough scales:")
    M_NS = 1.4 * M_SUN
    R_NS = 12.0e3
    rho_NS = 3.0 * M_NS / (4.0 * math.pi * R_NS ** 3)
    rho_nuc = 2.3e17
    g_NS = G * M_NS / R_NS ** 2
    z_NS = 1.0 / math.sqrt(1.0 - 2.0 * G * M_NS / (R_NS * C ** 2)) - 1.0
    print(f"  M ~ 1.4 M_sun     R ~ 10-12 km")
    print(f"  rho_avg ~ {rho_NS:.2e} kg/m^3   (nuclear sat. {rho_nuc:.2e})")
    print(f"  surface g = {g_NS:.2e} m/s^2  ({g_NS/9.81:.1e} x Earth)")
    print(f"  surface z = {z_NS:.3f}  (gravitational redshift)")
    print()
    print("TOV equation (general-relativistic hydrostatic equilibrium):")
    print("  dP/dr = -G[rho+P/c^2][m+4pi r^3 P/c^2] / [r^2 (1 - 2Gm/rc^2)]")
    print("Maximum NS mass (TOV limit) ~ 2.0 - 2.3 M_sun depending on EoS.")
    print("Above this -> black hole.")
    print()
    print(f"  {'pulsar':<22s}  {'P_spin':>10s}  {'B [G]':>10s}  {'note':<22s}")
    pulsars = [
        ("Crab (PSR B0531+21)",  "33 ms",  "4e12",  "SN 1054 remnant"),
        ("Vela (PSR B0833-45)",  "89 ms",  "3.4e12","glitcher"),
        ("PSR J0740+6620",       "2.9 ms", "2e8",   "M=2.08, MSP, NICER"),
        ("Magnetar SGR 1806-20", "7.5 s",  "8e14",  "2004 giant flare"),
        ("J1614-2230",           "3.2 ms", "2e8",   "M=1.97, Shapiro delay"),
        ("J1748-2446ad",         "1.4 ms", "1e8",   "fastest known spin"),
    ]
    for n, p, b, note in pulsars:
        print(f"  {n:<22s}  {p:>10s}  {b:>10s}  {note:<22s}")
    print()
    print("Glitches: sudden Delta P / P ~ 1e-6 spin-up = unpinning of superfluid")
    print("vortices in the inner crust. Substrate: discrete saturation rearrangement")
    print("of pinned strain-vortex cores. Magnetars ~ 10^15 G fields are the largest")
    print("known coherent strain-orientation fields in the universe.")

    # ============================================================
    section(8, "BLACK HOLES (saturation sigma -> 1/2 horizon)")
    # ============================================================
    print("Schwarzschild radius:  r_s = 2 G M / c^2")
    for label, m in [("1 Msun", M_SUN), ("Sgr A* (4.15e6 Msun)", 4.15e6*M_SUN),
                     ("M87* (6.5e9 Msun)", 6.5e9*M_SUN)]:
        rs = 2.0 * G * m / C ** 2
        print(f"  {label:<24s}  r_s = {rs:.3e} m  ({rs/1e3:.3e} km)")
    print()
    print("Substrate horizon: locus where saturation cap sigma = 1/2 is reached")
    print("for all infalling strain modes. The future-directed null cone tilts")
    print("past 90 deg there -> no causal escape. Horizon area A = 4 pi r_s^2 obeys")
    print("the area theorem (substrate strain-saturation is monotonic).")
    print()
    print("No-hair theorem: stationary BH characterized by (M, J, Q) only.")
    print("Substrate: all microscopic strain detail crushed below xi at horizon;")
    print("only conserved global charges survive.")
    print()
    print("Kerr metric:  spin parameter a = J c / (G M^2),  |a| <= 1.")
    print()
    print(f"  {'BH':<22s}  {'M [Msun]':>11s}  {'spin a':>9s}  {'r_s':<14s}")
    bhs = [
        ("Cyg X-1",            21.2,    0.95, "63 km"),
        ("GW150914 final",     62.0,    0.67, "184 km"),
        ("M33 X-7",            15.65,   0.84, "46 km"),
        ("LMC X-1",            10.91,   0.92, "32 km"),
        ("Sgr A*",        4.154e6,      0.10, "12.3 Gm"),
        ("M87*",          6.50e9,       0.90, "19.3 Tm"),
        ("TON 618",       6.6e10,       "?",  "196 Tm"),
    ]
    for n, m, a, rs in bhs:
        astr = f"{a}" if isinstance(a, (int, float)) else str(a)
        print(f"  {n:<22s}  {m:>11.3e}  {astr:>9}  {rs:<14s}")
    print()
    print("EHT imaging (2019 M87*, 2022 Sgr A*) directly resolves the photon ring,")
    print("the strain-mode capture surface at r ~ 1.5 r_s. Diameter / r_s ratio")
    print("matches GR (and thus substrate horizon prediction) within ~10%.")
    print()
    print("Mass spectrum:")
    print("  stellar-mass:   3 - 100 M_sun       (stellar collapse remnants)")
    print("  intermediate:   100 - 1e5 M_sun     (still rare; HLX-1 candidate)")
    print("  supermassive:   1e6 - 1e10 M_sun    (galactic centers)")
    print("  primordial?:    sub-solar           (DM candidate, microlensing limits)")

    # ============================================================
    section(9, "SUPERNOVAE (catastrophic strain reorganization)")
    # ============================================================
    print("Type Ia (thermonuclear):")
    print("  C/O WD accretes from companion -> mass approaches M_Ch ->")
    print("  carbon ignites under degenerate conditions -> RUNAWAY (no thermostat) ->")
    print("  WD entirely incinerated, ~0.6 M_sun of Ni56 produced.")
    print("  Standard candle  M_V ~ -19.3  (used for cosmology, dark energy 1998).")
    print()
    print("Type II / Ib / Ic (core collapse):")
    print("  Fe core exceeds M_Ch -> photodisintegration + e-capture -> collapse ->")
    print("  bounce at nuclear density -> outgoing shock + neutrino reheating ->")
    print("  envelope ejected at v ~ 10^4 km/s.")
    print("  Type II = H envelope still present; Ib/Ic = stripped (no H, no He).")
    print()
    print(f"  {'type':<6s}  {'progenitor':<26s}  {'mechanism':<22s}  {'remnant':<10s}")
    sntypes = [
        ("Ia",   "C/O WD + companion",      "thermonuclear runaway", "none"),
        ("II-P", "RSG 8-25 Msun",           "core collapse",         "NS"),
        ("II-L", "RSG less envelope",       "core collapse",         "NS"),
        ("IIn",  "LBV in dense CSM",        "shock + CSM interact",  "NS/BH"),
        ("IIb",  "RSG mostly stripped",     "core collapse",         "NS"),
        ("Ib",   "WR no H",                 "core collapse",         "NS/BH"),
        ("Ic",   "WR no H, no He",          "core collapse",         "NS/BH"),
        ("Ic-BL","collapsar (GRB)",         "jet-driven collapse",   "BH"),
        ("PISN", "He core 65-130 Msun",     "pair-instability",      "none"),
    ]
    for t, pr, me, rem in sntypes:
        print(f"  {t:<6s}  {pr:<26s}  {me:<22s}  {rem:<10s}")
    print()
    print("Energetics:")
    E_grav = 3.0/5.0 * G * (1.4*M_SUN)**2 / 1.0e4
    print(f"  Gravitational binding (NS) ~ {E_grav:.2e} J  ({E_grav/1.0e44:.2f} foe)")
    print(f"  Kinetic energy of ejecta   ~ 1e44 J        (1 foe = 10^51 erg)")
    print(f"  Photon emission            ~ 1e42 J        (~1% of total)")
    print(f"  NEUTRINO emission          ~ 3e46 J        (99% of total)")
    print()
    print("SN 1987A (LMC, Feb 23 1987):")
    print("  19 neutrino events detected (Kamiokande-II 12, IMB 8, Baksan 5),")
    print("  arriving 3 hours BEFORE optical brightening.")
    print("  Confirms core-collapse + neutrino-driven explosion mechanism.")
    print()
    print("Nucleosynthesis: SNe build elements C through Fe; r-process in NS-NS")
    print("mergers (kilonovae) builds heavy elements Au, Pt, U, Th.")
    print("GW170817 (Aug 17 2017) = first kilonova with multi-messenger detection")
    print("(GW + GRB + optical/UV/IR + X-ray + radio).  Confirmed r-process.")
    print()
    print("Substrate framing: SN = sudden release of cumulative gravitational strain")
    print("when the core's K_4 face inventory exhausts (Fe binding minimum). The")
    print("released strain energy is mostly carried by neutrino strain modes")
    print("(weakly coupled, lowest gamma drag) which thermalize the envelope.")

    # ============================================================
    section(10, "STELLAR POPULATIONS (substrate metallicity epochs)")
    # ============================================================
    print("Three-population scheme based on metallicity Z = mass fraction of metals:")
    print()
    print(f"  {'pop':<5s}  {'Z':<14s}  {'age':<14s}  {'kinematics':<20s}  {'ex.':<14s}")
    pops = [
        ("I",   "0.01 - 0.04",  "< 9 Gyr",     "thin disk, circ. orb.", "Sun, Sirius"),
        ("II",  "1e-4 - 1e-2",  "10-13 Gyr",   "halo, high vel disp.",   "M92, M3 (GC)"),
        ("III", "= 0",          "13.4-13.8 Gyr","first stars (z~20)",   "hypothetical"),
    ]
    for p, z, a, k, ex in pops:
        print(f"  {p:<5s}  {z:<14s}  {a:<14s}  {k:<20s}  {ex:<14s}")
    print()
    print("Pop III predicted properties:")
    print("  - No metals -> CNO catalyzed burning unavailable -> only pp possible")
    print("  - Without metal-line cooling, Jeans mass at primordial conditions large")
    print("  - Estimated mass range 100 - 1000 M_sun, lifetime ~ 1-3 Myr")
    print("  - End fate: pair-instability SN (no remnant) for 130 < M < 250 M_sun")
    print("  - First metals injected at z ~ 15-20 -> reionization era")
    print()
    print("JWST (2022-) is now finding luminous z > 12 galaxies; whether any")
    print("'pristine' Pop III star has been resolved remains open.")
    print()
    print("Substrate: cosmological strain expansion sets temperature floor ->")
    print("first stars condense from H/He only -> their burning + SNe seed the")
    print("substrate with K_4 reorganization products (C, N, O, ... Fe). Each")
    print("subsequent generation builds on a richer face inventory.")

    # ============================================================
    section(11, "SUMMARY: pressure balance, saturation, horizon")
    # ============================================================
    print("Stars across all masses, ages, and stages reduce to ONE strain-mechanic")
    print("balance: outward strain pressure (thermal + radiation + degenerate) vs.")
    print("inward gravitational strain. The relative weight selects the regime.")
    print()
    print("Pressure-source ladder (substrate origin):")
    print("  thermal P ~ n k T            <- gas-mode strain occupancy")
    print("  radiation P ~ a T^4 / 3      <- photon-mode strain energy density")
    print("  electron deg P_NR ~ n^5/3    <- sigma <= 1/2 cap on e- strain cells")
    print("  electron deg P_UR ~ n^4/3    <- relativistic limit -> M_Ch")
    print("  neutron deg P + nuc rep      <- hard-core strain volume xi^3")
    print("  -- HORIZON --                <- sigma = 1/2 reached for ALL modes")
    print()
    print("Each successive line corresponds to higher density / closer to saturation:")
    print("  Sun (gas+rad), WD (e- deg), NS (n deg + nuclear), BH (full saturation).")
    print()
    print("Burning hierarchy = K_4 face reorganization cascade:")
    print("  H -> He -> C -> O -> Si -> Fe   then collapse.")
    print()
    print("Endpoint by initial mass (substrate version):")
    print("  M < 8 Msun:  AGB ejection + WD              (cap holds in e- regime)")
    print("  8 < M < 25:  CCSN + NS                      (cap holds in n regime)")
    print("  M > 25:      CCSN + BH                      (cap fails -> horizon forms)")
    print()
    print("Honest scoreboard: substrate REPRODUCES standard stellar structure,")
    print("nucleosynthesis, and remnant mass functions because the underlying")
    print("equations (Lane-Emden, TOV, Saha, Eddington) are derived from the same")
    print("strain Lagrangian + thermodynamics. Value-add = unification of pressure,")
    print("degeneracy, and horizon as a single saturation phenomenon at increasing")
    print("density, rather than three unrelated chapters.")


if __name__ == "__main__":
    main()
