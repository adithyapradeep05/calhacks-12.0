import { memo, useState, useCallback } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Upload, FileText, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { uploadFile } from '@/lib/api';
import { Button } from '@/components/ui/button';

const UploadNode = ({ id, data }: NodeProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const { updateNodeData, updateNodeStatus, setSelectedNode } = useWorkflowStore();

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      const validTypes = ['.pdf', '.txt', '.md'];
      const isValid = validTypes.some(ext => selectedFile.name.toLowerCase().endsWith(ext));
      
      if (isValid) {
        setFile(selectedFile);
        updateNodeStatus(id, 'ready');
      } else {
        alert('Please select a .pdf, .txt, or .md file');
      }
    }
  }, [id, updateNodeStatus]);

  const handleUpload = useCallback(async () => {
    if (!file) return;

    setUploading(true);
    updateNodeStatus(id, 'running');

    try {
      const result = await uploadFile(file);
      updateNodeData(id, {
        config: { filename: result.filename },
        result: result,
        status: 'success',
      });
      updateNodeStatus(id, 'success');
    } catch (error) {
      console.error('Upload failed:', error);
      updateNodeStatus(id, 'error');
    } finally {
      setUploading(false);
    }
  }, [file, id, updateNodeData, updateNodeStatus]);

  const statusColors = {
    idle: 'border-node-uploadBorder',
    ready: 'border-node-uploadBorder',
    running: 'border-warning animate-pulse',
    success: 'border-success',
    error: 'border-destructive',
  };

  return (
    <div className={`bg-node-upload border-2 ${statusColors[data.status]} rounded-lg shadow-md hover:shadow-lg transition-shadow min-w-[280px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 !bg-node-uploadBorder" />
      
      <div className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <Upload className="w-5 h-5 text-node-uploadBorder" />
          <h3 className="font-semibold text-foreground">{data.label}</h3>
          <div className={`ml-auto px-2 py-0.5 rounded text-xs font-medium ${
            data.status === 'success' ? 'bg-success text-success-foreground' :
            data.status === 'error' ? 'bg-destructive text-destructive-foreground' :
            data.status === 'running' ? 'bg-warning text-warning-foreground' :
            'bg-muted text-muted-foreground'
          }`}>
            {data.status === 'success' ? 'Uploaded' : 
             data.status === 'running' ? 'Uploading...' :
             data.status === 'error' ? 'Error' : 'Idle'}
          </div>
        </div>

        <div className="space-y-3">
          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center">
            <input
              type="file"
              id={`file-${id}`}
              className="hidden"
              accept=".pdf,.txt,.md"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label htmlFor={`file-${id}`} className="cursor-pointer">
              {file ? (
                <div className="flex items-center gap-2 justify-center text-sm">
                  <FileText className="w-4 h-4" />
                  <span className="font-medium">{file.name}</span>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  Click to select file (.pdf, .txt, .md)
                </div>
              )}
            </label>
          </div>

          <Button
            onClick={handleUpload}
            disabled={!file || uploading || data.status === 'success'}
            className="w-full"
            size="sm"
          >
            {uploading ? 'Uploading...' : data.status === 'success' ? 'Uploaded' : 'Upload'}
          </Button>

          {data.config?.filename && (
            <div className="text-xs text-muted-foreground">
              Uploaded: {data.config.filename}
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

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 !bg-node-uploadBorder" />
    </div>
  );
};

export default memo(UploadNode);
