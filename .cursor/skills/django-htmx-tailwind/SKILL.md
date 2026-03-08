---
name: django-htmx-tailwind
description: Build server-driven UIs with Django Templates, HTMX, and Tailwind CSS. Use when building SaaS dashboards, admin panels, CRUD interfaces, MVPs, or internal tools with partial page updates, HTMX attributes, template partials, or when the user mentions Django + HTMX, server-rendered HTML, or progressive enhancement without a heavy SPA.
---

# Django Templates + HTMX + Tailwind

Server-driven UI with progressive enhancement: backend renders HTML, HTMX handles partial updates, minimal JavaScript, fast development, SEO-friendly.

**Ideal for:** SaaS products, admin panels, internal tools, MVPs, CRUD-heavy systems.

## Core principle

HTMX expects **HTML fragments**, not JSON. Views return partial templates; HTMX injects them into the DOM. No SPA required.

---

## 1. Django Templates

- Template inheritance: `base.html` and `{% block %}`
- Partials: `{% include "app/_partial.html" %}`
- Context processors, CSRF, Django Forms rendering

**Convention:** Filenames starting with `_` are HTMX partials (fragments only).

---

## 2. HTMX attributes

| Attribute   | Purpose                    |
|------------|----------------------------|
| `hx-get`   | GET request                |
| `hx-post`  | POST request               |
| `hx-target`| Where to inject response   |
| `hx-swap`  | How to replace (e.g. `innerHTML`, `beforeend`, `outerHTML`) |
| `hx-trigger` | When (e.g. `click`, `submit`) |
| `hx-include` | Include extra form fields (e.g. `closest form`) |
| `hx-redirect` | Redirect on response    |

Common `hx-swap`: `innerHTML`, `beforeend`, `outerHTML`, `none`.

---

## 3. Tailwind CSS

Focus on: Flexbox, Grid, spacing utilities (`p-*`, `m-*`), responsive prefixes (`sm:`, `md:`), button and form classes. Use CDN or `django-tailwind` / `npm install -D tailwindcss`.

---

## Setup

```bash
pip install django
# Optional: npm install -D tailwindcss  OR  pip install django-tailwind
```

In `base.html`:

```html
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script src="https://cdn.tailwindcss.com"></script>
```

---

## Project structure

```
project/
├── project/
│   ├── settings.py
│   └── urls.py
├── core/
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── models.py
└── templates/
    ├── base.html
    ├── components/
    │   ├── button.html
    │   └── modal.html
    └── core/
        ├── list.html
        ├── _item.html
        └── _form.html
```

---

## CRUD pattern: list + create

**Model**

```python
# models.py
from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
```

**View**

```python
# views.py
from django.shortcuts import render
from .models import Task
from .forms import TaskForm

def task_list(request):
    tasks = Task.objects.all()
    form = TaskForm()
    return render(request, "core/list.html", {"tasks": tasks, "form": form})

def create_task(request):
    form = TaskForm(request.POST)
    if form.is_valid():
        task = form.save()
        return render(request, "core/_item.html", {"task": task})
    # On error: return form fragment with errors (e.g. _form.html)
```

**Base template**

```html
<!-- base.html -->
<html>
<head>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    {% block content %}{% endblock %}
</body>
</html>
```

**List page**

```html
{% extends "base.html" %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">Tasks</h1>

<form
    hx-post="{% url 'create_task' %}"
    hx-target="#task-list"
    hx-swap="beforeend"
    class="mb-4"
>
    {% csrf_token %}
    {{ form.title }}
    <button class="bg-blue-500 text-white px-4 py-2 rounded">Add</button>
</form>

<div id="task-list">
    {% for task in tasks %}
        {% include "core/_item.html" %}
    {% endfor %}
</div>
{% endblock %}
```

**Partial `_item.html`**

```html
<div class="bg-white p-3 rounded shadow mb-2">
    {{ task.title }}
</div>
```

Form submit → Django returns HTML fragment → HTMX injects with `beforeend` → no full page reload.

---

## Quick patterns

**Delete (remove element)**

```html
<button
    hx-delete="{% url 'delete_task' task.id %}"
    hx-target="closest div"
    hx-swap="outerHTML"
>
    Delete
</button>
```

View returns empty or minimal fragment; `hx-swap="outerHTML"` replaces the target (e.g. the row).

**Loading indicator**

```html
<div hx-indicator="#spinner">...</div>
```

**Silent action (no content)**

```python
from django.http import HttpResponse
return HttpResponse(status=204)
```

---

## When to use this stack

**Use for:** SaaS dashboards, admin panels, CRUD systems, internal tools, MVPs, SEO-focused apps.

**Prefer SPA/React for:** Heavy client-side state, drag-and-drop UIs, real-time collaboration, complex client-side flows.

---

## Additional resources

- Advanced patterns (inline edit, modals, pagination, Alpine.js): [reference.md](reference.md)
