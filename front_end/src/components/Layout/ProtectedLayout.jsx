import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Sidebar from './Sidebar';

const ProtectedLayout = () => {
    const { user } = useAuth();

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto ml-64 p-8">
                <Outlet />
            </main>
        </div>
    );
};

export default ProtectedLayout;
