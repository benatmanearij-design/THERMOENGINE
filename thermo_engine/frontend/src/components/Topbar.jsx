export default function Topbar() {
  return (
    <header className="panel flex items-center justify-between gap-4 p-5">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-indigo-300">Universite Hassan 1er</p>
        <h2 className="mt-2 text-2xl font-bold text-white">Thermodynamic Modeling Workspace</h2>
      </div>
      <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-3 text-right">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Focus</p>
        <p className="text-sm text-slate-200">VLE, activity, fugacity, and data transparency</p>
      </div>
    </header>
  );
}

