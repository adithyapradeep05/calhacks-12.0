import { File, Save, Play, Moon, Sun } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { useTheme } from '@/hooks/useTheme';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export const Toolbar = ({ onToast }: { onToast: (message: string, type: 'success' | 'error' | 'info') => void }) => {
  const { namespace, setNamespace, resetWorkflow, saveWorkflow, nodes, selectedNode } = useWorkflowStore();
  const { theme, toggleTheme } = useTheme();

  const handleNew = () => {
    if (confirm('Create a new workflow? This will clear the current workflow.')) {
      resetWorkflow();
      onToast('New workflow created', 'info');
    }
  };

  const handleSave = () => {
    saveWorkflow();
    
    // Download JSON
    const data = {
      nodes,
      namespace,
      timestamp: new Date().toISOString(),
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'velora-workflow.json';
    a.click();
    URL.revokeObjectURL(url);
    
    onToast('Workflow saved and downloaded', 'success');
  };

  const handleRunFromStart = async () => {
    const uploadNode = nodes.find(n => n.data.type === 'upload');
    const embedNode = nodes.find(n => n.data.type === 'embed');

    if (!uploadNode?.data.result) {
      onToast('Please upload a document first', 'error');
      return;
    }

    if (embedNode?.data.status !== 'success') {
      onToast('Please embed the document first', 'error');
      return;
    }

    onToast('Pipeline ready! Use the chat panel to ask questions.', 'success');
  };

  return (
    <div className="bg-card border-b border-border p-3 flex items-center gap-3">
      <div className="flex items-center gap-2 mr-4">
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">V</span>
        </div>
        <h1 className="text-lg font-bold">Velora</h1>
      </div>

      <Button variant="outline" size="sm" onClick={handleNew}>
        <File className="w-4 h-4 mr-2" />
        New
      </Button>

      <Button variant="outline" size="sm" onClick={handleSave}>
        <Save className="w-4 h-4 mr-2" />
        Save
      </Button>

      <Button variant="default" size="sm" onClick={handleRunFromStart}>
        <Play className="w-4 h-4 mr-2" />
        Run from Start
      </Button>

      <div className="ml-auto flex items-center gap-2">
        <Button variant="ghost" size="icon" onClick={toggleTheme} title="Toggle theme">
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
      </div>
    </div>
  );
};
