import { X } from 'lucide-react';

interface NodeDeleteButtonProps {
  nodeId: string;
  onDelete: (nodeId: string) => void;
}

export const NodeDeleteButton = ({ nodeId, onDelete }: NodeDeleteButtonProps) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this node?')) {
      onDelete(nodeId);
    }
  };

  return (
    <button
      onClick={handleDelete}
      className="ml-1 p-0.5 rounded hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors"
      title="Delete node"
    >
      <X className="w-4 h-4" />
    </button>
  );
};
