# Frontend Styling Guide

This document defines the styling rules for the Agenda frontend.

## Goals

- Keep section layout consistent across lists, forms, and timetable views.
- Reuse shared tokens and primitives instead of ad hoc values.
- Preserve responsive behavior on desktop and mobile.

## CSS Layers

Use this import order in `src/index.css`:

1. `src/styles/globals.css`
2. `src/styles/utilities.css`
3. `src/styles/components.css`
4. Component-local CSS files

Responsibilities:

- `globals.css`: tokens (colors, spacing, radius, shadows, typography), theme variables.
- `utilities.css`: low-level helpers (`flex`, spacing, sizing, overflow, etc.).
- `components.css`: shared primitives (`btn`, `input`, `select`, section heading helpers).
- `src/components/Shared.css`: shared state blocks (`state-loading`, `state-error`, `state-empty`).
- `src/components/*.css`: component-specific rules only.

## SectionLayout Contract

All top-level sections should use `SectionLayout`.

Use this structure:

- `title`: required section heading (`h2` rendered by `SectionLayout`).
- `description`: optional helper text under title.
- `actions`: optional top-right action area (buttons/filters).
- `state`: one of `ready`, `loading`, `error`, `empty`.
- `errorMsg` / `emptyMsg`: optional custom text for state rendering.
- `children`: main content rendered only when `state="ready"`.

Rules:

- Do not duplicate a second section title inside children.
- Keep modals outside `SectionLayout` when they are overlays.
- Put primary section-level actions in `actions`, not inside content tables.
- Reuse shared state classes through `SectionLayout` instead of custom state banners.

## Token Usage Rules

Do not hardcode values when an equivalent token exists.

Prefer:

- Colors: `var(--color-*)`
- Spacing: `var(--space-*)`
- Radius: `var(--radius-*)`
- Shadows: `var(--shadow-*)`
- Borders: `var(--color-border)`, `var(--color-input-border)`

Examples:

- Use `var(--color-primary)` instead of `#2563eb`
- Use `var(--space-md)` instead of `1rem`
- Use `var(--radius-md)` instead of `6px`

Exception:

- Allowed hardcoded values for highly decorative gradients in timetable cells when no shared token exists yet.

## Naming and Specificity

- Prefer BEM-style classes for shared blocks.
- Keep selectors shallow; avoid deep nesting.
- Avoid `!important`.
- Keep component CSS focused on local concerns.

## Responsive Rules

- Shared responsive behavior belongs in `SectionLayout.css`.
- Component-specific responsive fixes belong in each component CSS file.
- Target mobile breakpoints used by the project (`640px`, `768px`) unless a feature requires otherwise.

Minimum responsive expectations:

- Header/actions stack properly on small screens.
- Horizontal overflow is handled for wide tables.
- Controls remain tappable and legible.

## Accessibility

- Preserve semantic headings and button elements.
- Keep visible focus states with `:focus-visible`.
- Ensure contrast remains readable with current token palette.

## PR Checklist

- [ ] New section uses `SectionLayout`.
- [ ] No duplicated section headings.
- [ ] No avoidable hardcoded colors/spacing/radius values.
- [ ] State handling uses shared `SectionLayout` states.
- [ ] Mobile behavior validated for updated view.