import { useEffect, useMemo, useState } from "react";

import { api } from "../api/client";
import EquationBlock from "../components/EquationBlock";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import ResultCard from "../components/ResultCard";
import { downloadCsv } from "../utils/export";

export default function VlePage({ components }) {
  const [form, setForm] = useState({
    component1: "",
    component2: "",
    x1: 0.5,
    temperature_c: 78,
    pressure_bar: 1.01325,
    activityModel: "NRTL",
    eosModel: "PR",
    approach: "gamma-phi",
  });
  const [bubbleP, setBubbleP] = useState(null);
  const [bubbleT, setBubbleT] = useState(null);
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

  const componentIds = useMemo(
    () => [Number(form.component1), Number(form.component2)],
    [form.component1, form.component2]
  );

  async function handleRun() {
    setLoading(true);
    setError("");
    try {
      const x = [Number(form.x1), 1 - Number(form.x1)];
      const [pressureData, temperatureData] = await Promise.all([
        api("/vle/bubble-pressure", {
          method: "POST",
          body: JSON.stringify({
            temperature_c: Number(form.temperature_c),
            component_ids: componentIds,
            x,
            activity_model: form.activityModel,
            eos_model: form.eosModel,
            approach: form.approach,
          }),
        }),
        api("/vle/bubble-temperature", {
          method: "POST",
          body: JSON.stringify({
            pressure_bar: Number(form.pressure_bar),
            component_ids: componentIds,
            x,
            activity_model: form.activityModel,
            eos_model: form.eosModel,
            approach: form.approach,
          }),
        }),
      ]);
      setBubbleP(pressureData);
      setBubbleT(temperatureData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const exportRows = bubbleP ? [{ x1: Number(form.x1), pressure_bar: bubbleP.pressure_bar, y1: bubbleP.y[0], y2: bubbleP.y[1] }] : [];

  return (
    <div className="grid gap-6 xl:grid-cols-[0.94fr_1.06fr]">
      <div className="panel space-y-4 p-6">
        <h3 className="text-2xl font-bold text-white">Vapor-Liquid Equilibrium</h3>
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
          <FormField label="Approach">
            <select className="field" value={form.approach} onChange={(event) => setForm({ ...form, approach: event.target.value })}>
              <option value="gamma-phi">gamma-phi</option>
              <option value="phi-phi">phi-phi</option>
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
          <FormField label="x1 liquid">
            <input className="field" type="number" step="0.01" min="0" max="1" value={form.x1} onChange={(event) => setForm({ ...form, x1: event.target.value })} />
          </FormField>
          <FormField label="Temperature (deg C)">
            <input className="field" type="number" value={form.temperature_c} onChange={(event) => setForm({ ...form, temperature_c: event.target.value })} />
          </FormField>
          <FormField label="Pressure target (bar)">
            <input className="field" type="number" step="0.01" value={form.pressure_bar} onChange={(event) => setForm({ ...form, pressure_bar: event.target.value })} />
          </FormField>
        </div>
        <FormField label="Activity model">
          <select className="field" value={form.activityModel} onChange={(event) => setForm({ ...form, activityModel: event.target.value })}>
            <option value="NRTL">NRTL</option>
            <option value="UNIQUAC">UNIQUAC</option>
          </select>
        </FormField>
        <button type="button" className="btn-primary w-full" onClick={handleRun}>Run VLE simulation</button>
        {loading ? <LoadingSpinner label="Solving bubble point equations..." /> : null}
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>

      <div className="space-y-6">
        <ResultCard
          title="Bubble Pressure"
          actions={bubbleP ? <button type="button" className="btn-secondary" onClick={() => downloadCsv("bubble_pressure.csv", exportRows)}>Export CSV</button> : null}
        >
          {bubbleP ? (
            <>
              <p>Pressure: <span className="font-semibold text-white">{bubbleP.pressure_bar.toFixed(5)} bar</span></p>
              <p>y1: <span className="font-semibold text-white">{bubbleP.y[0].toFixed(5)}</span> | y2: <span className="font-semibold text-white">{bubbleP.y[1].toFixed(5)}</span></p>
              {bubbleP.gamma ? <p>gamma1: <span className="font-semibold text-white">{bubbleP.gamma[0].toFixed(5)}</span> | gamma2: <span className="font-semibold text-white">{bubbleP.gamma[1].toFixed(5)}</span></p> : null}
              {bubbleP.phi ? <p>phi1: <span className="font-semibold text-white">{bubbleP.phi[0].toFixed(5)}</span> | phi2: <span className="font-semibold text-white">{bubbleP.phi[1].toFixed(5)}</span></p> : null}
              {bubbleP.equations?.map((equation) => <EquationBlock key={equation} equation={equation} />)}
            </>
          ) : <p>Run the VLE calculation to display bubble pressure results.</p>}
        </ResultCard>

        <ResultCard title="Bubble Temperature">
          {bubbleT ? (
            <>
              <p>Temperature: <span className="font-semibold text-white">{bubbleT.temperature_c.toFixed(5)} deg C</span></p>
              <p>Target pressure: <span className="font-semibold text-white">{bubbleT.target_pressure_bar.toFixed(5)} bar</span></p>
              <p>y1: <span className="font-semibold text-white">{bubbleT.y[0].toFixed(5)}</span> | y2: <span className="font-semibold text-white">{bubbleT.y[1].toFixed(5)}</span></p>
            </>
          ) : <p>Run the VLE calculation to display bubble temperature results.</p>}
        </ResultCard>
      </div>
    </div>
  );
}

