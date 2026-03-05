import { Play } from 'lucide-react';
import { useTGIPStore } from '../../../store/tgipStore';
import { tgipApi } from '../../../api/tgip';

const RunController = () => {
  const { selectedTechnology, isRunning, runAnalysis } = useTGIPStore();
  const disabled = !selectedTechnology || isRunning;

  return (
    <button
      onClick={() => runAnalysis(tgipApi)}
      disabled={disabled}
      className={`
        flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all
        ${disabled
          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
          : 'bg-violet-600 text-white hover:bg-violet-700 shadow-sm hover:shadow-md'
        }
      `}
    >
      {isRunning ? (
        <>
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          <span>Running...</span>
        </>
      ) : (
        <>
          <Play size={14} />
          <span>Run Analysis</span>
        </>
      )}
    </button>
  );
};

export default RunController;
