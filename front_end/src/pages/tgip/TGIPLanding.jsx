import { Link } from 'react-router-dom';

const VIEW_CARDS = [
  {
    id: 'RTS',
    title: 'Structural Maturity',
    desc: 'Measures how mature a technology\'s patent structure is — volume, growth, classification confidence, and citation strength.',
    color: 'border-violet-400 bg-violet-50',
    badge: 'bg-violet-100 text-violet-700',
    icon: '⬡',
  },
  {
    id: 'TPI',
    title: 'Propagation Dynamics',
    desc: 'Tracks how technology semantics spread across industries over time via citation and abstract clustering.',
    color: 'border-cyan-400 bg-cyan-50',
    badge: 'bg-cyan-100 text-cyan-700',
    icon: '⬡',
  },
  {
    id: 'FSS',
    title: 'Strategic Pressure',
    desc: 'Assesses filing strategy intensity — family expansion, geographic coverage, and assignee positioning.',
    color: 'border-red-400 bg-red-50',
    badge: 'bg-red-100 text-red-700',
    icon: '⬡',
  },
  {
    id: 'WSD',
    title: 'Opportunity Field',
    desc: 'Identifies white-space gaps between unsolved problems and underdeveloped solution clusters.',
    color: 'border-emerald-400 bg-emerald-50',
    badge: 'bg-emerald-100 text-emerald-700',
    icon: '⬡',
  },
];

const TRUST_ITEMS = [
  {
    title: 'Evidence-Based',
    desc: 'Every signal is derived directly from patent data — no opinion, no extrapolation.',
  },
  {
    title: 'Non-Prescriptive',
    desc: 'TGIP observes and surfaces patterns. It does not recommend actions or predict outcomes.',
  },
  {
    title: 'Transparent',
    desc: 'All scores include source patents, IPC codes, and confidence metrics for full auditability.',
  },
];

const TGIPLanding = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Hero */}
      <section className="min-h-[70vh] bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 flex flex-col items-center justify-center text-white px-6 py-20">
        <div className="max-w-3xl text-center">
          <span className="inline-block text-xs font-semibold tracking-widest text-violet-400 uppercase mb-4">
            Technology Geo-Intelligence Platform
          </span>
          <h1 className="text-4xl md:text-6xl font-black leading-tight tracking-tight mb-6">
            Observe Technology.<br />
            <span className="text-violet-400">Not Prescribe.</span>
          </h1>
          <p className="text-lg text-slate-300 mb-10 max-w-xl mx-auto leading-relaxed">
            TGIP analyzes patent signals across four observational lenses — structural maturity,
            propagation dynamics, strategic pressure, and opportunity fields.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/app/tech/solid-state-battery"
              className="px-8 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-semibold transition-colors shadow-lg shadow-violet-900/30"
            >
              Open Workspace →
            </Link>
            <Link
              to="/docs"
              className="px-8 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold transition-colors border border-white/20"
            >
              Read Docs
            </Link>
          </div>
        </div>
      </section>

      {/* 4-View Cards */}
      <section className="py-20 px-6 bg-slate-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-800 text-center mb-3">Four Observational Viewpoints</h2>
          <p className="text-slate-500 text-center mb-12 max-w-lg mx-auto">
            Each view reveals a different dimension of a technology's patent landscape.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {VIEW_CARDS.map((card) => (
              <div key={card.id} className={`rounded-2xl border-2 p-6 ${card.color}`}>
                <div className="flex items-center gap-3 mb-3">
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${card.badge}`}>{card.id}</span>
                  <span className="text-base font-semibold text-slate-800">{card.title}</span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-20 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-slate-800 text-center mb-12">Built on Observational Principles</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {TRUST_ITEMS.map((item) => (
              <div key={item.title} className="text-center">
                <div className="w-10 h-10 rounded-full bg-violet-100 flex items-center justify-center mx-auto mb-4">
                  <div className="w-3 h-3 rounded-full bg-violet-500" />
                </div>
                <h3 className="font-semibold text-slate-800 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="py-16 px-6 bg-slate-950 text-center">
        <div className="max-w-xl mx-auto">
          <h2 className="text-2xl font-bold text-white mb-4">Start Observing</h2>
          <p className="text-slate-400 mb-8 text-sm">
            Choose a technology and run a full four-view analysis in seconds.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/app/tech/solid-state-battery"
              className="px-8 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-xl font-semibold transition-colors"
            >
              Try the Workspace
            </Link>
            <Link
              to="/docs"
              className="px-8 py-3 bg-white/10 hover:bg-white/20 text-white rounded-xl font-semibold transition-colors"
            >
              View Docs
            </Link>
          </div>
          <p className="text-xs text-slate-600 mt-10">
            This system provides observational signals with evidence. It does not prescribe investment or strategic actions.
          </p>
        </div>
      </section>
    </div>
  );
};

export default TGIPLanding;
