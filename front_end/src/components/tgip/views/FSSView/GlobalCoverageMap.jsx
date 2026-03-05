import { useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

const GEO_URL = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';

// ISO alpha-2 → numeric 매핑 (주요 국가)
const ISO2_TO_NUMERIC = {
  KR: '410', US: '840', CN: '156', JP: '392', DE: '276',
  GB: '826', FR: '250', IN: '356', CA: '124', AU: '036',
  TW: '158', NL: '528', SE: '752', CH: '756', IT: '380',
};

const intensityToFill = (intensity) => {
  if (intensity === undefined || intensity === null) return '#f1f5f9';
  const alpha = Math.max(0.1, intensity);
  return `rgba(124, 58, 237, ${alpha})`;
};

const GlobalCoverageMap = ({ coverage }) => {
  const [tooltip, setTooltip] = useState(null);

  const coverageMap = {};
  (coverage || []).forEach((c) => {
    const numeric = ISO2_TO_NUMERIC[c.iso];
    if (numeric) coverageMap[numeric] = c;
    coverageMap[c.iso] = c;
  });

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-3">Global Patent Coverage</p>
      <ComposableMap
        projectionConfig={{ scale: 147, center: [0, 10] }}
        style={{ width: '100%', height: 'auto' }}
      >
        <Geographies geography={GEO_URL}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const numId = geo.id;
              const entry = coverageMap[numId];
              const fill = entry ? intensityToFill(entry.intensity) : '#f1f5f9';

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={fill}
                  stroke="#e2e8f0"
                  strokeWidth={0.5}
                  style={{
                    default: { outline: 'none' },
                    hover: { fill: entry ? '#7c3aed' : '#e2e8f0', outline: 'none', cursor: entry ? 'pointer' : 'default' },
                    pressed: { outline: 'none' },
                  }}
                  onMouseEnter={() => entry && setTooltip({ name: geo.properties?.name, count: entry.count, intensity: entry.intensity })}
                  onMouseLeave={() => setTooltip(null)}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>

      {tooltip && (
        <div className="mt-2 px-3 py-1.5 bg-slate-800 text-white text-xs rounded-lg inline-block">
          <span className="font-medium">{tooltip.name}</span>
          <span className="text-slate-300 ml-2">{tooltip.count?.toLocaleString()} patents</span>
          <span className="text-slate-400 ml-1">({(tooltip.intensity * 100).toFixed(0)}%)</span>
        </div>
      )}

      {/* 커버리지 요약 */}
      <div className="mt-4 flex flex-wrap gap-2">
        {(coverage || []).map((c) => (
          <div key={c.iso} className="flex items-center gap-1.5 text-xs">
            <span
              className="w-3 h-3 rounded-sm inline-block"
              style={{ backgroundColor: intensityToFill(c.intensity) }}
            />
            <span className="text-slate-600 font-medium">{c.iso}</span>
            <span className="text-slate-400">{c.count.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GlobalCoverageMap;
