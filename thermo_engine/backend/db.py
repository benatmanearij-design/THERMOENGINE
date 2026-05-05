from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("THERMO_ENGINE_DB", BASE_DIR / "thermo_engine.sqlite3"))


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS molecules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    formula TEXT NOT NULL,
    tc REAL NOT NULL,
    pc_bar REAL NOT NULL,
    omega REAL NOT NULL,
    zc REAL DEFAULT 0.27
);

CREATE TABLE IF NOT EXISTS antoine_constants (
    molecule_id INTEGER PRIMARY KEY,
    a REAL NOT NULL,
    b REAL NOT NULL,
    c REAL NOT NULL,
    t_min_c REAL,
    t_max_c REAL,
    FOREIGN KEY(molecule_id) REFERENCES molecules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nrtl_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_1_id INTEGER NOT NULL,
    component_2_id INTEGER NOT NULL,
    a12 REAL NOT NULL,
    a21 REAL NOT NULL,
    alpha REAL NOT NULL DEFAULT 0.3,
    UNIQUE(component_1_id, component_2_id),
    FOREIGN KEY(component_1_id) REFERENCES molecules(id) ON DELETE CASCADE,
    FOREIGN KEY(component_2_id) REFERENCES molecules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS uniquac_parameters (
    molecule_id INTEGER PRIMARY KEY,
    r REAL NOT NULL,
    q REAL NOT NULL,
    FOREIGN KEY(molecule_id) REFERENCES molecules(id) ON DELETE CASCADE
);
"""


SEED_MOLECULES = [
    {"name": "Water", "formula": "H2O", "tc": 647.096, "pc_bar": 220.64, "omega": 0.344, "zc": 0.229, "antoine": (8.07131, 1730.63, 233.426, 1.0, 100.0), "uniquac": (0.92, 1.40)},
    {"name": "Ethanol", "formula": "C2H6O", "tc": 514.71, "pc_bar": 61.48, "omega": 0.644, "zc": 0.241, "antoine": (8.20417, 1642.89, 230.300, -10.0, 90.0), "uniquac": (2.1055, 1.972)},
    {"name": "Methanol", "formula": "CH4O", "tc": 512.60, "pc_bar": 80.90, "omega": 0.565, "zc": 0.224, "antoine": (8.08097, 1582.27, 239.726, 10.0, 90.0), "uniquac": (1.4311, 1.432)},
    {"name": "Benzene", "formula": "C6H6", "tc": 562.02, "pc_bar": 48.90, "omega": 0.212, "zc": 0.271, "antoine": (6.90565, 1211.033, 220.790, 7.0, 80.0), "uniquac": (3.1878, 2.400)},
    {"name": "Acetone", "formula": "C3H6O", "tc": 508.10, "pc_bar": 47.00, "omega": 0.304, "zc": 0.233, "antoine": (7.11714, 1210.595, 229.664, -10.0, 80.0), "uniquac": (2.5735, 2.336)},
    {"name": "Toluene", "formula": "C7H8", "tc": 591.75, "pc_bar": 41.06, "omega": 0.263, "zc": 0.264, "antoine": (6.95464, 1344.8, 219.48, 6.0, 126.0), "uniquac": (4.0026, 3.328)},
    {"name": "n-Hexane", "formula": "C6H14", "tc": 507.60, "pc_bar": 30.25, "omega": 0.301, "zc": 0.266, "antoine": (6.8763, 1171.53, 224.366, -20.0, 110.0), "uniquac": (3.856, 3.316)},
    {"name": "Isopropanol", "formula": "C3H8O", "tc": 508.30, "pc_bar": 47.64, "omega": 0.665, "zc": 0.248, "antoine": (8.11778, 1580.92, 219.61, 12.0, 89.0), "uniquac": (2.7791, 2.508)},
    {"name": "Chloroform", "formula": "CHCl3", "tc": 536.40, "pc_bar": 53.72, "omega": 0.221, "zc": 0.293, "antoine": (6.95465, 1170.966, 226.232, -20.0, 80.0), "uniquac": (3.0878, 2.52)},
]


SEED_NRTL = [
    ("Water", "Ethanol", 342.12, -95.10, 0.30),
    ("Water", "Methanol", 181.20, -54.40, 0.30),
    ("Benzene", "Acetone", 120.50, 95.70, 0.28),
    ("Water", "Isopropanol", 420.15, -110.30, 0.30),
    ("Toluene", "n-Hexane", 35.00, 25.00, 0.20),
]


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


class DuplicateMoleculeNameError(ValueError):
    pass


def initialize_database() -> None:
    connection = get_connection()
    try:
        connection.executescript(SCHEMA_SQL)
        seed_database(connection)
        connection.commit()
    finally:
        connection.close()


def seed_database(connection: sqlite3.Connection) -> None:
    existing_rows = connection.execute("SELECT id, name FROM molecules").fetchall()
    molecule_ids = {row["name"]: row["id"] for row in existing_rows}

    for item in SEED_MOLECULES:
        if item["name"] in molecule_ids:
            continue

        cursor = connection.execute(
            """
            INSERT INTO molecules (name, formula, tc, pc_bar, omega, zc)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item["name"], item["formula"], item["tc"], item["pc_bar"], item["omega"], item["zc"]),
        )
        molecule_ids[item["name"]] = cursor.lastrowid
        connection.execute(
            """
            INSERT INTO antoine_constants (molecule_id, a, b, c, t_min_c, t_max_c)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (molecule_ids[item["name"]], *item["antoine"]),
        )
        connection.execute(
            """
            INSERT INTO uniquac_parameters (molecule_id, r, q)
            VALUES (?, ?, ?)
            """,
            (molecule_ids[item["name"]], *item["uniquac"]),
        )

    for item in SEED_MOLECULES:
        molecule_id = molecule_ids[item["name"]]
        connection.execute(
            """
            INSERT OR IGNORE INTO antoine_constants (molecule_id, a, b, c, t_min_c, t_max_c)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (molecule_id, *item["antoine"]),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO uniquac_parameters (molecule_id, r, q)
            VALUES (?, ?, ?)
            """,
            (molecule_id, *item["uniquac"]),
        )

    existing_pairs = {
        (row["component_1_id"], row["component_2_id"])
        for row in connection.execute("SELECT component_1_id, component_2_id FROM nrtl_parameters").fetchall()
    }

    for comp1, comp2, a12, a21, alpha in SEED_NRTL:
        pair = (molecule_ids[comp1], molecule_ids[comp2])
        reverse_pair = (pair[1], pair[0])
        if pair in existing_pairs or reverse_pair in existing_pairs:
            continue
        connection.execute(
            """
            INSERT INTO nrtl_parameters (component_1_id, component_2_id, a12, a21, alpha)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pair[0], pair[1], a12, a21, alpha),
        )
        existing_pairs.add(pair)


def list_molecules() -> list[dict[str, Any]]:
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT
                m.*,
                a.a AS antoine_a,
                a.b AS antoine_b,
                a.c AS antoine_c,
                a.t_min_c AS t_min_c,
                a.t_max_c AS t_max_c,
                u.r AS uniquac_r,
                u.q AS uniquac_q
            FROM molecules m
            LEFT JOIN antoine_constants a ON a.molecule_id = m.id
            LEFT JOIN uniquac_parameters u ON u.molecule_id = m.id
            ORDER BY m.name
            """
        ).fetchall()
        return rows_to_dicts(rows)
    finally:
        connection.close()


def get_molecule(molecule_id: int) -> dict[str, Any] | None:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT
                m.*,
                a.a AS antoine_a,
                a.b AS antoine_b,
                a.c AS antoine_c,
                a.t_min_c AS t_min_c,
                a.t_max_c AS t_max_c,
                u.r AS uniquac_r,
                u.q AS uniquac_q
            FROM molecules m
            LEFT JOIN antoine_constants a ON a.molecule_id = m.id
            LEFT JOIN uniquac_parameters u ON u.molecule_id = m.id
            WHERE m.id = ?
            """,
            (molecule_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def get_molecule_by_name(name: str) -> dict[str, Any] | None:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT
                m.*,
                a.a AS antoine_a,
                a.b AS antoine_b,
                a.c AS antoine_c,
                a.t_min_c AS t_min_c,
                a.t_max_c AS t_max_c,
                u.r AS uniquac_r,
                u.q AS uniquac_q
            FROM molecules m
            LEFT JOIN antoine_constants a ON a.molecule_id = m.id
            LEFT JOIN uniquac_parameters u ON u.molecule_id = m.id
            WHERE lower(trim(m.name)) = lower(trim(?))
            """,
            (name,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def normalize_molecule_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["name"] = str(payload["name"]).strip()
    normalized["formula"] = str(payload["formula"]).strip()
    return normalized


def create_molecule(payload: dict[str, Any]) -> dict[str, Any]:
    payload = normalize_molecule_payload(payload)
    existing = get_molecule_by_name(payload["name"])
    if existing:
        raise DuplicateMoleculeNameError(f"Molecule '{payload['name']}' already exists.")

    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO molecules (name, formula, tc, pc_bar, omega, zc)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload["formula"],
                payload["tc"],
                payload["pc_bar"],
                payload["omega"],
                payload.get("zc", 0.27),
            ),
        )
        molecule_id = cursor.lastrowid
        connection.execute(
            """
            INSERT INTO antoine_constants (molecule_id, a, b, c, t_min_c, t_max_c)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                molecule_id,
                payload["antoine_a"],
                payload["antoine_b"],
                payload["antoine_c"],
                payload.get("t_min_c"),
                payload.get("t_max_c"),
            ),
        )
        connection.execute(
            """
            INSERT INTO uniquac_parameters (molecule_id, r, q)
            VALUES (?, ?, ?)
            """,
            (molecule_id, payload["uniquac_r"], payload["uniquac_q"]),
        )
        connection.commit()
        return get_molecule(molecule_id) or {}
    finally:
        connection.close()


def update_molecule(molecule_id: int, payload: dict[str, Any]) -> dict[str, Any] | None:
    payload = normalize_molecule_payload(payload)
    existing = get_molecule_by_name(payload["name"])
    if existing and existing["id"] != molecule_id:
        raise DuplicateMoleculeNameError(f"Molecule '{payload['name']}' already exists.")

    connection = get_connection()
    try:
        connection.execute(
            """
            UPDATE molecules
            SET name = ?, formula = ?, tc = ?, pc_bar = ?, omega = ?, zc = ?
            WHERE id = ?
            """,
            (
                payload["name"],
                payload["formula"],
                payload["tc"],
                payload["pc_bar"],
                payload["omega"],
                payload.get("zc", 0.27),
                molecule_id,
            ),
        )
        connection.execute(
            """
            UPDATE antoine_constants
            SET a = ?, b = ?, c = ?, t_min_c = ?, t_max_c = ?
            WHERE molecule_id = ?
            """,
            (
                payload["antoine_a"],
                payload["antoine_b"],
                payload["antoine_c"],
                payload.get("t_min_c"),
                payload.get("t_max_c"),
                molecule_id,
            ),
        )
        connection.execute(
            """
            UPDATE uniquac_parameters
            SET r = ?, q = ?
            WHERE molecule_id = ?
            """,
            (payload["uniquac_r"], payload["uniquac_q"], molecule_id),
        )
        connection.commit()
        return get_molecule(molecule_id)
    finally:
        connection.close()


def delete_molecule(molecule_id: int) -> None:
    connection = get_connection()
    try:
        connection.execute("DELETE FROM molecules WHERE id = ?", (molecule_id,))
        connection.commit()
    finally:
        connection.close()


def get_antoine_constants(molecule_id: int) -> dict[str, Any]:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM antoine_constants WHERE molecule_id = ?",
            (molecule_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"Antoine constants not found for molecule {molecule_id}")
        return dict(row)
    finally:
        connection.close()


def get_nrtl_pair(component_ids: list[int]) -> dict[str, Any]:
    first, second = component_ids
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT *
            FROM nrtl_parameters
            WHERE (component_1_id = ? AND component_2_id = ?)
               OR (component_1_id = ? AND component_2_id = ?)
            LIMIT 1
            """,
            (first, second, second, first),
        ).fetchone()
        if not row:
            raise ValueError(f"NRTL parameters not found for pair {component_ids}")

        params = dict(row)
        if params["component_1_id"] == second and params["component_2_id"] == first:
            return {"a12": params["a21"], "a21": params["a12"], "alpha": params["alpha"]}
        return {"a12": params["a12"], "a21": params["a21"], "alpha": params["alpha"]}
    finally:
        connection.close()


def get_uniquac_pair(component_ids: list[int]) -> dict[str, Any]:
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT molecule_id, r, q
            FROM uniquac_parameters
            WHERE molecule_id IN (?, ?)
            ORDER BY CASE molecule_id WHEN ? THEN 0 ELSE 1 END
            """,
            (component_ids[0], component_ids[1], component_ids[0]),
        ).fetchall()
        if len(rows) != 2:
            raise ValueError(f"UNIQUAC parameters not found for pair {component_ids}")
        return {
            "r": [rows[0]["r"], rows[1]["r"]],
            "q": [rows[0]["q"], rows[1]["q"]],
        }
    finally:
        connection.close()


def get_parameter_snapshot() -> dict[str, Any]:
    connection = get_connection()
    try:
        nrtl = rows_to_dicts(connection.execute("SELECT * FROM nrtl_parameters ORDER BY id").fetchall())
        uniquac = rows_to_dicts(connection.execute("SELECT * FROM uniquac_parameters ORDER BY molecule_id").fetchall())
        return {"nrtl": nrtl, "uniquac": uniquac}
    finally:
        connection.close()
