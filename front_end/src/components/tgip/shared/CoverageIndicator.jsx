const CoverageIndicator = ({ coverage, lastRun, className = '' }) => {
  const pct = coverage != null ? Math.round(coverage * 100) : null;
  return (
    <div className={`text-xs text-slate-400 space-y-0.5 ${className}`}>
      {pct != null && (
        <div className="flex items-center gap-1.5">
          <div className="w-12 h-1 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-violet-400 rounded-full" style={{ width: `${pct}%` }} />
          </div>
          <span>{pct}%</span>
        </div>
      )}
      {lastRun && <p className="text-slate-300">Last: {lastRun}</p>}
    </div>
  );
};

export default CoverageIndicator;
