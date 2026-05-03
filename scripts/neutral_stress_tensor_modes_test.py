#!/usr/bin/env python3
"""Report the neutral-stress tensor mode count."""

from __future__ import annotations

from stiff_medium.neutral_stress_tensor_modes import assess_neutral_stress_modes


def main() -> None:
    result = assess_neutral_stress_modes()

    print("NEUTRAL-STRESS TENSOR MODES")
    print(f"projector rank = {result.projector_rank}")
    print(f"trace eigenvalue = {result.trace_eigenvalue:.3e}")
    print(
        "shear eigenvalues = "
        + ", ".join(f"{value:.3f}" for value in result.shear_eigenvalues)
    )
    print(f"idempotence error = {result.idempotence_error:.3e}")
    print(f"speed formula = {result.speed_formula}")
    print(f"v_dark = {result.v_dark_km_s:.6f} km/s")
    print(f"verdict = {result.verdict}")


if __name__ == "__main__":
    main()
