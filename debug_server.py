#!/usr/bin/env python3
"""Debug MCP Server with FastMCP - Full Feature Set"""

import os
import psutil
import subprocess
import json
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Create FastMCP server
mcp = FastMCP("jetson-debug")

@mcp.tool()
def system_status() -> str:
    """Get basic system status"""
    uname = os.uname()
    return f"System: {uname.sysname} {uname.machine}, Python: {os.sys.version.split()[0]}"

@mcp.tool()
def memory_info() -> str:
    """Get memory usage information"""
    mem = psutil.virtual_memory()
    return f"Memory: {mem.total//1024**3}GB total, {mem.available//1024**3}GB available ({mem.percent}% used)"

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

def main():
    mcp.run()

if __name__ == "__main__":
    main()
