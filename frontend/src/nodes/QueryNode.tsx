import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Search, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';

const QueryNode = ({ id, data }: NodeProps) => {
  const { updateNodeData, setSelectedNode } = useWorkflowStore();

  const k = data.config?.k || 4;

  const handleKChange = (value: number) => {
    updateNodeData(id, {
      config: { ...data.config, k: value },
    });
  };

  const statusColors = {
    idle: 'border-node-queryBorder',
    ready: 'border-node-queryBorder',
    running: 'border-warning animate-pulse',
    success: 'border-success',
    error: 'border-destructive',
  };

  return (
    <div className={`bg-node-query border-2 ${statusColors[data.status]} rounded-lg shadow-md hover:shadow-lg transition-shadow min-w-[280px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-node-queryBorder" />
      
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Search className="w-5 h-5 text-node-queryBorder" />
          <h3 className="font-semibold text-foreground">{data.label}</h3>
          <div className={`ml-auto px-2 py-0.5 rounded text-xs font-medium ${
            data.status === 'success' ? 'bg-success text-success-foreground' :
            'bg-muted text-muted-foreground'
          }`}>
            {data.status === 'success' ? 'Retrieved' : 'Ready'}
          </div>
        </div>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm text-muted-foreground">Top K results:</label>
              <span className="text-sm font-medium">{k}</span>
            </div>
            <input
              type="range"
              min="1"
              max="10"
              value={k}
              onChange={(e) => handleKChange(parseInt(e.target.value))}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-node-queryBorder"
            />
          </div>

          {data.result?.docs && data.result.docs.length > 0 && (
            <div className="text-xs space-y-1">
              <div className="font-medium text-success">Retrieved {data.result.docs.length} documents</div>
              <div className="max-h-20 overflow-y-auto space-y-1">
                {data.result.docs.map((doc: string, idx: number) => (
                  <div key={idx} className="p-1.5 bg-muted/50 rounded text-muted-foreground truncate">
                    {doc.substring(0, 60)}...
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="text-xs text-muted-foreground">
            Retrieval triggered by chat queries
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

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-node-queryBorder" />
    </div>
  );
};

export default memo(QueryNode);
