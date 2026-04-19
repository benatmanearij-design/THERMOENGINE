import { useState } from "react";

import { api } from "../api/client";
import EquationBlock from "../components/EquationBlock";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import ResultCard from "../components/ResultCard";

export default function VolumePage() {
  const [apparentForm, setApparentForm] = useState({
    concentration_mol_l: 0.1,
    density_solution_g_ml: 1.02,
    density_solvent_g_ml: 0.998,
    molar_mass_g_mol: 58.44,
  });
  const [dhForm, setDhForm] = useState({ ionic_strength: 0.1, a_phi: 1.0, b: 1.2 });
  const [apparentResult, setApparentResult] = useState(null);
  const [dhResult, setDhResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      const [apparentData, dhData] = await Promise.all([
        api("/volume/apparent", { method: "POST", body: JSON.stringify(apparentForm) }),
        api("/volume/debye-huckel", { method: "POST", body: JSON.stringify(dhForm) }),
      ]);
      setApparentResult(apparentData);
      setDhResult(dhData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div className="panel space-y-4 p-6">
        <h3 className="text-2xl font-bold text-white">Volumetric Properties</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <FormField label="Concentration (mol/L)">
            <input className="field" type="number" step="0.01" value={apparentForm.concentration_mol_l} onChange={(event) => setApparentForm({ ...apparentForm, concentration_mol_l: Number(event.target.value) })} />
          </FormField>
          <FormField label="Solution density (g/mL)">
            <input className="field" type="number" step="0.001" value={apparentForm.density_solution_g_ml} onChange={(event) => setApparentForm({ ...apparentForm, density_solution_g_ml: Number(event.target.value) })} />
          </FormField>
          <FormField label="Solvent density (g/mL)">
            <input className="field" type="number" step="0.001" value={apparentForm.density_solvent_g_ml} onChange={(event) => setApparentForm({ ...apparentForm, density_solvent_g_ml: Number(event.target.value) })} />
          </FormField>
          <FormField label="Molar mass (g/mol)">
            <input className="field" type="number" step="0.01" value={apparentForm.molar_mass_g_mol} onChange={(event) => setApparentForm({ ...apparentForm, molar_mass_g_mol: Number(event.target.value) })} />
          </FormField>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <FormField label="Ionic strength">
            <input className="field" type="number" step="0.01" value={dhForm.ionic_strength} onChange={(event) => setDhForm({ ...dhForm, ionic_strength: Number(event.target.value) })} />
          </FormField>
          <FormField label="Aphi">
            <input className="field" type="number" step="0.01" value={dhForm.a_phi} onChange={(event) => setDhForm({ ...dhForm, a_phi: Number(event.target.value) })} />
          </FormField>
          <FormField label="b">
            <input className="field" type="number" step="0.01" value={dhForm.b} onChange={(event) => setDhForm({ ...dhForm, b: Number(event.target.value) })} />
          </FormField>
        </div>
        <button type="button" className="btn-primary w-full" onClick={handleRun}>Calculate volumetric properties</button>
        {loading ? <LoadingSpinner label="Computing volumetric properties..." /> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>

      <div className="space-y-6">
        <ResultCard title="Apparent molar volume">
          {apparentResult ? (
            <>
              <p>Value: <span className="font-semibold text-white">{apparentResult.apparent_molar_volume_cm3_mol.toFixed(5)} cm3/mol</span></p>
              <EquationBlock equation={apparentResult.equation} />
            </>
          ) : <p>Run the calculation to view the apparent molar volume.</p>}
        </ResultCard>
        <ResultCard title="Debye-Huckel electrolyte term">
          {dhResult ? (
            <>
              <p>Value: <span className="font-semibold text-white">{dhResult.debye_huckel_term.toFixed(5)}</span></p>
              <EquationBlock equation={dhResult.equation} />
            </>
          ) : <p>Run the calculation to view the Debye-Huckel contribution.</p>}
        </ResultCard>
      </div>
    </div>
  );
}

