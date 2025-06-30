# mcp_servers/file_server.py
import json
import os
from pathlib import Path
from typing import Dict, Any, List


class FileSystemMCPServer:
    """Simple MCP server for file system operations"""

    _instance = None  # Class-level variable for Singleton pattern

    def __new__(cls, base_path: str = None):
        if cls._instance is None:
            cls._instance = super(FileSystemMCPServer, cls).__new__(cls)
            # Initialize only once
            cls._instance._init_once(base_path)
        return cls._instance

    def _init_once(self, base_path: str = None):
        if base_path is None:
            current_script_path = Path(__file__).resolve()
            project_root = current_script_path.parent.parent
            self.base_path = project_root / "data"
        else:
            self.base_path = Path(base_path)

        self.base_path.mkdir(exist_ok=True)
        print(f"📁 FileSystemMCPServer (Singleton) Initialized. Base Path: {self.base_path.absolute()}")

    def read_file(self, filepath: str) -> Dict[str, Any]:
        full_path = self.base_path / filepath
        print(f"DEBUG_MCP: Reading file: {full_path.absolute()}")
        try:
            if not full_path.exists():
                print(f"DEBUG_MCP: File NOT FOUND for read: {full_path.absolute()}")
                return {"error": f"File {filepath} not found"}
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"DEBUG_MCP: Successfully read {filepath}")
            return {"success": True, "content": content, "filepath": str(full_path)}
        except Exception as e:
            print(f"DEBUG_MCP: ERROR reading file {full_path.absolute()}: {e}")
            return {"error": str(e)}

    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        full_path = self.base_path / filepath
        print(f"DEBUG_MCP: Writing file: {full_path.absolute()}")
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"DEBUG_MCP: Successfully wrote to {filepath}")
            return {"success": True, "message": f"File written to {full_path}"}
        except Exception as e:
            print(f"DEBUG_MCP: ERROR writing file {full_path.absolute()}: {e}")
            return {"error": str(e)}

    def list_files(self, directory: str = ".") -> Dict[str, Any]:
        dir_path = self.base_path / directory
        print(f"DEBUG_MCP: Listing files in: {dir_path.absolute()}")
        try:
            if not dir_path.exists():
                print(f"DEBUG_MCP: Directory NOT FOUND for list: {dir_path.absolute()}")
                return {"error": f"Directory {directory} not found"}

            files = [f.name for f in dir_path.iterdir() if f.is_file()]
            print(f"DEBUG_MCP: Found files: {files} in {dir_path.absolute()}")
            return {"success": True, "files": files, "directory": str(dir_path)}
        except Exception as e:
            print(f"DEBUG_MCP: ERROR listing files in {dir_path.absolute()}: {e}")
            return {"error": str(e)}
# Test the MCP server
if __name__ == "__main__":
    server = FileSystemMCPServer()

    # Test write
    result = server.write_file("test.txt", "Hello MCP Server!")
    print("Write result:", result)

    # Test read
    result = server.read_file("test.txt")
    print("Read result:", result)

    # Test list
    result = server.list_files()
    print("List result:", result)