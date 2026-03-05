import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const VIEWS = [
  { id: 'RTS', name: 'RTS', label: 'Structural Maturity', desc: 'Observed structural maturity and bottleneck detection', color: 'bg-violet-50 border-violet-200 text-violet-700' },
  { id: 'TPI', name: 'TPI', label: 'Propagation', desc: 'Technology propagation and cross-industry diffusion', color: 'bg-cyan-50 border-cyan-200 text-cyan-700' },
  { id: 'FSS', name: 'FSS', label: 'Strategic Pressure', desc: 'Strategic pressure from patent family expansion', color: 'bg-red-50 border-red-200 text-red-700' },
  { id: 'WSD', name: 'WSD', label: 'Opportunity Field', desc: 'Opportunity fields and unresolved problem space', color: 'bg-emerald-50 border-emerald-200 text-emerald-700' },
];

const PIPELINE = [
  { step: '1', name: 'Data Ingestion', desc: 'Patent datasets collected from KR (KIPRIS) and US (Google Patents), normalized into a unified schema.' },
  { step: '2', name: 'Semantic Indexing', desc: 'Patent sections segmented and indexed using keyword search and vector embeddings.' },
  { step: '3', name: 'Knowledge Graph', desc: 'Entities including patents, applicants, technologies, problems and solutions mapped into a graph structure.' },
  { step: '4', name: 'Feature Extraction', desc: 'Technology signals extracted including problem-solution pairs, classification signatures, and semantic similarity.' },
  { step: '5', name: 'Analytical Metrics', desc: 'Four analytical metrics computed: RTS (maturity), TPI (propagation), FSS (strategic signals), WSD (opportunity).' },
  { step: '6', name: 'Evidence Packaging', desc: 'All outputs linked to traceable evidence packages including representative patents and IPC signatures.' },
];

const TGIPOverview = () => (
  <div className="text-slate-800">
    {/* Hero */}
    <section className="max-w-4xl mx-auto px-6 py-20 text-center">
      <h1 className="text-5xl font-black tracking-tight text-slate-900 mb-4">
        TGIP
      </h1>
      <p className="text-xl text-slate-600 mb-2 font-medium">
        Technology Geo-Intelligence Platform
      </p>
      <p className="text-slate-500 max-w-2xl mx-auto mb-8 leading-relaxed">
        Observe technology ecosystems through multiple analytical viewpoints.
        TGIP analyzes the same technology object from four complementary observation viewpoints —
        structural maturity, propagation dynamics, strategic pressure, and opportunity fields.
      </p>
      <p className="text-sm text-slate-400 italic mb-8">
        Rather than producing direct decisions, TGIP provides evidence-based observational signals
        to support expert judgement.
      </p>
      <div className="flex gap-3 justify-center">
        <Link
          to="/app/tech/solid-state-battery"
          className="inline-flex items-center gap-2 px-6 py-3 bg-violet-600 text-white font-semibold rounded-xl hover:bg-violet-700 transition-colors"
        >
          Open Demo <ArrowRight size={16} />
        </Link>
        <Link
          to="/features"
          className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
        >
          View Feature Specs
        </Link>
      </div>
    </section>

    {/* Multi-View Concept */}
    <section className="bg-slate-50 py-16">
      <div className="max-w-5xl mx-auto px-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">One Technology, Multiple Viewpoints</h2>
        <p className="text-slate-500 mb-8 max-w-2xl">
          A technology system can appear fundamentally different depending on the analytical viewpoint used to observe it.
          TGIP introduces four observation viewpoints.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {VIEWS.map((v) => (
            <div key={v.id} className={`rounded-xl border p-5 ${v.color}`}>
              <span className="text-xs font-black tracking-widest">{v.name}</span>
              <p className="text-sm font-semibold mt-1 mb-2">{v.label}</p>
              <p className="text-xs opacity-80 leading-relaxed">{v.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Landscape Concept */}
    <section className="py-16">
      <div className="max-w-5xl mx-auto px-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">Technology as a Geographic Landscape</h2>
        <p className="text-slate-500 max-w-3xl leading-relaxed">
          TGIP models the technology ecosystem as a geographic landscape.
          Some technologies form stable structural cores. Others propagate rapidly across industrial boundaries.
          Certain areas experience strong strategic pressure, while others remain unexplored opportunity zones.
          By observing these patterns simultaneously, TGIP enables analysts to understand technology
          structure, movement, influence, and opportunity.
        </p>
      </div>
    </section>

    {/* Pipeline */}
    <section className="bg-slate-50 py-16">
      <div className="max-w-5xl mx-auto px-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-8">How TGIP Produces Analytical Signals</h2>
        <div className="space-y-4">
          {PIPELINE.map((p) => (
            <div key={p.step} className="flex gap-5 items-start bg-white rounded-xl border border-slate-200 p-5">
              <span className="text-2xl font-black text-slate-200 shrink-0 w-8">{p.step}</span>
              <div>
                <p className="text-sm font-semibold text-slate-800">{p.name}</p>
                <p className="text-sm text-slate-500 mt-1 leading-relaxed">{p.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* CTA Footer */}
    <section className="py-16">
      <div className="max-w-3xl mx-auto px-6 text-center">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Start Observing</h2>
        <div className="flex gap-3 justify-center">
          <Link
            to="/app/tech/solid-state-battery"
            className="inline-flex items-center gap-2 px-6 py-3 bg-violet-600 text-white font-semibold rounded-xl hover:bg-violet-700 transition-colors"
          >
            Try the Workspace <ArrowRight size={16} />
          </Link>
          <Link
            to="/features"
            className="inline-flex items-center gap-2 px-6 py-3 border border-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
          >
            Read Feature Specs
          </Link>
        </div>
      </div>
    </section>
  </div>
);

export default TGIPOverview;
