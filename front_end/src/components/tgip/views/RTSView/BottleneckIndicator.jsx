const STAGE_CONFIG = {
  'Critical Bottleneck': {
    icon: '⚠',
    desc: 'Significant structural barriers are observed. Key components show low maturity signals.',
    color: 'bg-red-50 border-red-200 text-red-700',
  },
  'Bottleneck': {
    icon: '◈',
    desc: 'Moderate structural constraints observed. Progress signals present but bottlenecks remain.',
    color: 'bg-amber-50 border-amber-200 text-amber-700',
  },
  'Closure': {
    icon: '◉',
    desc: 'Structural maturity signals indicate convergence toward closure patterns.',
    color: 'bg-emerald-50 border-emerald-200 text-emerald-700',
  },
};

const BottleneckIndicator = ({ stage }) => {
  const config = STAGE_CONFIG[stage] ?? STAGE_CONFIG['Bottleneck'];
  return (
    <div className={`flex items-start gap-3 rounded-lg border p-4 ${config.color}`}>
      <span className="text-lg leading-none mt-0.5">{config.icon}</span>
      <div>
        <p className="text-sm font-semibold">{stage}</p>
        <p className="text-xs mt-1 opacity-80 leading-relaxed">{config.desc}</p>
      </div>
    </div>
  );
};

export default BottleneckIndicator;
