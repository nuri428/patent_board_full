import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

const BurstTimeline = ({ timeline }) => {
  if (!timeline?.length) return null;

  const data = {
    labels: timeline.map((t) => t.year),
    datasets: [
      {
        label: 'Patent Count',
        data: timeline.map((t) => t.count),
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.15)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#38bdf8',
        yAxisID: 'y',
      },
      {
        label: 'Burst Score',
        data: timeline.map((t) => Math.round(t.burstScore * 100)),
        borderColor: '#f97316',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#f97316',
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            if (ctx.datasetIndex === 0) return ` Patents: ${ctx.raw}`;
            return ` Burst: ${ctx.raw}%`;
          },
        },
      },
    },
    scales: {
      x: { grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } },
      y: {
        type: 'linear',
        position: 'left',
        grid: { color: '#f1f5f9' },
        ticks: { font: { size: 11 } },
        title: { display: true, text: 'Patents', font: { size: 10 }, color: '#94a3b8' },
      },
      y1: {
        type: 'linear',
        position: 'right',
        min: 0,
        max: 100,
        grid: { drawOnChartArea: false },
        ticks: { callback: (v) => `${v}%`, font: { size: 11 } },
        title: { display: true, text: 'Burst', font: { size: 10 }, color: '#94a3b8' },
      },
    },
  };

  return (
    <div>
      <div className="flex items-center gap-4 mb-3">
        <p className="text-sm font-medium text-slate-600">Burst Timeline</p>
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-sky-400 inline-block" /> Patents</span>
          <span className="flex items-center gap-1"><span className="w-3 h-0.5 bg-orange-400 inline-block border-dashed" /> Burst Score</span>
        </div>
      </div>
      <Line data={data} options={options} />
    </div>
  );
};

export default BurstTimeline;
