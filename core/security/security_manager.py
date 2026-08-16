"""
Security Manager - Orchestrate security components
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .authenticator import Authenticator
from .authorizer import Authorizer
from .encryptor import Encryptor
from .audit_logger import SecurityAuditLogger


class SecurityManager:
    """
    Main security manager that coordinates authentication, authorization, encryption, and auditing.
    """
    
    def __init__(self, 
                 secret_key: str = "default_secret_key_change_in_production",
                 token_expiry_hours: int = 24,
                 enable_encryption: bool = True):
        """
        Initialize the security manager.
        
        Args:
            secret_key: Secret key for token generation and encryption
            token_expiry_hours: Token expiry time in hours
            enable_encryption: Whether to enable encryption
        """
        self.authenticator = Authenticator(secret_key, token_expiry_hours)
        self.authorizer = Authorizer()
        self.encryptor = Encryptor(secret_key) if enable_encryption else None
        self.audit_logger = SecurityAuditLogger()
        
        self._enable_encryption = enable_encryption
        
    def register_user(self, 
                     username: str,
                     password: str,
                     email: str,
                     roles: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password (will be hashed)
            email: User email
            roles: List of roles to assign
            metadata: Additional user metadata
            
        Returns:
            Success status
        """
        # Register user with authenticator
        success = self.authenticator.register_user(username, password, email, roles or [], metadata or {})
        
        if success:
            # Log registration
            self.audit_logger.log_security_event(
                event_type="user_registration",
                username=username,
                details={"email": email, "roles": roles or []}
            )
            
            # Set up default permissions for roles
            if roles:
                for role in roles:
                    self.authorizer.assign_role_permissions(role, self._get_default_role_permissions(role))
        
        return success
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Authentication result with token or None if failed
        """
        result = self.authenticator.authenticate(username, password)
        
        if result:
            # Log successful authentication
            self.audit_logger.log_security_event(
                event_type="user_authentication",
                username=username,
                details={"success": True}
            )
            
            return result
        else:
            # Log failed authentication
            self.audit_logger.log_security_event(
                event_type="user_authentication",
                username=username,
                details={"success": False}
            )
            
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify an authentication token.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None if invalid
        """
        return self.authenticator.verify_token(token)
    
    def authorize_user(self, username: str, permission: str, resource: Optional[str] = None) -> bool:
        """
        Check if a user has permission for a resource.
        
        Args:
            username: Username
            permission: Permission to check
            resource: Optional resource identifier
            
        Returns:
            True if authorized, False otherwise
        """
        # Get user roles
        user = self.authenticator.get_user(username)
        if not user:
            return False
        
        roles = user.get("roles", [])
        
        # Check authorization
        authorized = self.authorizer.authorize(roles, permission, resource)
        
        # Log authorization check
        self.audit_logger.log_security_event(
            event_type="authorization_check",
            username=username,
            details={
                "permission": permission,
                "resource": resource,
                "authorized": authorized
            }
        )
        
        return authorized
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """
        Encrypt data.
        
        Args:
            data: Plain text data
            
        Returns:
            Encrypted data or None if encryption disabled
        """
        if not self._enable_encryption or not self.encryptor:
            return None
        
        return self.encryptor.encrypt(data)
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data or None if decryption failed
        """
        if not self._enable_encryption or not self.encryptor:
            return None
        
        return self.encryptor.decrypt(encrypted_data)
    
    def assign_role(self, username: str, role: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            username: Username
            role: Role to assign
            
        Returns:
            Success status
        """
        success = self.authenticator.assign_role(username, role)
        
        if success:
            # Set up role permissions
            self.authorizer.assign_role_permissions(role, self._get_default_role_permissions(role))
            
            # Log role assignment
            self.audit_logger.log_security_event(
                event_type="role_assignment",
                username=username,
                details={"role": role}
            )
        
        return success
    
    def revoke_role(self, username: str, role: str) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            username: Username
            role: Role to revoke
            
        Returns:
            Success status
        """
        success = self.authenticator.revoke_role(username, role)
        
        if success:
            # Log role revocation
            self.audit_logger.log_security_event(
                event_type="role_revocation",
                username=username,
                details={"role": role}
            )
        
        return success
    
    def get_user_permissions(self, username: str) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            username: Username
            
        Returns:
            List of permissions
        """
        user = self.authenticator.get_user(username)
        if not user:
            return []
        
        roles = user.get("roles", [])
        return self.authorizer.get_permissions_for_roles(roles)
    
    def get_security_audit_log(self, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              event_type: Optional[str] = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get security audit log entries.
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        return self.audit_logger.get_logs(start_date, end_date, event_type, limit)
    
    def get_security_stats(self) -> Dict[str, Any]:
        """
        Get security statistics.
        
        Returns:
            Dictionary with security statistics
        """
        auth_stats = self.authenticator.get_stats()
        authz_stats = self.authorizer.get_stats()
        audit_stats = self.audit_logger.get_stats()
        
        return {
            "authentication": auth_stats,
            "authorization": authz_stats,
            "audit": audit_stats,
            "encryption_enabled": self._enable_encryption
        }
    
    def _get_default_role_permissions(self, role: str) -> List[str]:
        """
        Get default permissions for a role.
        
        Args:
            role: Role name
            
        Returns:
            List of default permissions
        """
        default_permissions = {
            "admin": [
                "read", "write", "delete", "admin",
                "user_management", "role_management", "system_config"
            ],
            "user": [
                "read", "write_own"
            ],
            "moderator": [
                "read", "write", "moderate"
            ],
            "viewer": [
                "read"
            ],
            "analyst": [
                "read", "analyze", "export"
            ]
        }
        
        return default_permissions.get(role, ["read"])
    
    def create_permission(self, permission: str, description: str = "") -> bool:
        """
        Create a new permission.
        
        Args:
            permission: Permission name
            description: Permission description
            
        Returns:
            Success status
        """
        return self.authorizer.create_permission(permission, description)
    
    def assign_permission_to_role(self, role: str, permission: str) -> bool:
        """
        Assign a permission to a role.
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            Success status
        """
        return self.authorizer.assign_permission_to_role(role, permission)
    
    def revoke_permission_from_role(self, role: str, permission: str) -> bool:
        """
        Revoke a permission from a role.
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            Success status
        """
        return self.authorizer.revoke_permission_from_role(role, permission)