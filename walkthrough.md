# THERMO_ENGINE Complete Web Application

The THERMO_ENGINE web application has been successfully updated and configured to meet your production requirements.

Since the core scaffolding and algorithms were previously implemented and placed in your `thermo_engine` workspace, the final adjustments have been made to satisfy your specific backend criteria (Port 9000 + Logging & Error handling), and the React setup has been successfully linked.

---

## 1 & 2. Codebase Overview

Your complete codebase is integrated and ready. 

- **Backend Location**: `c:\Users\MOUZDAHIR ISMAIL\Downloads\THERMOENGINE\thermo_engine\backend\`
- **Frontend Location**: `c:\Users\MOUZDAHIR ISMAIL\Downloads\THERMOENGINE\thermo_engine\frontend\`

> [!NOTE] 
> The backend server port has been changed to `9000` (in `app.py`), and the frontend configuration (in `src/api/client.js`) has been similarly updated to point precisely to `http://127.0.0.1:9000/api`. Moreover, complete request and error logging was injected into your Flask API decorators.

## 3. Folder Structure

Here is the modular and professional structure of your project:

```text
thermo_engine/
│
├── frontend/                     # React + Tailwind CSS Application
│   ├── package.json              # Frontend dependencies
│   ├── vite.config.js            # Build configuration
│   ├── tailwind.config.js        # Design framework configuration
│   └── src/
│       ├── api/
│       │   └── client.js         # Axios/Fetch client -> mapped to port 9000
│       ├── components/           # Reusable UI items (Topbar, Sidebar...)
│       ├── pages/                # Screens (Dashboard, VLE, Volume, etc.)
│       ├── utils/                # Frontend helpers
│       ├── App.jsx               # Navigation router root
│       ├── main.jsx              # Application entrypoint
│       └── index.css             # Tailwind base & global styles
│
└── backend/                      # Python Flask REST API
    ├── app.py                    # Root API endpoints + logging + port 9000
    ├── db.py                     # SQLite interface for models
    ├── antoine.py                # Vapor pressure calculations
    ├── fraction_vapeur.py        # VLE simulation strategies (gamma-phi, phi-phi)
    ├── pression.py               # Activity and fugacity calculations
    ├── volume.py                 # Volumetric properties
    ├── graphe.py                 # Plotly data generators
    └── thermo_engine.sqlite3     # SQLite persistent database instance
```

## 4. How to Run Instructions

### Starting the Backend Application
1. Open a new terminal.
2. Navigate to the backend directory:
   ```bash
   cd "C:\Users\MOUZDAHIR ISMAIL\Downloads\THERMOENGINE\thermo_engine\backend"
   ```
3. Activate your virtual environment if one is used, then run:
   ```bash
   python app.py
   ```
4. The server will start on `http://127.0.0.1:9000`. You will see incoming requests actively logged in this terminal.

### Starting the Frontend Application
1. Open a second new terminal.
2. Navigate to the frontend directory:
   ```bash
   cd "C:\Users\MOUZDAHIR ISMAIL\Downloads\THERMOENGINE\thermo_engine\frontend"
   ```
3. Install frontend dependencies (only necessary the first time):
   ```bash
   npm install
   ```
4. Start the development server using Vite:
   ```bash
   npm run dev
   ```
5. It should tell you a local port to connect to (usually `http://localhost:5173/`). Hold `CTRL` and click the URL to open your browser!

---

## 5. Example API Requests

Here are examples showing how to interact with the Python backend directly using `curl`, in case you want to export data or hit the backend programmatically:

#### A. Health Check & Root Base
```bash
curl -X GET http://127.0.0.1:9000/
# Expected JSON: {"message": "THERMO ENGINE API is running"}
```

#### B. Antoine Calculation (Vapor Pressure)
```bash
curl -X POST http://127.0.0.1:9000/api/antoine \
  -H "Content-Type: application/json" \
  -d '{"component_id": 1, "temperature_c": 50}'
# Expected JSON: {"vapor_pressure_bar": 1.2, "component": "..."} 
```

#### C. Activity Coefficients (NRTL)
```bash
curl -X POST http://127.0.0.1:9000/api/pressure/activity \
  -H "Content-Type: application/json" \
  -d '{"model": "NRTL", "x": [0.3, 0.7], "temperature_c": 100, "component_ids": [1, 2]}'
# Returns the computed activities for the specified blend.
```

> [!TIP]
> Since the frontend is completely hooked up via `client.js`, you do not need to construct these queries manually. Navigating to the **Activity Models** or **VLE Simulation** pages in React will collect form data and invoke these exact endpoints automatically!
