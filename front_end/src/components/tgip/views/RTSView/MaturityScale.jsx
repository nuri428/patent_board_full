const stageColor = (stage) => {
  if (stage === 'Critical Bottleneck') return 'text-red-600 bg-red-50 border-red-200';
  if (stage === 'Bottleneck') return 'text-amber-600 bg-amber-50 border-amber-200';
  return 'text-emerald-600 bg-emerald-50 border-emerald-200';
};

const MaturityScale = ({ score, stage }) => {
  const pct = Math.round((score ?? 0) * 100);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-600">Structural Maturity Score</span>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${stageColor(stage)}`}>
          {stage}
        </span>
      </div>

      {/* 세그먼트 바 */}
      <div className="relative h-4 rounded-full overflow-hidden flex gap-0.5">
        <div className="flex-1 bg-red-200 rounded-l-full" />
        <div className="flex-1 bg-amber-200" />
        <div className="flex-1 bg-emerald-200 rounded-r-full" />
        {/* 포인터 */}
        <div
          className="absolute top-0 h-4 w-1 bg-slate-800 rounded-full shadow-md transition-all duration-500"
          style={{ left: `calc(${pct}% - 2px)` }}
        />
      </div>

      <div className="flex justify-between text-xs text-slate-400">
        <span>Critical Bottleneck</span>
        <span className="font-bold text-slate-700">{pct}%</span>
        <span>Closure</span>
      </div>
    </div>
  );
};

export default MaturityScale;
