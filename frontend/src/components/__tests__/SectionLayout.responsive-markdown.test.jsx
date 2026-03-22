import { describe, expect, it } from 'vitest';

import markdownTimetableCss from '../MarkdownTimetable.css?raw';

describe('Markdown timetable responsive behavior', () => {
  it('defines mobile width constraints for timetable columns', () => {
    expect(markdownTimetableCss).toContain('@media (max-width: 768px)');
    expect(markdownTimetableCss).toMatch(/\.markdown-timetable\s+th:not\(:first-child\),\s*\n\s*\.markdown-timetable\s+td:not\(:first-child\)\s*\{[^}]*min-width:\s*140px/s);
  });

  it('defines mobile container compaction for timetable wrapper', () => {
    expect(markdownTimetableCss).toMatch(/@media \(max-width:\s*768px\)\s*\{[^}]*\.timetable-container\s*\{[^}]*padding:\s*var\(--space-md\)/s);
  });
});
