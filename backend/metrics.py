"""
Prometheus metrics for RAGFlow system monitoring
"""

import time
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry, generate_latest
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collector for RAGFlow system metrics"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize all Prometheus metrics"""
        
        # Request metrics
        self.request_total = Counter(
            'ragflow_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'ragflow_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Classification metrics
        self.classification_total = Counter(
            'ragflow_classifications_total',
            'Total number of document classifications',
            ['category', 'confidence_level'],
            registry=self.registry
        )
        
        self.classification_accuracy = Gauge(
            'ragflow_classification_accuracy',
            'Classification accuracy by category',
            ['category'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_requests_total = Counter(
            'ragflow_cache_requests_total',
            'Total cache requests',
            ['level', 'result'],
            registry=self.registry
        )
        
        self.cache_hit_rate = Gauge(
            'ragflow_cache_hit_rate',
            'Cache hit rate by level',
            ['level'],
            registry=self.registry
        )
        
        # Vector database metrics
        self.vector_db_queries_total = Counter(
            'ragflow_vector_db_queries_total',
            'Total vector database queries',
            ['category', 'operation'],
            registry=self.registry
        )
        
        self.vector_db_documents = Gauge(
            'ragflow_vector_db_documents',
            'Number of documents in vector database',
            ['category'],
            registry=self.registry
        )
        
        # Query routing metrics
        self.query_routing_total = Counter(
            'ragflow_query_routing_total',
            'Total query routing operations',
            ['category', 'confidence_level'],
            registry=self.registry
        )
        
        self.query_routing_accuracy = Gauge(
            'ragflow_query_routing_accuracy',
            'Query routing accuracy',
            registry=self.registry
        )
        
        # System metrics
        self.active_connections = Gauge(
            'ragflow_active_connections',
            'Number of active connections',
            registry=self.registry
        )
        
        self.system_info = Info(
            'ragflow_system_info',
            'System information',
            registry=self.registry
        )
        
        # Performance metrics
        self.embedding_generation_time = Histogram(
            'ragflow_embedding_generation_seconds',
            'Time to generate embeddings',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.llm_response_time = Histogram(
            'ragflow_llm_response_seconds',
            'Time for LLM response generation',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'ragflow_errors_total',
            'Total number of errors',
            ['error_type', 'component'],
            registry=self.registry
        )
        
        # Initialize system info
        self.system_info.info({
            'version': '2.0.0',
            'component': 'ragflow-backend'
        })
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record request metrics"""
        self.request_total.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_classification(self, category: str, confidence: float):
        """Record classification metrics"""
        confidence_level = self._get_confidence_level(confidence)
        self.classification_total.labels(category=category, confidence_level=confidence_level).inc()
    
    def update_classification_accuracy(self, category: str, accuracy: float):
        """Update classification accuracy"""
        self.classification_accuracy.labels(category=category).set(accuracy)
    
    def record_cache_request(self, level: str, hit: bool):
        """Record cache request"""
        result = "hit" if hit else "miss"
        self.cache_requests_total.labels(level=level, result=result).inc()
    
    def update_cache_hit_rate(self, level: str, hit_rate: float):
        """Update cache hit rate"""
        self.cache_hit_rate.labels(level=level).set(hit_rate)
    
    def record_vector_db_query(self, category: str, operation: str):
        """Record vector database query"""
        self.vector_db_queries_total.labels(category=category, operation=operation).inc()
    
    def update_vector_db_documents(self, category: str, count: int):
        """Update vector database document count"""
        self.vector_db_documents.labels(category=category).set(count)
    
    def record_query_routing(self, category: str, confidence: float):
        """Record query routing"""
        confidence_level = self._get_confidence_level(confidence)
        self.query_routing_total.labels(category=category, confidence_level=confidence_level).inc()
    
    def update_query_routing_accuracy(self, accuracy: float):
        """Update query routing accuracy"""
        self.query_routing_accuracy.set(accuracy)
    
    def update_active_connections(self, count: int):
        """Update active connections count"""
        self.active_connections.set(count)
    
    def record_embedding_generation(self, provider: str, model: str, duration: float):
        """Record embedding generation time"""
        self.embedding_generation_time.labels(provider=provider, model=model).observe(duration)
    
    def record_llm_response(self, provider: str, model: str, duration: float):
        """Record LLM response time"""
        self.llm_response_time.labels(provider=provider, model=model).observe(duration)
    
    def record_error(self, error_type: str, component: str):
        """Record error"""
        self.errors_total.labels(error_type=error_type, component=component).inc()
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level"""
        if confidence >= 0.9:
            return "high"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.5:
            return "low"
        else:
            return "very_low"
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode('utf-8')
    
    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        metrics_data = {}
        
        # Collect all metric values
        for metric in self.registry.collect():
            metric_name = metric.name
            metric_type = metric.type
            
            if metric_type == 'counter':
                metrics_data[metric_name] = {
                    'type': 'counter',
                    'value': sum(sample.value for sample in metric.samples)
                }
            elif metric_type == 'gauge':
                metrics_data[metric_name] = {
                    'type': 'gauge',
                    'value': sum(sample.value for sample in metric.samples)
                }
            elif metric_type == 'histogram':
                metrics_data[metric_name] = {
                    'type': 'histogram',
                    'count': sum(sample.value for sample in metric.samples if sample.name.endswith('_count')),
                    'sum': sum(sample.value for sample in metric.samples if sample.name.endswith('_sum'))
                }
            elif metric_type == 'info':
                metrics_data[metric_name] = {
                    'type': 'info',
                    'value': dict(metric.samples[0].labels) if metric.samples else {}
                }
        
        return metrics_data

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Convenience functions
def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record request metrics"""
    metrics_collector.record_request(method, endpoint, status, duration)

def record_classification(category: str, confidence: float):
    """Record classification metrics"""
    metrics_collector.record_classification(category, confidence)

def update_classification_accuracy(category: str, accuracy: float):
    """Update classification accuracy"""
    metrics_collector.update_classification_accuracy(category, accuracy)

def record_cache_request(level: str, hit: bool):
    """Record cache request"""
    metrics_collector.record_cache_request(level, hit)

def update_cache_hit_rate(level: str, hit_rate: float):
    """Update cache hit rate"""
    metrics_collector.update_cache_hit_rate(level, hit_rate)

def record_vector_db_query(category: str, operation: str):
    """Record vector database query"""
    metrics_collector.record_vector_db_query(category, operation)

def update_vector_db_documents(category: str, count: int):
    """Update vector database document count"""
    metrics_collector.update_vector_db_documents(category, count)

def record_query_routing(category: str, confidence: float):
    """Record query routing"""
    metrics_collector.record_query_routing(category, confidence)

def update_query_routing_accuracy(accuracy: float):
    """Update query routing accuracy"""
    metrics_collector.update_query_routing_accuracy(accuracy)

def update_active_connections(count: int):
    """Update active connections count"""
    metrics_collector.update_active_connections(count)

def record_embedding_generation(provider: str, model: str, duration: float):
    """Record embedding generation time"""
    metrics_collector.record_embedding_generation(provider, model, duration)

def record_llm_response(provider: str, model: str, duration: float):
    """Record LLM response time"""
    metrics_collector.record_llm_response(provider, model, duration)

def record_error(error_type: str, component: str):
    """Record error"""
    metrics_collector.record_error(error_type, component)

def get_metrics() -> str:
    """Get metrics in Prometheus format"""
    return metrics_collector.get_metrics()

def get_metrics_dict() -> Dict[str, Any]:
    """Get metrics as dictionary"""
    return metrics_collector.get_metrics_dict()
