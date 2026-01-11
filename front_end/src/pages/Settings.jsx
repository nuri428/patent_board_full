import React, { useState, useEffect } from 'react';
import { Key, Plus, Trash2, Copy, Check, Eye, EyeOff, Shield } from 'lucide-react';
import api from '../api/axios';
import { motion, AnimatePresence } from 'framer-motion';

const Settings = () => {
    const [keys, setKeys] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [newKey, setNewKey] = useState(null);
    const [formData, setFormData] = useState({ name: '', key_type: 'simple' });
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        fetchKeys();
    }, []);

    const fetchKeys = async () => {
        try {
            const response = await api.get('/mcp/keys');
            setKeys(response.data);
        } catch (error) {
            console.error("Failed to fetch keys", error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const response = await api.post('/mcp/keys', formData);
            setNewKey(response.data);
            fetchKeys();
            setFormData({ name: '', key_type: 'simple' });
        } catch (error) {
            console.error("Failed to create key", error);
        }
    };

    const handleRevoke = async (id) => {
        if (!confirm("Are you sure you want to revoke this key? It will stop working immediately.")) return;
        try {
            await api.delete(`/mcp/keys/${id}`);
            fetchKeys();
        } catch (error) {
            console.error("Failed to revoke key", error);
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const getTypeColor = (type) => {
        switch (type) {
            case 'all': return 'bg-purple-100 text-purple-700 border-purple-200';
            case 'graph': return 'bg-indigo-100 text-indigo-700 border-indigo-200';
            default: return 'bg-gray-100 text-gray-700 border-gray-200';
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
                <p className="text-gray-500 mt-1">Manage your account and API configurations.</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                            <Key className="w-5 h-5 text-blue-600" />
                            MCP API Keys
                        </h2>
                        <p className="text-sm text-gray-500 mt-1">
                            Generate keys to access the Model Context Protocol (MCP) server.
                        </p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
                    >
                        <Plus className="w-4 h-4" /> Generate Key
                    </button>
                </div>

                <div className="p-6">
                    {loading ? (
                        <div className="text-center py-8 text-gray-400">Loading keys...</div>
                    ) : keys.length === 0 ? (
                        <div className="text-center py-12 bg-gray-50 rounded-lg border border-dashed border-gray-200">
                            <Key className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                            <h3 className="text-gray-900 font-medium mb-1">No API Keys Found</h3>
                            <p className="text-gray-500 text-sm">Generate your first key to start using MCP tools.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {keys.map((key) => (
                                <div key={key.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-200 transition-colors">
                                    <div className="flex items-center gap-4">
                                        <div className="p-2 bg-white rounded-md shadow-sm">
                                            <Shield className="w-5 h-5 text-gray-400" />
                                        </div>
                                        <div>
                                            <h4 className="font-medium text-gray-900">{key.name}</h4>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className={`text-xs px-2 py-0.5 rounded-full border ${getTypeColor(key.key_type)} capitalize`}>
                                                    {key.key_type}
                                                </span>
                                                <span className="text-xs text-gray-400">
                                                    Created: {new Date(key.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="font-mono text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded">
                                            {key.api_key.substring(0, 15)}...
                                        </div>
                                        <button
                                            onClick={() => handleRevoke(key.id)}
                                            className="text-gray-400 hover:text-red-500 transition-colors p-2 hover:bg-red-50 rounded-full"
                                            title="Revoke Key"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Generate Key Modal */}
            <AnimatePresence>
                {showModal && (
                    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden"
                        >
                            {!newKey ? (
                                <form onSubmit={handleCreate} className="p-6">
                                    <h3 className="text-lg font-bold text-gray-900 mb-4">Generate New API Key</h3>

                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                            <input
                                                type="text"
                                                required
                                                placeholder="e.g., My Cursor Integration"
                                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                                                value={formData.name}
                                                onChange={e => setFormData({ ...formData, name: e.target.value })}
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Permissions</label>
                                            <div className="grid grid-cols-1 gap-2">
                                                {[
                                                    { id: 'simple', label: 'Simple Retrieval', desc: 'Search and view patents only.' },
                                                    { id: 'graph', label: 'Knowledge Graph', desc: 'Access graph search and analysis.' },
                                                    { id: 'all', label: 'All Access', desc: 'Full access to all tools.' }
                                                ].map(type => (
                                                    <label
                                                        key={type.id}
                                                        className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all ${formData.key_type === type.id
                                                                ? 'border-blue-500 bg-blue-50'
                                                                : 'border-gray-200 hover:border-gray-300'
                                                            }`}
                                                    >
                                                        <input
                                                            type="radio"
                                                            name="key_type"
                                                            value={type.id}
                                                            checked={formData.key_type === type.id}
                                                            onChange={e => setFormData({ ...formData, key_type: e.target.value })}
                                                            className="mt-1"
                                                        />
                                                        <div>
                                                            <div className="font-medium text-gray-900">{type.label}</div>
                                                            <div className="text-xs text-gray-500">{type.desc}</div>
                                                        </div>
                                                    </label>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex justify-end gap-3 mt-8">
                                        <button
                                            type="button"
                                            onClick={() => setShowModal(false)}
                                            className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium"
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="submit"
                                            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
                                        >
                                            Generate
                                        </button>
                                    </div>
                                </form>
                            ) : (
                                <div className="p-6">
                                    <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mx-auto mb-4">
                                        <Check className="w-6 h-6 text-green-600" />
                                    </div>
                                    <h3 className="text-lg font-bold text-gray-900 text-center mb-2">API Key Generated</h3>
                                    <p className="text-gray-500 text-center text-sm mb-6">
                                        Please copy your key now. You won't be able to see it again!
                                    </p>

                                    <div className="bg-gray-900 rounded-lg p-4 relative group">
                                        <code className="text-green-400 font-mono break-all text-sm block pr-8">
                                            {newKey.api_key}
                                        </code>
                                        <button
                                            onClick={() => copyToClipboard(newKey.api_key)}
                                            className="absolute top-2 right-2 p-2 text-gray-400 hover:text-white rounded hover:bg-gray-800 transition-colors"
                                            title="Copy to clipboard"
                                        >
                                            {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                                        </button>
                                    </div>

                                    <div className="mt-8">
                                        <button
                                            onClick={() => {
                                                setShowModal(false);
                                                setNewKey(null);
                                            }}
                                            className="w-full px-4 py-2 bg-gray-100 text-gray-900 rounded-lg font-medium hover:bg-gray-200"
                                        >
                                            Done
                                        </button>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Settings;
