import { describe, expect, it } from 'vitest';

import configFormCss from '../ConfigForm.css?raw';

describe('ConfigForm responsive behavior', () => {
  it('defines mobile breakpoint for form spacing and controls', () => {
    expect(configFormCss).toContain('@media (max-width: 768px)');
    expect(configFormCss).toMatch(/\.config-form-container\s*\{[^}]*max-width:\s*100%/s);
    expect(configFormCss).toMatch(/\.config-tabs\s*\{[^}]*overflow-x:\s*auto/s);
  });
});
