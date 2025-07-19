"""
Performance Monitoring System for GrantSpider AMIF Assistant
Tracks response times, memory usage, agent execution metrics, and system performance
"""

import time
import psutil
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import json
import os
from pathlib import Path

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: datetime
    metric_type: str
    value: float
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type,
            "value": self.value,
            "metadata": self.metadata or {}
        }

@dataclass
class QueryMetrics:
    """Metrics for a single query execution"""
    query_id: str
    query_text: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration: Optional[float] = None
    
    # Agent-specific timings
    retrieval_duration: Optional[float] = None
    qa_duration: Optional[float] = None
    source_tracking_duration: Optional[float] = None
    
    # Document metrics
    documents_retrieved: int = 0
    sources_generated: int = 0
    
    # Language and success metrics
    detected_language: str = "unknown"
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "query_id": self.query_id,
            "query_text": self.query_text[:100] + "..." if len(self.query_text) > 100 else self.query_text,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration": self.total_duration,
            "retrieval_duration": self.retrieval_duration,
            "qa_duration": self.qa_duration,
            "source_tracking_duration": self.source_tracking_duration,
            "documents_retrieved": self.documents_retrieved,
            "sources_generated": self.sources_generated,
            "detected_language": self.detected_language,
            "success": self.success,
            "error_message": self.error_message
        }

class PerformanceMonitor:
    """Main performance monitoring system"""
    
    def __init__(self, max_metrics: int = 1000, persistence_path: str = "data/metrics"):
        """
        Initialize performance monitor
        
        Args:
            max_metrics: Maximum number of metrics to keep in memory
            persistence_path: Path to save metrics to disk
        """
        self.max_metrics = max_metrics
        self.persistence_path = Path(persistence_path)
        self.persistence_path.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.metrics: deque = deque(maxlen=max_metrics)
        self.query_metrics: Dict[str, QueryMetrics] = {}
        self.active_queries: Dict[str, QueryMetrics] = {}
        
        # Aggregated statistics
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "total_documents_processed": 0,
            "system_start_time": datetime.now()
        }
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
        
        # Start system monitoring thread
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._system_monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def start_query(self, query_id: str, query_text: str) -> QueryMetrics:
        """
        Start tracking a new query
        
        Args:
            query_id: Unique identifier for the query
            query_text: The actual query text
            
        Returns:
            QueryMetrics object for this query
        """
        with self._lock:
            query_metrics = QueryMetrics(
                query_id=query_id,
                query_text=query_text,
                start_time=datetime.now()
            )
            
            self.active_queries[query_id] = query_metrics
            self.stats["total_queries"] += 1
            
            return query_metrics
    
    def end_query(self, query_id: str, success: bool = True, error_message: str = None) -> Optional[QueryMetrics]:
        """
        End tracking for a query
        
        Args:
            query_id: Query identifier
            success: Whether query was successful
            error_message: Error message if failed
            
        Returns:
            Completed QueryMetrics object
        """
        with self._lock:
            if query_id not in self.active_queries:
                return None
            
            query_metrics = self.active_queries.pop(query_id)
            query_metrics.end_time = datetime.now()
            query_metrics.total_duration = (query_metrics.end_time - query_metrics.start_time).total_seconds()
            query_metrics.success = success
            query_metrics.error_message = error_message
            
            # Store completed query
            self.query_metrics[query_id] = query_metrics
            
            # Update stats
            if success:
                self.stats["successful_queries"] += 1
            else:
                self.stats["failed_queries"] += 1
            
            # Update average response time
            successful_queries = [q for q in self.query_metrics.values() if q.success and q.total_duration]
            if successful_queries:
                self.stats["avg_response_time"] = sum(q.total_duration for q in successful_queries) / len(successful_queries)
            
            return query_metrics
    
    def record_agent_timing(self, query_id: str, agent_name: str, duration: float):
        """
        Record timing for a specific agent
        
        Args:
            query_id: Query identifier
            agent_name: Name of the agent
            duration: Time taken in seconds
        """
        with self._lock:
            if query_id in self.active_queries:
                query_metrics = self.active_queries[query_id]
                
                if agent_name == "document_retriever":
                    query_metrics.retrieval_duration = duration
                elif agent_name == "qa_agent":
                    query_metrics.qa_duration = duration
                elif agent_name == "source_tracker":
                    query_metrics.source_tracking_duration = duration
    
    def record_document_metrics(self, query_id: str, documents_retrieved: int = 0, sources_generated: int = 0, detected_language: str = "unknown"):
        """
        Record document-related metrics
        
        Args:
            query_id: Query identifier
            documents_retrieved: Number of documents retrieved
            sources_generated: Number of sources generated
            detected_language: Detected language
        """
        with self._lock:
            if query_id in self.active_queries:
                query_metrics = self.active_queries[query_id]
                query_metrics.documents_retrieved = documents_retrieved
                query_metrics.sources_generated = sources_generated
                query_metrics.detected_language = detected_language
                
                self.stats["total_documents_processed"] += documents_retrieved
    
    def record_metric(self, metric_type: str, value: float, metadata: Dict[str, Any] = None):
        """
        Record a generic performance metric
        
        Args:
            metric_type: Type of metric (e.g., 'memory_usage', 'cpu_usage')
            value: Metric value
            metadata: Additional metadata
        """
        with self._lock:
            metric = PerformanceMetric(
                timestamp=datetime.now(),
                metric_type=metric_type,
                value=value,
                metadata=metadata
            )
            
            self.metrics.append(metric)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get current system statistics
        
        Returns:
            Dictionary of system statistics
        """
        with self._lock:
            # Get recent metrics
            current_time = datetime.now()
            recent_metrics = [m for m in self.metrics if (current_time - m.timestamp).total_seconds() < 300]  # Last 5 minutes
            
            # Calculate recent averages
            memory_metrics = [m.value for m in recent_metrics if m.metric_type == "memory_usage"]
            cpu_metrics = [m.value for m in recent_metrics if m.metric_type == "cpu_usage"]
            
            # Recent query performance
            recent_queries = [q for q in self.query_metrics.values() 
                            if q.end_time and (current_time - q.end_time).total_seconds() < 3600]  # Last hour
            
            return {
                "uptime_seconds": (current_time - self.stats["system_start_time"]).total_seconds(),
                "total_queries": self.stats["total_queries"],
                "successful_queries": self.stats["successful_queries"],
                "failed_queries": self.stats["failed_queries"],
                "success_rate": (self.stats["successful_queries"] / max(1, self.stats["total_queries"])) * 100,
                "avg_response_time": self.stats["avg_response_time"],
                "total_documents_processed": self.stats["total_documents_processed"],
                "active_queries": len(self.active_queries),
                "current_memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "current_cpu_percent": psutil.Process().cpu_percent(),
                "recent_avg_memory_mb": sum(memory_metrics) / len(memory_metrics) if memory_metrics else 0,
                "recent_avg_cpu_percent": sum(cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0,
                "recent_queries_count": len(recent_queries),
                "recent_avg_response_time": sum(q.total_duration for q in recent_queries if q.total_duration) / len(recent_queries) if recent_queries else 0
            }
    
    def get_query_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get query analytics for the specified time period
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary of query analytics
        """
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_queries = [q for q in self.query_metrics.values() 
                            if q.end_time and q.end_time >= cutoff_time]
            
            if not recent_queries:
                return {"message": "No queries in the specified time period"}
            
            # Response time analysis
            successful_queries = [q for q in recent_queries if q.success and q.total_duration]
            response_times = [q.total_duration for q in successful_queries]
            
            # Language distribution
            language_dist = defaultdict(int)
            for q in recent_queries:
                language_dist[q.detected_language] += 1
            
            # Agent performance
            retrieval_times = [q.retrieval_duration for q in successful_queries if q.retrieval_duration]
            qa_times = [q.qa_duration for q in successful_queries if q.qa_duration]
            source_times = [q.source_tracking_duration for q in successful_queries if q.source_tracking_duration]
            
            return {
                "time_period_hours": hours,
                "total_queries": len(recent_queries),
                "successful_queries": len(successful_queries),
                "success_rate": (len(successful_queries) / len(recent_queries)) * 100,
                "response_times": {
                    "avg": sum(response_times) / len(response_times) if response_times else 0,
                    "min": min(response_times) if response_times else 0,
                    "max": max(response_times) if response_times else 0,
                    "p95": sorted(response_times)[int(len(response_times) * 0.95)] if response_times else 0
                },
                "language_distribution": dict(language_dist),
                "agent_performance": {
                    "avg_retrieval_time": sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0,
                    "avg_qa_time": sum(qa_times) / len(qa_times) if qa_times else 0,
                    "avg_source_tracking_time": sum(source_times) / len(source_times) if source_times else 0
                },
                "document_metrics": {
                    "avg_documents_per_query": sum(q.documents_retrieved for q in recent_queries) / len(recent_queries),
                    "avg_sources_per_query": sum(q.sources_generated for q in recent_queries) / len(recent_queries)
                }
            }
    
    def save_metrics_to_disk(self):
        """Save current metrics to disk"""
        try:
            # Save system stats
            stats_file = self.persistence_path / "system_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, default=str, indent=2)
            
            # Save query metrics
            queries_file = self.persistence_path / f"queries_{datetime.now().strftime('%Y%m%d')}.json"
            query_data = [q.to_dict() for q in self.query_metrics.values()]
            with open(queries_file, 'w') as f:
                json.dump(query_data, f, indent=2)
            
            # Save performance metrics
            metrics_file = self.persistence_path / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
            metrics_data = [m.to_dict() for m in list(self.metrics)]
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving metrics: {e}")
    
    def _system_monitor_loop(self):
        """Background thread to monitor system resources"""
        while self._monitoring_active:
            try:
                # Record memory usage
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self.record_metric("memory_usage", memory_mb)
                
                # Record CPU usage
                cpu_percent = psutil.Process().cpu_percent()
                self.record_metric("cpu_usage", cpu_percent)
                
                # Save metrics periodically (every 10 minutes)
                if datetime.now().minute % 10 == 0:
                    self.save_metrics_to_disk()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ System monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def shutdown(self):
        """Shutdown the monitoring system"""
        self._monitoring_active = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        self.save_metrics_to_disk()

# Global performance monitor instance
performance_tracker = PerformanceMonitor()

# Context manager for easy query tracking
class QueryTracker:
    """Context manager for tracking query performance"""
    
    def __init__(self, query_id: str, query_text: str):
        self.query_id = query_id
        self.query_text = query_text
        self.query_metrics = None
    
    def __enter__(self):
        self.query_metrics = performance_tracker.start_query(self.query_id, self.query_text)
        return self.query_metrics
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None
        performance_tracker.end_query(self.query_id, success, error_message)

# Decorator for agent timing
def track_agent_execution(agent_name: str):
    """Decorator to track agent execution time"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract query_id from state if available
            query_id = None
            if args and isinstance(args[0], dict) and "session_id" in args[0]:
                query_id = args[0].get("session_id", "unknown")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if query_id:
                    performance_tracker.record_agent_timing(query_id, agent_name, duration)
        return wrapper
    return decorator 