import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const LABELS = {
  patent_volume: 'Patent Volume',
  growth: 'Growth Rate',
  classification_conf: 'Classification Confidence',
  citation_percentile: 'Citation Percentile',
};

const ScoreBreakdownChart = ({ components }) => {
  if (!components) return null;

  const keys = Object.keys(LABELS);
  const data = {
    labels: keys.map((k) => LABELS[k]),
    datasets: [
      {
        data: keys.map((k) => Math.round((components[k] ?? 0) * 100)),
        backgroundColor: ['#818cf8', '#38bdf8', '#34d399', '#fb923c'],
        borderRadius: 6,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: {
        min: 0,
        max: 100,
        grid: { color: '#f1f5f9' },
        ticks: { callback: (v) => `${v}%`, font: { size: 11 } },
      },
      y: { grid: { display: false }, ticks: { font: { size: 12 } } },
    },
  };

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-3">Why-Not-Yet Breakdown</p>
      <Bar data={data} options={options} />
    </div>
  );
};

export default ScoreBreakdownChart;
