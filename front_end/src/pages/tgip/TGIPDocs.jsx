const DOC_SECTIONS = [
  {
    title: 'API Reference',
    items: [
      { name: 'POST /api/v1/tgip/analysis', desc: 'Run analysis on a technology object. Returns analysis_run_id and RTS/TPI/FSS/WSD results.' },
      { name: 'GET /api/v1/tgip/runs/:run_id', desc: 'Retrieve a specific analysis run with full evidence bundles.' },
      { name: 'GET /api/v1/tgip/technologies', desc: 'Search available technology objects by query.' },
    ],
  },
  {
    title: 'Glossary',
    items: [
      { name: 'RTS (Readiness-Tension-Structure)', desc: 'Structural maturity score (0–1) measuring patent volume, growth, classification confidence, and citation percentile.' },
      { name: 'TPI (Technology Propagation Index)', desc: 'Measures semantic propagation across industries, including diffusion speed and lineage connections.' },
      { name: 'FSS (Family Strategic Score)', desc: 'Evaluates patent family expansion signals: FES, GCR, MIV, SCI, TLT.' },
      { name: 'WSD (White-Space Detection)', desc: 'Identifies low-density (problem, solution) pairs and cross-industry analog transfer candidates.' },
      { name: 'analysis_run_id', desc: 'Unique identifier for each analysis execution. Links all output signals to their evidence packages.' },
      { name: 'IPC/CPC', desc: 'International/Cooperative Patent Classification codes used as structural technology signatures.' },
    ],
  },
  {
    title: 'Data Sources',
    items: [
      { name: 'KR — KIPRIS', desc: 'Korean Intellectual Property Rights Information Service. Source for Korean patent data.' },
      { name: 'US — Google Patents', desc: 'Google Patents Public Data. Source for USPTO patent data.' },
    ],
  },
];

const TGIPDocs = () => (
  <div className="max-w-4xl mx-auto px-6 py-16">
    <h1 className="text-3xl font-bold text-slate-900 mb-2">Documentation</h1>
    <p className="text-slate-500 mb-10">
      Technical reference for TGIP analytical signals, API endpoints, and terminology.
    </p>

    <div className="space-y-10">
      {DOC_SECTIONS.map((section) => (
        <div key={section.title}>
          <h2 className="text-lg font-bold text-slate-800 mb-4 pb-2 border-b border-slate-200">
            {section.title}
          </h2>
          <div className="space-y-4">
            {section.items.map((item) => (
              <div key={item.name} className="flex gap-4">
                <code className="text-sm font-mono text-violet-700 bg-violet-50 px-2 py-1 rounded h-fit shrink-0 max-w-xs break-all">
                  {item.name}
                </code>
                <p className="text-sm text-slate-600 leading-relaxed pt-1">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

export default TGIPDocs;
