from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from hashlib import sha256
from json import dumps
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    SCHEDULED = "scheduled"
    LIVE = "live"
    PAUSED = "paused"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class MemoryItem:
    scope: str
    key: str
    content: str
    source: str
    owner: str
    confidence: float = 1.0
    created_at: datetime = field(default_factory=now)


@dataclass
class Task:
    title: str
    owner: str
    priority: str = "normal"
    due_date: datetime | None = None
    status: str = "not_started"
    dependencies: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: new_id("task"))


@dataclass
class Campaign:
    name: str
    objective: str
    audience: str
    owner: str
    success_metric: str
    status: CampaignStatus = CampaignStatus.DRAFT
    id: str = field(default_factory=lambda: new_id("campaign"))
    tasks: list[Task] = field(default_factory=list)


@dataclass(frozen=True)
class ExternalAction:
    action_type: str
    payload: dict[str, object]
    requested_by: str
    scope: str
    id: str = field(default_factory=lambda: new_id("action"))

    @property
    def payload_hash(self) -> str:
        serialized = dumps(self.payload, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(serialized.encode()).hexdigest()


@dataclass
class ApprovalRequest:
    action: ExternalAction
    summary: str
    requested_at: datetime = field(default_factory=now)
    status: ApprovalStatus = ApprovalStatus.PENDING
    id: str = field(default_factory=lambda: new_id("approval"))
    decided_by: str | None = None
    decided_at: datetime | None = None
    decision_note: str | None = None


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    actor: str
    details: dict[str, object]
    occurred_at: datetime = field(default_factory=now)
    id: str = field(default_factory=lambda: new_id("audit"))
