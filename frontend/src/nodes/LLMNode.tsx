import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Brain, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';

const LLMNode = ({ id, data }: NodeProps) => {
  const { setSelectedNode } = useWorkflowStore();

  const statusColors = {
    idle: 'border-node-llmBorder',
    ready: 'border-node-llmBorder',
    running: 'border-warning animate-pulse',
    success: 'border-success',
    error: 'border-destructive',
  };

  return (
    <div className={`bg-node-llm border-2 ${statusColors[data.status]} rounded-lg shadow-md hover:shadow-lg transition-shadow min-w-[280px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-node-llmBorder" />
      
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Brain className="w-5 h-5 text-node-llmBorder" />
          <h3 className="font-semibold text-foreground">{data.label}</h3>
          <div className={`ml-auto px-2 py-0.5 rounded text-xs font-medium ${
            data.status === 'success' ? 'bg-success text-success-foreground' :
            'bg-muted text-muted-foreground'
          }`}>
            {data.status === 'success' ? 'Responded' : 'Ready'}
          </div>
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Model:</span>
            <span className="font-medium">{data.result?.model || 'GPT-4'}</span>
          </div>

          {data.result?.tokens && (
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Tokens:</span>
              <span className="font-medium">{data.result.tokens}</span>
            </div>
          )}

          {data.status === 'success' && (
            <div className="mt-3 p-2 bg-success/10 rounded text-xs text-success">
              ✓ Answer generated successfully
            </div>
          )}

          <div className="text-xs text-muted-foreground mt-2">
            Response displayed in chat panel
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
    </div>
  );
};

export default memo(LLMNode);
