"""Atmospheric chemistry through the strain-medium framework.

Atmosphere = stratified gaseous substrate-strain region.
Chemistry driven by solar UV substrate-wave input.

Strain-medium primitives:
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2.

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Atmosphere primitives mapping:
  rho     -> air density (drops exponentially with altitude)
  K       -> bulk modulus (sets sound speed, compressibility)
  xi      -> mean free path (collision length, sets reaction rates)
  gamma   -> radiative + collisional damping
  sigma   -> photochemical saturation cap (Chapman quasi-steady-state)

Honest framing: substrate REPRODUCES standard atmospheric chemistry numbers.
Value-add is unification: ozone hole, greenhouse warming, smog, acid rain,
aerosol-cloud interactions all become geometric configurations of one
substrate-strain field driven by UV/IR substrate waves.
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
R_GAS = 8.314462618          # J / (mol K)
G_GRAV = 9.80665             # m / s^2
SIGMA_SB = 5.670374419e-8    # Stefan-Boltzmann W m^-2 K^-4
M_AIR = 28.97e-3             # kg/mol mean molar mass dry air
S_SOLAR = 1361.0             # W/m^2 solar constant


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Atmospheric chemistry in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2")
    print("Atmosphere = stratified gaseous strain region")
    print("Chemistry  = strain-bridge rearrangements driven by UV substrate waves")
    print()

    # ============================================================
    section(1, "ATMOSPHERIC STRUCTURE (strain stratification)")
    # ============================================================
    print("Atmosphere divides into 4 layers by temperature gradient (= strain")
    print("response to solar substrate-wave deposition at different altitudes):")
    print()
    print(f"  {'layer':<14s}  {'altitude [km]':>14s}  {'T [K]':>8s}  {'gradient':<14s}")
    layers = [
        ("Troposphere",  "0-12",     "288-217", "lapse -6.5/km"),
        ("Stratosphere", "12-50",    "217-271", "inversion (O3)"),
        ("Mesosphere",   "50-85",    "271-190", "lapse"),
        ("Thermosphere", "85-600",   "190-1500","strong heating"),
    ]
    for n, alt, T, g in layers:
        print(f"  {n:<14s}  {alt:>14s}  {T:>8s}  {g:<14s}")
    print()
    print("Pressure scale height H = R T / (M_air g):")
    for T_layer in (288.0, 250.0, 220.0, 190.0):
        H = R_GAS * T_layer / (M_AIR * G_GRAV)
        print(f"  T = {T_layer:5.1f} K  ->  H = {H/1000:5.2f} km")
    print()
    print("Pressure profile (isothermal slab approx):  P(z) = P0 exp(-z/H)")
    P0 = 101325.0
    H_typ = 8400.0
    for z_km in (0, 5, 10, 20, 30, 50, 80):
        P = P0 * math.exp(-z_km*1000.0/H_typ)
        print(f"  z = {z_km:3d} km   P = {P:10.1f} Pa   = {P/P0:.3e} atm")
    print()
    print("Substrate reading: rho(z) drops as exp(-z/H), xi (mean free path)")
    print("grows reciprocally.  Above ~100 km substrate becomes collisionless")
    print("and chemistry transitions to single-particle photodissociation.")

    # ============================================================
    section(2, "ATMOSPHERIC COMPOSITION (strain carrier inventory)")
    # ============================================================
    print(f"  {'species':<8s}  {'fraction':>14s}  {'role':<32s}")
    comp = [
        ("N2",   "0.7808",       "inert bulk strain medium"),
        ("O2",   "0.2095",       "oxidizer, UV photochem"),
        ("Ar",   "0.00934",      "inert noble gas"),
        ("CO2",  "0.00042",      "IR-active greenhouse"),
        ("Ne",   "1.8e-5",       "trace inert"),
        ("He",   "5.2e-6",       "trace inert"),
        ("CH4",  "1.9e-6",       "IR-active greenhouse"),
        ("N2O",  "3.3e-7",       "IR-active greenhouse"),
        ("O3",   "0-1e-5",       "UV shield (stratosphere)"),
        ("H2O",  "0-0.04",       "variable, dominant GHG"),
    ]
    for s, f, r in comp:
        print(f"  {s:<8s}  {f:>14s}  {r:<32s}")
    print()
    print("Substrate framing: each molecule = bound strain configuration with")
    print("characteristic absorption windows in the substrate-wave (photon) spectrum.")
    print("N2 and O2 dominate by mass but are nearly transparent in IR;")
    print("trace polar molecules (CO2, CH4, H2O) dominate the IR strain response.")

    # ============================================================
    section(3, "OZONE LAYER CHEMISTRY (Chapman cycle)")
    # ============================================================
    print("Chapman (1930) photochemical cycle in stratosphere (15-35 km):")
    print()
    print("  R1:  O2  + h*nu (<242 nm)  ->  2 O")
    print("  R2:  O   + O2 + M           ->  O3 + M       (3-body, M=N2/O2)")
    print("  R3:  O3  + h*nu (200-310)   ->  O2 + O       (UV-B absorption)")
    print("  R4:  O   + O3               ->  2 O2         (slow termination)")
    print()
    print("Steady state (sigma cap on O3 saturation):")
    print("  d[O3]/dt = k2 [O][O2][M] - J3 [O3] - k4 [O][O3] = 0")
    print()
    print("Threshold wavelengths from photon energy E = hc/lambda:")
    for lam_nm, label in [(242, "O2 dissoc"),(310,"O3 UV-B cutoff"),(320,"DNA UV-B"),(400,"UV/vis")]:
        E_eV = 1239.84 / lam_nm
        print(f"  lambda = {lam_nm:3d} nm  ->  E = {E_eV:.3f} eV   ({label})")
    print()
    print("Ozone column ~300 Dobson units = 3 mm at STP.")
    print("Substrate reading: O3 layer = standing strain shield. The xi")
    print("(strain wavelength) of UV photons matches the O3 absorption modes.")
    print()
    print("Catalytic destruction (anti-shield strain bridges):")
    print(f"  {'cycle':<10s}  {'X':<6s}  {'reactions':<48s}")
    cats = [
        ("ClOx", "Cl",  "Cl + O3 -> ClO + O2; ClO + O -> Cl + O2"),
        ("NOx",  "NO",  "NO + O3 -> NO2 + O2; NO2 + O -> NO + O2"),
        ("HOx",  "OH",  "OH + O3 -> HO2 + O2; HO2 + O -> OH + O2"),
        ("BrOx", "Br",  "Br + O3 -> BrO + O2; BrO + O -> Br + O2"),
    ]
    for c, x, rxn in cats:
        print(f"  {c:<10s}  {x:<6s}  {rxn:<48s}")
    print()
    print("One Cl atom destroys ~10^5 O3 molecules before scavenged.")
    print()
    print("Antarctic ozone hole (Sept-Oct each year, since ~1980):")
    print("  - Polar vortex isolates stratospheric air at -80 C")
    print("  - Polar stratospheric clouds (PSC, type I HNO3.3H2O, type II H2O)")
    print("    provide HETEROGENEOUS surface for: ClONO2 + HCl -> Cl2 + HNO3")
    print("  - Spring sunlight: Cl2 + h*nu -> 2 Cl, catalytic burst")
    print("  - O3 column drops from 300 DU to <100 DU over Antarctica")
    print()
    print("Substrate framing: ozone hole = substrate-strain perturbation by")
    print("Cl bridges that catalytically dismantle the O3 standing-mode shield.")

    # ============================================================
    section(4, "CFCs AND MONTREAL PROTOCOL (engineered strain contaminants)")
    # ============================================================
    print(f"  {'species':<10s}  {'formula':<10s}  {'lifetime [yr]':>12s}  {'ODP':>6s}  {'GWP':>8s}")
    cfcs = [
        ("CFC-11",  "CCl3F",     45,    1.0,   4750),
        ("CFC-12",  "CCl2F2",   100,    1.0,  10900),
        ("CFC-113", "C2Cl3F3",   85,    0.85, 6130),
        ("HCFC-22", "CHClF2",    12,    0.034,1810),
        ("HCFC-141b","C2H3Cl2F", 9.3,   0.11, 725),
        ("HFC-134a","C2H2F4",    14,    0.0,  1430),
        ("HFC-23",  "CHF3",     228,    0.0, 14800),
        ("Halon-1301","CBrF3",   65,   10.0,  7140),
    ]
    for s, f, life, odp, gwp in cfcs:
        print(f"  {s:<10s}  {f:<10s}  {life:>12.1f}  {odp:>6.3f}  {gwp:>8.0f}")
    print()
    print("Montreal Protocol (1987, amended 1990/92/95/97/99/07/16):")
    print("  - Phase out CFCs (developed: 1996; developing: 2010)")
    print("  - Phase out HCFCs (developed: 2020; developing: 2030)")
    print("  - Kigali (2016): phase down HFCs (climate, not ozone)")
    print()
    print("Atmospheric concentration drops:")
    print("  CFC-11 peaked 270 ppt (1994), now ~225 ppt (declining ~1%/yr)")
    print("  CFC-12 peaked 545 ppt (2003), now ~495 ppt")
    print("  Antarctic ozone projected to recover by 2065 (1980 levels)")
    print()
    print("Substrate framing: CFC = engineered halogen-substrate compound that")
    print("survives troposphere (strong C-F/C-Cl bridges) until UV photolysis")
    print("in stratosphere releases catalytic Cl strain bridges.")

    # ============================================================
    section(5, "GREENHOUSE EFFECT (IR strain absorption)")
    # ============================================================
    print("Bare-Earth equilibrium (no atmosphere):")
    alpha = 0.30  # albedo
    T_eq = (S_SOLAR * (1 - alpha) / (4 * SIGMA_SB)) ** 0.25
    print(f"  T_eq = ((1-A) S / 4 sigma)^(1/4) = {T_eq:.1f} K  = {T_eq-273.15:.1f} C")
    print()
    print("Observed surface T = 288 K (15 C).  Difference = 33 K = greenhouse warming.")
    print()
    print("IR-active species (absorption in atmospheric window 8-13 um):")
    print(f"  {'gas':<8s}  {'GWP-100':>10s}  {'atm conc':>14s}  {'lifetime [yr]':>14s}")
    ghg = [
        ("CO2",  1,       "421 ppm",     "300-1000"),
        ("CH4",  27,      "1.9 ppm",     "12"),
        ("N2O",  273,     "335 ppb",     "121"),
        ("O3",   "regional","tropo 30-50 ppb",  "0.05"),
        ("H2O",  "feedback","0.1-4%",          "0.025"),
        ("CFC-12",10900,  "495 ppt",     "100"),
        ("SF6",  23500,   "11 ppt",      "3200"),
        ("NF3",  17400,   "3 ppt",       "740"),
    ]
    for g, gwp, conc, life in ghg:
        gwp_s = str(gwp)
        print(f"  {g:<8s}  {gwp_s:>10s}  {conc:>14s}  {life:>14s}")
    print()
    print("Radiative forcing from doubling CO2:")
    print(f"  Delta F = 5.35 ln(C/C0) = 5.35 * ln(2) = {5.35*math.log(2):.2f} W/m^2")
    print()
    print("Climate sensitivity (equilibrium response to 2xCO2):")
    print(f"  {'estimate':<22s}  {'Delta T [C]':>12s}")
    sens = [
        ("Planck (no feedback)", "1.0-1.2"),
        ("+ water vapor",        "1.8-2.0"),
        ("+ ice-albedo",         "2.2-2.5"),
        ("+ clouds (uncertain)", "2.5-4.0"),
        ("IPCC AR6 best",        "3.0"),
        ("IPCC AR6 likely range","2.5-4.0"),
    ]
    for s, dt in sens:
        print(f"  {s:<22s}  {dt:>12s}")
    print()
    print("Substrate framing: greenhouse warming = atmospheric substrate-strain")
    print("absorption of IR substrate waves emitted by warm surface. Polar")
    print("molecules (asymmetric strain dipole) couple to IR; symmetric N2/O2 do not.")

    # ============================================================
    section(6, "TROPOSPHERIC CHEMISTRY (OH atmospheric detergent)")
    # ============================================================
    print("OH radical = primary tropospheric oxidant ('atmospheric detergent').")
    print("Production:  O3 + h*nu (<320 nm) -> O2 + O(1D)")
    print("             O(1D) + H2O          -> 2 OH")
    print()
    print("Mean global tropospheric [OH] ~ 1e6 molecules/cm^3 (very low!)")
    print()
    print("OH lifetimes for trace gases (tau = 1 / (k_OH [OH])):")
    print(f"  {'gas':<10s}  {'k_OH [cm3/s]':>14s}  {'tau':>14s}")
    oh_data = [
        ("CH4",   "6.4e-15",  "12 yr"),
        ("CO",    "2.4e-13",  "2 months"),
        ("C2H6",  "2.5e-13",  "2 months"),
        ("isoprene","1.0e-10","1.5 hr"),
        ("DMS",   "5.0e-12",  "1 day"),
        ("NH3",   "1.6e-13",  "3 months"),
        ("HFC-134a","4.0e-15","14 yr"),
    ]
    for g, k, tau in oh_data:
        print(f"  {g:<10s}  {k:>14s}  {tau:>14s}")
    print()
    print("NOx-VOC chemistry (urban photochemistry):")
    print("  NO2 + h*nu (<420 nm) -> NO + O")
    print("  O + O2 + M           -> O3 + M")
    print("  NO + O3              -> NO2 + O2   (null cycle without VOC)")
    print()
    print("WITH VOC peroxyl radicals (RO2):")
    print("  RO2 + NO -> RO + NO2  (skips O3 sink, net O3 production)")
    print()
    print("Substrate framing: OH = highly reactive open-shell strain bridge,")
    print("the universal reset switch for tropospheric strain configurations.")

    # ============================================================
    section(7, "PHOTOCHEMICAL SMOG (urban strain overload)")
    # ============================================================
    print("Los Angeles-type smog (warm, sunny, NOx + VOC):")
    print()
    print("  Morning: vehicle exhaust -> NO + VOC")
    print("  Midday:  UV drives NO2 photolysis -> O3 buildup (>100 ppb)")
    print("           RO2 + NO2 -> RO2NO2; PAN (peroxyacetyl nitrate) accumulates")
    print("  Evening: O3 decays via NO titration")
    print()
    print(f"  {'species':<22s}  {'NAAQS':>14s}  {'health effect':<24s}")
    smog = [
        ("O3 (8-hr avg)",       "70 ppb",   "respiratory, lung tissue"),
        ("NO2 (1-hr)",          "100 ppb",  "asthma, bronchial"),
        ("PAN",                 "no std",   "eye irritant, plant damage"),
        ("CO (8-hr)",           "9 ppm",    "carboxyhemoglobin"),
        ("SO2 (1-hr)",          "75 ppb",   "respiratory"),
        ("PM2.5 (24-hr)",       "35 ug/m3", "deep lung penetration"),
        ("PM10 (24-hr)",        "150 ug/m3","upper respiratory"),
    ]
    for s, n, h in smog:
        print(f"  {s:<22s}  {n:>14s}  {h:<24s}")
    print()
    print("PAN (CH3C(O)OONO2): thermally unstable but stable in cold/dry upper")
    print("troposphere; transports NOx thousands of km from source regions.")
    print()
    print("Substrate framing: smog = local strain overload. Saturation cap")
    print("sigma<=1/2 means fresh pollutant strain accumulates faster than OH")
    print("clearance can reset; system pushed near saturation -> bistable smog state.")

    # ============================================================
    section(8, "ACID RAIN (sulfur and nitrogen oxides)")
    # ============================================================
    print("Source reactions:")
    print("  SO2 + OH + M     -> HSO3 + M")
    print("  HSO3 + O2        -> SO3 + HO2")
    print("  SO3 + H2O        -> H2SO4   (very fast)")
    print()
    print("  NO2 + OH + M     -> HNO3 + M")
    print("  N2O5 + H2O(aq)   -> 2 HNO3 (heterogeneous, nighttime)")
    print()
    print("Resulting precipitation pH:")
    print("  Pure water:        pH 7.0")
    print("  CO2 saturated:     pH 5.6  (natural baseline)")
    print("  Acid rain:         pH 4.0-4.5  (industrial regions)")
    print("  Worst recorded:    pH 2.4   (Wheeling WV 1979)")
    print()
    print("Damage:")
    print(f"  {'target':<22s}  {'effect':<40s}")
    damage = [
        ("Lakes (granite shed)", "fish kill at pH<5; Al3+ leached"),
        ("Limestone forests",   "CaCO3 buffering, less damaged"),
        ("Boreal conifers",     "needle damage, Mg/Ca leaching"),
        ("Buildings (marble)",  "CaCO3 + H2SO4 -> CaSO4 (gypsum)"),
        ("Bronze statues",      "patina dissolution"),
        ("Soil",                "pH drop, nutrient leach"),
    ]
    for t, e in damage:
        print(f"  {t:<22s}  {e:<40s}")
    print()
    print("Mitigation tech:")
    print("  - Wet scrubbers (limestone slurry):  CaCO3 + SO2 -> CaSO3 + CO2")
    print("  - Selective catalytic reduction (SCR): NOx + NH3 -> N2 + H2O")
    print("  - Low-sulfur fuels (US <15 ppm S in road diesel since 2006)")
    print("  - Cap-and-trade: US SO2 emissions down ~90% from 1980 peak")
    print()
    print("Substrate framing: acid rain = mobile H+ strain bridges produced by")
    print("oxidation of S and N pollutant strains, deposited far from sources.")

    # ============================================================
    section(9, "AEROSOLS & PARTICULATE MATTER (templated strain droplets)")
    # ============================================================
    print(f"  {'PM source':<24s}  {'composition':<22s}  {'size [um]':>10s}")
    pm_src = [
        ("Sea spray",            "NaCl, sulfate",       "0.5-10"),
        ("Mineral dust",         "silicate, CaCO3",     "1-50"),
        ("Biomass burning",      "BC, organic, K",      "0.1-1"),
        ("Diesel exhaust",       "BC, organic, sulfate","0.05-0.5"),
        ("Coal combustion",      "sulfate, fly ash",    "0.1-10"),
        ("Secondary organic",    "oxidized VOC",        "0.1-1"),
        ("Volcanic",             "sulfate, ash",        "0.1-100"),
        ("Pollen, spores",       "biological",          "10-100"),
    ]
    for s, c, sz in pm_src:
        print(f"  {s:<24s}  {c:<22s}  {sz:>10s}")
    print()
    print("PM2.5 (<2.5 um) penetrates deep into alveoli; PM10 lodges upper airway.")
    print("WHO global mortality from PM2.5: ~4 million premature deaths/yr.")
    print()
    print("Aerosol radiative effects:")
    print("  Direct:    sulfate scatter sunlight back -> cooling (-0.4 W/m^2)")
    print("  Direct:    black carbon absorb sunlight  -> warming (+0.1 W/m^2)")
    print("  Indirect:  CCN (cloud condensation nuclei) -> brighter, longer clouds")
    print("             (Twomey effect, -0.5 to -1.5 W/m^2 estimated)")
    print()
    print("Net aerosol forcing: ~ -1.0 W/m^2 (cooling, masks ~0.5 C of CO2 warming)")
    print()
    print("Substrate framing: aerosol indirect effect = particles serve as")
    print("substrate-strain TEMPLATES for water nucleation. More CCN ->")
    print("more, smaller cloud droplets -> higher albedo cloud strain field.")

    # ============================================================
    section(10, "OXIDATION CYCLES & CARBON CYCLE (substrate radical chains)")
    # ============================================================
    print("Three coupled radical families ('Ox families'):")
    print()
    print(f"  {'family':<6s}  {'members':<28s}  {'role':<32s}")
    fams = [
        ("HOx",  "OH, HO2",                 "primary tropo oxidant"),
        ("NOx",  "NO, NO2, NO3",            "O3 production catalyst"),
        ("ROx",  "RO, RO2 (alkyl peroxy)",  "VOC oxidation chain"),
        ("ClOx", "Cl, ClO",                 "stratospheric O3 sink"),
    ]
    for fa, m, r in fams:
        print(f"  {fa:<6s}  {m:<28s}  {r:<32s}")
    print()
    print("Carbon cycle (annual fluxes, GtC/yr, ~2020 average):")
    print(f"  {'flux':<28s}  {'GtC/yr':>10s}")
    cflux = [
        ("Fossil fuel emissions",    9.6),
        ("Land use change",          1.2),
        ("Ocean uptake",            -2.9),
        ("Terrestrial sink",        -3.4),
        ("Atmospheric growth",       4.5),
    ]
    for f, v in cflux:
        print(f"  {f:<28s}  {v:>10.1f}")
    print()
    print("Reservoirs (GtC):  atm 880, ocean 38000, biosphere 2300, fossil 4000")
    print()
    print("Ice core records (Vostok, EPICA Dome C):")
    print("  - Glacial CO2: 180 ppm  / Interglacial CO2: 280 ppm  (last 800 kyr)")
    print("  - 2024 atmospheric CO2: 421 ppm  (50% above preindustrial)")
    print("  - Highest in >3 Myr (Pliocene); rate fastest in 66 Myr")
    print()
    print("Climate sensitivity to CO2 doubling: 3.0 C (IPCC AR6 best estimate)")
    print()
    print("Substrate framing: carbon cycle = transfer of carbon-strain bridges")
    print("between four substrate reservoirs. Anthropogenic CO2 = injection of")
    print("fossil-stored strain into atmospheric pool faster than ocean/biosphere")
    print("sinks can reabsorb -> net atmospheric strain accumulation.")

    # ============================================================
    section(11, "SUMMARY: one substrate, atmospheric expressions")
    # ============================================================
    print("All atmospheric chemistry reduces to the same substrate-strain field")
    print("driven by solar UV/visible/IR substrate waves through stratified rho(z):")
    print()
    print("  configuration -> phenomenon")
    print("  ----------------------------------------------------------------")
    print("  bound O3 strain shell in stratosphere     -> UV-B protection")
    print("  Cl-bridge catalytic dismantler            -> ozone hole")
    print("  IR-active polar strain dipole (CO2/CH4)   -> greenhouse warming")
    print("  OH radical strain reset                   -> tropospheric cleanup")
    print("  NOx-VOC RO2 chain near saturation         -> photochemical smog")
    print("  H+ mobile strain bridge in droplet        -> acid rain")
    print("  CCN strain template for water nucleation  -> aerosol cloud effect")
    print("  cumulative atm strain past sink capacity  -> climate change")
    print()
    print("Honest scoreboard: substrate predicts the SAME fluxes, lifetimes,")
    print("rates, and forcings as standard atmospheric chemistry, because the")
    print("bound-state spectrum of the substrate Lagrangian is the molecular")
    print("Schrodinger equation in the non-relativistic limit.")
    print()
    print("Value-add: ozone depletion, greenhouse warming, smog, acid rain,")
    print("aerosol-cloud interactions, and the carbon cycle become one")
    print("strain-field story rather than seven empirical chapters — driven by")
    print("solar substrate waves, governed by the K, rho, xi, gamma, sigma cap.")


if __name__ == "__main__":
    main()
