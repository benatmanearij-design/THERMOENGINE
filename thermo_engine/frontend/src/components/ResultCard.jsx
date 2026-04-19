export default function ResultCard({ title, children, actions }) {
  return (
    <div className="panel p-5">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        {actions}
      </div>
      <div className="space-y-3 text-sm text-slate-300">{children}</div>
    </div>
  );
}

