import React, { useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { uploadFile, embedDocument } from '../lib/api';
import { UploadResponse, EmbedResponse } from '../lib/api';
import CategoryBadge from '../components/CategoryBadge';

interface EnhancedUploadNodeData {
  file?: File;
  uploadResult?: UploadResponse;
  embedResult?: EmbedResponse;
  status: 'idle' | 'uploading' | 'embedding' | 'completed' | 'error';
  error?: string;
}

const EnhancedUploadNode: React.FC<NodeProps<EnhancedUploadNodeData>> = ({ 
  data, 
  selected 
}) => {
  const [file, setFile] = useState<File | null>(data.file || null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(data.uploadResult || null);
  const [embedResult, setEmbedResult] = useState<EmbedResponse | null>(data.embedResult || null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'embedding' | 'completed' | 'error'>(data.status || 'idle');
  const [error, setError] = useState<string | null>(data.error || null);
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setStatus('idle');
      setError(null);
      setUploadResult(null);
      setEmbedResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setStatus('uploading');
      setProgress(0);
      setError(null);

      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const result = await uploadFile(file);
      clearInterval(progressInterval);
      setProgress(100);
      
      setUploadResult(result);
      setStatus('embedding');

      // Auto-embed after upload
      const embedResult = await embedDocument({
        document_id: result.document_id,
        namespace: 'default'
      });

      setEmbedResult(embedResult);
      setStatus('completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setStatus('error');
      setProgress(0);
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'uploading': return 'text-blue-600';
      case 'embedding': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed': return '✅';
      case 'error': return '❌';
      case 'uploading': return '📤';
      case 'embedding': return '🔄';
      default: return '📄';
    }
  };

  return (
    <Card className={`w-80 ${selected ? 'ring-2 ring-blue-500' : ''}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <span>{getStatusIcon()}</span>
          Enhanced Upload
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* File Input */}
        <div>
          <input
            type="file"
            onChange={handleFileSelect}
            className="w-full p-2 border border-gray-300 rounded-md text-sm"
            accept=".pdf,.txt,.md,.doc,.docx"
          />
          {file && (
            <div className="mt-2 text-sm text-gray-600">
              <strong>Selected:</strong> {file.name}
              <br />
              <strong>Size:</strong> {(file.size / 1024).toFixed(1)} KB
            </div>
          )}
        </div>

        {/* Upload Button */}
        <Button 
          onClick={handleUpload} 
          disabled={!file || status === 'uploading' || status === 'embedding'}
          className="w-full"
        >
          {status === 'uploading' ? 'Uploading...' : 
           status === 'embedding' ? 'Embedding...' : 
           'Upload & Embed'}
        </Button>

        {/* Progress Bar */}
        {(status === 'uploading' || status === 'embedding') && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{status === 'uploading' ? 'Uploading' : 'Embedding'}</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>
        )}

        {/* Upload Results */}
        {uploadResult && (
          <div className="space-y-2 p-3 bg-green-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-green-800">Upload Successful</span>
              <Badge variant="outline" className="text-green-600 border-green-600">
                {uploadResult.filename}
              </Badge>
            </div>
            
            <div className="space-y-1 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-gray-600">Category:</span>
                <CategoryBadge 
                  category={uploadResult.category} 
                  confidence={uploadResult.confidence}
                />
              </div>
              <div className="text-gray-600">
                <strong>ID:</strong> {uploadResult.document_id.slice(0, 8)}...
              </div>
            </div>
          </div>
        )}

        {/* Embed Results */}
        {embedResult && (
          <div className="space-y-2 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-blue-800">Embedding Complete</span>
              <Badge variant="outline" className="text-blue-600 border-blue-600">
                {embedResult.chunks_processed} chunks
              </Badge>
            </div>
            
            <div className="text-sm text-gray-600">
              <strong>Category:</strong> {embedResult.category}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 rounded-lg">
            <div className="text-sm text-red-800">
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {/* Status */}
        <div className={`text-sm ${getStatusColor()}`}>
          Status: {status.charAt(0).toUpperCase() + status.slice(1)}
        </div>
      </CardContent>

      {/* Handles */}
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </Card>
  );
};

export default EnhancedUploadNode;
