"""Soft matter and active matter through the strain-medium framework.

Soft matter regime: K << K_atomic, where thermal energy kT is comparable to
binding energies and entropic forces dominate. Active matter: external
energy injection at the particle scale creates effective negative damping
locally, breaking detailed balance.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u
With active drive: L_active = L + f_active . u  (energy pumped per particle)

Soft matter   = substrate-strain in low-K regime; thermal kT probes config space.
Active matter = drag gamma + chemical pumping -> effective negative damping locally.
KPZ          = universal substrate-strain growth scaling (1+1d).
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
G_EARTH = 9.80665
T_ROOM = 298.15
KT_ROOM_J = K_B * T_ROOM             # ~4.11e-21 J
KT_ROOM_eV = KT_ROOM_J / EV_J        # ~0.0257 eV


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Soft matter and active matter in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Soft regime: K_soft << K_atomic; entropic + thermal scales dominate.")
    print(f"Thermal scale at T = {T_ROOM:.1f} K:  kT = {KT_ROOM_J:.3e} J = {KT_ROOM_eV*1000:.2f} meV")
    print()
    print("Active regime: localized energy injection -> effective gamma_eff < 0")
    print("over short scales; detailed balance broken; chiral / collective phases.")

    # ============================================================
    section(1, "LIQUID CRYSTALS (orientational substrate order)")
    # ============================================================
    print("Liquid crystal = substrate phase with broken rotational symmetry but")
    print("preserved translational symmetry (or partial). Director n(r) = local")
    print("average orientation of strain anisotropy axis.")
    print()
    print(f"  {'phase':<14s}  {'broken symm.':<28s}  {'order param':<18s}")
    phases = [
        ("Isotropic",   "none",                       "S = 0"),
        ("Nematic",     "rotational SO(3)->Z_2",      "S = <P_2(cos t)>"),
        ("Cholesteric", "+ chirality (helical n(r))", "pitch p"),
        ("Smectic A",   "+ 1d translation",           "rho_q + S"),
        ("Smectic C",   "+ tilt of n vs layer",       "rho_q + tilt phi"),
        ("Smectic B",   "+ in-plane hexatic order",   "psi_6"),
        ("Blue phase",  "double-twist + 3d defect",   "BPI/II/III lattice"),
        ("Discotic",    "disc-like, columnar stacks", "columnar Q"),
        ("Lyotropic",   "concentration-driven LC",    "phi_solvent"),
    ]
    for p, s, o in phases:
        print(f"  {p:<14s}  {s:<28s}  {o:<18s}")
    print()
    print("Frank elastic free energy density (continuum substrate strain):")
    print("  f_F = 1/2 K_1 (div n)^2 + 1/2 K_2 (n . curl n)^2 + 1/2 K_3 (n x curl n)^2")
    print()
    print(f"  {'mode':<8s}  {'name':<8s}  {'physical picture':<40s}")
    print(f"  {'-'*8:<8s}  {'-'*8:<8s}  {'-'*40:<40s}")
    print(f"  {'K_1':<8s}  {'splay':<8s}  {'fan-out of n; div n != 0':<40s}")
    print(f"  {'K_2':<8s}  {'twist':<8s}  {'helical winding of n; n . curl n':<40s}")
    print(f"  {'K_3':<8s}  {'bend':<8s}  {'curving of n; n x curl n':<40s}")
    print()
    print("Frank constants for common nematics (units 10^-12 N = pN):")
    print(f"  {'material':<10s}  {'K_1':>6s}  {'K_2':>6s}  {'K_3':>6s}  {'T [degC]':>8s}")
    fc = [
        ("5CB",   6.4,  3.0, 10.0, 25),
        ("PAA",   7.0,  3.8, 17.0, 125),
        ("MBBA",  6.7,  4.2,  8.6, 25),
        ("E7",   11.1,  5.9, 17.1, 25),
        ("8CB",   6.5,  4.0,  9.5, 32),
    ]
    for m, k1, k2, k3, T in fc:
        print(f"  {m:<10s}  {k1:>6.1f}  {k2:>6.1f}  {k3:>6.1f}  {T:>8d}")
    print()
    print("Frederiks transition (display tech): nematic film between rubbed plates")
    print("with surface anchoring, applied E (or B) above threshold rotates n.")
    print("  E_th = (pi/d) sqrt(K_1 / (eps_0 Delta_eps))")
    d_um = 5.0
    K1 = 6.4e-12
    deps = 11.0
    eps0 = 8.854e-12
    E_th = (PI / (d_um*1e-6)) * math.sqrt(K1 / (eps0 * deps))
    V_th = E_th * d_um*1e-6
    print(f"  Example: 5CB cell d={d_um} um, Delta_eps=11 -> V_th = {V_th:.2f} V")
    print("  This is the operating threshold of every twisted-nematic LCD pixel.")
    print()
    print("Substrate framing: K_1, K_2, K_3 are three projections of one rank-2")
    print("strain-elasticity tensor onto director geometry; orientability primitive")
    print("makes the cholesteric/blue-phase chirality natural (Mobius-like winding).")

    # ============================================================
    section(2, "POLYMER PHYSICS (random-walk substrate chains)")
    # ============================================================
    print("Polymer = 1d substrate strain bridge with N segments. Configuration is")
    print("a random walk in 3d -> end-to-end distance R ~ N^nu (Flory exponent).")
    print()
    print(f"  {'regime':<22s}  {'condition':<22s}  {'nu':>6s}  {'R(N=1e4) [nm]':>14s}")
    a_nm = 0.5
    flory = [
        ("Good solvent",        "T > T_theta",  3/5,  a_nm * (1e4) ** (3/5)),
        ("Theta solvent",       "T = T_theta",  1/2,  a_nm * (1e4) ** (1/2)),
        ("Poor solvent",        "T < T_theta",  1/3,  a_nm * (1e4) ** (1/3)),
        ("Melt (screened)",     "phi=1 / dense",1/2,  a_nm * (1e4) ** (1/2)),
        ("Rigid rod",           "L_p > L",      1.0,  a_nm * (1e4) ** 1.0),
    ]
    for r, c, n, R in flory:
        print(f"  {r:<22s}  {c:<22s}  {n:>6.3f}  {R:>14.1f}")
    print()
    print("Three classical regimes (Flory 1953, de Gennes 1979):")
    print("  - good solvent  : monomer-monomer repulsion; chain swells; nu = 3/5")
    print("  - theta solvent : 2nd virial cancels; ideal random walk; nu = 1/2")
    print("  - poor solvent  : monomers attract; chain collapses to globule; nu=1/3")
    print()
    print("Semidilute crossover (de Gennes blob picture):")
    print("  Below overlap c*, isolated swollen coils. Above c*, blobs of size xi")
    print("  with self-avoidance inside and gaussian random walk outside:")
    print("  xi ~ a (c/c*)^(-3/4)   (in good solvent)")
    print()
    overlap = 0.01  # mass fraction
    c_over_cstar = [0.5, 1.0, 5.0, 50.0]
    print(f"  {'c/c*':>8s}  {'xi/a':>8s}  {'regime':<20s}")
    for r in c_over_cstar:
        if r < 1:
            xi = float('inf')
            label = "dilute (single coil)"
            print(f"  {r:>8.2f}  {'inf':>8s}  {label:<20s}")
        else:
            xi = r ** (-3/4)
            label = "semidilute (blobs)"
            print(f"  {r:>8.2f}  {xi:>8.3f}  {label:<20s}")
    print()
    print("Substrate framing: polymer = strain-bridge of N units with self-energy")
    print("V_int(c). The exponent nu = 3/(d+2) (Flory) is the d-dimensional")
    print("min-strain compromise between elastic stretch and excluded-volume.")

    # ============================================================
    section(3, "GRANULAR MEDIA (substrate force chains)")
    # ============================================================
    print("Granular media = athermal soft matter (kT << gravitational/elastic E).")
    print("No equipartition; jamming and chains are PURE configuration physics.")
    print()
    print("Liu-Nagel jamming phase diagram (1998): three axes")
    print("  - density phi (1 - porosity)")
    print("  - shear stress sigma")
    print("  - 1/T (here generalized: 1/energy_input)")
    print("Jammed point J at phi_c ~ 0.64 (random close packing of monodisperse")
    print("spheres), zero stress, zero T.")
    print()
    print(f"  Random close packing phi_RCP   = 0.6366  (Bernal, 1960)")
    print(f"  Random loose packing phi_RLP   = 0.555")
    print(f"  FCC / HCP ordered phi_max      = pi/(3 sqrt(2)) = {PI/(3*math.sqrt(2)):.4f}")
    print()
    print("Force chains (photoelastic experiments, Behringer 1995+):")
    print("  In a packed granular bed, ~20% of the grains carry ~80% of the load")
    print("  along a sparse 1d 'chain' network. P(F) ~ exp(-F/<F>) tail.")
    print()
    print("Janssen effect (silos, 1895):")
    print("  Wall friction redirects vertical load to walls; pressure SATURATES.")
    print("  P(z) = P_inf (1 - exp(-z/lambda)),   lambda = R / (2 mu K)")
    R_silo = 1.0       # m
    mu_w = 0.5
    K_jan = 0.4
    lam = R_silo / (2 * mu_w * K_jan)
    print(f"  Silo R={R_silo} m, mu={mu_w}, K={K_jan} -> screening length = {lam:.2f} m")
    print(f"  P(infty) ~ rho g lambda = {1500*G_EARTH*lam:.0f} Pa for sand (rho=1500)")
    print("  Why grain elevators don't crush themselves: weight goes to walls.")
    print()
    print("Angle of repose (substrate yield surface):")
    print(f"  {'material':<14s}  {'angle [deg]':>12s}  {'mu_static':>10s}")
    repose = [
        ("dry sand",   34, 0.67),
        ("wet sand",   45, 1.00),
        ("gravel",     35, 0.70),
        ("dry wheat",  27, 0.51),
        ("snow",       38, 0.78),
    ]
    for m, a, mu in repose:
        print(f"  {m:<14s}  {a:>12d}  {mu:>10.2f}")
    print()
    print("Brazil-nut effect: shaken granular bed -> large grains rise to top.")
    print("  Substrate origin: small grains percolate downward into vacancies under")
    print("  large grains; the large grain has fewer vacancies on top (geometry).")
    print()
    print("Substrate framing: granular media live at kT->0 with K_grain finite;")
    print("phase diagram is purely geometric (configuration space exploration is")
    print("driven by external shaking, not thermal noise).")

    # ============================================================
    section(4, "FOAMS & EMULSIONS (Plateau substrate networks)")
    # ============================================================
    print("Foam = gas in liquid; emulsion = liquid in liquid. Both minimize")
    print("substrate surface strain (interfacial energy gamma_s).")
    print()
    print("Plateau's laws (1873) for dry soap froth:")
    print("  1. Films meet THREE at a time, at 120 deg edges.")
    print("  2. Edges meet FOUR at a time at 109.47 deg vertices (= acos(-1/3)).")
    print("  3. All faces are smooth (constant mean curvature).")
    print()
    print(f"  Plateau vertex angle:  arccos(-1/3) = {math.degrees(math.acos(-1/3)):.4f} deg")
    print("  Same as sp3 hybrid in molecular_bonding -> tetrahedral min-strain")
    print("  is universal: 4 unit bridges from a point repel maximally at 109.47 deg.")
    print()
    print("Topological transitions:")
    print("  T1 event:  film flips - two bubbles separate, two new ones meet")
    print("  T2 event:  a 3-sided bubble shrinks to zero (disappearance)")
    print()
    print("Dry vs wet foams:")
    print(f"  {'liquid frac phi':<16s}  {'regime':<24s}  {'rheology':<22s}")
    foam = [
        ("phi < 0.05",  "dry foam (polyhedra)",  "yield stress"),
        ("0.05 - 0.36", "wet foam",               "shear thinning"),
        ("phi > 0.36",  "bubbly liquid",          "Newtonian-ish"),
    ]
    for p, r, h in foam:
        print(f"  {p:<16s}  {r:<24s}  {h:<22s}")
    print()
    print("Coarsening (von Neumann's law, 1952):")
    print("  dA/dt = K (n - 6),   n = number of sides of a 2d bubble.")
    print("  Bubbles with n>6 grow, n<6 shrink, n=6 stays. Mean <R> ~ t^(1/2).")
    print()
    print("Microfluidic generation: T-junctions and flow-focusing produce")
    print("monodisperse droplets at 1-10 kHz with 1-3% size CV. Sets up labs-on-chip")
    print("for high-throughput biology and pharma.")

    # ============================================================
    section(5, "GELS, GLASSES, AND PERCOLATION")
    # ============================================================
    print("Gel = percolating substrate strain network with permanent crosslinks.")
    print("Glass = arrested liquid where structural relaxation time tau >> exp.")
    print()
    print("Sol-gel transition (Flory-Stockmayer, 1941):")
    print("  Random crosslinking of f-functional units; gelation when")
    print("  p_c = 1/(f-1).")
    print()
    print(f"  {'functionality f':<20s}  {'p_c':>8s}  {'example':<24s}")
    sg = [
        (3, 1/2, "trifunctional epoxy"),
        (4, 1/3, "silica gel (SiO2)"),
        (6, 1/5, "polyacrylamide"),
    ]
    for f, p, e in sg:
        print(f"  f = {f:<14d}  {p:>8.4f}  {e:<24s}")
    print()
    print("Percolation thresholds on lattices (geometric crosslinking):")
    print(f"  {'lattice':<22s}  {'p_c (site)':>10s}  {'p_c (bond)':>10s}")
    perc = [
        ("1d chain",            1.000, 1.000),
        ("2d square",           0.5927, 0.5000),
        ("2d triangular",       0.5000, 0.3473),
        ("2d honeycomb",        0.6962, 0.6527),
        ("3d simple cubic",     0.3116, 0.2488),
        ("3d FCC",              0.1992, 0.1198),
        ("3d BCC",              0.2459, 0.1803),
        ("Bethe (z=4)",         0.3333, 0.3333),
    ]
    for l, ps, pb in perc:
        print(f"  {l:<22s}  {ps:>10.4f}  {pb:>10.4f}")
    print()
    print("Glass transition T_g and Vogel-Tammann-Fulcher (VTF):")
    print("  tau(T) = tau_0 exp(B / (T - T_0))")
    print("  ('fragile' glasses: B small, strong T-dependence; 'strong' glasses: large B)")
    print()
    print(f"  {'material':<18s}  {'T_g [K]':>8s}  {'fragility':<14s}")
    glass = [
        ("Silica (SiO2)",     1473, "strong"),
        ("B2O3",                543, "moderate"),
        ("o-terphenyl",         243, "fragile"),
        ("Glycerol",            190, "moderate"),
        ("Polystyrene",         373, "fragile"),
        ("Metallic glass",      600, "fragile"),
    ]
    for m, T, f in glass:
        print(f"  {m:<18s}  {T:>8d}  {f:<14s}")
    print()
    print("Two-step relaxation: alpha (terminal, Maxwell-like) and beta (cage")
    print("rattling, Johari-Goldstein). Both seen in dielectric and shear spectra.")
    print()
    print("Substrate framing: glass = K-network with frozen disorder; thermal")
    print("kT cannot escape local cages over experimental timescales -> non-")
    print("ergodic; sigma<=1/2 cap means only finite local rearrangements possible.")

    # ============================================================
    section(6, "ACTIVE MATTER (negative-damping substrate)")
    # ============================================================
    print("Active matter = particles convert internal energy to motion locally.")
    print("Each particle has effective gamma_eff < 0 over its propulsion bandwidth.")
    print("Detailed balance broken; flocking, MIPS, chiral phases possible.")
    print()
    print("Vicsek model (1995):  N self-propelled particles, fixed speed v,")
    print("each step align direction with local average + noise eta.")
    print("  Order parameter: |<v>| / v")
    print("  Phase transition (T-like) controlled by noise eta.")
    print("  Continuous in 2d at finite density - BREAKS Mermin-Wagner because")
    print("  active drive is non-equilibrium.")
    print()
    print("Toner-Tu hydrodynamic theory: flocking has true long-range order in 2d.")
    print()
    print("MIPS - motility-induced phase separation:")
    print("  Pure repulsive self-propelled particles phase-separate into dense")
    print("  liquid + dilute gas at high enough Peclet number, despite NO attraction.")
    print("  Origin: particles slow down where dense -> piles up further (positive feedback).")
    print()
    print(f"  {'system':<26s}  {'speed v':>14s}  {'Peclet ~ v xi/D':>18s}")
    active = [
        ("E. coli swimmer",         "20 um/s",        "~ 50"),
        ("Janus colloid (light)",   "5 um/s",         "~ 20"),
        ("Microtubule + kinesin",   "100 nm/s",       "~ 100"),
        ("Bird flock (starling)",   "10 m/s",         "macroscopic"),
        ("Fish school (sardine)",   "0.5 m/s",        "macroscopic"),
        ("Pedestrian crowd",        "1.4 m/s",        "macroscopic"),
        ("Vehicle traffic",         "20 m/s",         "macroscopic"),
    ]
    for s, v, P in active:
        print(f"  {s:<26s}  {v:>14s}  {P:>18s}")
    print()
    print("Active nematics: rod-like swimmers form nematic order with TOPOLOGICAL")
    print("DEFECTS (+/- 1/2) that move ballistically. Microtubule-kinesin films")
    print("(Sanchez-Dogic 2012) self-organize into chaotic 'active turbulence'.")
    print()
    print("Substrate reading: drag gamma > 0 + active force -> effective gamma_eff")
    print("can become negative locally; injects energy at the particle scale that")
    print("flows up to the collective; saturation cap sigma<=1/2 still limits density.")

    # ============================================================
    section(7, "BIOLOGICAL SOFT MATTER (cells as active gels)")
    # ============================================================
    print("Living cells are active soft matter par excellence: lipid bilayer membranes")
    print("(K_bend ~ 20 kT) enclose actin/microtubule cytoskeleton driven by ATP-fed")
    print("motors. Whole organisms develop via active morphogenetic flows.")
    print()
    print("Cell membrane bending modulus kappa:")
    print("  Helfrich free energy F = integral [ (kappa/2)(2H - c_0)^2 + sigma ] dA")
    kappa_kT = 20.0
    kappa_J = kappa_kT * KT_ROOM_J
    print(f"  Typical kappa ~ 10-30 kT ~ {kappa_J:.2e} J ~ 0.5 eV")
    print("  Cells can sustain shape changes against thermal undulations because")
    print("  kappa >> kT but only by factor ~20 -> membranes are floppy on micron scale.")
    print()
    print("Cytoskeletal filaments (persistence length L_p):")
    print(f"  {'filament':<14s}  {'diameter':>10s}  {'L_p':>10s}  {'role':<20s}")
    cyto = [
        ("Actin",         "7 nm",     "~17 um",   "shape, motility"),
        ("Microtubule",   "25 nm",    "~5 mm",    "transport, mitosis"),
        ("Intermed. fil.","10 nm",    "~1 um",    "mechanical tough"),
        ("DNA",           "2 nm",     "~50 nm",   "genome storage"),
    ]
    for n, d, L, r in cyto:
        print(f"  {n:<14s}  {d:>10s}  {L:>10s}  {r:<20s}")
    print()
    print("Molecular motors (force, speed, step):")
    print(f"  {'motor':<14s}  {'F_stall [pN]':>14s}  {'v [um/s]':>10s}  {'step [nm]':>10s}  {'fuel':<6s}")
    motors = [
        ("Kinesin-1",    7,    0.8,  8.0,  "ATP"),
        ("Cytoplasmic dynein", 7, 0.8,  8.0,  "ATP"),
        ("Myosin V",     3,    0.4, 36.0,  "ATP"),
        ("Myosin II",    4,    8.0,  5.5,  "ATP"),
        ("RNA polymerase", 25, 0.05,  0.34,"NTP"),
        ("F1-ATPase",    40,   None, 120,  "ATP"),
    ]
    for n, F, v, s, fuel in motors:
        v_str = f"{v:.2f}" if v is not None else "rotary"
        print(f"  {n:<14s}  {F:>14.1f}  {v_str:>10s}  {s:>10.2f}  {fuel:<6s}")
    print()
    print("Mitotic spindle: bipolar active microtubule array organized by molecular")
    print("motors that segregates chromosomes. Self-assembles in minutes from")
    print("a sea of disordered filaments - biggest 'self-organization' demo in biology.")
    print()
    print("Embryogenesis as active fluid: gastrulation, convergent extension,")
    print("germ-band extension all describable via active gel hydrodynamics")
    print("(Prost-Julicher-Joanny). Tissue becomes a programmable substrate.")

    # ============================================================
    section(8, "RHEOLOGY (viscoelastic substrate response)")
    # ============================================================
    print("Soft matter responds with BOTH elastic (in-phase, G') and viscous")
    print("(out-of-phase, G'') components under oscillatory shear strain.")
    print()
    print("Two limiting models:")
    print("  Maxwell:       spring + dashpot in SERIES (liquid-like long time)")
    print("    G(t) = G_0 exp(-t/tau),    tau = eta/G_0")
    print("  Kelvin-Voigt:  spring + dashpot in PARALLEL (solid-like long time)")
    print("    G(t) = G_0 + eta delta(t), creep saturates")
    print()
    G0 = 1e3
    eta = 1.0
    tau_M = eta / G0
    print(f"  Maxwell example:  G_0 = {G0:.0f} Pa, eta = {eta:.1f} Pa.s -> tau = {tau_M*1000:.2f} ms")
    print()
    print("Frequency response (oscillatory):")
    print("  G'(omega) = G_0 (omega tau)^2 / (1 + (omega tau)^2)")
    print("  G''(omega) = G_0 (omega tau) / (1 + (omega tau)^2)")
    print(f"  {'omega tau':>10s}  {'G_p / G_0':>10s}  {'G_pp / G_0':>10s}  {'regime':<20s}")
    for ot in (0.01, 0.1, 1.0, 10.0, 100.0):
        Gp = ot**2 / (1 + ot**2)
        Gpp = ot / (1 + ot**2)
        if ot < 0.1:
            regime = "viscous (liquid)"
        elif ot < 10:
            regime = "viscoelastic"
        else:
            regime = "elastic (solid)"
        print(f"  {ot:>10.2f}  {Gp:>10.4f}  {Gpp:>10.4f}  {regime:<20s}")
    print()
    print("Common rheology classes:")
    print(f"  {'class':<22s}  {'tau(gamma_dot) law':<28s}  {'example':<22s}")
    rheo = [
        ("Newtonian",            "tau = eta gamma_dot",        "water, light oil"),
        ("Shear-thinning",       "tau = K gamma_dot^n, n<1",   "blood, paint, ketchup"),
        ("Shear-thickening",     "tau = K gamma_dot^n, n>1",   "cornstarch, suspensions"),
        ("Bingham plastic",      "tau = tau_y + eta gd",        "toothpaste, drilling mud"),
        ("Herschel-Bulkley",     "tau = tau_y + K gd^n",        "yogurt, mayonnaise"),
        ("Yield-stress fluid",   "flow only above tau_y",       "concrete, mayo, magma"),
    ]
    for c, l, e in rheo:
        print(f"  {c:<22s}  {l:<28s}  {e:<22s}")
    print()
    print("Normal stress differences (Weissenberg rod-climbing): non-Newtonian")
    print("polymer melts climb a rotating rod instead of forming a vortex; sign")
    print("of N_1 > 0 reveals chain orientation in flow.")
    print()
    print("Substrate framing: G' = real (elastic strain stored), G'' = imaginary")
    print("(strain dissipated via gamma); both come from the same Lagrangian when")
    print("computed at finite frequency under oscillatory drive.")

    # ============================================================
    section(9, "MICROFLUIDICS & LOW-Re FLOW (Stokes substrate)")
    # ============================================================
    print("At small length L, low velocity v: Reynolds number Re = rho v L / eta -> 0.")
    print("Inertia drops out -> Stokes equation:  eta nabla^2 v = grad P.")
    print("Time-reversible flow; no turbulence; mixing only by diffusion.")
    print()
    print(f"  {'system':<26s}  {'L':>10s}  {'v':>10s}  {'Re':>10s}")
    re_table = [
        ("Bacterium swimming",      "1 um",   "20 um/s", "2e-5"),
        ("Sperm in cervical mucus", "5 um",   "50 um/s", "2e-4"),
        ("Lab-on-chip droplet",     "100 um", "1 mm/s",  "0.1"),
        ("Capillary blood flow",    "10 um",  "0.5 mm/s","5e-3"),
        ("Garden hose",             "20 mm",  "1 m/s",   "2e4"),
        ("Atmosphere, hurricane",   "100 km", "50 m/s",  "3e11"),
    ]
    for s, L, v, R in re_table:
        print(f"  {s:<26s}  {L:>10s}  {v:>10s}  {R:>10s}")
    print()
    print("Hele-Shaw cell: thin gap between plates -> 2d Darcy-like flow")
    print("with fingers and viscous instability (Saffman-Taylor).")
    print()
    print("Capillary length:  l_c = sqrt(gamma_s / (rho g))")
    gamma_water = 0.072  # N/m
    rho_water = 1000.0
    l_c = math.sqrt(gamma_water / (rho_water * G_EARTH))
    print(f"  Water/air: gamma = {gamma_water*1000:.1f} mN/m -> l_c = {l_c*1000:.2f} mm")
    print("  Below l_c: surface tension dominates (droplets sphere). Above: gravity wins.")
    print()
    print("Microfluidic capabilities (lab-on-chip):")
    print("  - droplet generation 1-10 kHz with <3% CV")
    print("  - single-cell trapping at 100 cells/min")
    print("  - electrowetting for digital microfluidics (Mugele 2005)")
    print("  - PCR, sequencing, drug screening at uL volumes")
    print()
    print("Substrate framing: low-Re flow = drag gamma dominates over inertia rho*d_t;")
    print("Lagrangian reduces to gradient flow on strain energy -> exact reversibility.")

    # ============================================================
    section(10, "OUT-OF-EQUILIBRIUM SUBSTRATE: KPZ & FLUCT THMS")
    # ============================================================
    print("Driven non-equilibrium soft matter is governed by universality classes")
    print("distinct from Ising/XY. The KPZ equation (Kardar-Parisi-Zhang 1986):")
    print()
    print("  d_t h = nu nabla^2 h + (lambda/2)(grad h)^2 + zeta(x,t)")
    print()
    print("describes growing interfaces (paper burning, bacterial colonies, polymer")
    print("deposition). Universal late-time scaling in 1+1d:")
    print("  h(x,t) = v_inf t  +  (Gamma t)^(1/3) chi  +  ...")
    print("with chi a Tracy-Widom random variable (GUE/GOE/GSE depending on geometry).")
    print()
    print(f"  {'class / dimension':<22s}  {'alpha':>8s}  {'beta':>8s}  {'z':>8s}")
    kpz_table = [
        ("KPZ 1+1d",        0.5,    1/3,    1.5),
        ("KPZ 2+1d (num.)", 0.39,   0.24,   1.61),
        ("EW (linear)",     0.5,    0.25,   2.0),
        ("MBE (curv-driven)", 1.0,  0.25,   4.0),
    ]
    for n, a, b, z in kpz_table:
        print(f"  {n:<22s}  {a:>8.3f}  {b:>8.3f}  {z:>8.3f}")
    print()
    print("Exponent identity (Galilean invariance + scaling): alpha + z = 2 in KPZ.")
    print()
    print("ASEP (asymmetric simple exclusion process): 1d hopping particles with")
    print("hard-core exclusion biased one way. Maps to KPZ; current fluctuations")
    print("obey Tracy-Widom; exact solutions (Bethe ansatz, matrix product).")
    print()
    print("Fluctuation theorems (non-equilibrium identities):")
    print("  Jarzynski (1997):  <exp(-beta W)> = exp(-beta Delta F)")
    print("  Crooks (1999):     P_F(W) / P_R(-W) = exp(beta (W - Delta F))")
    print("  Onsager:           reciprocal coefficients L_ij = L_ji  (linear regime)")
    print()
    print("These RESCUE thermodynamic free-energy differences from non-equilibrium")
    print("trajectories - validated in single-molecule pulling (Liphardt 2002,")
    print("Collin 2005 RNA hairpins).")
    print()
    print("Substrate framing: KPZ = universal scaling of substrate-strain growth")
    print("when nonlinearity (lambda/2)(grad h)^2 is present. The 1/3 exponent is")
    print("a fingerprint of substrate-medium dynamics under directed driving.")

    # ============================================================
    section(11, "SUMMARY: low-K, thermal, and driven substrate")
    # ============================================================
    print("Soft matter and active matter share one organizing principle: the")
    print("substrate elastic stiffness K is small enough that thermal kT, drag")
    print("gamma, and external drive compete on equal footing.")
    print()
    print("Configuration -> phenomenology:")
    print("  K small + orientational anisotropy   -> liquid crystals, smectics, BPs")
    print("  K small + 1d connectivity            -> polymers (R ~ N^nu)")
    print("  K finite + kT->0                      -> granular media (Liu-Nagel)")
    print("  K small + interfacial gamma_s        -> foams, emulsions (Plateau)")
    print("  K + crosslinks above p_c             -> gels, glasses (Flory-Stockmayer)")
    print("  K small + active drive               -> flocks, MIPS, active nematics")
    print("  K_bend = 20 kT + cytoskeleton + ATP  -> living cells, embryos")
    print("  oscillatory drive + viscoelastic     -> rheology G', G''")
    print("  Re -> 0                               -> Stokes flow, microfluidics")
    print("  driven 1+1d growth                    -> KPZ universality (1/3 exponent)")
    print()
    print("Honest scoreboard: substrate framework REPRODUCES standard soft-matter")
    print("results (Frank-Oseen, Flory, Janssen, Plateau, KPZ, Jarzynski) because")
    print("they are continuum / statistical limits of the same Lagrangian. The")
    print("value-add is unification across length scales (atomic -> macroscopic)")
    print("and bridging equilibrium and non-equilibrium phases under one ontology.")
    print()
    print("Open frontier: the substrate ontology suggests that ACTIVE matter is")
    print("the natural way to realize effective negative damping in a passive,")
    print("dissipative substrate -> may also offer language for cosmological")
    print("dark-energy-like driving (energy injection at small scales).")


if __name__ == "__main__":
    main()
