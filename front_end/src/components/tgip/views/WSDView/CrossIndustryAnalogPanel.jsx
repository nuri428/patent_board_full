const CrossIndustryAnalogPanel = ({ analogs }) => {
  if (!analogs?.length) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-4">Cross-Industry Analogs</p>
      <div className="space-y-3">
        {analogs.map((item, idx) => (
          <div key={idx} className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-lg p-3">
            <div className="shrink-0 text-xs font-semibold text-violet-700 bg-violet-50 border border-violet-200 rounded px-2 py-1">
              {item.sourceIndustry}
            </div>
            <div className="text-slate-400 text-sm shrink-0">→</div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-500 mb-0.5">Target Problem</p>
              <p className="text-sm text-slate-700 font-medium truncate">{item.targetProblem}</p>
            </div>
            <div className="text-slate-400 text-sm shrink-0">→</div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-slate-500 mb-0.5">Analogy</p>
              <p className="text-sm text-slate-700 truncate">{item.analogy}</p>
            </div>
            <div className="shrink-0 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-2 py-1">
              {(item.similarity * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CrossIndustryAnalogPanel;
