# Frontend Styling Guide

> La referencia completa de tokens CSS, BEM, responsive y utilidades
> está en el **Skill frontend §4** (`.agents/skills/frontend/SKILL.md`).
> Este documento es solo el **PR checklist** para humanos.

## PR Checklist

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
- [ ] `import React` removed — React 19 JSX transform no longer needs it (unless using `React.cloneElement` etc.).
