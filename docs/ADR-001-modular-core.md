# ADR-001: Use a modular, local-first core for specialist AIs

**Status:** Accepted  
**Date:** 2026-08-16  
**Deciders:** Bowser Technologies

## Context

Forge Core must support multiple specialist AIs while keeping approval, memory scope,
and auditability consistent. The first specialist is Head of Marketing AI, but its
marketing strategy must not become platform code. The repository is newly initialized,
so early choices should favor a tested vertical slice and stable contracts over vendor
lock-in.

## Decision

Use a Python, dependency-light, local-first modular core. Forge-owned services expose
small protocols and domain models. Specialist modules consume them and contain their
own business logic. All effectful actions are classified and approval-gated before an
adapter can execute them.

## Consequences

- The initial system can run and test without credentials, cloud infrastructure, or
  external vendors.
- Integration adapters can be added behind contracts without changing specialist
  workflows.
- Persistent storage, authentication, queues, and a web API are deliberate later
  additions rather than assumptions hidden in the first prototype.
- In-memory services are development-only and must be replaced before production.
