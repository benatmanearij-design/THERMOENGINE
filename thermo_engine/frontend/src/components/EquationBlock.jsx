export default function EquationBlock({ title = "Equation", equation }) {
  return (
    <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-4">
      <p className="mb-2 text-xs uppercase tracking-[0.2em] text-cyan-300">{title}</p>
      <code className="font-mono text-sm text-slate-100">{equation}</code>
    </div>
  );
}

