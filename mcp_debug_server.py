#!/usr/bin/env python3
"""Full MCP Debug Server - All Features with Stable Transport"""

import json
import sys
import os
import psutil
import subprocess
import importlib
import traceback
from datetime import datetime
from pathlib import Path

class MCPDebugServer:
    def __init__(self):
        self.last_reload = datetime.now()
        self.errors = []
    
    def log_error(self, error):
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "trace": traceback.format_exc()
        })
        if len(self.errors) > 10:
            self.errors.pop(0)
    
    def debug_status(self, args=None):
        return {
            "server": "MCP Debug Server",
            "version": "1.0",
            "tools_count": 10,
            "tools": ["debug_status", "hot_reload", "test_all_tools", "system_info", "memory_info", "process_info", "file_check", "run_command", "mcp_health", "error_trace"],
            "last_reload": self.last_reload.isoformat(),
            "errors_count": len(self.errors),
            "status": "operational"
        }
    
    def hot_reload(self, args=None):
        try:
            current_module = sys.modules[__name__]
            importlib.reload(current_module)
            self.last_reload = datetime.now()
            return {"success": True, "reloaded_at": self.last_reload.isoformat()}
        except Exception as e:
            self.log_error(e)
            return {"success": False, "error": str(e)}
    
    def test_all_tools(self, args=None):
        tools = ["debug_status", "system_info", "memory_info", "process_info", "file_check", "mcp_health", "error_trace"]
        results = {}
        for tool in tools:
            try:
                getattr(self, tool)({})
                results[tool] = {"success": True}
            except Exception as e:
                results[tool] = {"success": False, "error": str(e)}
        return results
    
    def system_info(self, args=None):
        uname = os.uname()
        return {
            "platform": {
                "system": uname.sysname,
                "node": uname.nodename,
                "release": uname.release,
                "machine": uname.machine
            },
            "python_version": sys.version.split()[0],
            "working_directory": os.getcwd(),
            "path_count": len(sys.path)
        }
    
    def memory_info(self, args=None):
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "memory": {
                "total_gb": round(mem.total / 1024**3, 2),
                "available_gb": round(mem.available / 1024**3, 2),
                "used_percent": mem.percent
            },
            "disk": {
                "total_gb": round(disk.total / 1024**3, 2),
                "free_gb": round(disk.free / 1024**3, 2),
                "used_percent": round((disk.used / disk.total) * 100, 1)
            }
        }
    
    def process_info(self, args=None):
        try:
            current_process = psutil.Process()
            return {
                "pid": current_process.pid,
                "memory_mb": round(current_process.memory_info().rss / 1024**2, 2),
                "cpu_percent": current_process.cpu_percent(),
                "threads": current_process.num_threads()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def file_check(self, args=None):
        path = args.get("path", "/home/petr/jetson") if args else "/home/petr/jetson"
        try:
            p = Path(path)
            if p.is_file():
                stat = p.stat()
                return {
                    "exists": True,
                    "type": "file",
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            elif p.is_dir():
                files = list(p.iterdir())
                return {
                    "exists": True,
                    "type": "directory",
                    "file_count": len(files),
                    "files": [f.name for f in files[:10]]
                }
            else:
                return {"exists": False, "path": str(path)}
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def run_command(self, args=None):
        if not args or "command" not in args:
            return {"error": "command parameter required"}
        
        cmd = args["command"]
        timeout = args.get("timeout", 10)
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"error": str(e)}
    
    def mcp_health(self, args=None):
        health_checks = {}
        mcp_files = [
            "/home/petr/jetson/mcp_minimal.py",
            "/home/petr/jetson/core/mcp_unified_server.py"
        ]
        
        for mcp_file in mcp_files:
            if Path(mcp_file).exists():
                try:
                    result = subprocess.run(["python3", mcp_file, "--test"], capture_output=True, text=True, timeout=5)
                    health_checks[Path(mcp_file).name] = {
                        "exists": True,
                        "test_passed": result.returncode == 0,
                        "output": result.stdout if result.returncode == 0 else result.stderr
                    }
                except Exception as e:
                    health_checks[Path(mcp_file).name] = {"exists": True, "test_passed": False, "error": str(e)}
            else:
                health_checks[Path(mcp_file).name] = {"exists": False}
        
        return health_checks
    
    def error_trace(self, args=None):
        return {"recent_errors": self.errors, "error_count": len(self.errors)}

def main():
    server = MCPDebugServer()
    
    # Handle command line modes
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            print("MCP Debug Server OK")
            return 0
        elif sys.argv[1] == "--interactive":
            print("🔧 Interactive Mode")
            while True:
                try:
                    tool = input("Tool: ").strip()
                    if tool == 'quit': break
                    if hasattr(server, tool):
                        result = getattr(server, tool)({})
                        print(json.dumps(result, indent=2))
                    else:
                        print("Unknown tool")
                except KeyboardInterrupt:
                    break
            return 0
    
    # JSON-RPC mode for Q CLI
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                method = request.get("method")
                id = request.get("id")
                params = request.get("params", {})
                
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": "jetson-debug", "version": "1.0.0"}
                        }
                    }
                elif method == "tools/list":
                    tools = [
                        {"name": "debug_status", "description": "Get debug server status"},
                        {"name": "hot_reload", "description": "Hot reload server"},
                        {"name": "test_all_tools", "description": "Test all tools"},
                        {"name": "system_info", "description": "Get system information"},
                        {"name": "memory_info", "description": "Get memory information"},
                        {"name": "process_info", "description": "Get process information"},
                        {"name": "file_check", "description": "Check file/directory"},
                        {"name": "run_command", "description": "Run system command"},
                        {"name": "mcp_health", "description": "Check MCP server health"},
                        {"name": "error_trace", "description": "Get error traces"}
                    ]
                    response = {"jsonrpc": "2.0", "id": id, "result": {"tools": tools}}
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    
                    if hasattr(server, tool_name):
                        try:
                            result = getattr(server, tool_name)(tool_args)
                            response = {
                                "jsonrpc": "2.0",
                                "id": id,
                                "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
                            }
                        except Exception as e:
                            server.log_error(e)
                            response = {
                                "jsonrpc": "2.0",
                                "id": id,
                                "error": {"code": -32603, "message": str(e)}
                            }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": id,
                            "error": {"code": -32601, "message": f"Tool {tool_name} not found"}
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": id,
                        "error": {"code": -32601, "message": f"Method {method} not found"}
                    }
                
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": id if 'id' in locals() else None,
                    "error": {"code": -32603, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        pass
    except Exception:
        pass

if __name__ == "__main__":
    main()
