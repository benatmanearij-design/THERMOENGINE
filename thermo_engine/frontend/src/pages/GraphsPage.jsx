import { useEffect, useState } from "react";

import { api } from "../api/client";
import ChartCard from "../components/ChartCard";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";
import { downloadCsv } from "../utils/export";

export default function GraphsPage({ components }) {
  const [form, setForm] = useState({
    component1: "",
    component2: "",
    temperature_c: 78,
    activityModel: "NRTL",
    eosModel: "PR",
  });
  const [graphs, setGraphs] = useState(null);
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
      const payload = {
        temperature_c: Number(form.temperature_c),
        component_ids: [Number(form.component1), Number(form.component2)],
        activity_model: form.activityModel,
        eos_model: form.eosModel,
      };
      const [gamma, pxy, yx] = await Promise.all([
        api("/graphs/gamma", { method: "POST", body: JSON.stringify(payload) }),
        api("/graphs/pxy", { method: "POST", body: JSON.stringify(payload) }),
        api("/graphs/yx", { method: "POST", body: JSON.stringify(payload) }),
      ]);
      setGraphs({ gamma, pxy, yx });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const csvRows = graphs?.pxy?.x1.map((x1, index) => ({
    x1,
    y1: graphs.pxy.y1[index],
    pressure_bar: graphs.pxy.pressure_bar[index],
  })) || [];

  return (
    <div className="space-y-6">
      <div className="panel grid gap-4 p-6 md:grid-cols-5">
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
        <FormField label="Temperature (deg C)">
          <input className="field" type="number" value={form.temperature_c} onChange={(event) => setForm({ ...form, temperature_c: event.target.value })} />
        </FormField>
        <FormField label="Activity model">
          <select className="field" value={form.activityModel} onChange={(event) => setForm({ ...form, activityModel: event.target.value })}>
            <option value="NRTL">NRTL</option>
            <option value="UNIQUAC">UNIQUAC</option>
          </select>
        </FormField>
        <div className="flex items-end gap-3">
          <button type="button" className="btn-primary flex-1" onClick={handleRun}>Generate charts</button>
          {csvRows.length ? <button type="button" className="btn-secondary" onClick={() => downloadCsv("pxy_diagram.csv", csvRows)}>CSV</button> : null}
        </div>
      </div>
      {loading ? <LoadingSpinner label="Generating interactive plots..." /> : null}
      {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      {graphs ? (
        <div className="grid gap-6 xl:grid-cols-2">
          <ChartCard
            title="gamma vs composition"
            subtitle="Activity coefficients across liquid composition."
            data={[
              { x: graphs.gamma.x1, y: graphs.gamma.gamma1, type: "scatter", mode: "lines", name: "gamma1", line: { color: "#818cf8", width: 3 } },
              { x: graphs.gamma.x1, y: graphs.gamma.gamma2, type: "scatter", mode: "lines", name: "gamma2", line: { color: "#22d3ee", width: 3 } },
            ]}
            layout={{ xaxis: { title: "x1" }, yaxis: { title: "gamma" } }}
          />
          <ChartCard
            title="P-x-y diagram"
            subtitle="Bubble pressure versus liquid and vapor compositions."
            data={[
              { x: graphs.pxy.x1, y: graphs.pxy.pressure_bar, type: "scatter", mode: "lines", name: "P(x)", line: { color: "#f59e0b", width: 3 } },
              { x: graphs.pxy.y1, y: graphs.pxy.pressure_bar, type: "scatter", mode: "lines", name: "P(y)", line: { color: "#38bdf8", width: 3 } },
            ]}
            layout={{ xaxis: { title: "Composition of component 1" }, yaxis: { title: "Pressure (bar)" } }}
          />
          <ChartCard
            title="y-x diagram"
            subtitle="Vapor composition as a function of liquid composition."
            data={[
              { x: graphs.yx.x1, y: graphs.yx.y1, type: "scatter", mode: "lines+markers", name: "y(x)", line: { color: "#34d399", width: 3 } },
              { x: [0, 1], y: [0, 1], type: "scatter", mode: "lines", name: "y = x", line: { dash: "dash", color: "#94a3b8" } },
            ]}
            layout={{ xaxis: { title: "x1" }, yaxis: { title: "y1" } }}
          />
        </div>
      ) : null}
    </div>
  );
}

