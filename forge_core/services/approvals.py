from forge_core.contracts.models import ApprovalRequest, ApprovalStatus


class InMemoryApprovalService:
    """Development-only approval store. Production implementation requires RBAC and durable storage."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request(self, request: ApprovalRequest) -> ApprovalRequest:
        self._requests[request.id] = request
        return request

    def approve(self, approval_id: str, approver: str, note: str = "") -> ApprovalRequest:
        request = self._requests[approval_id]
        if request.status is not ApprovalStatus.PENDING:
            raise ValueError("Only pending approvals may be approved")
        request.status = ApprovalStatus.APPROVED
        request.decided_by, request.decision_note = approver, note
        from forge_core.contracts.models import now
        request.decided_at = now()
        return request

    def is_approved(self, approval_id: str, action_payload_hash: str) -> bool:
        request = self._requests.get(approval_id)
        return bool(request and request.status is ApprovalStatus.APPROVED and request.action.payload_hash == action_payload_hash)
