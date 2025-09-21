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

def main():
    mcp.run()

if __name__ == "__main__":
    main()
