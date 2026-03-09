# Task 10 — Timer action log and start_timer validation — Implementation Task Summary

## Relevant Files

### Core Implementation Files

- `tracking/models.py` — Add `TimerAction` model (event-sourced, append-only)
- `tracking/migrations/0004_timer_action_log.py` — Create TimerAction table; clear TimeEntry data; make project/task_type non-null on TimeEntry
- `tracking/domain/repositories/timer_action.py` — Protocol for TimerAction (insert-only)
- `tracking/infrastructure/repositories/timer_action_repository.py` — Django implementation (append only)
- `tracking/domain/services/timer_service.py` — Validation in start(); call action-log repo on start/stop
- `tracking/application/clients.py` — Handle TimerValidationError
- `tracking/views/timer_views.py` — Catch TimerValidationError, render partial with message
- `tracking/application/dtos.py` — StartTimerInputDTO: project_id and task_type_id required

### Integration Points

- `core/di.py` — Register TimerAction repository and inject into TimerService
- `tracking/urls.py` — Timer endpoints (unchanged)

### Documentation Files

- `README.md` — Security/validation and event-sourcing note for TimerAction
- This task doc and ADR if updated

## Design Summary

- **TimerAction**: Event-sourced table; insert-only (no update, no delete). One row per start, stop, or manual event. Actions: `start`, `stop`, `manual`. For `manual`, the optional `value` field stores `manual_duration_seconds` (duration in seconds).
- **TimeEntry**: Unchanged role (current/last state); project and task_type become required (non-null) after migration.
- **start_timer**: Requires user_id, project_id, task_type_id; validates project/task_type exist; raises TimerValidationError on failure.
- **Migration**: Create TimerAction; delete all TimeEntry rows; alter TimeEntry to non-null project/task_type.

## Tasks

- [ ] 1.0 Create task document (this file) from template
- [ ] 2.0 Add TimerAction model and migration (create table, delete TimeEntry data, TimeEntry project/task_type non-null)
- [ ] 3.0 Repository: protocol + Django implementation insert-only for TimerAction
- [ ] 4.0 Validation: TimerService.start() require project_id/task_type_id; raise TimerValidationError; inject project/task_type repos
- [ ] 5.0 Logging: TimerService start/stop call action-log repository after DB updates
- [ ] 6.0 View + client: catch TimerValidationError and render timer partial with message
- [ ] 7.0 Tests: unit (validation + action log), integration (timer flow + TimerAction rows), functional (HTMX start validation errors)
- [ ] 8.0 Manual entry logging: TimerAction action=`manual` and `value` (duration_seconds); TimesheetService calls action repo after create_manual_entry; migration 0005 adds MANUAL choice and value field.
