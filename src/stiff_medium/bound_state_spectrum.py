"""Bound-state spectrum solver for substrate cone-bouncing oscillations.

Solves the radial Schrodinger eigenvalue problem
    H psi = E psi,    H = -(hbar^2 / 2 mu) d^2/dr^2 + V_eff(r)
with V_eff(r) = V_conf(r) + hbar^2 l(l+1) / (2 mu r^2)
on a 1D radial grid using a sparse tridiagonal Hamiltonian and scipy.sparse.linalg.eigsh.

Substrate framework interpretation: bound states (electrons, quarks, deuteron, ...)
are cone-bouncing oscillations of the substrate field with effective inertia
mu = mu(K, rho, xi, gamma) and a confining potential V_conf inherited from
the substrate Lagrangian (Coulomb, harmonic, finite well, K_4 face-pair).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import eigsh

# ---- physical constants (SI / convenient atomic & nuclear units) ----
HBAR_eVs = 6.582119569e-16          # eV s
HBAR_MeVs = 6.582119569e-22         # MeV s
M_E_eV = 0.51099895000e6            # electron mass in eV/c^2
M_E_kg = 9.1093837015e-31
E_CHARGE = 1.602176634e-19          # C
EPS0 = 8.8541878128e-12             # F/m
A0 = 5.29177210903e-11              # Bohr radius (m)
RYDBERG_eV = 13.605693122994        # H ground-state binding energy
HBARC_eV_nm = 197.3269804           # eV nm
HBARC_MeV_fm = 197.3269804          # MeV fm
M_PROTON_MeV = 938.27208816
M_NEUTRON_MeV = 939.56542052
MU_DEUTERON_MeV = (M_PROTON_MeV * M_NEUTRON_MeV) / (M_PROTON_MeV + M_NEUTRON_MeV)


@dataclass
class SubstrateParams:
    """Substrate Lagrangian parameters (placeholders for downstream coupling)."""
    K: float = 1.0       # stiffness
    rho: float = 1.0     # density
    xi: float = 1.0      # cone aperture
    gamma: float = 1.0   # damping / dissipation

    def effective_mass(self, m_bare: float) -> float:
        """Substrate-renormalised effective mass.

        For now, a passthrough; framework hooks (back-reaction, dressing) can
        modify this with K, rho, xi, gamma.
        """
        return m_bare


@dataclass
class GridSpec:
    r_min: float
    r_max: float
    N: int
    def axis(self) -> np.ndarray:
        # avoid r=0 to keep the centrifugal/Coulomb singular term finite
        return np.linspace(self.r_min, self.r_max, self.N)


class BoundStateSpectrum:
    """Radial Schrodinger eigenvalue solver on a uniform 1D grid.

    Units convention is set per-call: pass (hbar, mass) in matched units and
    the potential V(r) in the same energy unit on the same length unit.
    Provided helpers (solve_hydrogen, solve_harmonic, solve_finite_well,
    solve_substrate_K4) wire up unit-consistent defaults.
    """

    def __init__(self, params: Optional[SubstrateParams] = None):
        self.params = params or SubstrateParams()
        self._last_report: list[dict] = []

    # ---------- core eigensolver ----------
    @staticmethod
    def _hamiltonian(r: np.ndarray, V: np.ndarray, hbar: float, mass: float,
                     l: int = 0):
        """Build H = T + V_eff as a sparse tridiagonal matrix.

        Uses the reduced radial wavefunction u(r) = r * R(r), so
            -(hbar^2 / 2m) u''(r) + [V(r) + hbar^2 l(l+1)/(2 m r^2)] u(r) = E u(r)
        with Dirichlet BC u(r_min)=u(r_max)=0 (interior grid).
        """
        N = len(r)
        dr = r[1] - r[0]
        kin_coeff = hbar * hbar / (2.0 * mass * dr * dr)
        centrifugal = hbar * hbar * l * (l + 1) / (2.0 * mass * r * r)
        diag_main = 2.0 * kin_coeff + V + centrifugal
        diag_off = -kin_coeff * np.ones(N - 1)
        H = diags([diag_off, diag_main, diag_off], offsets=[-1, 0, 1], format="csr")
        return H

    def solve(self, r: np.ndarray, V: np.ndarray, hbar: float, mass: float,
              k: int = 5, l: int = 0,
              sigma: Optional[float] = None) -> tuple[np.ndarray, np.ndarray]:
        """Return (eigenvalues_ascending, eigenvectors[:,k]).

        If `sigma` is provided, use shift-invert mode anchored at sigma; this
        is much faster for finding the few lowest bound states when the
        Hamiltonian's spectrum extends to large positive kinetic energies.
        """
        H = self._hamiltonian(r, V, hbar, mass, l=l)
        if sigma is not None:
            vals, vecs = eigsh(H, k=k, sigma=sigma, which="LM")
        else:
            vals, vecs = eigsh(H, k=k, which="SA")
        order = np.argsort(vals)
        return vals[order], vecs[:, order]

    # ---------- problem wrappers ----------
    def solve_hydrogen(self, n_states: int = 5, l: int = 0,
                       r_max_bohr: float = 80.0, N: int = 8000):
        """Hydrogen Coulomb: V(r) = -e^2 / (4 pi eps0 r). Returns eigenvalues in eV."""
        # Work in SI; convert energy result to eV at the end.
        # r_min should be a small fraction of a_0 — too small produces a
        # spurious deep eigenvalue from the discretised Coulomb singularity,
        # too large under-resolves the cusp.  r_min ~ 0.05 a_0 with a fine
        # grid lands within 1% of -13.6 eV.
        r_min = 0.01 * A0
        r = np.linspace(r_min, r_max_bohr * A0, N)
        V_J = -(E_CHARGE ** 2) / (4.0 * np.pi * EPS0 * r)
        V_eV = V_J / E_CHARGE
        # Schrodinger in eV units: hbar in eV*s, mass converted.  Use
        # natural atomic units instead via the 'effective Rydberg' scaling:
        # convert by computing in SI and translating.
        hbar_SI = 1.054571817e-34
        m_e = self.params.effective_mass(M_E_kg)
        H = self._hamiltonian(r, V_J, hbar_SI, m_e, l=l)
        vals, vecs = eigsh(H, k=n_states + l, which="SA")
        vals = np.sort(vals) / E_CHARGE  # to eV
        # take the lowest n_states eigenvalues (states with given l start at n=l+1)
        eigs_eV = vals[:n_states]
        analytic = np.array([-RYDBERG_eV / (n + l + 1) ** 2 for n in range(n_states)])
        self._record("Hydrogen (l=%d)" % l, eigs_eV, analytic, unit="eV")
        return eigs_eV, analytic

    def solve_harmonic(self, n_states: int = 5, omega: float = 1.0,
                       mass: float = 1.0, hbar: float = 1.0,
                       r_max: float = 12.0, N: int = 4000):
        """1D harmonic oscillator on the half-line with l=0 reduced radial form.

        For an isotropic 3D HO with l=0 the radial spectrum is
            E_{n_r,0} = hbar omega (2 n_r + 3/2),  n_r = 0,1,2,...
        We compare against this 3D-l=0 ladder.
        """
        r = np.linspace(1e-6, r_max, N)
        V = 0.5 * mass * omega ** 2 * r ** 2
        vals, _ = self.solve(r, V, hbar=hbar, mass=mass, k=n_states, l=0)
        analytic = np.array([hbar * omega * (2 * n + 1.5) for n in range(n_states)])
        self._record("Harmonic (3D l=0)", vals, analytic, unit="hbar*omega units")
        return vals, analytic

    def solve_finite_well(self, V0: float = 50.0, a: float = 1.0,
                          mass: float = 1.0, hbar: float = 1.0,
                          r_max: float = 20.0, N: int = 4000,
                          k: int = 8):
        """Spherical finite well V=-V0 for r<a, 0 outside. Returns bound (E<0) eigenvalues."""
        r = np.linspace(1e-6, r_max, N)
        V = np.where(r < a, -V0, 0.0)
        vals, _ = self.solve(r, V, hbar=hbar, mass=mass, k=k, l=0)
        bound = vals[vals < 0.0]
        # crude analytic count (l=0 transcendental): N_bound ~ floor(z0/pi) + 1
        z0 = a * np.sqrt(2.0 * mass * V0) / hbar
        expected_count = int(np.floor(z0 / np.pi)) + 1
        self._record("Finite well (count)",
                     np.array([len(bound)], dtype=float),
                     np.array([expected_count], dtype=float),
                     unit="states")
        return bound, expected_count

    def solve_substrate_K4(self, n_states: int = 3,
                           V0_MeV: float = 35.0,
                           a_fm: float = 2.1,
                           r_max_fm: float = 30.0,
                           N: int = 4000):
        """K_4 face-pair potential approximated as a finite spherical well.

        The B3 K_4 cell binds two nucleons through face-pair coupling; at the
        coarse-grained scale this maps onto a short-range attractive well of
        depth V0 ~ 35 MeV and range a ~ 2.1 fm, the standard deuteron-fit
        parameters.  The l=0 ground state is identified with the deuteron and
        compared to the empirical binding energy 2.2245 MeV.
        """
        r = np.linspace(1e-3, r_max_fm, N)               # fm
        V = np.where(r < a_fm, -V0_MeV, 0.0)             # MeV
        # Use natural nuclear units: hbar*c = 197.327 MeV*fm, mass = mu c^2 in MeV.
        # Schrodinger in these units: kinetic prefactor (hbar c)^2 / (2 mu c^2).
        # Equivalent to using hbar -> hbar*c, mass -> mu*c^2 with r in fm and V in MeV.
        hbar_eff = HBARC_MeV_fm
        mass_eff = MU_DEUTERON_MeV
        vals, _ = self.solve(r, V, hbar=hbar_eff, mass=mass_eff,
                             k=n_states, l=0, sigma=-V0_MeV * 0.5)
        bound = vals[vals < 0.0]
        BE_pred = -bound[0] if len(bound) else float("nan")
        BE_emp = 2.2245
        self._record("K_4 -> deuteron BE",
                     np.array([BE_pred]), np.array([BE_emp]),
                     unit="MeV")
        return BE_pred, BE_emp, bound

    # ---------- reporting ----------
    def _record(self, label: str, predicted: np.ndarray, analytic: np.ndarray,
                unit: str = ""):
        self._last_report.append(dict(label=label, predicted=np.asarray(predicted),
                                      analytic=np.asarray(analytic), unit=unit))

    def report(self) -> str:
        lines = []
        lines.append("=" * 72)
        lines.append("BoundStateSpectrum  -  predicted vs analytic")
        lines.append("=" * 72)
        for entry in self._last_report:
            lines.append(f"\n{entry['label']}   [{entry['unit']}]")
            lines.append(f"  {'idx':>4} {'predicted':>16} {'analytic':>16} {'rel.err':>12}")
            p = entry["predicted"]; a = entry["analytic"]
            n = min(len(p), len(a))
            for i in range(n):
                ai = a[i]
                rel = abs(p[i] - ai) / abs(ai) if ai != 0 else float("nan")
                lines.append(f"  {i:>4d} {p[i]:>16.6g} {ai:>16.6g} {rel:>12.3%}")
        lines.append("=" * 72)
        text = "\n".join(lines)
        print(text)
        return text


__all__ = ["BoundStateSpectrum", "SubstrateParams", "GridSpec",
           "RYDBERG_eV", "M_PROTON_MeV", "M_NEUTRON_MeV", "MU_DEUTERON_MeV",
           "HBARC_MeV_fm"]
