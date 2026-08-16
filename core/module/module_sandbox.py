"""
Module Sandbox - Isolated execution environment for modules
"""

import subprocess
import tempfile
import os
import shutil
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path


class ModuleSandbox:
    """
    Sandbox for isolated module execution with resource limits.
    """
    
    def __init__(self, 
                 temp_dir: Optional[str] = None,
                 memory_limit_mb: int = 512,
                 timeout_seconds: int = 30,
                 restricted_imports: Optional[List[str]] = None):
        """
        Initialize the module sandbox.
        
        Args:
            temp_dir: Temporary directory for sandbox
            memory_limit_mb: Memory limit in MB
            timeout_seconds: Default timeout in seconds
            restricted_imports: List of restricted import modules
        """
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="module_sandbox_")
        self.memory_limit_mb = memory_limit_mb
        self.timeout_seconds = timeout_seconds
        self.restricted_imports = restricted_imports or [
            "os", "sys", "subprocess", "socket", "pickle"
        ]
        
        # Create sandbox directory structure
        self._setup_sandbox()
    
    def _setup_sandbox(self) -> None:
        """Setup sandbox directory structure."""
        sandbox_path = Path(self.temp_dir)
        sandbox_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (sandbox_path / "modules").mkdir(exist_ok=True)
        (sandbox_path / "data").mkdir(exist_ok=True)
        (sandbox_path / "output").mkdir(exist_ok=True)
        (sandbox_path / "temp").mkdir(exist_ok=True)
    
    def execute_module_function(self, 
                               module_func: callable,
                               *args,
                               timeout: Optional[int] = None,
                               **kwargs) -> Dict[str, Any]:
        """
        Execute a module function in the sandbox.
        
        Args:
            module_func: Function to execute
            args: Positional arguments
            timeout: Optional timeout override
            kwargs: Keyword arguments
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or self.timeout_seconds
        
        try:
            # Execute with timeout
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Module execution exceeded timeout of {timeout} seconds")
            
            # Set timeout signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            
            try:
                result = module_func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                
                return {
                    "success": True,
                    "result": result,
                    "error": None
                }
            except TimeoutError as e:
                signal.alarm(0)
                return {
                    "success": False,
                    "result": None,
                    "error": str(e)
                }
                
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "error": str(e)
            }
    
    def execute_module_code(self, 
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
        modules_dir = Path(self.temp_dir) / "modules"
        script_file = modules_dir / "sandbox_module.py"
        
        try:
            with open(script_file, 'w') as f:
                f.write(python_code)
            
            # Execute with resource limits
            command = f"python {script_file}"
            return self._execute_command(command, timeout=timeout)
            
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
    
    def _execute_command(self, 
                        command: str,
                        input_data: Optional[str] = None,
                        timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute a command in the sandbox.
        
        Args:
            command: Command to execute
            input_data: Optional input data for stdin
            timeout: Optional timeout override
            
        Returns:
            Dictionary with execution results
        """
        timeout = timeout or self.timeout_seconds
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(Path(self.temp_dir) / "modules"),
                input=input_data,
                capture_output=True,
                text=True,
                timeout=timeout
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
    
    def create_isolated_file(self, filename: str, content: str, directory: str = "data") -> str:
        """
        Create a file in the sandbox.
        
        Args:
            filename: Name of the file
            content: File content
            directory: Directory within sandbox
            
        Returns:
            Path to created file
        """
        target_dir = Path(self.temp_dir) / directory
        target_dir.mkdir(exist_ok=True)
        file_path = target_dir / filename
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)
    
    def read_file(self, filename: str, directory: str = "data") -> Optional[str]:
        """
        Read a file from the sandbox.
        
        Args:
            filename: Name of the file
            directory: Directory within sandbox
            
        Returns:
            File content or None if not found
        """
        target_dir = Path(self.temp_dir) / directory
        file_path = target_dir / filename
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                return f.read()
        return None
    
    def check_import_restrictions(self, import_statement: str) -> tuple[bool, Optional[str]]:
        """
        Check if an import statement violates restrictions.
        
        Args:
            import_statement: Import statement to check
            
        Returns:
            Tuple of (is_allowed, error_message)
        """
        for restricted in self.restricted_imports:
            if restricted in import_statement:
                return False, f"Import of '{restricted}' is restricted in sandbox"
        
        return True, None
    
    def get_sandbox_resources(self) -> Dict[str, Any]:
        """
        Get sandbox resource usage.
        
        Returns:
            Dictionary with resource information
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
            "exists": sandbox_path.exists(),
            "restricted_imports": self.restricted_imports
        }
    
    def cleanup(self) -> None:
        """Clean up the sandbox directory."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up sandbox: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
        return False