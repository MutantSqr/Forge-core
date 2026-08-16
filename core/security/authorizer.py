"""
Authorizer - Role-based access control (RBAC)
"""

from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class Permission:
    """Permission definition."""
    name: str
    description: str
    resources: List[str]


class Authorizer:
    """
    Authorizer for role-based access control (RBAC).
    """
    
    def __init__(self):
        """Initialize the authorizer."""
        self._permissions: Dict[str, Permission] = {}
        self._role_permissions: Dict[str, Set[str]] = {}
        self._resource_permissions: Dict[str, Set[str]] = {}
        
        # Initialize default permissions
        self._initialize_default_permissions()
    
    def _initialize_default_permissions(self) -> None:
        """Initialize default permissions."""
        default_permissions = [
            Permission("read", "Read access to resources", ["*"]),
            Permission("write", "Write access to resources", ["*"]),
            Permission("delete", "Delete access to resources", ["*"]),
            Permission("admin", "Administrative access", ["*"]),
            Permission("user_management", "Manage users", ["users"]),
            Permission("role_management", "Manage roles", ["roles"]),
            Permission("system_config", "Configure system", ["system"]),
            Permission("write_own", "Write own resources", ["own"]),
            Permission("moderate", "Moderate content", ["content"]),
            Permission("analyze", "Analyze data", ["data"]),
            Permission("export", "Export data", ["data"])
        ]
        
        for permission in default_permissions:
            self._permissions[permission.name] = permission
    
    def create_permission(self, name: str, description: str = "", resources: Optional[List[str]] = None) -> bool:
        """
        Create a new permission.
        
        Args:
            name: Permission name
            description: Permission description
            resources: List of resources this permission applies to
            
        Returns:
            Success status
        """
        if name in self._permissions:
            return False
        
        permission = Permission(
            name=name,
            description=description,
            resources=resources or ["*"]
        )
        
        self._permissions[name] = permission
        return True
    
    def assign_permission_to_role(self, role: str, permission: str) -> bool:
        """
        Assign a permission to a role.
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            Success status
        """
        if permission not in self._permissions:
            return False
        
        if role not in self._role_permissions:
            self._role_permissions[role] = set()
        
        self._role_permissions[role].add(permission)
        return True
    
    def revoke_permission_from_role(self, role: str, permission: str) -> bool:
        """
        Revoke a permission from a role.
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            Success status
        """
        if role not in self._role_permissions:
            return False
        
        if permission in self._role_permissions[role]:
            self._role_permissions[role].remove(permission)
            return True
        
        return False
    
    def assign_role_permissions(self, role: str, permissions: List[str]) -> bool:
        """
        Assign multiple permissions to a role.
        
        Args:
            role: Role name
            permissions: List of permission names
            
        Returns:
            Success status
        """
        if role not in self._role_permissions:
            self._role_permissions[role] = set()
        
        for permission in permissions:
            if permission in self._permissions:
                self._role_permissions[role].add(permission)
        
        return True
    
    def authorize(self, roles: List[str], permission: str, resource: Optional[str] = None) -> bool:
        """
        Check if roles have permission for a resource.
        
        Args:
            roles: List of roles
            permission: Permission to check
            resource: Optional resource identifier
            
        Returns:
            True if authorized, False otherwise
        """
        if permission not in self._permissions:
            return False
        
        # Check if any role has the permission
        for role in roles:
            if role in self._role_permissions:
                if permission in self._role_permissions[role]:
                    # Check resource access
                    permission_obj = self._permissions[permission]
                    if self._check_resource_access(permission_obj, resource):
                        return True
        
        return False
    
    def _check_resource_access(self, permission: Permission, resource: Optional[str]) -> bool:
        """
        Check if permission applies to the specified resource.
        
        Args:
            permission: Permission object
            resource: Resource identifier
            
        Returns:
            True if permission applies to resource
        """
        if not resource:
            return True
        
        # Check wildcard permission
        if "*" in permission.resources:
            return True
        
        # Check specific resource
        if resource in permission.resources:
            return True
        
        # Check for resource patterns (e.g., "users:*")
        for resource_pattern in permission.resources:
            if ":" in resource_pattern:
                pattern_prefix, pattern_suffix = resource_pattern.split(":", 1)
                if pattern_suffix == "*" and resource.startswith(pattern_prefix + ":"):
                    return True
        
        return False
    
    def get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        """
        Get all permissions for a list of roles.
        
        Args:
            roles: List of roles
            
        Returns:
            List of permission names
        """
        permissions = set()
        
        for role in roles:
            if role in self._role_permissions:
                permissions.update(self._role_permissions[role])
        
        return list(permissions)
    
    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get permissions for a specific role.
        
        Args:
            role: Role name
            
        Returns:
            List of permission names
        """
        if role not in self._role_permissions:
            return []
        
        return list(self._role_permissions[role])
    
    def get_permission(self, permission: str) -> Optional[Permission]:
        """
        Get a permission by name.
        
        Args:
            permission: Permission name
            
        Returns:
            Permission object or None if not found
        """
        return self._permissions.get(permission)
    
    def list_permissions(self) -> List[Permission]:
        """
        List all permissions.
        
        Returns:
            List of all permissions
        """
        return list(self._permissions.values())
    
    def list_roles(self) -> List[str]:
        """
        List all roles.
        
        Returns:
            List of role names
        """
        return list(self._role_permissions.keys())
    
    def delete_permission(self, permission: str) -> bool:
        """
        Delete a permission.
        
        Args:
            permission: Permission name
            
        Returns:
            Success status
        """
        if permission not in self._permissions:
            return False
        
        # Remove from all roles
        for role_permissions in self._role_permissions.values():
            role_permissions.discard(permission)
        
        # Remove permission
        del self._permissions[permission]
        
        return True
    
    def delete_role(self, role: str) -> bool:
        """
        Delete a role.
        
        Args:
            role: Role name
            
        Returns:
            Success status
        """
        if role not in self._role_permissions:
            return False
        
        del self._role_permissions[role]
        return True
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get authorizer statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_permissions = len(self._permissions)
        total_roles = len(self._role_permissions)
        
        role_permission_counts = {
            role: len(permissions)
            for role, permissions in self._role_permissions.items()
        }
        
        return {
            "total_permissions": total_permissions,
            "total_roles": total_roles,
            "role_permission_counts": role_permission_counts
        }