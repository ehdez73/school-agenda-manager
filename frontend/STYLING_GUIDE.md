# Frontend Styling Guide

> Single source of truth for CSS conventions, tokens, and design patterns.
> For **architecture, components, i18n, API, and testing** — see the
> **frontend skill** (`.agents/skills/frontend/SKILL.md`).

---

## 1. CSS Architecture & Import Order

`src/index.css` loads styles in a strict layer order:

```css
@import './styles/globals.css';      /* tokens, reset, base */
@import './styles/utilities.css';    /* flex, spacing, typography helpers */
@import './styles/components.css';   /* btn, input, table, card, chip, alert */
@import './components/Shared.css';   /* state blocks, form patterns, modals */
/* component-local CSS imported in each .jsx file */
```

`Shared.css` comes **after** `components.css` so it can compose the atomic
primitives. Component-local CSS files import last in each `.jsx`.

---

## 2. Design Tokens

All values come from CSS custom properties defined in `src/styles/globals.css:18-78`.
**Never hardcode** colors, spacing, radius, or shadows when a token exists.

```css
/* Correct */
.my-element {
  color: var(--color-primary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

/* Wrong — hardcoded */
.my-element {
  color: #2563eb;
  padding: 1rem;
  border-radius: 6px;
}
```

### 2.1 Colors

| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `#2563eb` | Blue accent (used sparingly for borders, not buttons) |
| `--color-primary-dark` | `#1d4ed8` | Darker primary variant |
| `--color-secondary` | `#64748b` | Muted / secondary elements |
| `--color-success` | `#16a34a` | Positive / success states |
| `--color-warning` | `#f59e0b` | Caution / warning states |
| `--color-danger` | `#ef4444` | Destructive / error states |
| `--color-accent` | `#475569` | Slate-600; non-button accent elements, focus rings |
| `--color-nav-bg` | `#374151` | Navigation bar background |
| `--color-bg` | `#f4f7f6` | Page background |
| `--color-text` | `#222222` | Default text color |
| `--color-text-muted` | `#64748b` | Muted / secondary text |
| `--color-surface` | `#ffffff` | Card / modal / component backgrounds |
| `--color-surface-variant` | `#f8fafc` | Alternate surface (e.g. chip list bg) |
| `--color-border` | `#e2e8f0` | Default borders |
| `--color-border-light` | `#f1f5f9` | Subtle dividers |
| `--color-hover-bg` | `#f1f5f9` | Row/option hover background |
| `--color-hover-text` | `#334155` | Row/option hover text |

**Table colors:**

| Token | Value | Usage |
|-------|-------|-------|
| `--color-table-header` | `#334155` | Table header bg, `.btn--primary` bg |
| `--color-table-header-text` | `#ffffff` | Table header + button text |
| `--color-table-row-even` | `#f8fafc` | Even table rows |
| `--color-table-row-odd` | `#ffffff` | Odd table rows |
| `--color-table-hover` | `#f1f5f9` | Table row hover |

**Input colors:**

| Token | Value |
|-------|-------|
| `--color-input-bg` | `#ffffff` |
| `--color-input-text` | `#222222` |
| `--color-input-border` | `#d1d5db` |
| `--color-input-focus` | `#64748b` |

> **Note:** `.btn--primary` uses `--color-table-header` (`#334155`) as its
> background — not `--color-primary` (blue). This is intentional per the
> slate-based design system.

### 2.2 Spacing

| Token | Value |
|-------|-------|
| `--space-xs` | `0.25rem` |
| `--space-sm` | `0.5rem` |
| `--space-md` | `1rem` |
| `--space-lg` | `1.5rem` |
| `--space-xl` | `2rem` |
| `--space-2xl` | `3rem` |

### 2.3 Border Radius

| Token | Value |
|-------|-------|
| `--radius-sm` | `0.25rem` |
| `--radius-md` | `0.5rem` |
| `--radius-lg` | `0.75rem` |
| `--radius-xl` | `1rem` |
| `--radius-full` | `9999px` |

### 2.4 Shadows

| Token | Value |
|-------|-------|
| `--shadow-sm` | `0 1px 2px 0 rgba(0,0,0,0.05)` |
| `--shadow-md` | `0 4px 6px -1px rgba(0,0,0,0.1)` |
| `--shadow-lg` | `0 10px 15px -3px rgba(0,0,0,0.1)` |

---

## 3. BEM Naming Convention

Use BEM for all shared and component-level CSS:

```css
/* Block */
.section-layout { ... }

/* Element */
.section-layout__header { ... }
.section-layout__content { ... }

/* Modifier */
.btn--primary { ... }
.btn--compact { ... }
```

Component-local classes follow the same pattern: `block-name__element--modifier`.

---

## 4. Shared Primitives (from `components.css`)

Available globally — import is automatic via `index.css`.

### Buttons

| Class | Purpose |
|-------|---------|
| `.btn` | Base button |
| `.btn--primary` | Slate dark (save, primary actions) |
| `.btn--secondary` | Gray (cancel, neutral actions) |
| `.btn--danger` | Red (destructive actions) |
| `.btn--warning` | Amber (caution actions) |
| `.btn--compact` | Smaller padding |
| `.btn--large` | Larger padding |

### Form Controls

| Class | Purpose |
|-------|---------|
| `.input` | Text input |
| `.select` | Native select (themed) |
| `.textarea` | Multi-line text |
| `.form-group` | Label + input wrapper |
| `.form-group__label` | Field label |
| `.form-group__error` | Inline field error |
| `.form-group__help` | Help text below field |
| `.form-info` | Info box (blue-gray) |
| `.form-error` | Error box (red) |

### Tables

| Class | Purpose |
|-------|---------|
| `.modern-table` | Main data table |
| `.modern-table th` | Header cell |
| `.modern-table td` | Body cell |
| `.modern-table .subject-table-th-sort` | Sortable header |

### Other Primitives

| Class | Purpose |
|-------|---------|
| `.chip`, `.chip__remove` | Tag / selection chips |
| `.card`, `.card__header`, `.card__content`, `.card__actions`, `.card__title` | Card container |
| `.alert`, `.alert--success`, `.alert--error`, `.alert--warning`, `.alert--info` | Message banners |
| `.section__title`, `.section__description`, `.section__actions` | Section-level primitives |

---

## 5. Shared State Blocks & Patterns (from `Shared.css`)

### Section States

| Class | Purpose |
|-------|---------|
| `.state-loading` | Centered spinner (used by `SectionLayout`) |
| `.state-error` | Error alert box |
| `.state-empty` | Centered muted message |

### Search & Filter

| Class | Purpose |
|-------|---------|
| `.search-bar` | Filter bar wrapper |
| `.search-input` | Search input (min-width: 200px) |
| `.search-select` | Search dropdown (min-width: 150px) |

### Form Layout

| Class | Purpose |
|-------|---------|
| `.form-container` | Card-style form wrapper |
| `.form-actions` | Button row (flex-end) |
| `.form-actions--start` | Button row (flex-start) |
| `.form-actions--center` | Button row (center) |
| `.form-row`, `.form-row--responsive` | Multi-column form rows |
| `.form-col-1`, `.form-col-2` | Column width in form rows |
| `.form-section` | Section separator inside forms |

### Chip & Action Groups

| Class | Purpose |
|-------|---------|
| `.chip-list`, `.chip-list--compact` | Chip container |
| `.action-group`, `.action-group--compact` | Table row action buttons |

### Table Utilities

| Class | Purpose |
|-------|---------|
| `.table-container` | Scrollable table wrapper |
| `.table-actions` | Table toolbar (flex-between) |
| `.table-row-clickable` | Pointer cursor on rows |
| `.edit-view` | Inline edit wrapper |

### Modal Overlay

| Class | Purpose |
|-------|---------|
| `.modal-overlay` | Fixed full-screen backdrop |
| `.modal-content` | Modal card |

### Misc

| Class | Purpose |
|-------|---------|
| `.loading-spinner` | Inline spinner |
| `.empty-state`, `.empty-state__icon`, `.empty-state__title`, `.empty-state__description` | Empty state card |
| `.subject-name` | Bold subject name |
| `.group-badge` | Small inline group tag |
| `.subject-selection`, `.subject-selection__input`, `.subject-selection__list`, `.subject-selection__empty` | Chip list in forms |

---

## 6. Utility Classes (from `utilities.css`)

### Layout
`.flex`, `.flex-col`, `.flex-wrap`, `.flex-1`, `.items-center`, `.items-start`, `.justify-center`, `.justify-between`, `.justify-end`, `.shrink-0`, `.min-w-0`, `.overflow-x-auto`, `.w-full`

### Gap
`.gap-xs`, `.gap-sm`, `.gap-md`, `.gap-lg`, `.gap-xl`

### Padding
`.p-xs`, `.p-sm`, `.p-md`, `.p-lg`, `.p-xl`

### Margin (all sides)
`.m-xs`, `.m-sm`, `.m-md`, `.m-lg`, `.m-xl`

### Margin-bottom
`.mb-xs`, `.mb-sm`, `.mb-md`, `.mb-lg`, `.mb-xl`

### Margin-top
`.mt-xs`, `.mt-sm`, `.mt-md`, `.mt-lg`, `.mt-xl`

### Typography
`.text-center`, `.text-left`, `.text-right`, `.font-medium`, `.font-semibold`, `.font-bold`, `.text-muted`, `.text-success`, `.text-danger`, `.text-warning`

### Border Radius
`.rounded-sm`, `.rounded-md`, `.rounded-lg`, `.rounded-xl`, `.rounded-full`

### Shadow
`.shadow-sm`, `.shadow-md`, `.shadow-lg`

### Background
`.bg-surface`, `.bg-surface-variant`

### Border
`.border`, `.border-light`

### Block Composition
`.section-block` — card-like container (padding + surface + shadow + radius + margin)

---

## 7. Responsive Breakpoints

| Breakpoint | Where | Behavior |
|------------|-------|----------|
| `1024px` | `HelpSection.css` | TOC sidebar collapses |
| `768px` | `App.css`, `Shared.css`, component CSS | Nav stacks, form columns collapse, `form-row` → column, `form-actions` → column-reverse, `search-bar` → column |
| `720px` | `TeacherList.css` | Preferences grid shrinks |
| `640px` | `SectionLayout.css` | Compact padding, heading stacks |
| `480px` | `App.css` | Nav links stack vertically |

---

## 8. Component CSS Conventions

Each component gets its own CSS file imported at the top of the `.jsx`:

```jsx
import './YourComponent.css';
```

**Rules:**
- Keep component CSS focused on local concerns only
- Use tokens (`var(--color-*)`, `var(--space-*`, `var(--radius-*`, `var(--shadow-*`) — never hardcoded values
- No `!important` — use BEM specificity instead
- Use BEM class names to avoid conflicts with other components
- Responsive overrides specific to this component go here, not in `Shared.css`

Example:

```css
/* YourList.css */
.your-list-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

@media (max-width: 768px) {
  .your-list-header {
    flex-direction: column;
  }
}
```

---

## 9. PR Checklist

- [ ] New section uses `SectionLayout`.
- [ ] No duplicated section headings.
- [ ] Modals outside `SectionLayout` (siblings, not children).
- [ ] All text uses `t('key')` — added to **both** `en.json` and `es.json`.
- [ ] API calls use `api.js` (not raw `fetch`).
- [ ] No `/api/` prefix in API paths — `api.js` already prepends it.
- [ ] No hardcoded colors/spacing/radius — use `var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--shadow-*)`.
- [ ] CSS follows BEM naming, placed in a component-local CSS file.
- [ ] Mobile responsive validated at `768px` and `640px` breakpoints.
- [ ] Tests added for states and regression.
- [ ] Form uses `form-actions` with `btn--primary` (save), `btn--secondary` (cancel), optional `btn--danger` (delete).
- [ ] Table rows clickable → `tabIndex={0}`, `role="button"`, `onKeyDown` for Enter key.
- [ ] New page registered in `App.jsx` with nav button + conditional render.
- [ ] `import React` removed — React 19 JSX transform no longer needs it (unless using `React.useEffect` directly via `React.X`).

---

## 10. Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Hardcoding colors in component CSS | Use `var(--color-*)` tokens from `globals.css` |
| Double `/api` prefix in API paths | `api.js` already prepends `/api` from `VITE_API_BASE`. Use `api.get('/timetable')` not `api.get('/api/timetable')` |
| Using `!important` in CSS | Increase specificity with BEM instead |
| Forgetting to add new i18n keys to both locale files | Add to both `en.json` and `es.json` — missing keys fall back to the key string |
| Duplicating section title in `children` | `SectionLayout` already renders the `<h2>` — remove your duplicate |
| Putting modals inside `SectionLayout` | Place them as siblings outside the layout wrapper |
| Adding custom loading/error/empty banners | Use `SectionLayout`'s built-in `state`, `errorMsg`, `emptyMsg` props |
| Table rows without keyboard accessibility | Add `tabIndex={0}`, `role="button"`, `onKeyDown={e => e.key === 'Enter' && handleEdit(item)}` to clickable `<tr>` elements |

---

## 11. Quick Reference — File Locations

| What | Where |
|------|-------|
| CSS tokens | `src/styles/globals.css:18-78` |
| Shared components | `src/styles/components.css` |
| Utility classes | `src/styles/utilities.css` |
| Shared state blocks | `src/components/Shared.css` |
| CSS entrypoint | `src/index.css` |
| Component-local CSS | `src/components/YourComponent.css` |
