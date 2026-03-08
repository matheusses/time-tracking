# Manual Entry — Implementation Task Summary

Users should be able to manually enter and update hours for any day from the weekly timesheet (no timer required).

**Depends on:** Task 04 (Weekly Timesheet & Dynamic UX) — weekly grid and week navigation must be in place.

## Relevant Files

### Core Implementation Files

- `tracking/domain/services/timesheet_service.py` - TimesheetService: `update_or_create_entry` for manual/inline edits
- `tracking/use_cases/update_time_entry.py` - UpdateTimeEntryUseCase for manual entry and updates
- `tracking/views/timesheet_views.py` - Views and HTMX endpoints for grid, inline editing
- `templates/tracking/_timesheet_grid.html` - Partial for weekly grid
- `templates/tracking/_timesheet_cell.html` or inline-edit partial - For cell/row updates

### Integration Points

- `tracking/urls.py` or `project/urls.py` - URL routes for timesheet (week param) and inline update (PATCH/PUT or POST)
- HTMX targets and swaps for grid and row/cell updates (`hx-target`, `hx-swap`)

### Documentation Files

- Manual entry behavior and validation rules

## Tasks

- [x] 1.0 Allow adding hours for a day/project/task when no entry exists (create new time entry from grid)
- [x] 2.0 Allow updating existing hours from the grid (edit existing time entry)
- [x] 3.0 Validation and persistence in domain/service layer (e.g. non-negative hours, valid date/project/task)
- [x] 4.0 HTMX or form submit with partial response for updated cell/row (no full-page reload)
