const cards = [
  { title: "Antoine", text: "Calculate saturation pressure with transparent constants and curves." },
  { title: "Activity Models", text: "Compare NRTL and UNIQUAC behavior across composition." },
  { title: "VLE", text: "Run gamma-phi, phi-phi, and bubble point simulations." },
  { title: "Volume", text: "Estimate apparent molar volume and Debye-Huckel contributions." },
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="panel grid gap-6 overflow-hidden p-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-4">
          <p className="text-sm uppercase tracking-[0.28em] text-cyan-300">Scientific Computing Platform</p>
          <h3 className="max-w-3xl text-4xl font-extrabold leading-tight text-white">
            Professional thermodynamic modeling for non-ideal mixtures, designed for engineering education and rapid simulation.
          </h3>
          <p className="max-w-2xl text-slate-300">
            THERMO_ENGINE combines numerical methods, transparent equations, database-backed parameters, and interactive visualization in a single responsive interface.
          </p>
        </div>
        <div className="grid-glow rounded-[2rem] border border-white/10 bg-slate-950/40 p-6">
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-400">Core methods</p>
              <p className="text-xl font-bold text-white">NRTL, UNIQUAC, PR, SRK</p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Deliverables</p>
              <p className="text-xl font-bold text-white">API, charts, exports, molecule manager</p>
            </div>
            <div>
              <p className="text-sm text-slate-400">Primary use</p>
              <p className="text-xl font-bold text-white">Pedagogical and engineering exploration</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <div key={card.title} className="panel animate-floatin p-5">
            <p className="text-sm uppercase tracking-[0.2em] text-indigo-300">{card.title}</p>
            <p className="mt-4 text-sm text-slate-300">{card.text}</p>
          </div>
        ))}
      </section>
    </div>
  );
}

