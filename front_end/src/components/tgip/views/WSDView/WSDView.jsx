import ProblemSolutionHeatmap from './ProblemSolutionHeatmap';
import GapCandidatesList from './GapCandidatesList';
import CrossIndustryAnalogPanel from './CrossIndustryAnalogPanel';
import DisclaimerBanner from '../../shared/DisclaimerBanner';

const WSDView = ({ data }) => {
  if (!data) return (
    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
      <p className="text-lg font-medium">WSD — Opportunity Field View</p>
      <p className="text-sm mt-1">Run analysis to observe opportunity fields and gap candidates.</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">
          WSD — Opportunity Field View
        </h2>
        <p className="text-sm text-slate-500">
          Observed problem-solution density and unresolved gap candidates in this technology field.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <ProblemSolutionHeatmap
          matrix={data.heatmapMatrix}
          problems={data.problemClusters}
          solutions={data.solutionClusters}
        />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <GapCandidatesList candidates={data.gapCandidates} />
      </div>

      {data.crossIndustryAnalogs?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <CrossIndustryAnalogPanel analogs={data.crossIndustryAnalogs} />
        </div>
      )}

      <div className="pt-2">
        <DisclaimerBanner />
      </div>
    </div>
  );
};

export default WSDView;
