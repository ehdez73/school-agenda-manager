import { describe, expect, it } from 'vitest';

import sectionLayoutCss from '../SectionLayout.css?raw';
import courseListCss from '../CourseList.css?raw';

describe('SectionLayout responsive behavior for list sections', () => {
  it('defines mobile stacking for heading row and actions in shared layout', () => {
    expect(sectionLayoutCss).toContain('@media (max-width: 640px)');
    expect(sectionLayoutCss).toMatch(/\.section-layout__heading-row\s*\{[^}]*flex-direction:\s*column/s);
    expect(sectionLayoutCss).toMatch(/\.section-layout__actions\s*\{[^}]*width:\s*100%/s);
  });

  it('defines mobile adjustments for CourseList action zone', () => {
    expect(courseListCss).toContain('@media (max-width: 768px)');
    expect(courseListCss).toMatch(/\.course-form-actions\s*\{[^}]*flex-direction:\s*column/s);
  });
});
