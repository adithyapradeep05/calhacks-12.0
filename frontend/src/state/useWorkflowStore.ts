import { create } from 'zustand';
import { Node, Edge, Connection, addEdge, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from 'reactflow';

export type NodeStatus = 'idle' | 'ready' | 'running' | 'success' | 'error';

export interface NodeData {
  label: string;
  type: string;
  status: NodeStatus;
  config?: any;
  result?: any;
}

interface WorkflowState {
  nodes: Node<NodeData>[];
  edges: Edge[];
  namespace: string;
  selectedNode: string | null;
  lastRunMetadata: Record<string, any>;
  
  setNodes: (nodes: Node<NodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  setNamespace: (namespace: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  updateNodeData: (nodeId: string, data: Partial<NodeData>) => void;
  updateNodeStatus: (nodeId: string, status: NodeStatus) => void;
  resetWorkflow: () => void;
  saveWorkflow: () => void;
  loadWorkflow: (data: any) => void;
  addNode: (nodeType: string, position: { x: number; y: number }) => void;
  deleteNode: (nodeId: string) => void;
}

const STORAGE_KEY = 'ragflow-workflow';

const defaultNodes: Node<NodeData>[] = [
  {
    id: '1',
    type: 'uploadNode',
    position: { x: 100, y: 100 },
    data: { label: 'Upload Docs', type: 'upload', status: 'idle' },
  },
  {
    id: '2',
    type: 'embedNode',
    position: { x: 100, y: 250 },
    data: { label: 'Embed', type: 'embed', status: 'idle' },
  },
  {
    id: '3',
    type: 'storeNode',
    position: { x: 100, y: 400 },
    data: { label: 'Store (Chroma)', type: 'store', status: 'idle' },
  },
  {
    id: '4',
    type: 'queryNode',
    position: { x: 100, y: 550 },
    data: { label: 'Query', type: 'query', status: 'idle' },
  },
  {
    id: '5',
    type: 'llmNode',
    position: { x: 100, y: 700 },
    data: { label: 'LLM Response', type: 'llm', status: 'idle' },
  },
];

const defaultEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: false },
  { id: 'e2-3', source: '2', target: '3', animated: false },
  { id: 'e3-4', source: '3', target: '4', animated: false },
  { id: 'e4-5', source: '4', target: '5', animated: false },
];

const loadFromStorage = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const data = JSON.parse(stored);
      return {
        nodes: data.nodes || defaultNodes,
        edges: data.edges || defaultEdges,
        namespace: data.namespace || '',
      };
    }
  } catch (error) {
    console.error('Failed to load workflow from storage:', error);
  }
  return { nodes: defaultNodes, edges: defaultEdges, namespace: '' };
};

const initialState = loadFromStorage();

export const useWorkflowStore = create<WorkflowState>((set, get) => ({
  nodes: initialState.nodes,
  edges: initialState.edges,
  namespace: initialState.namespace,
  selectedNode: null,
  lastRunMetadata: {},

  setNodes: (nodes) => set({ nodes }),
  
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set({
      nodes: applyNodeChanges(changes, get().nodes),
    });
  },

  onEdgesChange: (changes) => {
    set({
      edges: applyEdgeChanges(changes, get().edges),
    });
  },

  onConnect: (connection) => {
    const { nodes } = get();
    const sourceNode = nodes.find(n => n.id === connection.source);
    const targetNode = nodes.find(n => n.id === connection.target);

    // Validate connection based on node types
    const validConnections: Record<string, string[]> = {
      upload: ['embed'],
      embed: ['store'],
      store: ['query'],
      query: ['llm'],
      llm: [],
    };

    if (sourceNode && targetNode) {
      const sourceType = sourceNode.data.type;
      const targetType = targetNode.data.type;
      
      if (!validConnections[sourceType]?.includes(targetType)) {
        console.warn(`Invalid connection: ${sourceType} → ${targetType}`);
        return;
      }
    }

    set({
      edges: addEdge(connection, get().edges),
    });
  },

  setNamespace: (namespace) => {
    set({ namespace });
    get().saveWorkflow();
  },

  setSelectedNode: (nodeId) => set({ selectedNode: nodeId }),

  updateNodeData: (nodeId, data) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...data } }
          : node
      ),
    });
    get().saveWorkflow();
  },

  updateNodeStatus: (nodeId, status) => {
    set({
      nodes: get().nodes.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, status } }
          : node
      ),
    });
  },

  resetWorkflow: () => {
    set({
      nodes: defaultNodes,
      edges: defaultEdges,
      namespace: '',
      selectedNode: null,
      lastRunMetadata: {},
    });
    localStorage.removeItem(STORAGE_KEY);
  },

  saveWorkflow: () => {
    const { nodes, edges, namespace } = get();
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ nodes, edges, namespace })
      );
    } catch (error) {
      console.error('Failed to save workflow:', error);
    }
  },

  loadWorkflow: (data) => {
    set({
      nodes: data.nodes || defaultNodes,
      edges: data.edges || defaultEdges,
      namespace: data.namespace || '',
    });
    get().saveWorkflow();
  },

  addNode: (nodeType, position) => {
    const newNodeId = `node-${Date.now()}`;
    const nodeConfig: Record<string, { label: string; type: string }> = {
      uploadNode: { label: 'Upload Docs', type: 'upload' },
      embedNode: { label: 'Embed', type: 'embed' },
      storeNode: { label: 'Store (Chroma)', type: 'store' },
      queryNode: { label: 'Query', type: 'query' },
      llmNode: { label: 'LLM Response', type: 'llm' },
    };

    const config = nodeConfig[nodeType];
    if (!config) return;

    const newNode: Node<NodeData> = {
      id: newNodeId,
      type: nodeType,
      position,
      data: {
        ...config,
        status: 'idle',
      },
    };

    set({
      nodes: [...get().nodes, newNode],
    });
    get().saveWorkflow();
  },

  deleteNode: (nodeId) => {
    const { nodes, edges } = get();
    
    // Remove the node
    const updatedNodes = nodes.filter(n => n.id !== nodeId);
    
    // Remove all edges connected to this node
    const updatedEdges = edges.filter(
      e => e.source !== nodeId && e.target !== nodeId
    );

    // Clear selection if deleted node was selected
    const clearSelection = get().selectedNode === nodeId;

    set({
      nodes: updatedNodes,
      edges: updatedEdges,
      selectedNode: clearSelection ? null : get().selectedNode,
    });
    get().saveWorkflow();
  },
}));
