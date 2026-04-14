# backend/thermo_engine/pure_props.py
import math
from db import get_db

def get_psat(component_id, T):
    """
    Antoine equation
    T en °C
    Psat en bar
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT A, B, C FROM antoine WHERE component_id=%s",
        (component_id,)
    )

    result = cursor.fetchone()

    if not result:
        raise Exception(f"❌ Antoine params not found for component {component_id}")

    A, B, C = result

    cursor.close()
    db.close()

    Psat = 10 ** (A - B / (T + C))
    return Psat