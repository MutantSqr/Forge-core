"""
AI Platform Core
A comprehensive framework for building intelligent AI agents with memory, reasoning, 
task management, tool management, security, module management, and auditing capabilities.
"""

__version__ = "0.1.0"
__author__ = "MutantSqr"

from .memory import MemorySystem
from .reasoning import ReasoningEngine
from .task import TaskManager
from .tool import ToolManager
from .security import SecurityManager
from .module import ModuleManager
from .audit import AuditSystem

__all__ = [
    "MemorySystem",
    "ReasoningEngine", 
    "TaskManager",
    "ToolManager",
    "SecurityManager",
    "ModuleManager",
    "AuditSystem",
]