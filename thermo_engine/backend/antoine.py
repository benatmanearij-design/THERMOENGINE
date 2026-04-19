from __future__ import annotations

import math

from db import get_antoine_constants


MMHG_TO_BAR = 0.001333223684


def psat_antoine(temperature_c: float, a: float, b: float, c: float, unit: str = "bar") -> float:
    pressure_mmhg = 10 ** (a - (b / (temperature_c + c)))
    if unit == "mmHg":
        return pressure_mmhg
    if unit == "bar":
        return pressure_mmhg * MMHG_TO_BAR
    raise ValueError("Unsupported pressure unit. Use 'bar' or 'mmHg'.")


def calculate_vapor_pressure(component_id: int, temperature_c: float, unit: str = "bar") -> dict:
    constants = get_antoine_constants(component_id)
    pressure = psat_antoine(temperature_c, constants["a"], constants["b"], constants["c"], unit=unit)
    return {
        "component_id": component_id,
        "temperature_c": temperature_c,
        "pressure": pressure,
        "unit": unit,
        "equation": r"\log_{10}(P^{sat}) = A - \frac{B}{T + C}",
        "constants": {"A": constants["a"], "B": constants["b"], "C": constants["c"]},
    }


def antoine_curve(component_id: int, start_c: float, end_c: float, points: int = 40, unit: str = "bar") -> dict:
    if end_c <= start_c:
        raise ValueError("end_c must be greater than start_c")
    temperatures = [start_c + (end_c - start_c) * idx / (points - 1) for idx in range(points)]
    pressures = [calculate_vapor_pressure(component_id, value, unit=unit)["pressure"] for value in temperatures]
    return {"temperature_c": temperatures, "pressure": pressures, "unit": unit}


def relative_error(reference: float, candidate: float) -> float:
    if math.isclose(reference, 0.0):
        return abs(candidate)
    return abs(candidate - reference) / abs(reference)

