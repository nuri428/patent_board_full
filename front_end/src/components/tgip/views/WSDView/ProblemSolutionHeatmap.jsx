import { useState } from 'react';

const cellColor = (value) => {
  const alpha = Math.max(0.08, value);
  return `rgba(124, 58, 237, ${alpha})`;
};

const cellTextColor = (value) => (value > 0.5 ? '#ffffff' : '#4c1d95');

const ProblemSolutionHeatmap = ({ matrix, problems, solutions }) => {
  const [tooltip, setTooltip] = useState(null);

  if (!matrix || !problems || !solutions) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-4">Problem × Solution Density Matrix</p>
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* 헤더 행 (솔루션 레이블) */}
          <div className="flex gap-1 mb-1 ml-36">
            {solutions.map((sol) => (
              <div
                key={sol.id}
                className="w-24 text-xs text-slate-500 text-center truncate px-1"
                title={sol.label}
              >
                {sol.label}
              </div>
            ))}
          </div>

          {/* 데이터 행 */}
          {problems.map((prob, i) => (
            <div key={prob.id} className="flex items-center gap-1 mb-1">
              {/* 문제 레이블 */}
              <div className="w-36 text-xs text-slate-600 text-right pr-2 truncate shrink-0" title={prob.label}>
                {prob.label}
              </div>
              {/* 셀들 */}
              {(matrix[i] || []).map((value, j) => (
                <div
                  key={j}
                  className="w-24 h-12 rounded flex items-center justify-center text-xs font-semibold cursor-default transition-transform hover:scale-105 relative"
                  style={{
                    backgroundColor: cellColor(value),
                    color: cellTextColor(value),
                  }}
                  onMouseEnter={() => setTooltip({ i, j, value, prob: prob.label, sol: solutions[j]?.label })}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {(value * 100).toFixed(0)}%
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* 툴팁 */}
      {tooltip && (
        <div className="mt-3 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg inline-block">
          <span className="font-medium">{tooltip.prob}</span>
          <span className="text-slate-400 mx-1">×</span>
          <span className="font-medium">{tooltip.sol}</span>
          <span className="text-slate-300 ml-2">density: {(tooltip.value * 100).toFixed(0)}%</span>
        </div>
      )}

      {/* 범례 */}
      <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
        <span>Low</span>
        <div className="flex gap-0.5">
          {[0.1, 0.3, 0.5, 0.7, 0.9].map((v) => (
            <div key={v} className="w-6 h-3 rounded-sm" style={{ backgroundColor: cellColor(v) }} />
          ))}
        </div>
        <span>High density</span>
      </div>
    </div>
  );
};

export default ProblemSolutionHeatmap;
