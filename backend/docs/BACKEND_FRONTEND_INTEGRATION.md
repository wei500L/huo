# BACKEND_FRONTEND_INTEGRATION

## 1. Protocol Overview
Version: `v=1`.

Transport:
- REST for request/response flows
- WebSocket for interactive play
- JSON only

Envelope fields:
- `v`
- `id`
- `ts`
- `direction`
- `type`
- `ack_for`
- `payload`

Encoding rules:
- outbound payloads use camelCase JSON keys
- inbound payloads stay strict and explicit
- unknown keys are rejected unless a route documents otherwise

Message direction:
- `INBOUND` from frontend to backend
- `OUTBOUND` from backend to frontend

Outbound payloads are always serialized from DTOs, not raw domain models.
That is the boundary that keeps backend-only fields out of the frontend contract.

## 2. Message Sequencing
### 2.1 New game
1. Frontend opens `WS /api/v1/ws/{player_id}`
2. Frontend sends `create_game`
3. Backend creates a run
4. Backend sends `GameSnapshot`

### 2.2 Select decision
1. Frontend sends `select_decision`
2. Backend returns `DecisionAck`
3. Backend advances the phase internally
4. If the quarter is Q3, the flow continues toward press handling
5. Otherwise it continues toward settlement

### 2.3 Q3 press conference
1. Frontend sends `submit_press`
2. Backend returns `PressAck`
3. Frontend or backend advances to settlement
4. Backend settles the quarter
5. Backend sends `SettlementBundle`

### 2.4 Death replay
1. Backend settles a terminal quarter
2. `SettlementBundle.death` is present
3. Backend generates `DeathReportBundle`
4. Frontend renders the obituary and unlock summary

### 2.5 Reconnect
1. Frontend reconnects to `WS /api/v1/ws/{player_id}?session_id={session_id}`
2. Backend immediately sends `GameSnapshot`
3. No replay protocol is required

## 3. Async LLM Timing
This is the part to keep stable.

Realtime APIs:
- `create_game`
- `select_decision`
- `collect_gossip`
- `submit_press`
- `state.transition`

Realtime rule:
- zero LLM calls

Settlement rule:
- `settle_quarter` calls 1 Director completion
- Q3 settlement additionally calls 1 PressEval completion

Terminal rule:
- `generate_death_report` calls 1 DeathReport completion

Current per-run cost:
- normal win path: about 5 calls
- death path: about 6 calls

The backend never asks the model during realtime actions.

## 4. Degradation Path
When the model is unavailable or invalid, the backend falls back.

Triggers:
- timeout
- `401`
- `500`
- parse failure
- schema failure

Fallback behavior:
- deterministic stub is used
- `llm_degraded=true`
- outbound bundles stay non-empty
- UI should mark the result as `AI 失联`

Notes:
- fallback is automatic
- fallback is not a special frontend mode
- the session remains playable

## 5. WARN Fields
These are backend-only fields.
They are not sent to the frontend.
They are also not documented as part of the outbound JSON contract.

Field list:
- `hidden_secrets`
- `is_truth`
- `hidden_risks`
- `internalEval`

Validation rule:
- outbound JSON must not contain any of the field names above
- this applies to nested payloads too

## 6. Local Integration
Two supported local modes exist.

### 6.1 Frontend direct mode
The frontend can keep the existing direct model path for local work.
This remains backward compatible.

### 6.2 Backend websocket mode
Point the frontend websocket client at:

```text
ws://localhost:8000/api/v1/ws/{player_id}
```

The backend is designed to be used with test fixtures and local stubs.
No real database is required for this integration path.

Important:
- this backend task does not require starting `uvicorn`
- this backend task does not require `docker`
- this backend task does not require a live database

## 7. v1 vs v2 Fields
v1 is strict.

v1 metrics:
- `CASH`
- `MORALE`
- `BOARD`
- `FACE`

v2 adds extra business dimensions.
Those fields are not part of this backend v1 contract.

Frontend rule:
- do not assume SALES/MKT in v1
- do not synthesize extra metrics in the v1 UI contract

## 8. Static Checks
Use the same checks the backend uses in CI.

```bash
python -m pytest -q
python -m pytest -q --cov=app --cov-report=term-missing
ruff check .
mypy app
```

Coverage config:
- overall backend coverage should stay at or above 80%
- `domain`, `rules`, and parser-related modules should stay above 90%
- `app/repo/sql_stub.py` is excluded from coverage accounting

## 9. Error Codes
Canonical error map:

| HTTP | Code | Meaning |
| --- | --- | --- |
| 404 | `SESSION_NOT_FOUND` | Session was not found |
| 409 | `ILLEGAL_TRANSITION` | Phase transition was invalid |
| 422 | `VALIDATION` | Request payload failed validation |
| 400 | `TRANSCRIPT_REJECTED` | Press transcript was rejected |
| 503 | `LLM_DEGRADED` | LLM path degraded to fallback |
| 500 | `INTERNAL_ERROR` | Unhandled backend failure |

Frontend rule:
- surface the code, not the raw stack trace
- keep retry handling limited to retryable codes

## 10. No Server Start
This backend v1 task does not require a running development server.

Explicitly not required:
- `uvicorn`
- `docker`
- a live database
- a live model endpoint

Backend verification is done through tests and static checks.
Frontend integration should target the websocket route only after the backend contract passes.

## 11. Practical Order
Recommended backend verification order:
1. unit tests
2. architecture tests
3. integration loops
4. coverage
5. lint
6. type checking

Recommended frontend adaptation order:
1. keep direct mode intact
2. add websocket mode behind config
3. switch to websocket mode after backend contract is green

The backend contract is the source of truth for v1.
