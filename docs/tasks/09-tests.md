# Task 9 — Tests — Implementation Task Summary

## Relevant Files

### Core Implementation Files

- `core/tests/unit/test_timer_service.py` - Unit tests for TimerService
- `core/tests/unit/test_timesheet_service.py` - Unit tests for TimesheetService
- `core/tests/unit/test_project_service.py` - Unit tests for ProjectService
- `core/tests/unit/test_use_cases.py` - Unit tests for StartTimer, StopTimer, GenerateWeeklyTimesheet, UpdateTimeEntry use cases
- `core/tests/unit/test_domain_models.py` - Unit tests for domain model invariants and validation
- `core/tests/integration/test_timer_flow.py` - Integration tests for timer and timesheet with real DB
- `core/tests/integration/test_auth_and_transactions.py` - Integration tests for auth/permissions and transaction boundaries
- `core/tests/functional/test_htmx_timer_and_timesheet.py` - Functional tests for HTMX endpoints
- `core/tests/functional/test_security.py` - Functional tests for security and negative cases
- Fixtures/factories as needed (e.g. `core/tests/factories.py`)

### Integration Points

- `pytest.ini` or `pyproject.toml` - pytest-django (or Django test runner) configuration
- CI config - Test command and coverage

### Documentation Files

- `README.md` - Testing instructions; security test checklist (OWASP-aligned)

## Test Strategy

Prioritize **unit tests** (majority of coverage); then **integration tests** (DB and layer boundaries); then **functional tests** (end-to-end HTTP/HTMX). Tasks below are segregated by test type.

## Tasks — Unit tests (primary focus)

- [x] 1.0 Unit tests for TimerService: start timer (and that any active timer is stopped), stop timer, single-timer rule (only one active per user), edge cases (no project/task, invalid user)
- [x] 2.0 Unit tests for TimesheetService: weekly aggregation correctness, query count or structure to assert no N+1 (e.g. single query for grid data), get-or-create for manual entry
- [x] 3.0 Unit tests for ProjectService: list clients, list projects by client, list task types; hierarchy and filtering
- [x] 4.0 Unit tests for use cases: StartTimerUseCase, StopTimerUseCase, GenerateWeeklyTimesheetUseCase, UpdateTimeEntryUseCase (input validation, DTO in/out, delegation to correct service; mock services where appropriate)
- [x] 5.0 Unit tests for domain models: invariants, validation (e.g. hours >= 0, date in range)

## Tasks — Integration tests

- [x] 6.0 Integration tests: timer flow with real DB (start → stop → assert entry and duration); weekly timesheet with real DB and assert query count for N+1; project/client/task-type CRUD via service
- [x] 7.0 Integration tests: auth/permissions (authenticated vs anonymous, user can only see own data) and transaction boundaries where relevant

## Tasks — Functional tests

- [x] 8.0 Functional tests: HTMX start/stop timer (client requests, assert partial HTML and status codes); week navigation (change week, assert grid content); inline edit (submit value, assert response and optional follow-up fetch)
- [x] 9.0 Functional tests: security and negative cases (invalid CSRF, invalid payloads, unauthorized access); document in README and align with OWASP
