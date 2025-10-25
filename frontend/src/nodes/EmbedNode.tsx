import { memo, useState, useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Sparkles, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { embedDocument } from '@/lib/api';
import { Button } from '@/components/ui/button';

const EmbedNode = ({ id, data }: NodeProps) => {
  const [embedding, setEmbedding] = useState(false);
  const { nodes, namespace, updateNodeData, updateNodeStatus, setSelectedNode } = useWorkflowStore();

  const handleEmbed = useCallback(async () => {
    if (!namespace) {
      alert('Please set a namespace first');
      return;
    }

    // Find upload node
    const uploadNode = nodes.find(n => n.data.type === 'upload');
    if (!uploadNode?.data.result?.path) {
      alert('Please upload a document first');
      return;
    }

    setEmbedding(true);
    updateNodeStatus(id, 'running');

    try {
      const result = await embedDocument({
        path: uploadNode.data.result.path,
        namespace,
      });
      
      updateNodeData(id, {
        config: { chunkSize: 512, overlap: 50 },
        result: result,
        status: 'success',
      });
      updateNodeStatus(id, 'success');
    } catch (error) {
      console.error('Embedding failed:', error);
      updateNodeStatus(id, 'error');
    } finally {
      setEmbedding(false);
    }
  }, [id, namespace, nodes, updateNodeData, updateNodeStatus]);

  const statusColors = {
    idle: 'border-node-embedBorder',
    ready: 'border-node-embedBorder',
    running: 'border-warning animate-pulse',
    success: 'border-success',
    error: 'border-destructive',
  };

  return (
    <div className={`bg-node-embed border-2 ${statusColors[data.status]} rounded-lg shadow-md hover:shadow-lg transition-shadow min-w-[280px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-node-embedBorder" />
      
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-node-embedBorder" />
          <h3 className="font-semibold text-foreground">{data.label}</h3>
          <div className={`ml-auto px-2 py-0.5 rounded text-xs font-medium ${
            data.status === 'success' ? 'bg-success text-success-foreground' :
            data.status === 'error' ? 'bg-destructive text-destructive-foreground' :
            data.status === 'running' ? 'bg-warning text-warning-foreground' :
            'bg-muted text-muted-foreground'
          }`}>
            {data.status === 'success' ? 'Embedded' : 
             data.status === 'running' ? 'Embedding...' :
             data.status === 'error' ? 'Error' : 'Idle'}
          </div>
        </div>

        <div className="space-y-3">
          <Button
            onClick={handleEmbed}
            disabled={embedding || !namespace}
            className="w-full"
            size="sm"
          >
            {embedding ? 'Embedding...' : 'Embed Document'}
          </Button>

          {data.result && (
            <div className="text-xs space-y-1">
              <div className="text-success font-medium">
                ✓ Embedded {data.result.chunks} chunks
              </div>
              <div className="text-muted-foreground">
                Namespace: {data.result.namespace}
              </div>
            </div>
          )}

          {data.config && (
            <div className="text-xs text-muted-foreground space-y-0.5">
              <div>Chunk size: {data.config.chunkSize}</div>
              <div>Overlap: {data.config.overlap}</div>
            </div>
          )}
        </div>

        <div className="mt-3 pt-3 border-t border-border flex justify-between text-xs">
          <button
            onClick={() => setSelectedNode(id)}
            className="flex items-center gap-1 text-muted-foreground hover:text-foreground transition-colors"
          >
            <Settings className="w-3 h-3" />
            Settings
          </button>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-node-embedBorder" />
    </div>
  );
};

export default memo(EmbedNode);
