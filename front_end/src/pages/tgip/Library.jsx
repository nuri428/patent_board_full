import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { tgipApi } from '../../api/tgip';
import { DEFAULT_TECH_PATH } from '../../constants/tgip';

const formatDate = (iso) => {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

const EmptyState = () => (
  <div className="text-center py-20 text-slate-400">
    <div className="text-4xl mb-4">📂</div>
    <p className="text-lg font-medium text-slate-600">No runs yet</p>
    <p className="text-sm mt-1 mb-6">Start by running an analysis in the workspace.</p>
    <Link
      to={DEFAULT_TECH_PATH}
      className="inline-block px-6 py-2 bg-violet-600 text-white rounded-lg text-sm font-semibold hover:bg-violet-700 transition-colors"
    >
      Open Workspace →
    </Link>
  </div>
);

const ErrorState = ({ onRetry }) => (
  <div className="text-center py-20 text-slate-400">
    <div className="text-4xl mb-4">⚠️</div>
    <p className="text-lg font-medium text-slate-600">불러오기 실패</p>
    <p className="text-sm mt-1 mb-6">분석 기록을 가져올 수 없습니다.</p>
    <button
      onClick={onRetry}
      className="inline-block px-6 py-2 bg-violet-600 text-white rounded-lg text-sm font-semibold hover:bg-violet-700 transition-colors"
    >
      다시 시도
    </button>
  </div>
);

const RunCard = ({ run }) => (
  <div className="bg-white border border-slate-200 rounded-xl px-5 py-4 flex items-center justify-between hover:border-violet-300 hover:shadow-sm transition-all">
    <div className="flex-1 min-w-0">
      <p className="font-semibold text-slate-800 truncate capitalize">
        {run.technology_id?.replace(/-/g, ' ') || 'Unknown Technology'}
      </p>
      <p className="text-xs text-slate-400 mt-0.5 font-mono truncate">
        {run.run_id ?? '—'}
      </p>
    </div>
    <div className="flex items-center gap-4 shrink-0 ml-4">
      <span className="text-sm text-slate-500">{formatDate(run.created_at)}</span>
      <Link
        to={`/app/runs/${run.run_id ?? ''}`}
        className="px-3 py-1.5 bg-violet-50 text-violet-700 rounded-lg text-xs font-semibold hover:bg-violet-100 transition-colors"
      >
        View →
      </Link>
    </div>
  </div>
);

const Library = () => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    tgipApi.getLibrary({ signal: controller.signal })
      .then((res) => setRuns(res.data?.runs || []))
      .catch((err) => {
        if (err.name !== 'CanceledError') {
          console.error('[Library] Failed to load runs:', err);
          setError(err);
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [retryCount]);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-4">
            <Link to={DEFAULT_TECH_PATH} className="hover:text-violet-600 transition-colors">
              Workspace
            </Link>
            <span>/</span>
            <span className="text-slate-800 font-medium">Library</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">My Analysis Library</h1>
          {!loading && !error && runs.length > 0 && (
            <p className="text-sm text-slate-500 mt-1">{runs.length} saved run{runs.length !== 1 ? 's' : ''}</p>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-8 h-8 border-2 border-violet-200 border-t-violet-500 rounded-full animate-spin" />
          </div>
        ) : error ? (
          <ErrorState onRetry={() => setRetryCount((c) => c + 1)} />
        ) : runs.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-3">
            {runs.map((run) => (
              <RunCard key={run.run_id} run={run} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Library;
