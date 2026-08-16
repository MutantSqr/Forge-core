from hashlib import sha256
from json import dumps

from forge_core.contracts.models import AuditEvent


class HashChainedAuditLog:
    """Append-only, in-process audit log with tamper-evident event chaining."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._hashes: list[str] = []

    def record(self, event: AuditEvent) -> None:
        previous = self._hashes[-1] if self._hashes else "GENESIS"
        body = dumps({"event": event.event_type, "actor": event.actor, "details": event.details, "time": event.occurred_at.isoformat(), "previous": previous}, sort_keys=True, default=str)
        self._events.append(event)
        self._hashes.append(sha256(body.encode()).hexdigest())

    def events(self) -> list[AuditEvent]:
        return list(self._events)

    @property
    def head_hash(self) -> str:
        return self._hashes[-1] if self._hashes else "GENESIS"
