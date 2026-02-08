import React from 'react';
import { useAuth } from '../../context/AuthContext';
import NotificationCenter from '../Notifications/NotificationCenter';
import { Search, User as UserIcon } from 'lucide-react';

const Header = () => {
    const { user } = useAuth();

    return (
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 px-8 flex items-center justify-between sticky top-0 z-40">
            {/* Search Bar - Placeholder for consistency */}
            <div className="flex-1 max-w-xl">
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-purple-500 transition-colors" />
                    <input
                        type="text"
                        placeholder="Global search patents, tasks, or reports..."
                        className="w-full pl-10 pr-4 py-2 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-purple-100 outline-none transition-all"
                    />
                </div>
            </div>

            {/* Right Group: Notifications & User */}
            <div className="flex items-center gap-6">
                <NotificationCenter />

                <div className="h-8 w-[1px] bg-gray-100" />

                <div className="flex items-center gap-3 pl-2">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-bold text-gray-800">{user?.full_name || user?.username}</p>
                        <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">{user?.role || 'Guest'}</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-purple-100 ring-2 ring-white">
                        <UserIcon className="w-5 h-5" />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default Header;
