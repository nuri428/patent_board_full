import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { tgipApi } from '../../api/tgip';

const MetricCard = ({ label, children }) => (
  <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
    <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">{label}</p>
    {children}
  </div>
);

const RunDetail = () => {
  const { run_id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [evidenceOpen, setEvidenceOpen] = useState(false);

  useEffect(() => {
    setLoading(true);
    tgipApi.getRunDetail(run_id)
      .then((res) => setData(res.data))
      .catch((err) => setError(err.message || 'Failed to load run detail'))
      .finally(() => setLoading(false));
  }, [run_id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400">
        <div className="animate-spin w-8 h-8 border-4 border-slate-200 border-t-violet-500 rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400 gap-2">
        <p className="text-lg font-medium text-slate-600">Failed to load run</p>
        <p className="text-sm">{error}</p>
      </div>
    );
  }

  const { technology_id, results = {}, evidence = {}, created_at, metadata = {} } = data || {};

  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tgip-run-${run_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* 헤더 */}
      <div className="flex items-center gap-3 mb-8">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1"
        >
          ← Back
        </button>
        <h1 className="text-xl font-bold text-slate-800">Analysis Run Detail</h1>
      </div>

      {/* Summary Card */}
      <div className="bg-violet-50 border border-violet-200 rounded-xl p-5 mb-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 text-sm">
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Technology</p>
            <p className="font-semibold text-slate-800">{technology_id?.replace(/-/g, ' ')}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Run ID</p>
            <p className="font-mono text-xs text-violet-700 break-all">{run_id}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Analyzed</p>
            <p className="font-medium text-slate-700">{created_at ? new Date(created_at).toLocaleString() : '—'}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500 mb-0.5">Patents</p>
            <p className="font-semibold text-slate-800">{metadata.patentsAnalyzed?.toLocaleString() || '—'}</p>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <MetricCard label="RTS — Structural Maturity">
          {results.RTS ? (
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold text-violet-700">
                {(results.RTS.score * 100).toFixed(0)}%
              </span>
              <div>
                <p className="text-sm font-medium text-slate-700">{results.RTS.stage}</p>
                <p className="text-xs text-slate-400">maturity stage</p>
              </div>
            </div>
          ) : <p className="text-xs text-slate-400">No data</p>}
        </MetricCard>

        <MetricCard label="TPI — Propagation">
          {results.TPI ? (
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold text-cyan-600">
                {(results.TPI.semanticPropagationScore * 100).toFixed(0)}%
              </span>
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {results.TPI.industryFlow?.[0]?.industry || '—'}
                </p>
                <p className="text-xs text-slate-400">top industry</p>
              </div>
            </div>
          ) : <p className="text-xs text-slate-400">No data</p>}
        </MetricCard>

        <MetricCard label="FSS — Strategic Pressure">
          {results.FSS ? (
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold text-red-500">
                {(results.FSS.familyMetrics.GCR * 100).toFixed(0)}%
              </span>
              <div>
                <p className="text-sm font-medium text-slate-700">GCR</p>
                <p className="text-xs text-slate-400">global coverage rate</p>
              </div>
            </div>
          ) : <p className="text-xs text-slate-400">No data</p>}
        </MetricCard>

        <MetricCard label="WSD — Opportunity Field">
          {results.WSD ? (
            <div className="flex items-center gap-4">
              <span className="text-3xl font-bold text-emerald-600">
                {results.WSD.gapCandidates?.length || 0}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-700">Gap Candidates</p>
                <p className="text-xs text-slate-400">observed</p>
              </div>
            </div>
          ) : <p className="text-xs text-slate-400">No data</p>}
        </MetricCard>
      </div>

      {/* Evidence Bundle (접힘 가능) */}
      <div className="bg-white border border-slate-200 rounded-xl mb-6 overflow-hidden">
        <button
          onClick={() => setEvidenceOpen(!evidenceOpen)}
          className="w-full flex items-center justify-between px-5 py-4 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          <span>Evidence Bundle</span>
          <span className="text-slate-400 text-lg">{evidenceOpen ? '−' : '+'}</span>
        </button>
        {evidenceOpen && (
          <div className="px-5 pb-5 border-t border-slate-100">
            <div className="mt-4 space-y-3">
              {(evidence.representativePatents || []).map((patent) => (
                <div key={patent.id} className="border border-slate-100 rounded-lg p-3 bg-slate-50 text-sm">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-slate-700 text-xs">{patent.title}</p>
                    <span className="text-xs text-slate-400 font-mono shrink-0">{patent.id}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-1 line-clamp-2">{patent.abstractSnippet}</p>
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    {(patent.ipc || []).map((code) => (
                      <span key={code} className="text-xs font-mono bg-violet-50 text-violet-600 px-1.5 py-0.5 rounded">
                        {code}
                      </span>
                    ))}
                    <span className="text-xs text-slate-400 ml-auto">
                      confidence {(patent.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
              <div className="flex gap-2 flex-wrap mt-2">
                {(evidence.ipcSignatures || []).map((sig) => (
                  <span key={sig} className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                    {sig}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Download */}
      <div className="flex gap-3">
        <button
          onClick={handleDownloadJSON}
          className="px-4 py-2 bg-slate-800 text-white text-sm rounded-lg hover:bg-slate-700 transition-colors"
        >
          Download JSON
        </button>
        <button
          disabled
          className="px-4 py-2 bg-slate-100 text-slate-400 text-sm rounded-lg cursor-not-allowed"
          title="PDF export — coming in Phase 3"
        >
          Export PDF (Phase 3)
        </button>
      </div>

      {/* 면책 고지 */}
      <p className="mt-8 text-xs text-slate-400 border-t border-slate-100 pt-4">
        This system provides observational signals with evidence. Final decisions remain with the user.
      </p>
    </div>
  );
};

export default RunDetail;
