"""
Tool Sandbox - Isolated execution environment for tools
"""

import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any, Optional
from pathlib import Path


class ToolSandbox:
    """
    Sandbox for isolated tool execution with resource limits.
    """
    
    def __init__(self, 
                 temp_dir: Optional[str] = None,
                 memory_limit_mb: int = 512,
                 timeout_seconds: int = 30):
        """
        Initialize the tool sandbox.
        
        Args:
            temp_dir: Temporary directory for sandbox
            memory_limit_mb: Memory limit in MB
            timeout_seconds: Default timeout in seconds
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="tool_sandbox_")
        self.memory_limit_mb = memory_limit_mb
        self.timeout_seconds = timeout_seconds
        
        # Create sandbox directory structure
        self._setup_sandbox()
    
    def _setup_sandbox(self) -> None:
        """Setup sandbox directory structure."""
        sandbox_path = Path(self.temp_dir)
        sandbox_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (sandbox_path / "input").mkdir(exist_ok=True)
        (sandbox_path / "output").mkdir(exist_ok=True)
        (sandbox_path / "temp").mkdir(exist_ok=True)
        (sandbox_path / "work").mkdir(exist_ok=True)
    
    def execute_command(self, 
                       command: str,
                       input_data: Optional[str] = None,
                       env_vars: Optional[Dict[str, str]] = None,
                       timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a command in the sandbox.
        
        Args:
            command: Command to execute
            input_data: Optional input data for stdin
            env_vars: Optional environment variables
            timeout: Optional timeout override
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or self.timeout_seconds
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if env_vars:
                env.update(env_vars)
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(Path(self.temp_dir) / "work"),
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": timeout  # Approximate
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "execution_time": timeout
            }
        except Exception as e:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0
            }
    
    def execute_python(self, 
                      python_code: str,
                      timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute Python code in the sandbox.
        
        Args:
            python_code: Python code to execute
            timeout: Optional timeout override
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or self.timeout_seconds
        
        # Write code to temporary file
        work_dir = Path(self.temp_dir) / "work"
        script_file = work_dir / "sandbox_script.py"
        
        try:
            with open(script_file, 'w') as f:
                f.write(python_code)
            
            # Execute with resource limits
            command = f"python {script_file}"
            return self.execute_command(command, timeout=timeout)
            
        except Exception as e:
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0
            }
        finally:
            # Clean up script file
            if script_file.exists():
                script_file.unlink()
    
    def create_isolated_file(self, filename: str, content: str) -> str:
        """
        Create a file in the sandbox.
        
        Args:
            filename: Name of the file
            content: File content
            
        Returns:
            Path to created file
        """
        work_dir = Path(self.temp_dir) / "work"
        file_path = work_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)
    
    def read_file(self, filename: str) -> Optional[str]:
        """
        Read a file from the sandbox.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content or None if not found
        """
        work_dir = Path(self.temp_dir) / "work"
        file_path = work_dir / filename
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                return f.read()
        return None
    
    def cleanup(self) -> None:
        """Clean up the sandbox directory."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up sandbox: {e}")
    
    def get_sandbox_info(self) -> Dict[str, Any]:
        """
        Get sandbox information.
        
        Returns:
            Dictionary with sandbox information
        """
        sandbox_path = Path(self.temp_dir)
        
        # Calculate directory size
        total_size = 0
        for file_path in sandbox_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return {
            "temp_dir": self.temp_dir,
            "memory_limit_mb": self.memory_limit_mb,
            "timeout_seconds": self.timeout_seconds,
            "current_size_mb": total_size / (1024 * 1024),
            "exists": sandbox_path.exists()
        }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False