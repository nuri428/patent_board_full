import { useMemo } from 'react';
import { ReactFlow, Background, Controls } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const RADIUS = 180;

const buildLayout = (rawNodes) => {
  const coreNode = rawNodes.find((n) => n.id === 'core') || rawNodes[0];
  const otherNodes = rawNodes.filter((n) => n.id !== coreNode.id);
  const angleStep = (2 * Math.PI) / Math.max(otherNodes.length, 1);

  const positioned = [
    {
      id: coreNode.id,
      position: { x: 250, y: 180 },
      data: { label: coreNode.label },
      style: {
        width: coreNode.size * 2,
        height: coreNode.size * 2,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '11px',
        fontWeight: '700',
        background: '#7c3aed',
        color: '#fff',
        border: '2px solid #5b21b6',
      },
    },
    ...otherNodes.map((n, i) => {
      const angle = angleStep * i - Math.PI / 2;
      return {
        id: n.id,
        position: {
          x: 250 + RADIUS * Math.cos(angle) - n.size,
          y: 180 + RADIUS * Math.sin(angle) - n.size,
        },
        data: { label: n.label },
        style: {
          width: n.size * 2,
          height: n.size * 2,
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '10px',
          fontWeight: '600',
          background: '#e0e7ff',
          color: '#3730a3',
          border: '1.5px solid #a5b4fc',
        },
      };
    }),
  ];

  return positioned;
};

const PropagationGraph = ({ nodes: rawNodes, edges: rawEdges }) => {
  const nodes = useMemo(() => buildLayout(rawNodes || []), [rawNodes]);

  const edges = useMemo(
    () =>
      (rawEdges || []).map((e) => ({
        id: e.id || `${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
        label: `${(e.weight * 100).toFixed(0)}%`,
        style: { strokeWidth: Math.max(1, e.weight * 5), stroke: '#a78bfa' },
        labelStyle: { fontSize: 10, fill: '#6b7280' },
      })),
    [rawEdges],
  );

  return (
    <div>
      <p className="text-sm font-medium text-slate-600 mb-3">Semantic Propagation Graph</p>
      <div style={{ height: 380 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          zoomOnScroll={false}
          panOnScroll={false}
          panOnDrag={false}
        >
          <Background color="#f1f5f9" gap={20} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
};

export default PropagationGraph;
