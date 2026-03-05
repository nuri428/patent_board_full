const gapBadgeColor = (score) => {
  if (score >= 0.8) return 'bg-emerald-100 text-emerald-700 border-emerald-200';
  if (score >= 0.6) return 'bg-cyan-100 text-cyan-700 border-cyan-200';
  return 'bg-slate-100 text-slate-600 border-slate-200';
};

const GapCandidatesList = ({ candidates }) => {
  if (!candidates?.length) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-4">Gap Candidates</p>
      <div className="space-y-3">
        {candidates.map((gap, idx) => (
          <div key={gap.id} className="border border-slate-200 rounded-lg p-4 bg-slate-50">
            <div className="flex items-start gap-3">
              <span className="text-xs text-slate-400 font-mono mt-0.5 shrink-0">#{idx + 1}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-2">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${gapBadgeColor(gap.gapScore)}`}>
                    Gap {(gap.gapScore * 100).toFixed(0)}%
                  </span>
                  <span className="text-xs text-slate-400">
                    confidence {(gap.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-0.5">Problem Area</p>
                    <p className="text-slate-700">{gap.problem}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-slate-500 mb-0.5">Solution Candidate</p>
                    <p className="text-slate-700">{gap.solution}</p>
                  </div>
                </div>
                {/* 신뢰도 진행바 */}
                <div className="mt-2">
                  <div className="h-1 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-violet-400 rounded-full"
                      style={{ width: `${gap.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GapCandidatesList;
