"""Oceanography in the strain-medium framework.

The ocean is a stratified, rotating substrate-strain fluid. Currents, tides,
internal waves, ENSO, and biogeochemistry all reduce to substrate-strain
dynamics in the same Lagrangian:

  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Substrate primitives:
  K (stiffness), rho (density), xi (length scale), gamma (drag),
  saturation cap sigma <= 1/2.

Honest framing: substrate REPRODUCES classical fluid mechanics; the value-add
is unification — thermohaline circulation, M2 tides, SOFAR channel,
Pierson-Moskowitz spectrum, Bjerknes feedback are ONE strain-density story.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
G_M_S2 = 9.80665           # surface gravity
RHO_SW = 1025.0            # mean seawater density [kg/m3]
C_SOUND_SW = 1500.0        # mean seawater sound speed [m/s]
CP_SW = 3990.0             # specific heat of seawater [J/(kg K)]
OMEGA_EARTH = 7.2921e-5    # Earth angular velocity [rad/s]
R_EARTH = 6.371e6          # Earth radius [m]
M_MOON = 7.342e22          # Moon mass [kg]
M_SUN = 1.989e30
D_MOON = 3.844e8
D_SUN = 1.496e11
GRAV = 6.6743e-11


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Oceanography in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2")
    print("Ocean = stratified rotating substrate-strain fluid")
    print("Currents = mesoscale strain-flow patterns; tides = forced strain modes")
    print()

    # ============================================================
    section(1, "OCEAN PHYSICAL STRUCTURE (vertical strain stratification)")
    # ============================================================
    print("The ocean is a vertically stratified substrate-strain medium. Density")
    print("rho(z) increases with depth; T and S set the structure via UNESCO EOS.")
    print()
    print("Standard layered structure (low/mid latitudes):")
    print()
    print(f"  {'layer':<22s}  {'depth [m]':>14s}  {'gradient':<26s}")
    print(f"  {'-'*22:<22s}  {'-'*14:>14s}  {'-'*26:<26s}")
    layers = [
        ("Surface mixed layer",   "0-50 to 200",   "near-isothermal, well-stirred"),
        ("Seasonal thermocline",  "50-300",        "T drops 15->10 C"),
        ("Permanent thermocline", "200-1000",      "T drops 10->4 C"),
        ("Halocline",             "100-1000",      "S drops/rises ~1-2 PSU"),
        ("Pycnocline",            "100-1000",      "rho jumps ~3-5 kg/m3"),
        ("Deep water",            "1000-4000",     "near-uniform, T~2-4 C"),
        ("Bottom water (AABW)",   "4000-bottom",   "T ~ -0.5 to 1 C"),
    ]
    for name, d, grad in layers:
        print(f"  {name:<22s}  {d:>14s}  {grad:<26s}")
    print()
    print("Mixed layer depth (MLD) varies seasonally and by latitude:")
    print(f"  {'region':<28s}  {'winter MLD [m]':>15s}  {'summer MLD [m]':>15s}")
    mld = [
        ("Tropical Pacific",          50,   30),
        ("Subtropical N. Atlantic",   200,  40),
        ("Subpolar N. Atlantic",      600, 100),
        ("Labrador Sea",             2000,  50),
        ("Southern Ocean (ACC)",      400, 100),
        ("Weddell Sea",              1500,  80),
    ]
    for r, w, s in mld:
        print(f"  {r:<28s}  {w:>15d}  {s:>15d}")
    print()
    print("Deep water formation (substrate-density-driven downwelling):")
    print("  - North Atlantic Deep Water (NADW): Labrador + Greenland-Iceland-Norwegian")
    print("    seas, T~2-4 C, S~34.9, rho~27.8 kg/m3 (anomaly)")
    print("  - Antarctic Bottom Water (AABW): Weddell + Ross seas, T~-0.5 C,")
    print("    S~34.65, rho~27.88 kg/m3 — densest water on Earth")
    print()
    print("Substrate framing: pycnocline = sharp gradient in rho primitive ->")
    print("supports internal-wave modes and confines mixing vertically.")

    # ============================================================
    section(2, "SEAWATER PROPERTIES (UNESCO EOS, sound speed)")
    # ============================================================
    print("Mean salinity ~ 35 PSU (Practical Salinity Units, ~35 g/kg dissolved")
    print("salts). Mean T ~ 3.5 C (mass-weighted whole-ocean).")
    print()
    print("Density via UNESCO 1980 (simplified) — rho(T,S,p) [kg/m3]:")
    print()
    print(f"  {'T [C]':>6s}  {'S [PSU]':>8s}  {'p [dbar]':>10s}  {'rho [kg/m3]':>12s}")
    samples = [
        ( 0, 35,    0),
        ( 4, 35,    0),
        (10, 35,    0),
        (20, 35,    0),
        (25, 35,    0),
        ( 4, 35, 4000),  # deep
        (-1, 34.65, 4000),  # AABW
        (15, 36,    0),  # Mediterranean surface
    ]
    for T, S, p in samples:
        # simplified UNESCO-style fit
        rho0 = (999.842594 + 6.793952e-2*T - 9.095290e-3*T**2
                + 1.001685e-4*T**3 - 1.120083e-6*T**4 + 6.536332e-9*T**5)
        A = 0.824493 - 4.0899e-3*T + 7.6438e-5*T**2 - 8.2467e-7*T**3 + 5.3875e-9*T**4
        B = -5.72466e-3 + 1.0227e-4*T - 1.6546e-6*T**2
        C = 4.8314e-4
        rho_p0 = rho0 + A*S + B*S**1.5 + C*S**2
        # crude pressure correction ~ 4.5 kg/m3 per 1000 dbar
        rho = rho_p0 + 4.5e-3 * p
        print(f"  {T:>6.1f}  {S:>8.2f}  {p:>10.0f}  {rho:>12.3f}")
    print()
    print("Sound speed (Mackenzie 1981, simplified):")
    print("  c(T,S,z) = 1448.96 + 4.591 T - 5.304e-2 T^2 + 2.374e-4 T^3")
    print("            + 1.340 (S-35) + 1.630e-2 z + 1.675e-7 z^2  [m/s]")
    print()
    print(f"  {'T [C]':>6s}  {'S [PSU]':>8s}  {'z [m]':>8s}  {'c [m/s]':>10s}")
    csamples = [(25, 35, 0), (15, 35, 0), (10, 35, 0), (4, 35, 1000),
                (2, 35, 4000), (4, 34.7, 700)]
    for T, S, z in csamples:
        c = (1448.96 + 4.591*T - 5.304e-2*T**2 + 2.374e-4*T**3
             + 1.340*(S-35) + 1.630e-2*z + 1.675e-7*z**2)
        print(f"  {T:>6.1f}  {S:>8.2f}  {z:>8.0f}  {c:>10.2f}")
    print()
    print("Note the MINIMUM in c near z ~ 700-1000 m: this is the SOFAR channel,")
    print("a substrate-strain wave-guide trapping low-frequency sound.")

    # ============================================================
    section(3, "SURFACE CURRENTS AND WIND-DRIVEN CIRCULATION")
    # ============================================================
    print("Wind stress tau on the substrate surface drives Ekman transport.")
    print("In a rotating frame (Coriolis f = 2 Omega sin(phi)), the steady-state")
    print("balance between vertical viscous strain and Coriolis gives:")
    print()
    print("  Ekman spiral: surface flow at 45 deg right of wind (NH),")
    print("                rotating with depth, decay scale d_E = sqrt(2 A_v / f).")
    print("  Ekman transport (vertically integrated): M_E = tau / (rho f) [m2/s]")
    print()
    print("Coriolis parameter f at typical latitudes:")
    print(f"  {'phi [deg]':>10s}  {'f [s^-1]':>14s}  {'d_E [m] (A_v=0.05)':>22s}")
    for phi in (5, 15, 30, 45, 60, 75):
        f = 2 * OMEGA_EARTH * math.sin(math.radians(phi))
        d_E = math.sqrt(2 * 0.05 / max(f, 1e-9))
        print(f"  {phi:>10d}  {f:>14.3e}  {d_E:>22.1f}")
    print()
    print("Sverdrup transport (interior basin): integrated meridional flow set by")
    print("wind-stress curl:  beta V = curl(tau)/rho.")
    print("Western boundary intensification (Stommel/Munk): friction returns the")
    print("Sverdrup flux in narrow, fast western boundary currents.")
    print()
    print("Major surface currents (substrate-strain mesoscale flows):")
    print(f"  {'current':<26s}  {'transport [Sv]':>15s}  {'speed [m/s]':>12s}")
    currents = [
        ("Gulf Stream",                 100, 2.5),
        ("Kuroshio",                     65, 2.0),
        ("Agulhas",                      70, 2.0),
        ("Brazil Current",               20, 0.5),
        ("East Australian Current",      35, 0.7),
        ("Antarctic Circumpolar (ACC)", 173, 0.2),
        ("North Equatorial Counter",     45, 0.4),
        ("California Current",           10, 0.1),
        ("Peru (Humboldt) Current",      18, 0.2),
    ]
    for n, t, s in currents:
        print(f"  {n:<26s}  {t:>15d}  {s:>12.2f}")
    print()
    print("(1 Sverdrup = 1e6 m3/s.  ACC at 173 Sv is the largest current on Earth.)")
    print()
    print("Five subtropical gyres (closed substrate-strain circulation cells):")
    print("  N. Pacific, S. Pacific, N. Atlantic, S. Atlantic, Indian.")
    print("  Each rotates anticyclonically (NH clockwise / SH counter), carrying")
    print("  warm water poleward on the west, cold equatorward on the east.")

    # ============================================================
    section(4, "THERMOHALINE CIRCULATION (great ocean conveyor)")
    # ============================================================
    print("Density-driven global overturning. Cold, salty water sinks at high")
    print("latitudes; deep flow returns to the surface via diffusive upwelling")
    print("and Southern Ocean wind-driven upwelling.")
    print()
    print("Branch budget (approximate transports):")
    print(f"  {'branch':<32s}  {'transport [Sv]':>15s}  {'depth [m]':>10s}")
    thc = [
        ("NADW formation (Labrador+GIN)",   18,  2500),
        ("AABW formation (Weddell+Ross)",   10,  4000),
        ("Indian-Pacific deep upwelling",   25,  1000),
        ("Agulhas leakage to Atlantic",     15,   500),
        ("Drake Passage (ACC)",            173,  4000),
        ("Atlantic Meridional Overturning", 17,  1500),
    ]
    for n, t, d in thc:
        print(f"  {n:<32s}  {t:>15d}  {d:>10d}")
    print()
    print("Global overturning timescale ~ 1000 yr (radiocarbon age of deep Pacific).")
    print()
    print("Substrate framing: NADW formation = locally densest substrate-strain")
    print("packet sinks under gravity. The driver is rho(T,S) gradients, not wind.")
    print()
    print("Vulnerability: freshening (ice melt -> reduced surface S) lowers rho,")
    print("can collapse NADW formation. AMOC has slowed ~15% since 1950 (proxy).")
    print()
    print("Energy balance: solar heating warms tropics, polar export cools high")
    print("latitudes; THC carries ~1.3 PW of meridional heat flux.")

    # ============================================================
    section(5, "TIDES (forced substrate-strain modes in rotating frame)")
    # ============================================================
    print("Tidal forcing = differential gravity from Moon/Sun across Earth's")
    print("substrate. The leading tide-generating potential goes as M/d^3, so")
    print("the Moon dominates despite being much less massive.")
    print()
    a_moon = 2 * GRAV * M_MOON / D_MOON**3 * R_EARTH
    a_sun  = 2 * GRAV * M_SUN  / D_SUN**3  * R_EARTH
    print(f"  Lunar tidal acceleration (equatorial bulge): {a_moon:.3e} m/s2")
    print(f"  Solar tidal acceleration:                    {a_sun:.3e} m/s2")
    print(f"  Sun/Moon ratio: {a_sun/a_moon:.3f} (Sun ~46% of Moon's tide)")
    print()
    print("Principal tidal constituents (Doodson harmonic decomposition):")
    print(f"  {'symbol':<8s}  {'name':<28s}  {'period [h]':>12s}  {'rel. amp':>10s}")
    constituents = [
        ("M2",  "Principal lunar semidiurnal", 12.4206, 1.000),
        ("S2",  "Principal solar semidiurnal", 12.0000, 0.466),
        ("N2",  "Larger lunar elliptic",       12.6583, 0.192),
        ("K2",  "Lunisolar declinational",     11.9672, 0.127),
        ("K1",  "Lunar diurnal",               23.9345, 0.584),
        ("O1",  "Lunar diurnal",               25.8193, 0.415),
        ("P1",  "Solar diurnal",               24.0659, 0.193),
        ("Mf",  "Lunar fortnightly",          327.86,   0.172),
    ]
    for s, n, p, a in constituents:
        print(f"  {s:<8s}  {n:<28s}  {p:>12.4f}  {a:>10.3f}")
    print()
    print("Equilibrium vs dynamic theory:")
    print("  Equilibrium (Newton): static bulge follows Moon — predicts ~50 cm")
    print("    range. Wrong by 10-30x in real basins.")
    print("  Dynamic (Laplace): tidal wave is a forced substrate strain mode in")
    print("    a rotating, bounded basin — amphidromic systems, resonant gulfs.")
    print()
    print("M2 amplitude worldwide (range = 2*amplitude):")
    print(f"  {'location':<30s}  {'M2 amp [m]':>10s}  {'range [m]':>10s}")
    m2sites = [
        ("Open ocean (typical)",         0.4,  0.8),
        ("Hawaii, mid-Pacific",          0.25, 0.5),
        ("Pacific amphidrome (zero)",    0.0,  0.0),
        ("Brest, France",                2.0,  4.0),
        ("Bay of Fundy, Canada",         8.0, 16.0),
        ("Severn Estuary, UK",           6.0, 12.0),
        ("Cook Inlet, Alaska",           5.0, 10.0),
        ("Ungava Bay, Canada",           7.5, 15.0),
        ("Bristol Channel",              5.5, 11.0),
        ("Patagonian shelf",             4.0,  8.0),
    ]
    for n, a, r in m2sites:
        print(f"  {n:<30s}  {a:>10.2f}  {r:>10.2f}")
    print()
    print("Bay of Fundy: 16 m range — quarter-wavelength resonance of M2 with")
    print("the bay's natural period (~13 h, very close to M2's 12.42 h).")
    print()
    print("Tidal bores: Qiantang (China) up to 9 m, Severn 2 m, Amazon pororoca 4 m.")

    # ============================================================
    section(6, "SURFACE WAVES (substrate-strain dispersion at the boundary)")
    # ============================================================
    print("Linear deep-water gravity waves: dispersion omega^2 = g k.")
    print("  Phase velocity:  c_p = omega/k = sqrt(g/k) = sqrt(g L / 2pi)")
    print("  Group velocity:  c_g = d omega/d k = c_p / 2")
    print()
    print(f"  {'L [m]':>8s}  {'T [s]':>8s}  {'c_p [m/s]':>10s}  {'c_g [m/s]':>10s}")
    for L in (10, 50, 100, 200, 400, 800):
        k = 2 * PI / L
        omega = math.sqrt(G_M_S2 * k)
        T = 2 * PI / omega
        cp = omega / k
        cg = cp / 2
        print(f"  {L:>8.0f}  {T:>8.2f}  {cp:>10.2f}  {cg:>10.2f}")
    print()
    print("Shallow-water limit (h << L): c = sqrt(g h), non-dispersive.")
    print("  Tsunami at h = 4000 m:  c = sqrt(9.81*4000) = "
          f"{math.sqrt(G_M_S2*4000):.1f} m/s = {math.sqrt(G_M_S2*4000)*3.6:.0f} km/h")
    print()
    print("Pierson-Moskowitz spectrum (fully developed sea, wind speed U):")
    print("  S(omega) = (alpha g^2 / omega^5) exp(-beta (omega_0/omega)^4)")
    print("  alpha = 0.0081, beta = 0.74, omega_0 = g/U_19.5")
    print()
    print(f"  {'U_10 [m/s]':>10s}  {'H_s [m]':>8s}  {'T_p [s]':>8s}  {'sea state':<14s}")
    for U10 in (5, 10, 15, 20, 25, 30):
        H_s = 0.0246 * U10**2          # significant wave height (P-M)
        T_p = 0.83 * U10               # peak period
        if   U10 <  6: ss = "calm"
        elif U10 < 12: ss = "moderate"
        elif U10 < 18: ss = "rough"
        elif U10 < 24: ss = "very rough"
        else:           ss = "high/storm"
        print(f"  {U10:>10.0f}  {H_s:>8.2f}  {T_p:>8.2f}  {ss:<14s}")
    print()
    print("Rogue waves: H > 2 H_s. Confirmed events: Draupner (1995, 25.6 m),")
    print("Andrea (2007, 21 m). Mechanism: nonlinear focusing (modulational")
    print("instability) — substrate-strain energy concentrates from a broad sea.")

    # ============================================================
    section(7, "INTERNAL WAVES (substrate strain modes on pycnocline)")
    # ============================================================
    print("Stratified fluid supports internal gravity waves with restoring force")
    print("from rho(z) gradient. Buoyancy (Brunt-Vaisala) frequency:")
    print()
    print("  N^2 = -(g/rho) d rho/d z   [s^-2]")
    print()
    print(f"  {'region':<24s}  {'d rho/d z [kg/m4]':>17s}  {'N [cph]':>10s}  {'period [min]':>14s}")
    nsites = [
        ("Permanent thermocline", -3.0e-3,    0,  0),
        ("Seasonal thermocline",  -1.0e-2,    0,  0),
        ("Mixed layer",           -1.0e-5,    0,  0),
        ("Deep ocean (uniform)",  -1.0e-4,    0,  0),
        ("Estuary (sharp halo.)", -3.0e-2,    0,  0),
    ]
    for n, drho, _, _ in nsites:
        N2 = -(G_M_S2 / RHO_SW) * drho
        N = math.sqrt(max(N2, 0))
        N_cph = N * 3600 / (2 * PI)
        T_min = (2 * PI / N) / 60 if N > 0 else float('inf')
        print(f"  {n:<24s}  {drho:>17.2e}  {N_cph:>10.3f}  {T_min:>14.2f}")
    print()
    print("Internal waves obey omega^2 = N^2 cos^2(theta) + f^2 sin^2(theta)")
    print("with f < omega < N. Beams propagate at angle to gravity.")
    print()
    print("Internal tides: M2 (12.4 h) forcing scattered by topography ->")
    print("internal wave at near-tidal frequency; carries ~1 TW of energy used")
    print("for diapycnal mixing (sets the 1000-yr THC overturning rate).")
    print()
    print("Mixing efficiency Gamma ~ 0.2 (Osborn 1980): fraction of dissipated")
    print("kinetic energy that goes into raising potential energy via mixing.")

    # ============================================================
    section(8, "EL NINO / LA NINA AND ENSO (Bjerknes substrate feedback)")
    # ============================================================
    print("Equatorial Pacific normally has an east-west thermocline tilt: shallow")
    print("in the east (~50 m, Peru), deep in the west (~150 m, warm pool).")
    print("Trade winds drive this tilt; warm pool drives convection over Indonesia.")
    print()
    print("Bjerknes feedback (positive, substrate-coupled):")
    print("  weak trade winds  ->  thermocline flattens  ->  east warms")
    print("                    ->  weaker SST gradient  ->  even weaker winds  -> El Nino")
    print()
    print("La Nina = opposite phase: stronger trades, sharper tilt, cold east.")
    print()
    print("ENSO oscillation period: 2-7 yr (delayed-oscillator: equatorial Rossby")
    print("waves reflect at western boundary as Kelvin waves, returning the signal).")
    print()
    print("Major ENSO events (Nino 3.4 SSTA peak):")
    print(f"  {'event':<22s}  {'peak SSTA [C]':>14s}  {'phase':<10s}")
    enso = [
        ("1982/83 El Nino",       2.3, "strong"),
        ("1997/98 El Nino",       2.6, "very strong"),
        ("2010/11 La Nina",      -1.7, "strong"),
        ("2015/16 El Nino",       2.6, "very strong"),
        ("2020/22 La Nina",      -1.4, "triple-dip"),
        ("2023/24 El Nino",       2.0, "strong"),
    ]
    for e, t, p in enso:
        print(f"  {e:<22s}  {t:>14.1f}  {p:<10s}")
    print()
    print("Atmospheric teleconnections: California floods, Australian drought,")
    print("Atlantic hurricane suppression, Indian monsoon weakening.")

    # ============================================================
    section(9, "OCEAN ACOUSTICS (SOFAR channel as strain wave-guide)")
    # ============================================================
    print("Sound speed c(z) has a minimum at z ~ 700-1000 m (mid-latitudes):")
    print("  - above: T decreases (slows c), but T effect dominates")
    print("  - below: pressure increases (speeds c)")
    print("Refraction toward the minimum traps acoustic strain modes -> SOFAR.")
    print()
    print("Substrate framing: SOFAR = substrate-strain wave-guide from sound")
    print("speed minimum, exactly analogous to optical fiber (refractive index).")
    print()
    print("Range performance:")
    print(f"  {'source':<28s}  {'freq [Hz]':>10s}  {'level [dB re uPa]':>18s}  {'range [km]':>11s}")
    src = [
        ("Blue whale call",             20,    188,  3000),
        ("Fin whale 20-Hz pulse",       20,    186,  2500),
        ("Snapping shrimp click",     5000,    190,     1),
        ("Container ship",             100,    180,   100),
        ("Air gun (seismic survey)",    50,    220,  4000),
        ("LFA naval sonar",            300,    235,  1000),
        ("Atomic test (Heard 1991)",    57,    220, 16000),
    ]
    for s, f, l, r in src:
        print(f"  {s:<28s}  {f:>10d}  {l:>18d}  {r:>11d}")
    print()
    print("Anthropogenic noise floor in 10-100 Hz band has risen ~3 dB/decade")
    print("since 1950 (shipping). Masks marine mammal communication.")

    # ============================================================
    section(10, "OCEAN CARBON & BIOGEOCHEMISTRY")
    # ============================================================
    print("CO2 dissolution (Henry's law):  [CO2_aq] = K_H p_CO2")
    print("Cold water holds more dissolved CO2 (K_H increases as T drops).")
    print()
    print("Carbonate system (sets pH):")
    print("  CO2 + H2O <-> H2CO3 <-> H+ + HCO3- <-> 2H+ + CO3^2-")
    print()
    print("Pre-industrial pH ~ 8.18.  Modern (2025) pH ~ 8.05.")
    print(f"  Delta pH = -0.13 since 1850 (ocean acidification).")
    print(f"  This is a {10**0.13:.2f}x increase in [H+].")
    print()
    print("Ocean carbon reservoirs and fluxes:")
    print(f"  {'reservoir / flux':<32s}  {'value':>12s}  {'units':<10s}")
    carbon = [
        ("Atmosphere",                       880, "Gt C"),
        ("Surface ocean (DIC)",              900, "Gt C"),
        ("Deep ocean (DIC)",               37100, "Gt C"),
        ("Marine biota",                       3, "Gt C"),
        ("Annual gross air-sea flux (in)",    80, "Gt C/yr"),
        ("Annual gross air-sea flux (out)",   78, "Gt C/yr"),
        ("Net anthropogenic uptake",         2.6, "Gt C/yr"),
        ("Biological pump export (>100 m)",   10, "Gt C/yr"),
    ]
    for n, v, u in carbon:
        print(f"  {n:<32s}  {v:>12.1f}  {u:<10s}")
    print()
    print("Biological pump (substrate-strain photosynthetic patterning):")
    print("  CO2 + H2O + h*nu  ->  CH2O + O2   (Calvin cycle in phytoplankton)")
    print("  Sinking organic snow exports carbon to depth on timescale ~ 1000 yr.")
    print()
    print("Dissolved oxygen:")
    print(f"  {'depth':<20s}  {'O2 [umol/kg]':>12s}  {'saturation':>12s}")
    oxy = [
        ("Surface",                280, "100%"),
        ("Mixed layer",            260, "95%"),
        ("Thermocline (200 m)",     50, "20%"),
        ("OMZ (500 m, E. Pacific)",  5, "<5%"),
        ("Deep N. Pacific",        130, "50%"),
        ("Deep N. Atlantic",       260, "90%"),
        ("AABW",                   240, "85%"),
    ]
    for d, o, s in oxy:
        print(f"  {d:<20s}  {o:>12d}  {s:>12s}")
    print()
    print("Ocean heat content (top 2000 m, OHC anomaly):")
    print(f"  {'period':<14s}  {'OHC anomaly [ZJ]':>18s}  {'rate [ZJ/yr]':>14s}")
    ohc = [
        ("1955-1970",  -10.0, 0.5),
        ("1970-1990",   30.0, 2.0),
        ("1990-2005",  100.0, 5.0),
        ("2005-2015",  200.0, 10.0),
        ("2015-2025",  330.0, 13.0),
    ]
    for p, a, r in ohc:
        print(f"  {p:<14s}  {a:>18.1f}  {r:>14.1f}")
    print()
    print("(1 ZJ = 1e21 J. Ocean absorbs ~93% of Earth's energy imbalance.)")

    # ============================================================
    section(11, "SUMMARY: one substrate, ten ocean phenomena")
    # ============================================================
    print("All oceanography reduces to substrate-strain dynamics in a stratified,")
    print("rotating fluid governed by K, rho, xi, gamma plus the saturation cap.")
    print()
    print("Configuration -> phenomenon:")
    print("  vertical rho gradient                  -> thermocline / pycnocline")
    print("  surface forcing + Coriolis             -> Ekman transport, gyres")
    print("  density-driven vertical strain         -> NADW / AABW / THC")
    print("  Moon/Sun differential gravity          -> tides (M2, S2, K1, ...)")
    print("  free surface dispersion omega^2=gk     -> wind waves, swell, tsunami")
    print("  internal pycnocline strain modes       -> internal waves, mixing")
    print("  coupled ocean-atmosphere feedback      -> ENSO (Bjerknes loop)")
    print("  c(z) minimum at ~1000 m                -> SOFAR acoustic wave-guide")
    print("  CO2 dissolution + biological pump      -> ocean carbon sink, pH")
    print("  cumulative TOA energy imbalance        -> ocean heat content rise")
    print()
    print("Honest scoreboard: substrate REPRODUCES classical fluid mechanics +")
    print("Boussinesq + primitive equations + carbonate chemistry. The framework")
    print("does not replace numerical ocean models; it interprets them as one")
    print("strain-density story rather than ten empirical chapters.")
    print()
    print("Key invariants:")
    print("  - Mass, momentum, salt, and energy conservation = continuity of u(x,t)")
    print("  - Ekman 45 deg deflection = exact rotation of K-rho-f balance")
    print("  - Sverdrup interior + Stommel/Munk boundary = unique BVP solution")
    print("  - sigma <= 1/2 cap shows up as static-stability requirement N^2 > 0")


if __name__ == "__main__":
    main()
