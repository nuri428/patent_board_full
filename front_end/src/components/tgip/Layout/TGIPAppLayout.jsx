import { Outlet } from 'react-router-dom';

const TGIPAppLayout = () => (
  <div className="h-screen flex flex-col overflow-hidden bg-slate-50">
    <Outlet />
  </div>
);

export default TGIPAppLayout;
