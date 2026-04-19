import Plot from "react-plotly.js";

export default function ChartCard({ title, subtitle, data, layout }) {
  return (
    <div className="panel animate-floatin p-5">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-slate-400">{subtitle}</p>
      </div>
      <Plot
        data={data}
        layout={{
          paper_bgcolor: "rgba(0,0,0,0)",
          plot_bgcolor: "rgba(2,6,23,0.15)",
          font: { color: "#cbd5e1" },
          margin: { t: 16, r: 16, b: 48, l: 56 },
          ...layout,
        }}
        config={{ responsive: true, displaylogo: false }}
        style={{ width: "100%", height: "360px" }}
      />
    </div>
  );
}

