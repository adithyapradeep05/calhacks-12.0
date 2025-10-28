import { memo, useState, useCallback, useEffect } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Upload, FileText, Settings } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { uploadFile } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { NodeDeleteButton } from '@/components/NodeDeleteButton';

const UploadNode = ({ id, data }: NodeProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const { updateNodeData, updateNodeStatus, setSelectedNode, deleteNode } = useWorkflowStore();

  // Reset local file state when node is reset to idle with no result
  useEffect(() => {
    if (data.status === 'idle' && !data.result) {
      setFile(null);
    }
  }, [data.status, data.result]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      console.log('File selected:', selectedFile.name, 'Size:', selectedFile.size);
      const validTypes = ['.pdf', '.txt', '.md'];
      const isValid = validTypes.some(ext => selectedFile.name.toLowerCase().endsWith(ext));
      
      if (isValid) {
        setFile(selectedFile);
        updateNodeStatus(id, 'ready');
        console.log('File is valid, ready for upload');
      } else {
        console.log('Invalid file type:', selectedFile.name);
        alert('Please select a .pdf, .txt, or .md file');
      }
    }
  }, [id, updateNodeStatus]);

  const handleUpload = useCallback(async () => {
    if (!file) return;

    setUploading(true);
    updateNodeStatus(id, 'running');

    try {
      console.log('Starting upload for file:', file.name);
      const result = await uploadFile(file);
      console.log('Upload successful:', result);
      
      updateNodeData(id, {
        config: { filename: result.filename },
        result: result,
        status: 'success',
      });
      updateNodeStatus(id, 'success');
    } catch (error: any) {
      console.error('Upload failed:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed';
      console.error('Error details:', errorMessage);
      updateNodeStatus(id, 'error');
      
      // Show user-friendly error message
      alert(`Upload failed: ${errorMessage}`);
    } finally {
      setUploading(false);
    }
  }, [file, id, updateNodeData, updateNodeStatus]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      console.log('File dropped:', droppedFile.name, 'Size:', droppedFile.size);
      const validTypes = ['.pdf', '.txt', '.md'];
      const isValid = validTypes.some(ext => droppedFile.name.toLowerCase().endsWith(ext));
      
      if (isValid) {
        setFile(droppedFile);
        updateNodeStatus(id, 'ready');
        console.log('Dropped file is valid, ready for upload');
      } else {
        console.log('Invalid dropped file type:', droppedFile.name);
        alert('Please drop a .pdf, .txt, or .md file');
      }
    }
  }, [id, updateNodeStatus]);

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
          <NodeDeleteButton nodeId={id} onDelete={deleteNode} />
        </div>

        <div className="space-y-3">
          <div 
            className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
              dragOver ? 'border-primary bg-primary/5' : 
              file ? 'border-green-500 bg-green-50' : 
              'border-border hover:border-primary/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id={`file-${id}`}
              className="hidden"
              accept=".pdf,.txt,.md"
              onChange={handleFileChange}
              disabled={uploading}
            />
            <label htmlFor={`file-${id}`} className="cursor-pointer block">
              {file ? (
                <div className="flex items-center gap-2 justify-center text-sm">
                  <FileText className="w-4 h-4 text-green-600" />
                  <span className="font-medium text-green-700">{file.name}</span>
                  <span className="text-xs text-muted-foreground">({Math.round(file.size / 1024)} KB)</span>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  <div className="mb-2">
                    {dragOver ? '📁 Drop file here' : '📁 Click to select file or drag & drop'}
                  </div>
                  <div className="text-xs">Supports: .pdf, .txt, .md</div>
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
            {uploading ? 'Uploading...' : 
             data.status === 'success' ? '✅ Uploaded' : 
             !file ? 'Select a file first' : 
             '📤 Upload File'}
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
