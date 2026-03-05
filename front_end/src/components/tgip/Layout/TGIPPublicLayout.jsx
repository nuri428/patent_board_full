import { Outlet, Link, useLocation } from 'react-router-dom';
import DisclaimerBanner from '../shared/DisclaimerBanner';

const NAV_LINKS = [
  { to: '/overview', label: 'Overview' },
  { to: '/features', label: 'Features' },
  { to: '/demo', label: 'Demo' },
  { to: '/docs', label: 'Docs' },
];

const TGIPPublicLayout = () => {
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* 퍼블릭 네비 */}
      <nav className="border-b border-slate-200 px-6 py-4 flex items-center gap-8">
        <Link to="/" className="text-lg font-black text-slate-900 tracking-tight">TGIP</Link>
        <div className="flex items-center gap-6">
          {NAV_LINKS.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`text-sm font-medium transition-colors ${
                pathname.startsWith(to)
                  ? 'text-violet-600'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>
        <div className="ml-auto">
          <Link
            to="/app/tech/solid-state-battery"
            className="px-4 py-2 bg-violet-600 text-white text-sm font-semibold rounded-lg hover:bg-violet-700 transition-colors"
          >
            Open Workspace
          </Link>
        </div>
      </nav>

      {/* 페이지 콘텐츠 */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* 퍼블릭 푸터 */}
      <footer className="border-t border-slate-100 px-6 py-6 flex items-center justify-between">
        <span className="text-sm font-bold text-slate-400">TGIP</span>
        <DisclaimerBanner />
      </footer>
    </div>
  );
};

export default TGIPPublicLayout;
