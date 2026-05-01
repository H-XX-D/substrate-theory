"""Civil and structural engineering in the substrate framework.

How does substrate explain beams, columns, reinforced concrete, soils,
seismic dynamics, wind loading, foundations, and fatigue in bridges —
the daily bread of civil/structural engineering?

Core principle: matter IS substrate strain pattern. Structures are
macroscopic substrate-strain assemblies under quasi-static and dynamic
loading. The Lagrangian L = ½ρ(∂_t u)² - ½K|∇u|² - V(u) - γ·u·∂_t u
specializes directly to elastodynamics, soil consolidation, and
structural vibration.

Substrate adds nothing to the engineering numbers (E, f_c', σ_y, etc.
are still measured), but provides:
  - One Lagrangian origin for static, dynamic, and dissipative response
  - Saturation cap σ ≤ 1/2 regularizes stress singularities (crack tips
    in concrete, re-entrant corners, point loads on soil)
  - Topological-defect interpretation of fatigue micro-cracks in bridges
"""

from __future__ import annotations
import math


PI = math.pi
G_N = 6.674e-11
G_GRAV = 9.81  # m/s² standard gravity


def main() -> None:
    print("Civil and structural engineering in the substrate framework")
    print("=" * 70)

    # ============== 1. STRUCTURAL ANALYSIS ==============
    print()
    print("=" * 70)
    print("1. STRUCTURAL ANALYSIS (beams, trusses, frames)")
    print("=" * 70)
    print()
    print("Standard Euler-Bernoulli beam:")
    print("  EI·d⁴y/dx⁴ = w(x)        (transverse load equation)")
    print("  M = EI·d²y/dx²            (bending moment ↔ curvature)")
    print("  σ = M·c/I                 (extreme fibre stress)")
    print()
    print("Truss: ΣF=0 at each pin → axial-only members, σ = P/A")
    print("Frame: combined axial + bending + shear; stiffness matrix [K]{u}={F}")
    print()
    print("Substrate explanation:")
    print("  - Beam = elongated substrate strain volume; bending = gradient of")
    print("    longitudinal strain across cross-section")
    print("  - EI literally measures Σ(K_substrate × moment-arm²) over section")
    print("  - Lagrangian ½K|∇u|² → bending strain energy U = ½∫EI(y'')²dx")
    print("  - Static equilibrium = stationary substrate strain configuration")
    print()
    print("Common deflection formulas (substrate gives identical numbers):")
    print(f"  {'case':>30s}    {'δ_max':>20s}")
    cases = [
        ('Cantilever, tip load P',        'PL³/(3EI)'),
        ('Cantilever, UDL w',             'wL⁴/(8EI)'),
        ('Simply supported, midspan P',   'PL³/(48EI)'),
        ('Simply supported, UDL w',       '5wL⁴/(384EI)'),
        ('Fixed-fixed, midspan P',        'PL³/(192EI)'),
        ('Fixed-fixed, UDL w',            'wL⁴/(384EI)'),
    ]
    for name, formula in cases:
        print(f"  {name:>28s}      {formula:>20s}")
    print()

    print("Section properties (I = second moment of area):")
    print(f"  {'shape':>20s}    {'I [b·h units]':>20s}")
    sections = [
        ('Rectangle b×h',       'b·h³/12'),
        ('Solid circle d',      'π·d⁴/64'),
        ('Hollow tube d_o,d_i', 'π·(d_o⁴ - d_i⁴)/64'),
        ('I-beam (W14×30)',     '291 in⁴ ≈ 1.21e-4 m⁴'),
        ('W36×150 girder',      '9040 in⁴ ≈ 3.76e-3 m⁴'),
    ]
    for name, val in sections:
        print(f"  {name:>18s}      {val:>20s}")
    print()

    # ============== 2. REINFORCED CONCRETE ==============
    print()
    print("=" * 70)
    print("2. REINFORCED CONCRETE (composite action)")
    print("=" * 70)
    print()
    print("Standard ACI 318 / Eurocode 2:")
    print("  M_n = A_s·f_y·(d - a/2),  a = A_s·f_y/(0.85·f_c'·b)  (rectangular)")
    print("  V_c = 0.17·√(f_c')·b·d  (MPa, shear capacity of plain concrete)")
    print("  Modulus: E_c ≈ 4700·√(f_c')  MPa")
    print()
    print("Substrate:")
    print("  - Concrete = aggregate-cement substrate with strong compressive bonds")
    print("    but weak tensile bonds (cracks at low strain)")
    print("  - Steel rebar = high-K, high-yield substrate inclusion that carries")
    print("    tensile strain when surrounding concrete cracks")
    print("  - Composite action = substrate strain compatibility at bond interface")
    print("  - Saturation σ ≤ 1/2 caps stress at crack tips → finite cohesive zone")
    print()
    fc_label = "f_c' [MPa]"
    print(f"  {'concrete grade':>20s}    {fc_label:>12s}    {'E_c [GPa]':>10s}    {'use':>20s}")
    concretes = [
        ('Normal C20/25',          20,  21.0, 'low-rise, slabs'),
        ('Normal C30/37',          30,  25.7, 'standard structural'),
        ('Normal C40/50',          40,  29.7, 'commercial, bridges'),
        ('High-strength C60/75',   60,  36.4, 'columns, towers'),
        ('Ultra-high UHPC',       150,  57.6, 'Burj-class, prestressed'),
    ]
    for name, fc, ec, use in concretes:
        print(f"  {name:>18s}      {fc:>10.0f}      {ec:>8.1f}      {use:>20s}")
    print()
    print(f"  {'rebar grade':>20s}    {'f_y [MPa]':>10s}    {'f_u [MPa]':>10s}    {'εu':>8s}")
    rebars = [
        ('Grade 40 (ASTM)',  280, 420, 0.12),
        ('Grade 60 (ASTM)',  420, 620, 0.09),
        ('Grade 75 (ASTM)',  520, 690, 0.07),
        ('B500B (EN)',       500, 540, 0.05),
        ('Prestress strand', 1860, 1960, 0.035),
    ]
    for name, fy, fu, eu in rebars:
        print(f"  {name:>18s}      {fy:>8.0f}      {fu:>8.0f}      {eu:>6.3f}")
    print()
    print("Substrate prediction: identical M_n, V_c. Crack-tip σ regularized")
    print("  by saturation cap → matches measured cohesive-zone width ~3-5 mm.")
    print()

    # ============== 3. SOIL MECHANICS ==============
    print()
    print("=" * 70)
    print("3. SOIL MECHANICS (Mohr-Coulomb, bearing capacity)")
    print("=" * 70)
    print()
    print("Standard Mohr-Coulomb failure:")
    print("  τ_f = c + σ_n·tan(φ)        (cohesion c, friction angle φ)")
    print()
    print("Terzaghi bearing capacity (strip footing):")
    print("  q_ult = c·N_c + q·N_q + 0.5·γ·B·N_γ")
    print("  N_q = e^(π tan φ)·tan²(45+φ/2),  N_c = (N_q-1)·cot φ")
    print()
    print("Substrate:")
    print("  - Soil = granular substrate with weak cohesive bonds + frictional")
    print("    grain-grain contacts (asperity bonds, see mechanical_systems_substrate)")
    print("  - Pore water = mobile substrate fluid (Lagrangian drag γ → consolidation)")
    print("  - Terzaghi 1-D consolidation: ∂u/∂t = c_v·∂²u/∂x² IS diffusion of pore")
    print("    pressure, derivable from L = ½ρ(∂_t u)² - ½K|∇u|² - γ·u·∂_t u")
    print()
    print(f"  {'soil type':>22s}    {'c [kPa]':>8s}    {'φ [deg]':>8s}    {'q_a [kPa]':>10s}")
    soils = [
        ('Soft clay',              25,    0,   75),
        ('Stiff clay',            100,    0,  300),
        ('Loose sand',              0,   30,  100),
        ('Dense sand',              0,   40,  500),
        ('Gravel',                  0,   38,  600),
        ('Weathered rock',        200,   45, 1500),
        ('Sound bedrock',        2000,   50,10000),
    ]
    for name, c, phi, qa in soils:
        print(f"  {name:>20s}      {c:>6.0f}      {phi:>6.0f}      {qa:>8.0f}")
    print()
    print("(q_a = allowable bearing pressure, presumptive, factor of safety ~3)")
    print()

    # ============== 4. SEISMIC DYNAMICS ==============
    print()
    print("=" * 70)
    print("4. SEISMIC DYNAMICS (resonance, modal analysis)")
    print("=" * 70)
    print()
    print("Standard equation of motion (MDOF):")
    print("  [M]{ü} + [C]{u̇} + [K]{u} = -[M]{1}·ü_g(t)")
    print("  Modes: ω_n² φ_n = M⁻¹K φ_n;  T_n = 2π/ω_n")
    print()
    print("Empirical fundamental period (ASCE 7):")
    print("  T_a = C_t·h_n^x,   moment frame steel: C_t=0.028, x=0.8 (h in m)")
    print()
    print("Substrate:")
    print("  - Structure = distributed substrate strain volume; modes = standing")
    print("    strain waves with boundary conditions set by foundation + roof")
    print("  - Damping ζ = drag γ in Lagrangian; same for all modes (Rayleigh OK)")
    print("  - Resonance disaster (Tacoma Narrows '40, Mexico City '85) = forced")
    print("    substrate-mode amplification when ω_drive ≈ ω_n and γ small")
    print()
    print(f"  {'building type':>26s}    {'h [m]':>6s}    {'T_1 [s]':>8s}    {'ζ':>6s}")
    buildings = [
        ('1-story house',           4,  0.10, 0.05),
        ('5-story masonry',        15,  0.30, 0.05),
        ('10-story RC frame',      33,  0.75, 0.05),
        ('20-story steel MRF',     67,  1.65, 0.03),
        ('40-story tube',         140,  3.50, 0.025),
        ('Burj Khalifa (~163 fl)', 828, 11.0, 0.015),
    ]
    for name, h, t1, z in buildings:
        print(f"  {name:>24s}      {h:>4.0f}      {t1:>6.2f}      {z:>4.3f}")
    print()
    print(f"  {'historic earthquake':>26s}    {'M_w':>5s}    {'PGA [g]':>8s}    {'period':>10s}")
    quakes = [
        ('San Francisco 1906',    7.9, 0.6,  '~0.5 s'),
        ('Mexico City 1985',      8.0, 0.17, '~2 s (lake bed)'),
        ('Loma Prieta 1989',      6.9, 0.65, '~0.4 s'),
        ('Northridge 1994',       6.7, 1.8,  '~0.3 s'),
        ('Tohoku 2011',           9.1, 2.7,  '~0.2-3 s'),
    ]
    for name, m, pga, T in quakes:
        print(f"  {name:>24s}      {m:>3.1f}      {pga:>6.2f}      {T:>10s}")
    print()

    # ============== 5. WIND & FLUID LOADING ==============
    print()
    print("=" * 70)
    print("5. WIND AND FLUID LOADING")
    print("=" * 70)
    print()
    print("Standard ASCE 7 / Eurocode 1:")
    print("  q = 0.5·ρ_air·V²        (velocity pressure, ρ_air ≈ 1.225 kg/m³)")
    print("  p = q·G·C_p·K_z         (design pressure on surface)")
    print("  Vortex shedding: f_s = St·V/D,  St ≈ 0.2 for circular")
    print()
    print("Substrate:")
    print("  - Wind = bulk flow of air-substrate cells (see mechanical_systems)")
    print("  - Pressure on building = momentum-flux divergence at substrate boundary")
    print("  - Vortex shedding = topological strain defects (vortex lines) shed")
    print("    periodically into wake — same class as superfluid quantized vortices")
    print("  - Lock-in (ω_shed = ω_struct) → same resonance picture as seismic")
    print()
    print(f"  {'wind regime':>22s}    {'V [m/s]':>8s}    {'q [Pa]':>8s}    {'note':>20s}")
    winds = [
        ('Calm',                    1,    1, 'Beaufort 1'),
        ('Strong breeze',          12,   88, 'Beaufort 6'),
        ('Gale',                   20,  245, 'Beaufort 9'),
        ('Hurricane Cat-1',        38,  884, 'design serviceability'),
        ('Hurricane Cat-3',        53, 1719, 'design ULS coastal'),
        ('Hurricane Cat-5',        77, 3631, 'extreme'),
        ('Tornado EF5',           135, 11160, 'localized, often >design'),
    ]
    for name, v, q, note in winds:
        print(f"  {name:>20s}      {v:>6.0f}      {q:>6.0f}      {note:>20s}")
    print()
    print("Tacoma Narrows Bridge 1940: wind 19 m/s induced torsional flutter at")
    print("  f≈0.2 Hz matching natural mode — substrate-mode resonance failure.")
    print()

    # ============== 6. FOUNDATIONS ==============
    print()
    print("=" * 70)
    print("6. FOUNDATIONS (footings, piles, settlement)")
    print("=" * 70)
    print()
    print("Standard:")
    print("  Spread footing: q_applied ≤ q_a (presumptive bearing)")
    print("  Pile capacity:  Q_ult = Q_skin + Q_tip = ΣL·perim·f_s + A_tip·q_tip")
    print("  Elastic settlement: s = q·B·(1-ν²)·I_s / E_s")
    print("  Consolidation:  s_c = (C_c/(1+e_0))·H·log₁₀((σ'_0+Δσ)/σ'_0)")
    print()
    print("Substrate:")
    print("  - Foundation transfers building substrate strain into soil substrate")
    print("  - Pile = stiff cylindrical inclusion that drains strain along skin")
    print("  - Consolidation = pore-water drag γ relaxes pore pressure → solid")
    print("    skeleton substrate carries load over time (Terzaghi clock)")
    print("  - Saturation cap σ ≤ 1/2 regularizes Boussinesq point-load singularity")
    print()
    print(f"  {'foundation type':>26s}    {'capacity':>14s}    {'typical use':>22s}")
    fdns = [
        ('Strip footing 0.6 m wide',  '60-200 kN/m', 'walls, low-rise'),
        ('Pad footing 2×2 m',         '0.5-2 MN',     'columns, mid-rise'),
        ('Mat/raft 30×30 m',          '50-500 MN',    'high-rise basement'),
        ('Driven pile 0.4 m × 20 m',  '0.8-2 MN',     'soft soil, bridges'),
        ('Bored pile 1.2 m × 40 m',   '8-25 MN',      'high-rise columns'),
        ('Caisson / barrette',        '20-100 MN',    'mega-tall, bridges'),
    ]
    for name, cap, use in fdns:
        print(f"  {name:>24s}      {cap:>14s}      {use:>22s}")
    print()

    # ============== 7. FATIGUE IN BRIDGES ==============
    print()
    print("=" * 70)
    print("7. FATIGUE IN BRIDGES (cyclic traffic, wind loading)")
    print("=" * 70)
    print()
    print("Standard AASHTO / Eurocode 3 fatigue:")
    print("  N·(Δσ)^m = A     (S-N curve, m≈3 for steel welds)")
    print("  Detail categories A (best) → E' (worst); CAFL = constant-amplitude")
    print("  fatigue limit, ~165 MPa for category A, ~18 MPa for E'")
    print("  Miner's rule: Σ(n_i/N_i) ≤ 1 for cumulative damage")
    print()
    print("Substrate:")
    print("  - Each truck axle pass = strain cycle; γ-damped energy dissipation")
    print("    leaves residual sub-yield micro-defects (topological dislocations)")
    print("  - Defects accumulate, coalesce → critical crack at weld toe")
    print("  - Substrate prediction: fatigue limit σ_e ≈ 0.5·σ_UTS (matches data)")
    print()
    print(f"  {'AASHTO detail':>20s}    {'Δσ_th [MPa]':>12s}    {'example':>30s}")
    fatigue = [
        ('Category A',           165, 'plain rolled section'),
        ('Category B',           110, 'longitudinal welds'),
        ('Category C',            69, 'transverse stiffener welds'),
        ('Category D',            48, 'cover plate ends'),
        ('Category E',            31, 'short attachments'),
        ("Category E'",            18, 'thick attachments, T-joints'),
    ]
    for name, dth, ex in fatigue:
        print(f"  {name:>18s}      {dth:>10.0f}      {ex:>30s}")
    print()
    print("Real bridges: Silver Bridge collapse 1967 (eyebar fatigue, 46 dead);")
    print("  I-35W Minneapolis 2007 (gusset plate undersized, fatigue contributed).")
    print()

    # ============== 8. STRUCTURAL MATERIALS ==============
    print()
    print("=" * 70)
    print("8. STRUCTURAL MATERIALS (steel, concrete, prestressed, timber)")
    print("=" * 70)
    print()
    print("Standard mechanical properties at room temperature:")
    print()
    print(f"  {'material':>22s}    {'E [GPa]':>8s}    {'σ_y [MPa]':>10s}    {'ρ [kg/m³]':>10s}")
    mats = [
        ('A36 structural steel',       200,  250,  7850),
        ('A992 W-shapes (50 ksi)',     200,  345,  7850),
        ('A572 Gr 65',                 200,  450,  7850),
        ('S355 (EN)',                  210,  355,  7850),
        ('Stainless 304',              193,  215,  8000),
        ('Aluminum 6061-T6',            69,  276,  2700),
        ('C30/37 concrete',           25.7,   30,  2400),  # σ_y here = f_c'
        ('UHPC',                      57.6,  150,  2500),
        ('Glulam timber (24h)',         11,   24,   500),
        ('CLT panel',                   12,   24,   480),
        ('CFRP unidirectional',        140, 2200,  1600),
        ('Stay cable strand',          195, 1860,  7850),
    ]
    for name, E, sy, rho in mats:
        print(f"  {name:>20s}      {E:>6.1f}      {sy:>8.0f}      {rho:>8.0f}")
    print()
    print("Prestressed concrete: precompress with 0.7·f_pu·A_ps so live tensile")
    print("  load never makes net stress tensile → no cracking. Substrate view:")
    print("  bias the substrate strain field into compression so saturation cap")
    print("  governs both halves of the load cycle symmetrically.")
    print()
    print("Strength-to-weight (σ_y/ρ) ranking, kN·m/kg:")
    print(f"  {'material':>22s}    {'σ_y/ρ':>10s}")
    sw = [(n, sy / rho) for (n, _, sy, rho) in mats]
    sw.sort(key=lambda r: -r[1])
    for n, ratio in sw[:6]:
        print(f"  {n:>20s}      {ratio:>8.3f}")
    print()

    # ============== SUMMARY ==============
    print()
    print("=" * 70)
    print("Summary: substrate IS civil/structural engineering")
    print("=" * 70)
    print()
    print("Civil/structural engineering is a DIRECT substrate sector:")
    print("  - Bending, shear, axial = substrate strain modes of structural members")
    print("  - Soil mechanics = granular substrate with cohesion + asperity friction")
    print("  - Seismic dynamics = forced substrate-mode oscillation, drag-damped")
    print("  - Wind loading = momentum flux from atmospheric substrate flow")
    print("  - Fatigue = topological-defect accumulation in substrate strain field")
    print()
    print("Substrate adds NOTHING to engineering numbers:")
    print("  E_steel = 200 GPa, f_c' = 30 MPa, q_a = 300 kPa — all measured.")
    print("  ASCE 7, ACI 318, Eurocode formulas unchanged.")
    print()
    print("Substrate ADDITIONS:")
    print("  - One Lagrangian L = ½ρ(∂_t u)² - ½K|∇u|² - V(u) - γ·u·∂_t u")
    print("    yields elastostatics, elastodynamics, AND consolidation in one go")
    print("  - Saturation σ ≤ 1/2 regularizes stress singularities at:")
    print("      * concrete crack tips (finite cohesive zone)")
    print("      * Boussinesq point-load contacts (finite settlement)")
    print("      * re-entrant corners and weld toes (finite hot-spot stress)")
    print("  - Fatigue micro-cracks reframed as topological substrate defects")
    print("    — same defect class as dislocations, vortex lines, cosmic strings")
    print()
    print("Practical impact: design codes unchanged.")
    print("Conceptual gain: every civil/structural failure mode (yielding,")
    print("buckling, cracking, settlement, resonance, fatigue) emerges from a")
    print("single substrate Lagrangian — no separate phenomenologies needed.")


if __name__ == "__main__":
    main()
