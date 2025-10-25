import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Database, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';

const StoreNode = ({ id, data }: NodeProps) => {
  const { namespace, setSelectedNode } = useWorkflowStore();

  const statusColors = {
    idle: 'border-node-storeBorder',
    ready: 'border-node-storeBorder',
    running: 'border-warning animate-pulse',
    success: 'border-success',
    error: 'border-destructive',
  };

  return (
    <div className={`bg-node-store border-2 ${statusColors[data.status]} rounded-lg shadow-md hover:shadow-lg transition-shadow min-w-[280px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-node-storeBorder" />
      
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Database className="w-5 h-5 text-node-storeBorder" />
          <h3 className="font-semibold text-foreground">{data.label}</h3>
          <div className="ml-auto px-2 py-0.5 rounded text-xs font-medium bg-muted text-muted-foreground">
            Display
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Collection:</span>
            <span className="font-medium">{namespace || 'Not set'}</span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Status:</span>
            <span className={`font-medium ${data.status === 'success' ? 'text-success' : 'text-muted-foreground'}`}>
              {data.status === 'success' ? 'Active' : 'Waiting'}
            </span>
          </div>

          {data.result && (
            <div className="mt-3 p-2 bg-success/10 rounded text-xs text-success">
              Vectors stored in Chroma DB
            </div>
          )}

          <div className="text-xs text-muted-foreground mt-2">
            Vectors are automatically stored after embedding
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

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-node-storeBorder" />
    </div>
  );
};

export default memo(StoreNode);
