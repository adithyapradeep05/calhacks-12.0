import { useCallback, useState } from 'react';
import { Upload, Sparkles, Database, Search, Brain } from 'lucide-react';

interface BlockShelfProps {
  onAddNode: (nodeType: string) => void;
}

interface BlockDefinition {
  id: string;
  label: string;
  icon: React.ReactNode;
  iconColor: string;
  color: string;
  description: string;
}

const blockDefinitions: BlockDefinition[] = [
  {
    id: 'uploadNode',
    label: 'Upload Docs',
    icon: <Upload className="w-5 h-5" />,
    iconColor: 'text-node-uploadBorder',
    color: 'bg-node-upload border-node-uploadBorder',
    description: 'Upload PDFs, text, or markdown files',
  },
  {
    id: 'embedNode',
    label: 'Embed',
    icon: <Sparkles className="w-5 h-5" />,
    iconColor: 'text-node-embedBorder',
    color: 'bg-node-embed border-node-embedBorder',
    description: 'Convert text to embeddings',
  },
  {
    id: 'storeNode',
    label: 'Store (Chroma)',
    icon: <Database className="w-5 h-5" />,
    iconColor: 'text-node-storeBorder',
    color: 'bg-node-store border-node-storeBorder',
    description: 'Vector database storage',
  },
  {
    id: 'queryNode',
    label: 'Query',
    icon: <Search className="w-5 h-5" />,
    iconColor: 'text-node-queryBorder',
    color: 'bg-node-query border-node-queryBorder',
    description: 'Retrieve relevant chunks',
  },
  {
    id: 'llmNode',
    label: 'LLM Response',
    icon: <Brain className="w-5 h-5" />,
    iconColor: 'text-node-llmBorder',
    color: 'bg-node-llm border-node-llmBorder',
    description: 'Generate AI responses',
  },
];

export const BlockShelf = ({ onAddNode }: BlockShelfProps) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleDragStart = useCallback((e: React.DragEvent, nodeType: string) => {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('application/reactflow', nodeType);
  }, []);

  return (
    <div className="h-full bg-card border-r border-border flex flex-col">
      {/* Header */}
      <div 
        className="p-4 border-b border-border cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm">Node Blocks</h3>
          <span className="text-xs text-muted-foreground">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>

      {/* Block List */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {blockDefinitions.map((block) => (
            <div
              key={block.id}
              draggable
                className={`${block.color} border-2 rounded-lg shadow-md hover:shadow-lg transition-all cursor-move active:opacity-50`}
              onDragStart={(e) => handleDragStart(e, block.id)}
              onClick={() => onAddNode(block.id)}
            >
              <div className="p-3">
                <div className="flex items-center gap-2 mb-2">
                  <div className={block.iconColor}>
                    {block.icon}
                  </div>
                  <span className="font-medium text-sm text-foreground">
                    {block.label}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {block.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Section */}
      {isExpanded && (
        <div className="p-3 border-t border-border text-xs text-muted-foreground">
          <p className="mb-1">💡 Drag blocks onto canvas</p>
          <p>or click to add at center</p>
        </div>
      )}
    </div>
  );
};
