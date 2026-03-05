const RunIdBadge = ({ runId, className = '' }) => {
  if (!runId) return null;
  const short = runId.length > 16 ? `${runId.slice(0, 16)}…` : runId;
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-mono text-slate-400 bg-slate-100 px-2 py-0.5 rounded ${className}`}>
      <span className="text-slate-300">#</span>{short}
    </span>
  );
};

export default RunIdBadge;
