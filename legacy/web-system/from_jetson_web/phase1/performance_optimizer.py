#!/usr/bin/env python3
import asyncio
import torch
import psutil
import time
import json
import numpy as np
from collections import deque, defaultdict
import threading

class AdvancedMonitor:
    def __init__(self, history_size=1000):
        self.metrics_history = deque(maxlen=history_size)
        self.model_performance = defaultdict(list)
        self.system_alerts = []
        self.monitoring = True
        
    async def start_monitoring(self, interval=1.0):
        """Continuous system monitoring"""
        while self.monitoring:
            metrics = self.capture_comprehensive_metrics()
            self.metrics_history.append(metrics)
            self.analyze_performance_trends(metrics)
            await asyncio.sleep(interval)
    
    def capture_comprehensive_metrics(self):
        """Capture all system metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_times = psutil.cpu_times()
        
        metrics = {
            'timestamp': time.time(),
            
            # Memory metrics
            'ram_total': memory.total,
            'ram_used': memory.used,
            'ram_available': memory.available,
            'ram_percent': memory.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent,
            
            # GPU metrics
            'gpu_memory_allocated': torch.cuda.memory_allocated() if torch.cuda.is_available() else 0,
            'gpu_memory_reserved': torch.cuda.memory_reserved() if torch.cuda.is_available() else 0,
            'gpu_memory_cached': torch.cuda.memory_cached() if torch.cuda.is_available() else 0,
            
            # CPU metrics
            'cpu_percent': psutil.cpu_percent(interval=None),
            'cpu_user': cpu_times.user,
            'cpu_system': cpu_times.system,
            'cpu_idle': cpu_times.idle,
            'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
            
            # Temperature
            'cpu_temp': self.get_cpu_temperature(),
            'gpu_temp': self.get_gpu_temperature(),
            
            # I/O metrics
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
        }
        
        return metrics
    
    def get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000.0
        except:
            return 0
    
    def get_gpu_temperature(self):
        """Get GPU temperature"""
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 0
    
    def analyze_performance_trends(self, current_metrics):
        """Analyze performance trends and generate alerts"""
        if len(self.metrics_history) < 10:
            return
        
        # Memory pressure detection
        if current_metrics['ram_percent'] > 90:
            self.add_alert("HIGH_MEMORY_USAGE", f"RAM usage at {current_metrics['ram_percent']:.1f}%")
        
        # Temperature monitoring
        if current_metrics['cpu_temp'] > 80:
            self.add_alert("HIGH_CPU_TEMP", f"CPU temperature at {current_metrics['cpu_temp']:.1f}°C")
        
        if current_metrics['gpu_temp'] > 85:
            self.add_alert("HIGH_GPU_TEMP", f"GPU temperature at {current_metrics['gpu_temp']:.1f}°C")
        
        # Performance degradation detection
        recent_metrics = list(self.metrics_history)[-10:]
        avg_cpu = np.mean([m['cpu_percent'] for m in recent_metrics])
        
        if avg_cpu > 95:
            self.add_alert("HIGH_CPU_LOAD", f"Average CPU load at {avg_cpu:.1f}%")
    
    def add_alert(self, alert_type, message):
        """Add system alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': time.time()
        }
        self.system_alerts.append(alert)
        print(f"🚨 ALERT: {alert_type} - {message}")
    
    def get_performance_summary(self, window_minutes=5):
        """Get performance summary for recent window"""
        cutoff_time = time.time() - (window_minutes * 60)
        recent_metrics = [m for m in self.metrics_history if m['timestamp'] > cutoff_time]
        
        if not recent_metrics:
            return {}
        
        return {
            'avg_ram_percent': np.mean([m['ram_percent'] for m in recent_metrics]),
            'max_ram_percent': np.max([m['ram_percent'] for m in recent_metrics]),
            'avg_cpu_percent': np.mean([m['cpu_percent'] for m in recent_metrics]),
            'max_cpu_temp': np.max([m['cpu_temp'] for m in recent_metrics]),
            'avg_gpu_memory_gb': np.mean([m['gpu_memory_allocated'] for m in recent_metrics]) / 1024**3,
            'swap_usage_gb': np.mean([m['swap_used'] for m in recent_metrics]) / 1024**3,
            'alert_count': len([a for a in self.system_alerts if a['timestamp'] > cutoff_time])
        }

class ModelOptimizer:
    def __init__(self, model_pool):
        self.model_pool = model_pool
        self.optimization_history = []
        
    async def optimize_model_placement(self):
        """Optimize which models to keep in memory"""
        usage_stats = self.analyze_model_usage()
        memory_pressure = self.calculate_memory_pressure()
        
        if memory_pressure > 0.8:  # High memory pressure
            await self.aggressive_optimization(usage_stats)
        elif memory_pressure > 0.6:  # Medium memory pressure
            await self.moderate_optimization(usage_stats)
        else:
            await self.preload_popular_models(usage_stats)
    
    def analyze_model_usage(self):
        """Analyze model usage patterns"""
        stats = {}
        
        for model_name, model_data in self.model_pool.active_models.items():
            stats[model_name] = {
                'usage_count': model_data['usage_count'],
                'last_used': model_data['last_used'],
                'memory_size': model_data['memory_size'],
                'load_time': model_data['load_time'],
                'efficiency': model_data['usage_count'] / (model_data['memory_size'] / 1024**3)  # usage per GB
            }
        
        return stats
    
    def calculate_memory_pressure(self):
        """Calculate current memory pressure (0-1)"""
        current_usage = self.model_pool.get_memory_usage()
        return current_usage / self.model_pool.ram_budget
    
    async def aggressive_optimization(self, usage_stats):
        """Aggressive memory optimization"""
        # Keep only the most efficient models
        sorted_models = sorted(usage_stats.items(), key=lambda x: x[1]['efficiency'], reverse=True)
        
        models_to_keep = []
        memory_budget = self.model_pool.ram_budget * 0.7  # Use only 70% of budget
        current_memory = 0
        
        for model_name, stats in sorted_models:
            if current_memory + stats['memory_size'] <= memory_budget:
                models_to_keep.append(model_name)
                current_memory += stats['memory_size']
        
        # Evict models not in keep list
        for model_name in list(self.model_pool.active_models.keys()):
            if model_name not in models_to_keep:
                await self.model_pool.save_to_swap(model_name)
                del self.model_pool.active_models[model_name]
        
        print(f"🔧 Aggressive optimization: Keeping {len(models_to_keep)} models")
    
    async def moderate_optimization(self, usage_stats):
        """Moderate memory optimization"""
        # Remove least recently used models
        cutoff_time = time.time() - 300  # 5 minutes
        
        for model_name, stats in usage_stats.items():
            if stats['last_used'] < cutoff_time and stats['usage_count'] < 5:
                await self.model_pool.save_to_swap(model_name)
                del self.model_pool.active_models[model_name]
                print(f"🔧 Moderate optimization: Swapped out {model_name}")
    
    async def preload_popular_models(self, usage_stats):
        """Preload popular models when memory allows"""
        # Find models in swap cache that might be worth preloading
        for model_name in self.model_pool.swap_cache:
            if model_name not in self.model_pool.active_models:
                # Check if we have memory budget
                estimated_size = self.model_pool.estimate_model_size(model_name)
                if self.model_pool.get_memory_usage() + estimated_size < self.model_pool.ram_budget * 0.9:
                    try:
                        await self.model_pool.load_model_smart(model_name, priority="low")
                        print(f"🔧 Preloaded popular model: {model_name}")
                    except:
                        pass

class PerformanceProfiler:
    def __init__(self):
        self.inference_times = defaultdict(list)
        self.load_times = defaultdict(list)
        self.memory_usage = defaultdict(list)
        
    def record_inference(self, model_name, inference_time, tokens_generated):
        """Record inference performance"""
        self.inference_times[model_name].append({
            'time': inference_time,
            'tokens': tokens_generated,
            'tokens_per_second': tokens_generated / inference_time if inference_time > 0 else 0,
            'timestamp': time.time()
        })
    
    def record_load_time(self, model_name, load_time, memory_used):
        """Record model loading performance"""
        self.load_times[model_name].append({
            'load_time': load_time,
            'memory_used': memory_used,
            'timestamp': time.time()
        })
    
    def get_model_performance_report(self, model_name):
        """Get comprehensive performance report for model"""
        if model_name not in self.inference_times:
            return None
        
        inferences = self.inference_times[model_name]
        loads = self.load_times.get(model_name, [])
        
        return {
            'model_name': model_name,
            'total_inferences': len(inferences),
            'avg_inference_time': np.mean([i['time'] for i in inferences]),
            'avg_tokens_per_second': np.mean([i['tokens_per_second'] for i in inferences]),
            'avg_load_time': np.mean([l['load_time'] for l in loads]) if loads else 0,
            'avg_memory_usage_gb': np.mean([l['memory_used'] for l in loads]) / 1024**3 if loads else 0,
            'efficiency_score': self.calculate_efficiency_score(inferences, loads)
        }
    
    def calculate_efficiency_score(self, inferences, loads):
        """Calculate overall efficiency score"""
        if not inferences:
            return 0
        
        avg_speed = np.mean([i['tokens_per_second'] for i in inferences])
        avg_memory = np.mean([l['memory_used'] for l in loads]) / 1024**3 if loads else 1
        
        # Higher tokens/second per GB = better efficiency
        return avg_speed / avg_memory if avg_memory > 0 else 0
    
    def get_system_performance_report(self):
        """Get system-wide performance report"""
        all_models = {}
        
        for model_name in self.inference_times.keys():
            all_models[model_name] = self.get_model_performance_report(model_name)
        
        # Sort by efficiency
        sorted_models = sorted(all_models.items(), 
                             key=lambda x: x[1]['efficiency_score'] if x[1] else 0, 
                             reverse=True)
        
        return {
            'total_models_tested': len(all_models),
            'best_performing_model': sorted_models[0] if sorted_models else None,
            'model_rankings': sorted_models,
            'system_recommendations': self.generate_recommendations(sorted_models)
        }
    
    def generate_recommendations(self, sorted_models):
        """Generate optimization recommendations"""
        recommendations = []
        
        if not sorted_models:
            return recommendations
        
        # Recommend best models for different use cases
        fast_models = [m for m in sorted_models if m[1]['avg_tokens_per_second'] > 10]
        efficient_models = [m for m in sorted_models if m[1]['efficiency_score'] > 5]
        
        if fast_models:
            recommendations.append(f"For speed: Use {fast_models[0][0]} (avg {fast_models[0][1]['avg_tokens_per_second']:.1f} tok/s)")
        
        if efficient_models:
            recommendations.append(f"For efficiency: Use {efficient_models[0][0]} (score: {efficient_models[0][1]['efficiency_score']:.1f})")
        
        # Memory recommendations
        low_memory_models = [m for m in sorted_models if m[1]['avg_memory_usage_gb'] < 2.0]
        if low_memory_models:
            recommendations.append(f"For low memory: Use {low_memory_models[0][0]} ({low_memory_models[0][1]['avg_memory_usage_gb']:.1f}GB)")
        
        return recommendations

# Integration example
async def create_enhanced_system():
    """Create fully enhanced AI system"""
    from enhanced_model_server import EnhancedAIServer
    
    # Create components
    server = EnhancedAIServer()
    monitor = AdvancedMonitor()
    optimizer = ModelOptimizer(server.model_pool)
    profiler = PerformanceProfiler()
    
    # Start monitoring
    asyncio.create_task(monitor.start_monitoring())
    asyncio.create_task(server.start_batch_processor())
    
    # Optimization loop
    async def optimization_loop():
        while True:
            await asyncio.sleep(60)  # Optimize every minute
            await optimizer.optimize_model_placement()
    
    asyncio.create_task(optimization_loop())
    
    return server, monitor, optimizer, profiler

if __name__ == "__main__":
    async def main():
        server, monitor, optimizer, profiler = await create_enhanced_system()
        
        # Run some test inferences
        test_prompts = [
            "Write a Python function",
            "Explain AI",
            "What is 2+2?",
            "Tell me a joke"
        ]
        
        for prompt in test_prompts:
            result = await server.inference(prompt)
            print(f"Response: {result['response'][:50]}...")
        
        # Get performance report
        await asyncio.sleep(5)
        summary = monitor.get_performance_summary()
        print("\nPerformance Summary:", json.dumps(summary, indent=2))
        
        print("\nServer Status:", server.get_status())
    
    asyncio.run(main())
