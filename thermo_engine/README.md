# THERMO_ENGINE

**Author:** 

- ARIJ BENATEMNA
- THERMO_ENGINE Team

## Stack

- Backend: Python, Flask, NumPy, optional SciPy fallback
- Frontend: React, Vite, Tailwind CSS, Plotly.js
- Database: SQLite by default, designed to be extendable to MySQL later

## Folder Structure

```text
thermo_engine/
  backend/
    antoine.py
    pression.py
    fraction_vapeur.py
    volume.py
    graphe.py
    db.py
    app.py
    tests/
  frontend/
    src/
      components/
      pages/
      utils/
      api/
```

## Backend Setup

```bash
cd thermo_engine/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API will start on `http://127.0.0.1:9000`.

## Frontend Setup

```bash
cd thermo_engine/frontend
npm install
npm run dev
```

The frontend expects the backend on `http://127.0.0.1:9000`.

## Running Tests

```bash
cd thermo_engine/backend
pytest
```

## Example API Requests

### Antoine vapor pressure

```bash
curl -X POST http://127.0.0.1:9000/api/antoine ^
  -H "Content-Type: application/json" ^
  -d "{\"component_id\":1,\"temperature_c\":100}"
```

### Activity coefficient

```bash
curl -X POST http://127.0.0.1:9000/api/pressure/activity ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"NRTL\",\"temperature_c\":78,\"x\":[0.4,0.6],\"component_ids\":[2,1]}"
```

### Bubble pressure

```bash
curl -X POST http://127.0.0.1:9000/api/vle/bubble-pressure ^
  -H "Content-Type: application/json" ^
  -d "{\"temperature_c\":78,\"component_ids\":[2,1],\"x\":[0.5,0.5],\"activity_model\":\"NRTL\",\"eos_model\":\"PR\"}"
```

### Export CSV-ready results

```bash
curl -X POST http://127.0.0.1:9000/api/export/csv ^
  -H "Content-Type: application/json" ^
  -d "{\"filename\":\"bubble_results.csv\",\"rows\":[{\"x1\":0.1,\"pressure_bar\":0.52},{\"x1\":0.2,\"pressure_bar\":0.61}]}"
```

## Notes

- SciPy is optional at runtime. If it is installed, root-finding uses `scipy.optimize.brentq`; otherwise a robust bisection fallback is used.
- The seeded database includes water, ethanol, methanol, benzene, and acetone together with Antoine, NRTL, and UNIQUAC demonstration parameters.
- The EOS implementation supports Peng-Robinson and SRK fugacity coefficient calculations for binary educational workflows.

