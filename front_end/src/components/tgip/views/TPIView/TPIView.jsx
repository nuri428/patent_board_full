import PropagationGraph from './PropagationGraph';
import BurstTimeline from './BurstTimeline';
import IndustryFlowDiagram from './IndustryFlowDiagram';
import DisclaimerBanner from '../../shared/DisclaimerBanner';

const TPIView = ({ data }) => {
  if (!data) return (
    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
      <p className="text-lg font-medium">TPI — Propagation View</p>
      <p className="text-sm mt-1">Run analysis to observe propagation dynamics signals.</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">
          TPI — Propagation View
        </h2>
        <p className="text-sm text-slate-500">
          Observed semantic propagation score:{' '}
          <span className="font-semibold text-cyan-600">
            {(data.semanticPropagationScore * 100).toFixed(0)}%
          </span>
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <PropagationGraph
          nodes={data.propagationGraph?.nodes}
          edges={data.propagationGraph?.edges}
        />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <BurstTimeline timeline={data.burstTimeline} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <IndustryFlowDiagram flow={data.industryFlow} />
      </div>

      <div className="pt-2">
        <DisclaimerBanner />
      </div>
    </div>
  );
};

export default TPIView;
