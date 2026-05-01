"""Atmospheric dynamics and meteorology in the strain-medium framework.

Companion to atmospheric_chemistry_substrate.py: this script handles
DYNAMICS (motion, circulation, weather, climate) rather than chemistry
(composition, reactions, photolysis).

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability

The atmosphere is modeled as a rotating compressible substrate-strain fluid:
  - bulk fluid motion = long-wavelength substrate-strain wave
  - weather = mesoscale substrate-strain dynamics
  - climate = long-time ensemble of substrate-strain trajectories
  - Coriolis = rotating-frame substrate-strain pseudo-force
  - geostrophic balance = pressure-gradient <-> Coriolis equilibrium
  - hurricane eyewall = saturated substrate-strain heat engine

Honest framing: substrate REPRODUCES the standard equations of geophysical
fluid dynamics (Navier-Stokes on a rotating sphere, primitive equations,
hydrostatic balance). The value-add is unification with the rest of the
framework - not new meteorology.
"""

from __future__ import annotations
import math


# ---- universal & atmospheric constants ----
PI = math.pi
G = 9.80665                  # m/s^2 surface gravity
R_EARTH = 6.371e6            # m
OMEGA_E = 7.2921159e-5       # rad/s Earth rotation
R_DRY = 287.05               # J/(kg K) dry-air gas constant
R_VAP = 461.5                # J/(kg K) water-vapor gas constant
CP_DRY = 1004.6              # J/(kg K) dry-air specific heat at const p
LV = 2.5e6                   # J/kg latent heat of vaporization
P0 = 101325.0                # Pa surface pressure
T0 = 288.15                  # K standard surface temperature
KAPPA = R_DRY / CP_DRY       # 0.286
RHO0 = P0 / (R_DRY * T0)     # ~1.225 kg/m^3
H_SCALE = R_DRY * T0 / G     # ~8.4 km scale height


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def coriolis_param(lat_deg: float) -> float:
    return 2.0 * OMEGA_E * math.sin(math.radians(lat_deg))


def main() -> None:
    print("Atmospheric dynamics in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Atmosphere = rotating compressible substrate-strain fluid")
    print(f"Earth: Omega = {OMEGA_E:.4e} rad/s,  R = {R_EARTH/1e6:.3f} Mm")
    print(f"Surface: p0 = {P0/100:.1f} hPa,  T0 = {T0:.2f} K,  rho0 = {RHO0:.3f} kg/m^3")
    print(f"Scale height H = R T / g = {H_SCALE/1000:.2f} km")
    print()

    # ============================================================
    section(1, "GOVERNING EQUATIONS (primitive equations on rotating sphere)")
    # ============================================================
    print("Substrate momentum equation (Navier-Stokes in rotating frame):")
    print("  Du/Dt + 2 Omega x u  =  -(1/rho) grad p  +  g  +  F_visc")
    print()
    print("Hydrostatic balance (vertical primitive equation):")
    print("  dp/dz  =  -rho g")
    print()
    print("Ideal gas (substrate equation of state for dilute strain):")
    print("  p  =  rho R_d T")
    print()
    print("Thermodynamic energy (first law in flow form):")
    print("  c_p DT/Dt  -  (1/rho) Dp/Dt  =  Q_diabatic")
    print()
    print("Moisture conservation (substrate-tracer transport):")
    print("  Dq/Dt  =  S_q   (S_q = sources/sinks: evap, cond, precip)")
    print()
    print("Continuity (compressible substrate):")
    print("  d rho / d t  +  div(rho u)  =  0")
    print()
    print("Substrate framing of each term:")
    print("  Du/Dt        bulk substrate-strain acceleration")
    print("  2 Omega x u  rotating-frame pseudo-force on strain")
    print("  -(1/rho)gp   pressure-gradient = strain-density gradient")
    print("  g            gravity = vertical strain-energy gradient")
    print("  F_visc       gamma drag at small scales (boundary layer)")
    print()
    print("Reduction: with hydrostatic + spherical geometry these become the")
    print("'primitive equations' used in every operational weather model.")

    # ============================================================
    section(2, "GEOSTROPHIC AND GRADIENT WIND BALANCE")
    # ============================================================
    print("On scales L >> 100 km and timescales >> 1 day, acceleration is small")
    print("compared to Coriolis and pressure-gradient terms. Result: GEOSTROPHIC")
    print("balance, the substrate-equilibrium between strain-density gradient and")
    print("rotating-frame pseudo-force.")
    print()
    print("Geostrophic wind:")
    print("  u_g  =  -(1/(rho f)) dp/dy")
    print("  v_g  =  +(1/(rho f)) dp/dx       f = 2 Omega sin(phi)")
    print()
    print("Gradient wind (adds curvature):")
    print("  V^2 / R_c  +  f V  =  (1/rho) |grad p|")
    print()
    print("Coriolis parameter f vs latitude:")
    print(f"  {'lat [deg]':>10s}  {'f [10^-4 1/s]':>15s}  {'Rossby radius [km]':>20s}")
    for lat in (5, 15, 30, 45, 60, 75, 90):
        f = coriolis_param(lat)
        if f > 0:
            ld = math.sqrt(G * H_SCALE) / f / 1000.0
        else:
            ld = float("inf")
        print(f"  {lat:>10d}  {f*1e4:>15.4f}  {ld:>20.0f}")
    print()
    print("Substrate framing: geostrophic balance is the static-strain")
    print("equilibrium of the rotating-frame substrate fluid. Strain-density")
    print("gradient and Coriolis pseudo-force exactly cancel at zeroth order.")

    # ============================================================
    section(3, "SCALE ANALYSIS AND THE ROSSBY NUMBER")
    # ============================================================
    print("Rossby number Ro = U / (f L) measures inertia vs Coriolis.")
    print("  Ro << 1  -> rotation dominates, geostrophic balance, large-scale")
    print("  Ro ~ 1   -> mixed, gradient wind, fronts, jets")
    print("  Ro >> 1  -> rotation negligible, ageostrophic, mesoscale convection")
    print()
    print(f"  {'phenomenon':<26s}  {'U [m/s]':>8s}  {'L [km]':>8s}  {'lat':>5s}  {'Ro':>10s}")
    f_mid = coriolis_param(45.0)
    f_eq  = coriolis_param(5.0)
    f_pol = coriolis_param(75.0)
    cases = [
        ("Hadley cell",                  5,    5000, 15, f_eq),
        ("Synoptic cyclone (midlat)",   20,    1000, 45, f_mid),
        ("Jet streak",                  60,    1000, 45, f_mid),
        ("Polar low",                   25,     300, 75, f_pol),
        ("Tropical cyclone",            50,     500, 15, f_eq),
        ("Mesoscale convective system", 30,     200, 35, coriolis_param(35)),
        ("Supercell thunderstorm",      30,      20, 35, coriolis_param(35)),
        ("Tornado",                     80,    0.5,  35, coriolis_param(35)),
        ("Sea breeze",                   8,      50, 30, coriolis_param(30)),
        ("Mountain wave",               20,      20, 45, f_mid),
    ]
    for name, U, L_km, lat, f in cases:
        Ro = U / (abs(f) * L_km*1000.0) if f != 0 else float("inf")
        print(f"  {name:<26s}  {U:>8.0f}  {L_km:>8.0f}  {lat:>5d}  {Ro:>10.2e}")
    print()
    print("Reading: synoptic cyclones (Ro ~ 1e-1) are quasi-geostrophic;")
    print("tornadoes (Ro ~ 1e4) are pure ageostrophic substrate vorticity.")

    # ============================================================
    section(4, "THERMAL WIND, JET STREAMS, ROSSBY WAVES")
    # ============================================================
    print("Thermal wind relation: vertical shear of geostrophic wind is set")
    print("by horizontal temperature (i.e. strain-density) gradient.")
    print("  d u_g / d (ln p)  =  -(R/f) dT/dy")
    print()
    print("Consequence: strong meridional T gradients -> strong upper jets.")
    print()
    print(f"  {'jet':<22s}  {'lat band':<10s}  {'altitude [km]':>14s}  {'speed [m/s]':>12s}")
    jets = [
        ("Polar jet",       "40-60 N/S", 9,  60),   # 200-300 hPa
        ("Subtropical jet", "20-30 N/S", 12, 80),
        ("Tropical easterly","10-20 N",  15, 30),
        ("Polar night jet", "60-70",     30, 100),  # stratospheric
    ]
    for name, band, z, v in jets:
        print(f"  {name:<22s}  {band:<10s}  {z:>14d}  {v:>12d}")
    print()
    print("Rossby waves: planetary-scale meanders of the jet, dispersion")
    print("  omega  =  U k  -  beta k / (k^2 + l^2),     beta = df/dy")
    print("Typical zonal wavenumbers 4-7 around midlatitudes.")
    print()
    beta_45 = 2.0 * OMEGA_E * math.cos(math.radians(45)) / R_EARTH
    L_rossby = 2 * PI * math.sqrt(20.0 / beta_45)  # for U=20 m/s
    print(f"  beta (45 deg) = {beta_45:.3e} 1/(m s)")
    print(f"  Rossby stationary wavelength (U=20 m/s) ~ {L_rossby/1e6:.2f} Mm")
    print(f"  Earth circumference at 45 deg ~ {2*PI*R_EARTH*math.cos(math.radians(45))/1e6:.2f} Mm")
    print(f"  -> typical zonal wavenumber ~ {2*PI*R_EARTH*math.cos(math.radians(45))/L_rossby:.1f}")
    print()
    print("Substrate framing: jet streams are coherent strain-shear filaments")
    print("set up by the rotating-frame thermal-wind balance; Rossby waves are")
    print("substrate-strain modes restored by the planetary vorticity gradient.")

    # ============================================================
    section(5, "GLOBAL CIRCULATION CELLS")
    # ============================================================
    print("Three-cell mean meridional circulation of each hemisphere:")
    print()
    print(f"  {'cell':<10s}  {'lat band':<12s}  {'surface flow':<22s}  {'driver':<28s}")
    cells = [
        ("Hadley", "0-30",   "trade winds (NE/SE)",  "direct thermal (solar)"),
        ("Ferrel", "30-60",  "westerlies",           "indirect, eddy-driven"),
        ("Polar",  "60-90",  "polar easterlies",     "direct (cold subsidence)"),
    ]
    for name, band, flow, drv in cells:
        print(f"  {name:<10s}  {band:<12s}  {flow:<22s}  {drv:<28s}")
    print()
    print("ITCZ (Intertropical Convergence Zone): trade-wind convergence at the")
    print("thermal equator -> band of deep convection and heaviest rainfall.")
    print("Migrates seasonally ~ +/- 10 deg latitude, drives monsoons.")
    print()
    print("Surface wind regimes (climatology):")
    print(f"  {'belt':<22s}  {'lat':<10s}  {'mean speed [m/s]':>16s}")
    winds = [
        ("Doldrums (ITCZ)",   "0-5",   2),
        ("Trade winds",       "5-25",  7),
        ("Horse latitudes",   "25-35", 3),
        ("Westerlies",        "35-60", 10),
        ("Polar easterlies",  "60-90", 5),
    ]
    for b, l, v in winds:
        print(f"  {b:<22s}  {l:<10s}  {v:>16d}")
    print()
    print("Substrate framing: the three-cell pattern is the rotating-substrate")
    print("solution to a differentially heated spherical shell - the simplest")
    print("steady-state strain-flow that respects the saturation cap (Hadley")
    print("cannot extend to the pole because angular-momentum conservation")
    print("would force surface winds beyond the sigma <= 1/2 limit).")

    # ============================================================
    section(6, "EXTRATROPICAL CYCLONES, FRONTS, BAROCLINIC INSTABILITY")
    # ============================================================
    print("Midlatitude cyclones grow from BAROCLINIC INSTABILITY: the")
    print("temperature (strain-density) gradient stores available potential")
    print("energy released by tilted ascent of warm air over cold.")
    print()
    print("Charney-Eady growth rate ~ 0.31 f / N * |dU/dz|   (1/days)")
    print("Most-unstable wavelength ~ 4000 km (zonal), ~ 1500 km meridional")
    print()
    print("Frontal types (substrate-strain discontinuities):")
    print(f"  {'front':<10s}  {'slope':<12s}  {'dT/dx behavior':<20s}  {'weather':<20s}")
    fronts = [
        ("Cold",     "1:50",  "sharp, fast-moving",  "showers, gusts"),
        ("Warm",     "1:200", "gradual",             "stratiform rain"),
        ("Occluded", "mixed", "trapped warm sector", "extended precip"),
        ("Stationary","-",    "slow / wavy",         "prolonged rain"),
    ]
    for n, s, d, w in fronts:
        print(f"  {n:<10s}  {s:<12s}  {d:<20s}  {w:<20s}")
    print()
    print("Conveyor belts (cyclone-relative streams):")
    print("  - warm conveyor: rises ahead of cold front, makes the cloud shield")
    print("  - cold conveyor: low-level wraps around the low north of warm front")
    print("  - dry intrusion: stratospheric-origin downdraft behind cold front")
    print()
    print("Substrate framing: the cyclone is a self-organizing strain dipole")
    print("(low + high) that taps the meridional strain-density gradient and")
    print("converts it into rotational kinetic energy.")

    # ============================================================
    section(7, "TROPICAL CYCLONES (substrate-strain heat engine)")
    # ============================================================
    print("Genesis criteria (must hold simultaneously):")
    print("  1.  SST > 26.5 C (deep enough warm layer ~ 50 m)")
    print("  2.  Low vertical wind shear (< 10 m/s 200-850 hPa)")
    print("  3.  Mid-troposphere moisture (RH > 60% at 700 hPa)")
    print("  4.  Coriolis parameter |f| > 0   (no equatorial cyclones)")
    print("  5.  Pre-existing low-level disturbance (easterly wave, MCS)")
    print()
    print("Saffir-Simpson hurricane scale:")
    print(f"  {'cat':<5s}  {'wind [m/s]':>10s}  {'wind [mph]':>10s}  {'damage':<26s}")
    saffir = [
        ("TS",  (18, 32),  (40, 73),  "tropical storm"),
        ("1",   (33, 42),  (74, 95),  "very dangerous winds"),
        ("2",   (43, 49),  (96, 110), "extensive damage"),
        ("3",   (50, 58),  (111, 129), "devastating damage"),
        ("4",   (59, 70),  (130, 156), "catastrophic damage"),
        ("5",   (70, 999), (157, 999), "complete destruction"),
    ]
    for cat, ms, mph, dmg in saffir:
        m_lo, m_hi = ms
        ph_lo, ph_hi = mph
        m_str = f"{m_lo}-{m_hi}" if m_hi < 100 else f">{m_lo}"
        p_str = f"{ph_lo}-{ph_hi}" if ph_hi < 200 else f">{ph_lo}"
        print(f"  {cat:<5s}  {m_str:>10s}  {p_str:>10s}  {dmg:<26s}")
    print()
    print("Eyewall dynamics: warm moist air rises in a near-saturated annulus,")
    print("releases latent heat at ~ 10 km, returns subsiding air to the eye.")
    print("Carnot efficiency limit (Emanuel):")
    print("  V_pot^2  =  C_k/C_D * (T_s - T_o)/T_o * (h_0* - h*)")
    Ts, To = 300.0, 200.0
    eta = (Ts - To) / Ts
    print(f"  T_s = {Ts:.0f} K (sea surface), T_o = {To:.0f} K (outflow)")
    print(f"  Carnot eta = (Ts-To)/Ts = {eta:.3f}")
    print(f"  -> theoretical V_max ~ 80 m/s (Cat 5 boundary)")
    print()
    print("Climatology (long-term basin averages):")
    print(f"  {'basin':<22s}  {'season':<12s}  {'storms/yr':>10s}  {'hurricanes/yr':>14s}")
    basins = [
        ("Atlantic",            "Jun-Nov",  14,  7),
        ("Eastern Pacific",     "May-Nov",  17,  9),
        ("Western Pacific",     "all year", 26, 16),
        ("North Indian",        "Apr-Dec",   6,  3),
        ("South Indian",        "Nov-Apr",  10,  5),
        ("Australia/SW Pacific","Nov-Apr",  11,  5),
    ]
    for b, s, n, h in basins:
        print(f"  {b:<22s}  {s:<12s}  {n:>10d}  {h:>14d}")
    print()
    print("Substrate framing: hurricane = saturated substrate-strain heat engine.")
    print("Eyewall is the sigma~1/2 ANNULUS: condensation cap forces strain to")
    print("redistribute into rotational KE, sustained by SST-driven enthalpy flux.")

    # ============================================================
    section(8, "BOUNDARY LAYER, EKMAN, TURBULENCE")
    # ============================================================
    print("Atmospheric boundary layer (ABL): bottom 0.1-2 km where surface")
    print("friction (gamma drag in substrate language) couples flow to ground.")
    print()
    print("Ekman layer (steady, neutral, constant eddy viscosity K_m):")
    print("  K_m d^2 u/dz^2  +  f (v - v_g)  =  0")
    print("  K_m d^2 v/dz^2  -  f (u - u_g)  =  0")
    print("Ekman depth D_E = sqrt(2 K_m / f);  surface wind veers ~ 45 deg")
    print("from geostrophic, exponentially aligned upward.")
    print()
    f45 = coriolis_param(45)
    for K_m in (1.0, 5.0, 25.0):
        D = math.sqrt(2.0 * K_m / f45)
        print(f"  K_m = {K_m:>5.1f} m^2/s  ->  D_E = {D:>6.0f} m")
    print()
    print("Monin-Obukhov similarity (surface layer ~ 10% of ABL):")
    print("  u(z)  =  (u*/k) [ ln(z/z0)  -  Psi_m(z/L) ]")
    print("  L_MO  =  -u*^3 T / (k g w'theta')        (Obukhov length)")
    print()
    print("PBL regimes:")
    print(f"  {'regime':<14s}  {'driver':<24s}  {'depth':<12s}  {'profile':<20s}")
    pbl = [
        ("Convective",  "surface heating",     "1-3 km",     "well-mixed theta"),
        ("Stable",      "radiative cooling",   "100-500 m",  "T inversion"),
        ("Neutral",     "strong wind",         "0.5-1 km",   "log wind law"),
        ("Cloud-topped","stratocumulus",       "0.5-1.5 km", "decoupled below"),
    ]
    for n, d, dp, p in pbl:
        print(f"  {n:<14s}  {d:<24s}  {dp:<12s}  {p:<20s}")
    print()
    print("Reynolds-averaged Navier-Stokes (RANS) closure: split u = U + u',")
    print("ensemble-average; turbulent fluxes -<u'w'> modeled as -K_m dU/dz")
    print("with mixing-length l_m -> K_m = l_m^2 |dU/dz|.")
    print()
    print("Substrate framing: turbulence is the small-scale (xi-limited) cascade")
    print("of strain energy dissipated by the gamma drag primitive at the")
    print("Kolmogorov scale eta_K = (nu^3/eps)^(1/4).")

    # ============================================================
    section(9, "MESOSCALE PHENOMENA")
    # ============================================================
    print("L = 2-2000 km, lifetimes 1-24 h. Bridge between turbulence and synoptic.")
    print()
    print(f"  {'phenomenon':<24s}  {'L [km]':>7s}  {'tau [h]':>7s}  {'driver':<24s}")
    meso = [
        ("Single thunderstorm",      10,    1,  "buoyancy"),
        ("Multicell cluster",        50,    3,  "cold pool propagation"),
        ("Supercell",                30,    4,  "rotating updraft"),
        ("Tornado",                   1,  0.3,  "vortex stretching"),
        ("Mesoscale Conv. System", 200,   12,  "cold pool + LLJ"),
        ("Squall line",            500,    8,  "linear gust front"),
        ("Derecho",                500,    8,  "long-lived bow echo"),
        ("Sea breeze",              50,    8,  "land-sea T contrast"),
        ("Mountain wave",           20,    4,  "stable flow over ridge"),
        ("Downburst",                3,  0.3,  "neg. buoyancy plume"),
        ("Tropical squall line",   400,   10,  "cold pool + shear"),
    ]
    for n, L, tau, d in meso:
        print(f"  {n:<24s}  {L:>7.1f}  {tau:>7.1f}  {d:<24s}")
    print()
    print("Fujita / EF tornado damage scale:")
    print(f"  {'EF':<5s}  {'wind [m/s]':>10s}  {'wind [mph]':>10s}  {'description':<28s}")
    ef = [
        ("EF0", "29-38",   "65-85",   "minor damage"),
        ("EF1", "39-49",   "86-110",  "moderate"),
        ("EF2", "50-60",   "111-135", "considerable"),
        ("EF3", "61-74",   "136-165", "severe"),
        ("EF4", "75-89",   "166-200", "devastating"),
        ("EF5", ">89",     ">200",    "incredible"),
    ]
    for c, ms, mph, d in ef:
        print(f"  {c:<5s}  {ms:>10s}  {mph:>10s}  {d:<28s}")
    print()
    print("Beaufort wind scale (sea/land impacts):")
    print(f"  {'B':<3s}  {'name':<20s}  {'m/s':>10s}  {'effect':<24s}")
    beauf = [
        (0,  "Calm",            "0-0.3",   "smoke rises vertically"),
        (3,  "Gentle breeze",   "3.4-5.4", "leaves in motion"),
        (6,  "Strong breeze",   "10.8-13.8","large branches sway"),
        (8,  "Gale",            "17.2-20.7","twigs broken off"),
        (10, "Storm",           "24.5-28.4","trees uprooted"),
        (12, "Hurricane",       ">32.7",   "devastation"),
    ]
    for b, n, m, e in beauf:
        print(f"  {b:<3d}  {n:<20s}  {m:>10s}  {e:<24s}")
    print()
    print("Substrate framing: every mesoscale system is a coherent")
    print("substrate-strain packet at intermediate Ro, where the saturation")
    print("cap sigma <= 1/2 (saturated ascent / RH=100%) controls release of")
    print("CAPE through condensation - the key mesoscale energy source.")

    # ============================================================
    section(10, "NUMERICAL WEATHER PREDICTION (NWP)")
    # ============================================================
    print("Operational NWP integrates the primitive equations forward in time")
    print("from a gridded initial condition, then ensembles for uncertainty.")
    print()
    print("Discretization choices:")
    print("  - spectral: spherical harmonics (ECMWF IFS, GFS legacy)")
    print("  - grid-point: finite-volume on cubed sphere (FV3, ICON, MPAS)")
    print("  - vertical: hybrid sigma-pressure or terrain-following")
    print()
    print("Major operational global models (typical 2025-era specs):")
    print(f"  {'model':<14s}  {'grid':<14s}  {'levels':>7s}  {'dt [s]':>7s}  {'lead [d]':>9s}")
    models = [
        ("ECMWF IFS",   "9 km",    137, 600, 15),
        ("NOAA GFS",    "13 km",    127, 240, 16),
        ("UKMO UM",     "10 km",     90, 300, 7),
        ("DWD ICON",    "13 km",     90, 360, 7),
        ("Meteo-Fr ARP", "7.5 km",   105, 360, 4),
        ("JMA GSM",     "13 km",    128, 400, 11),
    ]
    for m, g, lv, dt, ld in models:
        print(f"  {m:<14s}  {g:<14s}  {lv:>7d}  {dt:>7d}  {ld:>9d}")
    print()
    print("Data assimilation:")
    print("  - 3D-Var:  cost J = (x-x_b)^T B^-1 (x-x_b) + (y-Hx)^T R^-1 (y-Hx)")
    print("  - 4D-Var:  same, integrated over a 6-12 h window with model M")
    print("  - EnKF:    flow-dependent B from ensemble, Kalman update")
    print("  - hybrid:  4D-Var with ensemble-derived B (operational at ECMWF, NOAA)")
    print()
    print("Lead-time skill (anomaly correlation 500 hPa Z, NH):")
    print(f"  {'lead [days]':>12s}  {'ACC':>8s}  {'state':<24s}")
    skill = [
        (1,  0.99, "near-perfect"),
        (3,  0.95, "highly skillful"),
        (5,  0.85, "useful"),
        (7,  0.70, "marginally useful"),
        (10, 0.50, "limit of deterministic"),
        (15, 0.30, "ensemble-only"),
    ]
    for d, a, s in skill:
        print(f"  {d:>12d}  {a:>8.2f}  {s:<24s}")
    print()
    print("Substrate framing: NWP integrates the same Lagrangian L = (1/2) rho")
    print("(d_t u)^2 - ... that defines the substrate; predictability limit")
    print("(~10-14 days) is set by exponential growth of small-scale strain")
    print("perturbations (Lorenz '63, Lyapunov exponent ~ 0.4 / day).")

    # ============================================================
    section(11, "CLIMATE DYNAMICS AND OSCILLATIONS")
    # ============================================================
    print("Climate = long-time ensemble (>30 yr) of substrate-strain trajectories.")
    print("General Circulation Models (GCMs) integrate the same primitive")
    print("equations as NWP, plus ocean, sea ice, land, and biogeochemistry.")
    print()
    print("CMIP6 typical model resolutions and ECS:")
    print(f"  {'model':<16s}  {'atm grid':<12s}  {'ECS [K]':>8s}  {'TCR [K]':>8s}")
    cmip = [
        ("CESM2",        "1.0 deg", 5.2, 2.0),
        ("HadGEM3-GC31", "1.4 deg", 5.5, 2.5),
        ("GFDL-CM4",     "1.0 deg", 3.9, 1.9),
        ("MPI-ESM1.2",   "1.5 deg", 3.0, 1.8),
        ("IPSL-CM6A",    "1.3 deg", 4.6, 2.3),
        ("NorESM2",      "2.0 deg", 2.5, 1.4),
        ("UKESM1",       "1.3 deg", 5.4, 2.8),
        ("CMIP6 mean",   "-",       3.8, 2.0),
    ]
    for m, g, ecs, tcr in cmip:
        print(f"  {m:<16s}  {g:<12s}  {ecs:>8.2f}  {tcr:>8.2f}")
    print()
    print("Equilibrium Climate Sensitivity (IPCC AR6 likely range): 2.5-4.0 K")
    print("Best estimate: 3.0 K per doubling of CO2.")
    print()
    print("Resolution evolution of GCMs (atmospheric grid spacing):")
    print(f"  {'CMIP':<6s}  {'year':>6s}  {'typical dx':>12s}  {'levels':>8s}")
    res = [
        ("CMIP1", 1995, "~500 km", 9),
        ("CMIP3", 2007, "~250 km", 26),
        ("CMIP5", 2013, "~150 km", 40),
        ("CMIP6", 2020, "~100 km", 60),
        ("k-scale", 2030, "~3-5 km", 100),
    ]
    for c, y, d, l in res:
        print(f"  {c:<6s}  {y:>6d}  {d:>12s}  {l:>8d}")
    print()
    print("Major modes of internal climate variability (substrate-strain")
    print("standing modes coupled across ocean-atmosphere):")
    print(f"  {'index':<6s}  {'period':<12s}  {'pattern':<28s}  {'amp [K]':>8s}")
    modes2 = [
        ("ENSO",  "2-7 yr",   "tropical Pacific E-W",       2.0),
        ("PDO",   "20-30 yr", "N. Pacific bipolar",         0.5),
        ("AMO",   "60-80 yr", "N. Atlantic monopole",       0.4),
        ("NAO",   "weeks-yr", "Iceland-Azores SLP",         0.3),
        ("AO",    "weeks-yr", "Arctic annular mode",        0.3),
        ("SAM",   "weeks-yr", "S. annular mode",            0.3),
        ("IOD",   "1-3 yr",   "Indian Ocean dipole",        1.0),
        ("MJO",   "30-60 d",  "tropical eastward wave",     0.5),
    ]
    for n, p, pat, amp in modes2:
        print(f"  {n:<6s}  {p:<12s}  {pat:<28s}  {amp:>8.1f}")
    print()
    print("Substrate framing: climate oscillations are large-scale standing")
    print("strain modes of the coupled ocean-atmosphere substrate, with periods")
    print("set by the slowest restoring timescale (thermocline depth for ENSO,")
    print("AMOC turnover for AMO, etc.).")

    # ============================================================
    section(12, "SUMMARY: one rotating substrate, all the weather")
    # ============================================================
    print("All atmospheric dynamics reduce to the same six primitives:")
    print("  - K, rho, xi, gamma, sigma<=1/2, orientability")
    print("operating on a rotating spherical shell of compressible substrate.")
    print()
    print("Configuration -> phenomenon:")
    print("  large-scale, Ro << 1                  ->  geostrophic, Hadley/Ferrel")
    print("  thermal-wind shear at midlat top      ->  jet streams")
    print("  beta-plane perturbations              ->  Rossby waves")
    print("  baroclinic release at midlat          ->  extratropical cyclones")
    print("  saturated heat engine over warm SST   ->  hurricanes")
    print("  surface-friction Ekman spiral         ->  PBL & sea-breeze")
    print("  CAPE release at sigma~1/2             ->  thunderstorms / MCS / tornado")
    print("  ocean-atmosphere strain coupling      ->  ENSO / PDO / AMO / NAO / MJO")
    print("  long-time ensemble + radiative drift  ->  climate change / ECS")
    print()
    print("Honest scoreboard: substrate yields the SAME primitive equations,")
    print("the SAME geostrophic balance, and the SAME predictability limit as")
    print("standard geophysical fluid dynamics - because the substrate")
    print("Lagrangian reduces to rotating compressible Navier-Stokes in this")
    print("regime. The value-add is unification: weather, climate, fluid,")
    print("chemistry, condensed matter, and particle physics all become one")
    print("strain-medium story rather than ten separate textbooks.")


if __name__ == "__main__":
    main()
