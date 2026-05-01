"""Geophysics, seismology, and Earth's interior in the strain-medium framework.

Earth = layered substrate-strain configuration; seismic waves = substrate-strain
wave packets; tectonics & geodynamo = mantle-scale substrate-strain convection.

Strain-medium primitives (six total):
  K (stiffness/bulk modulus), rho (density), xi (length scale), gamma (drag),
  saturation cap sigma <= 1/2, orientability.

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

In Earth, u(x,t) is a mechanical displacement field of the rock substrate;
K and rho become the depth-dependent bulk modulus and density of PREM.
Seismic P/S waves are linear modes of this Lagrangian; tectonics is its
slow nonlinear convective regime; the geodynamo is its MHD coupling in
the conducting outer core.

Honest framing: substrate REPRODUCES standard geophysical numbers (PREM,
v_p/v_s, magnitude scales, plate velocities). Value-add is unification:
seismic waves, mantle convection, and the geodynamo are one strain-field
story rather than three separate disciplines.
"""

from __future__ import annotations
import math


# ---- universal & geophysical constants ----
PI = math.pi
G_GRAV = 6.67430e-11        # N m^2 / kg^2
G_SURF = 9.81               # m/s^2
M_EARTH = 5.972e24          # kg
R_EARTH = 6371.0e3          # m
SEC_PER_YR = 3.15576e7
J_TO_ERG = 1.0e7


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Geophysics, seismology, and Earth's interior in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Earth interior =  layered substrate-strain phase configuration")
    print("Seismic waves   =  linear substrate-strain modes (P, S, Love, Rayleigh)")
    print("Tectonics       =  slow nonlinear substrate-strain convection of mantle")
    print("Geodynamo       =  MHD coupling of moving conducting substrate fluid -> B")
    print()

    # ============================================================
    section(1, "EARTH INTERIOR STRUCTURE (substrate-strain phase boundaries)")
    # ============================================================
    print("Each layer = substrate-strain phase set by local (P,T): increasing")
    print("compression -> stiffer K, denser rho, different mineral packing.")
    print("Boundaries (Moho, 410, 660, CMB, ICB) are FIRST-ORDER strain phase")
    print("transitions analogous to ice/water/steam, but in silicate/iron stack.")
    print()
    print(f"  {'layer':<22s}  {'r_top [km]':>10s}  {'thick [km]':>10s}  {'rho [kg/m3]':>11s}  {'P [GPa]':>8s}  {'T [K]':>7s}")
    layers = [
        ("Crust (oceanic)",        6371.0,    7.0,  3000,   0.2,   500),
        ("Crust (continental)",    6371.0,   35.0,  2700,   1.0,   600),
        ("Lithospheric mantle",    6336.0,   65.0,  3300,   3.0,  1000),
        ("Asthenosphere",          6271.0,  140.0,  3400,   4.5,  1600),
        ("Upper mantle",           6131.0,  280.0,  3500,  13.4,  1800),
        ("Transition zone",        5851.0,  250.0,  3900,  23.8,  1900),
        ("Lower mantle",           5601.0, 2230.0,  4900, 135.8,  2700),
        ("D'' layer (CMB top)",    3371.0,  200.0,  5500, 135.8,  3700),
        ("Outer core (liquid Fe/Ni)", 3486.0, 2266.0, 11000, 329.0, 4400),
        ("Inner core (solid Fe)",  1220.0, 1220.0, 13000, 364.0, 5400),
    ]
    for name, rtop, thk, rho, P, T in layers:
        print(f"  {name:<22s}  {rtop:>10.1f}  {thk:>10.1f}  {rho:>11d}  {P:>8.1f}  {T:>7d}")
    print()
    print("Substrate reading: each phase row is one minimum of the substrate")
    print("free-energy V(u; P,T). Pressure climbs from 0 (surface) to 364 GPa")
    print("(Earth's center). At each crossing, K and rho jump discontinuously.")
    print()
    print("Boundary nomenclature:")
    print("  Moho  - crust/mantle  (~7-70 km depending on continent vs ocean)")
    print("  410   - olivine -> wadsleyite phase change")
    print("  660   - ringwoodite -> bridgmanite + ferropericlase")
    print("  CMB   - core-mantle boundary at 2891 km depth (silicate -> liquid Fe)")
    print("  ICB   - inner-core boundary at 5151 km depth (liquid -> solid Fe)")

    # ============================================================
    section(2, "SEISMIC WAVE TYPES (linear substrate-strain modes)")
    # ============================================================
    print("Linearizing the substrate Lagrangian about the layered ground state:")
    print("  rho d_tt u = (K + 4G/3) grad(div u) - G curl(curl u)")
    print("This wave equation has TWO body-wave branches and TWO surface branches.")
    print()
    print("P-wave (primary, longitudinal compressional):")
    print("  v_p = sqrt( (K + 4G/3) / rho )")
    print("  Particle motion parallel to propagation. Fastest. Goes through")
    print("  liquids (only K + 4G/3 needed; G can be 0).")
    print()
    print("S-wave (secondary, shear transverse):")
    print("  v_s = sqrt( G / rho )")
    print("  Particle motion perpendicular to propagation. Requires G > 0.")
    print("  CANNOT propagate in true liquid -> shadow zone proves outer core liquid.")
    print()
    # quick numerical demo for each layer
    print("Substrate demo (typical parameter ranges per layer):")
    print(f"  {'layer':<22s}  {'K [GPa]':>8s}  {'G [GPa]':>8s}  {'rho [kg/m3]':>11s}  {'v_p [km/s]':>10s}  {'v_s [km/s]':>10s}")
    moduli = [
        ("Continental crust",   55,  30,  2700),
        ("Upper mantle",       130,  68,  3400),
        ("Transition zone",    180,  85,  3900),
        ("Lower mantle",       340, 175,  4900),
        ("Outer core (liq.)", 1100,   0, 11000),
        ("Inner core (solid)", 1350, 175, 13000),
    ]
    for name, K_GPa, G_GPa, rho in moduli:
        K_Pa = K_GPa * 1e9
        G_Pa = G_GPa * 1e9
        v_p = math.sqrt((K_Pa + 4.0/3.0 * G_Pa) / rho) / 1000.0
        v_s = math.sqrt(G_Pa / rho) / 1000.0 if G_Pa > 0 else 0.0
        print(f"  {name:<22s}  {K_GPa:>8d}  {G_GPa:>8d}  {rho:>11d}  {v_p:>10.2f}  {v_s:>10.2f}")
    print()
    print("Surface waves (interface modes — substrate boundary excitations):")
    print("  Love waves      - SH transverse, trapped in low-v_s surface layer")
    print("                    requires layer-over-halfspace geometry (waveguide)")
    print("  Rayleigh waves  - retrograde elliptical motion, P+SV combined")
    print("                    decays exponentially with depth (~lambda)")
    print("                    speed ~ 0.92 v_s in uniform halfspace")
    print()
    print("Both surface waves are slower than body waves but carry MOST of the")
    print("damaging energy in shallow earthquakes (lower geometric spreading 1/r")
    print("for surface vs 1/r^2 for body waves).")

    # ============================================================
    section(3, "SEISMIC TOMOGRAPHY & PREM (substrate-strain depth profile)")
    # ============================================================
    print("PREM (Preliminary Reference Earth Model, Dziewonski & Anderson 1981)")
    print("is the canonical 1-D radial depth profile of K, rho, G derived from")
    print("global seismic travel times + free-oscillation periods + Earth mass.")
    print()
    print("Substrate framing: PREM is the empirical reconstruction of substrate")
    print("primitives K(r), rho(r), G(r) inside Earth.")
    print()
    print(f"  {'depth [km]':>10s}  {'rho [kg/m3]':>11s}  {'v_p [km/s]':>10s}  {'v_s [km/s]':>10s}  {'note':<22s}")
    prem = [
        (   0,  1020,  1.45, 0.00, "ocean surface"),
        (   3,  2600,  5.80, 3.20, "upper crust"),
        (  35,  3380,  8.11, 4.49, "Moho"),
        ( 220,  3436,  8.55, 4.64, "lithosphere base"),
        ( 410,  3723,  9.13, 4.93, "olivine -> wadsleyite"),
        ( 660,  3992, 10.27, 5.57, "660-km discontinuity"),
        (1000,  4407, 11.41, 6.31, "lower mantle"),
        (2000,  4970, 12.78, 6.98, "lower mantle"),
        (2891,  5566, 13.72, 7.26, "CMB (just above)"),
        (2891,  9903,  8.06, 0.00, "CMB (just below) — S vanishes"),
        (4000, 11150, 10.03, 0.00, "outer core"),
        (5151, 12166, 10.36, 0.00, "ICB (just above)"),
        (5151, 12764, 11.03, 3.50, "ICB (just below) — S returns"),
        (6371, 13088, 11.26, 3.67, "Earth's center"),
    ]
    for d, rho, vp, vs, note in prem:
        print(f"  {d:>10d}  {rho:>11d}  {vp:>10.2f}  {vs:>10.2f}  {note:<22s}")
    print()
    print("Key signatures of the substrate phase boundaries:")
    print("  - 410 & 660: sharp jumps in v_p, v_s, rho (mineral phase changes)")
    print("  - CMB: v_s collapses to 0 (silicate solid -> liquid iron)")
    print("  - ICB: v_s reappears (~3.5 km/s) — solid Fe inner core")
    print()
    print("3-D tomography refines PREM with lateral variations (~+/- 2% v_s)")
    print("revealing slabs (cold dense, fast) and plumes (hot, slow). These are")
    print("the substrate-strain convection features (section 7).")

    # ============================================================
    section(4, "EARTHQUAKE MECHANICS (saddle release in fault strain)")
    # ============================================================
    print("Elastic rebound (Reid 1910): tectonic loading slowly accumulates")
    print("substrate strain across a locked fault until friction is overcome;")
    print("rapid slip releases stored elastic strain energy as seismic waves.")
    print()
    print("Substrate reading: a fault is a saddle point in the local strain")
    print("landscape (analogous to a chemical transition state). Slowly the")
    print("system is pushed up the saddle; when sigma cap on the fault is")
    print("exceeded, the configuration snaps to the relaxed minimum, releasing")
    print("Delta E_strain as a propagating substrate wave packet.")
    print()
    print("Fault types (Anderson classification — orientation of stress axes):")
    print(f"  {'fault':<14s}  {'stress':<14s}  {'motion':<22s}  {'example':<22s}")
    faults = [
        ("Normal",       "extensional", "hanging wall down",  "East African Rift"),
        ("Reverse/Thrust","compressive","hanging wall up",     "Himalaya, Cascadia"),
        ("Strike-slip",  "shear",        "horizontal, lateral", "San Andreas"),
        ("Oblique",      "mixed",        "combined",            "Alpine NZ"),
    ]
    for f, s, m, ex in faults:
        print(f"  {f:<14s}  {s:<14s}  {m:<22s}  {ex:<22s}")
    print()
    print("Focal mechanism 'beach balls' = lower-hemisphere stereographic")
    print("projection of P-wave first-motion polarities. The two nodal planes")
    print("are orthogonal; one is the fault, the other is the auxiliary plane.")
    print()
    print("Magnitude scales (each is a different summary of the source):")
    print(f"  {'scale':<8s}  {'sensor':<22s}  {'formula':<32s}")
    mags = [
        ("M_L",   "Wood-Anderson short-T", "log A - log A0(distance)"),
        ("M_b",   "1-s body waves",        "log(A/T) + Q(h, Delta)"),
        ("M_s",   "20-s surface waves",    "log(A/T) + 1.66 log Delta + 3.3"),
        ("M_w",   "seismic moment M0",     "(2/3) log10(M0) - 6.0  [Hanks-Kanamori]"),
    ]
    for nm, sn, fm in mags:
        print(f"  {nm:<8s}  {sn:<22s}  {fm:<32s}")
    print()
    print("Moment magnitude demo:")
    print(f"  {'M_w':>5s}  {'M_0 [N m]':>14s}  {'energy [J]':>12s}  {'TNT eq [Mt]':>12s}")
    for Mw in (4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 9.5):
        M0 = 10.0 ** (1.5 * (Mw + 6.0))
        # energy ~ M_0 / 2e4 (Kanamori)
        E = M0 / 2.0e4
        Mt = E / 4.184e15
        print(f"  {Mw:>5.1f}  {M0:>14.2e}  {E:>12.2e}  {Mt:>12.2e}")
    print()
    print("Mercalli intensity scale (MMI I-XII): qualitative ground-shaking")
    print("severity at a site (felt reports + damage). Distinct from magnitude:")
    print("magnitude = source size; intensity = local effect (decreases w/ r).")

    # ============================================================
    section(5, "EARTHQUAKE CATALOG & GUTENBERG-RICHTER LAW")
    # ============================================================
    print("Empirical statistics of all earthquakes globally satisfy:")
    print("  log10 N(>=M) = a - b M           (Gutenberg-Richter, 1944)")
    print()
    print("with b ~ 1 in nearly every tectonic setting. Each unit of M")
    print("multiplies count by ~10 and energy by ~31.6.")
    print()
    print("Substrate origin: cascade of saddle releases in a stressed")
    print("substrate strain network is a self-organized critical (SOC)")
    print("system. SOC universally yields power-law size distributions,")
    print("with b near 1 reflecting near-criticality of the strain field.")
    print()
    print("Global annual rates (CMT/PDE catalogs):")
    print(f"  {'M range':<12s}  {'N/yr (obs)':>11s}  {'N/yr (b=1 fit, a=8)':>22s}")
    rates = [
        (">= 8.0",      1.0),
        (">= 7.0",     15.0),
        (">= 6.0",    134.0),
        (">= 5.0",   1319.0),
        (">= 4.0",  13000.0),
        (">= 3.0", 130000.0),
    ]
    for rng, obs in rates:
        # crude fit anchored on M>=8 -> 1
        M_thresh = float(rng.split()[1])
        pred = 10.0 ** (8.0 - 1.0 * M_thresh)
        print(f"  {rng:<12s}  {obs:>11.0f}  {pred:>22.1f}")
    print()
    print("Major historical earthquakes (M_w, location, deaths approx):")
    print(f"  {'year':>4s}  {'M_w':>4s}  {'location':<28s}  {'deaths':>10s}")
    quakes = [
        (1556, 8.0, "Shaanxi, China",          "830,000"),
        (1755, 8.5, "Lisbon, Portugal",         "60,000"),
        (1906, 7.9, "San Francisco, USA",        "3,000"),
        (1923, 7.9, "Kanto, Japan",            "143,000"),
        (1960, 9.5, "Valdivia, Chile",           "5,700"),
        (1964, 9.2, "Alaska, USA",                 "131"),
        (1976, 7.6, "Tangshan, China",         "242,000"),
        (2004, 9.1, "Sumatra-Andaman",         "228,000"),
        (2010, 7.0, "Haiti",                   "160,000"),
        (2011, 9.1, "Tohoku, Japan",            "20,000"),
        (2015, 7.8, "Gorkha, Nepal",             "9,000"),
        (2023, 7.8, "Turkey-Syria",             "60,000"),
    ]
    for y, m, l, d in quakes:
        print(f"  {y:>4d}  {m:>4.1f}  {l:<28s}  {d:>10s}")

    # ============================================================
    section(6, "TSUNAMIS (long-wavelength gravity strain waves)")
    # ============================================================
    print("Tsunami = long-wavelength surface gravity wave triggered by sudden")
    print("vertical seafloor displacement (megathrust quake, landslide, impact).")
    print()
    print("In the long-wavelength (shallow-water) limit lambda >> H:")
    print("  v = sqrt(g H)                       (non-dispersive)")
    print()
    print("Substrate framing: ocean is a thin substrate-strain layer; tsunami")
    print("is its lowest gravity-restored mode. Wavelength (100-500 km) far")
    print("exceeds depth (4 km), so all components travel at the same speed.")
    print()
    print(f"  {'depth [m]':>9s}  {'v [m/s]':>9s}  {'v [km/h]':>10s}  {'wavelength [km]':>16s}")
    for H in (10, 50, 200, 1000, 4000, 7000):
        v = math.sqrt(G_SURF * H)
        # period ~ 20 min typical -> lambda = v T
        T_per = 1200.0
        lam = v * T_per / 1000.0
        print(f"  {H:>9d}  {v:>9.1f}  {v*3.6:>10.1f}  {lam:>16.1f}")
    print()
    print("In the deep ocean (4 km) tsunamis race at jet-airliner speed (~720")
    print("km/h) but with amplitude < 1 m, almost invisible to ships. Crossing")
    print("the Pacific takes < 24 h.")
    print()
    print("Shoaling: as v drops near coast (H -> small), energy flux ~ v rho A^2")
    print("conservation forces amplitude A to grow — Green's law A ~ H^(-1/4).")
    print()
    print("Notable events:")
    print("  2004 Sumatra (M_w 9.1):  max run-up 30+ m, ~228,000 deaths in 14 nations")
    print("  2011 Tohoku  (M_w 9.1):  max run-up 40 m, Fukushima Daiichi meltdown")
    print("  1958 Lituya Bay AK:      landslide-triggered, 524 m wave (max ever recorded)")

    # ============================================================
    section(7, "PLATE TECTONICS (slow nonlinear strain convection)")
    # ============================================================
    print("Earth's lithosphere = brittle outer substrate-strain shell, broken")
    print("into ~14 major plates that ride atop the convecting asthenosphere.")
    print()
    print("Three boundary types (geometry of relative substrate-strain motion):")
    print("  Divergent   - plates move APART; new lithosphere forms (mid-ocean ridges)")
    print("  Convergent  - plates COLLIDE; either subduction (oceanic under) or")
    print("                orogeny (continent-continent like Himalaya)")
    print("  Transform   - plates SLIDE past (San Andreas, North Anatolian)")
    print()
    print("Major plate velocities (mm/yr, NNR-MORVEL frame):")
    print(f"  {'plate':<14s}  {'speed [mm/yr]':>14s}  {'note':<28s}")
    plates = [
        ("Pacific",         70, "fast, mostly oceanic"),
        ("Australian",      62, "headed NE into Pacific"),
        ("Nazca",           56, "subducts under S. America"),
        ("Cocos",           70, "subducts under Central America"),
        ("Philippine Sea",  60, "subducts under Eurasian/Pacific"),
        ("Indian",          54, "collides with Eurasian -> Himalayas"),
        ("South American",  35, "western edge over Nazca"),
        ("African",         24, "very slow, splitting in EAR"),
        ("North American",  25, "westward drift"),
        ("Eurasian",        20, "slow"),
        ("Antarctic",       12, "essentially stationary"),
    ]
    for p, v, n in plates:
        print(f"  {p:<14s}  {v:>14d}  {n:<28s}")
    print()
    print("Hotspots = mantle plumes piercing plates (Hawaii, Iceland, Yellowstone).")
    print("Substrate framing: plumes are hot, low-density convective up-currents")
    print("in the strain field, advecting localized partial-melt anomalies.")
    print()
    print("Wilson cycle (rifting -> spreading -> subduction -> collision -> rifting),")
    print("period ~ 300-500 Myr, is the natural overturn time of mantle convection.")

    # ============================================================
    section(8, "MANTLE CONVECTION (Rayleigh number & substrate fluid)")
    # ============================================================
    print("On geological timescales the mantle behaves as a viscous fluid.")
    print("Convection is driven by radiogenic + primordial heat escaping outward.")
    print()
    print("Rayleigh number (dimensionless drive vs dissipation):")
    print("  Ra = g alpha Delta T d^3 / (nu kappa)")
    print()
    print("Convection onset at Ra_crit ~ 1700; Earth's mantle is at ~ 10^7-10^8")
    print("(strongly supercritical) and at ~ 10^9 if internally heated.")
    print()
    # numerics
    g_m = 9.8
    alpha = 3.0e-5     # 1/K thermal expansion
    DT = 2500.0        # K across mantle
    d = 2890.0e3       # m thickness
    nu = 1.0e17 / 3300 # kinematic viscosity m^2/s ~ eta/rho
    kappa = 1.0e-6     # m^2/s thermal diffusivity
    Ra = g_m * alpha * DT * d**3 / (nu * kappa)
    print(f"Numerical estimate: Ra ~ {Ra:.2e}  (well above critical 1700)")
    print()
    print("Three convective styles operate simultaneously:")
    print("  Slabs    - cold dense subducted lithosphere sinking to CMB")
    print("  Plumes   - hot buoyant columns rising from CMB / lower mantle")
    print("  Cells    - large-scale horizontal flow returning material")
    print()
    print("Substrate reading: mantle is a non-Newtonian (power-law) substrate")
    print("fluid. Slab pull (negative buoyancy of cold strain) is the dominant")
    print("plate-driving force, ridge push secondary. Convection self-organizes")
    print("the surface plate geometry — plates ARE the cold thermal boundary")
    print("layer of the convecting strain medium.")
    print()
    print("Two large low-shear-velocity provinces (LLSVPs) — Pacific 'Tuzo' and")
    print("African 'Jason' — are likely chemically distinct piles atop the CMB,")
    print("acting as anchors organizing the long-wavelength flow pattern.")

    # ============================================================
    section(9, "GEODYNAMO & EARTH'S MAGNETIC FIELD")
    # ============================================================
    print("Earth's magnetic field is generated by self-exciting MHD dynamo")
    print("action in the convecting liquid-iron outer core. It is NOT a")
    print("permanent magnet (core is far above iron's Curie point ~1043 K).")
    print()
    print("Dynamo equation (induction):")
    print("  d_t B = curl(v x B) + eta_m nabla^2 B")
    print("with magnetic diffusivity eta_m = 1/(mu_0 sigma_e) ~ 1-2 m^2/s")
    print()
    print("Substrate framing: outer core is a conducting strain fluid; its")
    print("convective velocity field v(x,t) (Coriolis-organized into columnar")
    print("rolls) twists, stretches, and folds magnetic field lines, sustaining")
    print("them against ohmic decay (Cowling's anti-theorem requires 3-D flow).")
    print()
    print("Field structure (Gauss-spherical-harmonic decomposition):")
    print(f"  {'component':<26s}  {'value':>14s}")
    field = [
        ("Surface dipole moment",   "7.94e22 A m^2"),
        ("Equatorial field strength",   "30,000 nT"),
        ("Polar field strength",         "60,000 nT"),
        ("Dipole tilt (2025)",          "9.4 deg"),
        ("Non-dipole fraction",            "~10%"),
        ("Secular variation rate",  "~80 nT/yr (drift)"),
        ("Westward drift rate",     "~0.18 deg/yr"),
        ("South Atlantic Anomaly",   "weakest 22000 nT"),
    ]
    for k, v in field:
        print(f"  {k:<26s}  {v:>14s}")
    print()
    print("Magnetic reversals (paleomagnetism on seafloor stripes):")
    print(f"  {'chron':<14s}  {'age [Ma]':>10s}  {'polarity':<12s}")
    reversals = [
        ("Brunhes",     0.000, "normal"),
        ("Matuyama",    0.781, "reversed"),
        ("Jaramillo",   0.990, "normal"),
        ("Olduvai",     1.778, "normal"),
        ("Gauss",       2.581, "normal"),
        ("Gilbert",     3.596, "reversed"),
        ("CK5",        10.949, "normal"),
        ("CK20",       43.789, "normal"),
        ("Cret. Quiet", 84.0,  "normal (long stable)"),
    ]
    for ch, age, pol in reversals:
        print(f"  {ch:<14s}  {age:>10.3f}  {pol:<12s}")
    print()
    print("Average reversal interval: ~250 kyr currently; varies wildly. The")
    print("Cretaceous Normal Superchron lasted ~40 Myr without a flip (~80-120 Ma).")
    print("Reversals themselves take ~1-10 kyr; field strength drops to ~10-20%")
    print("of normal during transition, with multipole structure dominating.")

    # ============================================================
    section(10, "GRAVITY, GEOID & HEAT FLOW (substrate energy budget)")
    # ============================================================
    print("Earth gravity field deviates from a perfect sphere by:")
    print("  J2 = 1.0826e-3   (oblateness from rotational flattening)")
    print("  flattening f = (a-c)/a = 1/298.257 = 3.353e-3")
    print()
    a_eq = 6378137.0
    c_pol = 6356752.3
    f_calc = (a_eq - c_pol) / a_eq
    g_eq = G_GRAV * M_EARTH / a_eq**2
    g_pol = G_GRAV * M_EARTH / c_pol**2
    print(f"Equatorial radius a = {a_eq/1000:.3f} km")
    print(f"Polar radius     c = {c_pol/1000:.3f} km")
    print(f"Flattening f       = {f_calc:.6f}  = 1/{1/f_calc:.3f}")
    print(f"g (equator)        = {g_eq:.4f} m/s^2 (no rotation correction)")
    print(f"g (pole)           = {g_pol:.4f} m/s^2")
    print()
    print("Geoid = equipotential surface coinciding with mean sea level.")
    print("It undulates +/- 100 m relative to the reference ellipsoid because")
    print("of mass anomalies in mantle and crust (substrate density variations).")
    print()
    print("GRACE / GRACE-FO satellite missions (2002-present): time-variable")
    print("gravity reveals ice-mass loss, groundwater depletion, ocean-mass change.")
    print()
    print("Internal heat budget (~47 TW total surface flow):")
    print(f"  {'source':<32s}  {'power [TW]':>10s}  {'%':>5s}")
    heat = [
        ("U-238 / U-235 decay",        8.0, 17),
        ("Th-232 decay",               8.0, 17),
        ("K-40 decay",                 4.0,  9),
        ("Total radiogenic",          20.0, 43),
        ("Primordial (accretion)",    12.0, 26),
        ("Inner-core crystallization", 7.0, 15),
        ("Tidal dissipation",          0.1,  0),
        ("Other / misc",               7.9, 16),
        ("TOTAL surface flux",        47.0, 100),
    ]
    for s, p, pct in heat:
        print(f"  {s:<32s}  {p:>10.1f}  {pct:>5d}")
    print()
    print("Average surface heat flux: 47 TW / (4 pi R^2) ~ 92 mW/m^2")
    q_avg = 47.0e12 / (4 * PI * R_EARTH**2)
    print(f"Computed: {q_avg*1000:.1f} mW/m^2")
    print()
    print("Substrate framing: Earth is a slowly cooling strain configuration.")
    print("The 47 TW outflow drives mantle convection (Rayleigh number > 10^7)")
    print("and the geodynamo (a few TW dissipated in the outer core). When")
    print("interior cools below dynamo threshold (~ Gyr from now), Earth's")
    print("magnetic field will collapse — Mars's fate, with its accompanying")
    print("solar-wind atmospheric stripping.")

    # ============================================================
    section(11, "SUMMARY: one strain field, many geophysical phenomena")
    # ============================================================
    print("All of geophysics reduces to ONE substrate strain field u(x,t)")
    print("with depth-dependent primitives K(r), rho(r), G(r), and slowly")
    print("varying boundaries set by the substrate free energy V(u; P, T).")
    print()
    print("Phenomenon  ->  substrate configuration:")
    print("  layered Earth interior        -> phase boundaries of V(u; P, T)")
    print("  P-wave                         -> longitudinal strain mode v_p=sqrt((K+4G/3)/rho)")
    print("  S-wave                         -> transverse strain mode v_s=sqrt(G/rho)")
    print("  outer-core liquidity proof     -> S-wave shadow zone (G -> 0)")
    print("  Love / Rayleigh waves          -> waveguide / interface strain modes")
    print("  earthquake                     -> saddle release in fault strain landscape")
    print("  Gutenberg-Richter (b ~ 1)      -> SOC of stressed strain network")
    print("  tsunami                        -> long-wavelength gravity strain mode")
    print("  plate tectonics                -> top boundary layer of mantle convection")
    print("  hotspots / plumes              -> hot upwelling strain columns")
    print("  geodynamo / B field            -> MHD dynamo of conducting strain fluid")
    print("  geoid undulations              -> density anomalies in strain medium")
    print("  47 TW heat flow                -> radiogenic + primordial strain energy escape")
    print()
    print("Honest scoreboard: substrate predicts the SAME PREM density/velocity")
    print("profiles, the SAME magnitude scales, the SAME plate velocities, the")
    print("SAME geodynamo behavior as standard geophysics — because PREM is")
    print("itself the empirical reconstruction of the substrate primitives K(r),")
    print("rho(r), G(r) inside Earth, and seismic waves are the linear modes of")
    print("the substrate Lagrangian.")
    print()
    print("Value-add: the four classical geophysical sub-disciplines (seismology,")
    print("tectonics, geodynamo, geodesy) become four regimes of one substrate")
    print("strain field, not four empirical chapters.")


if __name__ == "__main__":
    main()
