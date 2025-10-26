import React, { useState } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { queryRAG } from '../lib/api';
import { QueryResponse } from '../lib/api';
import CategoryBadge from '../components/CategoryBadge';

interface EnhancedQueryNodeData {
  query?: string;
  queryResult?: QueryResponse;
  status: 'idle' | 'querying' | 'completed' | 'error';
  error?: string;
}

const EnhancedQueryNode: React.FC<NodeProps<EnhancedQueryNodeData>> = ({ 
  data, 
  selected 
}) => {
  const [query, setQuery] = useState<string>(data.query || '');
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(data.queryResult || null);
  const [status, setStatus] = useState<'idle' | 'querying' | 'completed' | 'error'>(data.status || 'idle');
  const [error, setError] = useState<string | null>(data.error || null);

  const handleQuery = async () => {
    if (!query.trim()) return;

    try {
      setStatus('querying');
      setError(null);

      const result = await queryRAG({
        query: query.trim(),
        namespace: 'default',
        max_results: 5
      });

      setQueryResult(result);
      setStatus('completed');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Query failed');
      setStatus('error');
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'error': return 'text-red-600';
      case 'querying': return 'text-blue-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed': return '✅';
      case 'error': return '❌';
      case 'querying': return '🔍';
      default: return '❓';
    }
  };

  return (
    <Card className={`w-96 ${selected ? 'ring-2 ring-blue-500' : ''}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <span>{getStatusIcon()}</span>
          Enhanced Query
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Query Input */}
        <div>
          <Textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question..."
            className="min-h-[100px] resize-none"
          />
        </div>

        {/* Query Button */}
        <Button 
          onClick={handleQuery} 
          disabled={!query.trim() || status === 'querying'}
          className="w-full"
        >
          {status === 'querying' ? 'Querying...' : 'Query'}
        </Button>

        {/* Query Results */}
        {queryResult && (
          <div className="space-y-4">
            {/* Answer */}
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium text-blue-800">Answer</span>
                <div className="flex items-center gap-2">
                  <CategoryBadge category={queryResult.category} />
                  <Badge variant="outline" className="text-blue-600 border-blue-600">
                    {queryResult.sources} sources
                  </Badge>
                  <Badge variant="outline" className="text-gray-600 border-gray-600">
                    {queryResult.processing_time_ms}ms
                  </Badge>
                </div>
              </div>
              <div className="text-sm text-gray-800">
                {queryResult.answer}
              </div>
            </div>

            {/* Context Sources */}
            {queryResult.context && queryResult.context.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-gray-700">Sources</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {queryResult.context.map((source, index) => (
                    <div key={index} className="p-2 bg-gray-50 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        <CategoryBadge category={source.category} />
                        <Badge variant="outline" className="text-xs">
                          Distance: {source.distance.toFixed(3)}
                        </Badge>
                      </div>
                      <div className="text-gray-700 line-clamp-3">
                        {source.content}
                      </div>
                      {source.metadata?.filename && (
                        <div className="text-gray-500 mt-1">
                          📄 {source.metadata.filename}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
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
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </Card>
  );
};

export default EnhancedQueryNode;
