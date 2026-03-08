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
        DjangoORM
        PostgreSQL[(PostgreSQL)]
    end

    DjangoView --> UseCase
    UseCase --> DTO
    UseCase --> TimerService
    UseCase --> TimesheetService
    UseCase --> ProjectService

    TimerService --> DjangoORM
    TimesheetService --> DjangoORM
    ProjectService --> DjangoORM

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

**Important Rule:**

All database operations happen inside **services**, not in models and
not in other layers.

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

-   Django ORM
-   PostgreSQL
-   External integrations (if any)

Infrastructure is only accessed by Domain Services.

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

-   TimerService
-   TimesheetService
-   ProjectService

Not allowed in:

-   Views
-   Use Cases
-   Domain Models

This guarantees:

-   Predictable transaction handling
-   Easier testing
-   Better maintainability
-   Clean architecture compliance

------------------------------------------------------------------------

# Example Flow: Start Timer

1.  User clicks "Start Timer" (HTMX request)
2.  Django View receives request
3.  View calls StartTimerUseCase
4.  UseCase validates input and creates DTO
5.  UseCase calls TimerService
6.  TimerService:
    -   Stops any existing active timer
    -   Creates new timer entry
    -   Persists using Django ORM
7.  Response returned to View
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

-   Add Repository abstraction if ORM decoupling is needed
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