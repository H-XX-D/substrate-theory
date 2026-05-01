"""Could larger magic-number DM nuclei resolve dwarf cusp-core problem?

Cube DM (N=8): σ/m ~ 10⁻³⁰ cm²/g, way below SIDM requirement (0.1-1 cm²/g)

Could DM at HIGHER magic numbers (N=20 dodecahedron, N=28, N=50, ...) have
LARGER self-interaction enough to fix dwarf cusp-core? Audit the physics.

Self-interaction enhancement from cell size:
  - More vertices → more multipole moments → more cross-section per particle
  - But also more mass per particle
  - Net: σ/m ∝ (vertex²) / (vertex × m_unit) = N_vertex / m_unit
  - Linear in N_vertex, not exponential

To bridge from σ/m = 10⁻³⁰ to required 0.1 cm²/g requires factor 10²⁹.
Linear N_vertex scaling can't get there — would need N ~ 10²⁹ vertices.
Standard polyhedra max ~10² vertices.

What actually gives large σ/m in SIDM models:
  - LIGHT FORCE MEDIATOR (Yukawa-style) — substrate doesn't have one
  - BOUND-STATE FORMATION (DM-DM → bound state + photon emission) — substrate has no light photon mediator within DM sector

So substrate-DM CAN'T have SIDM-strength self-interaction regardless of cell size.

Honest answer: NO, larger magic-number DM doesn't resolve dwarf cusp-core
through self-interaction mechanism. Need different explanation:
  - Baryonic feedback (most likely; supernova-driven gas outflows)
  - Fuzzy DM (substrate-DM is too heavy, this isn't it)
  - Modified gravity at galactic scales (substrate doesn't predict)
"""

from __future__ import annotations
import math


PI = math.pi
HBAR_C_MEV_FM = 197.3
M_PROTON_MEV = 938.27


def main() -> None:
    print("Larger magic-number DM nuclei: do they fix dwarf cusp-core?")
    print("=" * 70)
    print()

    print("Magic-number polyhedra and predicted DM masses:")
    print()
    cells = [
        ('K_2 (bond)',         2,  1,  'magic 2'),
        ('Tetrahedron K_4',    4,  6,  'nucleon'),
        ('Cube Q_3',           8, 12,  'magic 8 ★ DM candidate'),
        ('Dodecahedron',      20, 30,  'magic 20'),
        ('No standard',       28, 0,   'magic 28 — needs substrate-derived cell'),
        ('Truncated icos.',   60, 90,  'fullerene C60 — non-magic'),
        ('No standard',       82, 0,   'magic 82'),
        ('No standard',      126, 0,   'magic 126'),
    ]

    print(f"{'cell':>20s}  {'N_v':>5s}  {'N_e':>5s}  {'magic? / role':>30s}")
    for name, nv, ne, role in cells:
        marker = ' ★' if 'DM' in role else ''
        print(f"  {name:>18s}    {nv:>3d}    {ne:>3d}    {role:>28s}{marker}")
    print()

    # Mass scales for larger cells
    print("=" * 70)
    print("Mass and self-interaction scaling with cell size")
    print("=" * 70)
    print()
    # m_DM ~ N_vertex × constituent mass × (binding-shift factor)
    # σ_self ~ N_vertex² × (multipole cross-section per vertex)
    # σ/m ~ N_vertex × (multipole / m_unit)
    #
    print(f"{'cell':>20s}  {'N_v':>5s}  {'m_DM est. [GeV]':>16s}  {'σ/m est. [cm²/g]':>20s}")
    for name, nv, ne, role in cells:
        if nv == 0:
            continue
        # Crude: m_DM ~ N_vertex × M_proton/4 (calibrated to cube → 27.5 / 4 ~ 7? but we used 27.5 above)
        # Use the corrected calibration: cube mass = 27.5 GeV from first excited mode
        # For N>8, scale linearly (rough estimate)
        m_DM_GeV = 27.5 * (nv / 8)
        # σ/m: cube was ~10⁻³⁰ cm²/g; scale linearly with N_vertex
        sigma_per_m = 1e-30 * (nv / 8)
        print(f"  {name:>18s}    {nv:>3d}    {m_DM_GeV:>12.2f}    {sigma_per_m:>16.2e}")
    print()
    print("Even N_vertex = 126 (largest magic number) gives σ/m ~ 1.6e-29 cm²/g")
    print("Required for dwarf cusp-core: 0.1-1 cm²/g")
    print("→ Need 10²⁹ enhancement, way beyond N_vertex scaling")
    print()

    # Why SIDM doesn't naturally happen in substrate
    print("=" * 70)
    print("Why substrate-DM CAN'T have SIDM-strength self-interaction")
    print("=" * 70)
    print()
    print("Standard SIDM models invoke:")
    print("  - Light Yukawa mediator (mass ~10 MeV - 1 GeV)")
    print("  - DM particles ~10 GeV exchange this mediator")
    print("  - Cross-section enhanced at low velocity (Sommerfeld)")
    print("  - Achieves σ/m ~ 1 cm²/g with mediator α_χ ~ 0.01")
    print()
    print("Substrate framework has NO such mediator:")
    print("  - Only photon (which doesn't couple to non-polar DM monopole)")
    print("  - Only gluon (confined, doesn't couple between separate DM cells)")
    print("  - Only graviton (universal, gives σ/m ~ 10⁻³⁸ cm²/g — way too small)")
    print()
    print("Substrate-DM IS strictly collisionless at galactic scales.")
    print()

    # What resolves dwarf cusp-core then?
    print("=" * 70)
    print("Resolution of dwarf cusp-core problem (substrate-compatible options)")
    print("=" * 70)
    print()
    print("1. BARYONIC FEEDBACK (most likely real answer)")
    print("   Supernova-driven gas outflows redistribute DM in small halos.")
    print("   FIRE simulations (Hopkins+) show this works well for dwarfs.")
    print("   Substrate-DM is consistent with this — pure CDM with feedback.")
    print()
    print("2. NUMERICAL SIMULATION ARTIFACTS")
    print("   Some 'cusps' in simulations are sub-resolution effects.")
    print("   Recent high-resolution work shows core-like profiles emerge naturally")
    print("   when stellar feedback is properly modeled.")
    print()
    print("3. MODIFIED GRAVITY (not substrate-compatible)")
    print("   MOND-style modifications could explain dwarf cores without DM.")
    print("   Substrate doesn't predict gravity modification → not this.")
    print()
    print("4. WARM/FUZZY DM (substrate-DM is too heavy)")
    print("   keV-scale or 10⁻²² eV DM gives natural cores.")
    print("   Substrate cube-DM at 27.5 GeV is firmly cold → not this.")
    print()
    print("Substrate framework's stance: dwarf cusp-core is BARYONIC, not DM.")
    print("DM is collisionless cold cube-cells; baryonic feedback creates cores.")


if __name__ == "__main__":
    main()
