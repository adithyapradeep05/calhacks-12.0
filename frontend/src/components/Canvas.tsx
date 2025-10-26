import { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, { Background, Controls, MiniMap, BackgroundVariant, useReactFlow, ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { nodeTypes } from '@/nodes';
import { BlockShelf } from './BlockShelf';

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
    addNode,
    deleteNode,
  } = useWorkflowStore();

  const { fitView, zoomIn, zoomOut, setViewport, screenToFlowPosition } = useReactFlow();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

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
        if (selectedNode && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
          e.preventDefault();
          deleteNode(selectedNode);
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
  }, [selectedNode, saveWorkflow, fitView, zoomIn, zoomOut, deleteNode]);

  const onPaneContextMenu = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const nodeType = e.dataTransfer.getData('application/reactflow');
      if (!nodeType) return;

      const position = screenToFlowPosition({
        x: e.clientX,
        y: e.clientY,
      });

      addNode(nodeType, position);
    },
    [addNode, screenToFlowPosition]
  );

  const handleAddNode = useCallback((nodeType: string) => {
    const viewport = { x: 0, y: 0, zoom: 1 };
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const position = screenToFlowPosition({ x: centerX, y: centerY });
    addNode(nodeType, position);
  }, [addNode, screenToFlowPosition]);

  // Resizable BlockShelf state
  const [shelfWidth, setShelfWidth] = useState<number>(() => {
    const stored = localStorage.getItem('shelfWidth');
    const parsed = stored ? parseInt(stored, 10) : 280;
    return isNaN(parsed) ? 280 : parsed;
  });
  const isResizingRef = useRef(false);
  const startXRef = useRef(0);
  const startWidthRef = useRef(0);

  const MIN_WIDTH = 200;
  const MAX_WIDTH = 480;

  const onResizerMouseDown = useCallback((e: React.MouseEvent) => {
    isResizingRef.current = true;
    startXRef.current = e.clientX;
    startWidthRef.current = shelfWidth;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
  }, [shelfWidth]);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!isResizingRef.current) return;
      const delta = e.clientX - startXRef.current;
      const next = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, startWidthRef.current + delta));
      setShelfWidth(next);
    };
    const onMouseUp = () => {
      if (!isResizingRef.current) return;
      isResizingRef.current = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
      try { localStorage.setItem('shelfWidth', String(shelfWidth)); } catch {}
    };
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [shelfWidth]);

  return (
    <div className="flex w-full h-full bg-canvas-bg">
      <div style={{ width: shelfWidth }} className="h-full">
        <BlockShelf onAddNode={handleAddNode} />
      </div>
      {/* Vertical resizer */}
      <div
        onMouseDown={onResizerMouseDown}
        className="relative w-[3px] bg-border hover:bg-primary/40 cursor-col-resize"
        title="Drag to resize"
      >
        <div className="absolute inset-y-0 -left-1 -right-1" />
      </div>
      
      <div ref={reactFlowWrapper} className="flex-1">
        <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneContextMenu={onPaneContextMenu}
        onDragOver={onDragOver}
        onDrop={onDrop}
        nodeTypes={nodeTypes}
        fitView
        className="bg-canvas-bg"
      >
        <Background 
          variant={BackgroundVariant.Dots} 
          gap={16} 
          size={2}
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
    </div>
  );
};
