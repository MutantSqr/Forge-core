from __future__ import annotations

from typing import Protocol

from .models import ApprovalRequest, AuditEvent, MemoryItem


class ScopedMemoryStore(Protocol):
    def save(self, item: MemoryItem) -> None: ...

    def search(self, scope: str, query: str) -> list[MemoryItem]: ...


class ApprovalService(Protocol):
    def request(self, request: ApprovalRequest) -> ApprovalRequest: ...

    def approve(self, approval_id: str, approver: str, note: str = "") -> ApprovalRequest: ...

    def is_approved(self, approval_id: str, action_payload_hash: str) -> bool: ...


class AuditLog(Protocol):
    def record(self, event: AuditEvent) -> None: ...

    def events(self) -> list[AuditEvent]: ...
