# backend/thermo_engine/equilibrium.py
from pure_props import get_psat
from activity_models import NRTL, UNIQUAC, UNIFAC

def bubble_point(T, comp_ids, x, model, params=None):

    if model == "NRTL":
        gamma = NRTL().get_gamma(x, T, params["a12"], params["a21"], params["alpha"])

    elif model == "UNIQUAC":
        gamma = UNIQUAC().get_gamma(x, params["r"], params["q"])

    elif model == "UNIFAC":
        gamma = UNIFAC().get_gamma(comp_ids, x, T)

    else:
        raise Exception("❌ Unknown model")

    P = 1.0

    for _ in range(50):
        P_new = 0

        for i in range(len(x)):
            Psat = get_psat(comp_ids[i], T)
            P_new += x[i] * gamma[i] * Psat

        if abs(P_new - P) < 1e-5:
            break

        P = P_new

    return P