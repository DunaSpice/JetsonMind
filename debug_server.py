#!/usr/bin/env python3
"""Debug MCP Server with FastMCP - Advanced Features"""

import os
import psutil
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
from functools import lru_cache
from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("jetson-debug")

# Cache for performance
@lru_cache(maxsize=32)
def _cached_system_info(timestamp_minute):
    """Cache system info per minute"""
    uname = os.uname()
    return f"System: {uname.sysname} {uname.machine}, Python: {os.sys.version.split()[0]}"

@lru_cache(maxsize=32)
def _cached_memory_info(timestamp_10sec):
    """Cache memory info per 10 seconds"""
    mem = psutil.virtual_memory()
    return f"Memory: {mem.total//1024**3}GB total, {mem.available//1024**3}GB available ({mem.percent}% used)"

@mcp.tool()
def system_status() -> str:
    """Get basic system status (cached)"""
    return _cached_system_info(int(time.time() // 60))

@mcp.tool()
def memory_info() -> str:
    """Get memory usage information (cached)"""
    return _cached_memory_info(int(time.time() // 10))

@mcp.tool()
def process_info() -> str:
    """Get current process information"""
    proc = psutil.Process()
    return f"PID: {proc.pid}, Memory: {proc.memory_info().rss//1024**2}MB, Threads: {proc.num_threads()}"

@mcp.tool()
def run_command(command: str) -> str:
    """Run a system command safely"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
        return f"Exit: {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out after 5 seconds"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def debug_status() -> str:
    """Get debug server status"""
    return f"Debug Server: Operational at {datetime.now().isoformat()}"

@mcp.tool()
def file_check(path: str = "/home/petr/jetson") -> str:
    """Check file or directory status"""
    try:
        p = Path(path)
        if p.is_file():
            stat = p.stat()
            return f"File: {path}\nSize: {stat.st_size} bytes\nModified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}"
        elif p.is_dir():
            files = list(p.iterdir())
            return f"Directory: {path}\nFiles: {len(files)}\nContents: {[f.name for f in files[:5]]}"
        else:
            return f"Path does not exist: {path}"
    except Exception as e:
        return f"Error checking {path}: {str(e)}"

@mcp.tool()
def mcp_health() -> str:
    """Check health of other MCP servers"""
    health = {}
    mcp_files = [
        "/home/petr/jetson/mcp_minimal.py",
        "/home/petr/jetson/core/mcp_unified_server.py"
    ]
    
    for mcp_file in mcp_files:
        if Path(mcp_file).exists():
            try:
                result = subprocess.run(["python3", mcp_file, "--test"], capture_output=True, text=True, timeout=3)
                health[Path(mcp_file).name] = "✅ Working" if result.returncode == 0 else "❌ Failed"
            except:
                health[Path(mcp_file).name] = "❌ Error"
        else:
            health[Path(mcp_file).name] = "❌ Not found"
    
    return f"MCP Health Check:\n" + "\n".join([f"{k}: {v}" for k, v in health.items()])

@mcp.tool()
def disk_usage() -> str:
    """Get disk usage information"""
    disk = psutil.disk_usage('/')
    return f"Disk: {disk.total//1024**3}GB total, {disk.free//1024**3}GB free ({(disk.used/disk.total)*100:.1f}% used)"

@mcp.tool()
def git_status() -> str:
    """Get git repository status"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            if result.stdout.strip():
                return f"Git Status: Changes detected\n{result.stdout}"
            else:
                return "Git Status: Clean working directory"
        else:
            return "Git Status: Not a git repository or error"
    except Exception as e:
        return f"Git Status Error: {str(e)}"

@mcp.tool()
def network_info() -> str:
    """Get network interface information"""
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        info = []
        for name, addrs in interfaces.items():
            if name != 'lo':  # Skip loopback
                ip = next((addr.address for addr in addrs if addr.family == 2), "No IP")
                status = "UP" if stats[name].isup else "DOWN"
                info.append(f"{name}: {ip} ({status})")
        return "Network Interfaces:\n" + "\n".join(info)
    except Exception as e:
        return f"Network Info Error: {str(e)}"

@mcp.tool()
def temperature() -> str:
    """Get system temperature information"""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            info = []
            for name, entries in temps.items():
                for entry in entries:
                    info.append(f"{name}: {entry.current}°C")
            return "Temperature:\n" + "\n".join(info)
        else:
            return "Temperature: No sensors found"
    except Exception as e:
        return f"Temperature Error: {str(e)}"

@mcp.tool()
def gpu_info() -> str:
    """Get NVIDIA GPU information (Jetson specific)"""
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            return f"GPU Info:\n{result.stdout.strip()}"
        else:
            return "GPU Info: nvidia-smi not available"
    except Exception as e:
        return f"GPU Info Error: {str(e)}"

@mcp.tool()
def docker_ps() -> str:
    """List Docker containers"""
    try:
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            return f"Docker Containers:\n{result.stdout}"
        else:
            return "Docker: Not available or no containers"
    except Exception as e:
        return f"Docker Error: {str(e)}"

@mcp.tool()
def service_status(service: str = "ssh") -> str:
    """Check system service status"""
    try:
        result = subprocess.run(["systemctl", "is-active", service], capture_output=True, text=True, timeout=3)
        status = result.stdout.strip()
        return f"Service {service}: {status}"
    except Exception as e:
        return f"Service Status Error: {str(e)}"

@mcp.tool()
def log_tail(logfile: str = "/var/log/syslog", lines: int = 10) -> str:
    """Get last N lines from log file"""
    try:
        result = subprocess.run(["tail", f"-{lines}", logfile], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            return f"Last {lines} lines from {logfile}:\n{result.stdout}"
        else:
            return f"Log file {logfile} not accessible"
    except Exception as e:
        return f"Log Tail Error: {str(e)}"

@mcp.tool()
def uptime() -> str:
    """Get system uptime and load average"""
    try:
        result = subprocess.run(["uptime"], capture_output=True, text=True, timeout=3)
        return f"Uptime: {result.stdout.strip()}"
    except Exception as e:
        return f"Uptime Error: {str(e)}"

@mcp.tool()
def tool_help(tool_name: str = "") -> str:
    """Get help and examples for tools"""
    help_data = {
        "file_check": "Usage: file_check('/path')\nExample: file_check('/home/petr')",
        "run_command": "Usage: run_command('command')\nExample: run_command('df -h')",
        "service_status": "Usage: service_status('service')\nExample: service_status('ssh')",
        "log_tail": "Usage: log_tail('/path/to/log', 10)\nExample: log_tail('/var/log/syslog', 5)"
    }
    if tool_name:
        return help_data.get(tool_name, f"No help available for {tool_name}")
    return "Available help: " + ", ".join(help_data.keys())

@mcp.tool()
def monitor_dashboard() -> str:
    """Get real-time system dashboard"""
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu = psutil.cpu_percent(interval=1)
    
    dashboard = f"""=== SYSTEM DASHBOARD ===
CPU Usage: {cpu}%
Memory: {mem.percent}% ({mem.available//1024**3}GB free)
Disk: {(disk.used/disk.total)*100:.1f}% ({disk.free//1024**3}GB free)
Processes: {len(psutil.pids())}
Time: {datetime.now().strftime('%H:%M:%S')}"""
    return dashboard

@mcp.tool()
def alert_check() -> str:
    """Check for system alerts and warnings"""
    alerts = []
    
    # Memory check
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        alerts.append(f"🚨 HIGH MEMORY: {mem.percent}%")
    elif mem.percent > 80:
        alerts.append(f"⚠️  Memory Warning: {mem.percent}%")
    
    # Disk check
    disk = psutil.disk_usage('/')
    disk_percent = (disk.used/disk.total)*100
    if disk_percent > 95:
        alerts.append(f"🚨 DISK FULL: {disk_percent:.1f}%")
    elif disk_percent > 85:
        alerts.append(f"⚠️  Disk Warning: {disk_percent:.1f}%")
    
    # CPU check
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 95:
        alerts.append(f"🚨 HIGH CPU: {cpu}%")
    
    return "System Alerts:\n" + ("\n".join(alerts) if alerts else "✅ All systems normal")

def main():
    mcp.run()

if __name__ == "__main__":
    main()
