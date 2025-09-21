#!/usr/bin/env python3
"""Debug MCP Server with FastMCP"""

import os
import psutil
import subprocess
from datetime import datetime
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

def main():
    mcp.run()

if __name__ == "__main__":
    main()
