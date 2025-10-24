# Architecture Overview
## Components & Roles
| Component | Role | Notes |
|---|---|---|
| <> | <> | <> |

## Data & Control Flow
```mermaid
flowchart LR
  A[User] --> B[API/UI]
  B --> C[LangGraph Node(s)]
  C --> D[Tools / MCP / Retrievers]
  D --> E[Stores: Vector DB / Cache]
  C --> F[Guardrails / Moderation]
  C --> G[LLM Response]
```

## Graph (Nodes/Edges)
- Nodes: <list>
- Edges: <conditions/routing>
- State: <fields, reducers>
- Human‑in‑the‑loop: <where/how>

## MCP & Tools
- Servers: <>
- Tools: <>
- Bindings: <graph node → tool>

## Observability & Eval
- Tracing: <LangSmith/Phoenix etc.>
- Metrics: <latency, correctness>
- Testsets: <RAGAS etc.>

## Migration / Version Context
- Relevant versions (e.g., LangChain/LangGraph 1.x): <>
- Notable breaking changes: <>
- Before/After summary: <>
- Upgrade path: <steps>

## Decisions & Trade‑offs
- <decision>: reason, alternatives

## Risks & Future Work
- Risk: mitigation
