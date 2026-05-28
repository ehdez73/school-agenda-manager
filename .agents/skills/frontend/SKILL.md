---
name: frontend
description: >-
  Best practices guide for the School Agenda Manager React 19 frontend.
  Covers code organization, reusable components, CSS design system, i18n,
  API calls, and testing patterns used in this project.
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
├── App.jsx               # Root: nav, page routing via useState, theme/locale sync
├── index.css             # CSS entry: imports layers in order
├── assets/               # Static assets (images, icons)
├── components/           # All React components + their CSS + tests
│   ├── SectionLayout.jsx     # — Shared layout wrapper for all sections
│   ├── FormModal.jsx         # — Overlay modal for add/edit forms
│   ├── ConfirmDeleteModal.jsx # — Deletion confirmation dialog
│   ├── AutocompleteSelect.jsx # — Multi/single-select with autocomplete
│   ├── LanguageSelector.jsx   # — Language switcher (EN/ES) popover
│   ├── CourseList.jsx         # — Section: course management
│   ├── CourseForm.jsx         # — Form: create/edit course
│   ├── SubjectList.jsx        # — Section: subject management
│   ├── SubjectForm.jsx        # — Form: create/edit subject
│   ├── SubjectGroupList.jsx   # — Section: subject group management
│   ├── SubjectGroupForm.jsx   # — Form: create/edit subject group
│   ├── TeacherList.jsx        # — Section: teacher management
│   ├── TeacherForm.jsx        # — Form: teacher + preferences grid
│   ├── ConfigForm.jsx         # — Section: app configuration
│   ├── HourNames.jsx          # — Sub-component: config hour names
│   ├── DayIndices.jsx         # — Sub-component: config day indices
│   ├── PreferencesGrid.jsx    # — Sub-component: availability grid
│   └── __tests__/             # — Vitest test files
├── i18n/
│   ├── index.js               # t(), setLocale(), getLocale()
│   └── locales/
│       ├── en.json
│       └── es.json
├── lib/
│   └── api.js                 # Centralized API client
├── styles/
│   ├── globals.css            # CSS custom properties (tokens), reset, themes
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
| `'subject-groups'` | `<SubjectGroupList />` |
| `'timetable-markdown'` | `<MarkdownTimetable />` |
| `'config'` | `<ConfigForm />` |

**To add a new page:**
1. Create a new section component (see §3)
2. Import it in `App.jsx`
3. Add a `nav__link` button calling `setPage('your-key')`
4. Add the conditional render: `{page === 'your-key' && <YourComponent />}`

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
import React, { useEffect, useState } from 'react';
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
          disabled={editingId !== null} // disable PK when editing
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

Multi-select (default) or single-select with search, keyboard navigation, and chip display:

```jsx
<AutocompleteSelect
  items={allItems}
  selectedIds={form.selectedIds}
  onAdd={id => setForm(f => ({ ...f, selectedIds: [...f.selectedIds, id] }))}
  onRemove={id => setForm(f => ({ ...f, selectedIds: f.selectedIds.filter(s => String(s) !== String(id)) }))}
  getDisplayLabel={item => item.full_name || item.name}
  placeholder={t('your.search') + '...'}
  noResultsText="No results"
  singleSelect={false}
/>
```

Keyboard: ArrowUp/Down to navigate, Enter to select, Escape to close. Click-outside to close.

### 3.4 LanguageSelector (`src/components/LanguageSelector.jsx`)

Language switcher popover in the nav bar:

```jsx
<LanguageSelector value={locale} onChange={setLocaleState} />
```

Switching language triggers `window.location.reload()` to ensure all strings update.

### 3.5 PreferencesGrid (`src/components/PreferencesGrid.jsx`)

Three-state toggle grid for teacher availability (day × hour):

| State | Visual | Toggle sequence |
|-------|--------|-----------------|
| Available | Default | Next click → Unavailable |
| Unavailable | Red/blocked cell | Next click → Preferred |
| Preferred | Green cell | Next click → Available |

```jsx
<PreferencesGrid
  value={form.preferences}
  onChange={v => setForm(f => ({ ...f, preferences: v }))}
  classesPerDay={numHours}
/>
```

### 3.6 HourNames / DayIndices (`src/components/HourNames.jsx`, `DayIndices.jsx`)

Sub-components used by `ConfigForm` for editing hour labels and day-to-index mappings:

```jsx
<HourNames classesPerDay={n} hourNames={names} setHourNames={setNames} suppressResize={bool} />
<DayIndices daysPerWeek={n} dayIndices={indices} setDayIndices={setIndices} suppressResize={bool} />
```

---

## 4. CSS Design System

### 4.1 Import Order (`src/index.css`)

```css
@import './styles/globals.css';      /* tokens, reset, themes */
@import './styles/utilities.css';    /* flex, spacing, typography helpers */
@import './styles/components.css';   /* btn, input, table, card, chip, alert */
@import './components/Shared.css';   /* state blocks, form patterns, modals */
/* component-local CSS imported in each .jsx file */
```

### 4.2 Token Usage Rules

Never hardcode values when a CSS variable exists:

```css
/* ✅ Correct */
.my-element {
  color: var(--color-primary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

/* ❌ Wrong — hardcoded */
.my-element {
  color: #2563eb;
  padding: 1rem;
  border-radius: 6px;
}
```

| Token category | Example variables |
|----------------|------------------|
| Colors | `--color-primary`, `--color-danger`, `--color-bg`, `--color-text`, `--color-surface`, `--color-border` |
| Spacing | `--space-xs` (0.25rem), `--space-sm` (0.5rem), `--space-md` (1rem), `--space-lg` (1.5rem), `--space-xl` (2rem), `--space-2xl` (3rem) |
| Border radius | `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, `--radius-full` |
| Shadows | `--shadow-sm`, `--shadow-md`, `--shadow-lg` |

Full token reference: `src/styles/globals.css:18-71`.

### 4.3 BEM Naming Convention

Use BEM for shared component blocks:

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

### 4.4 Shared Primitives (available globally from `components.css`)

| Class | Purpose |
|-------|---------|
| `.btn`, `.btn--primary`, `.btn--secondary`, `.btn--danger`, `.btn--compact` | Buttons |
| `.input`, `.select`, `.textarea` | Form controls |
| `.form-group`, `.form-group__label`, `.form-group__error` | Form layout |
| `.modern-table`, `.modern-table th`, `.modern-table td` | Data tables |
| `.chip`, `.chip__remove` | Tags / selections |
| `.card`, `.card__header`, `.card__content` | Cards |
| `.alert`, `.alert--success`, `.alert--error` | Messages |
| `.section__title`, `.section__description`, `.section__actions` | Section primitives |

### 4.5 Shared State Blocks (from `Shared.css`)

| Class | Where used |
|-------|------------|
| `.state-loading` | SectionLayout `loading` state |
| `.state-error` | SectionLayout `error` state |
| `.state-empty` | SectionLayout `empty` state |
| `.search-bar`, `.search-input` | List filter bars |
| `.form-actions` | Form button rows |
| `.subject-selection__list` | Chip list containers |
| `.edit-view` | Inline edit wrapper |

### 4.6 Utility Classes (from `utilities.css`)

Layout: `.flex`, `.flex-col`, `.flex-wrap`, `.items-center`, `.justify-center`, `.justify-between`
Spacing: `.p-sm`, `.p-md`, `.p-lg`, `.mb-md`, `.mb-lg`, `.mt-sm`, `.mt-md`, `.gap-sm`, `.gap-md`
Typography: `.text-center`, `.font-bold`, `.text-muted`, `.text-success`, `.text-danger`
Other: `.w-full`, `.rounded-md`, `.shadow-sm`, `.bg-surface`, `.border`

### 4.7 Dark Mode

The app supports light/dark themes via `data-theme` attribute on `<html>`:

```css
[data-theme="dark"] {
  --color-bg: #18181b;
  --color-surface: #23272f;
  --color-text: #f4f7f6;
  /* ... redefines all relevant tokens */
}
```

Toggle in `App.jsx` via a `<select>` that sets `document.documentElement.setAttribute('data-theme', theme)`.

If you add a new component CSS file, test it under both themes. Use `[data-theme="dark"]` overrides only when the default tokens don't suffice.

### 4.8 Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| `640px` | Compact SectionLayout padding |
| `768px` | Nav stacks, form columns collapse, `form-row` → column, `form-actions` → column-reverse, `search-bar` → column |
| `480px` | Nav links stack vertically |
| `720px` | Preferences grid shrinks |

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

Each component gets its own CSS file imported at the top of the component:

```jsx
import './YourComponent.css';
```

**Rules:**
- Keep component CSS focused on local concerns only
- Use tokens (`var(--color-*)`, `var(--space-*)`) instead of hardcoded values
- No `!important` — use specificity instead
- Use BEM-style class names to avoid conflicts
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

---

## 9. Adding a New Section — Checklist

Use this checklist when creating a new feature/section in the frontend:

- [ ] Component uses `SectionLayout` as its wrapper
- [ ] No duplicated section `<h2>` headings
- [ ] Modals (`FormModal`, `ConfirmDeleteModal`) are **outside** `SectionLayout`
- [ ] All text strings use `t('key')` and are added to both `en.json` and `es.json`
- [ ] API calls use `api.js` (not raw `fetch`)
- [ ] No hardcoded colors, spacing, or radius — use `var(--color-*)`, `var(--space-*)`, `var(--radius-*)`
- [ ] CSS follows BEM naming, placed in a component-local CSS file
- [ ] Dark mode works (verify with `data-theme="dark"`)
- [ ] Responsive behavior validated at `768px` and `640px` breakpoints
- [ ] Tests added in `src/components/__tests__/` for states and regression
- [ ] New page registered in `App.jsx` with nav button + conditional render
- [ ] Form uses `form-actions` with `btn--primary` (save), `btn--secondary` (cancel), optional `btn--danger` (delete)
- [ ] Table rows are clickable → inline edit view, not modal-for-edit

---

## 10. Quick Reference — File Locations

| What | Where |
|------|-------|
| Page routing & nav | `src/App.jsx:14-16` |
| SectionLayout component | `src/components/SectionLayout.jsx:16-61` |
| FormModal | `src/components/FormModal.jsx:4-24` |
| ConfirmDeleteModal | `src/components/ConfirmDeleteModal.jsx:5-30` |
| AutocompleteSelect | `src/components/AutocompleteSelect.jsx:4-146` |
| API client | `src/lib/api.js:1-76` |
| i18n helper (`t()`) | `src/i18n/index.js:29-46` |
| CSS tokens | `src/styles/globals.css:18-71` |
| CSS shared components | `src/styles/components.css:1-389` |
| CSS utilities | `src/styles/utilities.css:1-259` |
| CSS shared state blocks | `src/components/Shared.css:1-288` |
| Test fixtures | `src/test/layoutFixtures.jsx` |
| Styling guide (PR checklist) | `frontend/STYLING_GUIDE.md:95-101` |

---

## 11. Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Using `<a>` tags for nav | Use `<button>` with `onClick` — there's no URL routing |
| Adding a new nav link but not the conditional render | Both the button in `nav__links` AND the `{page === 'x' && <Component />}` are required |
| Hardcoding colors in component CSS | Use `var(--color-*)` tokens from `globals.css` |
| Using raw `fetch()` instead of `api.js` | Import `api` from `'../lib/api'` and use `api.get/post/put/del` |
| Forgetting to add new i18n keys to both locale files | Add to both `en.json` and `es.json` — missing keys fall back to the key string |
| Duplicating section title in `children` | `SectionLayout` already renders the `<h2>` — remove your duplicate |
| Putting modals inside `SectionLayout` | Place them as siblings outside the layout wrapper |
| Adding custom loading/error/empty banners | Use `SectionLayout`'s built-in `state`, `errorMsg`, `emptyMsg` props |
| Using `!important` in CSS | Increase specificity with BEM instead |
| Not testing dark mode | Always verify new components under `data-theme="dark"` |
