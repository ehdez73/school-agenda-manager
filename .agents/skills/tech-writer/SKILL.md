---
name: tech-writer
description: >
  Expert in writing and maintaining user documentation for School Agenda Manager.
  Use when the user mentions: GUIA_USUARIO.md, USER_GUIDE.md, user guide,
  guía de usuario, documentation, docs, writing documentation, keeping docs in sync,
  updating documentation, documenting the UI, sync docs, translation of guides,
  sync english spanish docs, user-facing guides, update user docs.
---

# Tech Writer Skill — User Documentation for School Agenda Manager

Responsible for keeping `docs/GUIA_USUARIO.md` (Spanish) and `docs/USER_GUIDE.md` (English) accurate, synchronized with each other, and up to date with the actual UI.

---

## 1. Core Rule

Every UI change — new routes, forms, labels, copy, components — **must** be reflected in **both** guide files. Never edit one without the other. The project convention (from `AGENTS.md`) states:

> *"Keep them in sync with the actual UI: update when routes, forms, labels, or UI copy change"*

---

## 2. Update Workflow

When asked to update the guides, follow this process:

1. Read **both** `docs/GUIA_USUARIO.md` and `docs/USER_GUIDE.md` completely
2. Read the relevant frontend components + i18n files to identify what changed in the UI
3. Edit both files **simultaneously**, section by section — same structural changes, different language
4. Verify:
   - Same sections exist in both files
   - Same numbering and hierarchy
   - Same examples, same steps, same terminology
   - Only the language differs
5. Check that every `[text](#anchor)` link in the table of contents still matches the auto-generated markdown anchor (lowercase, no accents, spaces → `-`)

---

## 3. Structure Reference

Both guides follow this 11-section mirror. Edits must preserve this structure:

| # | Section | Content |
|---|---------|---------|
| 1 | Application purpose | Goal of the app |
| 2 | Quick section map | Nav sections (Courses, Subjects, Packs, Teachers, Timetables, Settings) |
| 3 | Key definitions | Course, Line/Class, Subject, Pack, shared_hours, Teacher, Tutor, Availability, Preferences |
| 4 | Recommended workflow | 8-step order to avoid rework |
| 5 | How to create each element | Courses → Subjects → Packs → Teachers → Availability |
| 6 | Pack use cases | Religion / Educational Support, Communication/Music, with/without shared_hours |
| 7 | Timetable generation | Generate, review, recreate |
| 8 | Constraints: HARD and SOFT | Explanation + constraints table |
| 9 | Common issues | 4 error scenarios and how to fix them |
| 10 | Management best practices | 5 tips |
| 11 | Final checklist | Pre-generation checklist |

---

## 4. UI → Guide Section Mapping

| UI file(s) | Guide section(s) affected |
|---|---|
| `frontend/src/App.jsx` (nav links + page routing) | §2 Quick section map |
| `frontend/src/components/CourseList.jsx`, `CourseForm.jsx` | §5.1 Create courses |
| `frontend/src/components/SubjectList.jsx`, `SubjectForm.jsx` | §5.2 Create subjects |
| `frontend/src/components/SubjectGroupList.jsx`, `SubjectGroupForm.jsx` | §5.3 Create Packs, §6 Pack use cases |
| `frontend/src/components/TeacherList.jsx`, `TeacherForm.jsx` | §5.4 Create teachers |
| `frontend/src/components/PreferencesGrid.jsx` | §5.5 Availability and preferences |
| `frontend/src/components/ConfigForm.jsx` | §8 Constraints HARD/SOFT |
| `frontend/src/i18n/locales/en.json`, `es.json` | All sections (labels, button text, section titles) |
| `backend/translations.py` | Backend labels shown in API responses |

---

## 5. Format Conventions

- **Section headings**: `##` for top-level sections, `###` for subsections
- **Steps**: numbered lists (`1.`, `2.`)
- **Tables**: for constraints, quick references, and mappings
- **Key terms**: bold (`**term**` on first definition in §3)
- **Recommendations/notes**: italic block or bullet list after the steps
- **Index**: maintain the `[text](#section-anchor)` links at the top of both files
- **Anchor validation**: markdown auto-generates anchors by lowercasing, removing accents, and replacing spaces with `-`. Verify each link works (e.g. `[Packs](#packs)` matches `## Packs` → `#packs`)

---

## 6. Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Editing only one file | Always edit both GUIA_USUARIO.md and USER_GUIDE.md |
| Index links out of sync | Update `[text](#anchor)` when section titles change |
| Accents in anchors | Markdown strips accents — `"Restricciones"` → `#restricciones`, not `#restricciones` (no accent) |
| Copy mismatch with UI | Read the actual component or locale file, don't guess |
| Adding a section to only one file | Mirror every structural change in both languages |
