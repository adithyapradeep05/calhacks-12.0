import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UploadResponse {
  file_id: string;
  path: string;
  filename: string;
}

export interface EmbedRequest {
  path: string;
  namespace: string;
}

export interface EmbedResponse {
  chunks: number;
  namespace: string;
}

export interface QueryRequest {
  namespace: string;
  query: string;
  k?: number;
}

export interface QueryResponse {
  answer: string;
  context: string[];
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

export default api;
