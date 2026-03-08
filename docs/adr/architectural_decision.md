# Time Tracking Application

## Overview

This project is a **modular monolith** time-tracking application built
with:

-   Django 5+
-   PostgreSQL
-   HTMX
-   Tailwind CSS

The system allows users to:

-   Track time using an active timer
-   Enforce a single running timer per user
-   View and edit a weekly timesheet
-   Manage Clients and Projects (admin)

The architecture emphasizes clean layering, maintainability, and
efficient database usage.

------------------------------------------------------------------------

# Architecture

The system follows a **layered modular monolith architecture**.

``` mermaid
flowchart TD

    Browser -->|HTMX / HTTP| DjangoView

    subgraph Presentation Layer
        DjangoView
        Templates
    end

    subgraph Application Layer
        UseCase
        DTO
    end

    subgraph Domain Layer
        TimerService
        TimesheetService
        ProjectService
        DomainModels
    end

    subgraph Infrastructure Layer
        Repo[Repository]
        DAO[DAO]
        DjangoORM
        PostgreSQL[(PostgreSQL)]
    end

    DjangoView --> UseCase
    UseCase --> DTO
    UseCase --> TimerService
    UseCase --> TimesheetService
    UseCase --> ProjectService

    TimerService -->|DTO| Repo
    TimesheetService -->|DTO| Repo
    TimesheetService --> DAO
    ProjectService --> Repo

    Repo --> DjangoORM
    DAO --> DjangoORM
    DjangoORM --> PostgreSQL
```

------------------------------------------------------------------------

# Layer Responsibilities

## 1. Presentation Layer

**Responsibilities:**

-   Django Views
-   HTMX endpoints
-   Template rendering
-   Input validation (basic)
-   HTTP concerns

**Rules:**

-   ❌ No business logic
-   ❌ No direct ORM access
-   ✅ Only communicates with Application Layer (UseCases)

------------------------------------------------------------------------

## 2. Application Layer (Use Cases)

**Responsibilities:**

-   Orchestrates domain services
-   Defines transaction boundaries
-   Converts request input into DTOs
-   Coordinates workflows

**Rules:**

-   Services do NOT communicate directly with each other
-   Each use case is independent
-   No direct database access
-   Calls Domain Services only

Example:

-   StartTimerUseCase
-   StopTimerUseCase
-   GenerateWeeklyTimesheetUseCase

------------------------------------------------------------------------

## 3. Domain Layer

**Responsibilities:**

-   Core business rules
-   Timer logic
-   Weekly aggregation logic
-   Enforces single-timer-per-user rule
-   Domain validation

**Important Rules:**

-   **Services:** Receive **DTO in**, return **DTO out** (or domain value objects / row data). No Django model instances (ORM) in service method signatures or return types.
-   **Persistence:** Services depend on **Repository** (and optionally **DAO**) abstractions; they do not use `Model.objects` or QuerySets directly. All DB access is delegated to the Repository/DAO layer.

Services:

-   TimerService
-   TimesheetService
-   ProjectService

Domain Models:

-   Contain state and invariants
-   Do NOT perform database operations

------------------------------------------------------------------------

## 4. Infrastructure Layer

**Responsibilities:**

-   **Repository:** Persistence and querying of **domain entities/aggregates** (e.g. TimeEntry, Client, Project, TaskType, UserProfile). Naming: `TimeEntryRepository`, `ClientRepository`, etc. Implementations use Django ORM and translate to/from DTOs or domain types.
-   **DAO:** Any other DB access that does not map to a single domain aggregate (e.g. existence checks, raw reporting). May be methods on a repository or a dedicated DAO class.
-   Django ORM, PostgreSQL, external integrations

**Repository vs DAO:**

-   **Repository:** Domain entities only. Methods take/return DTOs or simple dataclasses (no ORM in interface).
-   **DAO:** Non-entity DB operations (e.g. existence checks for validation, reporting). Used when the operation is not “load/save one aggregate”.

Infrastructure is only accessed by Domain Services via Repository/DAO abstractions (dependency inversion).

------------------------------------------------------------------------

# Core Design Principles

### 1. Clear Layer Boundaries

Each layer has a single responsibility.

No circular dependencies.

------------------------------------------------------------------------

### 2. Modular Monolith

-   Single deployable unit
-   Internally modular
-   Clear domain separation
-   Ready for future extraction into microservices (if needed)

------------------------------------------------------------------------

### 3. Database Access Rule

Database operations are allowed ONLY inside:

-   **Repository** and **DAO** implementations (e.g. `TimeEntryRepository`, `ClientRepository`, `ProjectRepository`, `TaskTypeRepository`, `UserProfileRepository`)

Services call repositories/DAOs; they do not use `Model.objects` or QuerySets.

Not allowed in:

-   Views
-   Use Cases
-   Domain Models
-   Domain Services (services orchestrate and call repositories; they do not touch ORM directly)

This guarantees:

-   Predictable transaction handling
-   Easier testing (mock repositories in unit tests)
-   Better maintainability and SOLID (dependency inversion)
-   Clean architecture compliance

------------------------------------------------------------------------

# Example Flow: Start Timer

1.  User clicks "Start Timer" (HTMX request)
2.  Django View receives request
3.  View calls StartTimerUseCase
4.  UseCase validates input and creates DTO
5.  UseCase calls TimerService (DTO in)
6.  TimerService:
    -   Calls TimeEntryRepository to stop any existing active timer and create a new entry
    -   Returns domain value object (TimerResult with ActiveTimerState); no ORM in signature
7.  Response (DTO/value object) returned to View
8.  View renders partial template

------------------------------------------------------------------------

# Benefits of This Architecture

-   High maintainability
-   Testable business logic
-   Strict separation of concerns
-   Reduced accidental complexity
-   Scalable design without microservice overhead

------------------------------------------------------------------------

# Future Extensions

-   Repository/DAO layer is in place; further ORM decoupling can add alternative implementations (e.g. read replicas, caching).
-   Introduce Domain Events for cross-module communication
-   Add background job processing (Celery)
-   Implement auditing and observability

------------------------------------------------------------------------

# Conclusion

This project demonstrates a clean modular monolith architecture with:

-   Strict layering
-   Clear transaction boundaries
-   Centralized database access
-   Explicit domain services

It is production-ready while remaining simple and evolvable.