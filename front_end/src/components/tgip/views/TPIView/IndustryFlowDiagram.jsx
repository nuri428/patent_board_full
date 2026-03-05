import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const IndustryFlowDiagram = ({ flow }) => {
  if (!flow?.length) return null;

  const sorted = [...flow].sort((a, b) => b.score - a.score);

  const data = {
    labels: sorted.map((f) => f.industry),
    datasets: [
      {
        label: 'Propagation Score',
        data: sorted.map((f) => Math.round(f.score * 100)),
        backgroundColor: sorted.map((f) =>
          f.score >= 0.7 ? '#38bdf8' : f.score >= 0.5 ? '#7dd3fc' : '#bae6fd',
        ),
        borderRadius: 6,
        barThickness: 20,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const item = sorted[ctx.dataIndex];
            return [` Score: ${ctx.raw}%`, ` Patents: ${item.patents.toLocaleString()}`];
          },
        },
      },
    },
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
      <p className="text-sm font-medium text-slate-600 mb-3">Industry Propagation Flow</p>
      <Bar data={data} options={options} />
    </div>
  );
};

export default IndustryFlowDiagram;
