import { Database, Droplets, FlaskConical, Gauge, Home, LineChart, MoonStar, Orbit } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/antoine", label: "Antoine", icon: Droplets },
  { to: "/models", label: "Activity & Fugacity", icon: FlaskConical },
  { to: "/vle", label: "VLE", icon: Orbit },
  { to: "/volume", label: "Volume", icon: Gauge },
  { to: "/graphs", label: "Graphs", icon: LineChart },
  { to: "/molecules", label: "Molecule DB", icon: Database },
];

export default function Sidebar({ darkMode, onToggleDarkMode }) {
  return (
    <aside className="panel flex h-full flex-col gap-6 p-5">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Scientific Suite</p>
        <h1 className="mt-2 text-2xl font-extrabold text-white">THERMO_ENGINE</h1>
        <p className="mt-2 text-sm text-slate-400">Model non-ideal mixtures with a focused engineering workflow.</p>
      </div>

      <nav className="space-y-2">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-2xl px-4 py-3 text-sm transition ${
                isActive ? "bg-indigo-500/20 text-white" : "text-slate-300 hover:bg-white/5"
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      <button type="button" onClick={onToggleDarkMode} className="btn-secondary mt-auto gap-2">
        <MoonStar className="h-4 w-4" />
        {darkMode ? "Dark Mode On" : "Enable Dark Mode"}
      </button>
    </aside>
  );
}

