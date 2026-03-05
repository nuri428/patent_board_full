import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const DEMOS = [
  { id: 'solid-state-battery', name: 'Solid State Battery', desc: '전고체 배터리 — 성숙도 분석 및 전략적 압력 관찰' },
  { id: 'perovskite-solar', name: 'Perovskite Solar Cell', desc: '페로브스카이트 태양전지 — 전파 패턴 및 기회 필드 관찰' },
];

const TGIPDemo = () => (
  <div className="max-w-3xl mx-auto px-6 py-16">
    <h1 className="text-3xl font-bold text-slate-900 mb-2">Demo</h1>
    <p className="text-slate-500 mb-8">
      Observe sample technologies through the TGIP multi-view workspace.
      All signals are based on sample analysis runs.
    </p>
    <div className="space-y-4">
      {DEMOS.map((d) => (
        <Link
          key={d.id}
          to={`/app/tech/${d.id}`}
          className="flex items-center justify-between p-5 bg-white border border-slate-200 rounded-xl hover:border-violet-300 hover:shadow-sm transition-all group"
        >
          <div>
            <p className="font-semibold text-slate-800">{d.name}</p>
            <p className="text-sm text-slate-500 mt-1">{d.desc}</p>
          </div>
          <ArrowRight size={18} className="text-slate-400 group-hover:text-violet-600 transition-colors" />
        </Link>
      ))}
    </div>
  </div>
);

export default TGIPDemo;
