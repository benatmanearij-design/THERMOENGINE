import { useEffect, useState } from "react";

import { api } from "../api/client";
import ChartCard from "../components/ChartCard";
import EquationBlock from "../components/EquationBlock";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import ResultCard from "../components/ResultCard";

const MMHG_TO_BAR = 0.001333223684;

function formatNumber(value, digits = 5) {
  return Number(value).toFixed(digits);
}

function calculateLocalPressure(component, temperatureC) {
  const pressureMmHg = 10 ** (component.antoine_a - component.antoine_b / (temperatureC + component.antoine_c));
  return {
    component_id: component.id,
    component_name: component.name,
    temperature_c: temperatureC,
    pressure: pressureMmHg * MMHG_TO_BAR,
    unit: "bar",
    equation: String.raw`\log_{10}(P^{sat}) = A - \frac{B}{T + C}`,
    constants: {
      A: component.antoine_a,
      B: component.antoine_b,
      C: component.antoine_c,
    },
  };
}

function calculateLocalCurve(component, startC, endC, points = 40) {
  const safePoints = Math.max(points, 2);
  const temperature_c = Array.from({ length: safePoints }, (_, index) => (
    startC + ((endC - startC) * index) / (safePoints - 1)
  ));
  const pressure = temperature_c.map((value) => calculateLocalPressure(component, value).pressure);
  return { temperature_c, pressure, unit: "bar" };
}

export default function AntoinePage({ components }) {
  const [form, setForm] = useState({ component_id: "", temperature_c: 78, start_c: 20, end_c: 120 });
  const [result, setResult] = useState(null);
  const [curve, setCurve] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedComponent = components.find((component) => String(component.id) === String(form.component_id));
  const constants = result?.constants;
  const substitutedExponent = constants
    ? constants.A - (constants.B / (result.temperature_c + constants.C))
    : null;
  const pressureMmHg = result ? result.pressure / MMHG_TO_BAR : null;

  useEffect(() => {
    if (components[0] && !form.component_id) {
      setForm((current) => ({ ...current, component_id: String(components[0].id) }));
    }
  }, [components, form.component_id]);

  async function handleRun() {
    const temperature = Number(form.temperature_c);
    const start = Number(form.start_c);
    const end = Number(form.end_c);

    if (!selectedComponent) {
      setError("Please select a component.");
      return;
    }

    if (Number.isNaN(temperature) || Number.isNaN(start) || Number.isNaN(end)) {
      setError("Please enter valid numeric values.");
      return;
    }

    if (end <= start) {
      setError("Curve end temperature must be greater than curve start temperature.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const [pressure, graph] = await Promise.all([
        api("/antoine", { method: "POST", body: JSON.stringify({ component_id: Number(form.component_id), temperature_c: temperature }) }),
        api("/graphs/antoine", {
          method: "POST",
          body: JSON.stringify({
            component_id: Number(form.component_id),
            start_c: start,
            end_c: end,
          }),
        }),
      ]);
      setResult(pressure);
      setCurve(graph);
    } catch (err) {
      const fallbackResult = calculateLocalPressure(selectedComponent, temperature);
      const fallbackCurve = calculateLocalCurve(selectedComponent, start, end);
      setResult(fallbackResult);
      setCurve(fallbackCurve);
      setError("Backend unavailable. Displaying a local Antoine result with the selected component constants.");
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
            {!components.length ? <option value="">No component available</option> : null}
            {components.map((component) => (
              <option key={component.id} value={component.id}>{component.name} ({component.formula})</option>
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
        {selectedComponent ? (
          <div className="rounded-2xl border border-cyan-400/20 bg-slate-950/30 p-4 text-sm text-slate-300">
            <p className="font-semibold text-white">{selectedComponent.name} ({selectedComponent.formula})</p>
            <p>Recommended Antoine range: {selectedComponent.t_min_c} to {selectedComponent.t_max_c} deg C</p>
          </div>
        ) : null}
      </div>

      <div className="space-y-6">
        <ResultCard title="Result">
          {result ? (
            <>
              <p>Component: <span className="font-semibold text-white">{result.component_name ?? selectedComponent?.name ?? "Unknown"}</span></p>
              <p>Pressure: <span className="font-semibold text-white">{result.pressure.toFixed(5)} {result.unit}</span></p>
              <p>Pressure (mmHg): <span className="font-semibold text-white">{formatNumber(pressureMmHg, 3)} mmHg</span></p>
              <p>Temperature: <span className="font-semibold text-white">{result.temperature_c.toFixed(2)} deg C</span></p>
              <EquationBlock equation={result.equation} />
              {constants ? (
                <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <p>Constants: <span className="font-semibold text-white">A = {formatNumber(constants.A, 5)}, B = {formatNumber(constants.B, 3)}, C = {formatNumber(constants.C, 3)}</span></p>
                  <p>Substitution: <span className="font-semibold text-white">log10(Psat) = {formatNumber(constants.A, 5)} - {formatNumber(constants.B, 3)} / ({formatNumber(result.temperature_c, 2)} + {formatNumber(constants.C, 3)})</span></p>
                  <p>Exponent value: <span className="font-semibold text-white">{formatNumber(substitutedExponent, 6)}</span></p>
                  <p>Calculation: <span className="font-semibold text-white">Psat = 10^{formatNumber(substitutedExponent, 6)} = {formatNumber(pressureMmHg, 3)} mmHg = {formatNumber(result.pressure, 5)} bar</span></p>
                </div>
              ) : null}
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
