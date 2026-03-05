import { Download, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';
import TechnologySelector from '../Workspace/TechnologySelector';
import RunController from '../Workspace/RunController';
import { useTGIPStore } from '../../../store/tgipStore';

const VIEW_LABELS = { RTS: 'Structural', TPI: 'Propagation', FSS: 'Strategic', WSD: 'Opportunity' };

const TGIPHeader = ({ onExport, canExport }) => {
  const { selectedView, setView } = useTGIPStore();

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center gap-4 shrink-0">
      {/* 브랜드 */}
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-lg font-black text-slate-900 tracking-tight">TGIP</span>
      </div>

      <div className="w-px h-6 bg-slate-200 mx-1" />

      {/* 기술 셀렉터 */}
      <TechnologySelector />

      {/* 뷰 전환 */}
      <div className="hidden md:flex items-center gap-1 bg-slate-100 rounded-lg p-1 ml-2">
        {Object.keys(VIEW_LABELS).map((id) => (
          <button
            key={id}
            onClick={() => setView(id)}
            className={`
              px-3 py-1.5 rounded-md text-xs font-semibold transition-all
              ${selectedView === id
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'}
            `}
          >
            {id}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      {/* 액션 */}
      <RunController />
      <Link
        to="/app/library"
        className="p-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        title="Library"
      >
        <BookOpen size={16} />
      </Link>
      <button
        onClick={onExport}
        disabled={!canExport}
        className={`p-2 rounded-lg transition-colors ${canExport ? 'text-slate-600 hover:text-slate-800 hover:bg-slate-100' : 'text-slate-300 cursor-not-allowed'}`}
        title={canExport ? 'Export to PDF' : 'Run analysis first'}
      >
        <Download size={16} />
      </button>
    </header>
  );
};

export default TGIPHeader;
