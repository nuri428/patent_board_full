import { useState, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { tgipApi } from '../../../api/tgip';
import { useTGIPStore } from '../../../store/tgipStore';

// Mock 기술 목록 (백엔드 미구현 시)
const MOCK_TECHNOLOGIES = [
  { id: 'solid-state-battery', name: 'Solid State Battery', description: '전고체 배터리 기술', patent_count: 4821 },
  { id: 'perovskite-solar', name: 'Perovskite Solar Cell', description: '페로브스카이트 태양전지', patent_count: 3204 },
  { id: 'hydrogen-fuel-cell', name: 'Hydrogen Fuel Cell', description: '수소 연료전지', patent_count: 6130 },
  { id: 'quantum-computing', name: 'Quantum Computing', description: '양자 컴퓨팅', patent_count: 2890 },
];

const TechnologySelector = () => {
  const { selectedTechnology, setTechnology } = useTGIPStore();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (selectedTechnology) setQuery(selectedTechnology.name);
  }, [selectedTechnology]);

  useEffect(() => {
    const handler = (e) => { if (!ref.current?.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  useEffect(() => {
    if (!query || query === selectedTechnology?.name) { setResults([]); return; }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await tgipApi.searchTechnologies(query);
        setResults(res.data ?? MOCK_TECHNOLOGIES.filter(t =>
          t.name.toLowerCase().includes(query.toLowerCase())
        ));
      } catch {
        setResults(MOCK_TECHNOLOGIES.filter(t =>
          t.name.toLowerCase().includes(query.toLowerCase())
        ));
      } finally {
        setLoading(false);
        setOpen(true);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query, selectedTechnology?.name]);

  const select = (tech) => {
    setTechnology(tech);
    setQuery(tech.name);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-lg px-3 py-2 w-72 shadow-sm">
        <Search size={16} className="text-slate-400 shrink-0" />
        <input
          type="text"
          className="flex-1 text-sm outline-none placeholder:text-slate-400 text-slate-800"
          placeholder="Select technology..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => !selectedTechnology && setResults(MOCK_TECHNOLOGIES) || setOpen(true)}
        />
        {loading && (
          <div className="w-3 h-3 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
        )}
      </div>

      {open && results.length > 0 && (
        <div className="absolute top-full mt-1 left-0 w-80 bg-white border border-slate-200 rounded-lg shadow-lg z-50">
          {results.map((tech) => (
            <button
              key={tech.id}
              onClick={() => select(tech)}
              className="w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors first:rounded-t-lg last:rounded-b-lg"
            >
              <p className="text-sm font-medium text-slate-800">{tech.name}</p>
              <p className="text-xs text-slate-400 mt-0.5">
                {tech.description} · {tech.patent_count?.toLocaleString()} patents
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default TechnologySelector;
