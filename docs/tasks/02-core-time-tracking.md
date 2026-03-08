# Core Time Tracking — Implementation Task Summary

## Relevant Files

### Core Implementation Files

- `core/domain/services/timer_service.py` - TimerService: start/stop, enforce single active timer per user via ORM
- `core/domain/models/` - Time entry / timer state models (state and invariants only; no DB access)
- `core/use_cases/start_timer.py` - StartTimerUseCase; calls TimerService only
- `core/use_cases/stop_timer.py` - StopTimerUseCase; calls TimerService only
- `core/application/dtos.py` - DTOs for timer input/output
- `core/views/timer_views.py` - Views and HTMX endpoints for start/stop (no business logic)
- `templates/core/_timer_partial.html` - Partial template for timer UI (start/stop, active timer display)

### Integration Points

- `core/urls.py` or `project/urls.py` - URL routes for timer actions
- `templates/base.html` - Inclusion of timer partial in layout

### Documentation Files

- Inline or short doc on single-timer rule and flow (as in ADR "Example Flow: Start Timer")

## Sequence Diagram

### Start Timer

```mermaid
sequenceDiagram
    participant User as User/Browser
    participant View as DjangoView
    participant UseCase as StartTimerUseCase
    participant TimerSvc as TimerService
    participant ORM as DjangoORM

    User->>View: HTMX POST start timer
    View->>UseCase: execute(dto)
    UseCase->>TimerSvc: start(user_id, project_id, task_type_id)
    TimerSvc->>ORM: stop existing active timer for user
    ORM-->>TimerSvc: done
    TimerSvc->>ORM: create new time entry
    ORM-->>TimerSvc: entry
    TimerSvc-->>UseCase: result
    UseCase-->>View: result
    View-->>User: partial HTML (timer UI)
```

### Stop Timer

```mermaid
sequenceDiagram
    participant User as User/Browser
    participant View as DjangoView
    participant UseCase as StopTimerUseCase
    participant TimerSvc as TimerService
    participant ORM as DjangoORM

    User->>View: HTMX POST stop timer
    View->>UseCase: execute(dto)
    UseCase->>TimerSvc: stop(user_id)
    TimerSvc->>ORM: get active timer, compute duration, update
    ORM-->>TimerSvc: done
    TimerSvc-->>UseCase: result
    UseCase-->>View: result
    View-->>User: partial HTML (timer UI)
```

## Tasks

- [ ] 1.0 Implement domain models and TimerService (DB access only in service; single active timer per user)
- [ ] 2.0 Implement StartTimerUseCase and StopTimerUseCase (call TimerService; no direct ORM)
- [ ] 3.0 Add presentation: views and HTMX endpoints for start/stop timer (no business logic in views)
- [ ] 4.0 Build timer UI partial(s) with HTMX (start/stop, display active timer); limit full-page reloads for these actions
