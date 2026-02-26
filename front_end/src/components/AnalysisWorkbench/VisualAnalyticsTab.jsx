import React, { useState } from 'react';
import { BarChart3, PieChart, TrendingUp, RefreshCw } from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

const CHART_COLORS = [
  '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#ec4899', '#84cc16', '#f97316', '#14b8a6',
];

function extractCharts(results) {
  if (!results) return null;

  const data = results.data || results;

  // Semantic search 결과
  if (data.results && Array.isArray(data.results)) {
    const ipcCounts = {};
    const countryCounts = {};
    data.results.forEach(r => {
      (r.ipc_codes || []).forEach(code => {
        const section = code[0]; // IPC 섹션 (A-H)
        ipcCounts[section] = (ipcCounts[section] || 0) + 1;
      });
      if (r.country_code) {
        countryCounts[r.country_code] = (countryCounts[r.country_code] || 0) + 1;
      }
    });
    return { type: 'semantic', ipcCounts, countryCounts, total: data.total || data.results.length };
  }

  // Network analysis 결과
  if (data.nodes && Array.isArray(data.nodes)) {
    const labelCounts = {};
    data.nodes.forEach(n => {
      const label = n.label || n.type || 'Unknown';
      labelCounts[label] = (labelCounts[label] || 0) + 1;
    });
    return { type: 'network', labelCounts, nodeCount: data.nodes.length, edgeCount: (data.edges || []).length };
  }

  // Tech mapping 결과
  if (data.technologies && Array.isArray(data.technologies)) {
    const techCounts = {};
    data.technologies.forEach(t => {
      const name = t.technology_name || t.name || 'Unknown';
      techCounts[name] = (techCounts[name] || 0) + (t.patent_count || 1);
    });
    return { type: 'tech', techCounts };
  }

  return null;
}

const VisualAnalyticsResults = ({ results }) => {
  const charts = extractCharts(results);

  if (!charts) {
    return (
      <div className="flex flex-col items-center justify-center p-16 bg-amber-50/50 rounded-3xl border border-amber-100 border-dashed space-y-4">
        <BarChart3 className="w-12 h-12 text-amber-300" />
        <p className="text-slate-600 font-semibold">분석 결과가 없습니다</p>
        <p className="text-slate-400 text-sm text-center max-w-xs">
          다른 탭에서 분석을 먼저 실행한 후 Visual Analytics로 전환하세요.
        </p>
      </div>
    );
  }

  if (charts.type === 'semantic') {
    const ipcKeys = Object.keys(charts.ipcCounts).sort();
    const countryKeys = Object.keys(charts.countryCounts).sort();

    return (
      <div className="space-y-6">
        <div className="premium-card p-6">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" /> IPC 섹션 분포
          </h3>
          {ipcKeys.length > 0 ? (
            <Bar
              data={{
                labels: ipcKeys.map(k => `Section ${k}`),
                datasets: [{
                  label: '특허 수',
                  data: ipcKeys.map(k => charts.ipcCounts[k]),
                  backgroundColor: CHART_COLORS.slice(0, ipcKeys.length),
                  borderRadius: 6,
                }],
              }}
              options={{ responsive: true, plugins: { legend: { display: false } } }}
            />
          ) : (
            <p className="text-slate-400 text-sm text-center py-4">IPC 코드 데이터 없음</p>
          )}
        </div>

        {countryKeys.length > 0 && (
          <div className="premium-card p-6">
            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <PieChart className="w-4 h-4" /> 국가별 분포
            </h3>
            <div className="max-w-xs mx-auto">
              <Doughnut
                data={{
                  labels: countryKeys,
                  datasets: [{
                    data: countryKeys.map(k => charts.countryCounts[k]),
                    backgroundColor: CHART_COLORS.slice(0, countryKeys.length),
                  }],
                }}
                options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }}
              />
            </div>
          </div>
        )}

        <div className="premium-card p-4 flex items-center justify-between">
          <span className="text-slate-500 text-sm">총 검색 결과</span>
          <span className="text-2xl font-black text-indigo-600">{charts.total.toLocaleString()}</span>
        </div>
      </div>
    );
  }

  if (charts.type === 'network') {
    const labelKeys = Object.keys(charts.labelCounts);
    return (
      <div className="space-y-6">
        <div className="premium-card p-6">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" /> 노드 타입 분포
          </h3>
          <Bar
            data={{
              labels: labelKeys,
              datasets: [{
                label: '노드 수',
                data: labelKeys.map(k => charts.labelCounts[k]),
                backgroundColor: CHART_COLORS.slice(0, labelKeys.length),
                borderRadius: 6,
              }],
            }}
            options={{ responsive: true, plugins: { legend: { display: false } } }}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="premium-card p-4 text-center">
            <div className="text-2xl font-black text-emerald-600">{charts.nodeCount}</div>
            <div className="text-xs text-slate-500 mt-1">총 노드</div>
          </div>
          <div className="premium-card p-4 text-center">
            <div className="text-2xl font-black text-purple-600">{charts.edgeCount}</div>
            <div className="text-xs text-slate-500 mt-1">총 엣지</div>
          </div>
        </div>
      </div>
    );
  }

  if (charts.type === 'tech') {
    const techKeys = Object.keys(charts.techCounts).slice(0, 10);
    return (
      <div className="premium-card p-6">
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" /> 기술 분류별 특허 수 (상위 10)
        </h3>
        <Bar
          data={{
            labels: techKeys,
            datasets: [{
              label: '특허 수',
              data: techKeys.map(k => charts.techCounts[k]),
              backgroundColor: CHART_COLORS.slice(0, techKeys.length),
              borderRadius: 6,
            }],
          }}
          options={{
            indexAxis: 'y',
            responsive: true,
            plugins: { legend: { display: false } },
          }}
        />
      </div>
    );
  }

  return null;
};

const VisualAnalyticsTab = ({ results }) => (
  <div className="space-y-4">
    <div className="p-4 bg-amber-50 rounded-2xl border border-amber-100">
      <p className="text-amber-800 text-sm font-medium">
        다른 탭에서 분석을 실행하면 그 결과를 차트로 시각화합니다.
      </p>
    </div>
    {results ? (
      <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-100 text-emerald-700 text-sm font-medium flex items-center gap-2">
        <RefreshCw className="w-4 h-4" />
        결과 데이터 로드됨 — 우측에서 차트를 확인하세요
      </div>
    ) : (
      <p className="text-slate-400 text-sm">아직 분석 결과가 없습니다.</p>
    )}
  </div>
);

export { VisualAnalyticsTab, VisualAnalyticsResults };
