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
    console.log('Embed button clicked');
    console.log('Current namespace:', namespace);
    console.log('Available nodes:', nodes.map(n => ({ id: n.id, type: n.data.type, status: n.data.status })));
    
    if (!namespace) {
      alert('Please set a namespace first');
      return;
    }

    // Find upload node
    const uploadNode = nodes.find(n => n.data.type === 'upload');
    console.log('Upload node found:', uploadNode);
    
    if (!uploadNode?.data.result?.path) {
      alert('Please upload a document first');
      return;
    }

    console.log('Starting embedding process...');
    setEmbedding(true);
    updateNodeStatus(id, 'running');

    try {
      console.log('Calling embedDocument with:', {
        path: uploadNode.data.result.path,
        namespace,
      });
      
      const result = await embedDocument({
        path: uploadNode.data.result.path,
        namespace,
      });
      
      console.log('Embedding successful:', result);
      
      updateNodeData(id, {
        config: { chunkSize: 800, overlap: 150 },
        result: result,
        status: 'success',
      });
      updateNodeStatus(id, 'success');
      
      // Update store node to show vectors are stored
      const storeNode = nodes.find(n => n.data.type === 'store');
      if (storeNode) {
        updateNodeData(storeNode.id, {
          result: { stored: true, chunks: result.chunks },
          status: 'success',
        });
        updateNodeStatus(storeNode.id, 'success');
      }
    } catch (error: any) {
      console.error('Embedding failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Embedding failed';
      console.error('Error details:', errorMessage);
      updateNodeStatus(id, 'error');
      
      // Show user-friendly error message
      alert(`Embedding failed: ${errorMessage}`);
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
            disabled={embedding || !namespace || !nodes.find(n => n.data.type === 'upload')?.data.result}
            className="w-full"
            size="sm"
          >
            {embedding ? '🔄 Embedding...' : 
             !namespace ? '⚠️ Set namespace first' :
             !nodes.find(n => n.data.type === 'upload')?.data.result ? '⚠️ Upload document first' :
             '✨ Embed Document'}
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

          {/* Debug info */}
          <div className="text-xs text-muted-foreground space-y-0.5 border-t pt-2">
            <div>Namespace: {namespace || 'Not set'}</div>
            <div>Upload status: {nodes.find(n => n.data.type === 'upload')?.data.status || 'No upload node'}</div>
            <div>Upload result: {nodes.find(n => n.data.type === 'upload')?.data.result ? 'Yes' : 'No'}</div>
          </div>
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
