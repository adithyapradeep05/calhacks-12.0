import { useCallback, useEffect } from 'react';
import ReactFlow, { Background, Controls, MiniMap, BackgroundVariant, useReactFlow } from 'reactflow';
import 'reactflow/dist/style.css';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { nodeTypes } from '@/nodes';

export const Canvas = () => {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    saveWorkflow,
    selectedNode,
    setSelectedNode,
  } = useWorkflowStore();

  const { fitView, zoomIn, zoomOut, setViewport } = useReactFlow();

  const onNodeClick = useCallback((event: React.MouseEvent, node: any) => {
    setSelectedNode(node.id);
  }, [setSelectedNode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl+S: Save
      if ((e.metaKey || e.ctrlKey) && e.key === 's') {
        e.preventDefault();
        saveWorkflow();
        console.log('Workflow saved via keyboard shortcut');
      }

      // Cmd/Ctrl+K: Focus chat input (handled globally)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const chatInput = document.querySelector<HTMLInputElement>('[data-chat-input]');
        if (chatInput) chatInput.focus();
      }

      // Delete: Delete selected node/edge
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (selectedNode && document.activeElement?.tagName !== 'INPUT') {
          e.preventDefault();
          // Handle delete (can be extended to actually remove nodes)
          console.log('Delete node:', selectedNode);
        }
      }

      // Cmd/Ctrl+0: Reset zoom
      if ((e.metaKey || e.ctrlKey) && e.key === '0') {
        e.preventDefault();
        fitView({ padding: 0.2, duration: 300 });
      }

      // Cmd/Ctrl+=: Zoom in
      if ((e.metaKey || e.ctrlKey) && (e.key === '=' || e.key === '+')) {
        e.preventDefault();
        zoomIn({ duration: 300 });
      }

      // Cmd/Ctrl+-: Zoom out
      if ((e.metaKey || e.ctrlKey) && e.key === '-') {
        e.preventDefault();
        zoomOut({ duration: 300 });
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedNode, saveWorkflow, fitView, zoomIn, zoomOut]);

  return (
    <div className="w-full h-full bg-canvas-bg">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-canvas-bg"
      >
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={20} 
          size={1}
          color="hsl(var(--canvas-grid))"
        />
        <Controls className="bg-card border-border" />
        <MiniMap 
          className="bg-card border-border"
          nodeColor={(node) => {
            const colors: Record<string, string> = {
              uploadNode: 'hsl(var(--node-upload-border))',
              embedNode: 'hsl(var(--node-embed-border))',
              storeNode: 'hsl(var(--node-store-border))',
              queryNode: 'hsl(var(--node-query-border))',
              llmNode: 'hsl(var(--node-llm-border))',
            };
            return colors[node.type || ''] || 'hsl(var(--primary))';
          }}
        />
      </ReactFlow>
    </div>
  );
};
