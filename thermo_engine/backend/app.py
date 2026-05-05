from __future__ import annotations

import csv
import io
import logging
from pathlib import Path

from flask import Flask, Response, jsonify, request

try:
    from flask_cors import CORS
except Exception:  # pragma: no cover - fallback for environments without flask-cors installed
    def CORS(_app):  # type: ignore
        return None

from antoine import calculate_vapor_pressure
from db import (
    DuplicateMoleculeNameError,
    create_molecule,
    delete_molecule,
    get_parameter_snapshot,
    initialize_database,
    list_molecules,
    update_molecule,
)
from fraction_vapeur import bubble_point_pressure, bubble_point_temperature, gamma_phi_approach, phi_phi_approach
from graphe import Antoine_curve, gamma_vs_composition, pxy_diagram, yx_diagram
from pression import activity_coefficients, fugacity_coefficients
from volume import apparent_molar_volume, debye_huckel_volume


app = Flask(__name__)
CORS(app)

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
app.logger.setLevel(logging.INFO)

@app.before_request
def log_request_info():
    app.logger.info(f"Handling {request.method} request to {request.path}")

initialize_database()


def parse_json() -> dict:
    return request.get_json(force=True, silent=False) or {}
@app.get("/")
def index() -> Response:
    return jsonify({"message": "THERMO ENGINE API is running"})


@app.get("/api/health")
def health() -> Response:
    return jsonify({"status": "ok", "app": "THERMO_ENGINE"})


@app.get("/api/components")
def components() -> Response:
    return jsonify(list_molecules())


@app.get("/api/parameters")
def parameters() -> Response:
    return jsonify(get_parameter_snapshot())


@app.post("/api/antoine")
def antoine() -> Response:
    data = parse_json()
    return jsonify(
        calculate_vapor_pressure(
            component_id=int(data["component_id"]),
            temperature_c=float(data["temperature_c"]),
            unit=data.get("unit", "bar"),
        )
    )


@app.post("/api/pressure/activity")
def pressure_activity() -> Response:
    data = parse_json()
    result = activity_coefficients(
        model=data["model"],
        x=[float(value) for value in data["x"]],
        temperature_k=float(data["temperature_c"]) + 273.15,
        component_ids=[int(value) for value in data["component_ids"]],
        params=data.get("params"),
    )
    return jsonify(result)


@app.post("/api/pressure/fugacity")
def pressure_fugacity() -> Response:
    data = parse_json()
    result = fugacity_coefficients(
        eos_model=data["model"],
        temperature_k=float(data["temperature_c"]) + 273.15,
        pressure_bar=float(data["pressure_bar"]),
        composition=[float(value) for value in data["composition"]],
        component_ids=[int(value) for value in data["component_ids"]],
        phase=data.get("phase", "vapor"),
    )
    return jsonify(result)


@app.post("/api/vle/gamma-phi")
def vle_gamma_phi() -> Response:
    data = parse_json()
    result = gamma_phi_approach(
        temperature_c=float(data["temperature_c"]),
        component_ids=[int(value) for value in data["component_ids"]],
        x=[float(value) for value in data["x"]],
        activity_model=data.get("activity_model", "NRTL"),
        eos_model=data.get("eos_model", "PR"),
        pressure_guess_bar=float(data.get("pressure_guess_bar", 1.0)),
    )
    return jsonify(result)


@app.post("/api/vle/phi-phi")
def vle_phi_phi() -> Response:
    data = parse_json()
    result = phi_phi_approach(
        temperature_c=float(data["temperature_c"]),
        component_ids=[int(value) for value in data["component_ids"]],
        x=[float(value) for value in data["x"]],
        eos_model=data.get("eos_model", "PR"),
        pressure_guess_bar=float(data.get("pressure_guess_bar", 1.0)),
    )
    return jsonify(result)


@app.post("/api/vle/bubble-pressure")
def vle_bubble_pressure() -> Response:
    data = parse_json()
    result = bubble_point_pressure(
        temperature_c=float(data["temperature_c"]),
        component_ids=[int(value) for value in data["component_ids"]],
        x=[float(value) for value in data["x"]],
        activity_model=data.get("activity_model", "NRTL"),
        eos_model=data.get("eos_model", "PR"),
        approach=data.get("approach", "gamma-phi"),
    )
    return jsonify(result)


@app.post("/api/vle/bubble-temperature")
def vle_bubble_temperature() -> Response:
    data = parse_json()
    result = bubble_point_temperature(
        pressure_bar=float(data["pressure_bar"]),
        component_ids=[int(value) for value in data["component_ids"]],
        x=[float(value) for value in data["x"]],
        activity_model=data.get("activity_model", "NRTL"),
        eos_model=data.get("eos_model", "PR"),
        approach=data.get("approach", "gamma-phi"),
    )
    return jsonify(result)


@app.post("/api/volume/apparent")
def volume_apparent() -> Response:
    data = parse_json()
    return jsonify(
        apparent_molar_volume(
            concentration_mol_l=float(data["concentration_mol_l"]),
            density_solution_g_ml=float(data["density_solution_g_ml"]),
            density_solvent_g_ml=float(data["density_solvent_g_ml"]),
            molar_mass_g_mol=float(data["molar_mass_g_mol"]),
        )
    )


@app.post("/api/volume/debye-huckel")
def volume_debye() -> Response:
    data = parse_json()
    return jsonify(
        debye_huckel_volume(
            ionic_strength=float(data["ionic_strength"]),
            a_phi=float(data.get("a_phi", 1.0)),
            b=float(data.get("b", 1.2)),
        )
    )


@app.post("/api/graphs/antoine")
def graph_antoine() -> Response:
    data = parse_json()
    return jsonify(
        Antoine_curve(
            component_id=int(data["component_id"]),
            start_c=float(data.get("start_c", 20)),
            end_c=float(data.get("end_c", 120)),
            points=int(data.get("points", 40)),
        )
    )


@app.post("/api/graphs/gamma")
def graph_gamma() -> Response:
    data = parse_json()
    return jsonify(
        gamma_vs_composition(
            temperature_c=float(data["temperature_c"]),
            component_ids=[int(value) for value in data["component_ids"]],
            model=data.get("activity_model", "NRTL"),
            points=int(data.get("points", 31)),
        )
    )


@app.post("/api/graphs/pxy")
def graph_pxy() -> Response:
    data = parse_json()
    return jsonify(
        pxy_diagram(
            temperature_c=float(data["temperature_c"]),
            component_ids=[int(value) for value in data["component_ids"]],
            activity_model=data.get("activity_model", "NRTL"),
            eos_model=data.get("eos_model", "PR"),
            points=int(data.get("points", 31)),
        )
    )


@app.post("/api/graphs/yx")
def graph_yx() -> Response:
    data = parse_json()
    return jsonify(
        yx_diagram(
            temperature_c=float(data["temperature_c"]),
            component_ids=[int(value) for value in data["component_ids"]],
            activity_model=data.get("activity_model", "NRTL"),
            eos_model=data.get("eos_model", "PR"),
            points=int(data.get("points", 31)),
        )
    )


@app.post("/api/export/csv")
def export_csv() -> Response:
    data = parse_json()
    rows = data.get("rows", [])
    filename = Path(data.get("filename", "thermo_export.csv")).name
    if not rows:
        return jsonify({"message": "No rows provided"}), 400

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.route("/api/molecules", methods=["GET", "POST"])
def molecules() -> Response:
    if request.method == "GET":
        return jsonify(list_molecules())
    payload = parse_json()
    return jsonify(create_molecule(payload)), 201


@app.route("/api/molecules/<int:molecule_id>", methods=["PUT", "DELETE"])
def molecule_detail(molecule_id: int) -> Response:
    if request.method == "PUT":
        payload = parse_json()
        result = update_molecule(molecule_id, payload)
        if not result:
            return jsonify({"message": "Molecule not found"}), 404
        return jsonify(result)

    delete_molecule(molecule_id)
    return Response(status=204)


@app.errorhandler(Exception)
def handle_error(error: Exception) -> tuple[Response, int]:
    app.logger.error(f"Error processed: {str(error)}", exc_info=True)
    if isinstance(error, DuplicateMoleculeNameError):
        return jsonify({"status": "error", "message": str(error)}), 409
    return jsonify({"status": "error", "message": str(error)}), 400


if __name__ == "__main__":
    app.logger.info("Starting THERMO_ENGINE server on port 9000...")
    app.run(debug=True, port=9000)
