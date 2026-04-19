import { useEffect, useState } from "react";

import { api } from "../api/client";
import EquationBlock from "../components/EquationBlock";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import ResultCard from "../components/ResultCard";

export default function ModelsPage({ components }) {
  const [form, setForm] = useState({
    component1: "",
    component2: "",
    x1: 0.5,
    temperature_c: 78,
    pressure_bar: 1.0,
    activityModel: "NRTL",
    eosModel: "PR",
    phase: "vapor",
  });
  const [activity, setActivity] = useState(null);
  const [fugacity, setFugacity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (components.length > 1 && !form.component1) {
      setForm((current) => ({
        ...current,
        component1: String(components[0].id),
        component2: String(components[1].id),
      }));
    }
  }, [components, form.component1]);

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      const composition = [Number(form.x1), 1 - Number(form.x1)];
      const component_ids = [Number(form.component1), Number(form.component2)];
      const [activityData, fugacityData] = await Promise.all([
        api("/pressure/activity", {
          method: "POST",
          body: JSON.stringify({
            model: form.activityModel,
            component_ids,
            x: composition,
            temperature_c: Number(form.temperature_c),
          }),
        }),
        api("/pressure/fugacity", {
          method: "POST",
          body: JSON.stringify({
            model: form.eosModel,
            component_ids,
            composition,
            temperature_c: Number(form.temperature_c),
            pressure_bar: Number(form.pressure_bar),
            phase: form.phase,
          }),
        }),
      ]);
      setActivity(activityData);
      setFugacity(fugacityData);
    } catch (err) {
      console.error("Failed to evaluate models:", err);
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
      <div className="panel space-y-4 p-6">
        <h3 className="text-2xl font-bold text-white">Activity and Fugacity Models</h3>
        <div className="grid gap-4 md:grid-cols-2">
          <FormField label="Component 1">
            <select className="field" value={form.component1} onChange={(event) => setForm({ ...form, component1: event.target.value })}>
              {components.map((component) => <option key={component.id} value={component.id}>{component.name}</option>)}
            </select>
          </FormField>
          <FormField label="Component 2">
            <select className="field" value={form.component2} onChange={(event) => setForm({ ...form, component2: event.target.value })}>
              {components.map((component) => <option key={component.id} value={component.id}>{component.name}</option>)}
            </select>
          </FormField>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <FormField label="Activity model">
            <select className="field" value={form.activityModel} onChange={(event) => setForm({ ...form, activityModel: event.target.value })}>
              <option value="NRTL">NRTL</option>
              <option value="UNIQUAC">UNIQUAC</option>
            </select>
          </FormField>
          <FormField label="EOS">
            <select className="field" value={form.eosModel} onChange={(event) => setForm({ ...form, eosModel: event.target.value })}>
              <option value="PR">Peng-Robinson</option>
              <option value="SRK">SRK</option>
            </select>
          </FormField>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <FormField label="x1">
            <input className="field" type="number" min="0" max="1" step="0.01" value={form.x1} onChange={(event) => setForm({ ...form, x1: event.target.value })} />
          </FormField>
          <FormField label="Temperature (deg C)">
            <input className="field" type="number" value={form.temperature_c} onChange={(event) => setForm({ ...form, temperature_c: event.target.value })} />
          </FormField>
          <FormField label="Pressure (bar)">
            <input className="field" type="number" step="0.01" value={form.pressure_bar} onChange={(event) => setForm({ ...form, pressure_bar: event.target.value })} />
          </FormField>
        </div>
        <FormField label="Phase for fugacity">
          <select className="field" value={form.phase} onChange={(event) => setForm({ ...form, phase: event.target.value })}>
            <option value="vapor">Vapor</option>
            <option value="liquid">Liquid</option>
          </select>
        </FormField>
        <button type="button" className="btn-primary w-full" onClick={handleRun}>Evaluate models</button>
        {loading ? <LoadingSpinner label="Evaluating thermodynamic models..." /> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <ResultCard title="Activity coefficients">
          {activity ? (
            <>
              <p>gamma1: <span className="font-semibold text-white">{activity.gamma[0].toFixed(5)}</span></p>
              <p>gamma2: <span className="font-semibold text-white">{activity.gamma[1].toFixed(5)}</span></p>
              <EquationBlock equation={activity.equation} />
            </>
          ) : <p>Run the model comparison to display gamma values.</p>}
        </ResultCard>

        <ResultCard title="Fugacity coefficients">
          {fugacity ? (
            <>
              <p>phi1: <span className="font-semibold text-white">{fugacity.phi[0].toFixed(5)}</span></p>
              <p>phi2: <span className="font-semibold text-white">{fugacity.phi[1].toFixed(5)}</span></p>
              <p>Compressibility Z: <span className="font-semibold text-white">{fugacity.compressibility.toFixed(5)}</span></p>
              <EquationBlock equation={fugacity.equation} />
            </>
          ) : <p>Run the model comparison to display phi values.</p>}
        </ResultCard>
      </div>
    </div>
  );
}

