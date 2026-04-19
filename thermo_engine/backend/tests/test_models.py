from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from antoine import calculate_vapor_pressure
from db import initialize_database
from fraction_vapeur import bubble_point_pressure, bubble_point_temperature
from pression import activity_coefficients, fugacity_coefficients
from volume import apparent_molar_volume, debye_huckel_volume


initialize_database()


def test_antoine_water_at_100c_is_near_one_atm():
    result = calculate_vapor_pressure(1, 100.0, unit="bar")
    assert abs(result["pressure"] - 1.01325) < 0.02


def test_nrtl_gamma_is_positive():
    result = activity_coefficients("NRTL", [0.4, 0.6], 351.15, [2, 1])
    assert result["gamma"][0] > 0
    assert result["gamma"][1] > 0


def test_pr_fugacity_coefficients_are_positive():
    result = fugacity_coefficients("PR", 351.15, 1.2, [0.5, 0.5], [2, 1], phase="vapor")
    assert result["compressibility"] > 0
    assert all(value > 0 for value in result["phi"])


def test_bubble_pressure_returns_normalized_vapor_composition():
    result = bubble_point_pressure(78.0, [2, 1], [0.5, 0.5], activity_model="NRTL", eos_model="PR")
    assert 0.1 < result["pressure_bar"] < 3.0
    assert abs(sum(result["y"]) - 1.0) < 1e-6


def test_bubble_temperature_hits_target_pressure():
    result = bubble_point_temperature(1.01325, [2, 1], [0.5, 0.5], activity_model="NRTL", eos_model="PR")
    assert 60.0 < result["temperature_c"] < 110.0


def test_apparent_molar_volume_returns_equation():
    result = apparent_molar_volume(0.1, 1.02, 0.998, 58.44)
    assert "equation" in result


def test_debye_huckel_is_negative_for_positive_ionic_strength():
    result = debye_huckel_volume(0.1)
    assert result["debye_huckel_term"] < 0

