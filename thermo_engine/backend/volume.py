from __future__ import annotations

import math


def apparent_molar_volume(
    concentration_mol_l: float,
    density_solution_g_ml: float,
    density_solvent_g_ml: float,
    molar_mass_g_mol: float,
) -> dict:
    if concentration_mol_l <= 0:
        raise ValueError("concentration_mol_l must be positive")
    if density_solution_g_ml <= 0 or density_solvent_g_ml <= 0:
        raise ValueError("Densities must be positive")

    value = (molar_mass_g_mol / density_solution_g_ml) - (
        1000.0 * (density_solution_g_ml - density_solvent_g_ml)
    ) / (concentration_mol_l * density_solution_g_ml * density_solvent_g_ml)

    return {
        "apparent_molar_volume_cm3_mol": value,
        "equation": r"\phi_V = \frac{M}{\rho} - \frac{1000(\rho - \rho_0)}{c \rho \rho_0}",
    }


def debye_huckel_volume(
    ionic_strength: float,
    a_phi: float = 1.0,
    b: float = 1.2,
) -> dict:
    if ionic_strength < 0:
        raise ValueError("ionic_strength cannot be negative")
    root_i = math.sqrt(ionic_strength)
    value = -a_phi * root_i / (1.0 + b * root_i)
    return {
        "debye_huckel_term": value,
        "equation": r"V^{DH} = -A_{\phi}\frac{\sqrt{I}}{1 + b\sqrt{I}}",
    }

