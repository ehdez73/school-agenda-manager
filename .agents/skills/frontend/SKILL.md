---
name: frontend
description: >-
  Best practices guide for the School Agenda Manager React 19 frontend.
  Covers code organization, reusable components, i18n, API calls, and
  testing patterns. CSS/design-system details live in frontend/STYLING_GUIDE.md.
---

# Frontend Skill — Building & Extending the UI

Practical guide for adding new views, components, and features to the
React frontend. Focuses on the actual patterns, components, and conventions
used in this codebase.

---

## 0. Architecture Overview

### 0.1 Stack

| Layer | Technology |
|-------|------------|
| Framework | React 19 (JSX, no TypeScript) |
| Build | Vite 7 + `@vitejs/plugin-react` |
| CSS | Plain CSS with custom properties (no Tailwind/CSS Modules/CSS-in-JS) |
| Routing | `useState`-based page switcher in `App.jsx` (no React Router) |
| State | Local `useState` + prop drilling (no Context/Redux) |
| i18n | Custom minimal helper (`src/i18n/index.js`) |
| API | Native `fetch` wrapper (`src/lib/api.js`) |
| Testing | Vitest + `@testing-library/react` + `@testing-library/jest-dom` |
| Linting | ESLint (flat config) |

### 0.2 Source Directory Map

```
frontend/src/
├── main.jsx              # Bootstrap (StrictMode + createRoot)
├── App.jsx               # Root: nav, page routing via useState, locale sync
├── index.css             # CSS entry: imports layers in order
├── assets/               # Static assets (images, icons)
├── components/           # All React components + their CSS + tests
│   ├── SectionLayout.jsx     # — Shared layout wrapper for all sections
│   ├── FormModal.jsx         # — Overlay modal for add/edit forms
│   ├── ConfirmDeleteModal.jsx # — Deletion confirmation dialog
│   ├── AutocompleteSelect.jsx # — Multi/single-select with autocomplete
│   ├── LanguageSelector.jsx   # — Language switcher (EN/ES) popover
│   ├── Select.jsx             # — Custom dropdown select (used by DayIndices, ConfigForm)
│   ├── PreferencesGrid.jsx    # — Sub-component: availability grid
│   ├── useEscapeToCancel.js   # — Hook: Escape key listener for forms
│   ├── CourseList.jsx         # — Section: course management
│   ├── CourseForm.jsx         # — Form: create/edit course
│   ├── SubjectList.jsx        # — Section: subject management
│   ├── SubjectForm.jsx        # — Form: create/edit subject
│   ├── SubjectGroupList.jsx   # — Section: subject group management
│   ├── SubjectGroupForm.jsx   # — Form: create/edit subject group
│   ├── TeacherList.jsx        # — Section: teacher management
│   ├── TeacherForm.jsx        # — Form: teacher + preferences grid
│   ├── FixedSlotList.jsx      # — Section: fixed slots list (embedded in ConfigForm)
│   ├── FixedSlotForm.jsx      # — Form: fixed slot create/edit
│   ├── ConfigForm.jsx         # — Section: app configuration
│   ├── HelpSection.jsx        # — Section: markdown docs viewer + TOC sidebar
│   ├── MarkdownTimetable.jsx  # — Section: timetable viewer with filters, print, diagnostics
│   ├── HourNames.jsx          # — Sub-component: config hour names
│   ├── DayIndices.jsx         # — Sub-component: config day indices
│   ├── SectionLayout.css      # — SectionLayout styles
│   ├── Shared.css             # — Shared state blocks, form patterns, modals
│   ├── FormModal.css          # — Modal overlay styles
│   ├── ConfirmDeleteModal.css # — Delete confirmation styles
│   ├── AutocompleteSelect.css # — Autocomplete dropdown styles
│   ├── Select.css             # — Custom select styles
│   ├── PreferencesGrid.css    # — Availability grid styles
│   ├── CourseList.css         # — Course CRUD styles
│   ├── SubjectList.css        # — Subject CRUD styles
│   ├── SubjectGroupList.css   # — Subject group CRUD styles
│   ├── TeacherList.css        # — Teacher CRUD styles
│   ├── FixedSlotList.css      # — Fixed slot list styles
│   ├── ConfigForm.css         # — Config form styles
│   ├── HelpSection.css        # — Help viewer styles
│   ├── MarkdownTimetable.css  # — Timetable styles (618 lines)
│   └── __tests__/             # — Vitest test files
├── i18n/
│   ├── index.js               # t(), setLocale(), getLocale()
│   └── locales/
│       ├── en.json
│       └── es.json
├── lib/
│   └── api.js                 # Centralized API client
├── styles/
│   ├── globals.css            # CSS custom properties (tokens), reset, base styles
│   ├── utilities.css          # Utility classes (flex, spacing, typography)
│   └── components.css         # Reusable BEM components (btn, input, table, etc.)
└── test/
    ├── setupTests.js          # Test setup (imports jest-dom)
    └── layoutFixtures.jsx     # Shared test helpers
```

### 0.3 Page Routing (App.jsx)

Pages are switched via a `page` state variable persisted to `localStorage`:

```jsx
const [page, setPage] = useState(() => {
  try { return localStorage.getItem('currentPage') || 'home'; } catch { return 'home'; }
});
```

The value maps to conditional rendering. Each page section mounts/unmounts on navigation:

| `page` value | Component rendered |
|---|---|
| `'home'` | Inline `<div className="home">` |
| `'courses'` | `<CourseList />` |
| `'subjects'` | `<SubjectList />` |
| `'teachers'` | `<TeacherList />` |
| `'timetable-markdown'` | `<MarkdownTimetable />` |
| `'config'` | `<ConfigForm />` |
| `'help'` | `<HelpSection />` |

**To add a new page:**
1. Create a new section component (see §3)
2. Import it in `App.jsx`
3. Add a `nav__link` button calling `setPage('your-key')`
4. Add the conditional render: `{page === 'your-key' && <YourComponent />}`

### 0.4 Key Files & Entrypoints (Frontend)

- `src/App.jsx` — root component, top navigation, and `useState`-based page routing.
- `src/index.css` — CSS entrypoint; imports style layers in order (`globals.css` -> `utilities.css` -> `components.css`) plus component styles.
- `src/lib/api.js` — centralized `fetch` wrapper used by UI components.
- `src/i18n/index.js` — i18n helper (`t`, locale get/set) used across the app.

### 0.5 API proxy behavior

- In development, Vite rewrites `/api/*` to `http://localhost:5000/*`.
- In production, API base comes from `VITE_API_BASE` (default `/api`).
- Backend routes should not include an extra `/api` prefix when called through `src/lib/api.js`.

---

## 1. SectionLayout — The Architectural Backbone

Every top-level section **must** use `SectionLayout` (`src/components/SectionLayout.jsx`).
It enforces a consistent structure and handles 4 view states.

### Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `title` | string | Yes | — | Section heading (rendered as `<h2>`) |
| `description` | string | No | — | Helper text below the heading |
| `actions` | ReactNode | No | — | Top-right action area (e.g., "Add" button) |
| `children` | ReactNode | No | — | Main content (rendered only when `state === 'ready'`) |
| `state` | `'ready'\|'loading'\|'error'\|'empty'` | No | `'ready'` | Controls which content block is shown |
| `errorMsg` | string | No | — | Message shown in error state |
| `emptyMsg` | string | No | — | Message shown in empty state |
| `className` | string | No | — | Extra CSS class on the root element |
| `data-testid` | string | No | `'section-layout'` | Test identifier |

### Four View States

```jsx
<SectionLayout title={t('courses.title')} state={state} errorMsg={error} emptyMsg="No items">
  {/* rendered only when state === 'ready' */}
  <table className="modern-table">...</table>
</SectionLayout>
```

- **`ready`** — renders `children`
- **`loading`** — shows spinner with `role="status"` aria-live
- **`error`** — shows alert box with `role="alert"`, displays `errorMsg`
- **`empty`** — shows centered muted text with `emptyMsg`

### Rules

- Do **not** duplicate a section `<h2>` heading inside `children` — `SectionLayout` already renders it.
- Keep modals (`FormModal`, `ConfirmDeleteModal`) **outside** `SectionLayout` siblings (see §2).
- Put primary section-level actions (like "Add" buttons) in the `actions` prop, not inside the content table.

---

## 2. The CRUD List Pattern — Canonical Implementation

Every management section follows the **same** pattern:
- **List view** — `modern-table` with clickable rows + search bar
- **Add** — `FormModal` overlay
- **Edit** — click a table row → inline edit view replaces the table
- **Delete** — `ConfirmDeleteModal` dialog

### 2.1 Full Example (SubjectList pattern — the canonical one)

This is the pattern used by `SubjectList.jsx`, `TeacherList.jsx`, and `SubjectGroupList.jsx`.
(`CourseList.jsx` is legacy and still uses raw `fetch` — prefer the `api.js` pattern below.)

```jsx
import { useEffect, useState } from 'react';
import api from '../lib/api';
import { t } from '../i18n';
import SectionLayout from './SectionLayout';
import FormModal from './FormModal';
import ConfirmDeleteModal from './ConfirmDeleteModal';
import YourForm from './YourForm';
import './YourList.css';

export default function YourList() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(initialFormState);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => { fetchItems(); }, []);

  function fetchItems() {
    setLoading(true);
    setError(null);
    api.get('/your-endpoint')
      .then(setItems)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const action = editingId
      ? api.put(`/your-endpoint/${editingId}`, form)
      : api.post('/your-endpoint', form);
    action.then(() => {
      fetchItems();
      resetForm();
    }).catch(err => setError(err.message));
  }

  function handleEdit(entity) {
    setForm({ /* populate fields from entity */ });
    setEditingId(entity.id);
    setShowForm(false);
    setSelectedEntity(entity);
  }

  function handleDelete(id) {
    setDeleteId(id);
    setShowDeleteModal(true);
  }

  function confirmDelete() {
    api.del(`/your-endpoint/${deleteId}`).then(() => {
      fetchItems();
      setShowDeleteModal(false);
      setDeleteId(null);
      resetForm();
      setSelectedEntity(null);
    });
  }

  function cancelDelete() {
    setShowDeleteModal(false);
    setDeleteId(null);
  }

  function resetForm() {
    setForm(initialFormState);
    setEditingId(null);
    setShowForm(false);
  }

  return (
    <>
      <ConfirmDeleteModal
        open={showDeleteModal}
        entity={t('your.title')}
        id={deleteId}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
      {showForm && (
        <FormModal open={showForm} onClose={resetForm}>
          <YourForm
            form={form}
            setForm={setForm}
            editingId={editingId}
            formError={error}
            onSubmit={handleSubmit}
            onCancel={resetForm}
          />
        </FormModal>
      )}
      <SectionLayout
        title={selectedEntity ? `${t('common.edit')}: ${selectedEntity.name}` : t('your.title')}
        actions={
          !selectedEntity && (
            <button
              className="btn btn--primary btn--compact"
              onClick={() => { resetForm(); setShowForm(true); }}
            >
              {t('your.add')}
            </button>
          )
        }
        state={loading ? 'loading' : error ? 'error' : items.length === 0 && !selectedEntity ? 'empty' : 'ready'}
        errorMsg={error}
        emptyMsg={t('your.empty')}
      >
        {selectedEntity ? (
          <div className="edit-view">
            <YourForm
              form={form}
              setForm={setForm}
              editingId={editingId}
              onSubmit={handleSubmit}
              onCancel={() => { setSelectedEntity(null); resetForm(); }}
              onDelete={() => handleDelete(selectedEntity.id)}
            />
          </div>
        ) : (
          <>
            <div className="search-bar">
              <input
                type="text"
                className="input search-input"
                placeholder={t('common.search_placeholder')}
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <table className="modern-table">
              <thead>
                <tr>
                  <th>{t('your.column1')}</th>
                  <th>{t('your.column2')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredItems.map(item => (
                  <tr key={item.id} onClick={() => handleEdit(item)} style={{ cursor: 'pointer' }}>
                    <td>{item.name}</td>
                    <td>{item.otherField}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
      </SectionLayout>
    </>
  );
}
```

### 2.2 Form Component Pattern

Forms follow a consistent structure — controlled inputs, `form-actions` buttons, and conditional delete:

```jsx
export default function YourForm({ form, setForm, editingId, onSubmit, onCancel, onDelete, formError }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  return (
    <form onSubmit={onSubmit} className="your-form">
      {formError && <div className="form-error">{formError}</div>}
      <div className="form-group">
        <label className="form-group__label">{t('your.field_name')}:</label>
        <input
          name="name"
          className="input"
          value={form.name}
          onChange={handleChange}
          required
          disabled={editingId !== null}
        />
      </div>
      <div className="form-actions">
        <button type="submit" className="btn btn--primary">{t('common.save')}</button>
        <button type="button" className="btn btn--secondary" onClick={onCancel}>
          {t('common.cancel')}
        </button>
        {onDelete && (
          <button type="button" className="btn btn--danger" onClick={onDelete}>
            {t('common.delete')}
          </button>
        )}
      </div>
    </form>
  );
}
```

The form is inlined in an `edit-view` when editing (replacing the table) or rendered inside a `FormModal` when adding.

---

## 3. Existing Reusable Components

### 3.1 FormModal (`src/components/FormModal.jsx`)

Overlay modal for add/edit forms. Escape-to-close built in.

```jsx
<FormModal open={showForm} onClose={handleClose}>
  <YourForm ... />
</FormModal>
```

Props: `open` (boolean), `children`, `onClose`.

Returns `null` when not open. Renders a `.form-modal-overlay` + `.form-modal` wrapper with a close button.

### 3.2 ConfirmDeleteModal (`src/components/ConfirmDeleteModal.jsx`)

Confirmation dialog with i18n support:

```jsx
<ConfirmDeleteModal
  open={showDeleteModal}
  entity={t('your.title')}       // lowercase entity name for "confirm {entity} {id}"
  id={deleteId}
  onConfirm={confirmDelete}
  onCancel={cancelDelete}
/>
```

Props: `open`, `entity`, `id`, `text` (optional override), `onConfirm`, `onCancel`.

Escape-to-close built in. Shows "Confirm {entity} {id}" by default.

### 3.3 AutocompleteSelect (`src/components/AutocompleteSelect.jsx`)

**Use this component whenever you need to select one or more items from a dynamic list with search. Never use a native `<input type="text">` + `<datalist>`, a bare `<select multiple>`, or a third-party combobox library.**

Multi-select (default) or single-select with fuzzy search, keyboard navigation, and chip display. Selected items are shown as removable chips below the input.

```jsx
<AutocompleteSelect
  items={allItems}
  selectedIds={form.selectedIds}
  onAdd={id => setForm(f => ({ ...f, selectedIds: [...f.selectedIds, id] }))}
  onRemove={id => setForm(f => ({ ...f, selectedIds: f.selectedIds.filter(s => String(s) !== String(id)) }))}
  getDisplayLabel={item => item.full_name || item.name}
  placeholder={t('your.search') + '...'}
  noResultsText={t('common.no_results')}
  singleSelect={false}   // true → only one selection allowed at a time
/>
```

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `items` | object[] | Yes | Full list of available items (each must have an `id`) |
| `selectedIds` | string[] | Yes | IDs of currently selected items |
| `onAdd` | fn(id: string) | Yes | Called when the user selects an item |
| `onRemove` | fn(id: string) | Yes | Called when the user removes a chip |
| `getDisplayLabel` | fn(item) → string | No | Label resolver; defaults to `item.full_name \|\| item.name` |
| `placeholder` | string | No | Input placeholder |
| `noResultsText` | string | No | Message when no items match the query |
| `singleSelect` | bool | No | If `true`, replacing existing selection on each add |

**CSS classes (AutocompleteSelect.css):**

| Class | Role |
|-------|------|
| `.autocomplete` | Root wrapper; `position: relative` |
| `.autocomplete__input` | Search text input; design-system tokens (`--color-input-bg`, `--color-input-border`, `--radius-md`) |
| `.autocomplete__dropdown` | Floating results list; `position: absolute`, `z-index: 10`, `--shadow-lg` |
| `.autocomplete__option` | Single result row |
| `.autocomplete__option--highlighted` | Keyboard-focus row; uses `--color-hover-bg` / `--color-hover-text` |
| `.autocomplete__no-results` | Empty-state message; muted italic text |
| `.chip` | Selected-item tag rendered below the input |
| `.chip__remove` | Remove (×) button inside each chip |

Keyboard: ArrowUp/Down to navigate, Enter to select, Escape to close. Click-outside to close.

### 3.4 LanguageSelector (`src/components/LanguageSelector.jsx`)

Language switcher popover in the nav bar:

```jsx
<LanguageSelector value={locale} onChange={setLocaleState} />
```

Switching language triggers `window.location.reload()` to ensure all strings update.

### 3.5 PreferencesGrid (`src/components/PreferencesGrid.jsx`)

**Use this component for any teacher availability / time-preference grid. Never use native `<input type="checkbox">` or radio buttons to represent per-slot availability state — they cannot express three states cleanly and break the design system.**

Three-state toggle grid for teacher availability (day × hour). Each cell is a `<button aria-pressed>` that cycles through three states:

| State | `data-state` | Visual | aria-pressed | Toggle sequence |
|-------|-------------|--------|--------------|-----------------|
| Available | `available` | Default cell | `false` | Next click → Unavailable |
| Unavailable | `unavailable` | Red/blocked cell | `true` | Next click → Preferred |
| Preferred | `preferred` | Green cell | `mixed` | Next click → Available |

```jsx
<PreferencesGrid
  value={form.preferences}   // { [dayIndex]: { unavailable: number[], preferred: number[] } }
  onChange={v => setForm(f => ({ ...f, preferences: v }))}
  classesPerDay={numHours}   // number of hour rows
  days={['Lun', 'Mar', ...]} // optional; falls back to API /config day_names
/>
```

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | object | No | Current state: keys are day indices, values are `{ unavailable, preferred }` arrays |
| `onChange` | fn(value) | No | Called with updated value on each toggle |
| `classesPerDay` | number | No | Number of hour rows (default 5) |
| `days` | string[] | No | Day name headers; fetched from `/config` if not provided |

**Data format emitted by `onChange`:**
```json
{ "0": { "unavailable": [2, 3], "preferred": [0] }, "2": { "unavailable": [], "preferred": [1] } }
```
Day indices with no constraints are omitted from the object.

**Note:** This is a domain-specific component for teacher schedules. Do not use it as a generic checkbox grid.

### 3.6 Select (`src/components/Select.jsx`)

**This is the only component to use for single-option dropdowns in this project. Never use a native `<select>` element — it cannot be themed consistently across browsers and breaks the design system.**

Custom dropdown with click-outside detection, keyboard navigation (ArrowUp/Down, Enter, Escape) and per-option highlight. Fully themed via CSS custom properties.

```jsx
<Select
  value={form.field}
  options={[{ value: 'a', label: 'Option A' }, { value: 'b', label: 'Option B' }]}
  onChange={e => setForm(f => ({ ...f, field: e.target.value }))}
  placeholder="Select..."
  className="search-select"   {/* optional extra class */}
/>
```

**Props:**

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `value` | string | Yes | Currently selected value |
| `options` | `{ value, label }[]` | Yes | List of options to render |
| `onChange` | fn | Yes | Called with `{ target: { value } }` to mimic native `<select>` |
| `placeholder` | string | No | Shown when no option is selected |
| `className` | string | No | Extra CSS class on the root element |

**CSS classes (Select.css):**

| Class | Role |
|-------|------|
| `.custom-select` | Root wrapper; `position: relative` |
| `.custom-select__trigger` | Toggle button; uses design-system tokens (`--color-input-bg`, `--color-input-border`, `--color-input-text`, `--radius-md`) |
| `.custom-select__trigger--placeholder` | Applied when no option is selected; uses `--color-text-muted` |
| `.custom-select--open` | Added to root when dropdown is visible; rotates arrow icon 180° |
| `.custom-select__arrow` | SVG chevron icon inline via `background-image` |
| `.custom-select__dropdown` | Floating options list; `position: absolute`, `z-index: 50`, `--shadow-lg` |
| `.custom-select__option` | Individual option row |
| `.custom-select__option--highlighted` | Keyboard-focus row; uses `--color-hover-bg` / `--color-hover-text` |
| `.custom-select__option--selected` | Currently selected option; `font-weight: 600` |

### 3.7 useEscapeToCancel (`src/components/useEscapeToCancel.js`)

Custom hook that listens for Escape key and calls `onCancel`. Used in all form components.

```jsx
useEscapeToCancel(onCancel);
```

### 3.8 FixedSlotList / FixedSlotForm (`src/components/FixedSlotList.jsx`, `FixedSlotForm.jsx`)

Lists fixed slots (recess, etc.) for courses and teachers. Embedded inside `ConfigForm` via `standalone` prop. Uses the same CRUD list pattern as other sections (FormModal + ConfirmDeleteModal).

### 3.9 HelpSection (`src/components/HelpSection.jsx`)

Renders markdown help docs fetched from the backend. Features:
- TOC sidebar extracted from markdown headings
- Deep-link support via URL hashes
- Cross-language hash resolution (English ↔ Spanish headings)
- 15-second polling for doc updates
- Download and print actions
- Image source rewriting

### 3.10 MarkdownTimetable (`src/components/MarkdownTimetable.jsx`)

The most complex component (~1050 lines). Renders the generated timetable with:
- Dual sidebar: course/teacher selection with checkboxes and search
- Cell color consolidation (same-color entries fill the whole cell)
- Fixed slots visibility toggle
- Download markdown and print
- Diagnostic collapsible for solver errors
- SessionStorage-persisted selection state
- Async generation polling with elapsed time counter

### 3.11 HourNames / DayIndices (`src/components/HourNames.jsx`, `DayIndices.jsx`)

Sub-components used by `ConfigForm` for editing hour labels and day-to-index mappings:

```jsx
<HourNames classesPerDay={n} hourNames={names} setHourNames={setNames} suppressResize={bool} />
<DayIndices daysPerWeek={n} dayIndices={indices} setDayIndices={setIndices} suppressResize={bool} />
```

---

## 4. CSS Design System

> **Full CSS reference lives in `frontend/STYLING_GUIDE.md`** — tokens, BEM,
> shared primitives, utility classes, responsive breakpoints, component CSS
> conventions, and the PR checklist.
>
> The sections below provide a brief overview; consult the styling guide for
> authoritative details.

### 4.1 Overview

- Tokens are defined in `src/styles/globals.css:18-78` (colors, spacing, radius, shadows).
- Shared component primitives live in `src/styles/components.css` (btn, input, table, card, chip, alert).
- Utility classes live in `src/styles/utilities.css` (flex, spacing, typography).
- Shared state blocks and form patterns live in `src/components/Shared.css`.
- Each component owns its own CSS file, imported at the top of the `.jsx`.

### 4.2 Key Rules

- **Never hardcode** colors, spacing, radius, or shadows — use `var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--shadow-*)`.
- **BEM naming** for all CSS classes: `.block__element--modifier`.
- **No `!important`** — use specificity instead.
- See `frontend/STYLING_GUIDE.md` §2–§8 for the full token reference and conventions.

---

## 5. i18n (Internationalization)

### 5.1 Usage

```jsx
import { t } from '../i18n';

// Simple key
{t('courses.title')}

// With template variables (defined in the locale JSON as "Hello {name}!")
{t('common.greeting', { name: 'John' })}
```

### 5.2 Adding New Keys

1. Add the key to **both** `src/i18n/locales/en.json` and `src/i18n/locales/es.json`
2. Use dot-notation keys like `sectionName.subsection.field`

```json
{
  "your": {
    "title": "Your Items",
    "add": "Add Item",
    "empty": "No items yet",
    "field_name": "Name"
  }
}
```

### 5.3 How It Works

- `t(key, vars)` walks dot-separated keys through the locale object
- If a key is not found, it returns the key string itself (visible fallback)
- Locale is detected from `localStorage` → `navigator.language` → `'en'`
- `setLocale(code)` updates `localStorage` and triggers a full page reload in `LanguageSelector`

---

## 6. API Calls

### 6.1 The `api.js` Client (`src/lib/api.js`)

Always prefer the centralized API helper over raw `fetch`:

```js
import api from '../lib/api';

// GET
const items = await api.get('/your-endpoint');
const text = await api.get('/text-endpoint', { responseType: 'text' });

// POST
const created = await api.post('/your-endpoint', { name: 'value' });

// PUT
await api.put('/your-endpoint/id', { name: 'updated' });

// DELETE
await api.del('/your-endpoint/id');

// With cache busting (avoid browser-cached responses)
await api.get('/config', { cacheBust: true });
```

The client:
- Defaults `API_BASE` to `/api` (configurable via `VITE_API_BASE` env var)
- Automatically attaches `X-Locale` header from `localStorage`
- Sets `Content-Type: application/json` for POST/PUT bodies
- Parses JSON error responses into `Error` with `.status` and `.details` properties
- Supports `responseType: 'json'` (default) or `responseType: 'text'`
- Vite proxy in `vite.config.js` forwards `/api` → `http://localhost:5000` in dev

### 6.2 Error Handling

```js
try {
  const data = await api.post('/endpoint', payload);
} catch (err) {
  // err.message  — error text
  // err.status   — HTTP status code
  // err.details  — optional details from backend
  setError(err.message);
}
```

### 6.3 Legacy Pattern (avoid for new code)

`CourseList.jsx` uses raw `fetch()` directly. **Do not follow this pattern** for new components — use `api.js` instead.

---

## 7. Component-Level CSS

> **Full conventions live in `frontend/STYLING_GUIDE.md` §8** (Component CSS Conventions).

Each component gets its own CSS file imported at the top of the `.jsx`:

```jsx
import './YourComponent.css';
```

**Rules (summary — see styling guide for full details):**
- Keep component CSS focused on local concerns only
- Use tokens instead of hardcoded values
- No `!important` — use BEM specificity instead
- Responsive overrides specific to this component go here, not in `Shared.css`

---

## 8. Testing

### 8.1 Setup

- Framework: Vitest 3 + jsdom
- Library: `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`
- Config: `vitest.config.js` with `globals: true`, `css: true`
- Test location: `src/components/__tests__/`
- Setup file: `src/test/setupTests.js`

### 8.2 Test Patterns

**Layout/contract tests** verify SectionLayout renders correctly in all states:

```jsx
import { renderSection } from '../../test/layoutFixtures';

it('renders title and actions', () => {
  const { getByText } = renderSection({
    title: 'My Section',
    actions: <button>Add</button>,
  });
  expect(getByText('My Section')).toBeInTheDocument();
  expect(getByText('Add')).toBeInTheDocument();
});
```

**Component tests** mock `api` and `i18n`:

```jsx
import { vi } from 'vitest';

vi.mock('../../lib/api', () => ({
  default: {
    get: vi.fn().mockResolvedValue([]),
    post: vi.fn().mockResolvedValue({}),
    del: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../../i18n', () => ({
  t: key => key,
}));
```

### 8.3 Fixtures (`src/test/layoutFixtures.jsx`)

```jsx
import { render } from '@testing-library/react';
import SectionLayout from '../components/SectionLayout';

export function renderSection(overrides = {}) {
  const props = {
    title: 'Test Section',
    children: <div data-testid="content">content</div>,
    ...overrides,
  };
  return render(<SectionLayout {...props} />);
}
```

### 8.4 What to Test

- SectionLayout renders all 4 states correctly
- List components show loading, error, empty states
- Forms submit the correct payload
- Delete confirmation flow works
- Regression tests: guard against accidental changes to form/list structure

### 8.5 Testing Gotchas (Frontend)

- Keep component tests in `src/components/__tests__/` (this repo convention).
- Use Vitest with jsdom (configured in `vitest.config.js`) so DOM/UI assertions behave correctly.

---

## 9. Adding a New Section — Checklist

> For CSS-specific items, see also `frontend/STYLING_GUIDE.md` §9 (PR Checklist).

Use this checklist when creating a new feature/section in the frontend:

- [ ] Component uses `SectionLayout` as its wrapper
- [ ] No duplicated section `<h2>` headings
- [ ] Modals (`FormModal`, `ConfirmDeleteModal`) are **outside** `SectionLayout`
- [ ] All text strings use `t('key')` and are added to both `en.json` and `es.json`
- [ ] API calls use `api.js` (not raw `fetch`)
- [ ] No `/api/` prefix in API paths — `api.js` already prepends it
- [ ] No hardcoded colors, spacing, or radius — use `var(--color-*)`, `var(--space-*)`, `var(--radius-*)`, `var(--shadow-*)`
- [ ] CSS follows BEM naming, placed in a component-local CSS file
- [ ] Responsive behavior validated at `768px` and `640px` breakpoints
- [ ] Tests added in `src/components/__tests__/` for states and regression
- [ ] New page registered in `App.jsx` with nav button + conditional render
- [ ] Form uses `form-actions` with `btn--primary` (save), `btn--secondary` (cancel), optional `btn--danger` (delete)
- [ ] Table rows are clickable → inline edit view, `tabIndex={0}`, `role="button"`, `onKeyDown` for Enter key
- [ ] `import React` removed (React 19 JSX transform) — only needed when using `React.cloneElement` or `React.useEffect` directly

---

## 10. Quick Reference — File Locations

| What | Where |
|------|-------|
| Page routing & nav | `src/App.jsx:14-16` |
| SectionLayout component | `src/components/SectionLayout.jsx:16-61` |
| FormModal | `src/components/FormModal.jsx` |
| ConfirmDeleteModal | `src/components/ConfirmDeleteModal.jsx` |
| AutocompleteSelect | `src/components/AutocompleteSelect.jsx` |
| Select | `src/components/Select.jsx` |
| LanguageSelector | `src/components/LanguageSelector.jsx` |
| PreferencesGrid | `src/components/PreferencesGrid.jsx` |
| useEscapeToCancel hook | `src/components/useEscapeToCancel.js` |
| HelpSection | `src/components/HelpSection.jsx` |
| MarkdownTimetable | `src/components/MarkdownTimetable.jsx` |
| FixedSlotList / FixedSlotForm | `src/components/FixedSlotList.jsx`, `FixedSlotForm.jsx` |
| API client | `src/lib/api.js` |
| i18n helper (`t()`) | `src/i18n/index.js` |
| CSS tokens | `src/styles/globals.css:18-78` |
| CSS shared components | `src/styles/components.css` |
| CSS utilities | `src/styles/utilities.css` |
| CSS shared state blocks | `src/components/Shared.css` |
| Test fixtures | `src/test/layoutFixtures.jsx` |
| Styling guide (tokens, BEM, utilities, responsive, conventions) | `frontend/STYLING_GUIDE.md` |

---

## 11. Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| **Using native `<select>` for dropdowns** | Use `<Select>` from `src/components/Select.jsx` — native selects can't be themed consistently across browsers. ⚠️ Pre-existing violations in `JointClassForm.jsx`, `SubjectForm.jsx`, `MarkdownTimetable.jsx` |
| **Using `<input>` + `<datalist>` or `<select multiple>` for search-select** | Use `<AutocompleteSelect>` from `src/components/AutocompleteSelect.jsx` |
| **Using `<input type="checkbox">` for tri-state availability per timeslot** | Use `<PreferencesGrid>` for teacher availability grids. ⚠️ Pre-existing native checkbox usage in `ConfigForm.jsx`, `JointClassForm.jsx`, `SubjectGroupForm.jsx`, `TeacherForm.jsx`, `SubjectForm.jsx`, `MarkdownTimetable.jsx` — fix if touching those areas |
| Using `<a>` tags for nav | Use `<button>` with `onClick` — there's no URL routing |
| Adding a new nav link but not the conditional render | Both the button in `nav__links` AND the `{page === 'x' && <Component />}` are required |
| Hardcoding colors in component CSS | Use `var(--color-*)` tokens from `globals.css` |
| Using raw `fetch()` instead of `api.js` | Import `api` from `'../lib/api'` and use `api.get/post/put/del` |
| **Double `/api` prefix in API paths** | `api.js` already prepends `/api` from `VITE_API_BASE`. Use `api.get('/timetable')` not `api.get('/api/timetable')` |
| **Unused `import React`** | React 19's JSX transform doesn't need it. Only keep when using `React.cloneElement`, `React.useEffect` (via `React.X`), etc. |
| **`window.location.reload()` loses React state** | After import/clear/export, consider alternative patterns. Language selector reloads the whole page. |
| **`generateLineLetters` / `toggleLine` duplicated** | These functions are copied in `SubjectForm.jsx` and `SubjectGroupForm.jsx`. Extract to `src/lib/utils.js`. |
| **Dual modal state (`showForm` + `selectedEntity`)** | Can cause both modals to render simultaneously. Prefer a single state: `{ mode: 'closed' \| 'add' \| 'edit', entity?: T }`. |
| **Table rows without keyboard accessibility** | Add `tabIndex={0}`, `role="button"`, `onKeyDown={e => e.key === 'Enter' && handleEdit(item)}` to clickable `<tr>` elements. |
| Forgetting to add new i18n keys to both locale files | Add to both `en.json` and `es.json` — missing keys fall back to the key string |
| Duplicating section title in `children` | `SectionLayout` already renders the `<h2>` — remove your duplicate |
| Putting modals inside `SectionLayout` | Place them as siblings outside the layout wrapper |
| Adding custom loading/error/empty banners | Use `SectionLayout`'s built-in `state`, `errorMsg`, `emptyMsg` props |
| Using `!important` in CSS | Increase specificity with BEM instead |
