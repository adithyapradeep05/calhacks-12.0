import { useState } from 'react';
import { Send, ChevronDown, ChevronUp, Copy, Trash2, Download, FileText } from 'lucide-react';
import { useWorkflowStore } from '@/state/useWorkflowStore';
import { queryRAG } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import ReactMarkdown from 'react-markdown';

export const ChatPanel = ({ onToast }: { onToast: (message: string, type: 'success' | 'error' | 'info') => void }) => {
  const { namespace, setNamespace, nodes, updateNodeData, updateNodeStatus } = useWorkflowStore();
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [context, setContext] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [showSources, setShowSources] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;

    if (!namespace) {
      onToast('Please set a namespace first', 'error');
      return;
    }

    // Check if upload and embed are done
    const uploadNode = nodes.find(n => n.data.type === 'upload');
    const embedNode = nodes.find(n => n.data.type === 'embed');

    if (!uploadNode?.data.result || embedNode?.data.status !== 'success') {
      onToast('Please upload and embed a document first', 'error');
      return;
    }

    // Get k value from query node
    const queryNode = nodes.find(n => n.data.type === 'query');
    const k = queryNode?.data.config?.k || 4;

    setLoading(true);
    setAnswer('');
    setContext([]);

    // Update query node status
    if (queryNode) {
      updateNodeStatus(queryNode.id, 'running');
    }

    // Update LLM node status
    const llmNode = nodes.find(n => n.data.type === 'llm');
    if (llmNode) {
      updateNodeStatus(llmNode.id, 'running');
    }

    try {
      console.log('Starting query:', { namespace, query: question, k });
      
      const response = await queryRAG({
        namespace,
        query: question,
        k,
      });

      console.log('Query response received:', response);
      setAnswer(response.answer);
      setContext(response.context);

      // Update query node with results
      if (queryNode) {
        updateNodeData(queryNode.id, {
          result: { docs: response.context },
          status: 'success',
        });
        updateNodeStatus(queryNode.id, 'success');
      }

      // Update LLM node
      if (llmNode) {
        updateNodeData(llmNode.id, {
          result: { model: 'Claude Sonnet', tokens: response.answer.length },
          status: 'success',
        });
        updateNodeStatus(llmNode.id, 'success');
      }

      onToast('Answer generated successfully', 'success');
    } catch (error: any) {
      console.error('Query failed:', error);
      
      let errorMessage = 'Query failed';
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Query timed out (60s). The backend might be slow or overloaded. Please try again.';
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      onToast(errorMessage, 'error');
      
      if (queryNode) updateNodeStatus(queryNode.id, 'error');
      if (llmNode) updateNodeStatus(llmNode.id, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  const handleCopyAnswer = () => {
    if (answer) {
      navigator.clipboard.writeText(answer);
      onToast('Answer copied to clipboard', 'success');
    }
  };

  const handleClearChat = () => {
    if (confirm('Clear the current chat?')) {
      setAnswer('');
      setContext([]);
      setQuestion('');
      onToast('Chat cleared', 'info');
    }
  };

  const handleExportChat = () => {
    if (!answer) {
      onToast('No chat to export', 'info');
      return;
    }

    const exportData = {
      namespace,
      timestamp: new Date().toISOString(),
      question,
      answer,
      context,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ragflow-chat-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    onToast('Chat exported', 'success');
  };

  return (
    <div className="w-full h-full bg-card border-l border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Chat</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setAnswer('');
              setContext([]);
              setQuestion('');
              setNamespace('');
              // Reset all nodes
              nodes.forEach(node => {
                updateNodeData(node.id, { result: null, status: 'idle' });
                updateNodeStatus(node.id, 'idle');
              });
              onToast('Workflow reset', 'success');
            }}
            className="text-xs"
          >
            🆕 New
          </Button>
        </div>
        <div>
          <label className="text-sm text-muted-foreground mb-1 block">Namespace</label>
          <Input
            value={namespace}
            onChange={(e) => setNamespace(e.target.value)}
            placeholder="e.g., my-docs"
            className="w-full"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {answer && (
          <div className="space-y-3">
            <div className="bg-primary/10 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="text-sm font-medium text-primary">Answer</div>
                  {context.length > 0 && (
                    <div className="px-2 py-0.5 bg-primary/20 text-primary text-xs rounded-full">
                      {context.length} source{context.length !== 1 ? 's' : ''}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleCopyAnswer} title="Copy answer">
                    <Copy className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleClearChat} title="Clear chat">
                    <Trash2 className="w-3.5 h-3.5" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleExportChat} title="Export chat">
                    <Download className="w-3.5 h-3.5" />
                  </Button>
                </div>
              </div>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            </div>

            {context.length > 0 && (
              <div className="bg-muted rounded-lg p-4">
                <button
                  onClick={() => setShowSources(!showSources)}
                  className="flex items-center gap-2 text-sm font-medium text-foreground hover:text-primary transition-colors w-full"
                >
                  {showSources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  Show Sources ({context.length})
                </button>
                
                {showSources && (
                  <div className="mt-3 space-y-2">
                    {context.map((snippet, idx) => (
                      <div key={idx} className="bg-background rounded p-3 text-xs">
                        <div className="text-muted-foreground mb-1">Source {idx + 1}</div>
                        <div className="text-foreground">{snippet}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {!answer && !loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4 max-w-sm">
              <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
                <FileText className="w-8 h-8 text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Ready to Chat</h3>
                <p className="text-sm text-muted-foreground">
                  {namespace ? 
                    'Ask a question about your documents below.' : 
                    'Set a namespace and upload documents to begin.'
                  }
                </p>
              </div>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-muted-foreground">Generating answer...</p>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1"
            data-chat-input
          />
          <Button
            onClick={handleAsk}
            disabled={loading || !question.trim()}
            size="icon"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
        {!namespace && (
          <p className="text-xs text-muted-foreground mt-2">Set a namespace above to start querying</p>
        )}
      </div>
    </div>
  );
};
