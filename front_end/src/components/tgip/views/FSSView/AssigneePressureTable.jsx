const gcrBadge = (gcr) => {
  if (gcr >= 0.88) return 'bg-violet-100 text-violet-700 border-violet-200';
  if (gcr >= 0.75) return 'bg-cyan-100 text-cyan-700 border-cyan-200';
  return 'bg-slate-100 text-slate-600 border-slate-200';
};

const AssigneePressureTable = ({ leaderboard }) => {
  if (!leaderboard?.length) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-4">Assignee Pressure Leaderboard</p>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left text-xs font-semibold text-slate-500 pb-2 w-8">#</th>
              <th className="text-left text-xs font-semibold text-slate-500 pb-2">Assignee</th>
              <th className="text-right text-xs font-semibold text-slate-500 pb-2">Patent Families</th>
              <th className="text-right text-xs font-semibold text-slate-500 pb-2">GCR</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((item, idx) => (
              <tr key={idx} className="border-b border-slate-100 last:border-0">
                <td className="py-2.5 text-xs text-slate-400">{idx + 1}</td>
                <td className="py-2.5 font-medium text-slate-700">{item.name}</td>
                <td className="py-2.5 text-right text-slate-600">{item.familyCount.toLocaleString()}</td>
                <td className="py-2.5 text-right">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${gcrBadge(item.gcr)}`}>
                    {(item.gcr * 100).toFixed(0)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssigneePressureTable;
