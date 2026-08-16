"""
Authenticator - User authentication and token management
"""

import hashlib
import secrets
import jwt
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class User:
    """User data structure."""
    username: str
    password_hash: str
    email: str
    roles: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True


class Authenticator:
    """
    Authenticator for user authentication and JWT token management.
    """
    
    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        """
        Initialize the authenticator.
        
        Args:
            secret_key: Secret key for JWT token generation
            token_expiry_hours: Token expiry time in hours
        """
        self.secret_key = secret_key
        self.token_expiry_hours = token_expiry_hours
        self._users: Dict[str, User] = {}
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self) -> None:
        """Create default admin user."""
        admin_password = self._hash_password("admin123")  # Change in production
        admin_user = User(
            username="admin",
            password_hash=admin_password,
            email="admin@localhost",
            roles=["admin"],
            metadata={"is_default": True},
            created_at=datetime.now()
        )
        self._users["admin"] = admin_user
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        # In production, use bcrypt or argon2 instead
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            password_hash: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, stored_hash = password_hash.split(":")
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == stored_hash
        except:
            return False
    
    def register_user(self, 
                     username: str,
                     password: str,
                     email: str,
                     roles: List[str],
                     metadata: Dict[str, Any]) -> bool:
        """
        Register a new user.
        
        Args:
            username: Username
            password: Plain text password
            email: User email
            roles: List of roles
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if username in self._users:
            return False
        
        if len(password) < 8:
            return False
        
        password_hash = self._hash_password(password)
        
        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            roles=roles,
            metadata=metadata,
            created_at=datetime.now()
        )
        
        self._users[username] = user
        return True
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user and generate a token.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Authentication result with token or None if failed
        """
        user = self._users.get(username)
        
        if not user or not user.is_active:
            return None
        
        if not self._verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        # Generate token
        token = self._generate_token(user)
        
        return {
            "token": token,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "expires_at": (datetime.now() + timedelta(hours=self.token_expiry_hours)).isoformat()
        }
    
    def _generate_token(self, user: User) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user: User object
            
        Returns:
            JWT token
        """
        payload = {
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "exp": datetime.now() + timedelta(hours=self.token_expiry_hours),
            "iat": datetime.now()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information.
        
        Args:
            username: Username
            
        Returns:
            User information or None if not found
        """
        user = self._users.get(username)
        if not user:
            return None
        
        return {
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "metadata": user.metadata,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_active": user.is_active
        }
    
    def assign_role(self, username: str, role: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            username: Username
            role: Role to assign
            
        Returns:
            Success status
        """
        user = self._users.get(username)
        if not user:
            return False
        
        if role not in user.roles:
            user.roles.append(role)
        
        return True
    
    def revoke_role(self, username: str, role: str) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            username: Username
            role: Role to revoke
            
        Returns:
            Success status
        """
        user = self._users.get(username)
        if not user:
            return False
        
        if role in user.roles:
            user.roles.remove(role)
        
        return True
    
    def deactivate_user(self, username: str) -> bool:
        """
        Deactivate a user.
        
        Args:
            username: Username
            
        Returns:
            Success status
        """
        user = self._users.get(username)
        if not user:
            return False
        
        user.is_active = False
        return True
    
    def activate_user(self, username: str) -> bool:
        """
        Activate a user.
        
        Args:
            username: Username
            
        Returns:
            Success status
        """
        user = self._users.get(username)
        if not user:
            return False
        
        user.is_active = True
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password
            
        Returns:
            Success status
        """
        user = self._users.get(username)
        if not user:
            return False
        
        if not self._verify_password(old_password, user.password_hash):
            return False
        
        if len(new_password) < 8:
            return False
        
        user.password_hash = self._hash_password(new_password)
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get authenticator statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_users = len(self._users)
        active_users = sum(1 for user in self._users.values() if user.is_active)
        
        role_counts = {}
        for user in self._users.values():
            for role in user.roles:
                role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_distribution": role_counts,
            "token_expiry_hours": self.token_expiry_hours
        }