#!/usr/bin/env python3
import time
import json
import threading
import psutil
import subprocess
import os
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.data = []
        self.alerts = []
        
    def get_gpu_stats(self):
        """Get GPU temperature, memory, utilization"""
        try:
            # Use nvidia-smi for GPU stats
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=temperature.gpu,memory.used,memory.total,utilization.gpu',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                temp, mem_used, mem_total, util = result.stdout.strip().split(', ')
                return {
                    'gpu_temp_c': int(temp),
                    'gpu_memory_used_mb': int(mem_used),
                    'gpu_memory_total_mb': int(mem_total),
                    'gpu_utilization_percent': int(util)
                }
        except:
            pass
        
        return {
            'gpu_temp_c': 0,
            'gpu_memory_used_mb': 0,
            'gpu_memory_total_mb': 0,
            'gpu_utilization_percent': 0
        }
    
    def get_system_stats(self):
        """Get comprehensive system statistics"""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_temp_c': self.get_cpu_temp(),
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024**3,
            'memory_available_gb': memory.available / 1024**3,
            'disk_used_percent': disk.percent,
            'disk_free_gb': disk.free / 1024**3,
            'load_average': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        }
        
        # Add GPU stats
        stats.update(self.get_gpu_stats())
        
        return stats
    
    def get_cpu_temp(self):
        """Get CPU temperature"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000
                return temp
        except:
            return 0
    
    def check_safety_limits(self, stats):
        """Check if system is within safe operating limits"""
        alerts = []
        
        # Temperature checks
        if stats['gpu_temp_c'] > 80:
            alerts.append(f"🔥 GPU temperature critical: {stats['gpu_temp_c']}°C")
        elif stats['gpu_temp_c'] > 70:
            alerts.append(f"⚠️ GPU temperature high: {stats['gpu_temp_c']}°C")
            
        if stats['cpu_temp_c'] > 80:
            alerts.append(f"🔥 CPU temperature critical: {stats['cpu_temp_c']}°C")
        
        # Memory checks
        if stats['memory_percent'] > 95:
            alerts.append(f"🔥 Memory critical: {stats['memory_percent']:.1f}%")
        elif stats['memory_percent'] > 85:
            alerts.append(f"⚠️ Memory high: {stats['memory_percent']:.1f}%")
        
        # GPU memory checks
        gpu_mem_percent = (stats['gpu_memory_used_mb'] / stats['gpu_memory_total_mb']) * 100 if stats['gpu_memory_total_mb'] > 0 else 0
        if gpu_mem_percent > 95:
            alerts.append(f"🔥 GPU memory critical: {gpu_mem_percent:.1f}%")
        
        # Disk space checks
        if stats['disk_used_percent'] > 95:
            alerts.append(f"🔥 Disk space critical: {stats['disk_used_percent']:.1f}%")
        
        return alerts
    
    def should_abort_test(self, stats):
        """Determine if test should be aborted for safety"""
        return (stats['gpu_temp_c'] > 85 or 
                stats['cpu_temp_c'] > 85 or 
                stats['memory_percent'] > 98 or
                stats['disk_used_percent'] > 98)
    
    def start_monitoring(self, interval=5):
        """Start continuous monitoring"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                stats = self.get_system_stats()
                self.data.append(stats)
                
                # Check safety limits
                alerts = self.check_safety_limits(stats)
                if alerts:
                    self.alerts.extend(alerts)
                    for alert in alerts:
                        print(alert)
                
                # Keep only last 100 readings
                if len(self.data) > 100:
                    self.data = self.data[-100:]
                
                time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def get_current_stats(self):
        """Get current system statistics"""
        return self.get_system_stats()
    
    def save_monitoring_data(self, filename):
        """Save monitoring data to file"""
        with open(filename, 'w') as f:
            json.dump({
                'monitoring_data': self.data,
                'alerts': self.alerts
            }, f, indent=2)

# Global monitor instance
monitor = SystemMonitor()

def start_monitoring():
    monitor.start_monitoring()

def stop_monitoring():
    monitor.stop_monitoring()

def get_stats():
    return monitor.get_current_stats()

def check_safety():
    stats = monitor.get_current_stats()
    return not monitor.should_abort_test(stats), monitor.check_safety_limits(stats)

def save_data(filename):
    monitor.save_monitoring_data(filename)
