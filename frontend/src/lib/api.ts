import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout
});

export interface UploadResponse {
  message: string;
  document_id: string;
  filename: string;
  category: string;
  confidence: number;
  storage_path: string;
}

export interface EmbedRequest {
  document_id: string;
  namespace: string;
}

export interface EmbedResponse {
  message: string;
  document_id: string;
  chunks_processed: number;
  category: string;
}

export interface QueryRequest {
  query: string;
  namespace: string;
  max_results?: number;
}

export interface QueryResponse {
  answer: string;
  context: Array<{
    content: string;
    metadata: Record<string, any>;
    distance: number;
    category: string;
  }>;
  category: string;
  sources: number;
  processing_time_ms: number;
}

export interface StatsResponse {
  total_documents: number;
  total_chunks: number;
  categories: Record<string, number>;
  cache_stats: Record<string, any>;
  classification_stats: Record<string, any>;
}

export interface ClassificationResponse {
  category: string;
  confidence: number;
  reasoning: string;
  processing_time_ms: number;
}

export interface CacheStatsResponse {
  cache_statistics: Record<string, any>;
  health_status: Record<string, any>;
  timestamp: number;
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const embedDocument = async (data: EmbedRequest): Promise<EmbedResponse> => {
  const response = await api.post<EmbedResponse>('/embed', data);
  return response.data;
};

export const queryRAG = async (data: QueryRequest): Promise<QueryResponse> => {
  const response = await api.post<QueryResponse>('/query', data);
  return response.data;
};

export const getStats = async (): Promise<StatsResponse> => {
  const response = await api.get<StatsResponse>('/stats');
  return response.data;
};

export const classifyDocument = async (text: string, filename: string = ''): Promise<ClassificationResponse> => {
  const response = await api.post<ClassificationResponse>('/classify', { text, filename });
  return response.data;
};

export const getCacheStats = async (): Promise<CacheStatsResponse> => {
  const response = await api.get<CacheStatsResponse>('/cache/stats');
  return response.data;
};

export default api;
