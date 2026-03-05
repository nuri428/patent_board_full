import { Link } from 'react-router-dom';

const TGIPAbout = () => (
  <div className="max-w-3xl mx-auto px-6 py-16">
    <h1 className="text-3xl font-bold text-slate-900 mb-2">About TGIP</h1>
    <p className="text-slate-500 mb-10 text-lg">
      Technology Geo-Intelligence Platform
    </p>

    <div className="space-y-8 text-slate-700 leading-relaxed">
      <section>
        <h2 className="text-lg font-bold text-slate-800 mb-3">What is TGIP?</h2>
        <p>
          TGIP is a multi-view technology observation system. Rather than producing direct
          recommendations, TGIP provides evidence-based observational signals derived from
          patent data across multiple analytical viewpoints.
        </p>
      </section>

      <section>
        <h2 className="text-lg font-bold text-slate-800 mb-3">Core Principles</h2>
        <ul className="space-y-2">
          {[
            ['Evidence First', 'All analytical signals are backed by traceable patent evidence.'],
            ['Decision Neutrality', 'TGIP provides observations, not recommendations or investment guidance.'],
            ['Multi-View Observation', 'The same technology object is analyzed through four complementary viewpoints.'],
            ['Structural Thinking', 'Focus on structure, propagation, strategic pressure, and opportunity fields.'],
          ].map(([title, desc]) => (
            <li key={title} className="flex gap-3">
              <span className="font-semibold text-slate-800 shrink-0">{title}:</span>
              <span className="text-slate-600">{desc}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="text-lg font-bold text-slate-800 mb-3">Data Sources</h2>
        <p>
          TGIP processes patent data from KR (KIPRIS) and US (Google Patents) jurisdictions.
          All analytical outputs are linked to specific patent identifiers and IPC/CPC signatures.
        </p>
      </section>

      <section className="pt-2">
        <Link
          to="/overview"
          className="inline-flex items-center gap-2 text-violet-600 font-semibold hover:underline"
        >
          Learn more about TGIP →
        </Link>
      </section>
    </div>
  </div>
);

export default TGIPAbout;
