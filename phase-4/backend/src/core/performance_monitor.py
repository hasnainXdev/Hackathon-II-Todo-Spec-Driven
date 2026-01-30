import time
import psutil
import threading
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from collections import deque, defaultdict
import statistics


class PerformanceMonitor:
    """
    Performance monitor for AI service operations
    """
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.request_times = deque(maxlen=max_samples)
        self.error_count = 0
        self.success_count = 0
        self.start_time = datetime.utcnow()
        
        # Track performance by endpoint/function
        self.endpoint_stats = defaultdict(lambda: {
            "request_times": deque(maxlen=max_samples),
            "error_count": 0,
            "success_count": 0
        })
        
        # Lock for thread safety
        self.lock = threading.Lock()
    
    def start_timer(self) -> float:
        """
        Start timing an operation
        """
        return time.time()
    
    def end_timer(self, start_time: float, endpoint: str = "unknown") -> float:
        """
        End timing an operation and record stats
        """
        duration = time.time() - start_time
        
        with self.lock:
            # Record overall stats
            self.request_times.append(duration)
            
            # Record endpoint-specific stats
            self.endpoint_stats[endpoint]["request_times"].append(duration)
        
        return duration
    
    def record_success(self, endpoint: str = "unknown"):
        """
        Record a successful operation
        """
        with self.lock:
            self.success_count += 1
            self.endpoint_stats[endpoint]["success_count"] += 1
    
    def record_error(self, endpoint: str = "unknown"):
        """
        Record an erroneous operation
        """
        with self.lock:
            self.error_count += 1
            self.endpoint_stats[endpoint]["error_count"] += 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get overall performance metrics
        """
        with self.lock:
            total_requests = self.success_count + self.error_count
            uptime = datetime.utcnow() - self.start_time
            
            if self.request_times:
                response_times = list(self.request_times)
                p95_response_time = self._calculate_percentile(response_times, 95)
                p99_response_time = self._calculate_percentile(response_times, 99)
                
                metrics = {
                    "uptime_seconds": uptime.total_seconds(),
                    "total_requests": total_requests,
                    "successful_requests": self.success_count,
                    "failed_requests": self.error_count,
                    "error_rate": self.error_count / total_requests if total_requests > 0 else 0,
                    "success_rate": self.success_count / total_requests if total_requests > 0 else 0,
                    "avg_response_time": statistics.mean(response_times),
                    "median_response_time": statistics.median(response_times),
                    "p95_response_time": p95_response_time,
                    "p99_response_time": p99_response_time,
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "requests_per_minute": total_requests / (uptime.total_seconds() / 60) if uptime.total_seconds() > 0 else 0,
                    "system_resources": self._get_system_resources()
                }
            else:
                metrics = {
                    "uptime_seconds": uptime.total_seconds(),
                    "total_requests": total_requests,
                    "successful_requests": self.success_count,
                    "failed_requests": self.error_count,
                    "error_rate": self.error_count / total_requests if total_requests > 0 else 0,
                    "success_rate": self.success_count / total_requests if total_requests > 0 else 0,
                    "avg_response_time": 0,
                    "median_response_time": 0,
                    "p95_response_time": 0,
                    "p99_response_time": 0,
                    "min_response_time": 0,
                    "max_response_time": 0,
                    "requests_per_minute": total_requests / (uptime.total_seconds() / 60) if uptime.total_seconds() > 0 else 0,
                    "system_resources": self._get_system_resources()
                }
        
        return metrics
    
    def get_endpoint_performance(self, endpoint: str) -> Dict[str, Any]:
        """
        Get performance metrics for a specific endpoint
        """
        with self.lock:
            stats = self.endpoint_stats[endpoint]
            total_requests = stats["success_count"] + stats["error_count"]
            
            if stats["request_times"]:
                response_times = list(stats["request_times"])
                p95_response_time = self._calculate_percentile(response_times, 95)
                p99_response_time = self._calculate_percentile(response_times, 99)
                
                endpoint_metrics = {
                    "total_requests": total_requests,
                    "successful_requests": stats["success_count"],
                    "failed_requests": stats["error_count"],
                    "error_rate": stats["error_count"] / total_requests if total_requests > 0 else 0,
                    "success_rate": stats["success_count"] / total_requests if total_requests > 0 else 0,
                    "avg_response_time": statistics.mean(response_times),
                    "median_response_time": statistics.median(response_times),
                    "p95_response_time": p95_response_time,
                    "p99_response_time": p99_response_time,
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times)
                }
            else:
                endpoint_metrics = {
                    "total_requests": total_requests,
                    "successful_requests": stats["success_count"],
                    "failed_requests": stats["error_count"],
                    "error_rate": stats["error_count"] / total_requests if total_requests > 0 else 0,
                    "success_rate": stats["success_count"] / total_requests if total_requests > 0 else 0,
                    "avg_response_time": 0,
                    "median_response_time": 0,
                    "p95_response_time": 0,
                    "p99_response_time": 0,
                    "min_response_time": 0,
                    "max_response_time": 0
                }
        
        return endpoint_metrics
    
    def _calculate_percentile(self, data: list, percentile: float) -> float:
        """
        Calculate percentile of response times
        """
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index // 1)
            upper_index = lower_index + 1
            weight = index % 1
            
            if upper_index >= len(sorted_data):
                return sorted_data[-1]
            
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight
    
    def _get_system_resources(self) -> Dict[str, float]:
        """
        Get system resource utilization
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    
    def reset_counters(self):
        """
        Reset all performance counters
        """
        with self.lock:
            self.request_times.clear()
            self.error_count = 0
            self.success_count = 0
            self.start_time = datetime.utcnow()
            
            # Reset endpoint-specific stats
            for endpoint in self.endpoint_stats:
                self.endpoint_stats[endpoint]["request_times"].clear()
                self.endpoint_stats[endpoint]["error_count"] = 0
                self.endpoint_stats[endpoint]["success_count"] = 0


class AIPerformanceMonitor:
    """
    Specialized performance monitor for AI service operations
    """
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.ai_specific_metrics = {
            "nlp_processing_times": deque(maxlen=1000),
            "model_inference_times": deque(maxlen=1000),
            "token_counts": deque(maxlen=1000),
            "context_window_utilization": deque(maxlen=1000)
        }
        self.lock = threading.Lock()
    
    def monitor_nlp_processing(self, func: Callable) -> Callable:
        """
        Decorator to monitor NLP processing performance
        """
        def wrapper(*args, **kwargs):
            start_time = self.monitor.start_timer()
            try:
                result = func(*args, **kwargs)
                duration = self.monitor.end_timer(start_time, "nlp_processing")
                
                with self.lock:
                    self.ai_specific_metrics["nlp_processing_times"].append(duration)
                
                self.monitor.record_success("nlp_processing")
                return result
            except Exception as e:
                self.monitor.end_timer(start_time, "nlp_processing")
                self.monitor.record_error("nlp_processing")
                raise e
        return wrapper
    
    def monitor_model_inference(self, func: Callable) -> Callable:
        """
        Decorator to monitor model inference performance
        """
        def wrapper(*args, **kwargs):
            start_time = self.monitor.start_timer()
            try:
                result = func(*args, **kwargs)
                duration = self.monitor.end_timer(start_time, "model_inference")
                
                with self.lock:
                    self.ai_specific_metrics["model_inference_times"].append(duration)
                
                self.monitor.record_success("model_inference")
                return result
            except Exception as e:
                self.monitor.end_timer(start_time, "model_inference")
                self.monitor.record_error("model_inference")
                raise e
        return wrapper
    
    def record_token_usage(self, token_count: int):
        """
        Record token usage for AI model
        """
        with self.lock:
            self.ai_specific_metrics["token_counts"].append(token_count)
    
    def record_context_window_utilization(self, utilization_percent: float):
        """
        Record context window utilization
        """
        with self.lock:
            self.ai_specific_metrics["context_window_utilization"].append(utilization_percent)
    
    def get_ai_performance_metrics(self) -> Dict[str, Any]:
        """
        Get AI-specific performance metrics
        """
        with self.lock:
            metrics = {
                "general_performance": self.monitor.get_performance_metrics(),
                "ai_specific": {}
            }
            
            if self.ai_specific_metrics["nlp_processing_times"]:
                nlp_times = list(self.ai_specific_metrics["nlp_processing_times"])
                metrics["ai_specific"]["nlp_processing"] = {
                    "avg_time": statistics.mean(nlp_times),
                    "median_time": statistics.median(nlp_times),
                    "p95_time": self.monitor._calculate_percentile(nlp_times, 95),
                    "p99_time": self.monitor._calculate_percentile(nlp_times, 99),
                    "min_time": min(nlp_times),
                    "max_time": max(nlp_times)
                }
            
            if self.ai_specific_metrics["model_inference_times"]:
                inference_times = list(self.ai_specific_metrics["model_inference_times"])
                metrics["ai_specific"]["model_inference"] = {
                    "avg_time": statistics.mean(inference_times),
                    "median_time": statistics.median(inference_times),
                    "p95_time": self.monitor._calculate_percentile(inference_times, 95),
                    "p99_time": self.monitor._calculate_percentile(inference_times, 99),
                    "min_time": min(inference_times),
                    "max_time": max(inference_times)
                }
            
            if self.ai_specific_metrics["token_counts"]:
                token_counts = list(self.ai_specific_metrics["token_counts"])
                metrics["ai_specific"]["token_usage"] = {
                    "avg_tokens": statistics.mean(token_counts),
                    "median_tokens": statistics.median(token_counts),
                    "total_tokens": sum(token_counts),
                    "min_tokens": min(token_counts),
                    "max_tokens": max(token_counts)
                }
            
            if self.ai_specific_metrics["context_window_utilization"]:
                utilizations = list(self.ai_specific_metrics["context_window_utilization"])
                metrics["ai_specific"]["context_window"] = {
                    "avg_utilization": statistics.mean(utilizations),
                    "median_utilization": statistics.median(utilizations),
                    "p95_utilization": self.monitor._calculate_percentile(utilizations, 95),
                    "p99_utilization": self.monitor._calculate_percentile(utilizations, 99),
                    "min_utilization": min(utilizations),
                    "max_utilization": max(utilizations)
                }
            
            return metrics


# Global performance monitor instance
ai_performance_monitor = AIPerformanceMonitor()


def get_ai_performance_monitor() -> AIPerformanceMonitor:
    """
    Get the global AI performance monitor instance
    """
    return ai_performance_monitor