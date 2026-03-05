import MaturityScale from './MaturityScale';
import ScoreBreakdownChart from './ScoreBreakdownChart';
import BottleneckIndicator from './BottleneckIndicator';
import SolutionOptionsTable from './SolutionOptionsTable';
import DisclaimerBanner from '../../shared/DisclaimerBanner';

const RTSView = ({ data }) => {
  if (!data) return (
    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
      <p className="text-lg font-medium">No RTS data</p>
      <p className="text-sm mt-1">Run analysis to observe structural maturity signals.</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">
          RTS — Structural Maturity View
        </h2>
        <p className="text-sm text-slate-500">
          Observed structural maturity and bottleneck stage of this technology.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <MaturityScale score={data.score} stage={data.stage} />
      </div>

      <BottleneckIndicator stage={data.stage} />

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <ScoreBreakdownChart components={data.components} />
      </div>

      {data.solutionOptions?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <SolutionOptionsTable options={data.solutionOptions} />
        </div>
      )}

      <div className="pt-2">
        <DisclaimerBanner />
      </div>
    </div>
  );
};

export default RTSView;
