# Forge Core

Forge Core is the shared, secure runtime for Bowser Technologies specialist AIs.
It provides the capabilities every specialist needs—identity-ready roles, scoped
memory, approvals, audit records, task orchestration, and policy enforcement—without
embedding the business rules of any particular specialist.

The first vertical slice demonstrates a Head of Marketing AI workflow:

1. create a campaign from a business objective;
2. use approved company context to produce a brief and tasks;
3. request approval for an external draft;
4. record approval and produce an auditable weekly report.

It deliberately does **not** publish content, contact anyone, spend money, or connect
to live services.

## Run the local demonstration

```bash
python3 -m forge_core.demo
```

## Run tests

```bash
python3 -m unittest discover -s tests -v
```

## Package boundaries

- `forge_core/contracts`: stable domain models and interfaces used by specialists.
- `forge_core/services`: reusable Forge services: memory, approvals, audit, and
  campaign/task workflow.
- `forge_core/policies`: default safety policy. Specialist-specific policies belong
  in their own module, not here.
- `forge_core/specialists`: the Head of Marketing AI example adapter. Its messaging,
  strategy, KPI definitions, and channel behavior are business logic.
- `docs`: architecture decisions and implementation contracts.

See `docs/ADR-001-modular-core.md` and `docs/phase-1-contracts.md` before adding a
new specialist or connector.
