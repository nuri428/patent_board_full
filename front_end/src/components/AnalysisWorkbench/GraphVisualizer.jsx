import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Loader2, ZoomIn, Maximize2 } from 'lucide-react';

const NODE_COLORS = {
    Corporation: '#8b5cf6', // purple-500
    Technology: '#3b82f6',  // blue-500
    Patent: '#10b981',      // emerald-500
    Person: '#f59e0b',      // amber-500
    Default: '#6b7280'      // gray-500
};

const BATCH_SIZE = 30;
const BATCH_DELAY = 100;

const GraphVisualizer = ({ data }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);
    const [progress, setProgress] = useState(0);

    // Progressive Loading Logic
    useEffect(() => {
        if (!data || !data.nodes) return;

        setLoading(true);
        setNodes([]);
        setEdges([]);
        setProgress(0);

        const rawNodes = data.nodes || [];
        const rawEdges = data.edges || [];
        const totalItems = rawNodes.length + rawEdges.length;
        let itemsProcessed = 0;

        // Process nodes in batches
        let nodeIndex = 0;
        const loadNodes = () => {
            const nextBatch = rawNodes.slice(nodeIndex, nodeIndex + BATCH_SIZE);
            if (nextBatch.length === 0) {
                loadEdges();
                return;
            }

            const newNodes = nextBatch.map((node, idx) => ({
                id: node.id,
                data: { label: node.label || node.id },
                position: {
                    x: Math.random() * 800 - 400 + (nodeIndex + idx) * 10,
                    y: Math.random() * 600 - 300
                },
                style: {
                    background: NODE_COLORS[node.group] || NODE_COLORS.Default,
                    color: '#fff',
                    borderRadius: '12px',
                    padding: '10px',
                    fontSize: '12px',
                    fontWeight: 'bold',
                    width: 150,
                    textAlign: 'center',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    border: 'none'
                }
            }));

            setNodes((nds) => [...nds, ...newNodes]);
            nodeIndex += BATCH_SIZE;
            itemsProcessed += nextBatch.length;
            if (totalItems > 0) {
                setProgress(Math.round((itemsProcessed / totalItems) * 100));
            }

            setTimeout(loadNodes, BATCH_DELAY);
        };

        // Process edges in batches
        let edgeIndex = 0;
        const loadEdges = () => {
            const nextBatch = rawEdges.slice(edgeIndex, edgeIndex + BATCH_SIZE);
            if (nextBatch.length === 0) {
                setLoading(false);
                setProgress(100);
                return;
            }

            const newEdges = nextBatch.map((edge) => ({
                id: `e-${edge.from}-${edge.to}`,
                source: edge.from,
                target: edge.to,
                label: edge.label,
                animated: true,
                style: { stroke: '#94a3b8', strokeWidth: 2 },
                labelStyle: { fill: '#64748b', fontWeight: 700, fontSize: 10 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: '#94a3b8',
                },
            }));

            setEdges((eds) => [...eds, ...newEdges]);
            edgeIndex += BATCH_SIZE;
            itemsProcessed += nextBatch.length;
            if (totalItems > 0) {
                setProgress(Math.round((itemsProcessed / totalItems) * 100));
            }

            setTimeout(loadEdges, BATCH_DELAY);
        };

        loadNodes();

        return () => {
            // Cleanup could go here if needed
        };
    }, [data, setNodes, setEdges]);

    if (!data?.nodes || data.nodes.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">
                <p className="text-gray-400 font-medium">No graph data available to visualize.</p>
            </div>
        );
    }

    return (
        <div className="relative w-full h-[600px] bg-white rounded-3xl border border-gray-100 shadow-inner overflow-hidden">
            {loading && (
                <div className="absolute inset-0 z-10 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center">
                    <Loader2 className="w-8 h-8 text-purple-600 animate-spin mb-4" />
                    <div className="w-64 bg-gray-200 rounded-full h-2 mb-2">
                        <div
                            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <p className="text-sm font-bold text-gray-600">Rendering Knowledge Graph... {progress}%</p>
                </div>
            )}

            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView
                className="bg-gray-50/50"
            >
                <Background color="#e2e8f0" gap={20} />
                <Controls />
                <MiniMap
                    nodeColor={(n) => n.style?.background || '#eee'}
                    maskColor="rgb(241, 245, 249, 0.6)"
                    className="rounded-xl border border-gray-200 shadow-sm"
                />

                {/* Floating Tools HUD */}
                <div className="absolute top-4 right-4 flex flex-col gap-2 z-20">
                    <div className="bg-white/90 backdrop-blur-md p-3 rounded-2xl shadow-lg border border-gray-100 flex flex-col gap-3">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-[#8b5cf6]"></div>
                            <span className="text-[10px] font-bold text-gray-500">Corporation</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-[#3b82f6]"></div>
                            <span className="text-[10px] font-bold text-gray-500">Technology</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-[#10b981]"></div>
                            <span className="text-[10px] font-bold text-gray-500">Patent</span>
                        </div>
                    </div>
                </div>
            </ReactFlow>

            {/* Bottom HUD */}
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 px-6 py-2 bg-gray-900/80 backdrop-blur-md text-white rounded-full text-xs font-medium flex items-center gap-4 z-20 shadow-2xl">
                <div className="flex items-center gap-2 border-r border-gray-700 pr-4">
                    <span className="text-gray-400">Nodes:</span>
                    <span>{nodes.length}</span>
                </div>
                <div className="flex items-center gap-2 border-r border-gray-700 pr-4">
                    <span className="text-gray-400">Edges:</span>
                    <span>{edges.length}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-green-400">●</span>
                    <span>System Live</span>
                </div>
            </div>
        </div>
    );
};

export default GraphVisualizer;
