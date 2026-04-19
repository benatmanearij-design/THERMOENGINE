import { useEffect, useState } from "react";

import { api } from "../api/client";
import ChartCard from "../components/ChartCard";
import EquationBlock from "../components/EquationBlock";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import ResultCard from "../components/ResultCard";

export default function AntoinePage({ components }) {
  const [form, setForm] = useState({ component_id: "", temperature_c: 78, start_c: 20, end_c: 120 });
  const [result, setResult] = useState(null);
  const [curve, setCurve] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (components[0] && !form.component_id) {
      setForm((current) => ({ ...current, component_id: String(components[0].id) }));
    }
  }, [components, form.component_id]);

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      const [pressure, graph] = await Promise.all([
        api("/antoine", { method: "POST", body: JSON.stringify({ component_id: Number(form.component_id), temperature_c: Number(form.temperature_c) }) }),
        api("/graphs/antoine", {
          method: "POST",
          body: JSON.stringify({
            component_id: Number(form.component_id),
            start_c: Number(form.start_c),
            end_c: Number(form.end_c),
          }),
        }),
      ]);
      setResult(pressure);
      setCurve(graph);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <div className="panel space-y-4 p-6">
        <h3 className="text-2xl font-bold text-white">Antoine Vapor Pressure</h3>
        <FormField label="Component">
          <select className="field" value={form.component_id} onChange={(event) => setForm({ ...form, component_id: event.target.value })}>
            {components.map((component) => (
              <option key={component.id} value={component.id}>{component.name}</option>
            ))}
          </select>
        </FormField>
        <FormField label="Temperature (deg C)">
          <input className="field" type="number" value={form.temperature_c} onChange={(event) => setForm({ ...form, temperature_c: event.target.value })} />
        </FormField>
        <div className="grid gap-4 md:grid-cols-2">
          <FormField label="Curve Start (deg C)">
            <input className="field" type="number" value={form.start_c} onChange={(event) => setForm({ ...form, start_c: event.target.value })} />
          </FormField>
          <FormField label="Curve End (deg C)">
            <input className="field" type="number" value={form.end_c} onChange={(event) => setForm({ ...form, end_c: event.target.value })} />
          </FormField>
        </div>
        <button type="button" className="btn-primary w-full" onClick={handleRun}>Calculate</button>
        {loading ? <LoadingSpinner label="Running Antoine calculation..." /> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>

      <div className="space-y-6">
        <ResultCard title="Result">
          {result ? (
            <>
              <p>Pressure: <span className="font-semibold text-white">{result.pressure.toFixed(5)} {result.unit}</span></p>
              <p>Temperature: <span className="font-semibold text-white">{result.temperature_c.toFixed(2)} deg C</span></p>
              <EquationBlock equation={result.equation} />
            </>
          ) : (
            <p>Run the calculation to display the saturation pressure.</p>
          )}
        </ResultCard>

        {curve ? (
          <ChartCard
            title="Psat vs Temperature"
            subtitle="Interactive Plotly chart with hover and zoom."
            data={[
              {
                x: curve.temperature_c,
                y: curve.pressure,
                type: "scatter",
                mode: "lines+markers",
                line: { color: "#38bdf8", width: 3 },
                marker: { color: "#818cf8" },
              },
            ]}
            layout={{ xaxis: { title: "Temperature (deg C)" }, yaxis: { title: `Pressure (${curve.unit})` } }}
          />
        ) : null}
      </div>
    </div>
  );
}

