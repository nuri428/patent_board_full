import { useTGIPStore } from '../../../store/tgipStore';

const VIEWS = [
  {
    id: 'RTS',
    name: 'RTS',
    label: 'Structural Maturity',
    color: 'border-violet-500 text-violet-700 bg-violet-50',
    dot: 'bg-violet-500',
    available: true,
  },
  {
    id: 'TPI',
    name: 'TPI',
    label: 'Propagation',
    color: 'border-cyan-500 text-cyan-700 bg-cyan-50',
    dot: 'bg-cyan-500',
    available: true,
  },
  {
    id: 'FSS',
    name: 'FSS',
    label: 'Strategic Pressure',
    color: 'border-red-500 text-red-700 bg-red-50',
    dot: 'bg-red-500',
    available: true,
  },
  {
    id: 'WSD',
    name: 'WSD',
    label: 'Opportunity Field',
    color: 'border-emerald-500 text-emerald-700 bg-emerald-50',
    dot: 'bg-emerald-500',
    available: true,
  },
];

const SidebarViewSelector = () => {
  const { selectedView, setView, results } = useTGIPStore();

  return (
    <aside className="w-52 shrink-0 bg-white border-r border-slate-200 flex flex-col py-4 gap-1">
      <p className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
        Viewpoints
      </p>
      {VIEWS.map((v) => {
        const isActive = selectedView === v.id;
        const hasData = !!results?.[v.id];

        return (
          <button
            key={v.id}
            onClick={() => v.available && setView(v.id)}
            disabled={!v.available}
            className={`
              mx-2 rounded-lg px-3 py-3 text-left transition-all
              ${isActive ? `border-l-4 ${v.color}` : 'border-l-4 border-transparent hover:bg-slate-50'}
              ${!v.available ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full shrink-0 ${hasData ? v.dot : 'bg-slate-300'}`} />
              <span className={`text-sm font-bold ${isActive ? '' : 'text-slate-700'}`}>{v.name}</span>
            </div>
            <p className={`text-xs mt-0.5 pl-4 ${isActive ? '' : 'text-slate-500'}`}>{v.label}</p>
          </button>
        );
      })}
    </aside>
  );
};

export default SidebarViewSelector;
