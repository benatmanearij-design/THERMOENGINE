from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from db import get_molecule, get_nrtl_pair, get_uniquac_pair


R = 0.08314472


def normalize(vector: list[float] | np.ndarray) -> np.ndarray:
    values = np.array(vector, dtype=float)
    total = values.sum()
    if total <= 0:
        raise ValueError("Composition must sum to a positive value.")
    return values / total


def fetch_activity_parameters(model: str, component_ids: list[int]) -> dict:
    if model == "NRTL":
        return get_nrtl_pair(component_ids)
    if model == "UNIQUAC":
        return get_uniquac_pair(component_ids)
    raise ValueError(f"Unsupported activity model {model}")


def nrtl_gamma(x: list[float], temperature_k: float, component_ids: list[int], params: dict | None = None) -> list[float]:
    x = normalize(x)
    if len(x) != 2:
        raise ValueError("NRTL implementation currently supports binary systems.")
    params = params or fetch_activity_parameters("NRTL", component_ids)
    tau12 = params["a12"] / temperature_k
    tau21 = params["a21"] / temperature_k
    alpha = params.get("alpha", 0.3)

    g12 = math.exp(-alpha * tau12)
    g21 = math.exp(-alpha * tau21)
    x1, x2 = float(x[0]), float(x[1])

    gamma1 = math.exp(
        x2**2
        * (
            tau21 * (g21 / (x1 + x2 * g21)) ** 2
            + tau12 * g12 / (x2 + x1 * g12) ** 2
        )
    )
    gamma2 = math.exp(
        x1**2
        * (
            tau12 * (g12 / (x2 + x1 * g12)) ** 2
            + tau21 * g21 / (x1 + x2 * g21) ** 2
        )
    )
    return [gamma1, gamma2]


def uniquac_gamma(x: list[float], component_ids: list[int], temperature_k: float | None = None, params: dict | None = None) -> list[float]:
    del temperature_k
    x = normalize(x)
    if len(x) != 2:
        raise ValueError("UNIQUAC implementation currently supports binary systems.")
    params = params or fetch_activity_parameters("UNIQUAC", component_ids)
    r = np.array(params["r"], dtype=float)
    q = np.array(params["q"], dtype=float)

    phi = (r * x) / np.sum(r * x)
    theta = (q * x) / np.sum(q * x)
    z = 10.0
    l = (z / 2.0) * (r - q) - (r - 1.0)
    ln_gamma_c = np.log(phi / x) + (z / 2.0) * q * np.log(theta / phi) + l - phi / x * np.sum(x * l)

    ln_gamma_r = 1.0 - theta
    gamma = np.exp(ln_gamma_c + ln_gamma_r)
    return gamma.tolist()


def activity_coefficients(model: str, x: list[float], temperature_k: float, component_ids: list[int], params: dict | None = None) -> dict:
    model_name = model.upper()
    if model_name == "NRTL":
        values = nrtl_gamma(x, temperature_k, component_ids, params)
        equation = r"\ln \gamma_i = \text{NRTL}(x, \tau_{ij}, \alpha)"
    elif model_name == "UNIQUAC":
        values = uniquac_gamma(x, component_ids, temperature_k, params)
        equation = r"\ln \gamma_i = \ln(\gamma_i^C) + \ln(\gamma_i^R)"
    else:
        raise ValueError(f"Unsupported activity model {model}")

    return {"model": model_name, "gamma": values, "equation": equation}


@dataclass
class ComponentEOS:
    tc: float
    pc_bar: float
    omega: float


def get_component_eos(component_id: int) -> ComponentEOS:
    molecule = get_molecule(component_id)
    if not molecule:
        raise ValueError(f"Molecule {component_id} not found")
    return ComponentEOS(tc=molecule["tc"], pc_bar=molecule["pc_bar"], omega=molecule["omega"])


def _cubic_parameters(component: ComponentEOS, temperature_k: float, eos_model: str) -> tuple[float, float]:
    tr = temperature_k / component.tc
    if eos_model == "PR":
        kappa = 0.37464 + 1.54226 * component.omega - 0.26992 * component.omega**2
        alpha = (1 + kappa * (1 - math.sqrt(tr))) ** 2
        a = 0.45724 * (R**2) * (component.tc**2) * alpha / component.pc_bar
        b = 0.07780 * R * component.tc / component.pc_bar
    elif eos_model == "SRK":
        m = 0.480 + 1.574 * component.omega - 0.176 * component.omega**2
        alpha = (1 + m * (1 - math.sqrt(tr))) ** 2
        a = 0.42748 * (R**2) * (component.tc**2) * alpha / component.pc_bar
        b = 0.08664 * R * component.tc / component.pc_bar
    else:
        raise ValueError(f"Unsupported EOS model {eos_model}")
    return a, b


def _mixing_rule(x: np.ndarray, a_values: np.ndarray, b_values: np.ndarray, kij: np.ndarray | None = None) -> tuple[float, float, np.ndarray]:
    count = len(x)
    kij = np.zeros((count, count)) if kij is None else kij
    aij = np.zeros((count, count))
    for i in range(count):
        for j in range(count):
            aij[i, j] = math.sqrt(a_values[i] * a_values[j]) * (1 - kij[i, j])
    am = float(np.sum(x[:, None] * x[None, :] * aij))
    bm = float(np.sum(x * b_values))
    return am, bm, aij


def _solve_cubic_roots(a_mix: float, b_mix: float, pressure_bar: float, temperature_k: float, eos_model: str) -> np.ndarray:
    a_cap = a_mix * pressure_bar / (R**2 * temperature_k**2)
    b_cap = b_mix * pressure_bar / (R * temperature_k)

    if eos_model == "PR":
        coeffs = [1.0, -(1.0 - b_cap), a_cap - 3.0 * b_cap**2 - 2.0 * b_cap, -(a_cap * b_cap - b_cap**2 - b_cap**3)]
    else:
        coeffs = [1.0, -1.0, a_cap - b_cap - b_cap**2, -a_cap * b_cap]

    roots = np.roots(coeffs)
    real_roots = np.real(roots[np.isclose(np.imag(roots), 0.0, atol=1e-10)])
    return np.sort(real_roots)


def fugacity_coefficients(
    eos_model: str,
    temperature_k: float,
    pressure_bar: float,
    composition: list[float],
    component_ids: list[int],
    phase: str = "vapor",
    kij: np.ndarray | None = None,
) -> dict:
    eos_name = eos_model.upper()
    x = normalize(composition)
    components = [get_component_eos(component_id) for component_id in component_ids]
    a_values = np.array([_cubic_parameters(component, temperature_k, eos_name)[0] for component in components], dtype=float)
    b_values = np.array([_cubic_parameters(component, temperature_k, eos_name)[1] for component in components], dtype=float)
    a_mix, b_mix, aij = _mixing_rule(x, a_values, b_values, kij)
    roots = _solve_cubic_roots(a_mix, b_mix, pressure_bar, temperature_k, eos_name)
    if len(roots) == 0:
        raise ValueError("No real compressibility root found.")

    z = float(roots[-1] if phase == "vapor" else roots[0])
    a_cap = a_mix * pressure_bar / (R**2 * temperature_k**2)
    b_cap = b_mix * pressure_bar / (R * temperature_k)

    phi = []
    for idx in range(len(x)):
        bi = b_values[idx]
        bi_cap = bi * pressure_bar / (R * temperature_k)
        sum_aij = float(np.sum(x * aij[idx, :]))
        if eos_name == "PR":
            sqrt2 = math.sqrt(2.0)
            term1 = bi_cap * (z - 1.0) / max(b_cap, 1e-12)
            term2 = -math.log(max(z - b_cap, 1e-12))
            term3 = (
                a_cap
                / (2.0 * sqrt2 * max(b_cap, 1e-12))
                * ((2.0 * sum_aij / max(a_mix, 1e-12)) - (bi / max(b_mix, 1e-12)))
                * math.log(max((z + (1.0 + sqrt2) * b_cap) / (z + (1.0 - sqrt2) * b_cap), 1e-12))
            )
            ln_phi = term1 + term2 - term3
        else:
            term1 = bi_cap * (z - 1.0) / max(b_cap, 1e-12)
            term2 = -math.log(max(z - b_cap, 1e-12))
            term3 = (a_cap / max(b_cap, 1e-12)) * ((2.0 * sum_aij / max(a_mix, 1e-12)) - (bi / max(b_mix, 1e-12))) * math.log(max(1.0 + b_cap / z, 1e-12))
            ln_phi = term1 + term2 - term3
        phi.append(math.exp(ln_phi))

    return {
        "model": eos_name,
        "phase": phase,
        "compressibility": z,
        "phi": phi,
        "equation": r"\phi_i = \exp\left(\frac{\bar{G}_i^R}{RT}\right)",
    }

