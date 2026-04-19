from __future__ import annotations

from typing import Callable

import numpy as np

from antoine import calculate_vapor_pressure
from pression import activity_coefficients, fugacity_coefficients, normalize

try:
    from scipy.optimize import brentq as scipy_brentq
except Exception:  # pragma: no cover - exercised when scipy is unavailable
    scipy_brentq = None


def root_find(function: Callable[[float], float], lower: float, upper: float, iterations: int = 80) -> float:
    if scipy_brentq is not None:
        return float(scipy_brentq(function, lower, upper, maxiter=iterations))

    f_lower = function(lower)
    f_upper = function(upper)
    if f_lower == 0:
        return lower
    if f_upper == 0:
        return upper
    if f_lower * f_upper > 0:
        raise ValueError("Root bracket does not change sign.")

    left, right = lower, upper
    for _ in range(iterations):
        mid = 0.5 * (left + right)
        f_mid = function(mid)
        if abs(f_mid) < 1e-8:
            return mid
        if f_lower * f_mid < 0:
            right = mid
            f_upper = f_mid
        else:
            left = mid
            f_lower = f_mid
    return 0.5 * (left + right)


def _psat_vector(component_ids: list[int], temperature_c: float) -> np.ndarray:
    return np.array(
        [calculate_vapor_pressure(component_id, temperature_c, unit="bar")["pressure"] for component_id in component_ids],
        dtype=float,
    )


def gamma_phi_approach(
    temperature_c: float,
    component_ids: list[int],
    x: list[float],
    activity_model: str,
    eos_model: str,
    pressure_guess_bar: float = 1.0,
) -> dict:
    liquid_x = normalize(x)
    temperature_k = temperature_c + 273.15
    gamma_result = activity_coefficients(activity_model, liquid_x.tolist(), temperature_k, component_ids)
    gamma = np.array(gamma_result["gamma"], dtype=float)
    psat = _psat_vector(component_ids, temperature_c)

    pressure = float(pressure_guess_bar)
    y = liquid_x.copy()
    phi = np.ones_like(liquid_x)
    for _ in range(80):
        numerator = liquid_x * gamma * psat
        pressure_new = float(np.sum(numerator / np.maximum(phi, 1e-12)))
        y_new = numerator / max(pressure_new, 1e-12)
        y_new = normalize(y_new)
        phi_result = fugacity_coefficients(eos_model, temperature_k, pressure_new, y_new.tolist(), component_ids, phase="vapor")
        phi_new = np.array(phi_result["phi"], dtype=float)
        if abs(pressure_new - pressure) < 1e-8 and np.max(np.abs(y_new - y)) < 1e-8:
            pressure = pressure_new
            y = y_new
            phi = phi_new
            break
        pressure = pressure_new
        y = y_new
        phi = phi_new

    return {
        "approach": "gamma-phi",
        "pressure_bar": pressure,
        "y": y.tolist(),
        "gamma": gamma.tolist(),
        "phi": phi.tolist(),
        "equations": [
            r"y_i P = x_i \gamma_i P_i^{sat} / \phi_i^V",
            gamma_result["equation"],
        ],
    }


def phi_phi_approach(
    temperature_c: float,
    component_ids: list[int],
    x: list[float],
    eos_model: str,
    pressure_guess_bar: float = 1.0,
) -> dict:
    liquid_x = normalize(x)
    temperature_k = temperature_c + 273.15
    psat = _psat_vector(component_ids, temperature_c)
    pressure = float(pressure_guess_bar)
    y = liquid_x.copy()

    for _ in range(60):
        phi_v = np.array(
            fugacity_coefficients(eos_model, temperature_k, pressure, y.tolist(), component_ids, phase="vapor")["phi"],
            dtype=float,
        )
        phi_l = np.array(
            fugacity_coefficients(eos_model, temperature_k, pressure, liquid_x.tolist(), component_ids, phase="liquid")["phi"],
            dtype=float,
        )
        k_values = (phi_l / np.maximum(phi_v, 1e-12)) * (psat / max(pressure, 1e-12))
        y_new = normalize(liquid_x * k_values)
        pressure_new = float(np.sum(liquid_x * k_values * pressure))
        if abs(pressure_new - pressure) < 1e-8 and np.max(np.abs(y_new - y)) < 1e-8:
            pressure = pressure_new
            y = y_new
            break
        pressure = pressure_new
        y = y_new

    return {
        "approach": "phi-phi",
        "pressure_bar": pressure,
        "y": y.tolist(),
        "equations": [r"y_i = K_i x_i", r"K_i = \phi_i^L P_i^{sat} / (\phi_i^V P)"],
    }


def bubble_point_pressure(
    temperature_c: float,
    component_ids: list[int],
    x: list[float],
    activity_model: str = "NRTL",
    eos_model: str = "PR",
    approach: str = "gamma-phi",
) -> dict:
    if approach == "phi-phi":
        return phi_phi_approach(temperature_c, component_ids, x, eos_model=eos_model)
    return gamma_phi_approach(temperature_c, component_ids, x, activity_model=activity_model, eos_model=eos_model)


def bubble_point_temperature(
    pressure_bar: float,
    component_ids: list[int],
    x: list[float],
    activity_model: str = "NRTL",
    eos_model: str = "PR",
    approach: str = "gamma-phi",
    bracket_c: tuple[float, float] = (20.0, 160.0),
) -> dict:
    def objective(temp_c: float) -> float:
        result = bubble_point_pressure(
            temperature_c=temp_c,
            component_ids=component_ids,
            x=x,
            activity_model=activity_model,
            eos_model=eos_model,
            approach=approach,
        )
        return result["pressure_bar"] - pressure_bar

    temperature_c = root_find(objective, bracket_c[0], bracket_c[1])
    result = bubble_point_pressure(
        temperature_c=temperature_c,
        component_ids=component_ids,
        x=x,
        activity_model=activity_model,
        eos_model=eos_model,
        approach=approach,
    )
    result["temperature_c"] = temperature_c
    result["target_pressure_bar"] = pressure_bar
    return result

