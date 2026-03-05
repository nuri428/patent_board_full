const ConfidenceBadge = ({ score }) => {
  const pct = Math.round((score ?? 0) * 100);
  const color = pct >= 80 ? 'bg-emerald-100 text-emerald-700' :
                pct >= 60 ? 'bg-amber-100 text-amber-700' :
                            'bg-red-100 text-red-700';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {pct}% confidence
    </span>
  );
};

export default ConfidenceBadge;
