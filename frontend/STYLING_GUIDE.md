# React Styling Best Practices Guide

This document outlines the styling approach implemented in this React application following modern best practices.

## Architecture Overview

Our styling system is organized into several layers:

### 1. Global Styles (`src/styles/globals.css`)
- CSS custom properties (variables) for colors, spacing, typography
- Base reset and typography styles
- Theme support via `data-theme` attribute
- Global accessibility styles

### 2. Utility Classes (`src/styles/utilities.css`)
# Styling Guide — Agenda Frontend

This guide replaces the previous long-form document with a concise, action-oriented reference for frontend developers working on the Agenda app. It covers the folder layout, conventions, examples, accessibility rules, theming, and a short migration + checklist.

Goals:
- Keep styles predictable, low-specificity, and easy to reason about.
- Support runtime theming with CSS variables.
- Make components portable and easy to test.

## Where styles live

Recommended layout (under `src/`):

- `src/styles/globals.css` — CSS variables, resets, base typography, and theme tokens.
- `src/styles/utilities.css` — Small utility classes (spacing, flex helpers, text helpers).
- `src/styles/components.css` — Shared component primitives (btn, card, input) using BEM-ish names.
- `src/components/Shared.css` — Cross-component helpers used only in this app.
- `src/components/<Component>.css` or `<Component>.module.css` — Component-scoped styles.

Import order in `src/index.css` (or `main.jsx`):

1. `globals.css`
2. `utilities.css`
3. `components.css`
4. Component imports (they bring their own CSS)

This order ensures variables and utilities are available to components and helps with predictable cascade.

## Key conventions

- Use CSS custom properties for all colors, spacing, radii, and type sizes (declare in `globals.css`).
- Prefer utility classes for layout and spacing (avoid repeating utility declarations in component files).
- Use simple BEM-style class names for shared components: `.btn`, `.btn--primary`, `.card__header`.
- Component files can use CSS Modules when encapsulation is needed (name them `Component.module.css`).
- Avoid deep selector nesting and !important.

Example tokens (place in `:root` in `globals.css`):

:root {
  --color-bg: #ffffff;
  --color-text: #0f172a;
  --color-primary: #2563eb;
  --color-success: #16a34a;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
}

## Utilities (examples)

- `.flex` — display: flex
- `.items-center` — align-items: center
- `.gap-md` — gap: var(--space-md)
- `.mt-sm` / `.mb-md` — margin-top/bottom helpers

Keep utilities small and composable. If you find many components repeating the same pattern, consider adding a new utility.

## Component patterns

Shared button example (in `components.css`):

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid transparent;
}
.btn--primary { background: var(--color-primary); color: white; }

Component-specific CSS (use module if you need scoping):

// MyComponent.module.css
.root { display:flex; gap:var(--space-md); }

Then in React:

import styles from './MyComponent.module.css'
<div className={styles.root}>…</div>

## Theming

Use the `data-theme` attribute on `document.documentElement` to switch theme tokens. Keep theme overrides limited to token values — avoid duplicating component rules per theme.

[data-theme="dark"] {
  --color-bg: #0b1220;
  --color-text: #e6eef8;
}

Toggle in React:

useEffect(() => {
  document.documentElement.setAttribute('data-theme', theme);
}, [theme]);

Keep theme tokens exhaustive: background, surface, text, primary, muted, border.

## Accessibility rules

- Use `:focus-visible` to show keyboard focus. Do not hide focus outlines for keyboard users.
- Ensure color contrast meets WCAG AA for normal text (>= 4.5:1) and large text (>= 3:1).
- Use semantic HTML (buttons, form controls) and ARIA only when necessary.
- Provide meaningful alt text for images and labels for form controls.

Focus example:

.btn:focus-visible { outline: 2px solid color-mix(in srgb, var(--color-primary) 60%, transparent); outline-offset: 2px; }

## CSS Modules vs global CSS

- Use CSS Modules for components that need guaranteed isolation (complex internal layouts, third-party widget wrappers).
- Use global shared styles for primitives (buttons, inputs) and utilities.

## Migration tips (small checklist)

1. Replace hard-coded values with variables from `globals.css`.
2. Move repeated layout rules into utilities.
3. Convert component styles that need isolation to CSS Modules.
4. Rename classes to BEM-ish naming for shared components.

## Performance & maintenance

- Import global styles once in `index.css` to keep bundle lean.
- Prefer CSS variables and small utilities over large component overrides.
- Keep selectors low specificity so overrides are predictable.

## Quick troubleshooting

- Variables not applied: ensure `globals.css` is imported before other styles.
- Styles not updating in dev: restart Vite and clear cache (hard reload).
- Unexpected specificity conflicts: inspect with DevTools and refactor to utilities or modules.

## Developer checklist before PR

- [ ] Follow token variables (no hard-coded hex unless unavoidable).
- [ ] Run the app in both light and dark themes and validate contrast.
- [ ] Keyboard-navigate the UI and check focus states.
- [ ] Keep CSS changes focused and add short notes in PR about style changes.

If you want, I can add a small `.env.example`, an audit script that checks color contrast automatically, or a set of Storybook stories for key components to help visual QA. Which of these would you like next?