const METRIC_CONFIG = [
  { key: 'FES', label: 'Family Expansion Score', color: 'bg-violet-500', max: 1 },
  { key: 'GCR', label: 'Global Coverage Rate', color: 'bg-cyan-500', max: 1 },
  { key: 'MIV', label: 'Market Importance Value', color: 'bg-emerald-500', max: 1 },
];

const FamilyExpansionMeter = ({ metrics }) => {
  if (!metrics) return null;

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-4">Family Expansion Metrics</p>
      <div className="space-y-4">
        {METRIC_CONFIG.map(({ key, label, color }) => {
          const value = metrics[key] ?? 0;
          return (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-600 font-medium">{key}</span>
                <span className="text-slate-500">{label}</span>
                <span className="font-semibold text-slate-700">{(value * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className={`h-full ${color} rounded-full transition-all`}
                  style={{ width: `${value * 100}%` }}
                />
              </div>
            </div>
          );
        })}

        {/* averageFamilySize 별도 표시 */}
        {metrics.averageFamilySize != null && (
          <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-600 font-medium">Avg. Family Size</span>
            <span className="text-lg font-bold text-violet-700">{metrics.averageFamilySize.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FamilyExpansionMeter;
