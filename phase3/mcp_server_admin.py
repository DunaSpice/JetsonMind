#!/usr/bin/env python3
"""
Phase 3 MCP Server - Admin Extended
Complete system management through MCP tools
"""

import asyncio
import json
import logging
import os
import subprocess
import sqlite3
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("phase3-admin")

app = Server("phase3-admin")

class SystemManager:
    def __init__(self):
        self.config_file = Path.home() / ".phase3" / "config.json"
        self.db_file = Path.home() / ".phase3" / "phase3.db"
        self.ensure_dirs()
        self.init_db()
    
    def ensure_dirs(self):
        self.config_file.parent.mkdir(exist_ok=True)
    
    def init_db(self):
        conn = sqlite3.connect(self.db_file)
        conn.execute('''CREATE TABLE IF NOT EXISTS sessions 
                       (id INTEGER PRIMARY KEY, timestamp TEXT, data TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS settings 
                       (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()
    
    def get_config(self):
        if self.config_file.exists():
            return json.loads(self.config_file.read_text())
        return {"debug_level": 1, "frontend_port": 8080, "agent_model": "gpt-4"}
    
    def save_config(self, config):
        self.config_file.write_text(json.dumps(config, indent=2))

manager = SystemManager()

@app.list_tools()
async def list_tools():
    return [
        # Core tools
        Tool(name="generate", description="Generate text", 
             inputSchema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}),
        Tool(name="get_status", description="System status", 
             inputSchema={"type": "object", "properties": {}}),
        
        # Admin tools
        Tool(name="start_frontend", description="Start web frontend", 
             inputSchema={"type": "object", "properties": {"port": {"type": "integer", "default": 8080}}}),
        Tool(name="set_debug", description="Set debug level", 
             inputSchema={"type": "object", "properties": {"level": {"type": "integer"}}, "required": ["level"]}),
        Tool(name="get_agent_config", description="Get agent configuration", 
             inputSchema={"type": "object", "properties": {}}),
        Tool(name="set_agent_config", description="Set agent configuration", 
             inputSchema={"type": "object", "properties": {"model": {"type": "string"}, "temperature": {"type": "number"}}}),
        Tool(name="db_status", description="Database status", 
             inputSchema={"type": "object", "properties": {}}),
        Tool(name="db_query", description="Execute database query", 
             inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}),
        Tool(name="get_settings", description="Get all settings", 
             inputSchema={"type": "object", "properties": {}}),
        Tool(name="set_setting", description="Set configuration setting", 
             inputSchema={"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}),
        Tool(name="restart_service", description="Restart system service", 
             inputSchema={"type": "object", "properties": {"service": {"type": "string"}}, "required": ["service"]}),
        Tool(name="get_logs", description="Get system logs", 
             inputSchema={"type": "object", "properties": {"lines": {"type": "integer", "default": 50}}})
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "generate":
            prompt = arguments.get("prompt", "")
            result = f"Generated: {prompt[:50]}..."
            return [TextContent(type="text", text=result)]
        
        elif name == "get_status":
            status = {
                "status": "healthy",
                "server": "phase3-admin",
                "version": "1.0.0",
                "frontend_running": check_frontend_running(),
                "database_connected": check_db_connection(),
                "debug_level": manager.get_config().get("debug_level", 1)
            }
            return [TextContent(type="text", text=json.dumps(status, indent=2))]
        
        elif name == "start_frontend":
            port = arguments.get("port", 8080)
            result = start_frontend_server(port)
            return [TextContent(type="text", text=result)]
        
        elif name == "set_debug":
            level = arguments.get("level", 1)
            config = manager.get_config()
            config["debug_level"] = level
            manager.save_config(config)
            logging.getLogger().setLevel([logging.ERROR, logging.INFO, logging.DEBUG, logging.DEBUG][min(level, 3)])
            return [TextContent(type="text", text=f"Debug level set to {level}")]
        
        elif name == "get_agent_config":
            config = manager.get_config()
            agent_config = {
                "model": config.get("agent_model", "gpt-4"),
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("max_tokens", 1000)
            }
            return [TextContent(type="text", text=json.dumps(agent_config, indent=2))]
        
        elif name == "set_agent_config":
            config = manager.get_config()
            if "model" in arguments:
                config["agent_model"] = arguments["model"]
            if "temperature" in arguments:
                config["temperature"] = arguments["temperature"]
            manager.save_config(config)
            return [TextContent(type="text", text="Agent configuration updated")]
        
        elif name == "db_status":
            status = get_db_status()
            return [TextContent(type="text", text=json.dumps(status, indent=2))]
        
        elif name == "db_query":
            query = arguments.get("query", "")
            result = execute_db_query(query)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_settings":
            settings = manager.get_config()
            return [TextContent(type="text", text=json.dumps(settings, indent=2))]
        
        elif name == "set_setting":
            key = arguments.get("key")
            value = arguments.get("value")
            config = manager.get_config()
            config[key] = value
            manager.save_config(config)
            return [TextContent(type="text", text=f"Setting {key} = {value}")]
        
        elif name == "restart_service":
            service = arguments.get("service", "phase3")
            result = restart_system_service(service)
            return [TextContent(type="text", text=result)]
        
        elif name == "get_logs":
            lines = arguments.get("lines", 50)
            logs = get_system_logs(lines)
            return [TextContent(type="text", text=logs)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

def check_frontend_running():
    try:
        result = subprocess.run(["pgrep", "-f", "phase3_frontend"], capture_output=True)
        return result.returncode == 0
    except:
        return False

def check_db_connection():
    try:
        conn = sqlite3.connect(manager.db_file)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except:
        return False

def start_frontend_server(port):
    try:
        cmd = f"cd /home/petr/jetson/phase3/frontend && ./phase3_frontend --port {port} &"
        subprocess.run(cmd, shell=True)
        return f"Frontend started on port {port}"
    except Exception as e:
        return f"Failed to start frontend: {e}"

def get_db_status():
    try:
        conn = sqlite3.connect(manager.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        sessions = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM settings")
        settings = cursor.fetchone()[0]
        conn.close()
        return {
            "connected": True,
            "sessions": sessions,
            "settings": settings,
            "file": str(manager.db_file)
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}

def execute_db_query(query):
    try:
        conn = sqlite3.connect(manager.db_file)
        cursor = conn.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            return {"columns": columns, "rows": result}
        else:
            conn.commit()
            conn.close()
            return {"affected_rows": cursor.rowcount}
    except Exception as e:
        return {"error": str(e)}

def restart_system_service(service):
    try:
        if service == "phase3":
            subprocess.run(["pkill", "-f", "mcp_server"], check=False)
            subprocess.Popen(["/home/petr/jetson/phase3/run_mcp_server.sh"])
            return "Phase 3 service restarted"
        else:
            return f"Unknown service: {service}"
    except Exception as e:
        return f"Failed to restart {service}: {e}"

def get_system_logs(lines):
    try:
        result = subprocess.run(["tail", f"-{lines}", "/var/log/syslog"], 
                              capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Failed to get logs: {e}"

async def main():
    try:
        logger.info("Starting Phase 3 Admin MCP Server")
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
