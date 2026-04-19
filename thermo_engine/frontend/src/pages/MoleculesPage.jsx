import { useMemo, useState } from "react";

import { api } from "../api/client";
import FormField from "../components/FormField";
import LoadingSpinner from "../components/LoadingSpinner";

const blankForm = {
  name: "",
  formula: "",
  tc: 500,
  pc_bar: 50,
  omega: 0.2,
  zc: 0.27,
  antoine_a: 8,
  antoine_b: 1500,
  antoine_c: 220,
  t_min_c: 0,
  t_max_c: 100,
  uniquac_r: 2.0,
  uniquac_q: 2.0,
};

export default function MoleculesPage({ components, reloadComponents }) {
  const [form, setForm] = useState(blankForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const total = useMemo(() => components.length, [components.length]);

  function startEdit(component) {
    setEditingId(component.id);
    setForm({
      name: component.name,
      formula: component.formula,
      tc: component.tc,
      pc_bar: component.pc_bar,
      omega: component.omega,
      zc: component.zc,
      antoine_a: component.antoine_a,
      antoine_b: component.antoine_b,
      antoine_c: component.antoine_c,
      t_min_c: component.t_min_c ?? 0,
      t_max_c: component.t_max_c ?? 100,
      uniquac_r: component.uniquac_r,
      uniquac_q: component.uniquac_q,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const method = editingId ? "PUT" : "POST";
      const path = editingId ? `/molecules/${editingId}` : "/molecules";
      await api(path, { method, body: JSON.stringify(form) });
      setForm(blankForm);
      setEditingId(null);
      await reloadComponents();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    setLoading(true);
    setError("");
    try {
      await api(`/molecules/${id}`, { method: "DELETE" });
      if (editingId === id) {
        setEditingId(null);
        setForm(blankForm);
      }
      await reloadComponents();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div className="panel p-6">
        <div className="mb-5 flex items-center justify-between gap-4">
          <div>
            <h3 className="text-2xl font-bold text-white">Molecule Database Manager</h3>
            <p className="text-sm text-slate-400">{total} molecules loaded in SQLite.</p>
          </div>
          {loading ? <LoadingSpinner label="Saving..." /> : null}
        </div>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          {Object.entries(form).map(([key, value]) => (
            <FormField key={key} label={key.replaceAll("_", " ")}>
              <input
                className="field"
                type={typeof value === "number" ? "number" : "text"}
                step={typeof value === "number" ? "0.01" : undefined}
                value={value}
                onChange={(event) =>
                  setForm({
                    ...form,
                    [key]: typeof value === "number" ? Number(event.target.value) : event.target.value,
                  })
                }
              />
            </FormField>
          ))}
          <div className="md:col-span-2 flex gap-3">
            <button type="submit" className="btn-primary flex-1">{editingId ? "Update molecule" : "Add molecule"}</button>
            <button type="button" className="btn-secondary" onClick={() => { setEditingId(null); setForm(blankForm); }}>Reset</button>
          </div>
        </form>
        {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
      </div>

      <div className="panel p-6">
        <h3 className="mb-4 text-2xl font-bold text-white">Stored Molecules</h3>
        <div className="space-y-3">
          {components.map((component) => (
            <div key={component.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-lg font-semibold text-white">{component.name}</p>
                  <p className="text-sm text-slate-400">{component.formula} • Tc {component.tc} K • Pc {component.pc_bar} bar</p>
                  <p className="mt-2 text-xs text-slate-500">Antoine: {component.antoine_a}, {component.antoine_b}, {component.antoine_c}</p>
                </div>
                <div className="flex gap-2">
                  <button type="button" className="btn-secondary" onClick={() => startEdit(component)}>Edit</button>
                  <button type="button" className="btn-secondary" onClick={() => handleDelete(component.id)}>Delete</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

