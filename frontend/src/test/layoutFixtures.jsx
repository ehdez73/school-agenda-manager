/**
 * layoutFixtures.js
 * Reusable render helpers for section layout tests.
 *
 * Usage:
 *   import { renderSection, renderSectionWithState } from '../../test/layoutFixtures';
 */
import { render, screen } from '@testing-library/react';
import { expect } from 'vitest';
import SectionLayout from '../components/SectionLayout';

/**
 * Render a minimal SectionLayout with sensible defaults.
 * @param {object} overrides – props merged with defaults
 * @returns render result
 */
export function renderSection(overrides = {}) {
  const defaults = {
    title: 'Test Section',
    children: <p>Content</p>,
    state: 'ready',
  };
  return render(<SectionLayout {...defaults} {...overrides} />);
}

/**
 * Render a SectionLayout in a given state.
 */
export function renderSectionWithState(state, { errorMsg = 'Error occurred', emptyMsg = 'Nothing here', ...props } = {}) {
  return render(
    <SectionLayout
      title="Test Section"
      state={state}
      errorMsg={errorMsg}
      emptyMsg={emptyMsg}
      {...props}
    >
      <p>Ready content</p>
    </SectionLayout>
  );
}

/**
 * Assert that a section has the standard structural elements.
 * @param {string} titleText – expected h2 text
 */
export function assertSectionStructure(titleText) {
  expect(screen.getByRole('heading', { level: 2, name: titleText })).toBeInTheDocument();
  expect(screen.getByTestId('section-layout')).toBeInTheDocument();
  expect(screen.getByRole('banner')).toBeInTheDocument(); // <header>
}
