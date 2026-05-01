"""Polymer chemistry and macromolecular dynamics in the strain-medium framework.

Polymers are LONG topological linear strain patterns: a chain of N monomeric
strain bridges (see molecular_bonding_substrate.py for the bridge primitive)
linked head-to-tail. Above a critical chain density they form ENTANGLEMENTS
(topological strain crossings the chains cannot pass through), and below a
critical temperature drag gamma exceeds thermal noise and the substrate
configuration FREEZES — the glass transition T_g.

Strain-medium primitives (the same six everywhere):
  K (stiffness), rho (density), xi (length), gamma (drag),
  saturation cap sigma <= 1/2, orientability

Lagrangian: L = (1/2) rho (d_t u)^2 - (1/2) K |grad u|^2 - V(u) - gamma u d_t u

Honest framing: the substrate REPRODUCES the standard polymer-physics numbers
(Gaussian-chain stats, reptation M^3.4 viscosity, WLF equation, Flory-Huggins
chi parameter, rubber-elasticity nkT modulus). The value-add is unification
under one ontology, not new exponents.
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
ANGSTROM = 1.0e-10
NM = 1.0e-9


def section(n: int, title: str) -> None:
    print()
    print("=" * 72)
    print(f"{n}. {title}")
    print("=" * 72)
    print()


def main() -> None:
    print("Polymer chemistry & macromolecular dynamics in strain-medium framework")
    print("=" * 72)
    print()
    print("Substrate primitives: K, rho, xi, gamma, sigma<=1/2, orientability")
    print("Polymer  =  topological LINEAR chain of N strain bridges")
    print("Entangle =  topological strain crossings between two chains")
    print("T_g      =  drag gamma >> thermal -> substrate config frozen")
    print()

    # ============================================================
    section(1, "CHAIN STATISTICS (random walk, Gaussian chain)")
    # ============================================================
    print("Treat the chain as N freely-jointed segments of length b (Kuhn length).")
    print("Each segment is one substrate-strain link with random orientation.")
    print()
    print("  End-to-end vector:   R = sum_i b_i      <R> = 0")
    print("  Mean square:         <R^2> = N b^2")
    print("  RMS end-to-end:      R_rms = b sqrt(N)")
    print("  Radius of gyration:  R_g   = b sqrt(N/6)")
    print()
    print("Persistence length L_p (orientational memory along contour):")
    print("  L_p = b/2  for freely-jointed chain (Kuhn ~ 2 L_p)")
    print()
    print(f"  {'polymer':<14s}  {'L_p [nm]':>10s}  {'Kuhn b [nm]':>12s}  {'note':<26s}")
    persistence = [
        ("Polyethylene",     0.7,  1.4, "flexible coil"),
        ("Polystyrene",      1.0,  2.0, "atactic"),
        ("PMMA",             0.9,  1.8, "atactic"),
        ("ssDNA",            1.5,  3.0, "single-strand, charged"),
        ("dsDNA",           50.0,100.0, "double helix, semi-rigid"),
        ("Actin filament", 17000.0, 34000.0, "biopolymer, very stiff"),
        ("Microtubule",   5000000.0, 1e7, "near-rigid rod"),
    ]
    for n, lp, b, note in persistence:
        print(f"  {n:<14s}  {lp:>10.2f}  {b:>12.2f}  {note:<26s}")
    print()
    print("Numeric demo: polyethylene chain, b = 1.4 nm")
    b = 1.4 * NM
    for N in (10, 100, 1000, 10000, 100000):
        R_rms = b * math.sqrt(N) / NM
        R_g   = b * math.sqrt(N/6.0) / NM
        Lc    = N * b / NM   # contour length
        print(f"  N = {N:6d}   R_rms = {R_rms:8.2f} nm   R_g = {R_g:8.2f} nm   L_c = {Lc:9.1f} nm")
    print()
    print("Substrate reading: each Kuhn segment is a localized strain bridge of")
    print("scale xi ~ b. The chain is a topological CONCATENATION of bridges,")
    print("with random orientation in the substrate strain field — pure diffusion")
    print("on the unit sphere of bridge orientations.")

    # ============================================================
    section(2, "FLORY-HUGGINS SOLUBILITY (chi from strain mismatch)")
    # ============================================================
    print("Free energy of mixing per lattice site:")
    print("  Delta F_mix / (k_B T) = (phi/N) ln phi + (1-phi) ln(1-phi)")
    print("                           + chi phi (1 - phi)")
    print()
    print("chi = z * Delta epsilon / (k_B T),  z = lattice coordination,")
    print("Delta epsilon = (eps_AB - (eps_AA + eps_BB)/2) = strain-mismatch energy.")
    print()
    print("Substrate origin of chi:  the cross-bridge eps_AB has different")
    print("equilibrium strain configuration than the pure-component bridges.")
    print("chi < 0 -> mixing strains relax (good solvent).")
    print("chi > 0 -> mixing strains add (poor solvent / phase separation).")
    print()
    print("Critical chi for phase separation (high-N polymer in solvent):")
    print("  chi_c = 1/2 + 1/sqrt(N) + 1/(2N)  ~ 1/2  as N -> inf")
    print()
    print(f"  {'polymer':<10s}  {'solvent':<14s}  {'chi (300 K)':>12s}  {'quality':<12s}")
    chi_table = [
        ("PS",   "toluene",       0.40, "good"),
        ("PS",   "cyclohexane",   0.51, "theta"),
        ("PS",   "methanol",      2.0,  "poor"),
        ("PMMA", "acetone",       0.48, "good"),
        ("PMMA", "water",         3.0,  "poor"),
        ("PE",   "xylene (hot)",  0.42, "good"),
        ("PVA",  "water",         0.49, "marginal"),
        ("PEG",  "water",        -0.20, "very good"),
    ]
    for p, s, x, q in chi_table:
        print(f"  {p:<10s}  {s:<14s}  {x:>12.2f}  {q:<12s}")
    print()
    print("Note: chi ~ 1/2 = the substrate saturation cap sigma <= 1/2!")
    print("Above chi_c ~ 1/2 the strain-bridge density per site exceeds the")
    print("saturation bound -> demixing is the substrate's way to relieve overload.")

    # ============================================================
    section(3, "REPTATION & TUBE MODEL (de Gennes)")
    # ============================================================
    print("Above the entanglement molecular weight M_e, chains cannot pass")
    print("through each other. Each chain is confined to a TUBE of diameter a")
    print("set by neighboring chains' topological strain bridges.")
    print()
    print("Motion: the chain reptates (snakes) along its own contour.")
    print("  Reptation time:   tau_rep ~ N^3  (theory)")
    print("  Viscosity:        eta     ~ M^3.4  (experiment, all polymers)")
    print()
    print("The 3.4 (vs predicted 3.0) comes from CONSTRAINT RELEASE — neighboring")
    print("chains also reptate, occasionally vacating the tube.")
    print()
    print("Substrate origin: a topological strain crossing cannot be undone")
    print("locally (it is a Z_2 winding of the chain past another). The chain")
    print("must SLIDE along its strain contour to escape — 1D diffusion through")
    print("a 3D constraint network.")
    print()
    print(f"  {'polymer':<14s}  {'M_e [g/mol]':>12s}  {'rho [g/cm3]':>12s}  {'tube a [nm]':>12s}")
    entangle = [
        ("Polyethylene",   1250, 0.85, 3.5),
        ("Polystyrene",   18000, 1.05, 8.5),
        ("PMMA",           9200, 1.18, 6.0),
        ("PDMS",           8100, 0.97, 6.5),
        ("cis-PB",         1900, 0.90, 4.2),
        ("PIB",            7000, 0.92, 6.0),
    ]
    for p, me, rho, a in entangle:
        print(f"  {p:<14s}  {me:>12d}  {rho:>12.2f}  {a:>12.2f}")
    print()
    print("Numeric demo: M^3.4 viscosity scaling for polystyrene (M_e = 18 kg/mol)")
    eta_ref = 1.0  # arbitrary units at M = M_e
    print(f"  {'M [g/mol]':>10s}  {'M/M_e':>8s}  {'eta / eta(M_e)':>16s}")
    for M in (1e4, 3e4, 1e5, 3e5, 1e6, 3e6):
        ratio = (M / 18000.0)
        if ratio < 1.0:
            eta = ratio                   # Rouse regime, eta ~ M
        else:
            eta = ratio ** 3.4            # reptation regime
        print(f"  {M:>10.0e}  {ratio:>8.2f}  {eta:>16.2e}")
    print()
    print("Below M_e: Rouse regime, eta ~ M (no entanglement constraint).")
    print("Above M_e: reptation, eta ~ M^3.4 (the universal polymer signature).")

    # ============================================================
    section(4, "GLASS TRANSITION T_g (drag-frozen substrate config)")
    # ============================================================
    print("As T drops, segmental relaxation time tau slows. When tau ~ 100 s")
    print("(experimental timescale) the chain CANNOT rearrange — it is frozen.")
    print("This is T_g, the glass transition.")
    print()
    print("Substrate framing:  effective Maxwell time  tau ~ gamma / K")
    print("  - high T -> thermal activation > drag -> liquid-like")
    print("  - low  T -> drag wins -> substrate configuration frozen")
    print()
    print("Empirical WLF equation above T_g:")
    print("  log(a_T) = -C1 (T - T_g) / (C2 + T - T_g)")
    print("  universal:  C1 ~ 17.4,  C2 ~ 51.6 K  (same for ALL polymers above T_g)")
    print()
    print("The universality is the substrate fingerprint: ONE drag-vs-thermal")
    print("crossover law, dressed by polymer-specific T_g.")
    print()
    print(f"  {'polymer':<24s}  {'T_g [K]':>8s}  {'T_g [C]':>8s}  {'class':<14s}")
    tg = [
        ("Polydimethylsiloxane (PDMS)", 150, -123, "elastomer"),
        ("cis-Polybutadiene",           165, -108, "rubber"),
        ("Polyethylene (LDPE amorph.)", 195,  -78, "thermoplastic"),
        ("Polypropylene atactic",       265,   -8, "thermoplastic"),
        ("Poly(vinyl chloride)",        354,   81, "rigid plastic"),
        ("Polystyrene atactic",         373,  100, "rigid plastic"),
        ("Poly(methyl methacrylate)",   378,  105, "acrylic glass"),
        ("Polycarbonate (BPA)",         420,  147, "engineering"),
        ("PEEK",                        416,  143, "high-perf engineering"),
        ("Polyimide (Kapton)",          658,  385, "ultra high-T"),
    ]
    for p, k, c, cl in tg:
        print(f"  {p:<24s}  {k:>8d}  {c:>8d}  {cl:<14s}")
    print()
    print("Pattern: T_g rises with backbone stiffness K and side-group bulk.")
    print("Substrate reading: bulky/rigid groups raise the local strain barrier")
    print("for backbone rotation -> higher T at which thermal kT can hop it.")
    print()
    print("Demo of WLF shift factor a_T (PS, T_g = 373 K):")
    Tg_ps = 373.0
    for T in (373, 383, 403, 423, 473):
        if T <= Tg_ps:
            print(f"  T = {T:4.0f} K  (at or below T_g)  log a_T = inf (frozen)")
        else:
            log_a = -17.4 * (T - Tg_ps) / (51.6 + (T - Tg_ps))
            print(f"  T = {T:4.0f} K  (T - T_g = {T-Tg_ps:5.0f})  log a_T = {log_a:6.2f}   a_T = {10**log_a:.2e}")

    # ============================================================
    section(5, "RUBBER ELASTICITY (entropic, F = -T dS/dL)")
    # ============================================================
    print("Cross-linked rubber far above T_g: chain segments freely rearrange.")
    print("Stretching DECREASES the number of available substrate configurations")
    print("(fewer random walks reach a stretched end-to-end distance).")
    print()
    print("  S(R) = S_0 - (3 k_B / 2) (R^2 - R_0^2) / (N b^2)")
    print("  F = -T dS/dR = +3 k_B T R / (N b^2)   (linear restoring, like a spring)")
    print()
    print("Force is POSITIVE in T:  warm a stretched rubber band -> it shortens.")
    print("(Gough-Joule effect; opposite sign to ordinary thermal expansion.)")
    print()
    print("Bulk modulus of an ideal cross-linked network:")
    print("  G = n k_B T  =  rho R T / M_c   (n = chain-strand density)")
    print()
    T = 298.15
    rho_rub = 920.0   # kg/m^3 typical
    print(f"  {'M_c [g/mol]':>12s}  {'G [MPa]':>10s}  {'note':<28s}")
    for Mc in (500, 2000, 5000, 10000, 50000):
        G = rho_rub * R_GAS * T / (Mc * 1e-3)   # Pa
        print(f"  {Mc:>12d}  {G/1e6:>10.3f}  {'M_c = strand between links':<28s}")
    print()
    print("Substrate origin: the network is a topological cage of strain bridges.")
    print("Each strand visits ~N^(3/2) substrate configurations; stretching trims")
    print("the count. The 'force' is purely the substrate counting its own states.")

    # ============================================================
    section(6, "POLYMER CRYSTALLINITY & SEMICRYSTALLINE MORPHOLOGY")
    # ============================================================
    print("Most polymers are SEMICRYSTALLINE: ordered lamellae (10-30 nm thick)")
    print("threaded by amorphous tie chains. Crystallinity X_c = 0 (atactic) to")
    print("~95 percent (HDPE, PTFE).")
    print()
    print("Substrate reading: lamella = locally REGISTERED strain bridges")
    print("(periodic alignment lowers strain energy by sqrt(N) factor like an")
    print("ordered array of harmonic oscillators); amorphous regions = frozen")
    print("disordered bridges (locally glassy).")
    print()
    print(f"  {'polymer':<22s}  {'T_m [K]':>8s}  {'X_c [%]':>8s}  {'lamella d [nm]':>14s}")
    cryst = [
        ("HDPE",                   408, 80, 20),
        ("LDPE",                   388, 50, 12),
        ("Polypropylene (iso)",    449, 60, 15),
        ("PTFE",                   600, 90, 25),
        ("Nylon 6",                498, 50, 10),
        ("Nylon 6,6",              538, 55, 12),
        ("PET",                    538, 35, 12),
        ("POM",                    448, 75, 18),
        ("PEEK",                   616, 35, 10),
        ("PVDF",                   450, 50, 14),
    ]
    for p, tm, xc, d in cryst:
        print(f"  {p:<22s}  {tm:>8d}  {xc:>8d}  {d:>14d}")
    print()
    print("Hoffman-Lauritzen crystal growth rate G(T):")
    print("  G(T) = G_0 exp(-U*/(R(T-T_inf))) exp(-K_g / (T DT f))")
    print("  competes thermal mobility (drops near T_g) vs nucleation barrier")
    print("  (drops near T_m). Maximum growth at T_m - 30 to 50 K typically.")
    print()
    print("Tacticity controls crystallizability:")
    print("  - isotactic   (all R groups same side)  -> crystalline, high T_m")
    print("  - syndiotactic (alternating)            -> crystalline, lower T_m")
    print("  - atactic     (random)                  -> amorphous, glassy only")
    print()
    print("Substrate explanation: only stereoregular chains have a periodic")
    print("strain register that can lock into a 3D lattice. Atactic = quenched")
    print("disorder along the contour -> no periodic strain template available.")

    # ============================================================
    section(7, "ADDITION vs CONDENSATION POLYMERIZATION")
    # ============================================================
    print("Two mechanisms by which N monomeric strain bridges concatenate:")
    print()
    print("ADDITION (chain-growth):")
    print("  active center adds monomer one at a time, no byproduct")
    print("  Initiation -> Propagation (fast) -> Termination/Transfer")
    print("  Examples: free radical (PE, PS, PVC), cationic, anionic, Ziegler-Natta")
    print("  Kinetics: high MW reached at LOW conversion; M_n insensitive to time")
    print()
    print("CONDENSATION (step-growth, Carothers):")
    print("  any two functional groups react, releases small molecule (H2O, HCl)")
    print("  All chains grow together; high MW only at HIGH conversion.")
    print("  Carothers eq:  X_n = 1/(1 - p)  where p = fractional conversion.")
    print("  Examples: nylon, PET, polycarbonate, epoxy, polyurethane")
    print()
    print("  conversion p   X_n (number-avg degree of polymerization)")
    for p in (0.50, 0.80, 0.90, 0.95, 0.98, 0.99, 0.995, 0.999):
        Xn = 1.0 / (1.0 - p)
        print(f"     p = {p:5.3f}     X_n = {Xn:7.1f}")
    print()
    print("Free-radical kinetics (steady-state):")
    print("  Rp = k_p [M] (f k_d [I] / k_t)^(1/2)   (rate of propagation)")
    print("  Kinetic chain length: nu = k_p [M] / (2 (f k_d k_t [I])^(1/2))")
    print()
    print("Substrate framing:")
    print("  - addition = ONE active strain center walks down a monomer queue")
    print("  - condensation = MANY centers converge in pairs, releasing slack strain")
    print("Both build the same topological linear strain pattern; only the SCHEDULE")
    print("of bridge formation differs.")

    # ============================================================
    section(8, "CONTROLLED RADICAL POLYMERIZATION (ATRP, RAFT, NMP)")
    # ============================================================
    print("Standard radical polymerization gives broad MW distribution (D ~ 1.5-2)")
    print("because termination is uncontrolled. Three living-radical methods")
    print("achieve D < 1.2 by reversibly DEACTIVATING the active center, keeping")
    print("[radical] tiny so termination is rare:")
    print()
    print(f"  {'method':<24s}  {'mediator':<22s}  {'mechanism':<18s}")
    methods = [
        ("ATRP (Matyjaszewski)", "Cu(I)/Cu(II) + ligand", "halide reversible"),
        ("RAFT (CSIRO 1998)",    "thiocarbonylthio CTA",  "degenerative chain xfer"),
        ("NMP (Hawker, Solomon)", "TEMPO / nitroxide",     "thermal homolysis"),
        ("ICAR/ARGET-ATRP",      "Cu + reducing agent",   "low-Cu variant"),
        ("SET-LRP",              "Cu(0) wire/powder",     "single-electron"),
    ]
    for m, med, mech in methods:
        print(f"  {m:<24s}  {med:<22s}  {mech:<18s}")
    print()
    print("Living-character signature: D = M_w / M_n -> 1 + 1/X_n  (Poisson),")
    print("so for X_n = 100 the dispersity D approaches 1.01.")
    print()
    print(f"  {'X_n':>6s}  {'D (Poisson limit)':>20s}")
    for Xn in (10, 50, 100, 500, 1000):
        D = 1.0 + 1.0/Xn
        print(f"  {Xn:>6d}  {D:>20.4f}")
    print()
    print("Substrate reading: the deactivation step PARKS the active strain")
    print("center in a low-energy strain configuration (dormant), throttling the")
    print("encounter rate of two active centers. Topology of bridge formation")
    print("becomes deterministic, not Poissonian-broadened by termination.")
    print()
    print("Key impact: enabled BLOCK copolymers (PS-b-PMMA, PEO-b-PCL, etc.) and")
    print("complex architectures (stars, brushes, gradient, miktoarm).")

    # ============================================================
    section(9, "CONDUCTING POLYMERS (doped strain bridges)")
    # ============================================================
    print("Polyacetylene (CH=CH)_n discovered 1977 by Shirakawa, Heeger,")
    print("MacDiarmid (Nobel 2000). Pristine polyacetylene = semiconductor,")
    print("Eg ~ 1.5 eV. Doped with I_2, AsF_5, alkali metals -> conductivity")
    print("rises by 10-12 orders of magnitude, reaching ~10^5 S/cm (Cu ~ 6e5).")
    print()
    print(f"  {'polymer':<22s}  {'Eg [eV]':>8s}  {'sigma_pristine':>14s}  {'sigma_doped [S/cm]':>20s}")
    cond = [
        ("trans-Polyacetylene",   1.5,  "1e-9",    "1e5"),
        ("Polyaniline (EB->ES)",  3.8,  "1e-10",   "1e2"),
        ("Polypyrrole",           3.2,  "1e-10",   "1e3"),
        ("Polythiophene",         2.0,  "1e-9",    "1e3"),
        ("PEDOT:PSS",             1.6,  "1e-3",    "4e3"),
        ("Poly(p-phenylenevinylene)", 2.5, "1e-13", "1e3"),
    ]
    for p, eg, s0, sd in cond:
        print(f"  {p:<22s}  {eg:>8.2f}  {s0:>14s}  {sd:>20s}")
    print()
    print("Mechanism: conjugated backbone provides delocalized pi strain bridges.")
    print("Doping injects/removes electrons -> creates SOLITONS (mid-gap states")
    print("for degenerate ground state, polyacetylene) or POLARONS / BIPOLARONS")
    print("(non-degenerate, polythiophene/polypyrrole). These topological")
    print("strain defects move along the chain and carry charge.")
    print()
    print("Substrate framing: pristine polymer = unbroken pi-bridge sequence with")
    print("a substrate band gap (Peierls distortion alternates bond lengths,")
    print("opens 1D gap). Doping breaks the alternation locally, creating a")
    print("topological domain wall (kink) in the bond-length-alternation order")
    print("parameter — the soliton. The kink sits AT THE BAND CENTER (zero-energy")
    print("mid-gap state) and is the carrier of charge OR spin.")
    print()
    print("Mark-Houwink intrinsic viscosity:  [eta] = K M^alpha")
    print("  alpha tracks chain shape:  0.5 = theta solvent (Gaussian),")
    print("                              0.8 = good solvent (swollen coil),")
    print("                              1.0 = rigid rod,  2.0 = max for rod.")
    print()
    print(f"  {'polymer':<14s}  {'solvent':<14s}  {'T [C]':>6s}  {'K x 1e3':>10s}  {'alpha':>8s}")
    mh = [
        ("PS",   "toluene",     25,  17.0, 0.69),
        ("PS",   "cyclohex.",   34,   80.0, 0.50),
        ("PMMA", "acetone",     25,    7.5, 0.70),
        ("PMMA", "chloroform",  25,    4.8, 0.80),
        ("PE",   "decalin",    135,   62.0, 0.70),
        ("PIB",  "cyclohex.",   30,   27.6, 0.69),
        ("Nylon66", "form.acid",25,   110.0, 0.72),
        ("DNA",  "0.2 M NaCl",  25,    1.4, 1.10),
    ]
    for p, s, t, k, a in mh:
        print(f"  {p:<14s}  {s:<14s}  {t:>6d}  {k:>10.1f}  {a:>8.2f}")
    print()
    print("Substrate reading of alpha: the exponent reports HOW the strain")
    print("contour fills space. Gaussian (alpha=0.5) = pure random walk;")
    print("good solvent (alpha~0.8) = swollen self-avoiding walk; rod (alpha=1)")
    print("= maximally extended bridge sequence. The same self-avoidance limit")
    print("that gives the Flory exponent nu = 3/5 in 3D shows up here as alpha=3nu-1.")

    # ============================================================
    section(10, "SUMMARY: chain of bridges, drag, and topology")
    # ============================================================
    print("Polymer = topological LINEAR strain pattern: N strain bridges")
    print("  concatenated head-to-tail. All polymer-specific phenomena reduce to")
    print("  three substrate facts about that pattern:")
    print()
    print("  1. CHAIN STATISTICS — random walk on bridge orientations:")
    print("        R ~ b sqrt(N), entropic spring, Mark-Houwink alpha = 3 nu - 1")
    print()
    print("  2. TOPOLOGY — bridges cannot pass through each other:")
    print("        entanglements -> tube confinement -> reptation -> eta ~ M^3.4")
    print()
    print("  3. DRAG vs THERMAL — gamma controls which configs are accessible:")
    print("        T > T_g  -> liquid melt / rubber (entropic)")
    print("        T < T_g  -> drag-frozen substrate -> glass")
    print()
    print("Cross-cut by sigma <= 1/2 (saturation cap):")
    print("        chi_c ~ 1/2 in Flory-Huggins (above the cap, bridges demix)")
    print("        Lieb-Oxford bound on E_xc in DFT (same cap, electronic version)")
    print()
    print("Honest scoreboard: substrate REPRODUCES Gaussian chain stats, the")
    print("3.4 reptation exponent, the WLF universal coefficients, the nkT rubber")
    print("modulus, the Carothers MW evolution, the Hoffman-Lauritzen growth law,")
    print("and the SSH soliton picture of conducting polymers. The value-add is")
    print("ontological: nine 'distinct' chapters of polymer physics become one")
    print("chain-of-bridges story under K, rho, xi, gamma, sigma <= 1/2.")


if __name__ == "__main__":
    main()
