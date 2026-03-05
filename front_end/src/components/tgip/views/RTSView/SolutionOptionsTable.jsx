const SolutionOptionsTable = ({ options }) => {
  if (!options?.length) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-3">Solution Approaches (observed)</p>
      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left px-4 py-2.5 text-slate-500 font-medium">Approach</th>
              <th className="text-right px-4 py-2.5 text-slate-500 font-medium">Patents</th>
              <th className="text-right px-4 py-2.5 text-slate-500 font-medium">Coverage</th>
              <th className="text-left px-4 py-2.5 text-slate-500 font-medium">Evidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {options.map((row, i) => (
              <tr key={i} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-2.5 font-medium text-slate-800">{row.approach}</td>
                <td className="px-4 py-2.5 text-right text-slate-600">{row.patents.toLocaleString()}</td>
                <td className="px-4 py-2.5 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-violet-500 rounded-full"
                        style={{ width: `${Math.round(row.coverage * 100)}%` }}
                      />
                    </div>
                    <span className="text-slate-600">{Math.round(row.coverage * 100)}%</span>
                  </div>
                </td>
                <td className="px-4 py-2.5 text-slate-400 font-mono text-xs">{row.evidence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SolutionOptionsTable;
