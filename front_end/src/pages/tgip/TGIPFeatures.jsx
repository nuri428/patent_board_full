import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';

const FEATURES = {
  RTS: {
    name: 'RTS',
    label: 'Structural Maturity View',
    question: 'Where is this technology in maturity, and why not yet?',
    outputs: ['rts_score (0–1)', 'stage: Critical Bottleneck | Bottleneck | Closure', 'component scores: patent_volume, growth, classification_conf, citation_percentile', 'solution approaches (top-k, in compare mode)'],
    evidence: ['Representative patents (≤5)', 'IPC/CPC signatures', 'Snippets per section (problem/solution/claim)', 'Confidence and coverage indicators'],
    widgets: ['Maturity scale (segmented bar + pointer)', '"Why Not Yet" breakdown (component bars)', 'Options comparison table'],
    color: 'violet',
  },
  TPI: {
    name: 'TPI',
    label: 'Propagation View',
    question: 'Where is it spreading, how fast, and where does it converge?',
    outputs: ['semantic_propagation score', 'industry_flow matrix / top transitions', 'burst timeline (tipping points)', 'hidden lineage (kNN semantic neighbors)'],
    evidence: ['Top neighbor patents (semantic) + similarity', 'Citations (where available)', 'Industry mapping provenance'],
    widgets: ['Flow map (Sankey-like)', 'Timeline burst chart', 'Lineage strip (neighbors carousel)'],
    color: 'cyan',
  },
  FSS: {
    name: 'FSS',
    label: 'Strategic Pressure View',
    question: 'How strongly is the assignee defending globally (family-based signals)?',
    outputs: ['FES, GCR, MIV, SCI, TLT (+ definitions)', 'Family size + country coverage', 'Status normalization flags'],
    evidence: ['Family members list', 'Legal status normalized codes', 'Country coverage checklist'],
    widgets: ['Coverage map (country list/map)', 'Family expansion meter', 'Assignee leaderboard'],
    color: 'red',
  },
  WSD: {
    name: 'WSD',
    label: 'Opportunity Field View',
    question: 'Where are unsolved problem areas and untried combinations?',
    outputs: ['Problem clusters + density', 'Solution clusters + density', 'Gap candidates: (problem, solution) low-density pairs', 'Cross-industry analog matches', 'Gap classification: Data Gap vs True White-space'],
    evidence: ['Supporting patents per cluster', 'Extraction confidence / missingness indicators'],
    widgets: ['Heatmap (problem × solution density)', 'Gap list (ranked by gap score + confidence)', 'Analog transfer panel (industry A → B)'],
    color: 'emerald',
  },
};

const colorMap = {
  violet: { nav: 'text-violet-700 bg-violet-50 border-violet-200', badge: 'bg-violet-100 text-violet-700', border: 'border-violet-400' },
  cyan:   { nav: 'text-cyan-700 bg-cyan-50 border-cyan-200',       badge: 'bg-cyan-100 text-cyan-700',   border: 'border-cyan-400' },
  red:    { nav: 'text-red-700 bg-red-50 border-red-200',           badge: 'bg-red-100 text-red-700',     border: 'border-red-400' },
  emerald:{ nav: 'text-emerald-700 bg-emerald-50 border-emerald-200', badge: 'bg-emerald-100 text-emerald-700', border: 'border-emerald-400' },
};

const TGIPFeatures = () => {
  const { view: paramView } = useParams();
  const [activeView, setActiveView] = useState(paramView?.toUpperCase() ?? 'RTS');
  const feature = FEATURES[activeView] ?? FEATURES.RTS;
  const colors = colorMap[feature.color];

  return (
    <div className="flex min-h-screen">
      {/* 좌측 네비 */}
      <aside className="w-48 shrink-0 border-r border-slate-200 pt-8 px-4 space-y-1">
        {Object.values(FEATURES).map((f) => (
          <button
            key={f.name}
            onClick={() => setActiveView(f.name)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-semibold transition-all ${
              activeView === f.name
                ? `${colorMap[f.color].nav} border`
                : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            {f.name}
            <span className="block text-xs font-normal opacity-70 mt-0.5">{f.label.split(' ')[0]} {f.label.split(' ')[1]}</span>
          </button>
        ))}
      </aside>

      {/* 우측 콘텐츠 */}
      <main className="flex-1 max-w-3xl px-8 py-8 space-y-8">
        <div>
          <span className={`text-xs font-black tracking-widest px-2.5 py-1 rounded-full ${colors.badge}`}>{feature.name}</span>
          <h1 className="text-2xl font-bold text-slate-900 mt-3">{feature.label}</h1>
          <blockquote className={`mt-3 pl-4 border-l-4 ${colors.border} text-slate-600 italic`}>
            "{feature.question}"
          </blockquote>
        </div>

        <Section title="Core Outputs" items={feature.outputs} />
        <Section title="Evidence Package" items={feature.evidence} />
        <Section title="UI Widgets" items={feature.widgets} />

        <div className="pt-4">
          <Link
            to={`/app/tech/solid-state-battery`}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-lg hover:bg-slate-700 transition-colors"
          >
            Observe {feature.name} in Workspace →
          </Link>
        </div>
      </main>
    </div>
  );
};

const Section = ({ title, items }) => (
  <div>
    <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">{title}</h3>
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
          <span className="text-slate-300 mt-0.5">—</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  </div>
);

export default TGIPFeatures;
