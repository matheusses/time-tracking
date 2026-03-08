# Django + HTMX + Tailwind — Reference

## Advanced patterns

### Inline edit

1. Click row/cell → replace display with form (e.g. `hx-get` form URL, `hx-target="this"`, `hx-swap="innerHTML"`).
2. Submit form → view returns updated fragment; HTMX swaps form back to display.

### Modals

Use a modal container in `base.html`; trigger with `hx-get` to a view that returns `components/modal.html` (or a fragment), `hx-target="#modal-container"`, `hx-swap="innerHTML"`.

### Server-side pagination

- List view accepts `?page=2`; returns only the fragment for that page (e.g. `core/_list_page.html`).
- "Load more" or next button: `hx-get="{% url 'task_list' %}?page=2"` (or next page number), `hx-target="#task-list"`, `hx-swap="beforeend"` (append) or replace list.

### Infinite scroll

Use `hx-trigger="revealed"` (or `intersect`) on a sentinel element at the bottom; `hx-get` next page URL, append to list.

### Django messages + HTMX

Return a fragment that includes `{% if messages %} ... {% endif %}` so messages appear in the same layout (e.g. in a fixed toast area). Optionally use `HX-Trigger` response header to refresh a messages block.

### Optimistic UI

Use `hx-swap="none"` and fire a request; update DOM with Alpine.js or a small script, or use `hx-trigger` with `HX-Trigger` response header to swap another element.

### Template fragment caching

Use `{% load cache %}` and `{% cache 500 fragment_name %} ... {% endcache %}` for expensive partials; invalidate or use a key that includes object version/id.

---

## Stack comparison

- **Django + HTMX + Tailwind:** CRUD-heavy, dashboards, internal tools, fast iteration, server-owned UI.
- **Turbo (Rails/Hotwire):** Similar idea; Turbo Streams for multiple simultaneous updates.
- **React/SPA:** When you need heavy client state, real-time collaboration, or very rich interactivity.

---

## Interview-style summary

> I prefer Django Templates with HTMX for products that don't require heavy client-side interactivity. It reduces JavaScript complexity, keeps logic server-side, improves maintainability, and accelerates development. It's perfect for SaaS dashboards and internal systems. For highly interactive UIs or complex client-side state, I'd choose React; for CRUD-heavy systems, HTMX is often more efficient.

---

## Next-level enhancements

- **Django + HTMX + Alpine.js** — Lightweight client behavior (toggles, dropdowns) without a full SPA.
- **Server-side pagination / infinite scroll** — As above.
- **Modal forms** — Fragment for modal content; `hx-target` into a fixed container.
- **Django Messages + HTMX** — Consistent message display in partial flows.
- **Optimistic UI** — Optional; combine with `HX-Trigger` or small JS.
- **Template fragment caching** — Reduce server work for repeated fragments.
- **Compare with Turbo Streams** — Multiple targeted updates in one response.
