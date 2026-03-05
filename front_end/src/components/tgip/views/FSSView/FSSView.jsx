import FamilyExpansionMeter from './FamilyExpansionMeter';
import GlobalCoverageMap from './GlobalCoverageMap';
import AssigneePressureTable from './AssigneePressureTable';
import DisclaimerBanner from '../../shared/DisclaimerBanner';

const FSSView = ({ data }) => {
  if (!data) return (
    <div className="flex flex-col items-center justify-center h-64 text-slate-400">
      <p className="text-lg font-medium">FSS — Strategic Pressure View</p>
      <p className="text-sm mt-1">Run analysis to observe patent family strategic signals.</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-1">
          FSS — Strategic Pressure View
        </h2>
        <p className="text-sm text-slate-500">
          Observed patent family expansion and global coverage signals.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <FamilyExpansionMeter metrics={data.familyMetrics} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <GlobalCoverageMap coverage={data.countryCoverage} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <AssigneePressureTable leaderboard={data.assigneeLeaderboard} />
      </div>

      <div className="pt-2">
        <DisclaimerBanner />
      </div>
    </div>
  );
};

export default FSSView;
