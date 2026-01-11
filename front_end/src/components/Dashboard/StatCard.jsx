import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, icon: Icon, color, trend }) => {
    return (
        <motion.div
            whileHover={{ y: -5 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-start justify-between relative overflow-hidden group"
        >
            <div className="z-10">
                <p className="text-gray-500 text-sm font-medium mb-1">{title}</p>
                <h3 className="text-3xl font-bold text-gray-800">{value}</h3>
                {trend && (
                    <div className="flex items-center mt-2 text-sm">
                        <span className={`font-medium ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {trend >= 0 ? '+' : ''}{trend}%
                        </span>
                        <span className="text-gray-400 ml-1">vs last month</span>
                    </div>
                )}
            </div>

            <div className={`p-3 rounded-lg ${color} bg-opacity-10 text-${color.replace('bg-', '')}`}>
                <Icon className={`w-6 h-6 text-${color.replace('bg-', '')}-600`} />
            </div>

            {/* Decorative background circle */}
            <div className={`absolute -right-6 -bottom-6 w-24 h-24 rounded-full opacity-10 ${color} group-hover:scale-150 transition-transform duration-500 ease-out z-0`} />
        </motion.div>
    );
};

export default StatCard;
