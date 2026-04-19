from __future__ import annotations

from antoine import antoine_curve
from fraction_vapeur import bubble_point_pressure
from pression import activity_coefficients


def gamma_vs_composition(temperature_c: float, component_ids: list[int], model: str, points: int = 31) -> dict:
    x_values = []
    gamma1 = []
    gamma2 = []
    temperature_k = temperature_c + 273.15
    for idx in range(points):
        x1 = idx / (points - 1)
        composition = [x1, 1.0 - x1]
        gamma = activity_coefficients(model, composition, temperature_k, component_ids)["gamma"]
        x_values.append(x1)
        gamma1.append(gamma[0])
        gamma2.append(gamma[1])
    return {"x1": x_values, "gamma1": gamma1, "gamma2": gamma2}


def pxy_diagram(temperature_c: float, component_ids: list[int], activity_model: str, eos_model: str, points: int = 31) -> dict:
    x1_values = []
    y1_values = []
    pressures = []
    for idx in range(points):
        x1 = idx / (points - 1)
        result = bubble_point_pressure(
            temperature_c=temperature_c,
            component_ids=component_ids,
            x=[x1, 1.0 - x1],
            activity_model=activity_model,
            eos_model=eos_model,
            approach="gamma-phi",
        )
        x1_values.append(x1)
        y1_values.append(result["y"][0])
        pressures.append(result["pressure_bar"])
    return {"x1": x1_values, "y1": y1_values, "pressure_bar": pressures}


def yx_diagram(temperature_c: float, component_ids: list[int], activity_model: str, eos_model: str, points: int = 31) -> dict:
    pxy = pxy_diagram(temperature_c, component_ids, activity_model, eos_model, points=points)
    return {"x1": pxy["x1"], "y1": pxy["y1"]}


def Antoine_curve(component_id: int, start_c: float, end_c: float, points: int = 40) -> dict:
    return antoine_curve(component_id, start_c, end_c, points=points)

