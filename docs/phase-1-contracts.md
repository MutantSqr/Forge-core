# Phase 1 Contracts

## Forge-owned contracts

`ScopedMemoryStore` saves and retrieves sourced context by scope. `ApprovalService`
creates, approves, rejects, and verifies approval requests. `AuditLog` records
append-only events with hashes linking each event to its predecessor. `CampaignService`
manages campaign and task state.

## Specialist-owned logic

The Head of Marketing AI owns the campaign brief template, message suggestions,
marketing task decomposition, and KPI interpretation. It receives Forge services via
constructor injection; it must never bypass an approval service or write directly to a
connector.

## Effectful action contract

An adapter may run only when all conditions are true:

1. the action has a stable `action_id` and immutable payload hash;
2. its type is recognized by Forge policy;
3. a matching approval exists and is approved;
4. the approval payload hash matches the action payload hash;
5. the requester has permission for the action's scope.

Phase 1 intentionally has no effectful adapters.
