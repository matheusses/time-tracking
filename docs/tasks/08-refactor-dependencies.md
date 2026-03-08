# Task 8 — Refactor Dependencies (DI + Clients) — Implementation Task Summary

## Relevant Files

### Core Implementation Files

- `core/di.py` - DI container: repository and client getters
- `tracking/application/clients.py` - TrackClientInterface (Protocol) and TrackClient
- `project_management/application/clients.py` - ProjectManagementClientInterface (Protocol) and ProjectManagementClient

### Integration Points

- `tracking/views/` - Views obtain clients from DI and call only client methods
- `tracking/domain/services/` - TimerService, TimesheetService (unchanged; used by TrackClient)
- `project_management/domain/services/project_service.py` - Used by ProjectManagementClient

### Documentation Files

- `docs/adr/architectural_decision.md` - DI container, Client layer, "views only call clients" rule

## Tasks

- [x] 1.0 Add DI container: create `core/di.py` with getters for all repository interfaces and `get_track_client()` / `get_project_management_client()`
- [x] 2.0 Define TrackClientInterface (Protocol) and TrackClient: constructor takes repository protocols and ProjectManagementClientInterface; implement generate_weekly_timesheet, get_active_timer, start_timer, stop_timer, update_time_entry, has_entries_in_week
- [x] 3.0 Move "weekly timesheet with empty rows" logic into client: client calls TimesheetService.get_weekly_aggregation and ProjectManagementClient.list_projects/list_task_types, merges empty rows, builds WeeklyTimesheetDTO
- [x] 4.0 Define ProjectManagementClientInterface (Protocol) and ProjectManagementClient: constructor takes repository protocols; implement get_timer_options, list_projects, list_clients, list_task_types using ProjectService
- [x] 5.0 Refactor tracking views to use clients only: obtain TrackClient and ProjectManagementClient from DI; replace all use-case execute calls with client method calls
- [x] 6.0 Remove use-case modules; update tests to use clients from DI (get_track_client(), get_project_management_client())
- [x] 7.0 Update ADR: document DI container, Client layer, "views only call clients" rule, and updated layer diagram (Application Layer = Client + DTO)
- [x] 8.0 Rename `docs/tasks/08-tests.md` to `09-tests.md` and fix title to "Task 9 — Tests"
