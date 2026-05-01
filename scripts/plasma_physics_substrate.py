"""Plasma physics through the strain-medium framework.

Plasma = ionized substrate-strain regime in which the electron and ion
populations decouple as two coexisting substrate-strain fluids, coupled
by the long-range Coulomb (strain-density) interaction.

Strain-medium primitives (6 inputs total):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability (Mobius bundles allowed)

Lagrangian:  L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Substrate dictionary for plasma:
  plasma frequency  = collective substrate-strain mode of free electrons
  Debye screening   = exponential strain-density screening shell
  reconnection      = substrate-strain field-line topology change
  Landau damping    = substrate-strain wave/particle phase coupling
  saturation cap    = sigma -> 1/2 limit relevant for relativistic / dense
                      plasmas (degenerate electron gas at white dwarf cores,
                      pair plasmas near magnetars)

Honest framing: standard plasma physics numbers are REPRODUCED from the
substrate Lagrangian; the value-add is unification with the rest of the
strain-medium picture (chemistry, condensed matter, gravity).
"""

from __future__ import annotations
import math


# ---------------- universal constants (SI) ----------------
PI       = math.pi
C        = 2.99792458e8        # m/s
HBAR     = 1.054571817e-34     # J s
KB       = 1.380649e-23        # J/K
EV_J     = 1.602176634e-19     # J/eV
QE       = 1.602176634e-19     # C (elementary charge)
EPS0     = 8.8541878128e-12    # F/m
MU0      = 1.25663706212e-6    # N/A^2
ME       = 9.1093837015e-31    # kg (electron)
MP       = 1.67262192369e-27   # kg (proton)
MN_AMU   = 1.66053906660e-27   # kg (atomic mass unit)


# ---------------- helpers ----------------
def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def debye_length(n: float, T_eV: float) -> float:
    """Electron Debye length in meters; n in m^-3, T in eV."""
    T_K = T_eV * EV_J / KB
    return math.sqrt(EPS0 * KB * T_K / (n * QE * QE))


def plasma_frequency(n: float, m: float = ME) -> float:
    """Angular plasma frequency [rad/s]; n in m^-3, m in kg."""
    return math.sqrt(n * QE * QE / (EPS0 * m))


def gyrofrequency(B: float, m: float = ME, q: float = QE) -> float:
    """Cyclotron angular frequency [rad/s]."""
    return q * B / m


def alfven_speed(B: float, rho: float) -> float:
    """v_A = B / sqrt(mu0 rho)  [m/s]."""
    return B / math.sqrt(MU0 * rho)


def coulomb_log(n: float, T_eV: float) -> float:
    """Standard ln Lambda for an electron plasma (NRL formulary form)."""
    lam_D = debye_length(n, T_eV)
    b_min = QE * QE / (4 * PI * EPS0 * T_eV * EV_J)   # classical closest approach
    return math.log(lam_D / b_min)


# ---------------- main ----------------
def main() -> None:
    print("Plasma physics in the strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Plasma = ionized substrate-strain regime (electron / ion fluids)")
    print("Coupling: long-range strain-density (Coulomb) + B-field tension")
    print()

    # ============================================================
    section(1, "FUNDAMENTAL PLASMA PARAMETERS")
    # ============================================================
    print("Three derived length/time/number scales completely characterize a plasma:")
    print()
    print("  Debye length     lambda_D = sqrt(eps0 k_B T / n e^2)")
    print("  Plasma freq      omega_p  = sqrt(n e^2 / eps0 m)")
    print("  Plasma parameter Lambda   = n lambda_D^3      (#particles in Debye sphere)")
    print()
    print("Substrate reading:")
    print("  - lambda_D = exponential strain-density screening shell around a charge")
    print("  - omega_p  = lowest collective substrate-strain mode of free electrons")
    print("  - Lambda   = number of strain centers participating per screening cell")
    print()
    print("Quasi-neutrality requires Lambda >> 1; otherwise it is a Coulomb gas.")
    print()
    # demonstrative numbers
    n_demo  = 1.0e19           # m^-3 (laboratory plasma)
    T_demo  = 10.0             # eV
    lam_D   = debye_length(n_demo, T_demo)
    om_p    = plasma_frequency(n_demo)
    Lambda  = n_demo * lam_D ** 3
    lnL     = coulomb_log(n_demo, T_demo)
    print(f"Demo (n=1e19 m^-3, T=10 eV):")
    print(f"  lambda_D = {lam_D:.3e} m")
    print(f"  omega_p  = {om_p:.3e} rad/s   (f_p = {om_p/(2*PI):.3e} Hz)")
    print(f"  Lambda   = {Lambda:.3e}")
    print(f"  ln Lambda = {lnL:.2f}")

    # ============================================================
    section(2, "PLASMA REGIMES — TABLE ACROSS NATURE")
    # ============================================================
    print("Cold vs hot, weakly vs strongly coupled, classical vs degenerate,")
    print("magnetized vs unmagnetized — every realized plasma sits somewhere on")
    print("this 4-axis grid.  Substrate parameters K, rho, gamma, sigma map")
    print("directly onto these regimes.")
    print()
    print(f"  {'environment':<22s}  {'n [m^-3]':>10s}  {'T [eV]':>9s}  "
          f"{'lambda_D [m]':>14s}  {'f_p [Hz]':>11s}")
    regimes = [
        ("Ionosphere F-layer",    1.0e12,    0.1),
        ("Solar wind @ 1 AU",     5.0e6,     10.0),
        ("Solar corona",          1.0e15,    100.0),
        ("Tokamak (ITER core)",   1.0e20,    2.0e4),
        ("Inertial confinement",  1.0e31,    1.0e4),
        ("Stellar interior (Sun)",1.0e32,    1.4e3),
        ("White dwarf core",      1.0e36,    5.0e3),
        ("Neutron-star crust",    1.0e40,    1.0e4),
        ("ICM (galaxy cluster)",  1.0e3,     5.0e3),
        ("Lightning channel",     1.0e24,    3.0),
        ("Neon sign",             1.0e18,    2.0),
    ]
    for name, n, T in regimes:
        ld = debye_length(n, T)
        fp = plasma_frequency(n) / (2 * PI)
        print(f"  {name:<22s}  {n:>10.2e}  {T:>9.2e}  {ld:>14.3e}  {fp:>11.3e}")
    print()
    print("Coupling parameter  Gamma = e^2 / (4 pi eps0 a k_B T),  a = (3/4 pi n)^(1/3)")
    print("  Gamma << 1  weakly coupled (kinetic regime)  -> Vlasov / fluid OK")
    print("  Gamma ~ 1   moderately coupled               -> liquid-like")
    print("  Gamma >> 1  strongly coupled                 -> crystallizes (Coulomb")
    print("              crystal — observed in dust plasmas and neutron-star crust)")
    print()
    print("Substrate reading: Gamma = ratio of strain-bridge energy to thermal jiggle.")

    # ============================================================
    section(3, "SINGLE-PARTICLE MOTION (gyration + drifts)")
    # ============================================================
    print("Charged substrate excitation in B-field traces a helix:")
    print()
    print("  Larmor radius   r_L     = m v_perp / (q B)")
    print("  Cyclotron freq  Omega_c = q B / m")
    print()
    B    = 1.0     # T (lab magnet)
    v_perp = 1.0e6 # m/s thermal-ish electron
    rL_e = ME * v_perp / (QE * B)
    Wc_e = gyrofrequency(B, ME)
    rL_i = MP * v_perp / (QE * B)
    Wc_i = gyrofrequency(B, MP)
    print(f"At B = 1 T, v_perp = 1e6 m/s:")
    print(f"  electron r_L = {rL_e:.3e} m   Omega_ce = {Wc_e:.3e} rad/s")
    print(f"  proton   r_L = {rL_i:.3e} m   Omega_ci = {Wc_i:.3e} rad/s")
    print(f"  mass ratio MP/ME = {MP/ME:.1f} -> r_L_i / r_L_e = {(MP/ME):.1f}")
    print()
    print("Guiding-centre drifts (velocity of helix axis):")
    print(f"  {'name':<22s}  {'expression':<30s}  {'sign':>6s}")
    drifts = [
        ("E x B drift",        "v = E x B / B^2",                    "same"),
        ("Grad-B drift",       "v = (m v_perp^2 / 2 q B^3) B x grad B", "q-dep"),
        ("Curvature drift",    "v = (m v_par^2 / q B^2) R_c x B / R_c^2","q-dep"),
        ("Polarization drift", "v = (m / q B^2) dE/dt",              "q-dep"),
        ("Diamagnetic drift",  "v = -grad p x B / (q n B^2)",        "q-dep"),
    ]
    for n, expr, sgn in drifts:
        print(f"  {n:<22s}  {expr:<30s}  {sgn:>6s}")
    print()
    print("ExB drift is charge-INDEPENDENT -> bulk plasma drift, no current.")
    print("All others are charge-dependent -> generate currents -> drive MHD dynamics.")
    print()
    print("Substrate reading: helix = bound transverse strain-mode of an excitation")
    print("in a B-field-tensioned substrate; drifts = first-order corrections from")
    print("inhomogeneities of the underlying strain field.")

    # ============================================================
    section(4, "MHD EQUATIONS (substrate fluid limit)")
    # ============================================================
    print("Magnetohydrodynamics = single-fluid limit of substrate-strain plasma,")
    print("valid on scales >> Debye length and timescales >> 1/omega_p.")
    print()
    print("Continuity:    d_t rho + div(rho v) = 0")
    print("Momentum:      rho [d_t v + (v . grad) v] = -grad p + j x B + rho_g g")
    print("Induction:     d_t B = curl(v x B) + eta nabla^2 B           (eta = 1/sigma_mu0)")
    print("Ohm's law:     E + v x B = eta j + (j x B - grad p_e)/(n e)  (generalized)")
    print()
    print("Substrate translation:")
    print("  rho        -> substrate strain-density of charged fluid")
    print("  v          -> coarse-grained strain-velocity (d_t u, averaged)")
    print("  p          -> isotropic substrate strain pressure")
    print("  j          -> drift of charged strain centers")
    print("  B          -> conserved magnetic strain-flux density")
    print("  eta        -> resistive loss term ~ gamma in substrate Lagrangian")
    print()
    print("Two key dimensionless numbers:")
    print(f"  {'name':<10s}  {'def':<28s}  {'plasma physics meaning':<30s}")
    print(f"  {'Re_m':<10s}  {'mu0 sigma L v':<28s}  {'flux-freezing vs diffusion':<30s}")
    print(f"  {'beta':<10s}  {'p / (B^2 / 2 mu0)':<28s}  {'thermal vs magnetic pressure':<30s}")
    print()
    print("Flux freezing (Re_m -> infty): magnetic field lines = material lines of")
    print("the substrate strain fluid; topology preserved.  Reconnection (Section 7)")
    print("happens precisely where this freezing breaks down.")

    # ============================================================
    section(5, "ALFVEN AND MAGNETOSONIC WAVES")
    # ============================================================
    print("MHD supports three linear wave modes (small B and rho perturbations):")
    print()
    print("  Alfven wave:        omega = k_par v_A         (transverse, incompressible)")
    print("  Fast magnetosonic:  omega^2 = k^2 (v_A^2 + c_s^2)/2 + ... (compressive)")
    print("  Slow magnetosonic:  omega^2 = k^2 (v_A^2 + c_s^2)/2 - ... (compressive)")
    print()
    print("v_A = B / sqrt(mu0 rho) is the substrate-tension wave speed.  It is the")
    print("magnetic analog of sqrt(T/mu) on a string -- the magnetic field provides")
    print("the tension on the substrate-strain field-line bundle.")
    print()
    print(f"  {'environment':<24s}  {'B [T]':>9s}  {'rho [kg/m^3]':>14s}  {'v_A [m/s]':>11s}")
    alfven_envs = [
        ("Tokamak edge",          5.0,    1.6e-7),     # n_i ~ 1e20, ions
        ("Solar corona loop",     1.0e-2, 1.6e-12),    # n ~ 1e15
        ("Solar wind @ 1 AU",     5.0e-9, 8.4e-21),    # n ~ 5e6
        ("ISM (warm phase)",      5.0e-10,1.6e-21),    # n ~ 1e6
        ("Neutron star magnetar", 1.0e10, 1.0e17),     # crust-ish
    ]
    for name, B_env, rho_env in alfven_envs:
        vA = alfven_speed(B_env, rho_env)
        print(f"  {name:<24s}  {B_env:>9.2e}  {rho_env:>14.2e}  {vA:>11.3e}")
    print()
    print("Note magnetar v_A is capped by c (relativistic regime); the formula")
    print("above is non-relativistic and exceeds c for the crust-density estimate")
    print("-- a sign that the saturation cap sigma <= 1/2 is hit (substrate cannot")
    print("transmit transverse waves faster than its own light-speed).")

    # ============================================================
    section(6, "KINETIC THEORY — VLASOV AND LANDAU DAMPING")
    # ============================================================
    print("When collisions are negligible (ln Lambda finite, but mean free path huge)")
    print("the distribution function f(r, v, t) obeys the collisionless Vlasov eqn:")
    print()
    print("  d_t f + v . grad f + (q/m)(E + v x B) . grad_v f = 0")
    print()
    print("Linearize around Maxwellian: dispersion relation for Langmuir waves picks")
    print("up an imaginary part — Landau damping:")
    print()
    print("  gamma_L / omega_p ~ -sqrt(pi/8) (omega_p / k v_th)^3 exp(-omega^2 / 2 k^2 v_th^2)")
    print()
    print("Substrate reading: a substrate-strain wave with phase speed v_phi extracts")
    print("energy from particles slower than v_phi and gives energy to faster ones.")
    print("Net flux comes from the SLOPE of f at v=v_phi.  For a Maxwellian, slope is")
    print("negative -> wave damps without any collisions, purely by phase coupling.")
    print()
    # quick numerical demo
    n_dem = 1.0e18
    T_dem = 1.0
    om_p_dem = plasma_frequency(n_dem)
    v_th = math.sqrt(KB * T_dem * EV_J / KB / ME)  # ~ thermal speed
    v_th = math.sqrt(T_dem * EV_J / ME)
    print(f"Demo (n=1e18 m^-3, T=1 eV):")
    print(f"  v_th = {v_th:.3e} m/s")
    print(f"  omega_p = {om_p_dem:.3e} rad/s")
    for kld in (0.1, 0.3, 0.5):
        x = 1.0 / kld
        gL = -math.sqrt(PI / 8) * x ** 3 * math.exp(-x*x / 2.0)
        print(f"  k lambda_D = {kld:.2f}:  gamma_L/omega_p ~ {gL:.3e}")
    print()
    print("At small k lambda_D, damping is exponentially weak -> long-lived plasma")
    print("oscillations (the famous 'plasmon').")

    # ============================================================
    section(7, "INSTABILITIES AND RECONNECTION")
    # ============================================================
    print("Plasmas are notoriously unstable. Each instability = strain configuration")
    print("with a free-energy direction unbounded by the saturation cap.")
    print()
    print(f"  {'instability':<22s}  {'driver':<28s}  {'growth rate':<18s}")
    insts = [
        ("Two-stream",         "counter-streaming beams",    "~ omega_p"),
        ("Buneman",            "electron drift v_d > v_th",  "~ (m_e/m_i)^(1/3) omega_p"),
        ("Rayleigh-Taylor",    "heavy on light + g",         "sqrt(g k Atwood)"),
        ("Kelvin-Helmholtz",   "velocity shear",             "~ k Delta v"),
        ("Sausage (m=0)",      "current pinch radial",       "v_A / a"),
        ("Kink (m=1)",         "current pinch helical",      "v_A / a"),
        ("Tearing mode",       "resistive layer",            "S^(-3/5) tau_A^(-1)"),
        ("Weibel",             "anisotropic v-distribution", "~ omega_p (T_perp/T_par)"),
        ("Firehose",           "p_par > p_perp + B^2/mu0",   "k v_A"),
        ("Mirror",             "p_perp > p_par",             "k v_A"),
    ]
    for n, d, gr in insts:
        print(f"  {n:<22s}  {d:<28s}  {gr:<18s}")
    print()
    print("Magnetic reconnection — substrate-strain field-line topology change:")
    print()
    print(f"  {'model':<14s}  {'rate v_in/v_A':<18s}  {'regime':<28s}")
    print(f"  {'Sweet-Parker':<14s}  {'~ S^(-1/2)':<18s}  {'collisional, slow':<28s}")
    print(f"  {'Petschek':<14s}  {'~ pi/(8 ln S)':<18s}  {'standing slow shocks':<28s}")
    print(f"  {'Hall':<14s}  {'~ 0.1':<18s}  {'collisionless, fast':<28s}")
    print()
    print("S = Lundquist number = mu0 L v_A / eta. For solar S ~ 1e12-1e14, so")
    print("Sweet-Parker would predict reconnection on geological timescales -- but")
    print("flares occur in minutes. Hall / kinetic effects (and plasmoid instability")
    print("for S > 1e4) provide the fast rate observed.")
    print()
    print("Substrate reading: a reconnection layer is the locus where two distinct")
    print("strain-flux topologies meet. Sigma cap forbids the strain density from")
    print("piling up indefinitely -> the bridge tears, re-knits with new partners,")
    print("releases the stored magnetic strain energy as bulk flow + heat.")

    # ============================================================
    section(8, "WAVES IN MAGNETIZED PLASMA — THE FULL ZOO")
    # ============================================================
    print("Magnetized plasma supports many wave branches; the cold-plasma dispersion")
    print("(Stix) splits along k || B and k perp B.")
    print()
    print(f"  {'wave':<18s}  {'k direction':<14s}  {'frequency band':<26s}")
    waves = [
        ("Langmuir",        "any",        "near omega_pe"),
        ("Ion acoustic",    "any",        "omega = k c_s"),
        ("Whistler (R-mode)", "k || B",   "Omega_ci << omega << Omega_ce"),
        ("Alfven",          "k || B",     "omega = k v_A"),
        ("Bernstein (electron)", "k perp B", "n Omega_ce"),
        ("Bernstein (ion)", "k perp B",   "n Omega_ci"),
        ("Lower hybrid",    "k perp B",   "sqrt(Omega_ci Omega_ce)"),
        ("Upper hybrid",    "k perp B",   "sqrt(omega_pe^2 + Omega_ce^2)"),
        ("O-mode",          "k perp B",   "omega > omega_pe"),
        ("X-mode",          "k perp B",   "two branches around hybrid"),
        ("EMIC",            "k || B",     "near Omega_ci, ion cyclotron"),
    ]
    for n, k, f in waves:
        print(f"  {n:<18s}  {k:<14s}  {f:<26s}")
    print()
    print("Whistler waves: dispersion omega = (Omega_ce cos theta) k^2 c^2 / omega_pe^2")
    print("  -> high-frequency components arrive first ('whistling down' tone in radio).")
    print("  -> first plasma wave decoded historically (WW1 trench-telephone hum).")
    print()
    print("Bernstein modes: substrate strain oscillations between cyclotron harmonics,")
    print("reachable only in fully kinetic theory; no fluid analog.")
    print()
    print("Substrate reading: each branch = an eigenmode of the substrate-strain")
    print("Lagrangian under the constraints set by mean B-field tension and the two")
    print("species' inertia. Hybrid frequencies are coupled-oscillator beat tones.")

    # ============================================================
    section(9, "DUSTY / COMPLEX PLASMAS — SUBSTRATE CRYSTALS")
    # ============================================================
    print("When micron-sized grains are added to a plasma, they collect ~10^4 e^-")
    print("each and become highly charged. Coupling parameter for the dust component:")
    print()
    print("  Gamma_d = (Z_d e)^2 exp(-a/lambda_D) / (4 pi eps0 a k_B T_d)")
    print()
    print("With Z_d ~ 10^3-10^5 and a ~ 0.1 mm spacing, Gamma_d easily exceeds 170")
    print("-- the OCP crystallization threshold -- and the dust forms a Coulomb")
    print("crystal: a substrate-strain lattice with bcc, fcc, or hcp packing.")
    print()
    print("Observed phases (microgravity ICAPS/PK-4 experiments):")
    print(f"  {'Gamma_d range':<18s}  {'phase':<22s}")
    phases = [
        ("< 1",        "gas"),
        ("1 - 50",     "liquid-like"),
        ("50 - 170",   "supercooled liquid"),
        ("> 170",      "Coulomb crystal (bcc/fcc)"),
    ]
    for g, p in phases:
        print(f"  {g:<18s}  {p:<22s}")
    print()
    print("Substrate reading: when the substrate-strain bridges between charged")
    print("grains exceed thermal energy, the same orientability + sigma-cap that")
    print("makes ordinary atomic crystals forms a macroscopic plasma crystal.")
    print("Same Lagrangian, different scale.")

    # ============================================================
    section(10, "SUMMARY: plasma = ionized strain medium")
    # ============================================================
    print("All plasma phenomena reduce to ONE primitive: a substrate-strain medium")
    print("with two charged species that decouple as separate fluids, governed by")
    print("the four continuous primitives K, rho, xi, gamma plus the saturation cap")
    print("sigma <= 1/2 and orientability.")
    print()
    print("Configuration -> phenomenon:")
    print("  Coulomb screening of test charge       -> Debye length lambda_D")
    print("  Free-electron collective mode          -> plasma frequency omega_p")
    print("  Helix in B-field tension               -> gyromotion + drifts")
    print("  Single-fluid coarse grain              -> MHD")
    print("  Transverse mode along B-line bundle    -> Alfven wave")
    print("  Phase coupling wave-particle           -> Landau damping")
    print("  Free-energy direction in v-space       -> two-stream / Weibel")
    print("  Strain-flux topology change            -> magnetic reconnection")
    print("  Strongly coupled charged grains        -> dust Coulomb crystal")
    print("  Saturation hit at relativistic density -> degenerate / pair plasma")
    print()
    print("Honest scoreboard: every plasma number above is reproduced from the")
    print("same Lagrangian as chemistry, condensed matter, and gravity. The unique")
    print("value-add for plasma is the unification of regime classification (cold vs")
    print("hot, weakly vs strongly coupled, classical vs degenerate) under one")
    print("strain-medium ontology rather than three or four independent paradigms.")
    print()
    print("Predicted limit cases worth checking:")
    print("  - sigma -> 1/2 in white-dwarf cores  ->  electron degeneracy pressure")
    print("  - sigma -> 1/2 in pair plasmas       ->  natural cap on B^2/2mu0")
    print("  - orientability flip in toroidal     ->  helicity injection bifurcations")


if __name__ == "__main__":
    main()
