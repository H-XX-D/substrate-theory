"""Fluid turbulence through the strain-medium framework.

Turbulence is one of the few open problems remaining in classical physics
(Feynman's "most important unsolved problem of classical physics").
The strain-medium ontology recasts turbulence as a substrate-strain
energy cascade with broken scale invariance.

Strain-medium primitives (4 + 1 cap):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Turbulence  =  substrate-strain pattern with broken scale invariance,
energy cascading from large eddies (forcing) to small eddies (dissipation)
through nonlinear strain-strain coupling. The famous -5/3 spectrum is
scale-self-similar substrate-strain transfer in the inertial range.
Intermittency = local saturation events (sigma -> 1/2) producing burst
dissipation at small scales.
"""

from __future__ import annotations
import math


# ---- universal constants ----
PI = math.pi
RHO_AIR = 1.225        # kg/m^3 at STP
NU_AIR  = 1.5e-5       # m^2/s kinematic viscosity (air)
NU_WATER = 1.0e-6      # m^2/s kinematic viscosity (water)
MU_AIR  = NU_AIR * RHO_AIR


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Fluid turbulence in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2")
    print("Turbulence = scale-broken substrate-strain pattern with energy cascade")
    print("Inertial range = scale-self-similar substrate strain transfer (-5/3)")
    print("Intermittency  = saturation events sigma->1/2 at small scales")
    print()

    # ============================================================
    section(1, "LAMINAR -> TURBULENT TRANSITION (Reynolds number)")
    # ============================================================
    print("Reynolds number = ratio of inertial to viscous strain forces:")
    print("  Re = rho U L / mu = U L / nu")
    print()
    print("Re below critical -> laminar (smooth substrate strain field)")
    print("Re above critical -> turbulent (multi-scale strain pattern)")
    print()
    print(f"  {'flow geometry':<32s}  {'Re_crit':>10s}  {'mechanism':<22s}")
    print(f"  {'-'*32:<32s}  {'-'*10:>10s}  {'-'*22:<22s}")
    transitions = [
        ("Pipe flow (Hagen-Poiseuille)", 2300,  "wall-bounded shear"),
        ("Plane Couette flow",            350,  "linear stable, sub-crit."),
        ("Plane Poiseuille (channel)",   5772,  "Tollmien-Schlichting"),
        ("Boundary layer (flat plate)", 500000, "TS waves -> bypass"),
        ("Free shear layer / mixing",     50,   "Kelvin-Helmholtz"),
        ("Jet (round)",                  1000,  "axisymm. instability"),
        ("Wake behind cylinder",          47,   "von Karman shedding"),
        ("Rayleigh-Benard convection",   1708,  "buoyancy (Ra crit.)"),
        ("Taylor-Couette",                41,   "centrifugal instability"),
    ]
    for geom, rc, mech in transitions:
        print(f"  {geom:<32s}  {rc:>10d}  {mech:<22s}")
    print()
    print("Substrate reading: at low Re, viscous gamma drag damps perturbations")
    print("of the strain field. At high Re, nonlinear self-coupling of substrate")
    print("strain (the (u.grad)u term) overcomes drag and triggers cascade.")
    print()
    print("Kelvin-Helmholtz instability at a shear interface:")
    print("  growth rate omega_KH = k * |Delta U| / 2  (inviscid)")
    print("  -> any wavelength unstable in inviscid limit")
    for k_lam in (0.01, 0.1, 1.0):
        omega = k_lam * 1.0 / 2.0
        print(f"  k={k_lam:>5.2f}/m, dU=1 m/s -> omega_KH = {omega:.3f} 1/s")

    # ============================================================
    section(2, "KOLMOGOROV 1941 ENERGY CASCADE")
    # ============================================================
    print("Energy injected at large scale L (forcing) cascades through")
    print("intermediate scales (inertial range) and dissipates at scale eta")
    print("(viscous cutoff). In steady state, the dissipation rate epsilon")
    print("is constant across the inertial range:")
    print()
    print("  epsilon  =  rate of substrate-strain energy transfer per unit mass")
    print("           [m^2 / s^3]")
    print()
    print("Inertial-range spectrum (Kolmogorov 1941):")
    print("  E(k)  =  C_K * epsilon^(2/3) * k^(-5/3)")
    print("  with universal Kolmogorov constant C_K ~ 1.5 (~ 1.4 - 1.7)")
    print()
    print("  measured to extreme accuracy across atmosphere, ocean, lab,")
    print("  galaxy clusters. Maybe the most-confirmed power law in physics.")
    print()
    print("Kolmogorov dissipation scale (where viscous drag finally wins):")
    print("  eta = (nu^3 / epsilon)^(1/4)")
    print("  u_eta = (nu * epsilon)^(1/4)")
    print("  tau_eta = (nu / epsilon)^(1/2)")
    print()
    print("Scale separation L / eta ~ Re^(3/4):")
    print()
    print(f"  {'system':<28s}  {'L [m]':>10s}  {'U [m/s]':>8s}  {'Re':>10s}  {'L/eta':>10s}")
    examples = [
        ("Lab pipe (water)",        0.05, 1.0,    NU_WATER),
        ("Atmospheric BL",          1000.0, 10.0,   NU_AIR),
        ("Ocean mixed layer",       100.0, 0.5,    NU_WATER),
        ("Aircraft wing BL",        2.0,  250.0,   NU_AIR),
        ("Tokamak edge",            0.1,  1000.0,  1e-2),
        ("Solar convection",        2.0e8, 100.0,  1e-2),
        ("ISM cold neutral",        3e16,  10000.0, 1e17),  # nu_eff astrophys.
    ]
    for name, L, U, nu in examples:
        Re = U * L / nu
        ratio = Re ** 0.75
        print(f"  {name:<28s}  {L:>10.2e}  {U:>8.2f}  {Re:>10.2e}  {ratio:>10.2e}")
    print()
    print("Substrate framing: -5/3 spectrum is the unique scaling in which")
    print("substrate strain transfer rate epsilon is constant across scales,")
    print("dimensionally forcing E(k) = C_K epsilon^(2/3) k^(-5/3).")
    print("Universality of C_K reflects universality of the substrate Lagrangian.")

    # ============================================================
    section(3, "STRUCTURE FUNCTIONS & INTERMITTENCY")
    # ============================================================
    print("n-th order velocity structure function:")
    print("  S_n(r) = < |u(x+r) - u(x)|^n >  ~  r^{zeta(n)}")
    print()
    print("Kolmogorov 1941 prediction: zeta_K41(n) = n / 3")
    print()
    print("4/5 law (exact, no closure assumption):")
    print("  S_3(r) = -(4/5) epsilon r")
    print("  -> zeta(3) = 1 EXACTLY (rigorous from Navier-Stokes)")
    print()
    print("Anomalous scaling (intermittency) deviates from K41 for n != 3:")
    print()
    print(f"  {'n':>3s}  {'K41 n/3':>10s}  {'measured':>10s}  {'She-Leveque':>12s}")
    print(f"  {'-'*3:>3s}  {'-'*10:>10s}  {'-'*10:>10s}  {'-'*12:>12s}")
    # She-Leveque: zeta(n) = n/9 + 2(1 - (2/3)^(n/3))
    for n in range(1, 11):
        k41 = n / 3.0
        sl = n/9.0 + 2.0*(1.0 - (2.0/3.0)**(n/3.0))
        # measured (Anselmet et al. 1984, Benzi et al. 1993, etc.)
        measured = {1:0.37, 2:0.70, 3:1.00, 4:1.28, 5:1.54,
                    6:1.78, 7:2.00, 8:2.23, 9:2.41, 10:2.59}[n]
        print(f"  {n:>3d}  {k41:>10.4f}  {measured:>10.4f}  {sl:>12.4f}")
    print()
    print("Pattern: at high n the measured exponents lag K41 (concave curve).")
    print("Origin: rare, intense events (small-scale strain bursts) dominate")
    print("high-order moments. K41 assumes mean cascade; reality has fluctuating")
    print("local epsilon -> log-normal / multifractal models.")
    print()
    print("Substrate framing: intermittency = local saturation sigma -> 1/2 at")
    print("small scales. The cap forbids unbounded strain density, so when a")
    print("strain pocket approaches saturation it MUST dump energy via burst")
    print("dissipation. These rare bursts contribute disproportionately to")
    print("S_n for large n, producing the concave zeta(n) curve.")

    # ============================================================
    section(4, "TWO-DIMENSIONAL TURBULENCE (dual cascade)")
    # ============================================================
    print("In 2D, vortex stretching is forbidden -> different conservation laws:")
    print("  - energy E   conserved")
    print("  - enstrophy Z = <omega^2> / 2  ALSO conserved (vorticity squared)")
    print()
    print("Kraichnan-Batchelor dual cascade:")
    print("  - INVERSE energy cascade   (large k -> small k)   E(k) ~ k^(-5/3)")
    print("  - FORWARD enstrophy cascade (small k -> large k)  E(k) ~ k^(-3)")
    print()
    print(f"  {'cascade':<22s}  {'spectrum':>14s}  {'direction':<26s}")
    print(f"  {'-'*22:<22s}  {'-'*14:>14s}  {'-'*26:<26s}")
    cascades = [
        ("3D energy",            "k^(-5/3)",  "forward (large->small)"),
        ("2D inverse energy",    "k^(-5/3)",  "inverse (small->large)"),
        ("2D forward enstrophy", "k^(-3)",    "forward (large->small)"),
        ("3D MHD Iroshnikov",    "k^(-3/2)",  "isotropic Alfvenic"),
        ("3D MHD Goldreich-Sri", "k_perp^(-5/3)", "anisotropic"),
    ]
    for c, s, d in cascades:
        print(f"  {c:<22s}  {s:>14s}  {d:<26s}")
    print()
    print("Atmospheric & oceanic relevance:")
    print("  - large-scale flow is quasi-2D (thin layer, rotation)")
    print("  - explains why hurricanes / Jupiter Great Red Spot persist")
    print("  - inverse cascade self-organizes into long-lived vortices")
    print()
    print("Substrate reading: enstrophy conservation is a substrate")
    print("topological constraint in the 2D-confined strain field.")
    print("With one less spatial degree of freedom, the strain cannot fold")
    print("its way to small scales without piling up vorticity gradients.")
    print("The dual cascade splits the budget: energy rolls UP, enstrophy DOWN.")

    # ============================================================
    section(5, "WALL TURBULENCE & BOUNDARY LAYERS")
    # ============================================================
    print("Near a solid wall the substrate strain field is constrained to zero")
    print("velocity (no-slip). This produces a universal boundary layer with")
    print("self-similar profile in wall units:")
    print()
    print("  y+ = y * u_tau / nu    (wall-normal distance)")
    print("  u+ = u / u_tau         (velocity)")
    print("  u_tau = sqrt(tau_w / rho)   (friction velocity)")
    print()
    print("Three sublayers:")
    print()
    print(f"  {'region':<20s}  {'y+':>10s}  {'u+':<26s}")
    print(f"  {'-'*20:<20s}  {'-'*10:>10s}  {'-'*26:<26s}")
    layers = [
        ("Viscous sublayer",    "0 - 5",    "u+ = y+  (linear)"),
        ("Buffer layer",        "5 - 30",   "transition (matched)"),
        ("Log-law region",      "30 - 300", "u+ = (1/k) ln(y+) + B"),
        ("Outer / wake",        "> 300",    "u+ = log + wake func."),
    ]
    for r, y, u in layers:
        print(f"  {r:<20s}  {y:>10s}  {u:<26s}")
    print()
    KAPPA = 0.41   # von Karman constant
    B_SMOOTH = 5.2
    print(f"Universal constants:  kappa (von Karman) = {KAPPA},   B (smooth) = {B_SMOOTH}")
    print()
    print("Verify log-law for typical y+ values:")
    print(f"  {'y+':>8s}  {'u+ predicted':>14s}")
    for yp in (30, 50, 100, 300, 1000):
        up = (1.0 / KAPPA) * math.log(yp) + B_SMOOTH
        print(f"  {yp:>8d}  {up:>14.3f}")
    print()
    print("Skin friction (smooth flat plate, turbulent BL, Schlichting):")
    print("  C_f = 0.026 / Re_x^(1/7)")
    print()
    print(f"  {'Re_x':>10s}  {'C_f':>10s}  {'tau_w/rho_U^2':>14s}")
    for Re_x in (1e5, 1e6, 1e7, 1e8, 1e9):
        Cf = 0.026 / Re_x ** (1.0/7.0)
        print(f"  {Re_x:>10.2e}  {Cf:>10.5f}  {Cf/2:>14.5f}")
    print()
    print("Substrate origin of log law: only one length scale survives in")
    print("the overlap region (y itself); dimensional analysis then forces")
    print("du/dy = u_tau / (kappa y), integrating to the logarithm. kappa")
    print("is a universal substrate-strain transfer coefficient at the wall.")

    # ============================================================
    section(6, "TURBULENT TRANSPORT AND MIXING")
    # ============================================================
    print("Turbulent eddies transport mass, momentum and heat far faster than")
    print("molecular diffusion. Eddy diffusivity:")
    print()
    print("  D_T  ~  u' L  (mixing-length estimate)")
    print()
    print("Compare to molecular: nu (momentum), kappa (heat), D (species).")
    print("Schmidt and Prandtl numbers:")
    print("  Sc = nu / D     (mass)")
    print("  Pr = nu / kappa (heat)")
    print()
    print(f"  {'fluid / scalar':<28s}  {'Sc or Pr':>10s}")
    print(f"  {'-'*28:<28s}  {'-'*10:>10s}")
    sc_pr = [
        ("Air (heat) Pr",       0.71),
        ("Water (heat) Pr",     7.0),
        ("Liquid metal Pr",     0.025),
        ("Glycerin Pr",         12000.0),
        ("Salt in water Sc",    700.0),
        ("Dye in water Sc",     2500.0),
        ("Gas in air Sc",       1.0),
    ]
    for f, v in sc_pr:
        print(f"  {f:<28s}  {v:>10.3g}")
    print()
    print("Obukhov-Corrsin: passive scalar variance also obeys k^(-5/3) in")
    print("inertial-convective range:")
    print("  E_theta(k) = C_OC * chi * epsilon^(-1/3) * k^(-5/3)")
    print()
    print("Below the scalar Batchelor scale eta_B = eta / sqrt(Sc), scalar")
    print("variance is wound up by viscous strain into a k^(-1) range")
    print("(Batchelor 1959). Important for high-Sc fluids (salt in ocean).")
    print()
    print("Substrate reading: scalar field rides on the velocity strain field")
    print("as a passive marker. The cascade of strain advects the scalar to")
    print("ever-smaller scales; molecular diffusion finally smears it at eta_B.")

    # ============================================================
    section(7, "LES, RANS, DNS (computational closures)")
    # ============================================================
    print("DNS (direct numerical simulation) resolves all scales L down to eta:")
    print("  cost ~ Re^3 (3D space) * Re^(3/4) (time) ~ Re^(11/4)")
    print()
    print("For industrial Re (1e7) DNS needs ~1e19 grid points — unattainable.")
    print()
    print("Practical approaches:")
    print()
    print(f"  {'method':<8s}  {'resolves':<28s}  {'cost / Re':<22s}")
    print(f"  {'-'*8:<8s}  {'-'*28:<28s}  {'-'*22:<22s}")
    methods = [
        ("DNS",   "everything down to eta",       "Re^(11/4)"),
        ("LES",   "large eddies, models SGS",     "Re^(13/7) (wall-res)"),
        ("RANS",  "ensemble means, models all",   "~ Re^0 (geometry)"),
        ("DES/hybrid", "RANS at wall, LES outer", "intermediate"),
    ]
    for m, r, c in methods:
        print(f"  {m:<8s}  {r:<28s}  {c:<22s}")
    print()
    print("RANS turbulence models (closure problem: Reynolds stress unknown):")
    print()
    print(f"  {'model':<14s}  {'eqs':>4s}  {'class':<22s}  {'comment':<22s}")
    rans_models = [
        ("k-epsilon",     2, "two-equation",       "general purpose"),
        ("k-omega",       2, "two-equation",       "better near walls"),
        ("k-omega SST",   2, "blended",            "industry default"),
        ("Spalart-Allmaras", 1, "one-equation",    "aerodynamics"),
        ("RSM (Reynolds stress)", 7, "differential", "anisotropic flows"),
        ("v2-f",          4, "elliptic relax.",    "near-wall asymmetry"),
    ]
    for m, n, c, com in rans_models:
        print(f"  {m:<14s}  {n:>4d}  {c:<22s}  {com:<22s}")
    print()
    print("LES sub-grid models (filter at scale Delta, model below):")
    print("  - Smagorinsky (1963):  nu_t = (C_s Delta)^2 |S|,  C_s ~ 0.1 - 0.2")
    print("  - Dynamic Smagorinsky (Germano 1991): C_s computed locally")
    print("  - WALE (Nicoud-Ducros): better near walls, vanishes in laminar zones")
    print("  - Sigma model: vanishes in 2D / pure shear")
    print()
    print("Substrate framing: closure problem = no fundamental ignorance, just")
    print("computational cost. The substrate Lagrangian determines all moments;")
    print("RANS / LES are CHOICES of which strain scales to resolve explicitly.")

    # ============================================================
    section(8, "MHD TURBULENCE (substrate + magnetic field)")
    # ============================================================
    print("In conducting fluids the substrate strain couples to a magnetic field B:")
    print()
    print("  Iroshnikov-Kraichnan (1965):  E(k) ~ k^(-3/2)  (isotropic Alfven)")
    print("  Goldreich-Sridhar (1995):     E(k_perp) ~ k_perp^(-5/3)")
    print("                                with critical balance k_par ~ k_perp^(2/3)")
    print()
    print("Critical balance: nonlinear interaction time = Alfven crossing time")
    print("  -> anisotropic eddies elongated along B")
    print()
    print(f"  {'environment':<26s}  {'spectrum':<18s}  {'observed in':<18s}")
    print(f"  {'-'*26:<26s}  {'-'*18:<18s}  {'-'*18:<18s}")
    mhd = [
        ("Solar wind",          "k^(-5/3) inertial",  "Helios, Voyager"),
        ("Solar corona",        "anisotropic GS",     "RTV, AIA"),
        ("ICM (galaxy clusters)", "k^(-5/3)?",        "Faraday rotation"),
        ("ISM compressible",    "k^(-1.7-2.0)",       "21cm, dust"),
        ("Tokamak edge",        "k^(-5/3) plus ZF",   "fluctuation diag."),
        ("Earth magnetotail",   "k^(-5/3) above f_i", "MMS, Cluster"),
    ]
    for env, spec, obs in mhd:
        print(f"  {env:<26s}  {spec:<18s}  {obs:<18s}")
    print()
    print("Dynamo action: small-scale magnetic field grows via random stretching")
    print("of B by turbulent shear (Kazantsev mechanism, fluctuation dynamo).")
    print("Generates mean field via alpha-effect in rotating, helical flows.")
    print()
    print("Substrate framing: B is a separate substrate strain mode (transverse,")
    print("propagates as Alfven wave). MHD turbulence = TWO coupled strain")
    print("cascades, one velocity, one magnetic, sharing the same substrate.")

    # ============================================================
    section(9, "TURBULENT COMBUSTION & REACTIVE FLOWS")
    # ============================================================
    print("Turbulent flame speed >> laminar flame speed because turbulence")
    print("WRINKLES the flame front, increasing surface area:")
    print()
    print("  S_T / S_L  ~  1 + C (u' / S_L)^n   (Damkohler regime)")
    print()
    print("Damkohler number: Da = tau_t / tau_chem = (L/u') / (delta_L/S_L)")
    print()
    print(f"  {'regime':<24s}  {'Da':>8s}  {'character':<26s}")
    regimes = [
        ("Wrinkled flamelets",     ">> 1",  "thin flame, slow turb."),
        ("Corrugated flamelets",   "> 1",   "thicker wrinkles"),
        ("Thin reaction zones",    "~ 1",   "preheat zone broken"),
        ("Broken reaction zones",  "<< 1",  "extinction events"),
        ("Distributed reactions",  "<< 1",  "well-stirred reactor"),
    ]
    for r, d, c in regimes:
        print(f"  {r:<24s}  {d:>8s}  {c:<26s}")
    print()
    print("Borghi diagram axes:  u'/S_L   vs   L / delta_L")
    print()
    print(f"  {'fuel':<14s}  {'S_L [m/s]':>10s}  {'delta_L [mm]':>12s}")
    print(f"  {'-'*14:<14s}  {'-'*10:>10s}  {'-'*12:>12s}")
    flames = [
        ("Methane/air",   0.38,  0.4),
        ("Propane/air",   0.42,  0.4),
        ("Hydrogen/air",  2.50,  0.04),
        ("Ethanol/air",   0.45,  0.4),
        ("Acetylene/air", 1.55,  0.1),
    ]
    for f, sl, dl in flames:
        print(f"  {f:<14s}  {sl:>10.2f}  {dl:>12.2f}")
    print()
    print("Substrate framing: combustion couples a chemical-strain field")
    print("(reaction progress variable) to the velocity-strain cascade.")
    print("Saturation sigma<=1/2 caps local reaction rate (e.g. through")
    print("fuel availability), preventing infinite local heat release.")

    # ============================================================
    section(10, "OPEN PROBLEMS (Clay Millennium and beyond)")
    # ============================================================
    print("Famous unsolved problems in turbulence and Navier-Stokes:")
    print()
    print(f"  {'problem':<36s}  {'status':<26s}")
    print(f"  {'-'*36:<36s}  {'-'*26:<26s}")
    problems = [
        ("3D NS regularity (Clay Millennium)",  "open: $1M prize"),
        ("Closure of moment hierarchy",         "open: phenomenology only"),
        ("Origin of intermittency",             "open: She-Leveque empirical"),
        ("Re -> infinity dissipation anomaly",  "phenomenological (epsilon -> const)"),
        ("Universality of Kolmogorov constants", "narrow numerical, no proof"),
        ("Onsager conjecture (proved 2018)",    "Isett: yes, h<1/3 dissipates"),
        ("Beale-Kato-Majda criterion",          "necessary condition only"),
        ("Holder regularity threshold",         "h=1/3 confirmed"),
        ("Anomalous scaling of zeta(n)",        "open: no first-principles theory"),
        ("Wall log-law derivation",             "phenomenological"),
        ("Subgrid model universality",          "open"),
    ]
    for p, s in problems:
        print(f"  {p:<36s}  {s:<26s}")
    print()
    print("Beale-Kato-Majda criterion (1984): a smooth NS solution can blow up")
    print("at time T only if integral_0^T ||omega(t)||_infty dt = infinity.")
    print("Provides the sharp control on regularity.")
    print()
    print("Onsager 1949 conjecture (proved by Isett 2018): for Holder regularity")
    print("h > 1/3, weak solutions of Euler conserve energy; for h < 1/3,")
    print("anomalous dissipation is possible. The K41 value h = 1/3 is the")
    print("EXACT borderline -- a stunning consistency check.")
    print()
    print("Substrate position on these problems:")
    print(" - Closure: no separate closure needed; substrate Lagrangian fixes")
    print("   all moments. Closure is computational, not foundational.")
    print(" - Intermittency: arises from sigma <= 1/2 saturation events at")
    print("   small scales (not extra physics, just the cap activated).")
    print(" - Dissipation anomaly: epsilon stays finite as nu -> 0 because")
    print("   substrate strain cascades faster as Re increases, always")
    print("   delivering energy to scales where any small viscosity can")
    print("   absorb it. This is consistent with Onsager's 1/3.")
    print(" - NS regularity: blowup would require strain density at a point")
    print("   to diverge, which sigma <= 1/2 cap forbids -> consistency")
    print("   with the conjectured global regularity.")
    print()

    # ============================================================
    section(11, "SUMMARY: turbulence as substrate-strain cascade")
    # ============================================================
    print("Turbulence is the multi-scale, scale-broken behaviour of the same")
    print("substrate strain field that governs laminar flow, sound waves and")
    print("solid-state phonons. Difference: at high Re the (u.grad)u nonlinearity")
    print("dominates, opening a CASCADE channel that transfers strain energy")
    print("through scales until viscous gamma drag finally absorbs it at eta.")
    print()
    print("Configuration -> phenomenon:")
    print("  Re < Re_c                  -> laminar")
    print("  Re > Re_c, 3D              -> forward energy cascade, k^(-5/3)")
    print("  Re > Re_c, 2D              -> dual cascade (inverse E, forward Z)")
    print("  near wall                  -> log-law BL via single-scale matching")
    print("  saturation events at eta   -> intermittency / anomalous zeta(n)")
    print("  scalar advection           -> Obukhov-Corrsin / Batchelor mixing")
    print("  + magnetic field           -> MHD (Iroshnikov-Kraichnan / GS95)")
    print("  + chemistry                -> turbulent flames (Damkohler, Borghi)")
    print()
    print("Substrate predictions:")
    print(" 1. -5/3 spectrum is forced by scale-self-similar substrate strain")
    print("    transfer with constant epsilon.")
    print(" 2. Anomalous scaling of zeta(n) traces to sigma <= 1/2 saturation")
    print("    events at small scales (rare burst dissipation).")
    print(" 3. Onsager's h=1/3 borderline matches K41 exactly because that is")
    print("    the unique exponent at which substrate strain cascade is")
    print("    BARELY able to sustain finite epsilon as nu -> 0.")
    print(" 4. Global NS regularity is consistent with the cap sigma <= 1/2,")
    print("    which forbids strain density divergence at a point.")
    print()
    print("Honest scoreboard: substrate REPRODUCES standard turbulence")
    print("phenomenology (Re scaling, -5/3, log-law, dual cascade, etc.) and")
    print("offers a unifying ontology -- one strain field, one cascade story,")
    print("for fluid, plasma, atmospheric, oceanic, astrophysical and reactive")
    print("turbulence -- without claiming new measurable predictions over NS.")
    print("Its added value is interpretive: closure, intermittency, regularity,")
    print("and dissipation anomaly all become facets of the substrate cap.")


if __name__ == "__main__":
    main()
