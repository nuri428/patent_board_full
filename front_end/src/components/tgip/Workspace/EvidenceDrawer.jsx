import { ChevronUp, ChevronDown, FileText } from 'lucide-react';
import { useTGIPStore } from '../../../store/tgipStore';
import ConfidenceBadge from '../shared/ConfidenceBadge';

const EvidenceDrawer = () => {
  const { evidence, evidenceDrawerOpen, toggleEvidenceDrawer, analysisRunId } = useTGIPStore();
  const { representativePatents = [], ipcSignatures = [], confidenceScores = {} } = evidence;
  const hasEvidence = representativePatents.length > 0;

  return (
    <div className="border-t border-slate-200 bg-white shrink-0">
      {/* Drawer 헤더 */}
      <button
        onClick={toggleEvidenceDrawer}
        className="w-full flex items-center justify-between px-6 py-3 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <FileText size={16} className="text-slate-500" />
          <span className="text-sm font-semibold text-slate-700">Evidence</span>
          {hasEvidence && (
            <span className="text-xs bg-violet-100 text-violet-700 px-2 py-0.5 rounded-full">
              {representativePatents.length} patents
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          {analysisRunId && (
            <span className="text-xs text-slate-400 font-mono">
              Run: {analysisRunId.slice(0, 20)}{analysisRunId.length > 20 ? '…' : ''}
            </span>
          )}
          {evidenceDrawerOpen ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronUp size={16} className="text-slate-400" />}
        </div>
      </button>

      {/* Drawer 내용 */}
      {evidenceDrawerOpen && (
        <div className="px-6 pb-5 max-h-56 overflow-y-auto space-y-4">
          {!hasEvidence ? (
            <p className="text-sm text-slate-400 py-2">
              No evidence available. Run analysis to generate traceable signals.
            </p>
          ) : (
            <>
              {/* IPC 시그니처 */}
              {ipcSignatures.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {ipcSignatures.map((sig) => (
                    <span key={sig} className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-1 rounded">
                      {sig}
                    </span>
                  ))}
                </div>
              )}

              {/* 특허 목록 */}
              <div className="space-y-3">
                {representativePatents.map((patent) => (
                  <div key={patent.id} className="border border-slate-100 rounded-lg p-3 bg-slate-50">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-mono text-slate-400">{patent.id}</p>
                        <p className="text-sm font-medium text-slate-800 mt-0.5 truncate">{patent.title}</p>
                        {patent.abstractSnippet && (
                          <p className="text-xs text-slate-500 mt-1 line-clamp-2">{patent.abstractSnippet}</p>
                        )}
                        <div className="flex flex-wrap gap-1 mt-2">
                          {patent.ipc?.map((code) => (
                            <span key={code} className="text-xs font-mono bg-white border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded">
                              {code}
                            </span>
                          ))}
                        </div>
                      </div>
                      <ConfidenceBadge score={patent.confidence} />
                    </div>
                  </div>
                ))}
              </div>

              {/* 전체 신뢰도 */}
              {confidenceScores.overall && (
                <p className="text-xs text-slate-400">
                  Overall signal confidence: {Math.round(confidenceScores.overall * 100)}% ·
                  Coverage: {Math.round((confidenceScores.coverage ?? 0) * 100)}%
                </p>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default EvidenceDrawer;
